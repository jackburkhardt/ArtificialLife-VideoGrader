import vlc
import sys
import os
import json
import time
from dotenv import load_dotenv
from canvasapi import Canvas

vlc_player = None
names_and_times = None
assignment_id = None

grades = {}

def play():
    # play video
    global vlc_player
    vlc_player.play()

    sys.stdout.write("Video playing. Press 'n' to skip to the next student, 'p' to skip to the previous student, 'g <grade>' to set the grade, or 'exit' to exit.\n")

    # every second, check if the video is open 
    while vlc_player:
        # if it is, get the current time
        current_time = vlc_player.get_time()

        # loop through names_and_times and check between each time
        for name, times in names_and_times.items():
            # if the current time is between the start and end time, print the name
            if current_time >= times[0] and current_time <= times[1]:
                sys.stdout.write(f"Currently viewing: {name}\n")
                # accept input for the grade
                grade = input("Enter command: \n")
                # command for setting grade: g <grade>
                if grade.startswith("g ") and len(grade.split(" ")) == 2:
                    grades[name] = grade.split(" ")[1]
                    sys.stdout.write(f"Set grade for {name} to {grade.split(' ')[1]}.\n")
                # command for skipping to next student: n
                elif grade == "n":
                    sys.stdout.write("Skipping to next student...\n")
                    vlc_player.set_time(int(times[1]))
                    break
                # command for skipping to previous student: p
                elif grade == "p":
                    sys.stdout.write("Skipping to previous student...\n")
                    vlc_player.set_time(int(times[0]))
                    break
                # command for quitting: exit
                elif grade == "exit":
                    sys.stdout.write("Exiting playback...\n")
                    vlc_player.stop()
                    final_prompt()
            

             # sleep for 1 second
        time.sleep(1)

    # when the video is done playing, submit the grades
    final_prompt()


def final_prompt():
    i = input("Type 'list' to see the grades, 'submit <assignment id>' to submit them to Canvas, or 'exit' to exit.\n")

    if i == "list":
        for name, grade in grades.items():
            sys.stdout.write(f"{name}: {grade}\n")
        final_prompt()
    elif i.startswith("submit") and len(i.split(" ")) == 2:
        submit(int(i.split(" ")[1]))
    elif i == "exit":
        sys.exit(0)


def submit(id):
    
    load_dotenv()
    canvas = Canvas(os.getenv("CANVAS_API_URL"), os.getenv("CANVAS_API_KEY"))
    course = canvas.get_course(os.getenv("COURSE_ID"))
    assignment = course.get_assignment(id)

    # loop through the grades and submit them
    for name, grade in grades.items():
        # get the user id from the name
        user_id = names_and_times[name][2]
        # get the submission
        submission = assignment.get_submission(user_id)

        # submit the grade
        submission.edit(submission={"posted_grade": grade})

if __name__ == "__main__":

    # get video path from command line
    path = str(sys.argv[1])

    # check if video exists
    if not os.path.exists(path):
        sys.stderr.write("Error: Video not found at the given path!")
        sys.exit(1)

    # create vlc player
    vlc_player = vlc.MediaPlayer(f"{os.getcwd()}/{path}/COMBINED.mp4")

    # open the names and times txt file, deserialize it, and set the global variable
    with open(f"{path}/names_and_times.json", "r") as f:
        names_and_times = json.loads(f.read())

    play()