# globalPlugins\shared\npp_message.py
# a part of notepadPluPlusAccessEnhancement add-on
# Copyright 2025 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import gui
import gui.message
import wx
from gui.message import (
	MessageDialog, ReturnCode,
	DefaultButton, DefaultButtonSet, DialogType
)
from gui.guiHelper import wxCallOnMain
from typing import Literal


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
