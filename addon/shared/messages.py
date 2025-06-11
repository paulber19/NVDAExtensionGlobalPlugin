# globalPlugins\shared\npp_message.py
# a part of notepadPluPlusAccessEnhancement add-on
# Copyright 2025 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import gui
import gui.message
import wx
from enum import IntEnum
from versionInfo import version_year, version_major
NVDAVersion = [version_year, version_major]

if NVDAVersion < [2025, 1]:

	class ReturnCode(IntEnum):
		"""Enumeration of possible returns from :class:`MessageDialog`."""

		OK = wx.ID_OK
		CANCEL = wx.ID_CANCEL
		YES = wx.ID_YES
		NO = wx.ID_NO
		SAVE = wx.ID_SAVE
		APPLY = wx.ID_APPLY
		CLOSE = wx.ID_CLOSE
		HELP = wx.ID_HELP
		CUSTOM_1 = wx.ID_HIGHEST + 1
		CUSTOM_2 = wx.ID_HIGHEST + 2
		CUSTOM_3 = wx.ID_HIGHEST + 3
		CUSTOM_4 = wx.ID_HIGHEST + 4
		CUSTOM_5 = wx.ID_HIGHEST + 5

	def confirm(message, caption):
		ret = gui.messageBox(
			message,
			caption,
			wx.OK | wx.CANCEL | wx.ICON_QUESTION)
		if ret == wx.OK:
			return ReturnCode.OK
		return ReturnCode.CANCEL

	def confirm_YesNo(message, caption):
		ret = gui.messageBox(
			message,
			caption,
			wx.YES | wx.NO | wx.ICON_QUESTION)
		if ret == wx.YES:
			return ReturnCode.YES
		return ReturnCode.NO

	def ask(message, caption):
		ret = gui.messageBox(
			message,
			caption,
			wx.YES | wx.NO | wx.CANCEL | wx.ICON_QUESTION)
		if ret == wx.YES:
			return ReturnCode.YES
		if ret == wx.NO:
			return ReturnCode.NO
		return ReturnCode.CANCEL

	def warn(message, caption):
		gui.messageBox(message, caption, wx.OK | wx.ICON_WARNING)

	def alert(message, caption):
		gui.messageBox(message, caption, wx.OK | wx.ICON_ERROR)

	def inform(message, caption):
		gui.messageBox(message, caption, wx.OK | wx.ICON_INFORMATION)

else:
	# for nvda versions >= 2025.1
	from gui.message import MessageDialog, ReturnCode

	def confirm_YesNo(message, caption):
		return MyMessageDialog.confirm_YesNo(message, caption, gui.mainFrame)

	def ask(message, caption):
		return MessageDialog.ask(message, caption, gui.mainFrame)

	def warn(message, caption):
		MyMessageDialog.warn(message, caption, gui.mainFrame)

	def alert(message, caption):
		MyMessageDialog.alert(message, caption, gui.mainFrame)

	def inform(message, caption):
		MyMessageDialog.inform(message, caption, gui.mainFrame)

	from gui.message import DefaultButton, DefaultButtonSet, DialogType
	from gui.guiHelper import wxCallOnMain
	from typing import Literal

	class MyMessageDialog(MessageDialog):

		@classmethod
		def confirm_YesNo(
			cls,
			message,
			caption=wx.MessageBoxCaptionStr,
			parent=None,
			*,
			okLabel=None,
			cancelLabel=None,
		) -> Literal[ReturnCode.OK, ReturnCode.CANCEL]:
			"""Display a confirmation dialog with Yes and No buttons.

			.. note:: This method is thread safe.

			:param message: The message to be displayed in the dialog.
			:param caption: The caption of the dialog window, defaults to wx.MessageBoxCaptionStr.
			:param parent: The parent window for the dialog, defaults to None.
			:return: ReturnCode.YES if Yes is pressed else , ReturnCode.NO.
			"""

			def impl():
				dlg = cls(parent, message, caption, buttons=DefaultButtonSet.YES_NO)
				icon = wx.ArtProvider.GetIconBundle(wx.ART_QUESTION, client=wx.ART_MESSAGE_BOX)
				dlg.SetIcons(icon)
				ret = dlg.ShowModal()

				if ret == ReturnCode.YES:
					return ret
				return ReturnCode.NO

			return wxCallOnMain(impl)

		@classmethod
		def warn(
			cls,
			message: str,
			caption: str = wx.MessageBoxCaptionStr,
			parent: wx.Window | None = None,
			*,
			okLabel: str | None = None,
		):
			"""Display a blocking dialog with an OK button.

			.. note:: This method is thread safe.

			:param message: The message to be displayed in the warning dialog.
			:param caption: The caption of the warning dialog, defaults to wx.MessageBoxCaptionStr.
			:param parent: The parent window of the warning dialog, defaults to None.
			:param okLabel: Override for the label of the OK button, defaults to None.
			"""

			def impl():
				dlg = cls(parent, message, caption, buttons=(DefaultButton.OK,), dialogType=DialogType.WARNING)
				if okLabel is not None:
					dlg.setOkLabel(okLabel)
				dlg.ShowModal()

			wxCallOnMain(impl)

		@classmethod
		def alert(
			cls,
			message: str,
			caption: str = wx.MessageBoxCaptionStr,
			parent: wx.Window | None = None,
			*,
			okLabel: str | None = None,
		):
			"""Display a blocking dialog with an OK button.

			.. note:: This method is thread safe.

			:param message: The message to be displayed in the alert dialog.
			:param caption: The caption of the alert dialog, defaults to wx.MessageBoxCaptionStr.
			:param parent: The parent window of the alert dialog, defaults to None.
			:param okLabel: Override for the label of the OK button, defaults to None.
			"""

			def impl():
				dlg = cls(parent, message, caption, buttons=(DefaultButton.OK,), dialogType=DialogType.ERROR)
				if okLabel is not None:
					dlg.setOkLabel(okLabel)
				dlg.ShowModal()

			wxCallOnMain(impl)

		@classmethod
		def inform(
			cls,
			message: str,
			caption: str = wx.MessageBoxCaptionStr,
			parent: wx.Window | None = None,
			*,
			okLabel: str | None = None,
		):
			"""Display a blocking dialog with an OK button.

			.. note:: This method is thread safe.

			:param message: The message to be displayed in the information dialog.
			:param caption: The caption of the information dialog, defaults to wx.MessageBoxCaptionStr.
			:param parent: The parent window of the information dialog, defaults to None.
			:param okLabel: Override for the label of the OK button, defaults to None.
			"""

			def impl():
				dlg = cls(parent, message, caption, buttons=(DefaultButton.OK,))
				icon = wx.ArtProvider.GetIconBundle(wx.ART_INFORMATION, client=wx.ART_MESSAGE_BOX)
				dlg.SetIcons(icon)
				if okLabel is not None:
					dlg.setOkLabel(okLabel)
				dlg.ShowModal()

			wxCallOnMain(impl)
