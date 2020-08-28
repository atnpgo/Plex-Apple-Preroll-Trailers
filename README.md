# Plex-Cinema-Experience-Preroll
A set of python scripts for downloading upcoming trailers from Apple, randomly mixing them each time a movie is played, and playing them before movies in Plex as preroll trailers.

Forked and modified from [Plex-Apple-Preroll-Trailers](https://github.com/airship-david/Plex-Apple-Preroll-Trailers) to whom most of the credit belongs.

## Requirements

You will need to install these yourself but the installations should be fairly straightforward.

* [Python 3+](https://www.python.org/)

* [PlexAPI](https://github.com/pkkid/python-plexapi)

* [Tautulli](https://github.com/Tautulli/Tautulli) for automatically mixing trailers
    - If using the mac OS version, I recommend avoiding the .pkg installer since it bundles it's own version of python which makes installing PlexAPI more difficult. 


## Settings
Edit the **settings.ini** file. Here you can add your url and token for Plex, resolution settings, number of trailers to download, number of trailers to mix, and several optional video steps.

For each of these values, you can point to either a directory or a file. If pointing to a file, that file will be played every time. If pointing to a folder, a random video will be played from that folder. 

For the `trivia` config, see my [PlexScripts](https://github.com/atnpgo/PlexScripts) repo, more specifically the `trivia-gen.sh`, `slide-to-vid.sh` and `slide-merger.sh` scripts, to see how to create your own.
Although any video should work.
 

## Usage

### Downloads

You need to schedule a job for downloading trailers each week. I find that once per week is totally sufficient if you have download_number set to a decent value like 40 in your settings.ini file.

**macOS or Linux:**

```
crontab -e
30 3 * * fri python /path/to/scripts/download.py 2>&1
```

**Windows:**

Open the Control Panel and navigate to Administrative Tools > Task Scheduler. Then click "Create Basic Task Scheduler" and enter a name and description. Then set the task to run weekly and choose a day and time. For the action, choose "Start a program." For the "Program/script" add the location of your python installation. For the "Arguments" add the full path of the download.py script in double quotes (example: `"C:\Users\username\Trailers\download.py"`). Click "Finish" and you're all set.

### Mixing

Open Tautulli and go to Settings > Notification Agents and add a new notification agent. The type should be "script" and you'll want to add the path to the folder the scripts are located in and select mix.py as your script in the configuration tab. Be sure to add a description for the script as well. Next, go to the triggers tab and check the box for "Playback Stop" and then go to the conditions tab and add a condition to only fire when "media type is movie". For the arguments tab, go to the "Playback Stop" section and add the code below. After that, be sure to save it and you're all set.

```
nopythonpath
```

### Config

This is the order in which the video steps will be played:

01. Trivia Intro
    * Plays a video from the `trivia_intro` folder 
02. Trivia
    * Plays a video from the `trivia` config
03. Trivia Outro
    * Plays a video from the `trivia_outro` folder
04. Theater Intro
    * Plays a video from the `theatre_intro` folder
05. Trailers Intro
    * Plays a video from the `trailers_intro` folder
06. Trailers
    * Plays `X` videos downloaded from the trailers website where `X` is the number specified in the `mix_number` config
07. Sponsor Intro
    * Plays a video from the `sponsor_intro` folder
08. Sponsor
    * Plays a video from the `sponsor` folder
09. Countdown Video
    * Plays a video from the `countdown` folder
10. Feature Presentation Intro
    * Plays a video from the `feature_presentation` folder
11. Feature Presentation
    * The film you selected to play
    
All steps except `Trailers` and `Feature Presentation` are optional. Simply leave the folders empty or the configuration blank. 

## Running For The First Time

Since you just set up the scripts for the first time, you don't have any trailers downloaded yet so you need to manually run the script one time.

```
python /path/to/scripts/download.py
```

Enjoy!
