"""
Launches emulators directly, through their default.xbe file.

In comparison with emulator_launcher.py, the latter contains
logic to select cores and user configurations.
"""

import os
import xbmc


# TODO: Support cores here. Though, this may never be used nor needed
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
    emulator = xbmc.getInfoLabel('Container(9000).ListItem.Label2')

    emulator_path = xbmc.translatePath("Special://root/ivistation/emulators/{}/default.xbe".format(emulator))

    print("About to direct launch: ", emulator_path)

    if not os.path.isfile(emulator_path):
        print("Failed to direct launch emulator XBE, it doesn't exist.", emulator_path)
        return

    if xbmc.getCondVisibility('Skin.HasSetting(reloademustation)'):
        write_igr_file()

    xbmc.executebuiltin('runxbe({})'.format(emulator_path))


if __name__ == '__main__':
    print("direct_emulator_launcher.py: Running")
