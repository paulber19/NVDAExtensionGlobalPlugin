# globalPlugins\NVDAExtensionGlobalPlugin\keyboardKeyRenaming\__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2022 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import ui
import speech
import wx
from gui import guiHelper, SettingsDialog
import core
import queueHandler
from ..settings import _addonConfigManager

from ..utils import speakLater, makeAddonWindowTitle, getHelpObj
from ..utils import contextHelpEx
addonHandler.initTranslation()


class KeyboardKeyRenamingDialog(
	contextHelpEx.ContextHelpMixinEx,
	SettingsDialog):
	# Translators: This is the label for the ModifyKeyLabels dialog.
	title = _("Keyboard Keys's renaming")
	taskTimer = None
	# help id in the user manual.
	helpObj = getHelpObj("hdr12")

	def __init__(self, parent):
		self.title = makeAddonWindowTitle(self.title)
		super(KeyboardKeyRenamingDialog, self).__init__(parent)

	def makeSettings(self, settingsSizer):
		# init
		self.modifiedKeyLabels = _addonConfigManager .getRedefinedKeyLabels()
		self.basicLocalizedKeyLabels = _addonConfigManager.getBasicLocalizedKeyLabels()
		self.localizedLabel2KeyName = dict((name, code) for code, name in self.basicLocalizedKeyLabels.items())
		self.localizedLabels = [x for x in self.localizedLabel2KeyName]
		self.localizedLabels.sort()
		# gui
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: The label for the list box
		# in KeyboardKeyRenaming Dialog to select a key label.
		keyLabelsListlabelText = _("NVDA defined key labels:")
		self.keyLabelsList = sHelper.addLabeledControl(
			keyLabelsListlabelText, wx.ListBox,
			id=wx.ID_ANY,
			name="NVDAKeyLabels",
			choices=self.localizedLabels)
		self.keyLabelsList.SetSelection(0)
		# Translators: The label for the modified Label Box .
		modifiedLabelText = _("Modified label:")
		self.modifiedLabelBox_id = wx.NewIdRef()
		self.modifiedLabelBox = sHelper.addLabeledControl(
			modifiedLabelText, wx.TextCtrl, id=self.modifiedLabelBox_id)
		keyName = self.localizedLabel2KeyName[self.localizedLabels[0]]
		if keyName in self.modifiedKeyLabels:
			self.modifiedLabelBox.SetValue(self.modifiedKeyLabels[keyName])
		else:
			self.modifiedLabelBox.Disable()
		# buttons
		bHelper = guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: the button to redefine the selected key label.
		editButton = bHelper.addButton(self, label=_("&Modify"))
		# Translators: the button to remove the label of replacement.
		self.removeButton = bHelper.addButton(self, label=_("&Remove"))
		# Translators: the button to remove all the labels of replacement.
		labelText = _("R&emove all")
		self.removeAllButton = bHelper.addButton(self, label=labelText)
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			guiHelper.ButtonHelper(wx.HORIZONTAL))
		# events
		self.keyLabelsList.Bind(wx.EVT_LISTBOX, self.onSelect)
		self.keyLabelsList.Bind(wx.EVT_SET_FOCUS, self.onFocus)
		editButton.Bind(wx.EVT_BUTTON, self.onModifyLabel)
		self.removeButton.Bind(wx.EVT_BUTTON, self.onRemoveLabel)
		self.removeAllButton.Bind(wx.EVT_BUTTON, self.onRemoveAllLabels)
		self.keyLabelsList.Bind(wx.EVT_KEY_DOWN, self.onKeydown)
		self.modifiedLabelBox.Bind(wx.EVT_KEY_DOWN, self.onKeydown)
		self.modifiedLabelBox.Bind(wx.EVT_SET_FOCUS, self.onFocus)

	def postInit(self):
		self.keyLabelsList.SetFocus()

	def stopTaskTimer(self):
		if self.taskTimer is not None:
			self.taskTimer.Stop()
			self.taskTimer = None

	def onSelect(self, evt):
		self.stopTaskTimer()
		speech.cancelSpeech()
		label = self.keyLabelsList.GetStringSelection()
		self.reportLabelRedifinition(label)
		evt.Skip()

	def onFocus(self, evt):
		id = evt.GetId()
		if id == self.modifiedLabelBox_id:
			self.modifiedLabelBox.SetSelection(0, 0)
			evt.Skip()
			return
		label = self.keyLabelsList.GetStringSelection()
		core.callLater(100, self.reportLabelRedifinition, label)

	def reportLabelRedifinition(self, label):

		def callback(text):
			self.taskTimer = None
			queueHandler.queueFunction(
				queueHandler.eventQueue, ui.message, text)
		keyName = self.localizedLabel2KeyName[label]
		if keyName in self.modifiedKeyLabels:
			self.modifiedLabelBox.SetValue(self.modifiedKeyLabels[keyName])
			self.modifiedLabelBox.Enable()
			# Translators: message to the user when key label is redefined.
			text = _("Redefined in %s") % self.modifiedKeyLabels[keyName]
			self.taskTimer = wx.CallLater(500, callback, text)

			self.removeButton.Enable()
			self.removeAllButton.Enable()
		else:
			self.modifiedLabelBox.SetValue("")
			self.modifiedLabelBox.Disable()
			self.removeButton.Disable()
			if len(self.modifiedKeyLabels):
				self.removeAllButton.Enable()
			else:
				self.removeAllButton.Disable()

	def onModifyLabel(self, evt):
		localizedLabel = self.keyLabelsList.GetStringSelection()
		keyName = self.localizedLabel2KeyName[localizedLabel]
		if keyName in self.modifiedKeyLabels:
			label = self.modifiedKeyLabels[keyName]
		else:
			label = ""
		with wx.TextEntryDialog(
			self,
			# Translators: Message to show on the dialog.
			_("Enter new label:"),
			# Translators: caption of text box.
			_("Key label redifinition"),
			label) as d:
			while True:
				if d.ShowModal() == wx.ID_OK:
					newLabel = (d.Value).strip()
					if newLabel == "":
						if keyName in self.modifiedKeyLabels:
							# Translators: message to user when redefined key label is removed.
							text = _("New name is removed")
							speakLater(300, text)
							del self.modifiedKeyLabels[keyName]
						else:
							# Translators: message to the user when no modification.
							text = _("No modification")
							speakLater(300, text)
					else:
						self.modifiedKeyLabels[keyName] = newLabel
					self.keyLabelsList.SetFocus()
					return
				else:
					break

	def onRemoveLabel(self, evt):
		localizedLabel = self.keyLabelsList.GetStringSelection()
		keyName = self.localizedLabel2KeyName[localizedLabel]
		if keyName in self.modifiedKeyLabels:
			# Translators: message to the user when redefined key label is removed.
			text = _("New name is removed")
			speakLater(300, text)
			del self.modifiedKeyLabels[keyName]
			self.keyLabelsList.SetFocus()

	def onRemoveAllLabels(self, evt):
		self.modifiedKeyLabels = {}
		# Translators: message to the user when all redefined key label are removed.
		text = _("All replacement labels have been removed")
		speakLater(300, text)
		self.keyLabelsList.SetFocus()

	def onKeydown(self, evt):
		keyCode = evt.GetKeyCode()
		id = evt.GetId()
		if id == self.modifiedLabelBox_id:
			if keyCode not in [wx.WXK_RIGHT, wx.WXK_LEFT, wx.WXK_UP, wx.WXK_DOWN, wx.WXK_HOME, wx.WXK_END]:
				return
		evt.Skip()

	def onOk(self, evt):
		_addonConfigManager .saveRedefinedKeyLabels(self.modifiedKeyLabels)
		_addonConfigManager.reDefineKeyboardKeyLabels()
		super(KeyboardKeyRenamingDialog, self).onOk(evt)
