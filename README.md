
# flickrwall #

It's a program for MacOSX to provide desktop background and screensaver from
Flickr's interesting images.


## Why? ##

MacOSX supports desktop background and screensaver images to be taken randomly
from a selected folder. This application downloads images from Flickr that
then can be set up to work natively with MacOSX built in mechanism.

I looked at a few commercial applications that do this. But none of
them was doing exactly what I wanted, also they work a bit overpriced to
the little what they provided. So I decided to make my own app and share
it in the hope that others will find it useful.

## Installation ##

XXX ... install the app into Python

Then run:

```shell
    $ bin/python flickrwall-install.py
```

This will

- generate a configuration file on location `~/.flickrwall`

- generate a `.plist` file in `~/Library/LaunchAgents/local.flickrwall.plist`

- load or reload this `.plist` file with `launchtl`


If you run this for the first time, it will prompt for your Flickr API key
and secret.
You can also specify your api key and secret as parameters
to the install script.

```shell
    $ bin/python flickrwall-install.py <YOUR-API-KEY> <YOUR-API-SECRET>
```

You can change the parameters laters by editing the `.flickrwall` configuration
file. After changing it, you need to run `flickrwall-install.py` again
to update and reload the launchctl daemon.

XXX ... set up the screensaver and the desktop wallpaper to use the
```~/Downloads/iWallpaper``` folder.

XXX Changing preferences in ~/.flickrwall

```
[flickrwall]
# Do not change these
logfile_err = /Users/ree/work/flickrwall/flickrwall_err.log
api_secret = 36bedee48e462d32
logfile_out = /Users/ree/work/flickrwall/flickrwall_out.log
launch_minute = 25
launch_hour = 4
api_key = 4cf2083c87757bfd8e8ca162db86b6d0
base_dir = /Users/ree/Documents/iWallpaper

# Adjustable preferences
download_nr = 25
flush_days = 10
min_width = 5120
min_height = 2880
```


## About the Flickr API key ##

Why do you need your own Flickr API key? Because the app needs one, but I
cannot publish my own key with it, as this code is open sourced.
You need to use your own key which you can generate from the Flickr website.

