
from __future__ import print_function

import flickrapi
import os
import time
import datetime
import re
import urllib
import socket
import shutil
import ConfigParser

# timeout in seconds
timeout = 20
socket.setdefaulttimeout(timeout)

CONFIG_FILE_NAME = '.flickrwall'
CONFIG_SECTION = 'flickrwall'

def get_config():
    home = os.path.expanduser("~")
    path = os.path.join(home, CONFIG_FILE_NAME)
    o = dict(
        base_dir=os.path.join(home, 'Downloads', 'iWallpaper'),
        download_nr=20,
        flush_days=30,
    )
    if os.path.isfile(path):
        c = ConfigParser.ConfigParser()
        c.read(path)
        o.update(dict(c.items(CONFIG_SECTION)))
    o['download_nr'] = int(o['download_nr'])
    o['flush_days'] = int(o['flush_days'])
    return o


def feed(o):
    """Infinite feed of interesting images.
    Only landscape images above a given size are considered.
    """
    flickr = flickrapi.FlickrAPI(o['api_key'])
    page = 1
    while True:
        sets = flickr.interestingness_getList(page=page, extras="url_o,original_format")
        photos = sets[0]
        for photo in photos:
            if 'url_o' in photo.attrib:
                w = int(photo.attrib['width_o'])
                h = int(photo.attrib['height_o'])
                if w >= 1920 and h >= 1080 and w > h:
                    yield photo
        page += 1


def download(o):
    """Download a number of new images
    """
    re_filename = re.compile(r'\W+')
    downloaded = 0
    for i, photo in enumerate(feed(o)):
        kw = photo.attrib
        safe_title = re_filename.sub('_', kw['title'])
        file_name = safe_title + '_%(id)s.%(originalformat)s' % kw
        path = os.path.abspath(os.path.join(o['base_dir'], file_name))
        if not os.path.exists(path):
            try:
                tmp_path, _headers = urllib.urlretrieve(kw['url_o'])
                downloaded += 1
                print("NEW (%s)" % (file_name, ))
            except urllib.ContentTooShortError:
                print("ERR (ContentTooShortError) (%s)" % (file_name, ))
            except socket.timeout:
                print("ERR (timeout) (%s)" % (file_name, ))
            else:
                shutil.move(tmp_path, path)
        else:
            print("HIT (%s)" % (file_name, ))
        #print photo.attrib['url_o']
        if downloaded >= o['download_nr']:
            break

    # http://farm{farm-id}.staticflickr.com/{server-id}/{id}_{o-secret}_o.(jpg|gif|png)


def flush(o):
    now = time.time()
    for file_name in os.listdir(o['base_dir']):
        fullpath = os.path.join(o['base_dir'], file_name)
        if os.stat(fullpath).st_mtime < (now - o['flush_days'] * 86400):
            if os.path.isfile(fullpath):
                print("DEL (%s)" % (file_name, ))
                os.remove(fullpath)


def main():
    ts_begin = datetime.datetime.now()
    print('BEGIN RUN:', ts_begin);
    o = get_config()
    flush(o)
    download(o)
    ts_end = datetime.datetime.now()
    print('END RUN, elapsed time:', ts_end - ts_begin);


if __name__ == '__main__':
    main()
