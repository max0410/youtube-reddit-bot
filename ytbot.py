import praw
from comtypes.client import CreateObject
import comtypes.gen 
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap
import soundfile as sf
from moviepy.editor import *
from moviepy.config import change_settings
change_settings({"FFMPEG_BINARY": "ffmpeg"})
import math
import time as t

def create_title(username, time, content, outfile):
    diff = t.time()-time
    days = math.floor(diff/86400)
    diff -= days*86400
    if days > 1:
        time = str(diff.days) +" days ago"
    elif days > 0:
        time = "1 day ago"
    elif math.floor(diff/3600) > 1:
        time = str(math.floor(diff/3600)) +" hours ago"
    elif math.floor(diff/3600) > 0:
        time = "1 hour ago"
    elif math.floor(diff/60) > 1:
        time = str(math.floor(diff/60)) +" minutes ago"
    else:
        print("!!!!!!!!!!!!!!")
    img = Image.open("background.jpg").convert("RGBA")
    
    verdana = ImageFont.truetype("fonts/verdana.ttf", 12*3)
    contentFont = ImageFont.truetype("fonts/verdana.ttf", 20*3)
    verdanab = ImageFont.truetype("fonts/verdanab.ttf", 12*3)
    d = ImageDraw.Draw(img)

    content = textwrap.fill(content, width=55)

    logo = Image.open("askredditlogo.png").convert("RGBA")
    logo = logo.resize((50,50))
    logow, logoh = logo.size
    w1, h1 = d.textsize("r/AskReddit", font=verdanab)

    w = 623 * 3
    h = 15+h1+5+sum(list(map(lambda x: d.textsize(x, font=contentFont)[1], content.split("\n"))))
    y = int((img.size[1]-h)/2)
    x = int((img.size[0]-w)/2)
    
    d.rectangle([x,y,x+w,y+h], (255,255,255), 1)
    img.paste(logo, (x+15,y+15,x+15+logow,y+15+logoh), logo)
    d.text((x+20+logow, y+15), "r/AskReddit", font=verdanab, fill=(28, 28, 28))
    d.text((x+15+w1+logow, y+15), " • Posted by "+ username + " " + time, font=verdana, fill=(120, 124, 126))
    d.text((x+15, y+15+h1+5), content, font=contentFont, fill=(26, 26, 27))

    img.save(outfile)

def create_comment(username, points, time, content, outfile):
    points = str(math.floor(points/100)/10) + "k"
    diff = t.time()-time
    days = math.floor(diff/86400)
    diff -= days*86400
    if days > 1:
        time = str(diff.days) +" days ago"
    elif days > 0:
        time = "1 day ago"
    elif math.floor(diff/3600) > 1:
        time = str(math.floor(diff/3600)) +" hours ago"
    elif math.floor(diff/3600) > 0:
        time = "1 hour ago"
    elif math.floor(diff/60) > 1:
        time = str(math.floor(diff/60)) +" minutes ago"
    else:
        print("!!!!!!!!!!!!!!")
    img = Image.open("background.jpg")
    
    fnt = ImageFont.truetype("fonts/verdana.ttf", 12*3)
    d = ImageDraw.Draw(img)

    n = 0

    lines = list(map(lambda x: x+" ", content.split("\n")))
    if len(lines) == 1:
        content = textwrap.fill(lines[0], 100)
        n = 12
    else:
        new_lines = []
        for x in range(0,len(lines)):
            lines[x] = lines[x].replace("&#x200B;", "\n")
            if lines[x] == " ":
                new_lines.append(" ")
            else:
                new_lines = new_lines + textwrap.wrap(lines[x], 100)

        content = "\n".join(new_lines)
    l, h1 = d.textsize(username, font=fnt)
    h = 2+h1+9+sum(list(map(lambda x: d.textsize(x, font=fnt)[1], content.split("\n"))))+n
    y = (img.size[1]-h)/2
    w = 623*3
    x = (img.size[0]-w)/2


    d.rectangle([x,y,x+w,y+h], (255,255,255), 1)
    d.text((x+8, y+2), username, font=fnt, fill=(68, 78, 89))
    d.text((x+8+l+16, y+2), points +" points", font=fnt, fill=(124, 124, 124))
    l1 = d.textsize(points +" points", font=fnt)[0]
    d.text((x+8+l+l1+34, y+2), "·", font=fnt, fill=(124, 124, 124))
    l2 = d.textsize("·", font=fnt)[0]
    d.text((x+8+l+l1+l2+52, y+2), time, font=fnt, fill=(124, 124, 124))
    d.text((x+8, y+2+h1+12), content, font=fnt, fill=(26, 26, 27))

    img.save(outfile)

