from RobertTheBot import RobertTheBot
import sys

videoLength = int(sys.argv[1:][0])
videoUrl = sys.argv[1:][1]
data = sys.argv[1:][2]

bot = RobertTheBot(videoUrl, videoLength, data)

try:
    pass
    # first we have to  download the youtube video
    bot.downloadVideo()

    # now we're gonna cut the video's most replayed part
    bot.cutVideo()

    # now we're gonna get the subtitles for the required part of the video
    bot.getSubs()

    # and finally we can edit the video with the new subtitles
    bot.editVideo()

    # remove useless files
    bot.clear()

except Exception as e:
    print("Something went wrong!", e)
