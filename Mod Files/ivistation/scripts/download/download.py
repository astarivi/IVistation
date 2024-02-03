import os
import sys
import xbmc
import xbmcgui
import traceback

from utils.installer import install_zip
from ivistation.downloader import download_file


class Download(object):
    def __init__(self, name, url, dwn_type):
        self.progress_dialog = xbmcgui.DialogProgress()
        self.progress_dialog.create("DOWNLOAD AND INSTALL", "Initializing...")
        self.name = name
        self.url = url
        self.type = dwn_type
        self.extension = url.split(".")[-1]

        self.download_file = "Z:\\download." + self.extension

    def _core_installer(self):
        core_path = xbmc.translatePath(
            "special://root/ivistation/emulators"
        )

        for progress, current_file in install_zip(self.download_file, core_path):
            self.progress_dialog.update(
                progress,
                "Installing " + self.name,
                "Current file: " + current_file,
                "This can take a long time, please be patient."
            )

    def download(self):
        if os.path.isfile(self.download_file):
            os.remove(self.download_file)

        # Download it using our slow downloader for large files
        for progress, download_speed in download_file(self.url, self.download_file):
            self.progress_dialog.update(
                progress,
                "Downloading {}".format(self.name),
                "Download speed: " + download_speed,
                "This can take some time, please be patient."
            )

        # Now let's install it
        if self.type == "cores":
            self._core_installer()

        self.progress_dialog.close()

        xbmcgui.Dialog().ok(
            "LIBRARY DOWNLOADER",
            self.name,
            "has been installed successfully."
        )


# TODO: CHECK IF THERE'S ENOUGH STORAGE SPACE TO DOWNLOAD THIS
if __name__ == '__main__':
    print("Starting download.py...")

    args = sys.argv[1:]

    downloader = Download(args[0], args[1], args[2])

    try:
        downloader.download()
    except Exception as e:
        print("Downloader failed!", args, e)
        traceback.print_exc()
        xbmcgui.Dialog().ok(
            "DOWNLOAD AND INSTALL",
            "Download failed."
        )
    finally:
        try:
            downloader.progress_dialog.close()
        except:
            pass
