import os
import sys

import xbmc
import xbmcgui
import time

from parse_manual import parse_roms, SYSTEMS
from parse_auto import parse_auto


# TODO: Test how to remove an item from the carousel if it's empty
def main():
    xbmc.executebuiltin("Skin.Reset(SelectPreviewMode)")
    scan_type = sys.argv[1:][0]

    print("Systems parse {} mode selected".format(scan_type))

    xbmc.executebuiltin('Dialog.Close(1101,true)')

    dialog = xbmcgui.Dialog()
    progress_dialog = xbmcgui.DialogProgress()

    if scan_type == "manual":
        emulated_systems = sorted(SYSTEMS.keys())

        selected_system = dialog.select("SELECT A SYSTEM", emulated_systems)

        if selected_system == -1:
            return

        progress_dialog.create("MANUAL SCAN MODE", "Initializing")

        result = parse_roms(emulated_systems[selected_system], progress_dialog)

        progress_dialog.close()

        if result != 0:
            dialog.ok(
                "SCAN RESULTS",
                "[B]{}[/B] [B]{}[/B] games have been imported successfully.".format(
                    result,
                    emulated_systems[selected_system].upper()
                )
            )
        else:
            dialog.ok(
                "SCAN RESULTS",
                "No valid [B]{}[/B] games have been found.".format(
                    emulated_systems[selected_system].upper()
                )
            )
    else:
        if not dialog.yesno(
            "AUTO SCAN MODE",
            "Would you like to scan all systems?",
            "Depending on the game count, this could",
            "take a long time."
        ):
            return

        progress_dialog.create("AUTO SCAN MODE", "Initializing")

        result = parse_auto(progress_dialog)

        progress_dialog.close()

        if result != 0:
            dialog.ok(
                "SCAN RESULTS",
                "[B]{}[/B] games have been imported successfully.".format(
                    result
                )
            )
        else:
            dialog.ok(
                "SCAN RESULTS",
                "No valid games have been found."
            )

    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("MyScript.ExternalRunning", "True")

    xbmc.executebuiltin(
        'RunScript({})'.format(
            os.path.join(
                xbmc.translatePath("Special://root/"),
                "ivistation\\scripts\\menu\\refresh_carousel.py"
            )
        )
    )

    # Primitive Mutex
    while xbmcgui.Window(xbmcgui.getCurrentWindowId()).getProperty("MyScript.ExternalRunning") == "True":
        time.sleep(0.2)


if __name__ == '__main__':
    print("Initializing a systems parse...")
    main()
