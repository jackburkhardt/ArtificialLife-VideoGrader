from pytube import YouTube
import os
import sys
from canvasapi import Canvas
import combine
import threading

API_URL = os.getenv("CANVAS_API_URL")
API_KEY = os.getenv("CANVAS_API_KEY")
COURSE_ID = os.getenv("COURSE_ID")

canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course(COURSE_ID)
assignment = None
submissions = []

total_videos = 0
download_queue = []

student_names_ids = {}

def init(id):
    global assignment
    assignment = course.get_assignment(id)
    download_submissions()

def download_submissions():
    global submissions
    submissions = assignment.get_submissions()
    try:
        os.mkdir(f"{os.getcwd()}/{assignment.name}")
    except:
        sys.stderr.write("Error creating directory for video output!")
        sys.exit(1)

    for submission in submissions:
        # if already graded, skip
        if submission.score is not None: continue

        # if submission is url and url is youtube, download video asynchronously
        if submission.submission_type == "online_url" and ("youtube" in submission.url or "youtu.be" in submission.url):
            student_names_ids[submission.user_id] = canvas.get_user(submission.user_id).name
            threading.Thread(target=download_submission, args=(submission,)).start()
            global total_videos
            total_videos += 1
        else:
            submission.add_comment("Hi! Please submit a YouTube link to your video.")
    while len(download_queue) > 0:
        show_progress()


def download_submission(submission):
    # download video to current directory/assignment name
    try:
        video = YouTube(submission.url, on_complete_callback=lambda: download_queue.remove(video))
        download_queue.append(video)
    except:
        sys.stderr.write(f"Error downloading video for submission made by {submission.user_id}! Skipping...")
        return

    stream = video.streams.filter(progressive=True, file_extension="mp4").last()
    stream.download(output_path=f"{os.getcwd()}/{assignment.name}", filename=f"{video.title}_{submission.user_id}")

def show_progress():
    # clear the screen
    #os.system("clear")
    # print the progress
    sys.stdout.write(f"Downloading submission videos... [{total_videos - len(download_queue)}/{total_videos}]\n")

def start_combine():
    # start the combine.py script
    combine.combine()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 download.py <assignment_id>")
        sys.exit(1)
    init(sys.argv[1])

