# globalPlugins/NVDAextensionGlobalPlugin\gui\messageBoxPatches.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright 2025 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from logHandler import log
import gui
import gui.message
import config
import wx
from typing import Optional
from versionInfo import version_year, version_major


NVDAVersion = [version_year, version_major]
_NVDAGuiMessageBox = None
_NVDAGuiMessageMessageBox = None


# NVDA messageBox method patched to say in all cases the window content.
# even if the user has chosen not to have NVDA announce the description of the object

_reportObjectDescriptionOptions = []
if NVDAVersion < [2025, 1]:
	# for nvda version < 2025.1
	def myMessageBox(
		message: str,
		caption: str = wx.MessageBoxCaptionStr,
		style: int = wx.OK | wx.CENTER,
		parent: Optional[wx.Window] = None
	) -> int:
		"""Display a message dialog.
		Avoid using C{wx.MessageDialog} and C{wx.MessageBox} directly.
		@param message: The message text.
		@param caption: The caption (title) of the dialog.
		@param style: Same as for wx.MessageBox.
		@param parent: The parent window.
		@return: Same as for wx.MessageBox.
		`gui.message.messageBox` is a function which blocks the calling thread,
		until a user responds to the modal dialog.
		This function should be used when an answer is required before proceeding.
		Consider using a custom subclass of a wxDialog if an answer is not required
		or a default answer can be provided.

		It's possible for multiple message boxes to be open at a time.
		Before opening a new messageBox, use `isModalMessageBoxActive`
		to check if another messageBox modal response is still pending.

		Because an answer is required to continue after a modal messageBox is opened,
		some actions such as shutting down are prevented while NVDA is in a possibly uncertain state.
		"""
		from gui import mainFrame
		import core
		from logHandler import log
		global _reportObjectDescriptionOptions
		with gui.message._messageBoxCounterLock:
			gui.message._messageBoxCounter += 1
			_reportObjectDescriptionOptions.append(config.conf["presentation"]["reportObjectDescriptions"])
		config.conf["presentation"]["reportObjectDescriptions"] = True
		try:
			if not parent:
				mainFrame.prePopup()
			if not core._hasShutdownBeenTriggered:
				res = wx.MessageBox(message, caption, style, parent or mainFrame)
			else:
				log.debugWarning("Not displaying message box as shutdown has been triggered.", stack_info=True)
				res = wx.ID_CANCEL
		finally:
			if not parent:
				mainFrame.postPopup()
			with gui.message._messageBoxCounterLock:
				gui.message._messageBoxCounter -= 1
			config.conf["presentation"]["reportObjectDescriptions"] = _reportObjectDescriptionOptions.pop()
		return res
else:
	# for NVDA version >= 2025.1
	_NVDAMessageDialogShowModal = None

	def myMessageDialogFunc(func, *args, **kwargs):
		global _reportObjectDescriptionOptions
		log.debug("myMessageDialogInit")
		c = config.conf
		pre = c["presentation"]["reportObjectDescriptions"]
		_reportObjectDescriptionOptions.append((c, pre))
		c["presentation"]["reportObjectDescriptions"] = True
		res = func(*args, **kwargs)
		(c, pre) = _reportObjectDescriptionOptions.pop()
		c["presentation"]["reportObjectDescriptions"] = pre
		return res

	def myMessageBox(*args, **kwargs):
		return myMessageDialogFunc(_NVDAGuiMessageMessageBox, *args, **kwargs)

	def myMessageDialogShowModal(*args, **kwargs):
		return myMessageDialogFunc(_NVDAMessageDialogShowModal, *args, **kwargs)


def initialize():
	global _NVDAGuiMessageBox, _NVDAGuiMessageMessageBox
	# replace nvda gui.messageBox and NVDA gui.message.messageBox by myMessageBox
	_NVDAGuiMessageBox = gui.messageBox
	_NVDAGuiMessageMessageBox = gui.message.messageBox
	gui.messageBox = myMessageBox
	gui.message.messageBox = myMessageBox
	log.debug(
		"gui.messageBox and gui.message.messageBox patched by: %s of %s module "
		% (myMessageBox.__name__, myMessageBox.__module__))
	if NVDAVersion >= [2025, 1]:
		# for nvda version >= 2025.1
		global _NVDAMessageDialogShowModal
		from gui.message import MessageDialog
		_NVDAMessageDialogShowModal = MessageDialog.ShowModal
		MessageDialog.ShowModal = myMessageDialogShowModal
		log.debug(
			"gui.message.MessageDialog.ShowModal patched by: %s of %s module "
			% (myMessageDialogShowModal.__name__, myMessageDialogShowModal.__module__))


def terminate():
	global _NVDAGuiMessageBox, _NVDAGuiMessageMessageBox
	# restore NVDA gui.messageBox and gui.message.messageBox
	if _NVDAGuiMessageMessageBox is not None:
		gui.messageBox = _NVDAGuiMessageBox
		_NVDAGuiMessageBox = None
		gui.message.messageBox = _NVDAGuiMessageMessageBox
		_NVDAGuiMessageMessageBox = None
	if NVDAVersion >= [2025, 1]:
		# for nvda version >= 2025.1
		global _NVDAMessageDialogShowModal
		if _NVDAMessageDialogShowModal is not None:

			from gui.message import MessageDialog
			MessageDialog.ShowModal = _NVDAMessageDialogShowModal
