import xbmc

# Handle resolution
resolution = xbmc.getInfoLabel('system.screenresolution')

if "PAL" in resolution:
    layout_type = "pal"
    xml_mode = "xml_sd_pal"
elif "NTSC" in resolution or "480p" in resolution:
    layout_type = "ntsc"
    xml_mode = "xml_sd_ntsc"
else:
    layout_type = "720p"
    xml_mode = "xml"

# Template
URL_DOWNLOADER_TEMPLATE = xbmc.translatePath(
    'special://root/ivistation/data/downloader/layout/_Script_URLDownloader_{}.xml'.format(layout_type)
)

# Target
URL_DOWNLOADER_TARGET = xbmc.translatePath(
    "special://skin/{}/_Script_URLDownloader.xml".format(xml_mode)
)

# Download items
DOWNLOAD_ITEM = '''
                                <item id="{}">
                                        <label>{}</label>
                                        <label2>{}</label2>
                                        <icon>{}[CR]{}</icon>
                                        <thumb>{type}/{}.{img_extension}</thumb>
                                        <onclick>Skin.SetString(downloader_label,"$INFO[Container(9001).ListItem.Label]")</onclick>
                                        <onclick>Skin.SetString(downloader_label2,"$INFO[Container(9001).ListItem.Label2]")</onclick>
                                        <onclick>Skin.SetString(downloader_actualicon,"$INFO[Container(9001).ListItem.ActualIcon]")</onclick>
                                        <onclick>Skin.SetString(downloader_thumb,"$INFO[Container(9001).ListItem.Thumb]")</onclick>
                                        <onclick>Skin.SetString(downloader_script,"RunScript(special://root/ivistation/scripts/download/download.py,{},{type})")</onclick>
                                        <onclick>ActivateWindow(1902)</onclick>
                                </item>
'''

DOWNLOAD_SECTION_HEADER = '''
                        <control type="panel" id="9001">
                            <include>Downloader_Content_Buttons</include>
                            <include>Downloader_Look_and_Feel</include>
                            <visible>ControlGroup(9000).HasFocus({focus_id})</visible>
                            <content>
                            <!-- Content here -->
'''

DOWNLOAD_SECTION_FOOTER = '''
                            </content>
                        </control>
'''

# Download labels
DOWNLOAD_VISIBILITY_TOGGLE = "ControlGroup(9000).HasFocus({})"

DOWNLOAD_LABEL_GROUP_LIST_HEADER = '''
                                <control type="grouplist" id="9000">
                                        <description>button area</description>
                                        <posx>-190</posx>
                                        <posy>0</posy>
                                        <width>200</width>
                                        <height>720</height>
                                        <onright>9001</onright>
                                        <align>center</align>
                                        <itemgap>10</itemgap>
                                        <orientation>vertical</orientation>
                                        <visible allowhiddenfocus="true">{visibility_toggles}</visible>
                                        <!-- Content here -->
'''

DOWNLOAD_LABEL_GROUP_LIST_FOOTER = '''
                                </control>
'''

DOWNLOAD_LABEL_SECTION = '''
                                        <control type="button" id="{id}">
                                                <width>180</width>
                                                <height>40</height>
                                                <label>{label}</label>
                                                <align>center</align>
                                                <textcolor>$VAR[tab_text_nofo_colour]</textcolor>
                                                <focusedcolor>$VAR[tab_text_fo_colour]</focusedcolor>
                                                <onfocus>Skin.SetString(downloader_tab_id,{id})</onfocus>
                                                <onclick>SetFocus(9001)</onclick>
                                                <colordiffuse>$VAR[tab_underlay_colour]</colordiffuse>
                                                <texturefocus>Special://root/ivistation/data/downloader/artwork/UI/buttonfo.jpg</texturefocus>
                                                <texturenofocus>-</texturenofocus>
                                        </control>
'''
