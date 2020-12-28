# globalPlugins/NVDAextensionGlobalPlugin\special.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright 2018-2020 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import gui
import config
import wx
from gui import isInMessageBox, mainFrame


_NVDAMessageBox = None

# NVDA gui.messageBox method patched to say in all cases the window content.
# even if the user has chosen not to have NVDA announce the description of the object
def myMessageBox(message, caption=wx.MessageBoxCaptionStr, style=wx.OK | wx.CENTER, parent=None):
	"""Display a message dialog.
	This should be used for all message dialogs
	rather than using C{wx.MessageDialog} and C{wx.MessageBox} directly.
	@param message: The message text.
	@type message: str
	@param caption: The caption (title) of the dialog.
	@type caption: str
	@param style: Same as for wx.MessageBox.
	@type style: int
	@param parent: The parent window (optional).
	@type parent: C{wx.Window}
	@return: Same as for wx.MessageBox.
	@rtype: int
	"""
	global isInMessageBox
	option = config.conf["presentation"]["reportObjectDescriptions"]
	config.conf["presentation"]["reportObjectDescriptions"] = True
	wasAlready = isInMessageBox
	isInMessageBox = True
	if not parent:
		mainFrame.prePopup()
	res = wx.MessageBox(message, caption, style, parent or mainFrame)
	if not parent:
		mainFrame.postPopup()
	if not wasAlready:
		isInMessageBox = False
	config.conf["presentation"]["reportObjectDescriptions"] = option
	return res


def initialize():
	global _NVDAMessageBox
	# replace NVDA gui.messageBox by myMessageBox
	_NVDAMessageBox = gui.messageBox
	gui.messageBox = myMessageBox


def terminate():
	global _NVDAMessageBox
	# resume NVDA gui.messageBox
	if _NVDAMessageBox is not None:
		gui.messageBox = _NVDAMessageBox
		_NVDAMessageBox = None

