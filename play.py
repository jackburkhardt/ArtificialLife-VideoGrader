import vlc
import sys
import os
import json
import time
import fetch

vlc_player = None
names_and_times = None

grades = {}

def play():
    # play video
    global vlc_player
    vlc_player.play()

    sys.stdout.write("Video playing. Press 'n' to skip to the next student, 'p' to skip to the previous student, 'g <grade>' to set the grade, or 'exit' to exit.\n")

    # every second, check if the video is playing
    while vlc_player.is_playing():
        # if it is, get the current time
        current_time = vlc_player.get_time()
        # convert to seconds
        current_time = current_time / 1000

        os.system("clear")

        # loop through names_and_times and check between each time
        for name, times in names_and_times.items():
            # if the current time is between the start and end time, print the name
            if current_time >= times[0] and current_time <= times[1]:
                sys.stdout.write(f"Currently viewing: {name}\n")
                # accept input for the grade
                grade = input("Enter command: ")
                # command for setting grade: g <grade>
                if grade.startswith("g ") and len(grade.split(" ")) == 2:
                    grades[name] = grade.split(" ")[1]
                # command for skipping to next student: n
                elif grade == "n":
                    vlc_player.set_time(times[1] * 1000)
                    break
                # command for skipping to previous student: p
                elif grade == "p":
                    vlc_player.set_time(times[0] * 1000)
                    break
                # command for quitting: exit
                elif grade == "exit":
                    sys.exit(0)
            

             # sleep for 1 second
        time.sleep(1)

    # when the video is done playing, submit the grades
    final_prompt()


def final_prompt():
    i = input("Video playback done! Type 'list' to see the grades, 'submit' to submit them to Canvas, or 'exit' to exit.")

    if i == "list":
        for name, grade in grades.items():
            sys.stdout.write(f"{name}: {grade}\n")
            final_prompt()
    elif i == "submit":
        submit()
    elif i == "exit":
        sys.exit(0)


def submit():

    # loop through the grades and submit them
    for name, grade in grades.items():
        # get the user id from the name
        user_id = fetch.student_names_ids[name]
        # get the submission
        submission = fetch.submissions[user_id]

        # submit the grade
        submission.edit(submission={"posted_grade": grade})

if __name__ == "__main__":

    # get video path from command line
    path = sys.argv[1]

    # check if video exists
    if not os.path.exists(path):
        sys.stderr.write("Error: Video not found at the given path!")
        sys.exit(1)

    # create vlc player
    vlc_player = vlc.MediaPlayer(path)

    # open the names and times txt file, deserialize it, and set the global variable
    with open(f"{os.getcwd()}/{path}/names_and_times.json", "r") as f:
        names_and_times = json.loads(f.read())

    play()