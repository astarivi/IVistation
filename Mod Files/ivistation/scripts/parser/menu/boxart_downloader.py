import os
import xbmc
import sqlite3
import urllib2

from ivistation.downloader import turbo_download
from ivistation.utils import clean_rom_name


# noinspection PyClassHasNoInit
class DownloadResult:
    SUCCESSFUL = 1
    FAILED = 2
    LOCAL_EXISTS = 3
    REMOTE_MISSING = 4


class BoxArtDownloader(object):
    enabled = True

    def __init__(self, system):
        self.system = system
        self.db_path = os.path.join(
            xbmc.translatePath("Special://root/ivistation/data/art"),
            system + ".db"
        )
        declared_media_path = xbmc.getInfoLabel('skin.string(Custom_Media_Path)')
        self.media_path = os.path.join(declared_media_path, system, "boxart")
        # TODO: Opt out of downloads here by setting enabled to false
        if xbmc.getCondVisibility('Skin.HasSetting(disable_art_download)') or not os.path.isfile(self.db_path):
            self.enabled = False
            return

        self.db_connection = sqlite3.connect(self.db_path)

    def download_artwork(self, title, target):
        target_path = os.path.join(self.media_path, target + ".jpg")
        cleaned_title = clean_rom_name(title.replace("'", "_"))

        # It already exists
        if os.path.isfile(target_path):
            return DownloadResult.LOCAL_EXISTS

        cursor = self.db_connection.cursor()

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
