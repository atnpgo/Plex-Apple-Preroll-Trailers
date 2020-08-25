import os
import random
import sys
from configparser import *

# Python-PlexAPI
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
        'download_number': config.get('DEFAULT', 'download_number'),
        'mix_number': config.get('DEFAULT', 'mix_number'),
        'plex_url': config.get('DEFAULT', 'plex_url'),
        'plex_token': config.get('DEFAULT', 'plex_token'),
        'trailer_folder_path': config.get('DEFAULT', 'trailer_folder_path'),
        'feature_presentation_path': config.get('DEFAULT', 'feature_presentation_path'),
        'intros_path': config.get('DEFAULT', 'intros_path'),
        'trivia_video_path': config.get('DEFAULT', 'trivia_video_path'),
        'download_path': os.path.split(os.path.abspath(__file__))[0] + '/Trailers'
    }


def mix():
    # Settings
    settings = getSettings()

    # Make sure the download path exists
    if os.path.exists(settings['download_path']):

        # Selections
        selections = []

        # Mix preroll trailers
        try:
            if settings['trivia_video_path'] is not None and os.path.isfile(settings['trivia_video_path']):
                selections.append(settings['trivia_video_path'])

            if os.path.exists(settings['intros_path']):
                for item in random.sample(os.listdir(settings['intros_path']), 1):
                    selections.append(settings['intros_path'] + '/' + item)

            # Make random selections
            for item in random.sample(os.listdir(settings['download_path']), int(settings['mix_number'])):
                selections.append(settings['download_path'] + '/' + item)

            # Add feature presentation video
            if os.path.exists(settings['feature_presentation_path']):
                for item in random.sample(os.listdir(settings['feature_presentation_path']), 1):
                    selections.append(settings['feature_presentation_path'] + '/' + item)

            # Add selected preroll trailers to Plex
            try:
                plex = PlexServer(settings['plex_url'], settings['plex_token'])
                plex_settings = plex.settings.get('CinemaTrailersPrerollID')
                plex_settings.set(str(','.join(selections)))
                plex.settings.save()

            except:
                print('\033[91mERROR:\033[0m Failed to connect to Plex. Check your url and token.')

        except ValueError as error:
            print('\033[91mERROR:\033[0m No trailers have been downloaded yet.')

    else:
        print('\033[91mERROR:\033[0m No trailers have been downloaded yet.')


# Main
def main():
    mix()


# Run
if __name__ == '__main__':
    main()
