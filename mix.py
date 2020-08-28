import glob
import os
import random
import sys
from configparser import *

TRIVIA_INTRO = 'trivia_intro'
TRIVIA = 'trivia'
TRIVIA_OUTRO = 'trivia_outro'
THEATRE_INTRO = 'theatre_intro'
TRAILERS_INTRO = 'trailers_intro'
SPONSOR_INTRO = 'sponsor_intro'
SPONSOR = 'sponsor'
COUNTDOWN = 'countdown'
FEATURE_PRESENTATION = 'feature_presentation'

DOWNLOAD_PATH = 'download_path'
DEFAULT = 'DEFAULT'
DOWNLOAD_NUMBER = 'download_number'
MIX_NUMBER = 'mix_number'
PLEX_URL = 'plex_url'
PLEX_TOKEN = 'plex_token'
TRAILER_FOLDER_PATH = 'trailer_folder_path'

try:
    from plexapi.server import PlexServer
except:
    print('\033[91mERROR:\033[0m PlexAPI is not installed.')
    sys.exit()


# Settings
def getSettings():
    config = ConfigParser()
    config.read(os.path.split(os.path.abspath(__file__))[0] + '/settings.ini')
    return {
        DOWNLOAD_NUMBER: config.get(DEFAULT, DOWNLOAD_NUMBER),
        MIX_NUMBER: config.get(DEFAULT, MIX_NUMBER),
        PLEX_URL: config.get(DEFAULT, PLEX_URL),
        PLEX_TOKEN: config.get(DEFAULT, PLEX_TOKEN),

        TRAILER_FOLDER_PATH: os.path.split(os.path.abspath(__file__))[0] + '/trailers',
        DOWNLOAD_PATH: os.path.split(os.path.abspath(__file__))[0] + '/trailers',
        TRIVIA_INTRO: os.path.split(os.path.abspath(__file__))[0] + '/trivia_intro',
        TRIVIA: config.get(DEFAULT, TRIVIA),
        TRIVIA_OUTRO: os.path.split(os.path.abspath(__file__))[0] + '/trivia_outro',
        THEATRE_INTRO: os.path.split(os.path.abspath(__file__))[0] + '/theatre_intro',
        TRAILERS_INTRO: os.path.split(os.path.abspath(__file__))[0] + '/trailers_intro',
        SPONSOR_INTRO: os.path.split(os.path.abspath(__file__))[0] + '/sponsor_intro',
        SPONSOR: os.path.split(os.path.abspath(__file__))[0] + '/sponsor',
        COUNTDOWN: os.path.split(os.path.abspath(__file__))[0] + '/countdown',
        FEATURE_PRESENTATION: os.path.split(os.path.abspath(__file__))[0] + '/feature_presentation'
    }


def addItems(selections, settings, key, count=1):
    if settings[key] is not None:
        if os.path.isfile(settings[key]):
            selections.append(settings[key])
        elif os.path.isdir(settings[key]):
            if len(os.listdir(settings[key])) > count:
                for item in random.sample(glob.glob(os.path.join(settings[key], '*')), count):
                    selections.append(item)


def mix():
    # Settings
    settings = getSettings()
    # Make sure the download path exists
    if os.path.exists(settings[DOWNLOAD_PATH]):
        # Selections
        selections = []

        # Mix preroll trailers
        try:
            addItems(selections, settings, TRIVIA_INTRO)
            addItems(selections, settings, TRIVIA)
            addItems(selections, settings, TRIVIA_OUTRO)
            addItems(selections, settings, THEATRE_INTRO)
            addItems(selections, settings, TRAILERS_INTRO)
            addItems(selections, settings, DOWNLOAD_PATH, int(settings[MIX_NUMBER]))  # add trailers
            addItems(selections, settings, SPONSOR_INTRO)
            addItems(selections, settings, SPONSOR)
            addItems(selections, settings, FEATURE_PRESENTATION)

            # Add selected preroll trailers to Plex
            try:
                plex = PlexServer(settings[PLEX_URL], settings[PLEX_TOKEN])
                plex_settings = plex.settings.get('CinemaTrailersPrerollID')
                plex_settings.set(str(','.join(selections)))
                plex.settings.save()

            except:
                print('\033[91mERROR:\033[0m Failed to connect to Plex. Check your url and token.')

        except ValueError as error:
            print('\033[91mERROR:\033[0m No trailers have been downloaded yet.')
            print(error)

    else:
        print('\033[91mERROR:\033[0m No trailers have been downloaded yet.')


# Main
def main():
    mix()


# Run
if __name__ == '__main__':
    main()
