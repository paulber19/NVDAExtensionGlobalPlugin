# globalPlugins\NVDAExtensionGlobalPlugin\minuteTimer\__init__.py
# A part of NVDAExtensionGlobalPlugin add-pon
# Copyright (C) 2016 -2022 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import os
import time
import ui
import gui
from gui import guiHelper
import wx
import nvwave
import threading
from ..settings import _addonConfigManager
from ..utils.NVDAStrings import NVDAString
from ..utils import isInteger, speakLater, isOpened, makeAddonWindowTitle, getHelpObj
from ..utils import contextHelpEx

addonHandler.initTranslation()

_curMinuteTimer = None


def minuteTimer():
	if _curMinuteTimer is None:
		MinuteTimerLaunchDialog.run()
	else:
		CurrentMinuteTimerDialog.run()


class MinuteTimer(object):
	def __init__(
		self,
		duration,
		announce,
		ringCount,
		delayBetweenRings,
		delayBeforeEndDuration=None):
		# duration in seconds
		self.duration = int(duration * 60)
		# vocal announce to be spoken at the end of duration
		self.announce = announce
		# number of rings
		self.ringCount = ringCount
		# delay between ring
		self.delayBetweenRings = delayBetweenRings
		# delay before end duration in secondes
		self.delayBeforeEndDuration = delayBeforeEndDuration
		# ring sound file
		path = addonHandler.getCodeAddon().path
		self.ringFile = os.path.join(path, "sounds", "ringin.wav")
		if self.delayBeforeEndDuration is None:
			self.speakAnnounceTimer = wx.CallLater(
				int(1000 * self.duration), self.speakAnnounce)
		else:
			self.speakAnnounceTimer = wx.CallLater(
				int(1000 * (self.duration - int(60 * self.delayBeforeEndDuration))),
				self.speakAnnounceBeforeEnd)
		self.ringTimer = None
		self.startTime = int(time.time())

	def speakAnnounceBeforeEnd(self):
		msg = _("End duration in %s minutes") % self.delayBeforeEndDuration\
			if self.delayBeforeEndDuration > 1 else _("End duration in one minute")
		ui.message(msg)
		self.speakAnnounceTimer = wx.CallLater(
			int(1000 * 60 * self.delayBeforeEndDuration), self.speakAnnounce)

	def speakAnnounce(self):
		global _curMinuteTimer
		_curMinuteTimer = None
		self.speakAnnounceTimer = None
		if CurrentMinuteTimerDialog._instance is not None:
			CurrentMinuteTimerDialog._instance .Destroy()
		th = Ring(self.ringCount, self.delayBetweenRings / 1000, self.ringFile)
		th.start()
		wx.CallAfter(
			gui.messageBox,
			self.announce,
			# Translators: the title of a message box dialog.
			_("End of minutetimer"),
			wx.OK)

	def getRemainingTime(self):
		curTime = int(time.time())
		elapsedTime = int(curTime - self.startTime)
		return self.duration - elapsedTime

	def stop(self):
		if self.ringTimer is not None:
			self.ringTimer.Stop()
			self.ringTimer = None
		if self.speakAnnounceTimer is not None:
			self.speakAnnounceTimer.Stop()
			self.speakAnnounceTimer = None


class MinuteTimerLaunchDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	_instance = None
	title = None
	# help in the user manual.
	helpObj = getHelpObj("hdr14")

	def __new__(cls, *args, **kwargs):
		if MinuteTimerLaunchDialog._instance is not None:
			return MinuteTimerLaunchDialog._instance
		return wx.Dialog.__new__(cls)

	def __init__(self, parent):
		if MinuteTimerLaunchDialog._instance is not None:
			return
		MinuteTimerLaunchDialog._instance = self
		# Translators: This is the label for the MinuteTimer dialog.
		dialogTitle = _("Launch of the Minute timer")
		title = MinuteTimerLaunchDialog.title = makeAddonWindowTitle(dialogTitle)
		super(MinuteTimerLaunchDialog, self).__init__(parent, -1, title)
		self.doGui()

	def doGui(self):
		(lastDuration, lastAnnounce, lastDelayBeforeEndDuration) = _addonConfigManager.getLastMinuteTimerDatas()
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# the minute timer value
		self.minuteTimerDurationEdit = sHelper.addLabeledControl(
			# Translators: This is a label for a setting
			# in MinuteTimer (an edit box to define the timer delay).
			_("Enter the minute timer &duration (in minutes):"),
			wx.TextCtrl)
		self.minuteTimerDurationEdit.Value = str(lastDuration)
		# Translators: This is a label for a setting in MinuteTimer
		# (an edit box to define the text to be spoken at then end of duration).
		announceLabel = _("Enter the &announce to be spoken at the end of duration:")
		self.announceEdit = sHelper.addLabeledControl(announceLabel, wx.TextCtrl)
		self.announceEdit.Value = lastAnnounce
		self.delayBeforeEndDurationList = [str(x) for x in range(11)]
		self.delayBeforeEndDurationLB = sHelper.addLabeledControl(
			# Translators: This is a label for a setting in MinuteTimer dialog.
			_("Delay to be alerted before ending (in minutes):"),
			wx.Choice,
			choices=self.delayBeforeEndDurationList)
		self.delayBeforeEndDurationLB .SetSelection(
			self.delayBeforeEndDurationList .index(str(lastDelayBeforeEndDuration)))
		# buttons
		bHelper = guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)
		# Translators: The label for a button
		# in Minute Timer Launch dialog to display ring options dialog.
		ringOptionsButton = bHelper.addButton(self, label=_("Ring's &Options"))
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		okButton = bHelper.addButton(self, wx.ID_OK)
		okButton .SetDefault()
		cancelButton = bHelper.addButton(self, wx.ID_CANCEL)

		mainSizer.Add(
			sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# events
		ringOptionsButton.Bind(wx.EVT_BUTTON, self.onRingOptionsButton)
		okButton.Bind(wx.EVT_BUTTON, self.onOk)
		cancelButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CANCEL)
		self.minuteTimerDurationEdit.SetFocus()

	def Destroy(self):
		MinuteTimerLaunchDialog._instance = None
		super(MinuteTimerLaunchDialog, self).Destroy()

	def onRingOptionsButton(self, evt):
		with RingOptionsDialog(self) as d:
			d.ShowModal()
		return
		try:
			with RingOptionsDialog(self) as d:
				d.ShowModal()
		except Exception:
			pass

	def validate(self):
		global _curMinuteTimer
		duration = self.minuteTimerDurationEdit.GetValue()
		if not isInteger(duration):
			# Translators: message to the user when a invalid duration as been entered.
			text = _("Duration is not valid")
			speakLater(100, text)
			wx.CallLater(300, self.minuteTimerDurationEdit.SetFocus)
			return False
		announce = self.announceEdit.GetValue()
		duration = int(duration)
		delayBeforeEndDuration = int(self.delayBeforeEndDurationLB.GetSelection())
		if delayBeforeEndDuration >= duration:
			# Translators: message to the user when a invalid
			# delay before duration ending.
			text = _("The Delay to be notified before duration ending must be smaller than duration")
			speakLater(100, text)
			wx.CallLater(300, self.delayBeforeEndDurationLB.SetFocus)
			return False
		(ringCount, delayBetweenRings) = _addonConfigManager.getMinuteTimerOptions()
		_curMinuteTimer = MinuteTimer(
			duration, announce, ringCount, delayBetweenRings, delayBeforeEndDuration)
		_addonConfigManager.saveLastMinuteTimerDatas(
			(duration, announce, delayBeforeEndDuration))
		# Translators: message to the user when minute timer starts.
		text = _("Minute timer started for %s minutes") % duration
		speakLater(100, text)
		return True

	def onOk(self, evt):
		if not self.validate():
			return
		self.Close()

	@classmethod
	def run(cls):
		if isOpened(cls):
			return
		gui.mainFrame.prePopup()
		d = MinuteTimerLaunchDialog(gui.mainFrame)
		d.CentreOnScreen()
		d.Show()
		gui.mainFrame.postPopup()


class RingOptionsDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	# Translators: this i the title of ring Options dialog.
	title = _("Ring options")
	# help in the user manual.
	helpObj = getHelpObj("hdr14")

	def __init__(self, parent):
		super(RingOptionsDialog, self).__init__(parent, title=self.title)
		self.doGui()
		self.CentreOnScreen()

	def doGui(self):
		# init
		(ringCount, delayBetweenRings) = _addonConfigManager.getMinuteTimerOptions()
		# gui
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# the number of rings
		self.ringCountBox = sHelper.addLabeledControl(
			# Translators: This is the label for the edit field
			# in the ring options dialog to define number of ring.
			_("&Number of rings:"),
			wx.Choice,
			choices=[str(x) for x in range(0, 10)])
		self.ringCountBox.SetStringSelection(str(ringCount))
		# the delay between rings
		self.delayBetweenRingsBox = sHelper.addLabeledControl(
			# Translators: This is the label for the edit field
			# in the ring options dialog to define duration between rings.
			_("&Delay between rings (in milliseconds):"),
			wx.Choice,
			choices=[str(x * 500) for x in range(1, 11)])
		self.delayBetweenRingsBox.SetStringSelection(str(delayBetweenRings))

		# buttons
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		okButton = bHelper.addButton(self, wx.ID_OK)
		okButton .SetDefault()
		bHelper.addButton(self, wx.ID_CANCEL)
		mainSizer.Add(
			sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# events
		self.Bind(wx.EVT_BUTTON, self.onOkButton, id=wx.ID_OK)

	def onOkButton(self, evt):
		ringCount = int(self.ringCountBox.GetStringSelection())
		delayBetweenRings = int(self.delayBetweenRingsBox.GetStringSelection())
		_addonConfigManager.saveMinuteTimerOptions((ringCount, delayBetweenRings))
		self.Close()
		evt.Skip()


class CurrentMinuteTimerDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	_instance = None
	title = None
	# help in the user manual.
	helpObj = getHelpObj("hdr14")

	def __new__(cls, *args, **kwargs):
		if CurrentMinuteTimerDialog._instance is not None:
			return CurrentMinuteTimerDialog._instance
		return wx.Dialog.__new__(cls)

	def __init__(self, parent):
		if CurrentMinuteTimerDialog._instance is not None:
			return
		CurrentMinuteTimerDialog._instance = self
		# Translators: this is the title of Current minute timer dialog.
		dialogTitle = _("Current minute timer")
		title = CurrentMinuteTimerDialog.title = makeAddonWindowTitle(dialogTitle)
		super(CurrentMinuteTimerDialog, self).__init__(parent, -1, title)

		self.doGui()
		self.CentreOnScreen()

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is a label for a edit box in Minute Timer Dialog
		# to show remaining duration.
		remainingDurationLabel = _("Remaining duration:")
		self.remainingDurationEdit = sHelper.addLabeledControl(
			remainingDurationLabel, wx.TextCtrl)
		self.remainingDurationEdit.Value = str(_curMinuteTimer.getRemainingTime())
		# the buttons
		bHelper = sHelper.addDialogDismissButtons(
			guiHelper.ButtonHelper(wx.HORIZONTAL))
		# Translators: The label for a button
		# in Minute Timer dialog to stop minute timer.
		stopButton = bHelper.addButton(self, label=_("&Stop"))
		closeButton = bHelper.addButton(
			self, id=wx.ID_CLOSE, label=NVDAString("&Close"))
		closeButton.SetDefault()
		mainSizer.Add(
			sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# events
		self.remainingDurationEdit .Bind(wx.EVT_SET_FOCUS, self.onFocus)

		stopButton.Bind(wx.EVT_BUTTON, self.onStopButton)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)
		# start monitoring
		self.monitorRemainingTime()

	def Destroy(self):
		CurrentMinuteTimerDialog._instance = None
		super(CurrentMinuteTimerDialog, self).Destroy()

	def onFocus(self, evt):
		self.remainingDurationEdit .SetSelection(0, 0)
		evt.Skip()

	def onStopButton(self, evt):
		global _curMinuteTimer
		if _curMinuteTimer is not None:
			_curMinuteTimer.stop()
			_curMinuteTimer = None
			# Translators: message to user minute timer stopped.
			speakLater(100, _("Minute timer is stopped"))
		self.Close()

	def monitorRemainingTime(self):
		if CurrentMinuteTimerDialog._instance is None:
			return
		remainingTime = 0 if _curMinuteTimer is None\
			else _curMinuteTimer.getRemainingTime()
		if remainingTime == 0:
			return
		minutes = int(remainingTime / 60)
		seconds = int(remainingTime % 60)
		delay = 5000
		if minutes == 0:
			# Translators: this is a message to the user.
			text = _("%s seconds") % remainingTime
		else:
			# Translators: this is a message to the user.
			text = _("{minutes} minutes {seconds}") .format(
				minutes=minutes, seconds=seconds)
		self.remainingDurationEdit.SetValue(text)
		if (minutes == 0) and int(seconds / 5) == 0:
			delay = 1000
		if self.remainingDurationEdit.HasFocus():
			speakLater(100, text)
		wx.CallLater(delay, self.monitorRemainingTime)

	@classmethod
	def run(cls):
		if isOpened(cls):
			return
		gui.mainFrame.prePopup()
		d = CurrentMinuteTimerDialog(gui.mainFrame)
		d.Show()
		gui.mainFrame.postPopup()


class Ring(threading.Thread):
	def __init__(self, ringCount=3, delayBetweenRings=2, ringWavFile=None):
		threading.Thread.__init__(self)
		self.ringCount = ringCount
		self.delayBetweenRings = delayBetweenRings
		self.ringWavFile = ringWavFile
		if self.ringWavFile is None:
			path = addonHandler.getCodeAddon().path
			self.ringWavFile = os.path.join(path, "sounds", "ringin.wav")
		self._stopevent = threading.Event()

	def run(self):
		while self.ringCount and not self._stopevent.isSet():
			self._stopevent.wait(self.delayBetweenRings)
			nvwave.playWaveFile(self.ringWavFile)
			self.ringCount -= 1
		self._stopevent.wait(self.delayBetweenRings)
		self.stop()

	def stop(self):
		self._stopevent.set()
