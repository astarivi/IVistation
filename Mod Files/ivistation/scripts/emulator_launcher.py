import os
import sys
import xbmc
import time

from emulator_selector import EmulatorSelector

ROOT_DIR = xbmc.translatePath("Special://root/")
CONFIGS_PATH = xbmc.translatePath("Special://root/ivistation/configs/")


# Launches game emulators with the provided rom
def main():
    args = sys.argv[1:]
    target_system = args[0]
    rom_crc32 = args[1]
    rom_path = args[2]

    # Just in case
    if rom_path.startswith("Q:\\"):
        rom_path = rom_path.replace("Q:\\", ROOT_DIR)

    # Use CRC32 if available, else, use rom filename
    if rom_crc32 is None or rom_crc32 == "" or rom_crc32 == " " or rom_crc32 == 0 or rom_crc32 == "None":
        rom_identifier = os.path.splitext(os.path.basename(rom_path))[0]
    else:
        rom_identifier = rom_crc32

    emu_selector = EmulatorSelector(rom_identifier, target_system)
    emulator = emu_selector.get_emulator_xbe()

    if emulator is None:
        xbmc.executebuiltin('Dialog.Close(1101,true)')
        print("emulator_launcher.py: No emulator found to launch", args)
        return

    with open('z:\\tmp.cut', 'w') as cut:
        cut.write('<shortcut><path>{}</path><custom><game>{}</game></custom></shortcut>'.format(
            emulator,
            rom_path
        ))

    time.sleep(1)
    xbmc.executebuiltin('Dialog.Close(134,false)')
    xbmc.executebuiltin('runxbe(z:\\tmp.cut)')


if __name__ == '__main__':
    print("Launching game.")
    main()
