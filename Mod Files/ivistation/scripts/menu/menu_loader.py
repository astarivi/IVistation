import fileinput
import os
import sys
import time

import xbmc
import xbmcgui
from utils.layout_helper import DEFAULT_LAYOUT_XML, MY_PROGRAMS_PATH, HEADER_DATA_EMU, FOOTER_DATA_EMU, TEMPLATE_JUMP_LIST, OVERLAY_JUMP_LIST


def main():
    # Get target system to load, try args first
    try:
        target_system = sys.argv[1:][0]
    # Nothing found, get it from the UI
    # Perhaps it would be better to always use the arguments?
    except Exception:
        target_system = xbmc.getInfoLabel('Container(9000).ListItem.Label2')

    dialog = xbmcgui.Dialog()

    xbmc.executebuiltin('Skin.SetString(emuname,{})'.format(target_system))
    gamelists_path = xbmc.translatePath('special://root/ivistation/gamelists/{}'.format(target_system))
    gamelist = os.path.join(gamelists_path, 'gamelist.xml')

    if not os.path.isfile(gamelist):
        print("Tried to load a gamelist, but it wasn't found.", gamelist)
        xbmc.executebuiltin('SetFocus(9000)')
        dialog.ok(
            "ERROR",
            "No game list found for this system.",
            "Rescan [B]{}[/B] games to fix this issue.".format(target_system),
            gamelist
        )
        xbmc.executebuiltin('Dialog.Close(1101,true)')
        return

    # Write the layout to MY_PROGRAMS_PATH by using DEFAULT_LAYOUT_XML as a template
    with open(DEFAULT_LAYOUT_XML, "r") as layout_file, open(MY_PROGRAMS_PATH, "w") as programs_file:
        programs_file.write(
            HEADER_DATA_EMU.format("default")
        )
        for code in layout_file:
            code = code.replace(
                "[ArtworkFolder]",
                "{}{}\$INFO[Skin.String({}_artworkfolder)]\\".format(
                    xbmc.getInfoLabel('skin.string(Custom_Media_Path)'),
                    xbmc.getInfoLabel('Skin.String(emuname)'),
                    target_system
                )
            )
            code = code.replace('[Artwork_Type]', target_system + '_artworkfolder')
            code = code.replace('[Fanart_Toggle]',
                                'Skin.HasSetting(' + xbmc.getInfoLabel('Skin.String(emuname)') + 'fanart)')
            code = code.replace('[Media_Path]',
                                xbmc.getInfoLabel('skin.string(Custom_Media_Path)') + xbmc.getInfoLabel(
                                    'Skin.String(emuname)'))
            code = code.replace('[CurrentSystem]', target_system)
            if '<!-- video preview mode horizontal -->' in code:
                xbmc.executebuiltin('Skin.SetBool(videopreviewhorizontal)')
            programs_file.write(code)
        programs_file.write(FOOTER_DATA_EMU)

    # Write the game list to the layout
    with open(gamelist, "r") as gamelist_file:
        gamelist_file = gamelist_file.read()
        gamelist_file = gamelist_file.replace('[ArtworkFolder]',
                                            xbmc.getInfoLabel('skin.string(Custom_Media_Path)') + xbmc.getInfoLabel(
                                                'Skin.String(emuname)') + '\$INFO[Skin.String(' + target_system + '_artworkfolder)]\\')
        for line in fileinput.FileInput(MY_PROGRAMS_PATH, inplace=True):
            if '<!-- content list this label is required -->' in line:
                line = line.replace(line, line + gamelist_file)
            print line,

    # Write the TEMPLATE_JUMP_LIST by using OVERLAY_JUMP_LIST as a template
    with open(TEMPLATE_JUMP_LIST, "w") as template_jump_list:
        with open(OVERLAY_JUMP_LIST, "r") as overlay_jump_list:
            template_jump_list.write(
                overlay_jump_list.read().replace("' + MenuLabel + '", target_system)
            )

    # Perform the actual data replacement for the jump list
    with open(os.path.join(gamelists_path, "jumplist.xml"), "r") as jump_file:
        jump_file = jump_file.read()
        for line in fileinput.FileInput(TEMPLATE_JUMP_LIST, inplace=True):
            if '<!-- jumpcode -->' in line:
                line = line.replace(line, line + jump_file)
            print line,

    time.sleep(0.2)
    xbmc.executebuiltin('ActivateWindow(Programs,Static_Menu,return)')
    xbmc.executebuiltin('Dialog.Close(1101,true)')


if __name__ == '__main__':
    print("Loading menu.")
    main()
