import os
import xbmc
import time
import struct

SYSTEM_BACKUP_DIR = xbmc.translatePath("Special://root/system/SystemInfo")


class EEPROMReader(object):
    """
    Reads the console EEPROM with a little bit of magic, and XBMC built ins
    """
    def __init__(self):
        self.eeprom_file_path = os.path.join(SYSTEM_BACKUP_DIR, "EEPROMBackup.bin")
        self.eeprom = None

    # FIXME: Perhaps reading this at launch would be enough?
    def read_eeprom(self, timeout=5):
        # If the EEPROM backup exists, remove it
        if os.path.isfile(self.eeprom_file_path):
            try:
                os.remove(self.eeprom_file_path)
            except Exception as e:
                print("Failed to remove existing EEPROM backup file at ", self.eeprom_file_path, e)
                return False

        # Request a new backup
        xbmc.executebuiltin("XBMC.BackupSystemInfo")

        # Wait for timeout for the console to create the backup
        start_time = time.time()
        while True:
            if os.path.isfile(self.eeprom_file_path):
                # Exit as soon as found
                break

            elapsed_time = time.time() - start_time

            # Check if the timeout duration has been exceeded
            if elapsed_time >= timeout:
                print("Timeout for reading EEPROM reached. Exiting...")
                return False

        try:
            with open(self.eeprom_file_path, "rb") as eeprom_data:
                self.eeprom = eeprom_data.read()
                return True
        except Exception as e:
            print("Failed to open EEPROM backup due to ", e)

        return False

    def get_user_video_flags(self):
        # Get the address
        if len(self.eeprom) < 0x94 + 4:
            raise ValueError("Insufficient bytes in the EEPROM")

        bytes_to_convert = self.eeprom[0x94:0x94 + 4]

        value = struct.unpack('<I', bytes_to_convert)[0]

        flags = {
            '480i': 0x00000000,
            '480p': 0x00080000,
            '720p': 0x00020000,
            '1080i': 0x00040000,
            'Widescreen': 0x00010000,
            'Letterbox': 0x00100000,
            '60hz': 0x00400000,
            '50hz': 0x00800000
        }

        decoded_flags = {}

        for flag_name, flag_value in flags.items():
            if value & flag_value:
                decoded_flags[flag_name] = True
            else:
                decoded_flags[flag_name] = False

        return decoded_flags
