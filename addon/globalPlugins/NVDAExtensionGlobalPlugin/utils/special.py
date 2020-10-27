# globalPlugins/NVDAextensionGlobalPlugin\special.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright 2018-2020 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import gui
import config
import wx


_NVDAMessageBox = None



def myMessageBox(
	message,
	caption=wx.MessageBoxCaptionStr,
	style=wx.OK | wx.CENTER,
	parent=None):
	# NVDA function modified to say in all cases the window content
	global isInMessageBox
	
	option = config.conf["presentation"]["reportObjectDescriptions"]
	config.conf["presentation"]["reportObjectDescriptions"] = True
	res = _NVDAMessageBox(message, caption, style, parent or gui.mainFrame)
	config.conf["presentation"]["reportObjectDescriptions"] = option
	return res
def initialize():
	global _NVDAMessageBox
	_NVDAMessageBox = gui.messageBox
	gui.messageBox = myMessageBox

def terminate():
	global _NVDAMessageBox
	if _NVDAMessageBox is not None:
		gui.messageBox = _NVDAMessageBox
		_NVDAMessageBox = None

	