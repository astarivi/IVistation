import sys
import xbmc

ROOT_DIR = xbmc.translatePath("Special://root/")


def main():
    args = sys.argv[1:]
    game_title_id = args[1]
    game_xbe_path = args[2]

    if game_xbe_path.startswith("Q:\\"):
        game_xbe_path = game_xbe_path.replace("Q:\\", ROOT_DIR)

    xbmc.executebuiltin('Dialog.Close(134,false)')
    xbmc.executebuiltin("runxbe({})".format(
        game_xbe_path
    ))


if __name__ == '__main__':
    print("Launching Xbox game.")
    main()
