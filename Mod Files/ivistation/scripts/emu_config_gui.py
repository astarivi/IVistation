import xbmc
import xbmcgui

from config.content_config import *
from config.core_general import *
from config.xports import XportsSettings
from config.madmab import MadmabSettings

CORE_SETTINGS = {
    "xports": XportsSettings,
    "madmab": MadmabSettings
}


class EmuConfigMenu:
    def __init__(self, emu_system):
        xbmc.executebuiltin("Skin.Reset(SelectPreviewMode)")

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
            if not core_exists:
                self.config_manager.delete_config()
                self.config = None
            else:
                self.core = self.config["core"]
                return

        if self.config is None:
            self.config = {}

        # Let's check the system defaults
        sys_defaults = get_system_defaults()

        try:
            self.core = sys_defaults[self.system]
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

        verbose_available_cores = []
        core_relation = {}

        for core_id in available_cores:
            core_name = get_core_info(self.system, core_id)["title"]

            verbose_available_cores.append(core_name)
            core_relation[core_name] = core_id

        # More than one choice, let the user decide
        selection = self.dialog.select("SELECT A DEFAULT CORE", verbose_available_cores)

        # User didn't decide on anything
        if selection == -1:
            return

        self.core = core_relation[verbose_available_cores[selection]]
        self.config["core"] = self.core
        self.should_save = True

    def get_menu(self):
        # Load the info.json file from the emulator folder
        if self.core_info is None:
            self.core_info = get_core_info(self.system, self.core)

        options = [
            "CORE: {}".format(self.core_info["title"]),
            "RESET CORE TO DEFAULTS",
            "DELETE ALL CORE DATA"
        ]

        if self.core_info["config_type"] in CORE_SETTINGS.keys():
            options.insert(1, "CORE SETTINGS")

        return options

    def change_core(self):
        available_cores = get_emulator_list_for_system(self.system)

        core_relation = {}
        human_core_list = []

        for core_id in available_cores:
            core_name = get_core_info(self.system, core_id)["title"]
            # Selected core
            if self.core == core_id:
                core_name = "* " + core_name

            human_core_list.append(core_name)
            core_relation[core_name] = core_id

        selection = self.dialog.select("SELECT A CORE", human_core_list)

        # User canceled the operation
        if selection == -1:
            return

        selected_core = human_core_list[selection]

        # Same core
        if selected_core.startswith("* "):
            return

        self.core = core_relation[selected_core]
        self.config["core"] = self.core
        self.should_save = True
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
            title = self.system.upper() + " CORE SETTINGS"
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
                selected_core = CORE_SETTINGS[self.core_info["config_type"]]
                xports_config = selected_core(self.system, self.core, self.core_info)
                xports_config.show_menu(self.dialog)
                xports_config.save()

    # Save when this stuff gets recycled, which would be pronto
    def __del__(self):
        if self.should_save:
            self.config_manager.save_config(self.config)


def main():
    system = xbmc.getInfoLabel("Skin.String(emuname)")

    print("Core config menu for system {} has been requested".format(system))

    if system in ["xbox", "homebrew", "apps"]:
        return

    EmuConfigMenu(system).main_menu()


if __name__ == '__main__':
    xbmcgui.lock()
    print("Opening Core Config menu (emu_config_gui.py)")

    try:
        main()
    finally:
        xbmcgui.unlock()
