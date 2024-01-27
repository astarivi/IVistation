import os
import xbmc
import shutil
import simplejson as json

from abc import abstractmethod

ROOT_DIR = xbmc.translatePath("Special://root/")
EMULATORS_DIR = xbmc.translatePath("Special://root/ivistation/emulators/")
CONFIGS_PATH = xbmc.translatePath("Special://root/ivistation/configs/")


class BaseConfigManager(object):
    def __init__(self):
        pass

    @abstractmethod
    def _get_config_file_path(self):
        return ""

    def save_config(self, new_configuration, custom_path=None):
        path = self._get_config_file_path() if custom_path is None else custom_path

        if not new_configuration:
            return

        if os.path.isfile(path):
            try:
                os.remove(path)
            except Exception as e:
                print("BaseConfigManager: Couldn't remove: ", path, e)
                return

        with open(path, "w") as current_config:
            json.dump(new_configuration, current_config)

    def delete_config(self):
        if os.path.isfile(self._get_config_file_path()):
            os.remove(self._get_config_file_path())


class RomConfigManager(BaseConfigManager):
    """
    Loads a user declared configuration file, which affects only a given ROM from a given system.
    """

    def __init__(self, rom_identifier, system):
        super(RomConfigManager, self).__init__()
        self.game_identifier = rom_identifier
        self.system = system
        self.override = False

        current_configs_path = os.path.join(CONFIGS_PATH, system)

        self.paths = [
            os.path.join(
                current_configs_path,
                "{}.json".format(
                    rom_identifier
                )
            ),
            # Note how the override variant is later, is it's ignored if a user defined one exists
            os.path.join(
                current_configs_path,
                "d {}.json".format(
                    rom_identifier
                )
            )
        ]

    def _get_config_file_path(self):
        return self.paths[0]

    def is_override(self):
        return self.override

    def get_config(self):
        """
        Returns the dictionary representing the configuration file, or None if it doesn't exist.
        """

        configuration = None

        for config in self.paths:
            if not os.path.isfile(config):
                continue

            with open(config, "r") as current_config:
                configuration = json.load(current_config)

            if os.path.basename(config).startswith("d "):
                self.override = True

        return configuration

    def save_config(self, new_configuration, override=False):
        super(RomConfigManager, self).save_config(
            new_configuration,
            custom_path=self.paths[1] if override else self.paths[0]
        )


class CoreConfigManager(BaseConfigManager):
    """
    Loads a user declared configuration file, which affects all the roms for an emulator.
    Note that this could be overriden by individual ROM configuration files that were declared by using
    RomConfigManager, or that come bundled with a certain emulator.

    Although, emulator bundled configurations can be ignored.
    """

    def __init__(self, system):
        super(CoreConfigManager, self).__init__()
        self.system = system

        current_configs_path = os.path.join(CONFIGS_PATH, system)

        self.path = os.path.join(
            current_configs_path,
            "d  default.json"
        )

    def _get_config_file_path(self):
        return self.path

    def get_config(self):
        if not os.path.isfile(self.path):
            return None

        with open(self.path, "r") as current_config:
            return json.load(current_config)


def verify_emulator_existence(system, emulator):
    """
    Verifies if an emulator really exists. True if true. Ba dum tss
    """

    if emulator is None or emulator == "" or emulator == " ":
        return False

    ver_emulator_dir = os.path.join(EMULATORS_DIR, system, emulator, "default.xbe")

    emu_exists = os.path.isfile(ver_emulator_dir)

    if not emu_exists:
        try:
            shutil.rmtree(
                os.path.join(
                    EMULATORS_DIR,
                    system,
                    emulator
                )
            )
        except Exception as e:
            print("content_config.py: Couldn't delete ", ver_emulator_dir, e)

    return emu_exists


def get_emulator_list_for_system(system):
    """
    Gets all the 'valid' emulators for a system, returns a list.

    If nothing was found, returns an empty list.

    Returns the names only, not the paths.
    """

    valid_systems = []

    emulators_path = os.path.join(EMULATORS_DIR, system)

    for emulator in os.listdir(emulators_path):
        full_path = os.path.join(emulators_path, emulator)

        if os.path.isfile(os.path.join(full_path, "default.xbe")):
            valid_systems.append(full_path)
        else:
            try:
                shutil.rmtree(
                    full_path
                )
            except Exception as e:
                print("content_config.py: Couldn't delete ", full_path, e)

    return valid_systems


def get_system_defaults():
    """
    Return the system bundled emulators, which cannot be removed by the user, by default.
    Read only.
    """
    with open(os.path.join(ROOT_DIR, "ivistation\\data\\default_emus.json"), "r") as defaults:
        return json.load(defaults)


def get_core_path(emu_system, core):
    return os.path.join(EMULATORS_DIR, emu_system, core)
