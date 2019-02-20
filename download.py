import json
import os
import random
import shutil
import socket
import sys

# Python 3.0 and later
try:
    from configparser import *
    from urllib.request import *
    from urllib.error import *

# Python 2.7
except ImportError:
    from ConfigParser import *
    from urllib2 import *

# Python-PlexAPI
try:
    from plexapi.server import PlexServer

except:
    print('\033[91mERROR:\033[0m PlexAPI is not installed.')
    sys.exit()

# Settings
def getSettings():
    config = ConfigParser()
    config.read(os.path.split(os.path.abspath(__file__))[0]+'/settings.ini')
    return {
        'resolution': config.get('DEFAULT', 'resolution'),
        'download_number': config.get('DEFAULT', 'download_number'),
        'mix_number': config.get('DEFAULT', 'mix_number'),
        'plex_url': config.get('DEFAULT', 'plex_url'),
        'plex_token': config.get('DEFAULT', 'plex_token'),
        'feature_presentation': config.get('DEFAULT', 'feature_presentation'),
        'download_path': os.path.split(os.path.abspath(__file__))[0]+'/Trailers'
    }

# Remove special characters
def removeSpecialChars(string):
    return string.replace('/', '').replace('\\', '').replace(':', '-').replace('*', '').replace('?', '').replace('"', "'").replace('<', '').replace('>', '').replace('|', '')

# Load json from url
def loadJson(url):
    response = urlopen(url)
    str_response = response.read().decode('utf-8')
    return json.loads(str_response)

# Get file urls
def getUrls(page_url, res):
    urls = []
    film_data = loadJson(page_url + '/data/page.json')
    title = film_data['page']['movie_title']
    apple_size = mapRes(res)

    # Find trailer
    for clip in film_data['clips']:
        video_type = clip['title']
        if apple_size in clip['versions']['enus']['sizes']:
            file_info = clip['versions']['enus']['sizes'][apple_size]
            file_url = convertUrl(file_info['src'], res)
            video_type = video_type.lower()
            if (video_type.startswith('trailer')):
                url_info = {
                    'res': res,
                    'title': title,
                    'type': video_type,
                    'url': file_url,
                }
                urls.append(url_info)

    # If no trailer, fall back to teaser
    if len(urls) == 0:
        for clip in film_data['clips']:
            video_type = clip['title']
            if apple_size in clip['versions']['enus']['sizes']:
                file_info = clip['versions']['enus']['sizes'][apple_size]
                file_url = convertUrl(file_info['src'], res)
                video_type = video_type.lower()
                if (video_type.startswith('teaser')):
                    url_info = {
                        'res': res,
                        'title': title,
                        'type': video_type,
                        'url': file_url,
                    }
                    urls.append(url_info)

    final = []
    length = len(urls)

    if length > 1:
        final.append(urls[length-1])
        return final
    else:
        return urls

# Map resolution
def mapRes(res):
    res_mapping = {'480': u'sd', '720': u'hd720', '1080': u'hd1080'}
    if res not in res_mapping:
        res_string = ', '.join(res_mapping.keys())
        raise ValueError("Invalid resolution. Valid values: %s" % res_string)
    return res_mapping[res]

# Convert source url to file url
def convertUrl(src_url, res):
    src_ending = "_%sp.mov" % res
    file_ending = "_h%sp.mov" % res
    return src_url.replace(src_ending, file_ending)

# Download the file
def downloadFile(url, destdir, filename):
    data = None
    headers = {'User-Agent': 'Quick_time/7.6.2'}
    req = Request(url, data, headers)
    chunk_size = 1024 * 1024

    try:
        server_file_handle = urlopen(req)
    except HTTPError as error:
        return
    except URLError as error:
        return
    try:
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        with open(destdir+'/'+filename, 'wb') as local_file_handle:
            shutil.copyfileobj(server_file_handle, local_file_handle, chunk_size)
    except socket.error as error:
        return

# Download from Apple
def appleDownload(page_url, res, destdir, filename):
    trailer_urls = getUrls(page_url, res)
    for trailer_url in trailer_urls:
        downloadFile(trailer_url['url'], destdir, filename)
        return filename

# Search Apple
def searchApple():
    search_url = 'https://trailers.apple.com/itunes/us/json/most_pop.json'
    return loadJson(search_url)

# Get movie details
def getDetails(page_url):
    data = loadJson(page_url + '/data/page.json')
    return data['page']

# Delete old files
def deleteOldFiles(destdir, downloads):
    # Iterate through downloaded files
    for item in os.listdir(destdir):
        # Make sure the item is a file
        if os.path.isfile(destdir+'/'+item):
            # Delete any file that wasn't just downloaded
            if destdir+'/'+item not in downloads:
                os.remove(destdir+'/'+item)

# Main
def main():
    # Settings
    settings = getSettings()

    # Search Apple for trailers
    search = searchApple()

    # Queue
    queue = []

    # Downloads
    downloads = []

    # Iterate over search results and prepare queue
    count = 0
    while len(queue) < int(settings['download_number']) and count < 25:

        # Box office
        if search['items'][1]['thumbnails'][count] != None and search['items'][1]['thumbnails'][count] not in queue and len(queue) < int(settings['download_number']):
            queue.append(search['items'][1]['thumbnails'][count])

        # Most popular
        if search['items'][0]['thumbnails'][count] != None and search['items'][0]['thumbnails'][count] not in queue and len(queue) < int(settings['download_number']):
            queue.append(search['items'][0]['thumbnails'][count])

        count += 1

    # Iterate over queue and download
    for item in queue:

        # Get details
        details = getDetails('https://trailers.apple.com'+item['url'])

        # Year
        if len(details['release_date']) >= 4:
            year = ' ('+details['release_date'][:4]+')'
        else:
            year = ''

        # Make sure file has not already been downloaded
        if not os.path.exists(settings['download_path']+'/'+removeSpecialChars(item['title'])+year+'.mp4'):

            # Download
            file = appleDownload('https://trailers.apple.com'+item['url'], settings['resolution'], settings['download_path'], removeSpecialChars(item['title'])+year+'.mp4')

            # Add to download count
            if file:
                downloads.append(settings['download_path']+'/'+file)

        # Add to download count
        else:
            downloads.append(settings['download_path']+'/'+removeSpecialChars(item['title'])+year+'.mp4')

    # Delete old trailers
    deleteOldFiles(settings['download_path'], downloads)

    # Make sure the download path exists
    if os.path.exists(settings['download_path']):

        # Selections
        selections = []

        # Use download number if mix number > download number
        if int(settings['mix_number']) < int(settings['download_number']):
            number = int(settings['mix_number'])

        else:
            number = int(settings['download_number'])

        # Mix preroll trailers
        try:
            # Make random selections
            rand = random.sample(os.listdir(settings['download_path']), number)
            for item in rand:
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