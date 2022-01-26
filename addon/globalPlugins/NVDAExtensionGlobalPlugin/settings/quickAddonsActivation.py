# globalPlugins\NVDAExtensionGlobalPlugin\settings\quickAddonsActivation.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2021-2022 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


import addonHandler
from logHandler import log
import globalVars
import wx
import ui
import core
import gui
from gui import nvdaControls
from gui import guiHelper, mainFrame
from ..utils import isOpened, makeAddonWindowTitle, getHelpObj
from ..utils import contextHelpEx
from ..utils.NVDAStrings import NVDAString
from locale import strxfrm
from addonHandler import addonVersionCheck
import addonAPIVersion

addonHandler.initTranslation()


class QuickAddonsActivationDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	_instance = None
	# help in the user manual.
	helpObj = getHelpObj("hdr35")

	def __new__(cls, *args, **kwargs):
		if QuickAddonsActivationDialog._instance is None:
			return wx.Dialog.__new__(cls)
		return QuickAddonsActivationDialog._instance

	def __init__(self, parent):
		if QuickAddonsActivationDialog._instance is not None:
			return
		QuickAddonsActivationDialog._instance = self
		# Translators: this is the title of Temporary Audio output Device manager dialog
		dialogTitle = _("Quick addons activation")
		title = QuickAddonsActivationDialog.title = makeAddonWindowTitle(dialogTitle)
		super(QuickAddonsActivationDialog, self).__init__(parent, wx.ID_ANY, title)
		self.doGui()

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label for a listbox
		# on Addons activation dialog.
		labelText = _("Check to activate:")
		self.addonsListBox = sHelper.addLabeledControl(
			labelText,
			nvdaControls.CustomCheckListBox,
			choices=[]
		)

		# the buttons
		bHelper = sHelper.addDialogDismissButtons(
			guiHelper.ButtonHelper(wx.HORIZONTAL))
		checkAllButton = bHelper.addButton(
			self,
			# Translators: This is a label of a button appearing
			# on Addons activation dialog
			label=_("&Check all"))
		uncheckAllButton = bHelper.addButton(
			self,
			# Translators: This is a label of a button appearing
			# on Addons activation dialog.
			label=_("&Uncheck all"))
		saveAndRestartNVDAButton = bHelper.addButton(
			self,
			# Translators: This is a label of a button appearing
			# on Addons activation dialog.
			label=_("&Save and restart NVDA"))
		saveAndRestartNVDAButton.SetDefault()
		cancelButton = bHelper.addButton(
			self,
			id=wx.ID_CANCEL,
		)
		mainSizer.Add(sHelper.sizer, border=10, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# the events
		checkAllButton.Bind(wx.EVT_BUTTON, self.onCheckAll)
		uncheckAllButton.Bind(wx.EVT_BUTTON, self.onUncheckAll)
		saveAndRestartNVDAButton.Bind(wx.EVT_BUTTON, self.onSaveAndRestartNVDA)
		cancelButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CANCEL)
		self.addonsListBox.SetFocus()
		self.refreshAddonsList()

	def refreshAddonsList(self, activeIndex=0):
		self.addonsList = []
		self.curActivatedAddons = []
		self.curAddons = []
		for addon in sorted(addonHandler.getAvailableAddons(), key=lambda a: strxfrm(a.manifest['summary'])):
			addonIncompatible = (
				not addonVersionCheck.isAddonCompatible(
					addon,
					currentAPIVersion=addonAPIVersion.CURRENT,
					backwardsCompatToVersion=addonAPIVersion.BACK_COMPAT_TO
				)
			)
			if addonIncompatible or addon.isBlocked:
				continue
			if (
				addon.isRunning and not addon.isPendingDisable
				or addon.isDisabled and (
					not addon.isPendingDisable or not globalVars.appArgs.disableAddons)):
				self.curAddons.append(addon)
		for addon in self.curAddons:
			state = addon.isRunning
			if state:
				index = self.curAddons.index(addon)
				self.curActivatedAddons.append(index)
		self.addonsListBox.AppendItems([x.manifest["summary"] for x in self.curAddons])
		self.addonsListBox.SetCheckedItems(self.curActivatedAddons)
		self.addonsListBox.SetSelection(0)

	def Destroy(self):
		QuickAddonsActivationDialog._instance = None
		super(QuickAddonsActivationDialog, self).Destroy()

	def onCheckAll(self, evt):
		for addon in self.curAddons:
			index = self.curAddons.index(addon)
			self.addonsListBox.Check(index, True)
		# Translators: message to user to report that all add-ons have been checked.
		wx.CallLater(40, ui.message, _("All add-ons are checked"))

	def onUncheckAll(self, evt):
		for addon in self.curAddons:
			index = self.curAddons.index(addon)
			self.addonsListBox.Check(index, False)
		# Translators: message to user to report that all add-ons have been unchecked.
		wx.CallLater(40, ui.message, _("All add-ons unchecked"))

	def onSaveAndRestartNVDA(self, evt):
		checkedItems = list(self.addonsListBox.GetCheckedItems())
		if checkedItems == self.curActivatedAddons:
			# no change
			# Translators: Title for message asking if the user wishes to restart NVDA even if there were no changes
			restartTitle = NVDAString("Restart NVDA")
			# Translators: A message asking the user if they wish to restart NVDA
			# even if there were no changes
			restartMessage = _("There is no change. Do you want to restart NVDA anyway?")
			result = gui.messageBox(
				message=restartMessage,
				caption=restartTitle,
				style=wx.YES | wx.NO | wx.ICON_WARNING
			)
			if wx.YES == result:
				core.restart()
			return
		# there is  change, so set state of all cur addons
		for index in range(0, len(self.curAddons)):
			oldActivation = index in self.curActivatedAddons
			newActivation = index in checkedItems
			if newActivation == oldActivation:
				continue
			addon = self.curAddons[index]
			shouldEnable = index in checkedItems
			try:
				addon.enable(shouldEnable)
			except addonHandler.AddonError:
				log.error("Couldn't change state for %s add-on" % addon.name, exc_info=True)
				continue
		core.restart()

	def onClose(self, evt):
		self.Destroy()

	@classmethod
	def run(cls):
		if isOpened(cls):
			return
		mainFrame.prePopup()
		d = cls(mainFrame)
		d.CentreOnScreen()
		d.Show()
		mainFrame.postPopup()
