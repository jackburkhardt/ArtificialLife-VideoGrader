# ArtificialLife-VideoGrader

A tool that speeds up grading video submissions for the Artificial Life course at Northwestern University.

## Requirements
- Python 3.10 (untested on other versions)
- [ffmpeg](https://ffmpeg.org/download.html)
- [ImageMagick](https://imagemagick.org/script/download.php)
- pip packages: `moviepy`, `canvasapi`, `dotenv`, `pytube`

## Setup
1. Clone this repository
2. Create a `.env` file in the root directory of the repository with the following contents:
```
CANVAS_API_URL=
CANVAS_API_KEY=
COURSE_ID=
```
Note that for Northwestern, the Canvas API url is simply the base URL (https://canvas.northwestern.edu), and the course ID can be found in the URL of the course page (e.g. https://canvas.northwestern.edu/courses/123456). You can create an API key by going to your Canvas profile settings and clicking "New Access Token".

3. Install everything in the requirements section, if not already one
4. Run `py fetch.py (assignment id)`!

## How it works
`fetch.py` will go into Canvas and download all of the submissions for an assignment by the given ID. It then parses out the YouTube link that students should have included, and download the YouTube videos to the working directory. Once this process is finished, `combine.py` will automatically start up. It takes all of the downloaded video clips and puts the student's name on top, then combines them into one video. Although the program attempts to utilize multithreading, this process can still take some time. Go ahead and grab a snack.

To play the video (and grade the assignment), simply run `py play.py \'(assignment id)\'` (note the quotes). This will open up a video player which plays the combined video. As the video is playing, you can use the following commands in the terminal window:
- `n` to skip to the next student
- `p` to go back to the previous student
- `g (num)` to assign a grade of num to that student
- `exit` to exit the video player

Once exited or all videos are done, you can close the video window and the program will ask if you'd like to submit grades. You can use the following commands:
- `list` to list all students and their grades
- `submit (assignment id)` to send the grades to Canvas
- `exit` to exit the program without submitting grades (NOTE: grades will not be saved if you exit without submitting! you will have to regrade!)

 
