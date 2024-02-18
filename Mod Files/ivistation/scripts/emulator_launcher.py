import os
import sys
import time
import xbmc
import xbmcgui

from contextlib import closing
from config.content_config import *
from config.utils.user_database import UserDatabaseHelper


ROOT_DIR = xbmc.translatePath("Special://root/")
CONFIGS_PATH = xbmc.translatePath("Special://root/ivistation/configs/")


class EmulatorSelector:
    def __init__(self, rom_identifier, system):
        self.system = system
        self.rom_identifier = rom_identifier
        self.dialog = xbmcgui.Dialog()

    def get_rom_config(self):
        """
        User declared configuration for one specific ROM
        """
        # DatabaseEntry object
        with closing(UserDatabaseHelper(self.system)) as rom_config_manager:
            current_configuration = rom_config_manager.fetch(self.rom_identifier)

            # We can't use anything from here
            if not current_configuration.exists():
                return None

            if "core" not in current_configuration.json_data:
                if not current_configuration.is_override:
                    current_configuration.delete()
                return None

            selected_core = current_configuration.json_data["core"]
            core_exists = verify_emulator_existence(self.system, selected_core)

            # If this is an override.
            if current_configuration.is_override:
                # This override is ignored, don't go any further.
                if current_configuration.override_settings.ignored:
                    return None

                if not core_exists:
                    xbmc.executebuiltin('Dialog.Close(1101,true)')
                    selection = self.dialog.yesno(
                        "OPTIMAL CONFIGURATION FOUND",
                        "An optimal configuration was found for this rom.",
                        "Nonetheless, the required core is not installed.",
                        "Would you like to download it?"
                    )

                    # If user doesn't want to download the core
                    if not selection:
                        current_configuration.override_settings.ignored = True
                        current_configuration.override_settings.save()
                        return None

                    xbmc.executebuiltin('ActivateWindow(1101)')
                    from download.download_loader import retrieve_from_library
                    from download.download import run_downloader

                    try:
                        run_downloader(
                            *retrieve_from_library("cores", selected_core)
                        )
                        raise KeyboardInterrupt("Redirecting to downloader")
                    except KeyboardInterrupt as e:
                        raise e
                    except Exception as e:
                        print("Error while running downloader with intent", e)

                    return None

                if not current_configuration.override_settings.asked:
                    xbmc.executebuiltin('Dialog.Close(1101,true)')
                    use_optimal = self.dialog.yesno(
                        "OPTIMAL CONFIGURATION FOUND",
                        "An optimal configuration was found for this rom.",
                        "We will only ask this once per game."
                        "Would you like to use it?"
                    )

                    xbmc.executebuiltin('ActivateWindow(1101)')

                    if use_optimal:
                        current_configuration.override_settings.asked = True
                        current_configuration.override_settings.save()
                        return selected_core
                    # User doesn't want the optimal configuration
                    else:
                        current_configuration.override_settings.asked = True
                        current_configuration.override_settings.ignored = True
                        current_configuration.override_settings.save()
                        return None

                return selected_core

            # This isn't an override, so the user asked for this.
            if core_exists:
                return selected_core

            # Core doesn't exist, delete this config and return nothing.
            current_configuration.delete()
            return None

    def get_emulator_config(self):
        """
        User declared configuration, emulator wide
        """
        emulator_config_manager = CoreConfigManager(self.system)
        emulator_configuration = emulator_config_manager.get_config()

        if emulator_configuration is None:
            return None

        selected_core = emulator_configuration["core"]
        core_exists = verify_emulator_existence(self.system, selected_core)

        if not core_exists:
            emulator_config_manager.delete_config()
        else:
            return selected_core

        return None

    def get_system_default(self):
        system_config_manager = get_system_defaults()
        try:
            return system_config_manager[self.system]
        except KeyError:
            return None

    def _get_full_path_to_core(self, core):
        return os.path.join(get_core_path(self.system, core), "default.xbe")

    def get_emulator_xbe(self):
        """
        Returns the full path to the emulator .xbe, or None if nothing was found.
        """

        # Try to fetch the ROM specific configuration first
        core = self.get_rom_config()

        if core is not None:
            return self._get_full_path_to_core(core)

        core = self.get_emulator_config()

        if core is not None:
            return self._get_full_path_to_core(core)

        core = self.get_system_default()

        if core is not None:
            return self._get_full_path_to_core(core)

        system_emulators = get_emulator_list_for_system(self.system)

        if len(system_emulators) == 0:
            xbmc.executebuiltin('Dialog.Close(1101,true)')
            self.dialog.ok(
                "NO CORE FOUND",
                "No cores found for this system. Try downloading some."
            )
            return None

        # Just use whatever lonely core we have
        if len(system_emulators) == 1:
            return self._get_full_path_to_core(system_emulators[0])

        xbmc.executebuiltin('Dialog.Close(1101,true)')
        selection = self.dialog.select(
            "SELECT A DEFAULT CORE",
            system_emulators
        )
        xbmc.executebuiltin('ActivateWindow(1101)')

        if selection == -1:
            return None

        selected_core = system_emulators[selection]
        emulator_config_manager = CoreConfigManager(self.system)

        emulator_config_manager.save_config({
            "core": selected_core
        })

        return self._get_full_path_to_core(selected_core)


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
    if rom_crc32 is None or rom_crc32.strip() == "" or rom_crc32 == 0 or rom_crc32 == "None":
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