# Reddit Stuff
reddit = praw.Reddit(client_id="-",
                     client_secret="-",
                     user_agent="Youtube Reddit Bot")

post = list(reddit.subreddit("askReddit").top("day", limit=1))[0]

comments = post.comments[0:30]

# Audio stuff
f = open("list.txt", "w+")
f1 = open("final.txt", "w")
f1.write("")
f1.close()
f.write("")
os.system("del /q \"pictures\*\"")
os.system("del /q \"comments\*\"")
os.system("del endcard.wav")

engine = CreateObject("SAPI.SpVoice")
stream = CreateObject("SAPI.SpFileStream")
outfile = "title.wav"
f.write(f.read() + "file '"+outfile+"'\n")
f.write(f.read() + "file 'silence.wav'\n")
stream.Open(outfile, comtypes.gen.SpeechLib.SSFMCreateForWrite)
engine.AudioOutputStream = stream

engine.speak(post.title)
stream.Close()
create_title(post.author.name, post.created_utc, post.title, "title.png")

for comment in comments:
    body = comment.body
    try:
        create_comment(comment.author.name, comment.score, comment.created_utc, body, "pictures/picture"+ comment.id +".png")
    except:
        continue
    engine = CreateObject("SAPI.SpVoice")
    stream = CreateObject("SAPI.SpFileStream")
    outfile = "comments/comment"+ comment.id +".wav"
    f.write(f.read() + "file '"+outfile+"'\n")
    f.write(f.read() + "file 'silence.wav'\n")
    stream.Open(outfile, comtypes.gen.SpeechLib.SSFMCreateForWrite)
    engine.AudioOutputStream = stream

    engine.speak(comment.body)
    stream.Close()
    
engine = CreateObject("SAPI.SpVoice")
stream = CreateObject("SAPI.SpFileStream")
outfile = "endcard.wav"
f.write(f.read() + "file '"+outfile+"'\n")
f.write(f.read() + "file 'silence.wav'\n")
stream.Open(outfile, comtypes.gen.SpeechLib.SSFMCreateForWrite)
engine.AudioOutputStream = stream

engine.speak("Thanks for watching, please like, subscribe, and comment!")
stream.Close()

f.close()
os.system("ffmpeg -loglevel panic -f lavfi -i anullsrc=channel_layout=5.1:sample_rate=48000 -t 0.1 -y silence.wav")
os.system("ffmpeg -loglevel panic -i silence.wav -f lavfi -i anullsrc -c:v copy -video_track_timescale 30k -c:a aac -ac 6 -ar 44100 -shortest -t 1 -y silence.wav")
os.system("ffmpeg -loglevel panic -f concat -safe 0 -i list.txt -y -c copy output.wav")
os.system("ffmpeg -loglevel panic -y -i output.wav -i background_music.wav -filter_complex amix=inputs=2:duration=first:dropout_transition=3 combined.wav")
os.system('ffmpeg -loglevel panic -y -i combined.wav -filter_complex "afade=d=0.5, areverse, afade=d=0.5, areverse" final1.wav')

inFile = open("list.txt", "r")
outFile = open("final.txt", "a")
lines = inFile.read().split("\n")
outFile.write("ffconcat version 1.0\n")

clips = []
s = sf.SoundFile("silence.wav")
for line in lines:
    if line:
        if "silence" not in line:
            f = sf.SoundFile(line.split("'")[1])
            line = line.replace("comment", "picture").replace(".wav",".png")
            print(line)
            file = line.split("'")[1]
            time = (len(f) / f.samplerate) + 1.3
            clips.append(ImageClip(file).set_duration(time))

f = sf.SoundFile("endcard.wav")
clips.append(ImageClip("endcard.png").set_duration((len(f) / f.samplerate) + 1.3))

video = concatenate(clips, method="compose")
video.write_videofile("output.mp4", fps=24, codec="mpeg4")

inFile.close()
outFile.close()
os.system("ffmpeg -y -i final1.wav -r 30 -i output.mp4 -filter:a aresample=async=1 -c:v copy final.mp4")