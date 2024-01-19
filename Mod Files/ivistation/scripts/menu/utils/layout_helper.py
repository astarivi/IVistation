import os
import xbmc


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

DEFAULT_LAYOUT_PATH = xbmc.translatePath('special://xbmc/emustation/themes/simple/layouts/default' + layout_mode)
DEFAULT_LAYOUT_XML = os.path.join(DEFAULT_LAYOUT_PATH, 'layout.xml')
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
            <onfocus>RunScript(special://emustation_scripts/play_preview.py)</onfocus>
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