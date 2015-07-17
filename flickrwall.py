
import flickrapi
import os
import sys
import time
import datetime
import re
import httplib
import urllib
import urllib2
import socket
import shutil
import ConfigParser
import syslog
import tempfile

syslog.openlog('flickrwall')

# timeout in seconds
timeout = 20
socket.setdefaulttimeout(timeout)

CONFIG_FILE_NAME = '.flickrwall'
CONFIG_SECTION = 'flickrwall'


def here_path():
    return os.path.abspath(os.path.dirname(sys.modules[__name__].__file__))

def get_config():
    home = os.path.expanduser("~")
    path = os.path.join(home, CONFIG_FILE_NAME)
    here = here_path()
    o = dict(
        base_dir=os.path.join(home, 'Downloads', 'iWallpaper'),
        download_nr=20,
        flush_days=30,
        logfile_out=os.path.join(here, 'flickrwall_out.log'),
        logfile_err=os.path.join(here, 'flickrwall_err.log'),
        launch_hour=4,
        launch_minute=25,
        # HD
        # min_width=1920,
        # min_height=1080,
        # 5K
        min_width=5120,
        min_height=2880,
    )
    if os.path.isfile(path):
        c = ConfigParser.ConfigParser()
        c.read(path)
        o.update(dict(c.items(CONFIG_SECTION)))
    o['download_nr'] = int(o['download_nr'])
    o['flush_days'] = int(o['flush_days'])
    o['min_width'] = int(o['min_width'])
    o['min_height'] = int(o['min_height'])
    return o


def feed(o):
    """Infinite feed of interesting images.
    Only landscape images above a given size are considered.
    """
    flickr = flickrapi.FlickrAPI(o['api_key'], o['api_secret'])
    page = 1
    while page <= 5: # seems like there are only 5 pages
        sets = flickr.interestingness_getList(page=page, extras="url_o,original_format")
        photos = sets[0]
        for photo in photos:
            if 'url_o' in photo.attrib:
                w = int(photo.attrib['width_o'])
                h = int(photo.attrib['height_o'])
                if w >= o['min_width'] and h >= o['min_height'] and w > h:
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
            with tempfile.NamedTemporaryFile(dir='/tmp', delete=False) as tmpfile:
                try:
                    image = urllib2.urlopen(kw['url_o'])
                    out = file(tmpfile.name ,'wb')
                    out.write(image.read())
                    out.flush();
                    downloaded += 1
                    syslog.syslog(syslog.LOG_NOTICE, "NEW (%s)" % (file_name, ))
                except urllib2.HTTPError:
                    syslog.syslog(syslog.LOG_ERR, "ERR (HTTPError) (%s)" % (file_name, ))
                except urllib2.URLError:
                    syslog.syslog(syslog.LOG_ERR, "ERR (URLError) (%s)" % (file_name, ))
                except httplib.HTTPException:
                    syslog.syslog(syslog.LOG_ERR, "ERR (HTTPException) (%s)" % (file_name, ))
                except urllib.ContentTooShortError:
                    # ... probably not needed, since now we use urllib2.
                    syslog.syslog(syslog.LOG_ERR, "ERR (ContentTooShortError) (%s)" % (file_name, ))
                except socket.timeout:
                    syslog.syslog(syslog.LOG_ERR, "ERR (timeout) (%s)" % (file_name, ))
                else:
                    shutil.move(tmpfile.name, path)
        else:
            syslog.syslog(syslog.LOG_NOTICE, "HIT (%s)" % (file_name, ))
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
                syslog.syslog(syslog.LOG_NOTICE, "DEL (%s)"% (file_name, ))
                os.remove(fullpath)


def main():
    ts_begin = datetime.datetime.now()
    syslog.syslog(syslog.LOG_NOTICE, 'BEGIN RUN: %s' % (ts_begin, ))
    o = get_config()
    flush(o)
    download(o)
    ts_end = datetime.datetime.now()
    syslog.syslog(syslog.LOG_NOTICE, 'END RUN, elapsed time: %s' % (ts_end - ts_begin, ))


if __name__ == '__main__':
    main()
