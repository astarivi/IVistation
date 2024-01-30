import os
import xbmc
import glob
import itertools

from utils.xbe import XBE
from utils.xiso import process_iso_name, process_iso
from parse_system import ParseSystem

# These aren't used, but are here just for readability purposes
ALLOWED_EXTENSIONS = (
    "xbe",
    "iso"
)


class ParseXbox(ParseSystem):
    entries = []

    def __init__(self):
        super(ParseXbox, self).__init__()
        print("Initializing XBOX parser...")

        # TODO: Make this configurable
        self.paths = [
            os.path.join(
                xbmc.translatePath("Special://root/"),
                "ivistation\\roms\\xbox"
            ),
            "E:\\Games",
            "F:\\Games",
            "G:\\Games",
            "R:\\Games",
            "S:\\Games",
            "V:\\Games",
            "W:\\Games",
            "A:\\Games",
            "B:\\Games",
            "P:\\Games"
        ]

        print("XBOX search paths: ", self.paths)

    @staticmethod
    def get_progress_title():
        return "Processing [B]Xbox[/B] games"

    def _get_path(self):
        return self.paths

    def _get_allowed_extensions(self):
        return ALLOWED_EXTENSIONS

    def _use_crc32(self):
        return False

    def finalize(self):
        # No cleanup needed
        pass

    def prepare_entries(self):
        potential_files = []

        for path in self.paths:
            if not os.path.isdir(path):
                continue

            for possible_game in [os.path.join(path, file_name) for file_name in os.listdir(path)]:
                if not os.path.isdir(possible_game):
                    continue

                xbe_path = os.path.join(possible_game, "default.xbe")

                if not os.path.isfile(xbe_path):
                    # Check if we have any iso files here
                    folder = possible_game + "\\" if not possible_game.endswith("\\") else possible_game
                    if len(list(glob.iglob(folder + "*.iso"))) != 0:
                        potential_files.append(possible_game)
                    continue

                potential_files.append(xbe_path)

        if len(potential_files) == 0:
            yield -1, "Nothing found"

        # Start the fun
        count = 0

        for potential_file in potential_files:
            count += 1
            # XISO
            if not potential_file.endswith(".xbe"):
                result = self._xiso_parse(potential_file)

                if result is None:
                    yield int((count / float(len(potential_files))) * 100), "Invalid XISO, skipping..."
                    continue

                potential_file = result

            try:
                parsed_xbe = XBE(potential_file)
                title_name = parsed_xbe.cert.cleanTitleName
                title_id = parsed_xbe.cert.dwTitleId
            except Exception as e:
                print("XBOX file ", potential_file, " failed to parse due to ", e)
                yield int((count / float(len(potential_files))) * 100), "Invalid file, skipping..."
                continue

            # Check for title name duplicates
            if any(entry and entry[0] == title_name for entry in self.entries):
                title_name = title_name + " 2"

            self.entries.append(
                (title_name, title_id, potential_file)
            )

            yield int((count / float(len(potential_files))) * 100), title_name
        yield 100, "All done"

    @staticmethod
    def _xiso_parse(xiso_folder):
        folder = xiso_folder + "\\" if not xiso_folder.endswith("\\") else xiso_folder

        xiso_files_search = itertools.groupby(
            sorted(glob.iglob(folder + "*.iso")),
            lambda file_name: os.path.basename(process_iso_name(file_name))
        )

        xiso_files = [list(group) for key, group in xiso_files_search]

        # This is not supported. A single folder should contain a single set of xiso files.
        if len(xiso_files) > 1 or len(xiso_files) == 0:
            return None

        iso_files = xiso_files[0]

        print(str.format("Processing {}", iso_files))

        try:
            return process_iso(iso_files, xiso_folder)
        except Exception as e:
            print("Failed to import XBOX XISO(s) ", iso_files, " due to: ", e)
            import traceback
            traceback.print_exc()

    def count_entries(self):
        return len(self.entries)

    def get_entries(self):
        return sorted(self.entries, key=lambda x: x[0])
