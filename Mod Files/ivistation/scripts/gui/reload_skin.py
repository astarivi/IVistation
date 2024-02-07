import xbmc
import xbmcgui


xbmcgui.Dialog().ok("RELOAD SKIN", "The current skin will be reloaded", "to apply pending changes.")
xbmc.executebuiltin('Skin.Reset(ReloadSkin)')
xbmc.executebuiltin('ActivateWindow(10000)')
xbmc.executebuiltin('ReloadSkin')
