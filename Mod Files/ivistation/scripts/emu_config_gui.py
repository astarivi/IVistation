import xbmcgui
xbmcgui.lock()
import re
import simplejson as json

from config.content_config import *
from config.core_general import *
from config.xports import XportsSettings
from menu.utils.layout_helper import MY_PROGRAMS_PATH


class EmuConfigMenu:
    def __init__(self, emu_system):
        self.system = emu_system
        self.dialog = xbmcgui.Dialog()
        self.config_manager = CoreConfigManager(emu_system)
        self.config = self.config_manager.get_config()
        self.core = None
        self.core_info = None
        self.should_save = False

        # Let's check the emulator defaults
        if self.config is not None and "core" in self.config:
            core_exists = verify_emulator_existence(self.system, self.config["core"])
            if core_exists:
                self.core = self.config["core"]
                return

        # Let's check the system defaults
        sys_defaults = get_system_defaults()

        try:
            self.core = sys_defaults[self.system]
            return
        # Not in the system defaults
        except KeyError:
            pass

    def handle_no_core(self):
        available_cores = get_emulator_list_for_system(self.system)

        # No cores here, whoops
        # FIXME: Redirect to core downloads
        if len(available_cores) == 0:
            self.dialog.ok(
                "NO CORE FOUND",
                "No cores found for this system. Try downloading some."
            )
            return

        # Guess we will be using that lone core
        if len(available_cores) == 1:
            self.core = available_cores[0]
            self.should_save = True
            return

        # More than one choice, let the user decide
        selection = self.dialog.select("SELECT A DEFAULT CORE", available_cores)

        # User didn't decide on anything
        if selection == -1:
            return

        self.core = available_cores[selection]
        self.should_save = True

    def _get_core_info(self, core):
        core_path = get_core_path(self.system, core)

        with open(os.path.join(core_path, "info.json"), "r") as ci:
            return json.load(ci)

    def get_menu(self):

        # Load the info.json file from the emulator folder
        if self.core_info is None:
            self.core_info = self._get_core_info(self.core)

        options = [
            "CORE: {}".format(self.core_info["title"]),
            "RESET CORE TO DEFAULTS",
            "DELETE ALL CORE DATA"
        ]

        if self.core_info["config_type"] == "xports":
            options.insert(1, "CORE SETTINGS")

        return options

    # This little magic trick here will take us anywhere from 100 ms to 5 seconds
    def change_core(self):
        available_cores = get_emulator_list_for_system(self.system)

        human_core_list = []

        for core in available_cores:
            core_name = self._get_core_info(core)["title"]
            # Selected core
            if self.core == core_name:
                core_name = "* " + core_name

            human_core_list.append(core_name)

        selection = self.dialog.select("SELECT A CORE", human_core_list)

        # User canceled the operation
        if selection == -1:
            return

        selected_core = human_core_list[selection]

        # Same core
        if selected_core.startswith("* "):
            return

        self.config["core"] = selected_core
        self.should_save = True
        self.core = selected_core
        self.core_info = None

    def reset_core(self):
        choice = self.dialog.yesno(
            "ARE YOU SURE?",
            "{} will reset to defaults.".format(self.core_info["title"])
        )

        if not choice:
            return

        result = reset_core_to_defaults(self.system, self.core, self.core_info)

        self.dialog.ok(
            "CORE RESET RESULT",
            "Core reset was successful" if result else "Core reset failed",
        )

    def delete_core_data(self):
        choice = self.dialog.yesno(
            "ARE YOU SURE?",
            "ALL YOUR SAVED DATA FOR THIS CORE WILL BE LOST!",
            "THIS INCLUDES ALL YOUR SAVES IN THIS CORE"
        )

        if not choice:
            return

        result = delete_core_data(self.system, self.core, self.core_info)

        self.dialog.ok(
            "CORE WIPE RESULT",
            "CORE DATA REMOVED SUCCESSFULLY" if result else "CORE DATA FAILED TO BE REMOVED"
        )

    def main_menu(self):
        """
        Shows the UI
        """

        while True:
            if self.core is None:
                self.handle_no_core()

            # If the user didn't decide on any core
            if self.core is None:
                return

            # We have a core
            title = "CORE SETTINGS"
            menu = self.get_menu()
            xbmcgui.unlock()
            choice = self.dialog.select(title, menu)

            if choice == -1:
                return

            selected_option = menu[choice]

            if selected_option.startswith("CORE:"):
                self.change_core()
            elif selected_option == "RESET CORE TO DEFAULTS":
                self.reset_core()
            elif selected_option == "DELETE ALL CORE DATA":
                self.delete_core_data()
            else:
                xports_config = XportsSettings(self.system, self.core, self.core_info)
                xports_config.show_menu(self.dialog)
                xports_config.save()

    # Save when this stuff gets recycled, which would be pronto
    def __del__(self):
        if self.should_save:
            self.config_manager.save_config(self.config)


def main():
    # Only works in emulators. Maybe modify this if needed for Xbox or homebrew?
    pattern = r'emulator_launcher\.py,(.*?),'
    system = None

    with open(MY_PROGRAMS_PATH, "r") as current_system:
        for line_number, line in enumerate(current_system, 1):
            match = re.search(pattern, line)
            if match:
                system = match.group(1)

    if system is None:
        return

    EmuConfigMenu(system).main_menu()


if __name__ == '__main__':
    print("Opening Core Config menu (emu_config_gui.py)")

    try:
        main()
    finally:
        xbmcgui.unlock()
