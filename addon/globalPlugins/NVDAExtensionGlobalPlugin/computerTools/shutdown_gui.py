# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\shutdown_gui.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2019 - 2021 paulber19
# This file is covered by the GNU General Public License.

import addonHandler
import wx
import gui
from ..utils import isOpened, makeAddonWindowTitle, getHelpObj
from gui import nvdaControls
from . import shutdown_util as shutdown
import config
import ui
import speech

from ..utils import contextHelpEx
addonHandler.initTranslation()


class ComputerShutdownDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	_delayBeforeShutdownOrRestartLimits = (0, 600)
	_instance = None
	title = None
	# help id in the user manual.
	helpObj = getHelpObj("hdr19")

	def __new__(cls, *args, **kwargs):
		if ComputerShutdownDialog._instance is not None:
			return ComputerShutdownDialog._instance
		return wx.Dialog.__new__(cls)

	def __init__(self, parent):
		if ComputerShutdownDialog._instance is not None:
			return
		ComputerShutdownDialog._instance = self
		# Translators: This is the title of Computer shutdown dialog window.
		dialogTitle = _("Computer shutdown")
		title = ComputerShutdownDialog.title = makeAddonWindowTitle(dialogTitle)
		super(ComputerShutdownDialog, self).__init__(parent, -1, title)
		self.doGui()

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: This is a label of a button appearing
		# on Computer shutdown dialog.
		hibernateButton = bHelper.addButton(self, label=_("&Hibernate"))
		# Translators: This is a label of a button appearing
		# on Computer shutdowndialog.
		shutdownButton = bHelper.addButton(self, label=_("&Shutdown"))
		# Translators: This is a label of a button appearing
		# on Computer shutdown dialog.
		rebootButton = bHelper.addButton(self, label=_("&Reboot"))
		sHelper1 = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label for a checkbox
		# on the Computer shutdowndialog.
		labelText = _("F&orce running programs to close without warning")
		self.forceOptionBox = sHelper1.addItem(wx.CheckBox(self, label=labelText))
		from ..settings import _addonConfigManager
		self.forceOptionBox.SetValue(_addonConfigManager.getForceCloseOption())
		# Translators: This is a label for a edit box in Computer shutdown dialog.
		(min, max) = self._delayBeforeShutdownOrRestartLimits
		labelText = _("&Delay before shutdown or reboot between {min} and {max} seconds").format(min=min, max=max)
		self.delayBeforeShutdownOrRestartBox = sHelper1.addLabeledControl(
			labelText, nvdaControls.SelectOnFocusSpinCtrl,
			min=int(0),
			max=int(600),
			initial=_addonConfigManager.getdelayBeforeShutdownOrRestart())
		sHelper.addItem(sHelper1)
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		cancelButton = bHelper.addButton(self, id=wx.ID_CANCEL)
		mainSizer.Add(
			sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# Events
		shutdownButton.Bind(wx.EVT_BUTTON, self.onShutdownButton)
		rebootButton.Bind(wx.EVT_BUTTON, self.onRebootButton)
		hibernateButton.Bind(wx.EVT_BUTTON, self.onhibernateButton)
		cancelButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())

	def Destroy(self):
		ComputerShutdownDialog._instance = None
		super(ComputerShutdownDialog, self).Destroy()

	def saveSettings(self):
		forceClose = self.forceOptionBox.GetValue()
		timeout = self.delayBeforeShutdownOrRestartBox.GetValue()
		from ..settings import _addonConfigManager
		_addonConfigManager.setForceCloseOption(forceClose)
		_addonConfigManager.setDelayBeforeShutdownOrRestart(timeout)

	def waitBeforeProcess(self, action, timeout):
		with ShutdownProcessingDialog(self, action, timeout) as dlg:
			res = dlg.ShowModal()
			dlg.Destroy()
		return res

	def onShutdownButton(self, event):
		forceClose = self.forceOptionBox.GetValue()
		timeout = self.delayBeforeShutdownOrRestartBox.GetValue()
		if not self.waitBeforeProcess("shutdown", timeout):
			self.Destroy()
			return
		self.saveSettings()
		shutdown.shutdown(0, forceClose)
		self.Close()

	def onRebootButton(self, event):
		forceClose = self.forceOptionBox.GetValue()
		timeout = self.delayBeforeShutdownOrRestartBox.GetValue()
		if not self.waitBeforeProcess("reboot", timeout):
			self.Destroy()
			return
		self.saveSettings()
		shutdown.reboot(0, forceClose)
		self.Close()

	def onhibernateButton(self, evt):
		timeout = self.delayBeforeShutdownOrRestartBox.GetValue()
		if not self.waitBeforeProcess("hibernate", timeout):
			self.Destroy()
			return
		self.saveSettings()
		self.Close()
		shutdown.suspend(hibernate=True)

	@classmethod
	def run(cls):
		if isOpened(cls):
			return
		gui.mainFrame.prePopup()
		d = cls(gui.mainFrame)
		d.CentreOnScreen()
		d.Show()
		gui.mainFrame.postPopup()


