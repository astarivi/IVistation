import os

from backports import configparser
from content_config import get_core_path


SETTINGS = {
    "video_mode": "Display Resolution",
    "custom_display_type": "Video Mode",
    "software_filter": "Software Filter",
    "hardware_filter": "Hardware Filter",
    "showfps": "FPS Overlay",
    "auto_load_save_state": "Load Savestate on Launch"
}

REVERSE_SETTINGS = dict((value, key) for key, value in SETTINGS.iteritems())

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


def show_menu(emu_system, core, core_info, dialog):
    full_core_path = get_core_path(emu_system, core)
    settings_path = os.path.join(full_core_path, core_info["config_file"])

    # Read the config file
    xports_config = configparser.ConfigParser()
    xports_config.read(settings_path)


