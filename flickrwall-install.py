
from __future__ import print_function

import sys
import os
import plistlib
import ConfigParser
import subprocess

from flickrwall import (
    CONFIG_FILE_NAME,
    CONFIG_SECTION,
    get_config,
    here_path,
)


def gen_plist(o):
    here = here_path()
    plist_path = os.path.expanduser('~/Library/LaunchAgents/local.flickrwall.plist')
    plist = {}
    plist['RunAtLoad'] = True
    plist['Label'] = 'local.flickrwall'
    plist['StandardOutPath'] = o['logfile_out']
    plist['StandardErrorPath'] = o['logfile_err']
    plist['StartCalendarInterval'] = dict(Hour=o['launch_hour'], Minute=o['launch_minute'])
    plist['ProgramArguments'] = [
        os.path.join(here, 'bin', 'python'),
        os.path.join(here, 'flickrwall.py'),
    ]
    plistlib.writePlist(plist, plist_path)
    subprocess.call(['launchctl', 'unload', '-w', plist_path])
    subprocess.call(['launchctl', 'load', '-w', plist_path])


def gen_config(**kw):
    o = get_config()
    o.update(**kw)
    if not 'api_key' in o:
        o['api_key'] = raw_input('Please enter your Flickr API key: ')
    home = os.path.expanduser("~")
    path = os.path.join(home, CONFIG_FILE_NAME)
    c = ConfigParser.ConfigParser()
    c.add_section(CONFIG_SECTION)
    for key, value in o.iteritems():
        c.set(CONFIG_SECTION, key, value)
    c.write(open(path, 'w'))
    return o


def main():
    args = sys.argv[1:]
    kw = {}
    if len(args) >= 1:
        kw['api_key'] = args[0]
    o = gen_config(**kw)
    gen_plist(o)


if __name__ == '__main__':
    main()
