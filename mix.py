from argparse import ArgumentParser
import os
import random
import sys

# Python 3.0 and later
try:
    from configparser import *

# Python 2.7
except ImportError:
    from ConfigParser import *

# Python-PlexAPI
try:
    from plexapi.server import PlexServer

except:
    print('\033[91mERROR:\033[0m PlexAPI is not installed.')
    sys.exit()

# Arguments
def getArguments():
    name = 'Plex-Apple-Preroll-Trailers'
    version = '2.02'
    parser = ArgumentParser(description='{}: mix upcoming trailers for Plex'.format(name))
    parser.add_argument("-v", "--version", action='version', version='{} {}'.format(name, version), help="show the version number and exit")
    args = parser.parse_args()

# Settings
def getSettings():
    config = ConfigParser()
    config.read(os.path.split(os.path.abspath(__file__))[0]+'/settings.ini')
    return {
        'download_number': config.get('DEFAULT', 'download_number'),
        'mix_number': config.get('DEFAULT', 'mix_number'),
        'plex_url': config.get('DEFAULT', 'plex_url'),
        'plex_token': config.get('DEFAULT', 'plex_token'),
        'feature_presentation': config.get('DEFAULT', 'feature_presentation'),
        'download_path': os.path.split(os.path.abspath(__file__))[0]+'/Trailers'
    }

# Main
def main():
    # Arguments
    arguments = getArguments()

    # Settings
    settings = getSettings()

    # Make sure the download path exists
    if os.path.exists(settings['download_path']):

        # Selections
        selections = []

        # Mix preroll trailers
        try:
            # Make random selections
            for item in random.sample(os.listdir(settings['download_path']), int(settings['mix_number'])):
                selections.append(os.path.join(settings['download_path'], item))

            # Add feature presentation video
            if settings['feature_presentation'] is not None and os.path.isfile(settings['feature_presentation']):
                selections.append(settings['feature_presentation'])

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

# Run
if __name__ == '__main__':
    main()