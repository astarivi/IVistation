import xbmc
import time

from layout_helper import DEFAULT_FAVS_LAYOUT, FOOTER_DATA_FAVS, HEADER_DATA_FAVS, FAVS_LAYOUT_XML


def load_favs_layout():
    print("Launching favs layout.")

    with open(DEFAULT_FAVS_LAYOUT, "r") as layout_file, open(FAVS_LAYOUT_XML, "w") as output_line:
        output_line.write(HEADER_DATA_FAVS)
        for line in layout_file:
            output_line.write(line)
        output_line.write(FOOTER_DATA_FAVS)

    xbmc.executebuiltin('Skin.SetBool(favsloading)')
    time.sleep(0.5)
    xbmc.executebuiltin('ReplaceWindow(134,return)')
