import xbmc

from parse_roms import SYSTEMS
from menu.gamelist_helper import GameListCreator


def parse_auto(progress_dialog):
    """
    Iterates all the systems, and imports what it can find.
    """
    total = 0

    for system, sys_parser in SYSTEMS.items():
        if progress_dialog.iscanceled():
            return total

        parser = sys_parser()

        progress_title = parser.get_progress_title().format(system.upper())

        for progress, title in parser.prepare_entries():
            progress_dialog.update(
                progress,
                progress_title,
                title.upper(),
                "This can take some time, please be patient."
            )

            if progress == -1:
                break

        entries = parser.count_entries()

        print("{} auto-importer, {} valid entries found".format(system, entries))

        if entries == 0:
            xbmc.executebuiltin(
                "Skin.SetString({}_games,{})".format(
                    system,
                    entries
                )
            )
            continue

        current_entry = 0

        gamelist_creator = GameListCreator(system)

        for rom in parser.get_entries():
            gamelist_creator.add_entry(current_entry, rom)

            current_entry += 1
            progress = (current_entry / float(entries)) * 100
            progress_dialog.update(
                int(progress),
                "Building [B]{}[/B] game list".format(system.upper()),
                rom[0].upper(),
                "This can take some time, please be patient."
            )

        gamelist_creator.close()

        xbmc.executebuiltin(
            "Skin.SetString({}_games,{})".format(
                system,
                entries
            )
        )

        total += entries

    return total
