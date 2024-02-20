import os
import xbmc
import shutil
from synopsis_helper import SynopsisHelper, DEFAULT_GAME_DETAILS

GAMELIST_ENTRY = '''\n
	<item id="{}">
		<name>{}</name>
		<details>{}</details>
		<synopsis>{}</synopsis>
		<thumbnail>{}</thumbnail>
		<mediapath>{}</mediapath>
		<onclick>Stop</onclick>
		<onclick>{}</onclick>
		<onclick>{}</onclick>
	</item>'''

FAVORITES_ENTRY = '<favourites>{}|{}|{}</favourites>\n'

JUMPLIST_ENTRY = '''<control type="button" id="{}">
	<label>[UPPERCASE]$LOCALIZE[31405][/UPPERCASE]</label>
	<label2>&lt; [UPPERCASE]{}[/UPPERCASE] &gt;</label2>
	<include>MenuButtonCommonValues</include>
	<onclick>Dialog.Close(1120)</onclick>
	<onclick>{}</onclick>
</control>
'''


class GameListCreator:
    def __init__(self, system):
        root_path = xbmc.translatePath("Special://root/")

        self.system = system
        path = os.path.join(
            root_path,
            "ivistation\\gamelists\\{}\\".format(self.system)
        )

        # Remove the old stuff
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
        except Exception:
            print("Failed to erase gamelist folder at ", path)

        os.makedirs(path)

        self.gamelist_file = open(
            os.path.join(
                path,
                "gamelist.xml"
            ),
            "a"
        )
        self.gamelist_file.write("<content>\n")

        self.favorites_file = open(
            os.path.join(
                path,
                "favslist.xml"
            ),
            "a"
        )

        self.jumplist_file = open(
            os.path.join(
                path,
                "jumplist.xml"
            ),
            "a"
        )

        self.last_letter = None
        self.jump_count = 8000
        self.synopsis_helper = SynopsisHelper(self.system)

    @staticmethod
    def _cut_filename(filename):
        """
        If the sole filename is too long to fit the extension, cut it down.
        """
        return filename[:38] if len(filename) > 38 else filename

    def add_entry(self, count, rom):
        if self.system == "xbox":
            launcher = "RunScript(special://root/ivistation/scripts/xbox_launcher.py,{1},{2})"
            raw_rom_name = self._cut_filename(os.path.basename(os.path.dirname(rom[2])))
        else:
            launcher = "RunScript(special://root/ivistation/scripts/emulator_launcher.py,{},{},{})"
            raw_rom_name = self._cut_filename(
                os.path.splitext(
                    os.path.basename(
                        rom[2]
                    )
                )[0]
            )

        try:
            if not self.synopsis_helper.enabled:
                raise ValueError

            game_details, game_synopsis = self.synopsis_helper.get_synopsis(
                rom[0],
                crc32=rom[1]
            )
        except ValueError:
            game_details = DEFAULT_GAME_DETAILS.format(
                rom[0],
                self.system,
                rom[1]
            )

            game_synopsis = ""

        self.gamelist_file.write(
            GAMELIST_ENTRY.format(
                count,
                rom[0],
                game_details,
                game_synopsis,
                "{}.jpg".format(
                    raw_rom_name
                ),
                "[ArtworkFolder]",
                launcher.format(
                    self.system,
                    rom[1],
                    rom[2]
                ),
                "ActivateWindow(1101)"
            )
        )

        self.favorites_file.write(
            FAVORITES_ENTRY.format(
                rom[0],
                self.system,
                rom[2]
            )
        )

        self.calculate_jump(rom[0], count)

    def calculate_jump(self, title, count):
        current_letter = title.lower()[0]

        # First case
        if self.last_letter is None:
            self.last_letter = current_letter

            if current_letter.isalpha():
                self.jumplist_file.write(
                    JUMPLIST_ENTRY.format(
                        self.jump_count,
                        current_letter.upper(),
                        "SetFocus(9000,{})".format(0)
                    )
                )
            else:
                self.jumplist_file.write(
                    JUMPLIST_ENTRY.format(
                        self.jump_count,
                        "#",
                        "SetFocus(9000,{})".format(0)
                    )
                )

            self.jump_count += 1

            return

        # If we're still processing numbers and/or symbols, just skip until an alphanumeric value comes
        if not current_letter.isalpha():
            self.last_letter = current_letter
            return

        # We have an alphanumeric value now, but the last one wasn't, so the comparison may fail. Handle this
        # manually.
        if current_letter.isalpha() and (not self.last_letter.isalpha()):
            self.last_letter = current_letter
            self.jumplist_file.write(
                JUMPLIST_ENTRY.format(
                    self.jump_count,
                    current_letter.upper(),
                    "SetFocus(9000,{})".format(count)
                )
            )

            self.jump_count += 1
            return

        # If we are still in the same letter, or one before it
        if ord(current_letter) <= ord(self.last_letter):
            return

        self.jumplist_file.write(
            JUMPLIST_ENTRY.format(
                self.jump_count,
                current_letter.upper(),
                "SetFocus(9000,{})".format(count)
            )
        )

        self.last_letter = current_letter
        self.jump_count += 1

    def close(self):
        self.gamelist_file.write("\n</content>")

        self._finalize()

    def _finalize(self):
        self.gamelist_file.close()
        self.favorites_file.close()
        self.jumplist_file.close()

    def __del__(self):
        try:
            self._finalize()
        except Exception:
            print("Couldn't destroy gamelist creator for {}".format(self.system))
