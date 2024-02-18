VERSION := 1
XBMC_FOLDER := XBMC
TARGET_FOLDER := IVistation

.PHONY: all, build, clean

build:
	cp -r $(XBMC_FOLDER) $(TARGET_FOLDER)
	rm -rf $(TARGET_FOLDER)/plugins
	rm -rf $(TARGET_FOLDER)/sounds
	rm -rf $(TARGET_FOLDER)/userdata
	rm -rf $(TARGET_FOLDER)/visualisations
	rm -rf $(TARGET_FOLDER)/web
	rm -rf $(TARGET_FOLDER)/system/keymaps
	rm -rf $(TARGET_FOLDER)/system/cdrip
	rm -rf $(TARGET_FOLDER)/system/scrapers
	rm -rf $(TARGET_FOLDER)/system/players/mplayer/codecs
	rm -rf $(TARGET_FOLDER)/skin
	rm -rf $(TARGET_FOLDER)/scripts
	rm -rf $(TARGET_FOLDER)/screensavers
	rm -f $(TARGET_FOLDER)/system/filezilla\ server.xml
	rm -f $(TARGET_FOLDER)/copying.txt
	rm -f $(TARGET_FOLDER)/keymapping.txt
	rm -f $(TARGET_FOLDER)/media/icon.png
	rm -f $(TARGET_FOLDER)/media/Splash_2007.png
	rm -f $(TARGET_FOLDER)/media/Splash_2008.png
	rm -f $(TARGET_FOLDER)/media/weather.rar
	mv $(TARGET_FOLDER)/media $(TARGET_FOLDER)/system/
	mv $(TARGET_FOLDER)/language $(TARGET_FOLDER)/system/
	cp -r src/* $(TARGET_FOLDER)/
	mkdir -p $(TARGET_FOLDER)/system/SystemInfo
	rm -f $(TARGET_FOLDER)/default.xbe
	cp edits/default.xbe $(TARGET_FOLDER)/default.xbe
	rm -f $(TARGET_FOLDER)/system/SystemInfo/changes.txt
	cp Changes.txt $(TARGET_FOLDER)/system/SystemInfo/changes.txt
	sed -i 's/xbmc-emustation\ 0.0.000/IVistation\ v$(VERSION)/g' src/ivistation/themes/simple/language/English/strings.po
	sed -i 's/xbmc-emustation\ 0.0.000/IVistation\ v$(VERSION)/g' src/ivistation/themes/simple/language/French/strings.po
	wget -P $(TARGET_FOLDER) https://github.com/astarivi/IVistation-Updater/releases/latest/download/update.xbe

clean:
	rm -rf $(TARGET_FOLDER)