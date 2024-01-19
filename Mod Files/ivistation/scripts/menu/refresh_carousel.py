import os
import sys
import xbmc
import shutil
import xbmcgui

EMULATORS = ["3do", "amiga", "amstradcpc", "apple2", "atari2600", "atari5200", "atari7800", "atari800", "atarijaguar",
             "atarilynx", "atarist", "atarixe", "atarixl", "c64", "c64pet", "chip8x", "coco", "colecovision", "cv20",
             "daphne", "dreamcastvmu", "famicom", "fba", "fbaxxx", "fbl", "fblc", "gamegear", "gb", "gba", "gbc",
             "genesis", "intellivision", "mame", "mastersystem", "megadrive", "mess", "msx", "n64", "nds", "neogeo",
             "neogeocd", "nes", "ngp", "ngpc", "odyssey2", "pc-98", "pce-cd", "pcengine", "pokemonmini", "psx",
             "samcoupe", "saturn", "sc-3000", "scummvm", "sega32x", "segacd", "sf-7000", "sg-1000", "sgb", "snes",
             "tg-cd", "tg16", "ti99", "virtualboy", "waterasupervision", "wonderswan", "x68000",
             "zxspectrum"]  ## used to create folders of the supported emulators.


def main():
    system = sys.argv[1:][0]

    # Create some folders first

    roms_path = "Q:\\ivistation\\roms\\"
    emulators_path = "Q:\\ivistation\\emulators\\"

    for emulator in EMULATORS:
        try:
            os.makedirs(os.path.join(roms_path, emulator))
        except Exception:
            pass

        try:
            os.makedirs(os.path.join(emulators_path, emulator))
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

    xbmc.executebuiltin("Notification(Complete,Carousel Information Updated)")
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("MyScript.ExternalRunning", "False")


if __name__ == '__main__':
    print("Refreshing carousel.")
    main()
