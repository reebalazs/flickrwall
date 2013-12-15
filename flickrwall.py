
from __future__ import print_function

import flickrapi
import os
import sys
import time
import datetime
import re
import urllib
import socket
import shutil

# timeout in seconds
timeout = 20
socket.setdefaulttimeout(timeout)

def feed(api_key):
    """Infinite feed of interesting images.
    Only landscape images above a given size are considered.
    """
    flickr = flickrapi.FlickrAPI(api_key)
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


def download(base_dir, api_key, nr=20):
    """Download a number of new images
    """
    re_filename = re.compile(r'\W+')
    downloaded = 0
    for i, photo in enumerate(feed(api_key)):
        kw = photo.attrib
        safe_title = re_filename.sub('_', kw['title'])
        file_name = safe_title + '_%(id)s.%(originalformat)s' % kw
        path = os.path.abspath(os.path.join(base_dir, file_name))
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
        if downloaded >= nr:
            break

    # http://farm{farm-id}.staticflickr.com/{server-id}/{id}_{o-secret}_o.(jpg|gif|png)


def flush(base_dir, days=30):
    now = time.time()
    for file_name in os.listdir(base_dir):
        fullpath = os.path.join(base_dir, file_name)
        if os.stat(fullpath).st_mtime < (now - days * 86400):
            if os.path.isfile(fullpath):
                print("DEL (%s)" % (file_name, ))
                os.remove(fullpath)


def main():
    (api_key, ) = sys.argv[1:]
    base_dir = "/Users/ree/Downloads/iWallpaper"
    ts_begin = datetime.datetime.now()
    print('BEGIN RUN:', ts_begin);
    flush(base_dir, days=30)
    download(base_dir, api_key=api_key, nr=20)
    ts_end = datetime.datetime.now()
    print('END RUN, elapsed time:', ts_end - ts_begin);


if __name__ == '__main__':
    main()
