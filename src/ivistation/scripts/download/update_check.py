import xbmc
import simplejson as json

from download_loader import LISTING_URL
from ivistation.downloader import memory_download
from ivistation.utils import IVISTATION_VERSION


# TODO: Check for core updates here, too
def main():
    library = json.loads(
        memory_download(LISTING_URL, timeout=10)
    )

    for item in library["updates"]["items"]:
        if item["id"] != "ivistation":
            continue

        # We found the listing for the update, but is it actually newer?
        if IVISTATION_VERSION >= item["version"]:
            # We are in the latest version already
            return

        xbmc.executebuiltin(
            "Notification(IVistation Update Available,A new update has been found. v{})".format(
                item["version"]
            )
        )


if __name__ == '__main__':
    print("Checking for update.")
    try:
        main()
    except Exception as e:
        print("update_check failed due to ", e)
