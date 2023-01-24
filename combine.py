import moviepy.editor as mpy
import os
import sys
import json

names_and_times = {}

def combine(video_path, student_names_ids):
    # combine all videos in current directory/assignment name into a single video
    sys.stdout.write("Combining videos...\n")

    videos = os.listdir(f"{video_path}")
    current_length = 0

    # create a list of video clips
    clips = []
    for video in videos:
        clip = mpy.VideoFileClip(f"{video_path}/{video}")
        id = int(video[:-4])

        # put the name of the student over the video clip
        text = mpy.TextClip(student_names_ids[id], fontsize=25, color="purple")
        text = text.set_pos("bottom").set_duration(clip.duration)
        clip = mpy.CompositeVideoClip([clip, text])

        # add the length of the video to the names_and_times dictionary
        current_length += clip.duration
        names_and_times[student_names_ids[id]] = [int((current_length - clip.duration) * 1000), int(current_length * 1000), id]

        clips.append(clip)

    # concatenate all clips
    final_clip = mpy.concatenate_videoclips(clips=clips, method="compose")

    # write to file
    final_clip.write_videofile(f"{video_path}/COMBINED.mp4")

    # serialize names_and_times to a new json file
    with open(f"{video_path}/names_and_times.json", "x") as f:
        f.write(json.dumps(names_and_times))

    sys.stdout.write(f"Done! Video saved to {video_path}/COMBINED.mp4\nYou can play it by running 'python3 play.py \'{video_path}\''.")