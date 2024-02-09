import os
import xbmc

# Handle resolution
resolution = xbmc.getInfoLabel('system.screenresolution')

if "PAL" in resolution and os.path.isdir(xbmc.translatePath('special://skin/xml_sd_pal')):
    print("SD PAL Mode")
    layout_mode = "/sd_pal"
    xml_mode = "xml_sd_pal/"
elif ("NTSC" in resolution and os.path.isdir(xbmc.translatePath('special://skin/xml_sd_ntsc')) or "480p" in resolution
      and os.path.isdir(xbmc.translatePath('special://skin/xml_sd_ntsc'))):
    print "SD NTSC Mode"
    layout_mode = "/sd_ntsc"
    xml_mode = "xml_sd_ntsc/"
else:
    print ">720p"
    layout_mode = ""
    xml_mode = "xml/"

# Handle layout type
if xbmc.getCondVisibility('Skin.HasSetting(synopsislayout)'):
    layout = "synopsis_layout.xml"
elif xbmc.getCondVisibility('Skin.HasSetting(thumblayout)'):
    layout = "thumb_layout.xml"
else:
    layout = "layout.xml"

# - Export variables

# Emulator listings
DEFAULT_LAYOUT_PATH = xbmc.translatePath('special://skin/layouts/default' + layout_mode)
DEFAULT_LAYOUT_XML = os.path.join(DEFAULT_LAYOUT_PATH, layout)
MY_PROGRAMS_PATH = xbmc.translatePath('special://skin/{}MyPrograms.xml'.format(xml_mode))
TEMPLATE_JUMP_LIST = xbmc.translatePath('special://skin/{}_script_jumpList.xml'.format(xml_mode))
OVERLAY_JUMP_LIST = xbmc.translatePath('special://skin/{}Includes_layout_overlay.xml'.format(xml_mode))
HEADER_DATA_EMU = '''<window type="window" id="1">
        <onunload condition="Player.HasVideo">Stop</onunload>
        <defaultcontrol always="true">9000</defaultcontrol>
        <allowoverlay>no</allowoverlay>
        <view>50</view>
        <layout>{}</layout>
        <controls>
        <control type="button" id="9200">
            <left>-500</left>
        </control>
        <control type="group">
                <visible>!Window.IsVisible(1101)</visible>
                <animation type="Hidden">
                        <effect type="fade" start="100" end="0" delay="1100" time="1000"/>
                </animation>
                <include>CommonBackground</include>
        </control>
        <control type="group">
        <include>Layout_Animation</include>
        <animation type="Hidden">
                <effect type="zoom" start="100" end="200" center="auto" easing="in" tween="cubic" delay="100" time="1100"/>
                <effect type="fade" start="100" end="0" delay="300" time="600"/>
        </animation>
        <visible>!Window.IsVisible(1101)</visible>
        <!-- Used to run the script and stop folk moving the list forward or backwards -->
        <control type="button" id="9999">
            <left>-500</left>
            <onfocus>RunScript(special://root/ivistation/scripts/gui/play_preview.py)</onfocus>
            <visible>!Skin.HasSetting(videolayout)</visible>
        </control>
        <control type="button" id="9990">
            <left>-500</left>
            <onfocus>SetFocus(9000)</onfocus>
            <onfocus>ActivateWindow(1120)</onfocus>
        </control>
        <!-- Used to stop playback if one of the direction buttons are pressed or the (A) button -->
        <control type="button" id="9100">
            <left>-500</left>
            <onup>setfocus(9000)</onup>
            <ondown>setfocus(9000)</ondown>
            <onleft>setfocus(9000)</onleft>
            <onright>setfocus(9000)</onright>
            <onclick>setfocus(9000)</onclick>
            <onup>stop</onup>
            <ondown>stop</ondown>
            <onleft>stop</onleft>
            <onright>stop</onright>
            <onclick>stop</onclick>
            <onup>Control.Move(9000,-1)</onup>
            <ondown>Control.Move(9000,1)</ondown>
            <onleft>PageUp</onleft>
            <onright>PageDown</onright>
            <visible>!Skin.HasSetting(videolayout) + !Skin.HasSetting(videopreviewhorizontal)</visible>
        </control>
        <control type="button" id="9100">
            <left>-500</left>
            <onup>setfocus(9000)</onup>
            <ondown>setfocus(9000)</ondown>
            <onleft>setfocus(9000)</onleft>
            <onright>setfocus(9000)</onright>
            <onclick>setfocus(9000)</onclick>
            <onup>stop</onup>
            <ondown>stop</ondown>
            <onleft>stop</onleft>
            <onright>stop</onright>
            <onclick>stop</onclick>
            <onup>PageDown</onup>
            <ondown>PageUp</ondown>
            <onleft>Control.Move(9000,-1)</onleft>
            <onright>Control.Move(9000,1)</onright>
            <visible>!Skin.HasSetting(videolayout) + Skin.HasSetting(videopreviewhorizontal)</visible>
        </control>
    '''