class ShutdownProcessingDialog(wx.Dialog):
	_remainingDuration = 0
	_timer = None

	def __init__(self, parent, action, duration):
		dialogTitles = {
			"shutdown": _("Computer Shutdown"),
			"reboot": _("Computer reboot"),
			"hibernate": _("Computer hibernation"),
		}
		self.action = action
		self.duration = duration
		dialogTitle = dialogTitles[action]
		title = ShutdownProcessingDialog.title = makeAddonWindowTitle(dialogTitle)
		super(ShutdownProcessingDialog, self).__init__(parent, -1, title)
		self.doGui()
		self.monitorRemainingTime(duration)
		self.CentreOnScreen()

	def doGui(self):
		remainingDurationLabels = {
			# Translators: This is a label for a edit box in Shutdown processing Dialog
			# to show remaining duration for shutdown action.
			"shutdown": _("Number of seconds to wait before shutdown:"),
			# Translators: This is a label for a edit box in Shutdown processing Dialog
			# to show remaining duration for reboot action.
			"reboot": _("Number of seconds to wait before reboot:"),
			# Translators: This is a label for a edit box in Shutdown processing Dialog
			# to show remaining duration for hibernate action.
			"hibernate": _("Number of seconds to wait before hibernation:")
		}
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		remainingDurationLabel = remainingDurationLabels[self.action]
		self.remainingDurationEdit = sHelper.addLabeledControl(
			remainingDurationLabel, wx.TextCtrl, style=wx.TE_READONLY)
		self.remainingDurationEdit.Value = str(self._remainingDuration)
		# the buttons
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		# Translators: This is a label of a button appearing
		# on ShutdownProcessingDialog.
		remainingTimeReportButton = bHelper.addButton(self, label=_("&Report remaining time"))
		cancelButton = bHelper.addButton(self, id=wx.ID_CANCEL)
		cancelButton.SetDefault()
		cancelButton.SetFocus()
		mainSizer.Add(
			sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# events
		remainingTimeReportButton.Bind(wx.EVT_BUTTON, self.onRemainingTimeReportButton)
		cancelButton.Bind(wx.EVT_BUTTON, self.onCancelButton)
		self.Bind(wx.EVT_ACTIVATE, self.onActivate)
		self.isActive = True

	def onActivate(self, evt):
		self.isActive = evt.GetActive()

	def onFocus(self, evt):
		self.remainingDurationEdit .SetSelection(0, 0)
		evt.Skip()

	def onRemainingTimeReportButton(self, evt):
		remainingTime = self.remainingDurationEdit.GetValue()
		wx.CallLater(1, ui.message, _("Remaining time: %s seconds") % remainingTime)

	def onCancelButton(self, evt):
		if self._timer is not None:
			self._timer.Stop()
			self._timer = None
		self.Destroy()

	def monitorRemainingTime(self, duration=None):
		if self._timer is not None:
			self._timer.Stop()
		if duration is not None:
			# init remaining time textCtrl
			self.remainingDurationEdit.SetValue(str(duration))
			# and start monitoring
			self._timer = wx.CallLater(1000, self.monitorRemainingTime)
			return
		duration = int(self.remainingDurationEdit.GetValue())
		if duration == 0:
			self.EndModal(True)
			self.Destroy()
			return
		self.remainingDurationEdit.SetValue(str(duration - 1))
		percentage = 100 - int(100 * float(duration) / float(self.duration))
		pbConf = config.conf["presentation"]["progressBarUpdates"]
		if pbConf["progressBarOutputMode"] == "off":
			self._timer = wx.CallLater(1000, self.monitorRemainingTime)
			return
		if self.isActive or config.conf["presentation"]["progressBarUpdates"]["reportBackgroundProgressBars"]:
			if pbConf["progressBarOutputMode"] in ("beep", "both"):
				import tones
				tones.beep(110 * 2**(percentage / 25.0), 40)
			if pbConf["progressBarOutputMode"] in ("speak", "both"):
				wx.CallAfter(speech.speakMessage, str(duration))
		self._timer = wx.CallLater(1000, self.monitorRemainingTime)
