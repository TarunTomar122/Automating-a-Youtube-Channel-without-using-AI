import os
from pytube import YouTube
from moviepy.video.io.VideoFileClip import VideoFileClip
from youtube_transcript_api import YouTubeTranscriptApi
from moviepy.editor import *
from moviepy.config import change_settings
import numpy as np
change_settings(
    {"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.0-Q16-HDRI\\magick.exe"})


class RobertTheBot:

    url = ''
    length = 0

    start = 0
    end = 0

    subs = []

    def __init__(self, url, length, data):
        self.url = url
        self.length = length

        self.getMostReplayedPart(data)

    def preProcessData(self, data):

        tripletsArray = data.split("C ")

        dataPointsArray = []

        for triplets in tripletsArray:
            if triplets != "":

                pointsArray = triplets.split(" ")[:3]

                for points in pointsArray:
                    p = points.split(",")
                    dataPointsArray.append([float(p[0]), float(p[1])])

        return dataPointsArray

    @staticmethod
    def getXforMaxY(x, y):

        maxX = -1
        maxY = -float('inf')
        for index in range(int(len(y)*(0.2)), len(y)-(int(len(y)*0.2))):
            point = y[index]
            if point > maxY:
                maxX = index
                maxY = point

        return maxX

    def getMostReplayedPart(self, data):

        dataPointsArray = self.preProcessData(data)

        x = [((p[0] - 1) * (self.length) / (1000 - 1))
             for p in dataPointsArray]
        y = [-p[1] for p in dataPointsArray]

        maxX = x[self.getXforMaxY(x, y)]

        print(x, y)

        self.start = max(0, maxX-10)
        self.end = min(self.length-1, maxX+40)

    def downloadVideo(self):

        yt = YouTube(self.url)
        stream = yt.streams.filter(progressive=True).order_by(
            'resolution').desc().first()
        stream.download(output_path="./", filename="input.mp4")

    def cutVideo(self):

        video = VideoFileClip("input.mp4")
        clip = video.subclip(self.start, self.end)
        clip = clip.resize((1080, 1300))
        clip.write_videofile("cut.mp4")

    def getSubs(self):

        videoCode = self.url.split("?v=")[1]

        srt = YouTubeTranscriptApi.get_transcript(videoCode)

        subs = []

        for i in srt:
            if i['start'] >= self.start and i['start'] <= self.end:
                subs.append(i)

        self.subs = subs

    def editVideo(self):

        # Load the video file
        video = VideoFileClip("cut.mp4")

        subTexts = []

        index = 0
        for sub in self.subs:
            text = TextClip(sub['text'], fontsize=100,
                            color="yellow", font="Arial")
            
            text = text.resize(width=1000)
            if index < len(self.subs)-1:
                text = text.set_duration(self.subs[index+1]['start']-sub['start'])
            else:
                text = text.set_duration(self.end-sub['start'])
            # text = text.set_duration(
            #     min(sub['duration'], self.end-sub['start']))
            text = text.set_start(sub['start']-self.start)
            text = text.set_position(("center", 0.7), relative=True)
            subTexts.append(text)
            index += 1

        compositeArr = [video]+subTexts
        final_video = CompositeVideoClip(compositeArr)

        final_video.write_videofile("final.mp4", fps=video.fps)

    def clear(self):

        os.remove('./cut.mp4')
        os.remove('./input.mp4')