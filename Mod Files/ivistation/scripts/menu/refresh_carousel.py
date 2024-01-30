import os
import sys
import xbmc
import shutil
import xbmcgui

# used to create folders of the supported emulators.
EMULATORS = ["nes", "snes"]


def main():
    try:
        silent = True if sys.argv[1:][1] == "1" else False
    except Exception:
        silent = False

    # Create some folders first

    roms_path = "Q:\\ivistation\\roms\\"
    emulators_path = "Q:\\ivistation\\emulators\\"
    configs_path = "Q:\\ivistation\\configs\\"

    for emulator in EMULATORS:
        try:
            os.makedirs(os.path.join(roms_path, emulator))
        except Exception:
            pass

        try:
            os.makedirs(os.path.join(emulators_path, emulator))
        except Exception:
            pass

        try:
            os.makedirs(os.path.join(configs_path, emulator))
        except Exception:
            pass

        # Reset available systems
        xbmc.executebuiltin(
            "Skin.Reset({}_exists)".format(
                emulator
            )
        )

    gamelists_path = "Q:\\ivistation\\gamelists\\"

    for gamelist in os.listdir(gamelists_path):
        full_gamelist_path = os.path.join(gamelists_path, gamelist)

        # Check if the gamelist.xml exists
        if not os.path.isfile(
                os.path.join(
                    full_gamelist_path,
                    "gamelist.xml"
                )
        ):
            if os.path.isdir(full_gamelist_path):
                shutil.rmtree(full_gamelist_path)
            else:
                os.remove(full_gamelist_path)

            continue

        xbmc.executebuiltin(
            "Skin.SetBool({}_exists)".format(
                gamelist
            )
        )

    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("MyScript.ExternalRunning", "False")

    if not silent:
        xbmc.executebuiltin("Notification(Complete,Carousel Information Updated)")


if __name__ == '__main__':
    print("Refreshing carousel.")
    main()
