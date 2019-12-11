import sys
import io

t = sys.stderr
sys.stderr = io.StringIO()

import youtube
import youtube_dl
import threading
import numpy as np
import pydub
import time
import soundcard as sc
import os
import pythoncom

sys.stderr = t

class Player:
    def __init__(self):
        self.speaker = sc.default_speaker()

        self.playthread = None
        self.q = []
        self.loadl = []
        self.play()

    def SearchVideo(self, q):
        return youtube.search.videos(q = q, maxResults=1)

    def SearchRelatedVideo(self, id):
        return youtube.search.videos(relatedToVideoId=id, maxResults=10)

    def read(self, f, normalized=False):
        """MP3 to numpy array"""
        a = pydub.AudioSegment.from_mp3(f)
        y = np.array(a.get_array_of_samples())

        if a.channels == 2:
            y = y.reshape((-1, 2))
        if normalized:
            return a.frame_rate, np.float32(y) / 2**15
        else:
            return a.frame_rate, y

    def queue(self, f):
        self.q.append(f)

    def loadla(self, f):
        self.loadl.append(f)

        if len(self.loadl) > 10:
            for item in self.loadl:
                if item not in self.q:
                    self.loadl.remove(item)
                    os.remove(item)

    def load(self, id):
        if not id+".mp3" in self.loadl:
            self.loadla(id+".mp3")

            ydl_opts = {
                'format': 'best[ext=mp4]',
                'outtmpl': id+".mp4",
                'quiet': True,
                'no_warnings': True,
                "nocheckcertificate": True,
                'noplaylist': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3'
                }]
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download(["https://www.youtube.com/watch?v=" + id])

        self.queue(id+".mp3")

    def play(self):
        def play():
            a = 1
            pythoncom.CoInitialize()

            while a == 1:
                if len(self.q) > 0:
                    f = self.q.pop(0)

                    # Get next related video
                    tthread = threading.Thread(target=self.load,\
                        args=[self.SearchRelatedVideo(f.split(".")[0])[0].id])
                    tthread.daemon = True
                    tthread.start()

                    fr, data = self.read(f)
                    self.speaker.play(data/np.max(data), fr)
                else:
                    time.sleep(.1)

        self.playthread = threading.Thread(target=play)
        self.playthread.daemon = True
        self.playthread.start()

devkey = "token"

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

os.environ["PATH"] += os.pathsep + resource_path("ffmpeg\\")
youtube.SetClient(devkey)
player = Player()

def QueueId(id):
    if id in loading and id not in loaded:
        while not id in loaded:
            time.sleep(.1)
        player.queue(id+".mp3")
    elif not id in loading:
        if id in loaded:
            player.queue(id+".mp3")
        else:
            LoadFromId(id)
            QueueId(id)

player.load(player.SearchVideo(input("Starting video name: "))[0].id)

while player.playthread.is_alive():
    time.sleep(1)
