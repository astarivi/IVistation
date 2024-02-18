import os
import xbmc


# FIXME: Try this before committing an update
try:
    # noinspection PyUnresolvedReferences
    import updateexec

    print("updateexec.py found, executing...")

    should_erase = updateexec.run_update()

    if should_erase:
        os.remove(
            xbmc.translatePath("Special://root/system/scripts/updateexec.py")
        )
except ImportError:
    print("updateexec.py file not found, skipping...")


def main():
    # FIXME: This seems to cause black screens from time to time
    # Request an EEPROM backup for later use
    eeprom_file_path = os.path.join(xbmc.translatePath("Special://root/system/SystemInfo"), "EEPROMBackup.bin")

    if os.path.isfile(eeprom_file_path):
        try:
            os.remove(eeprom_file_path)
        except Exception as e:
            print("Failed to remove existing EEPROM backup file at ", eeprom_file_path, e)
            return False

    xbmc.executebuiltin("XBMC.BackupSystemInfo")


if __name__ == '__main__':
    print("Running autoexec.")
    main()
