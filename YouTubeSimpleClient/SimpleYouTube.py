from __future__ import unicode_literals

from pygame import mixer
mixer.init()

from subprocess import call, DEVNULL

import youtube_dl
#import shutil
import json
import sys
import os

import time
import YouTube
import threading

if __name__ != "__main__":
    exit()

if sys.platform == "win32":
    from msvcrt import getch
else:
    from getch import getch

_LastLength = 0

def Print(Item):
    global _LastLength

    Item = str(Item)

    while len(Item) < _LastLength:
        Item += " "

    _LastLength = len(Item)
    sys.stdout.write("\r")
    sys.stdout.write(Item)

def Input(Text = None):
    if Text == None:
        Data = input()
    else:
        Print(Text)
        Data = input()

    return Data

def Clear(Lines = 1):
    CURSOR_UP_ONE = '\x1b[1A'
    ERASE_LINE = '\x1b[2K'

    for loop in range(Lines):
        print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)
    sys.stdout.write(CURSOR_UP_ONE + "\r")

def Select(SL, removeAfterSelected = True): ## KatisticUtils/ioput.py
    CURSOR_UP_ONE = '\x1b[1A'
    ERASE_LINE = '\x1b[2K'

    Selecting = 0
    Entrance = "b'\\xe0'"
    Down = "b'H'"
    Up = "b'P'"
    Enter = "b'\\r'"
    Nul = "b'\\xff'"

    Selected = False

    while not Selected:
        NewSL = ""
        for x in range(len(SL)):
            if x == Selecting:
                NewSL += " >> " + SL[x]
            else:
                NewSL += "    " + SL[x]

            if x != len(SL) + 1:
                NewSL += "\n"

        print(NewSL)

        while True:
            Key = getch()
            Key = str(Key)

            if Key == Entrance:
                Key = getch()
                Key = str(Key)

                if Key == Up:
                    if Selecting == len(SL) - 1:
                        Selecting = 0
                    else:
                        Selecting += 1
                    break

                elif Key == Down:
                    if Selecting == 0:
                        Selecting = len(SL) - 1
                    else:
                        Selecting -= 1
                    break

            elif Key == Enter:
                Selected = True
                break

        if Selected:
            if removeAfterSelected:
                for x in range(len(SL) + 1):
                    print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)
                sys.stdout.write(CURSOR_UP_ONE + "\r")
            break
        else:
            for x in range(len(SL) + 1):
                print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)
            sys.stdout.write(CURSOR_UP_ONE + "\r")

    return SL[Selecting]

try:
    with open(".\\prefs.json", "r") as SetFile:
        Setts = json.load(SetFile)
except:
    Setts = {
        "Autoplay (Inaffective)": [True],
        "Pre-Download Next Video (Inaffective)": [True],
        "Clear Cache On Start (Inaffective)": [True],
        "Consecutive Downloads (Inaffective)": [1, 1, 8]
    }

    with open(".\\prefs.json", "w") as SetFile:
        json.dump(Setts, SetFile, indent = 4)

DownloadingList = []
DownloadedList = []
Playing = None

def Settings():
    while True:
        SelList = []
        Length = 50

        for Thing in Setts:
            SelList.append(Thing + "  :  " + str(Setts[Thing][0]))

        SelList.append("Back")

        Sel = Select(SelList)

        if Sel == "Back":
            break

        Seled = Setts[Sel.split("  :  ")[0]]

        if type(Seled[0]) == int:
            Sel = Input("New Value: ")
            Clear()
            Pass = True

            try:
                int(Sel)
                Sel = int(Sel)

                if len(Seled) > 1:
                    if Seled[1] != None:
                        if Sel < Seled[1]:
                            Pass = False

                    if Seled[2] != None:
                        if Sel > Seled[2]:
                            Pass = False
            except:
                Pass = False

            if Pass:
                Seled[0] = Sel

        elif Seled[0] == True or Seled[0] == False:
            Sel = Select(["True", "False"])
            Seled[0] = eval(Sel)

        with open(".\\prefs.json", "w") as SetFile:
            json.dump(Setts, SetFile, indent = 4)

    with open(".\\prefs.json", "w") as SetFile:
        json.dump(Setts, SetFile, indent = 4)

