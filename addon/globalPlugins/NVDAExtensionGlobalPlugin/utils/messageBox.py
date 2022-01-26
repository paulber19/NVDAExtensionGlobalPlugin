# globalPlugins/NVDAextensionGlobalPlugin\messageBox.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright 2018-2021 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import gui
import config
import wx
from typing import Optional


_NVDAMessageBox = None


# NVDA messageBox method patched to say in all cases the window content.
# even if the user has chosen not to have NVDA announce the description of the object
try:
	# for nvda version >= 2021.3
	import gui.message
	_reportObjectDescriptionOptions = []

	def myMessageBox(
		message: str,
		caption: str = wx.MessageBoxCaptionStr,
		style: int = wx.OK | wx.CENTER,
		parent: Optional[wx.Window] = None
	) -> int:
		"""Display a message dialog.
		This should be used for all message dialogs
		rather than using C{wx.MessageDialog} and C{wx.MessageBox} directly.
		@param message: The message text.
		@param caption: The caption (title) of the dialog.
		@param style: Same as for wx.MessageBox.
		@param parent: The parent window.
		@return: Same as for wx.MessageBox.
		"""
		from gui import mainFrame
		global _reportObjectDescriptionOptions
		with gui.message._messageBoxCounterLock:
			gui.message._messageBoxCounter += 1
			_reportObjectDescriptionOptions.append(config.conf["presentation"]["reportObjectDescriptions"])
		config.conf["presentation"]["reportObjectDescriptions"] = True
		try:
			if not parent:
				mainFrame.prePopup()
			res = wx.MessageBox(message, caption, style, parent or mainFrame)
			if not parent:
				mainFrame.postPopup()
		finally:
			with gui.message._messageBoxCounterLock:
				gui.message._messageBoxCounter -= 1
			config.conf["presentation"]["reportObjectDescriptions"] = _reportObjectDescriptionOptions.pop()
		return res

except ImportError:
	# for nvda version< 2021.3
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
		option = config.conf["presentation"]["reportObjectDescriptions"]
		config.conf["presentation"]["reportObjectDescriptions"] = True
		wasAlready = gui.isInMessageBox
		gui.isInMessageBox = True
		if not parent:
			gui.mainFrame.prePopup()
		res = wx.MessageBox(message, caption, style, parent or gui.mainFrame)
		if not parent:
			gui.mainFrame.postPopup()
		if not wasAlready:
			gui.isInMessageBox = False
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
