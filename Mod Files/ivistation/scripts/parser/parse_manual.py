import os
import xbmc

from emulators.parse_nes import ParseNES
from emulators.parse_snes import ParseSNES
from emulators.parse_xbox import ParseXbox
from menu.gamelist_helper import GameListCreator
from menu.boxart_downloader import DownloadResult, BoxArtDownloader


SYSTEMS = {
    "nes": ParseNES,
    "snes": ParseSNES,
    "xbox": ParseXbox
}


# Takes two parameters, the system, and a progress dialog to write progress to.
# Returns a number, which is the amount of processed entries.
def parse_roms(system, progress_dialog):
    parser = SYSTEMS[system]()

    # Prepare entries
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

    print("{} importer, {} valid entries found".format(system, entries))

    if entries == 0:
        xbmc.executebuiltin(
            "Skin.SetString({}_games,{})".format(
                system,
                entries
            )
        )
        return entries

    current_entry = 0

    # Create the gamelist
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

    # Boxart download
    boxart_downloader = BoxArtDownloader(system)

    if boxart_downloader.enabled:
        c_entry = 0

        for rom in parser.get_entries():
            c_entry += 1

            raw_rom_name = os.path.splitext(
                os.path.basename(
                    rom[2]
                )
            )[0]

            download_result = boxart_downloader.download_artwork(rom[0], raw_rom_name)

            # No internet connection?
            if download_result == DownloadResult.FAILED:
                break

            progress = (c_entry / float(entries)) * 100
            progress_dialog.update(
                int(progress),
                "Downloading [B]{}[/B] box art".format(system.upper()),
                rom[0].upper(),
                "This can take some time, please be patient."
            )

    xbmc.executebuiltin(
        "Skin.SetString({}_games,{})".format(
            system,
            entries
        )
    )

    return entries
