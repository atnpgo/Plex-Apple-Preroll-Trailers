import json
import os
import shutil
import socket
import sys

from mix import mix
from mix import getSettings

from urllib.request import *
from urllib.error import *

# Python-PlexAPI
try:
    from plexapi.server import PlexServer
except:
    print('\033[91mERROR:\033[0m PlexAPI is not installed.')
    sys.exit()

# Remove special characters
def removeSpecialChars(string):
    return string.replace('/', '').replace('\\', '').replace(':', '').replace('*', '').replace('?', '').replace('"', "'") \
        .replace('<', '').replace('>', '').replace(',', '').replace('|', '')


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

    final = []

    if len(urls) > 1:
        # Use newest trailer
        final.append(urls[0])
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
        with open(destdir + '/' + filename, 'wb') as local_file_handle:
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
    # Fetch from sources
    just_added = loadJson('https://trailers.apple.com/trailers/home/feeds/just_added.json')
    box_office = loadJson('https://trailers.apple.com/trailers/home/feeds/popular/most_pop.json')['items'][1]['thumbnails']
    opening = loadJson('https://trailers.apple.com/trailers/home/feeds/opening.json')['items'][0]['thumbnails']
    # Combine sources
    results = []
    selections = []
    count = 0
    while count <= len(just_added) - 1:
        if count <= len(just_added) - 1 and just_added[count]['title'] not in selections:
            just_added[count]['location'] = 'https://trailers.apple.com' + just_added[count]['location']
            results.append(just_added[count])
            selections.append(just_added[count]['title'])
        if count <= len(box_office) - 1 and box_office[count]['title'] not in selections:
            box_office[count]['location'] = box_office[count]['url']
            results.append(box_office[count])
            selections.append(box_office[count]['title'])
        if count <= len(opening) - 1 and opening[count]['title'] not in selections:
            opening[count]['location'] = 'https://trailers.apple.com' + opening[count]['url']
            results.append(opening[count])
            selections.append(opening[count]['title'])
        count += 1
    return results


# Delete old files
def deleteOldFiles(destdir, downloads):
    # Iterate through downloaded files
    for item in os.listdir(destdir):
        # Make sure the item is a file
        if os.path.isfile(destdir + '/' + item):
            # Delete any file that wasn't just downloaded
            if destdir + '/' + item not in downloads:
                os.remove(destdir + '/' + item)


# Main
def main():
    # Settings
    settings = getSettings()

    # Search Apple for trailers
    search = searchApple()

    # Downloads
    downloads = []

    # Iterate over search results and download
    for item in search:

        # Make sure file has not already been downloaded
        if not os.path.exists(settings['download_path'] + '/' + removeSpecialChars(item['title']) + ' (Trailer).mp4'):

            # Download
            file = appleDownload(item['location'], settings['resolution'], settings['download_path'], removeSpecialChars(item['title']) + ' (Trailer).mp4')

            # Add to download count
            if file:
                downloads.append(settings['download_path'] + '/' + file)

        # Add to download count
        else:
            downloads.append(settings['download_path'] + '/' + removeSpecialChars(item['title']) + ' (Trailer).mp4')

        if len(downloads) >= int(settings['download_number']):
            break

    # Delete old trailers
    deleteOldFiles(settings['download_path'], downloads)
    mix()


# Run
if __name__ == '__main__':
    main()
