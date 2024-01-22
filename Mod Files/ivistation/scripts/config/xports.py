import os
import xbmcgui

from backports import configparser
from content_config import get_core_path
from collections import OrderedDict
from utils.eeprom import EEPROMReader


SETTINGS = OrderedDict([
    ("Video Mode", "video_mode"),
    ("Software Filter", "software_filter"),
    ("Hardware Filter", "hardware_filter"),
    ("FPS Overlay", "showfps"),
    ("Load Savestate on Launch", "auto_load_save_state")
])

SETTINGS_VALUES = {
    "video_mode": [
        "Standard 480i",
        "480p",
        "720p",
        "1080i"
    ],
    "software_filter": [
        "None",
        "2xSai",
        "Super 2xSai",
        "HQ2X",
        "Eagle2x",
        "Super Eagle 2x",
        "Super Scale 2x",
        "AdvanceMame 2x",
        "Simple 2x",
        "2xSai Scanline",
        "Eagle2x Scanline",
        "Super Eagle2x Scanline",
        "SuperScale 2x Scanline"
    ],
    "hardware_filter": [
        "Point Filtering",
        "Bilinear Filtering",
        "Trilinear Filtering",
        "Anisotropic Filtering"
    ],
    "showfps": [
        "Disabled",
        "Enabled"
    ],
    "auto_load_save_state": [
        "Disabled",
        "Enabled"
    ]
}


class XportsSettings(object):
    def __init__(self, emu_system, core, core_info):
        self.system = emu_system
        self.core = core
        self.core_info = core_info
        self.full_core_path = get_core_path(emu_system, core)
        self.should_save = False
        self.settings_path = os.path.join(self.full_core_path, self.core_info["config_file"])

        # Read the config file
        self.xports_config = configparser.ConfigParser()
        self.xports_config.read(self.settings_path)

    def _set_aspect_ratio(self, keep_ratio, res, flags):
        resolution = None
        if "480" in res:
            resolution = (640, 480)
        elif "720" in res:
            resolution = (1280, 720)
        elif "1080" in res:
            resolution = (1920, 1080)

        # Not supported
        if resolution is None:
            print("Failed to set aspect ratio for resolution: ", res, " flags: ", flags)

        # Handle widescreen 16:9 resolutions
        if resolution[0] in (1280, 1920):
            if keep_ratio:
                screen_size_x = int(4.0/3.0 * resolution[1])

                self.xports_config["GENERAL"]["screenmaxx"] = str(screen_size_x)
                self.xports_config["GENERAL"]["screenmaxy"] = str(resolution[1])
                # Center the screen-x axis
                self.xports_config["GENERAL"]["screenx"] = str(int((resolution[0] - screen_size_x) / 2.0))
                self.xports_config["GENERAL"]["screeny"] = "0"
                return

            # Stretched
            self.xports_config["GENERAL"]["screenmaxx"] = str(resolution[0])
            self.xports_config["GENERAL"]["screenmaxy"] = str(resolution[1])
            self.xports_config["GENERAL"]["screenx"] = "0"
            self.xports_config["GENERAL"]["screeny"] = "0"
            return

        # 480p
        if keep_ratio:
            screen_size_x = int(0.89/1.0 * resolution[1])
            self.xports_config["GENERAL"]["screenmaxx"] = str(screen_size_x)
            self.xports_config["GENERAL"]["screenmaxy"] = str(resolution[1])
            self.xports_config["GENERAL"]["screenx"] = str(int((resolution[0] - screen_size_x) / 2.0))
            self.xports_config["GENERAL"]["screeny"] = "0"
            return

        self.xports_config["GENERAL"]["screenmaxx"] = str(resolution[0])
        self.xports_config["GENERAL"]["screenmaxy"] = str(resolution[1])
        self.xports_config["GENERAL"]["screenx"] = "0"
        self.xports_config["GENERAL"]["screeny"] = "0"

    def _handle_video_mode(self, dialog):
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create("OBTAINING CAPABILITIES", "Initializing, please wait")
        eeprom_reader = EEPROMReader()
        progress_dialog.update(0, "Reading console capabilities")

        if not eeprom_reader.read_eeprom():
            progress_dialog.close()
            dialog.ok("ERROR", "Couldn't read EEPROM for video modes.")
            return

        progress_dialog.update(100, "All done. Preparing modes...")

        video_flags = eeprom_reader.get_user_video_flags()

        available_video_modes = []
        possible_video_modes = SETTINGS_VALUES["video_mode"]

        # Iterate the heck out of it
        for video_flag, value in video_flags.items():
            for video_mode in possible_video_modes:
                if video_flag in video_mode and value:
                    available_video_modes.append(video_mode)

        # Display default if none are available
        if len(available_video_modes) == 0:
            available_video_modes.append(possible_video_modes[0])

        progress_dialog.close()

        selection = dialog.select(
            "VIDEO MODE",
            available_video_modes
        )

        # No changes done
        if selection == -1:
            return

        choice = available_video_modes[selection]
        choice_index = possible_video_modes.index(
            choice
        )

        self.xports_config["GENERAL"]["video_mode"] = str(choice_index)
        self.xports_config["GENERAL"]["init_video"] = "1"

        # If the user has widescreen, let them choose
        if video_flags["Widescreen"]:
            is_keep_aspect_ratio = dialog.yesno(
                "CHOOSE ASPECT RATIO",
                "Please choose a display aspect",
                "ratio mode for this resolution.",
                "",
                "STRETCHED",
                "KEEP ASPECT RATIO"
            )
        # Else, just stretch the hell out
        else:
            is_keep_aspect_ratio = False
            dialog.ok(
                "LIMITED ASPECT RATIO",
                "Widescreen is currently disabled in your console, change",
                "your Microsoft dashboard settings if your TV is widescreen.",
                "For now, 4:3 display mode will be used, as 16:9 is unavailable."
            )

        # Set the display mode
        self._set_aspect_ratio(is_keep_aspect_ratio, choice, video_flags)
        self.should_save = True

    def _show_submenu(self, title, option, dialog):
        options = list(SETTINGS_VALUES[option])
        # Add * to the start of the selected value
        current_index = int(self.xports_config["GENERAL"][option])
        current_value = options[current_index]
        options[current_index] = "* " + current_value

        selection = dialog.select(
            title,
            options
        )

        if selection == -1:
            return

        if "* " in options[selection]:
            return

        user_choice = options[selection]
        self.xports_config["GENERAL"][option] = options.index(user_choice)
        self.should_save = True

    def show_menu(self, dialog):

        while True:
            options = SETTINGS.keys()

            selection = dialog.select(
                "{} SETTINGS".format(self.core_info["title"]),
                options
            )

            if selection == -1:
                return

            user_choice = SETTINGS[options[selection]]

            if user_choice == "video_mode":
                self._handle_video_mode(dialog)
            else:
                self._show_submenu(options[selection], user_choice, dialog)
