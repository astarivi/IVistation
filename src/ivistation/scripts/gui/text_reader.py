import os
import sys
import xbmcgui


def main():
    mode = sys.argv[1:][0]
    file_path = sys.argv[2:][0]

    dialog = xbmcgui.Dialog()

    # Changelog
    if mode == '0':
        if os.path.isfile(file_path):
            with open(file_path, "rb") as changelog_file:
                xbmcgui.Dialog().textviewer(
                    os.path.basename(file_path),
                    changelog_file.read()
                )
        else:
            print("Changes file not found at: ", file_path)
            dialog.ok("ERROR", "Cant find the changes file.")
    # Browse (Unused)
    elif mode == '1':
        file_path = dialog.browse(1, "Select file to view", 'files', '')
        if os.path.isfile(file_path):
            with open(file_path, "rb") as text_viewer:
                xbmcgui.Dialog().textviewer(os.path.basename(file_path), text_viewer.read())
    # View logs
    elif mode == '2':
        log_path = 'E:/TDATA/Rocky5 needs these Logs/'
        select_root = dialog.select("Select Log File", sorted(os.listdir(log_path)), 10000)
        if select_root == -1:
            pass
        else:
            select_file = os.path.join(log_path, sorted(os.listdir(log_path))[select_root])
            if os.path.isdir(select_file) and len(os.listdir(select_file)) > 0:
                select_root = dialog.select("Select Log File", sorted(os.listdir(select_file)), 10000)
                select_file = os.path.join(select_file, sorted(os.listdir(select_file))[select_root])
            else:
                xbmcgui.Dialog().ok("ERROR", "There are no logs to be viewed.", "", "This is a good thing.")
            if select_root == -1 or select_file == -1:
                pass
            else:
                file_path = select_file
                Input = os.path.basename(file_path)
                if os.path.isfile(file_path):
                    with open(file_path, "rb") as text_viewer:
                        xbmcgui.Dialog().textviewer(Input, text_viewer.read())


if __name__ == '__main__':
    print("text_reader.py: Initializing")
    main()
