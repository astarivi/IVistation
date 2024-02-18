import os
import glob
import xbmc
import fileinput

from utils.layout_helper import HOME_LAYOUT_XML, DEFAULT_HOME_LAYOUT, HEADER_DATA_HOME, FOOTER_DATA_HOME


def main():
    if xbmc.getCondVisibility('Skin.HasSetting(sort_system_name)'):
        sort_type = xbmc.translatePath('special://skin/system_list/_Sort_Name')
    else:
        sort_type = xbmc.translatePath('special://skin/system_list/_Sort_ID')

    system_list_xml = xbmc.translatePath('special://skin/system_list/system_list.xml')

    if not os.path.isdir(sort_type):
        print("Sort requested, because '", sort_type, "' folder does not exist.")
        return

    try:
        os.remove(HOME_LAYOUT_XML)
        with open(DEFAULT_HOME_LAYOUT, "r") as layout_file, open(HOME_LAYOUT_XML, "w") as output_file:
            output_file.write(HEADER_DATA_HOME)
            for line in layout_file:
                output_file.write(line)
            output_file.write(FOOTER_DATA_HOME)
    except Exception as e:
        print("Failed to sort carousel, failed to delete current Home.XML due to ", e)

    xml_counter = 0
    files = sorted(glob.glob(sort_type + '/*.xml'))
    with open(system_list_xml, "w") as outfile:
        outfile.write('<content>\n')
        # astarivi: Why twice?
        for xml in files:
            if "direct launch" not in xml.lower():
                with open(xml, "r") as infile:
                    outfile.write(infile.read().replace('<item id="">', '<item id="' + str(xml_counter) + '">'))
                xml_counter += 1
        for xml in files:
            if "direct launch" in xml.lower():
                with open(xml, "r") as infile:
                    outfile.write(infile.read().replace('<item id="">', '<item id="' + str(xml_counter) + '">'))
                xml_counter += 1
        outfile.write('\n</content>')

    with open(system_list_xml, "r") as fin:
        fin = fin.read()
        for line in fileinput.FileInput(HOME_LAYOUT_XML, inplace=True):
            if '</focusedlayout>' in line:
                if "</focusedlayout> <!-- don't populate -->" not in line:
                    line = line.replace(line, line + fin)
            elif '<!-- Home_Layout -->' in line:
                line = line.replace(line, line + fin)
            print line,


if __name__ == '__main__':
    print("Loading menu.")
    main()
