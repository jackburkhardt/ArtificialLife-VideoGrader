from pytube import YouTube
import os
import sys
from canvasapi import Canvas
import combine
import threading
import re
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("CANVAS_API_URL")
API_KEY = os.getenv("CANVAS_API_KEY")
COURSE_ID = os.getenv("COURSE_ID")

canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course(COURSE_ID)
assignment = None
submissions = []

total_videos = 0
download_queue = []
video_path = ""

student_names_ids = {}

def init(id):
    global assignment
    global video_path
    assignment = course.get_assignment(id)
    video_path = f"{id}"
    download_submissions()

def download_submissions():
    global submissions
    submissions = [assignment.get_submission(229733)]
    try:
        print(assignment.name)
        os.mkdir(f"{video_path}")
    except FileExistsError:
        pass
    except:
        sys.stderr.write("Error creating directory for video output!")
        sys.exit(1)

    for submission in submissions:
        # if already graded, skip
        if submission.score is not None: continue
        print(submission.user_id)

        # if submission is url and url is youtube, download video asynchronously
        if submission.submission_type == "online_text_entry" and ("youtube" in submission.body or "youtu.be" in submission.body):
            student_names_ids[submission.user_id] = "Test Student"
            #canvas.get_user(submission.user_id).name
            threading.Thread(target=download_submission, args=(submission,)).start()
            global total_videos
            total_videos += 1
        else:
            sys.stderr.write(f"Submission made by {student_names_ids[submission.user_id]} does not include a youtube link! Skipping...")
            return


def download_submission(submission):
    # look for youtube.com or youtu.be in the submission text, and then grab the whole url
    if "youtube.com" in submission.body:
        url = re.search("https://www.youtube.com/watch\?v=[a-zA-Z0-9_-]+", submission.body).group(0)
    elif "youtu.be" in submission.body:
        url = re.search("https://youtu.be/[a-zA-Z0-9_-]+", submission.text).group(0)

    # download video to current directory/assignment name
    try:
        video = YouTube(url, on_complete_callback=lambda x, y: show_progress(video))
        download_queue.append(video)
    except:
        sys.stderr.write(f"Error downloading video for submission made by {student_names_ids[submission.user_id]}! Skipping...")
        return

    stream = video.streams.filter(progressive=True, file_extension="mp4").last()
    stream.download(output_path=f"{video_path}", filename=f"{submission.user_id}.mp4")

def show_progress(video):
    # clear the screen  
    #os.system("clear")
    # print the progress
    download_queue.remove(video)
    sys.stdout.write(f"Downloading submission videos... [{total_videos - len(download_queue)}/{total_videos}]\n")

    # if all videos have been downloaded, start the combine.py script
    if len(download_queue) == 0:
        start_combine()

def start_combine():
    # start the combine.py script
    combine.combine(video_path, student_names_ids)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 download.py <assignment_id>")
        sys.exit(1)
    init(sys.argv[1])

