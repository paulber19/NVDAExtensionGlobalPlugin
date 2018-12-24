# shared/vlc_special.py
# a part of VLC media player add-on
# Copyright 2018 paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import addonHandler
addonHandler.initTranslation()
from logHandler import log
import gui
from gui import mainFrame, isInMessageBox
import config
import wx

# function modified to say in all cases the window content 
def messageBox(message, caption=wx.MessageBoxCaptionStr, style=wx.OK | wx.CENTER, parent=None):
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
	wasAlready = isInMessageBox
	isInMessageBox = True
	if not parent:
		mainFrame.prePopup()
	option = config.conf["presentation"]["reportObjectDescriptions"]
	config.conf["presentation"]["reportObjectDescriptions"] = True
	res = wx.MessageBox(message, caption, style, parent or mainFrame)
	config.conf["presentation"]["reportObjectDescriptions"] = option
	if not parent:
		mainFrame.postPopup()
	if not wasAlready:
		isInMessageBox = False
	return res
