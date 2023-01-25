import vlc
import sys
import os
import json
from dotenv import load_dotenv
from canvasapi import Canvas

vlc_player = None
assignment_id = None

videos = []
curr = 0

grades = {}
ids_to_names = {}

def play(id):
    global vlc_player

    # if id is None, we are not playing another video. keep playing!
    if id == None:
        cmd = input("Enter command: \n")
        do_command(cmd, videos[curr])

    # create vlc player if it doesn't exist
    if vlc_player is None:
        vlc_player = vlc.MediaPlayer()

    # play video at path id
    vlc_player.set_mrl(f"{os.getcwd()}/{path}/{id}.mp4")
    vlc_player.play()

    sys.stdout.write(f"Currently viewing: {ids_to_names[id]}.\nPress 'n' to skip to the next student, 'p' to skip to the previous student, 'g <grade>' to set the grade, or 'exit' to exit.\n")
    cmd = input("Enter command: \n")
    do_command(cmd, id)
   

def do_command(cmd, id):
    global curr
    
    if cmd.startswith("g ") and len(cmd.split(" ")) == 2:
        name = ids_to_names[id]
        grade = cmd.split(" ")[1]
        
        # check if grade is float or int
        try:
            float(grade)
        except ValueError:
            sys.stdout.write("Error: Invalid grade! Please enter a number.\n")
            play(None)
        grades[id] = grade
        sys.stdout.write(f"Set grade for {name} to {grades[id]}.\n")
        
        # skip to next student
        if curr + 1 >= len(videos):
            vlc_player.stop()
            sys.stdout.write("Finished playing the last submission.\n")
            final_prompt()
        else:
            curr += 1
            play(videos[curr])
    
    # command for skipping to next student: n
    elif cmd == "n":
        sys.stdout.write("Skipping to next student...\n")
        if curr + 1 >= len(videos):
            sys.stdout.write("Already playing the last submission!\n")
            play(None)
        curr += 1
        play(videos[curr])
    
    # command for skipping to previous student: p
    elif cmd == "p":
        sys.stdout.write("Skipping to previous student...\n")
        if curr - 1 < 0:
            sys.stdout.write("Already playing the first submission!\n")
            play(None)
        curr -= 1
        play(videos[curr])
    
    # command for quitting: exit
    elif cmd == "exit":
        sys.stdout.write("Exiting playback...\n")
        vlc_player.stop()
        final_prompt()

    else:
        sys.stdout.write("Invalid command!\n")
        play(None)

def final_prompt():
    i = input("Type 'list' to see the grades, 'submit <assignment id>' to submit them to Canvas, 'replay' to play the videos again, or 'exit' to exit.\n")

    if i == "list":
        for id, grade in grades.items():
            sys.stdout.write(f"{ids_to_names[id]}: {grade}\n")
        final_prompt()
    elif i.startswith("submit") and len(i.split(" ")) == 2:
        submit(int(i.split(" ")[1]))
    elif i == "exit":
        sys.stdout.write("Exiting...\n")
        with open(f"{path}/grades.json", "w") as f:
            f.write(json.dumps(grades))
        sys.exit(0)
    elif i == "replay":
        curr = 0
        play(videos[curr])
    else:
        sys.stdout.write("Invalid command!\n")
        final_prompt()


def submit(id):

    sys.stdout.write("Submitting grades to Canvas...\n")
    
    load_dotenv()
    canvas = Canvas(os.getenv("CANVAS_API_URL"), os.getenv("CANVAS_API_KEY"))
    course = canvas.get_course(os.getenv("COURSE_ID"))
    assignment = course.get_assignment(id)

    # loop through the grades and submit them
    for id, grade in grades.items():
        submission = assignment.get_submission(id)
        submission.edit(submission={"posted_grade": grade})

    sys.stdout.write("Successfully submitted grades!\n")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Error: Invalid number of arguments! Usage: py play.py <assignment id>")
        sys.exit(1)

    # get video path from command line
    path = str(sys.argv[1])

    # check if videos exist
    if not os.path.exists(path):
        sys.stderr.write("Error: Videos not found at the given path!")
        sys.exit(1)

    # list the videos within the directory without the extension
    videos = [f.split(".")[0] for f in os.listdir(path) if f.endswith(".mp4")]

    # open the names and times txt file, deserialize it, and set the global variable
    with open(f"{path}/ids_to_names.json", "r") as f:
        ids_to_names = json.loads(f.read())

    # if there are grades already, load them
    if os.path.exists(f"{path}/grades.json"):
        with open(f"{path}/grades.json", "r") as f:
            grades = json.loads(f.read())

    play(videos[curr])