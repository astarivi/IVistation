import sys
import xbmc
import xbmcgui

from ivistation.verbose import VERBOSE_SYSTEMS


def main():
    system = xbmc.getInfoLabel('Container(9000).ListItem.Label2')

    print("y_home_interaction.py: Interaction started for " + system)

    if system in VERBOSE_SYSTEMS.values():
        print("Core config menu for system {} has been requested".format(system))

        # Add scripts root dir to path, and import from it
        sys.path.append(
            xbmc.translatePath("Special://root/ivistation/scripts/")
        )

        # noinspection PyUnresolvedReferences
        from emu_config_gui import EmuConfigMenu

        EmuConfigMenu(system).main_menu()

    # TODO: Check for other conditions


if __name__ == '__main__':

    try:
        main()
    finally:
        xbmcgui.unlock()
