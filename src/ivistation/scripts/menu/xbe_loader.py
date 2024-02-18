import sys
import time
import xbmc

from utils.layout_helper import XBE_LAYOUT_XML, FOOTER_DATA_XBE, HEADER_DATA_XBE, MY_PROGRAMS_PATH


def main():
    try:
        target_type = sys.argv[1:][0]
    # Nothing found, get it from the UI
    # Perhaps it would be better to always use the arguments?
    except Exception:
        target_type = xbmc.getInfoLabel('Container(9000).ListItem.Label2')

    xbmc.executebuiltin('Skin.SetString(emuname,{})'.format(target_type))

    with open(XBE_LAYOUT_XML, "r") as layout_file, open(MY_PROGRAMS_PATH, "w") as output_file:
        output_file.write(HEADER_DATA_XBE.format(target_type))
        for line in layout_file:
            output_file.write(line)
        output_file.write(FOOTER_DATA_XBE)

    time.sleep(0.5)

    xbmc.executebuiltin('Dialog.Close(1111,true)')
    xbmc.executebuiltin('Dialog.Close(1101,true)')
    xbmc.executebuiltin('ActivateWindow(Programs,{},return)'.format(target_type))


if __name__ == '__main__':
    print("xbe_loader.py: Initializing")
    main()
