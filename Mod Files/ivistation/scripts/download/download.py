import os
import sys
import zlib
import xbmc
import base64
import xbmcgui
import traceback
import simplejson as json

from contextlib import closing
from utils.installer import install_zip, calculate_crc32, get_update_installer_version
from ivistation.downloader import download_file
from ivistation.utils import IVISTATION_VERSION


class Download(object):
    def __init__(self, dwn_type, entry):
        xbmc.executebuiltin("Skin.Reset(SelectPreviewMode)")

        # gui
        self.dialog = xbmcgui.Dialog()
        self.progress_dialog = xbmcgui.DialogProgress()
        self.progress_dialog.create("DOWNLOAD AND INSTALL", "Initializing...")

        # data
        self.entry = entry
        self.type = dwn_type
        self.self_update = self.entry["id"] == "ivistation"

        # path
        if self.self_update:
            self.download_file = "Q:\\update.tar"
        else:
            self.download_file = "Z:\\download." + self.entry["url"].split(".")[-1]

    def _get_available_mounts(self):
        default_routes = [
            "E:\\",
            "F:\\",
            "G:\\"
        ]

        valid_mounts = []

        total_routes = float(len(default_routes))
        count = 0

        for mount_point in default_routes:
            count += 1

            self.progress_dialog.update(
                int((count / total_routes) * 100),
                "Testing existing mount points",
                "Current point: " + mount_point,
                "This shouldn't take much time."
            )

            if os.path.isdir(mount_point):
                valid_mounts.append(mount_point)

        return valid_mounts

    def _cancel_install(self):
        if os.path.isfile(self.download_file):
            os.remove(self.download_file)

        self.dialog.ok(
            "LIBRARY DOWNLOADER",
            "Installation cancelled by user."
        )

        raise KeyboardInterrupt

    def _generic_installer(self, i_path):
        for progress, current_file in install_zip(self.download_file, i_path):
            self.progress_dialog.update(
                progress,
                "Installing " + self.entry["title"],
                "Current file: " + current_file,
                "This can take a long time, please be patient."
            )

    def _apps_installer(self):
        mount_points = [point + "Apps\\" for point in self._get_available_mounts()]
        mount_points.append("LET ME PICK WHERE")

        result = self.dialog.select("SELECT INSTALL DRIVE", mount_points)

        if result == -1:
            self._cancel_install()

        result_point = mount_points[result]

        if result_point == "LET ME PICK WHERE":
            user_path = self.dialog.browse(0, "Select install folder", "files")

            if not os.path.isdir(user_path):
                self.dialog.ok(
                    "LIBRARY DOWNLOADER",
                    "Invalid selection."
                )
                self._cancel_install()

            result_point = user_path

        if not os.path.isdir(result_point):
            os.makedirs(result_point)

        for progress, current_file in install_zip(self.download_file, result_point):
            self.progress_dialog.update(
                progress,
                "Installing " + self.entry["title"],
                "Current file: " + current_file,
                "This can take a long time, please be patient."
            )

    def _self_update_install(self):
        if "checksum" in self.entry and self.entry["checksum"] is not None:
            expected_checksum = self.entry["checksum"].lower()
            crc32_checksum = None

            for progress, checksum in calculate_crc32(self.download_file):
                self.progress_dialog.update(
                    progress,
                    "Verifying update integrity",
                    "This can take a long time, please be patient."
                )

                # We're done
                if checksum != "":
                    crc32_checksum = checksum
                    break

            # If we don't match
            if expected_checksum != crc32_checksum:
                self.dialog.ok(
                    "UPDATE INSTALLER",
                    "Invalid checksum, corrupt update file.",
                    "Expected: " + expected_checksum,
                    "Got: " + crc32_checksum
                )
                print("Invalid checksum for platform update", expected_checksum, crc32_checksum)
                os.remove(self.download_file)
                raise KeyboardInterrupt

        # Valid file, keep going with the installation
        xbmc.executebuiltin("runxbe({})".format(
            xbmc.translatePath(
                "special://root/update.xbe"
            )
        ))
        raise KeyboardInterrupt

    def download(self):
        if os.path.isfile(self.download_file):
            os.remove(self.download_file)

        # If we require a higher version of IVistation
        if self.entry["required_version"] > IVISTATION_VERSION:
            self.dialog.ok(
                "INVALID VERSION",
                "Please update IVistation to use this package.",
                "Required version: v" + str(self.entry["required_version"]),
                "Current version: v" + str(IVISTATION_VERSION)
            )
            raise KeyboardInterrupt

        # If we're trying to update IVistation and require a newer update.xbe
        if self.self_update:
            updater_version = get_update_installer_version()
            if self.entry["required_updater"] > get_update_installer_version():
                current_version = str(updater_version) if updater_version != -1 else "MISSING!"

                self.dialog.ok(
                    "INVALID UPDATER",
                    "Please upgrade 'IVistation Updater'.",
                    "Required version: v" + str(self.entry["required_updater"]),
                    "Current version: v" + current_version
                )
                raise KeyboardInterrupt

        # Download it using our slow downloader for large files
        for progress, download_speed in download_file(self.entry["url"], self.download_file):
            self.progress_dialog.update(
                progress,
                "Downloading {}".format(self.entry["title"]),
                "Download speed: " + download_speed,
                "This can take some time, please be patient."
            )

        # Now let's install it
        if self.self_update:
            # This shouldn't return
            self._self_update_install()
        elif self.type == "cores":
            self._generic_installer(
                xbmc.translatePath(
                    "special://root/ivistation/emulators"
                )
            )
        elif self.type == "updates":
            self._generic_installer(
                xbmc.translatePath(
                    "special://root/ivistation"
                )
            )
        elif self.type == "apps":
            self._apps_installer()

        self.progress_dialog.close()

        self.dialog.ok(
            "LIBRARY DOWNLOADER",
            self.entry["title"],
            "has been installed successfully."
        )


# TODO: CHECK IF THERE'S ENOUGH STORAGE SPACE TO DOWNLOAD THIS
def run_downloader(dwn_type, entry):
    xbmc.executebuiltin('Dialog.Close(1101,true)')
    downloader = Download(dwn_type, entry)

    try:
        downloader.download()
    except Exception as e:
        print("Downloader failed!", dwn_type, entry, e)
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


if __name__ == '__main__':
    print("Starting download.py...")

    args = sys.argv[1:]

    with closing(xbmcgui.DialogProgress()) as dialog_window:
        dialog_window.create("DOWNLOAD AND INSTALL", "...Decoding data...")
        decoded_data = json.loads(zlib.decompress(base64.b64decode(args[1])))

    run_downloader(
        args[0],
        decoded_data
    )
