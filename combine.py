import moviepy.editor as mpy
import fetch
import os
import sys
import json

names_and_times = {}

def combine():
    # combine all videos in current directory/assignment name into a single video
    sys.stdout.write("Combining videos... (no progress available)")

    # get all videos in current directory
    assignment = fetch.assignment
    student_names_ids = fetch.student_names_ids

    videos = os.listdir(f"{os.getcwd()}/{assignment.name}")
    current_length = 0

    # create a list of video clips
    clips = []
    for video in videos:
        clip = mpy.VideoFileClip(f"{os.getcwd()}/{assignment.name}/{video}")


        # put the name of the student over the video clip
        text = mpy.TextClip(student_names_ids[int(video.split("_")[1])], fontsize=25, color="purple")
        text = text.set_pos("bottom").set_duration(clip.duration)
        clip = mpy.CompositeVideoClip([clip, text])

        # add the length of the video to the names_and_times dictionary
        current_length += clip.duration
        names_and_times[student_names_ids[int(video.split("_")[1])]] = [current_length - clip.duration, current_length]

        clips.append(clip)

    # concatenate all clips
    final_clip = mpy.concatenate_videoclips(clips=clips, method="compose")

    # write to file
    final_clip.write_videofile(f"{os.getcwd()}/{assignment.name}/COMBINED.mp4")

    # serialize names_and_times to a new json file
    with open(f"{os.getcwd()}/{assignment.name}/names_and_times.json", "x") as f:
        f.write(json.dumps(names_and_times))

    sys.stdout.write(f"Done! Video saved to {os.getcwd()}/{assignment.name}/COMBINED.mp4\nYou can play it by running 'python3 play.py {assignment.name}/COMBINED.mp4'.")