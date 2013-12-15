
from __future__ import print_function

import sys
import os
import plistlib


def here_path():
    return os.path.abspath(os.path.dirname(sys.modules[__name__].__file__))

def gen_plist(api_key=None):
    here = here_path()
    plist_path = os.path.expanduser('~/Library/LaunchAgents/local.flickrwall.plist')
    if api_key is None:
        try:
            plist = plistlib.readPlist(plist_path)
        except Exception:
            pass
        else:
            try:
                api_key = plist['ProgramArguments'][2]
            except (IndexError, KeyError):
                pass
    if not api_key:
        api_key = input('Please enter your Flickr API key: ')
    plist = {}
    plist['RunAtLoad'] = True
    plist['Label'] = 'local.flickrwall'
    plist['StandardOutPath'] = os.path.join(here, 'flickrwall_out.log')
    plist['StandardErrorPath'] = os.path.join(here, 'flickrwall_err.log')
    plist['StartCalendarInterval'] = dict(Hour=4, Minute=34)
    plist['ProgramArguments'] = [
        os.path.join(here, 'bin', 'python'),
        os.path.join(here, 'flickrwall.py'),
        api_key,
    ]
    plistlib.writePlist(plist, plist_path)


def main():
    args = sys.argv[1:]
    api_key = args[0] if len(args) >= 1 else None
    gen_plist(api_key=api_key)


if __name__ == '__main__':
    main()
