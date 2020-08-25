# Plex-Apple-Preroll-Trailers
A set of python scripts for downloading upcoming trailers from Apple, randomly mixing them each time a movie is played, and playing them before movies in Plex as preroll trailers.

Forked and modified from [Plex-Apple-Preroll-Trailers](https://github.com/airship-david/Plex-Apple-Preroll-Trailers) to whom most of the credit belongs.

## Requirements

You will need to install these yourself but the installations should be fairly straightforward.

* [Python 3+](https://www.python.org/)

* [PlexAPI](https://github.com/pkkid/python-plexapi)

* [Tautulli](https://github.com/Tautulli/Tautulli) for automatically mixing trailers
    - If using the mac OS version, I recommend avoiding the .pkg installer since it bundles it's own version of python. 


## Settings
Edit the **settings.ini** file. Here you can add your url and token for Plex, resolution settings, number of trailers to download, number of trailers to mix, an optional feature presentation video folder, an optional intro video, and an optional pre-roll trivia video.

* `feature_presentation_path` a path to a folder containing one or more feature presentation video. If present, a random video in the folder will be played after the trailers but before the movie. 
* `intros_path` a path to a folder containing one or more intro video. If present, a random video in the folder will be played right before the trailers.
* `trivia_video_path` a path to a trivia style video to be played before the intro video, similar to the slideshows shown in movie theatres before the trailers start. See my [PlexScripts](https://github.com/atnpgo/PlexScripts) repo, more specifically the `trivia-gen.sh`, `slide-to-vid.sh` and `slide-merger.sh` scripts, to see how to create your own.

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

## Running For The First Time

Since you just set up the scripts for the first time, you don't have any trailers downloaded yet so you need to manually run the script one time.

```
python /path/to/scripts/download.py
```

Enjoy!
