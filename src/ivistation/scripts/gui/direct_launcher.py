"""
Launches custom tiles, or just any kind of .xbe files, really.

In comparison with xbox_launcher.py, the latter is focused on
games, and may include more features in the future.
"""

import os
import sys
import xbmc


def write_igr_file():
    try:
        # Create the cache folder
        if not os.path.isdir('E:\\CACHE'):
            os.makedirs('E:\\CACHE')

        with open("E:\\CACHE\\LocalCache20.bin", "w") as tmp:
            tmp.write(xbmc.translatePath("Special://root/default.xbe"))

    except Exception as e:
        print("Couldn't create CACHE folder due to ", e)


def main():
    direct_launch = sys.argv[1:][0]
    print("About to launch: ", direct_launch)

    if not os.path.isfile(direct_launch):
        print("Failed to launch XBE, it doesn't exist.", direct_launch)
        return

    if xbmc.getCondVisibility('Skin.HasSetting(reloademustation)'):
        write_igr_file()

    xbmc.executebuiltin('runxbe({})'.format(direct_launch))


if __name__ == '__main__':
    print("direct_launcher.py: Running")
