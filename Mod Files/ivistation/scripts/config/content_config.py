import os
import re
import xbmc
import shutil
import simplejson as json


ROOT_DIR = xbmc.translatePath("Special://root/")
EMULATORS_DIR = xbmc.translatePath("Special://root/ivistation/emulators/")
CONFIGS_PATH = xbmc.translatePath("Special://root/ivistation/configs/")


class CoreConfigManager(object):
    """
    Loads a user declared configuration file, which affects all the roms for an emulator.
    Note that this could be overriden by individual ROM configuration files that were declared by using
    RomConfigManager, or that came with IVistation as ROM overrides.

    Although, overrides can be ignored.

    In practice, this class tells IVistation what core to load for a system, and nothing more, as the
    actual core configurations are handled by the core setting files.

    Uses simple JSON structures.
    """

    def __init__(self, system):
        super(CoreConfigManager, self).__init__()
        self.system = system

        self.path = os.path.join(
            CONFIGS_PATH,
            system,
            "core.json"
        )

    def get_config(self):
        if not os.path.isfile(self.path):
            return None

        with open(self.path, "r") as current_config:
            return json.load(current_config)

    def save_config(self, new_configuration):
        path = self.path

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
        if os.path.isfile(self.path):
            os.remove(self.path)


def get_core_path(emu_system, core):
    """
    Returns the full path to a core, for a given system.
    """

    possible_paths = (
        os.path.join(EMULATORS_DIR, emu_system, core),
        os.path.join(EMULATORS_DIR, "multi", core)
    )

    for path in possible_paths:
        if os.path.isdir(path):
            return path

    raise KeyError("Core path not found, searched in: ", possible_paths, emu_system, core)


def check_multicore_compatibility(emu_system, core_path):
    """
    Given the path to a core, (or the path to its executable),
    checks if it's a multi-system core, and then checks if
    the given system is supported.

    If a regular core path is passed, and not a multi-system
    core, False is returned.

    If the info.json file is invalid, the whole core will
    be deleted.

    Args:
        emu_system: The system to check compat for
        core_path: The core path to check compat with
    Returns:
        boolean for validity
    """

    if core_path.endswith("default.xbe"):
        core_path = os.path.dirname(core_path)

    with open(os.path.join(core_path, "info.json"), "r") as ci:
        core_info = json.load(ci)

    # This is not a multi-system core, return false.
    if "multi" not in core_info:
        return False

    if "systems" not in core_info["multi"]:
        try:
            shutil.rmtree(
                os.path.dirname(core_path)
            )
        except Exception as e:
            print("content_config.py: Couldn't delete ", core_path, emu_system, e)
        return False

    if emu_system not in core_info["multi"]["systems"]:
        return False

    return True


def verify_emulator_existence(system, emulator):
    """
    Verifies if an emulator really exists. If the emulator isn't valid,
    it will be deleted.
    """

    if not isinstance(emulator, str) or emulator.strip() == "":
        return False

    try:
        emu_exe = os.path.join(get_core_path(system, emulator), "default.xbe")
    except KeyError:
        return False

    emu_exists = os.path.isfile(emu_exe)

    if not emu_exists:
        try:
            shutil.rmtree(
                os.path.dirname(emu_exe)
            )
        except Exception as e:
            print("content_config.py: Couldn't delete ", emu_exe, e)

    return emu_exists


def get_emulator_list_for_system(system):
    """
    Gets all the 'valid' emulators for a system, returns a list.

    If nothing was found, returns an empty list.

    Returns the names only, not the paths.
    """

    valid_systems = []

    emulators_path = (
        os.path.join(EMULATORS_DIR, system),
        os.path.join(EMULATORS_DIR, "multi")
    )

    for index in range(0, 2):
        for emulator in os.listdir(emulators_path[index]):
            full_path = os.path.join(emulators_path[index], emulator)

            # Multi-systems core
            if index == 1 and not check_multicore_compatibility(system, full_path):
                continue

            # Standalone systems core
            if os.path.isfile(os.path.join(full_path, "default.xbe")):
                valid_systems.append(emulator)
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
    Return the system bundled emulators, which cannot be removed by the user.
    Read only.
    """

    with open(os.path.join(ROOT_DIR, "ivistation\\data\\default_emus.json"), "r") as defaults:
        return json.load(defaults)


def get_core_info(emu_system, core_id):
    with open(os.path.join(get_core_path(emu_system, core_id), "info.json"), "r") as ci:
        return json.load(ci)


def _is_valid_ini_line(line):
    # Regular expression pattern for matching section (header)
    section_pattern = re.compile(r'^\s*\[([^]]+)]\s*$')

    # Regular expression pattern for matching key-value pair
    key_value_pattern = re.compile(r'^\s*([^=]+)\s*=\s*(.*)\s*$')

    # Check if the line matches the section pattern
    if section_pattern.match(line):
        return True
    # Check if the line matches the key-value pattern
    elif key_value_pattern.match(line):
        return True
    else:
        return False


def prepare_config_file(config_path):
    """
    Clean the config file from lines breaking the .ini convention, so it can be
    parsed by configparser later.
    """
    with open(config_path, "r+") as config_file:
        lines = config_file.readlines()
        config_file.seek(0)

        for line in lines:
            if _is_valid_ini_line(line):
                config_file.write(line)

        config_file.truncate()
