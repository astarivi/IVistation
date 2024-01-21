import os
import xbmc
import xbmcgui

from config.content_config import *


class EmulatorSelector:
    def __init__(self, rom_identifier, system):
        self.system = system
        self.rom_identifier = rom_identifier
        self.dialog = xbmcgui.Dialog()

    def get_rom_config(self):
        """
        User declared configuration for one specific ROM
        """
        rom_config_manager = RomConfigManager(self.rom_identifier, self.system)
        current_configuration = rom_config_manager.get_config()
        is_override = rom_config_manager.is_override()

        if current_configuration is None:
            return None

        selected_core = current_configuration["core"]
        core_exists = verify_emulator_existence(self.system, selected_core)

        # If this is an override, but the core doesn't exist.
        if is_override:
            # This override is ignored, don't go any further.
            if "ignored" in current_configuration:
                return None

            # TODO: Implement this
            if not core_exists:
                selection = self.dialog.yesno(
                    "OPTIMAL CONFIGURATION FOUND",
                    "",
                    "An optimal configuration was found for this rom."
                    "Nonetheless, the target core is not installed."
                    "Would you like to download it?"
                )
                return None

            if "asked" not in current_configuration:
                xbmc.executebuiltin('Dialog.Close(1101,true)')
                use_optimal = self.dialog.yesno(
                    "OPTIMAL CONFIGURATION FOUND",
                    "",
                    "An optimal configuration was found for this rom."
                    "Would you like to use it?"
                )
                xbmc.executebuiltin('ActivateWindow(1101)')

                if use_optimal:
                    current_configuration["asked"] = True
                    rom_config_manager.save_config(current_configuration, override=True)
                    return selected_core
                # User doesn't want the optimal configuration
                else:
                    current_configuration["asked"] = True
                    current_configuration["ignored"] = True
                    rom_config_manager.save_config(current_configuration, override=True)
                    return None

            return selected_core

        # This isn't an override, so the user asked for this.
        if core_exists:
            return selected_core

        # User created this configuration, but the core doesn't exist, so we delete everything related to the core
        # (in content_config.verify_emulator_existence()) call.

        # Nonetheless, we keep the configuration.
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

        if core_exists:
            return selected_core

        return None

    def get_system_default(self):
        system_config_manager = get_system_defaults()
        try:
            return system_config_manager[self.system]
        except KeyError:
            return None

    def _get_full_path_to_core(self, core):
        return os.path.join(EMULATORS_DIR, self.system, core, "default.xbe")

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
