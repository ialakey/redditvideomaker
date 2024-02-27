from moviepy.editor import *
import reddit, screenshot, time, subprocess, random, configparser, sys, math, os
from os import listdir
from os.path import isfile, join
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from pytube import YouTube
import glob
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips, CompositeVideoClip, clips_array
from moviepy.video.fx.all import resize, margin

def createShortsVideo():
    config = configparser.ConfigParser()
    config.read('config.ini')
    templateDir = config["General"]["TemplateDirectory"]
    outputDir = config["General"]["OutputDirectory"]

    startTime = time.time()

    # Get script from reddit
    # If a post id is listed, use that. Otherwise query top posts
    if len(sys.argv) == 2:
        script = reddit.getContentFromId(templateDir, sys.argv[1])
    else:
        postOptionCount = int(config["Reddit"]["NumberOfPostsToSelectFrom"])
        script = reddit.getContent(templateDir, postOptionCount)
    fileName = script.getFileName()

    # Create screenshots
    screenshot.getPostScreenshots(fileName, script)

    # Setup background clip
    bgDir = config["General"]["BackgroundDirectory"]
    bgFiles = [f for f in listdir(bgDir) if isfile(join(bgDir, f))]
    bgCount = len(bgFiles)
    bgIndex = random.randint(1, bgCount)
    backgroundVideo = VideoFileClip(
        filename=f"{bgDir}/{bgIndex}.mp4",
        audio=False
    ).subclip(0, script.getDuration())
    w, h = backgroundVideo.size

    # # Resize the background video to 9:16
    # backgroundVideo = resize(backgroundVideo, newsize=(w, int(w * 16 / 9)))

    # # Add margins to the resized background video
    # backgroundVideo = margin(backgroundVideo, top=500, bottom=500)

    def createClip(screenShotFile, audioClip, marginSize):
        imageClip = ImageClip(
            screenShotFile,
            duration=audioClip.duration
        ).set_position(("center", "center"))
        imageClip = imageClip.resize(width=(w-marginSize))
        videoClip = imageClip.set_audio(audioClip)
        videoClip.fps = 1
        return videoClip

    # Create video clips
    print("Editing clips together...")
    clips = []
    marginSize = int(config["Video"]["MarginSize"])
    clips.append(createClip(script.titleSCFile, script.titleAudioClip, marginSize))
    for comment in script.frames:
        clips.append(createClip(comment.screenShotFile, comment.audioClip, marginSize))

    # Merge clips into a single track
    contentOverlay = concatenate_videoclips(clips).set_pos(("center", 50))

    # Compose background/foreground
    final = CompositeVideoClip(
        clips=[backgroundVideo, contentOverlay],
        size=backgroundVideo.size
    ).set_audio(contentOverlay.audio)

    final.duration = script.getDuration()
    final.set_fps(backgroundVideo.fps)

    print("Rendering final video...")
    bitrate = config["Video"]["Bitrate"]
    threads = config["Video"]["Threads"]
    outputFile = f"{outputDir}/{fileName}_shorts.mp4"
    final.write_videofile(
        outputFile,
        codec='libx264',
        threads=threads,
        bitrate=bitrate
    )
    print(f"Video completed in {time.time() - startTime}")

    deleteAllFilesInDirectory(templateDir)

    print("Shorts video is ready to upload!")
    print(f"Title: {script.title}  File: {outputFile}")
    endTime = time.time()
    print(f"Total time: {endTime - startTime}")

    # video_title = script.title
    # video_description = "Best Telegram group with all movies: https://t.me/kino_narezo4ka"
    # publish_video_to_youtube(outputFile, config["Youtube"]["CLIENT_SECRET_FILE"], video_title, video_description)


def deleteAllFilesInDirectory(directory):
    files = glob.glob(os.path.join(directory, '*'))
    
    for file in files:
        try:
            os.remove(file)
            print(f"File {file} deleted.")
        except FileNotFoundError:
            print(f"File {file} not found.")
        except IsADirectoryError:
            print(f"{file} is a directory, skipping.")
        except Exception as e:
            print(f"Error deleting file {file}: {e}")

def publish_video_to_youtube(output_path, client_secrets_file, video_title, video_description):
    try:

        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, ["https://www.googleapis.com/auth/youtube.upload"])
        credentials = flow.run_local_server(port=0)

        youtube = build("youtube", "v3", credentials=credentials)

        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "description": video_description,
                    "title": video_title,
                    "tags": ["YouTube Shorts"],
                    "categoryId": "22",
                },
                "status": {
                    "privacyStatus": "public"
                }
            },
            media_body=MediaFileUpload(output_path)
        )

        response = request.execute()

        print(f"Video successfully published to YouTube. Video ID: {response['id']}")

    except Exception as e:
        print(f"Error publishing video to YouTube: {e}")

if __name__ == "__main__":
    createShortsVideo()
