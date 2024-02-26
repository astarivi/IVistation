import os
import xbmc
import sqlite3
import urllib
import urllib2

from contextlib import closing
from ivistation.utils import clean_rom_name
from ivistation.downloader import turbo_download, libretro_thumbnail_download


# noinspection PyClassHasNoInit
class DownloadResult:
    SUCCESSFUL = 1
    FAILED = 2
    LOCAL_EXISTS = 3
    REMOTE_MISSING = 4
    INVALID_LOCAL = 5


class LibRetroBoxArtDownloader(object):
    remote_systems = {
        "gba": "Nintendo_-_Game_Boy_Advance",
        "gbc": "Nintendo_-_Game_Boy_Color",
        "gb": "Nintendo_-_Game_Boy",
        "n64": "Nintendo_-_Nintendo_64",
        "snes": "Nintendo_-_Super_Nintendo_Entertainment_System",
        "nes": "Nintendo_-_Nintendo_Entertainment_System"

    }
    remote_url = "https://raw.githubusercontent.com/libretro-thumbnails/{}/master/Named_Boxarts/{}.png"

    def __init__(self, system):
        self.system = system
        self.remote_system = self.remote_systems[system]
        declared_media_path = xbmc.getInfoLabel('skin.string(Custom_Media_Path)')
        self.media_path = os.path.join(declared_media_path, system, "boxart")

    def download_artwork(self, title, target):
        target_path = os.path.join(self.media_path, target + ".jpg")

        if os.path.isfile(target_path):
            return DownloadResult.LOCAL_EXISTS

        download_url = self.remote_url.format(self.remote_system, urllib.quote(title))

        try:
            libretro_thumbnail_download(download_url, target_path)
        except urllib2.HTTPError as e:
            # We could try again later.
            if e.code == 404 or e.code == 500:
                return DownloadResult.REMOTE_MISSING
            print("Failed to download artwork from ", download_url, " due to HTTPError: ", e)
            return DownloadResult.FAILED
        except Exception as e:
            print("Failed to download artwork from ", download_url, " due to: ", e)
            return DownloadResult.FAILED

        return DownloadResult.SUCCESSFUL

    def close(self):
        pass


class IViBoxArtDownloader(object):
    def __init__(self, system):
        self.system = system
        self.db_path = os.path.join(
            xbmc.translatePath("Special://root/ivistation/data/art"),
            system + ".db"
        )
        declared_media_path = xbmc.getInfoLabel('skin.string(Custom_Media_Path)')
        self.media_path = os.path.join(declared_media_path, system, "boxart")

        self.db_connection = sqlite3.connect(self.db_path)

    def download_artwork(self, title, target):
        target_path = os.path.join(self.media_path, target + ".jpg")

        if os.path.isfile(target_path):
            return DownloadResult.LOCAL_EXISTS

        cleaned_title = clean_rom_name(title.replace("'", "_"))

        with closing(self.db_connection.cursor()) as cursor:
            select_query = '''
                SELECT * FROM root WHERE name = ?;
            '''

            cursor.execute(select_query, (cleaned_title,))

            row = cursor.fetchone()

            if row is None:
                return DownloadResult.REMOTE_MISSING

            url = row[2]

        try:
            turbo_download(url, target_path)
        except urllib2.HTTPError as e:
            # We could try again later.
            if e.code == 404 or e.code == 500:
                return DownloadResult.REMOTE_MISSING
            print("Failed to download artwork from ", url, " due to HTTPError: ", e)
            return DownloadResult.FAILED
        except Exception as e:
            print("Failed to download artwork from ", url, " due to: ", e)
            return DownloadResult.FAILED

        return DownloadResult.SUCCESSFUL

    def close(self):
        if hasattr(self, 'db_connection') and self.db_connection is not None:
            self.db_connection.close()

    def __del__(self):
        try:
            self.close()
        except Exception as e:
            print("Couldn't destroy boxart downloader for {} due to: ".format(self.system), e)


class BoxArtDownloader(object):
    ivi_systems = [os.path.splitext(_sys)[0] for _sys in os.listdir(xbmc.translatePath("Special://root/ivistation/data/art"))]
    libretro_systems = LibRetroBoxArtDownloader.remote_systems.keys()

    def __init__(self, system):
        self.enabled = True
        self.downloader = None

        if xbmc.getCondVisibility('Skin.HasSetting(disable_art_download)'):
            self.enabled = False
            return

        if xbmc.getCondVisibility('Skin.HasSetting(prefer_libretro_thumbs)'):
            if system in self.libretro_systems:
                self.downloader = IViBoxArtDownloader(system)
            elif system in self.ivi_systems:
                self.downloader = LibRetroBoxArtDownloader(system)
            else:
                self.enabled = False
        else:
            if system in self.ivi_systems:
                self.downloader = IViBoxArtDownloader(system)
            elif system in self.libretro_systems:
                self.downloader = LibRetroBoxArtDownloader(system)
            else:
                self.enabled = False

    @staticmethod
    def _cut_filename(filename):
        """
        If the sole filename is too long to fit the extension, cut it down.
        """
        return filename[:38] if len(filename) > 38 else filename

    def download_artwork(self, rom):
        # If we have an .xbe, use the folder name for the thumbnail
        if rom[2].endswith(".xbe"):
            if rom[1] is None or rom[1].strip() == "":
                return DownloadResult.INVALID_LOCAL

            self.downloader.download_artwork(
                rom[1],
                self._cut_filename(
                    os.path.basename(
                        os.path.dirname(rom[2])
                    )
                )
            )
        else:
            self.downloader.download_artwork(
                rom[0],
                self._cut_filename(
                    os.path.splitext(
                        os.path.basename(
                            rom[2]
                        )
                    )[0]
                )
            )

    def close(self):
        if hasattr(self, 'downloader') and self.downloader is not None:
            self.downloader.close()

    def __del__(self):
        try:
            self.close()
        except Exception as e:
            print("Couldn't destroy boxart downloader", e)