def Search():
    if YouTube.Online:
        Vid = Input("Search Index: ")
        Clear()

        Results = YouTube.search_list(Vid, mResults = 20)
        Vids = []

        for Result in Results:
            Vids.append(Result["title"] + " (" + Result["id"] + ")")

        Vids.append("<< Back >>")

        Sel = Select(Vids)
        if Sel == "<< Back >>":
            return

        for Result in Results:
            if Sel == Result["title"] + " (" + Result["id"] + ")":
                Vid = Result

        ydl_opts = {
            'format': 'worstvideo[ext=mp4]+bestaudio[ext=mp3]/best[ext=mp4]',
            'noplaylist': True,
            'quiet': True,
            'outtmpl': ".\\Music\\"+Vid['id']+'.mp4'
        }

        def Download():
            DownloadingList.append(Vid["title"] + " (" + Vid["id"] + ")")

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download(["https://www.youtube.com/watch?v=" + Vid["id"]])

            command = ".\\ffmpeg\\bin\\ffmpeg.exe -i .\\Music\\" + Vid['id'] + ".mp4 -vn .\\Music\\" + Vid['id'] +".wav"
            c = call(command, stderr = DEVNULL, stdout = DEVNULL)

            DownloadingList.remove(Vid["title"] + " (" + Vid["id"] + ")")
            DownloadedList.append([Vid["title"], Vid["id"]])

        DLThread = threading.Thread(target = Download) # playsound(".\\Music\\"+Result['id']+'.wav')
        DLThread.daemon = True
        DLThread.start()

def Downloading():
    while True:
        ToSel = []

        for item in DownloadingList:
            ToSel.append(item)

        ToSel.append("<< Refresh >>")
        ToSel.append("<<  Back  >>")

        Sel = Select(ToSel)
        if Sel == "<< Refresh >>":
            continue
        elif Sel == "<<  Back  >>":
            return
        else:
            continue

"""
try:
    if Setts["Clear Cache On Start"][0]:
        shutil.rmtree(".\\Music")
except:
    pass

"""

try:
    os.mkdir(".\\Music\\")
except:
    pass

def YTConnect():
    while True:
        time.sleep(1)
        YouTube.Connect()

def PlayLoop():
    global Playing

    while True:
        time.sleep(1)

        if not mixer.music.get_busy():
            if len(DownloadedList) > 0:
                Vid = DownloadedList.pop(0)

                mixer.music.load(".\\Music\\" + Vid[1] +".wav")
                mixer.music.play()

                if not Playing == None:
                    if not Playing in DownloadedList and not Playing == Vid: # Repeat? Save dl
                        os.remove(".\\Music\\"+Playing[1]+'.mp4')
                        os.remove(".\\Music\\" + Playing[1] +".wav")

                Playing = Vid

        if len(DownloadedList) == 0 and len(DownloadingList) == 0:
            if not Playing == None:
                if YouTube.Online:
                    Result = YouTube.related_list(Playing[1])[0]

                    ydl_opts = {
                        'format': 'worstvideo[ext=mp4]+bestaudio[ext=mp3]/best[ext=mp4]',
                        'noplaylist': True,
                        'quiet': True,
                        'outtmpl': ".\\Music\\"+Result['id']+'.mp4'
                    }

                    def Download():
                        DownloadingList.append(Result["title"] + " (" + Result["id"] + ")")

                        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                            ydl.download(["https://www.youtube.com/watch?v=" + Result["id"]])

                        command = ".\\ffmpeg\\bin\\ffmpeg.exe -i .\\Music\\" + Result['id'] + ".mp4 -vn .\\Music\\" + Result['id'] +".wav"
                        c = call(command, stderr = DEVNULL, stdout = DEVNULL)

                        DownloadingList.remove(Result["title"] + " (" + Result["id"] + ")")
                        DownloadedList.append([Result["title"], Result["id"]])

                    DLThread = threading.Thread(target = Download) # playsound(".\\Music\\"+Result['id']+'.wav')
                    DLThread.daemon = True
                    DLThread.start()

ConnThread = threading.Thread(target = YTConnect)
ConnThread.daemon = True
ConnThread.start()

PlayThread = threading.Thread(target = PlayLoop)
PlayThread.daemon = True
PlayThread.start()

while True:
    Sel = Select(["Search", "Downloading", "Settings", "Exit"])

    if Sel == "Exit":
        exit()

    eval(Sel + "()")
