import sys
import xbmcgui


# Ugly code, don't mind it
if __name__ == '__main__':
	args = sys.argv[1:]

	try:
		title = args[0]
	except:
		title = ""
	try:
		line1 = args[1]
	except:
		line1 = ""
	try:
		line2 = args[2]
	except:
		line2 = ""
	try:
		line3 = args[3]
	except:
		line3 = ""

	xbmcgui.Dialog().ok(title, line1, line2, line3)
