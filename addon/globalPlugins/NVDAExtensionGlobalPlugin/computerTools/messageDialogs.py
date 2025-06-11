# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\messageDialogs.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2025 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import wx
from gui.guiHelper import (
	BoxSizerHelper,
	BORDER_FOR_DIALOGS,
	ButtonHelper,
	SPACE_BETWEEN_VERTICAL_DIALOG_ITEMS,
)
import windowUtils
from ..utils import makeAddonWindowTitle, getHelpObj
from ..gui import contextHelpEx

addonHandler.initTranslation()


class SplitAudioWarningDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog,  # wxPython does not seem to call base class initializer, put last in MRO
):
	"""A dialog warning the user about the risks of  incompatibility with NVDA split audio."""
	# help in the user manual.
	helpObj = getHelpObj("hdr34")

	def __init__(self, parent: wx.Window):
		# Translators: The warning of a dialog
		dialogTitle = makeAddonWindowTitle(_("Warning"))
		super().__init__(parent, title=dialogTitle)
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: Warning that is displayed at add-on start when nvda split audio is not in desactivated state
		_warningText = _(
			"The NVDA Split audio mode being in disabled mode,"
			" it may be in contradiction with the Split audio functionality of the add-on.")
		sText = sHelper.addItem(wx.StaticText(self, label=_warningText))
		# the wx.Window must be constructed before we can get the handle.
		self.scaleFactor = windowUtils.getWindowScalingFactor(self.GetHandle())
		sText.Wrap(
			# 600 was fairly arbitrarily chosen by a visual user to look acceptable on their machine.
			self.scaleFactor * 600,
		)

		sHelper.sizer.AddSpacer(SPACE_BETWEEN_VERTICAL_DIALOG_ITEMS)
		self.dontShowAgainCheckbox = sHelper.addItem(
			wx.CheckBox(
				self,
				label=_(
					# Translators: The label of a checkbox in the split audio warning dialog
					"&Don't show this message again",
				),
			),
		)

		bHelper = sHelper.addDialogDismissButtons(ButtonHelper(wx.HORIZONTAL))
		# Translators: The label of a button in a dialog
		okButton = bHelper.addButton(self, wx.ID_OK, label=pgettext("addonStore", "&OK"))
		okButton.Bind(wx.EVT_BUTTON, self.onOkButton)

		mainSizer.Add(sHelper.sizer, border=BORDER_FOR_DIALOGS, flag=wx.ALL)
		self.Sizer = mainSizer
		mainSizer.Fit(self)
		self.CentreOnScreen()

	def onOkButton(self, evt: wx.CommandEvent):
		# addonDataManager.storeSettings.showWarning = not self.dontShowAgainCheckbox.GetValue()
		self.EndModal(wx.ID_OK)