FOOTER_DATA_EMU = '''
    </control>
    </controls>
    </window>
'''

# XBE listings
XBE_LAYOUT_XML = os.path.join(DEFAULT_LAYOUT_PATH, "XBE files", layout)

HEADER_DATA_XBE = '''<window id="1">
    <onunload condition="Player.HasVideo">Stop</onunload>
    <defaultcontrol always="true">50</defaultcontrol>
    <allowoverlay>no</allowoverlay>
    <view>50</view>
    <layout>{}</layout>
    <controls>
        <include>CommonBackground</include>
        <control type="group">
            <include>Layout_Animation</include>
            <control type="button" id="9990">
                <left>-500</left>
                <onfocus>SetFocus(50)</onfocus>
                <onfocus>ContextMenu</onfocus>
            </control>
            <control type="button" id="9000">
                <left>-500</left>
                <onfocus>SetFocus(50)</onfocus>
            </control>
            <!-- Used to stop playback if one of the direction buttons are pressed or the (A) button -->
            <control type="button" id="9100">
                <left>-500</left>
                <onup>setfocus(50)</onup>
                <ondown>setfocus(50)</ondown>
                <onleft>setfocus(50)</onleft>
                <onright>setfocus(50)</onright>
                <onclick>setfocus(50)</onclick>
                <onup>stop</onup>
                <ondown>stop</ondown>
                <onleft>stop</onleft>
                <onright>stop</onright>
                <onclick>stop</onclick>
                <onup>Control.Move(50,-1)</onup>
                <ondown>Control.Move(50,1)</ondown>
                <onleft>PageUp</onleft>
                <onright>PageDown</onright>
            </control>
    '''

FOOTER_DATA_XBE = '''
    </control>
    </controls>
    </window>
'''

# Home
HOME_LAYOUT_XML = xbmc.translatePath('special://skin/{}Home.xml'.format(xml_mode))
DEFAULT_HOME_LAYOUT = xbmc.translatePath('special://skin/layouts/home{}/layout.xml'.format(layout_mode))

HEADER_DATA_HOME = '''
<window id="10000">
    <defaultcontrol always="true">9000</defaultcontrol>
    <onload>Skin.Reset(editmode)</onload>
    <onload>Skin.Reset(videopreviewhorizontal)</onload>
    <controls>
        <include>SecretPassCode</include>
        <control type="button" id="9100">
            <left>-500</left>
            <onclick>-</onclick>
        </control>
        <control type="button" id="9999">
            <left>-500</left>
            <onfocus>ActivateWindow(Screensaver)</onfocus>
            <visible>!Player.HasAudio</visible>
            <animation effect="fade" start="0" end="100" time="100" delay="1000">WindowOpen</animation>
        </control>
        <control type="button" id="9999">
            <left>-500</left>
            <onfocus>ActivateWindow(2006)</onfocus>
            <visible>Player.HasAudio</visible>
            <animation effect="fade" start="0" end="100" time="100" delay="1000">WindowOpen</animation>
        </control>
        <include>CommonBackground</include>
        <control type="group">
            <include>Home_Animation</include>
            <include>Home_Fav_Animation</include>
'''

FOOTER_DATA_HOME = '''
    </control>
    <include>overlay_plane</include>
    </controls>
</window>
'''

# Favorites
FAVS_LAYOUT_XML = xbmc.translatePath('special://skin/{}DialogFavourites.xml'.format(xml_mode))
DEFAULT_FAVS_LAYOUT = xbmc.translatePath('special://skin/layouts/favs{}/{}'.format(layout_mode, layout))

HEADER_DATA_FAVS = '''
<window type="dialog" id="134">
    <defaultcontrol always="true">450</defaultcontrol>
    <onunload>Skin.Reset(favsloading)</onunload>
    <include>Fav_Layout_Animation</include>
    <controls>
        <control type="button" id="9990">
            <left>-500</left>
            <onfocus>SetFocus(1000)</onfocus>
        </control>
'''

FOOTER_DATA_FAVS = '''
    </controls>
    </window>
'''