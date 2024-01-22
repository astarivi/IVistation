import sys
import xbmc
import xbmcgui
import simplejson as json

from config.content_config import *
from config.core_general import *


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
            self.main_menu()
            return

        selected_core = human_core_list[selection]

        # Same core
        if selected_core.startswith("* "):
            self.main_menu()
            return

        self.config["core"] = selected_core
        self.should_save = True
        self.core = selected_core
        self.core_info = None

        self.main_menu()

    def reset_core(self):
        choice = self.dialog.yesno(
            "ARE YOU SURE?",
            "{} WILL RESET TO DEFAULTS".format(self.core_info["title"])
        )

        if not choice:
            self.main_menu()
            return

        result = reset_core_to_defaults(self.system, self.core, self.core_info)

        self.dialog.ok(
            "CORE RESET RESULT",
            "CORE RESET WAS SUCCESSFUL" if result else "CORE RESET FAILED"
        )

        self.main_menu()

    def delete_core_data(self):
        choice = self.dialog.yesno(
            "ARE YOU SURE?",
            "ALL YOUR SAVED DATA FOR THIS CORE WILL BE LOST!".format(self.core_info["title"])
        )

        if not choice:
            self.main_menu()
            return

        choice = self.dialog.yesno(
            self.core_info["title"],
            "THIS INCLUDES YOUR SAVES IN THIS CORE. ARE YOU REALLY SURE?"
        )

        if not choice:
            self.main_menu()
            return

        result = delete_core_data(self.system, self.core, self.core_info)

        self.dialog.ok(
            "CORE WIPE RESULT",
            "CORE DATA REMOVED" if result else "CORE DATA FAILED TO BE REMOVED"
        )

        self.main_menu()

    # FIXME: Make this a loop
    def main_menu(self):
        """
        Shows the UI
        """

        if self.core is None:
            self.handle_no_core()

        # If the user didn't decide on any core
        if self.core is None:
            return

        # We have a core
        title = "CORE SETTINGS"
        menu = self.get_menu()
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
            # TODO: Core settings
            pass

    # Save when this stuff gets recycled, which would be pronto
    def __del__(self):
        if self.should_save:
            self.config_manager.save_config(self.config)


if __name__ == '__main__':
    print("Initializing a systems parse...")
    system = sys.argv[1:][0]
    rom_identifier = sys.argv[1:][1]

