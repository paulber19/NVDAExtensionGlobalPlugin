# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\audioDevice.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2021-2024 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


import addonHandler
from logHandler import log
import api
import tones
import synthDriverHandler
import config
import speech
import time
import wx
import nvwave
from gui import nvdaControls
from synthDriverHandler import getSynth
from gui import guiHelper, mainFrame
from ..utils import isOpened, makeAddonWindowTitle, getHelpObj
from ..utils import contextHelpEx
from ..utils.NVDAStrings import NVDAString

addonHandler.initTranslation()


# hold the current temporary audio device, None if there is no temporary audio device
_temporaryOutputDevice = None
# save NVDA OneCore SynthDriver MaybeInitPlayer
_NVDAOneCoreSynthDriverMaybeInitPlayer = None


def getTemporaryOutputDevice():
	return _temporaryOutputDevice


def getDeviceNames():
	deviceNames = nvwave.getOutputDeviceNames()
	# #11349: On Windows 10 20H1 and 20H2, Microsoft Sound Mapper returns an empty string.
	if deviceNames[0] in ("", "Microsoft Sound Mapper"):
		# Translators: name for default (Microsoft Sound Mapper) audio output device.
		deviceNames[0] = NVDAString("Microsoft Sound Mapper")
	return deviceNames


def updateSynthetizerAndTones(synth):
	log.debug("updateSynthetizerAndTones: temporaryOutputDevice= %s" % _temporaryOutputDevice)
	import speech
	speech.cancelSpeech()
	res = synthDriverHandler .setSynth(synth.name)
	if not res:
		log.error("Could not load the %s synthesizer." % synth)
		return False
	# Reinitialize the tones module to update the audio device
	tones.terminate()
	tones.initialize()
	return True


def setTemporaryAudioOutputDevice(outputDevice):
	global _temporaryOutputDevice
	synth = getSynth()
	currentTemporaryOutputDevice = _temporaryOutputDevice
	prevOutputDevice = config.conf["speech"]["outputDevice"]
	if _temporaryOutputDevice:
		prevOutputDevice = _temporaryOutputDevice
	temporary = bool(_temporaryOutputDevice)
	_temporaryOutputDevice = outputDevice
	ret = updateSynthetizerAndTones(synth)
	if not ret:
		_temporaryOutputDevice = currentTemporaryOutputDevice
		return

	def reportFocus():
		speech.cancelSpeech()
		obj = api.getFocusObject()
		speech.speakObject(obj)

	def confirm(synth, prevOutputDevice, temporary):
		global _temporaryOutputDevice, confirmDialog
		from ..settings import _addonConfigManager
		timeToLive = _addonConfigManager.getConfirmAudioDeviceChangeTimeOut()
		from ..utils import PutWindowOnForeground
		dialog = ConfirmOutputDevice(None, timeToLive)
		with dialog as d:
			PutWindowOnForeground(d.GetHandle(), 10, 0.5)
			res = d.ShowModal()
			d.Destroy()
		if res != wx.ID_OK:
			# return to previous output device
			if temporary:
				_temporaryOutputDevice = prevOutputDevice
			else:
				_temporaryOutputDevice = None
			updateSynthetizerAndTones(synth)
			wx.CallLater(100, reportFocus)
		else:
			log.debug("Temporary output device set to: %s" % _temporaryOutputDevice)

	from ..settings import toggleConfirmAudioDeviceChangeAdvancedOption
	if toggleConfirmAudioDeviceChangeAdvancedOption(False):
		wx.CallLater(10, confirm, synth, prevOutputDevice, temporary)
		return
	reportFocus()
	log.debug("Temporary output device set to: %s" % _temporaryOutputDevice)


def cancelTemporaryAudioOutputDevice():
	global _temporaryOutputDevice
	if not _temporaryOutputDevice:
		return
	# back to speech configuration output device
	outputDevice = config.conf["speech"]["outputDevice"]
	log.debug("Cancel temporary output device: current output device= %s" % outputDevice)
	synth = getSynth()
	_temporaryOutputDevice = None
	updateSynthetizerAndTones(synth)
	obj = api.getFocusObject()
	speech.speakObject(obj)


def checkOutputDeviceChange():
	from ..settings import isInstall
	from ..settings.addonConfig import FCT_TemporaryAudioDevice
	if not isInstall(FCT_TemporaryAudioDevice):
		return
	from synthDriverHandler import _audioOutputDevice
	if _temporaryOutputDevice and _temporaryOutputDevice != _audioOutputDevice:
		# log.debug("back to temporary output device: %s" %_temporaryOutputDevice)
		updateSynthetizerAndTones(getSynth())


class TemporaryAudioDeviceManagerDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	_instance = None
	# help in the user manual.
	helpObj = getHelpObj("hdr33")
	shouldSuspendConfigProfileTriggers = True
	selectDelay = None

	def __new__(cls, *args, **kwargs):
		if TemporaryAudioDeviceManagerDialog._instance is None:
			return wx.Dialog.__new__(cls)
		return TemporaryAudioDeviceManagerDialog._instance

	def __init__(self, parent):
		if TemporaryAudioDeviceManagerDialog._instance is not None:
			return
		TemporaryAudioDeviceManagerDialog._instance = self
		# Translators: this is the title of Temporary Audio output Device manager dialog
		dialogTitle = _("Temporary Audio device manager")
		title = TemporaryAudioDeviceManagerDialog.title = makeAddonWindowTitle(dialogTitle)
		super(TemporaryAudioDeviceManagerDialog, self).__init__(parent, wx.ID_ANY, title)
		self.doGui()

	def doGui(self):
		global _temporaryOutputDevice
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		self.deviceNames = getDeviceNames()
		from synthDriverHandler import _audioOutputDevice
		self.curOutputDevice = _audioOutputDevice
		if _temporaryOutputDevice and _temporaryOutputDevice != _audioOutputDevice:
			# audio output device has been changed by setsynth, so reset temporary audio output device
			_temporaryOutputDevice = None
			updateSynthetizerAndTones(getSynth())
		# Translators: temporary output device text
		# on Temporary audio output device manager dialog.
		labelText = _(
			"Current temporary audio device: %s") % (_temporaryOutputDevice if _temporaryOutputDevice else _("None"))
		self.currentTemporaryOutputDeviceTextCtrl = sHelper.addItem(wx.StaticText(
			self,
			label=labelText)
		)
		# Translators: This is the label for a listbox
		# on Temporary audio device manager dialog.
		labelText = _("Select a &device:")
		deviceNames = getDeviceNames()
		self.audioDevicesListBox = sHelper.addLabeledControl(
			labelText,
			nvdaControls.CustomCheckListBox,
			choices=deviceNames)
		self.audioDevicesListBox.SetStringSelection(self.curOutputDevice)
		from ..settings import _addonConfigManager
		devicesForCycle = _addonConfigManager.getAudioDevicesForCycle()
		for device in deviceNames:
			index = deviceNames.index(device)
			if device in devicesForCycle:
				self.audioDevicesListBox.Check(index)
		# the buttons
		bHelper = sHelper.addDialogDismissButtons(
			guiHelper.ButtonHelper(wx.HORIZONTAL))
		self.setButton = bHelper.addButton(
			self,
			# Translators: This is a label of a button appearing
			# on Temporary audio device manager dialog.
			label=_("&Set as temporary audio device"))
		self.setButton.SetDefault()
		quitTemporaryAudioDeviceButton = bHelper.addButton(
			self,
			# Translators: This is a label of a button appearing
			# on Temporary audio device manager dialog.
			label=_("&leave up the temporary audio device"))
		closeButton = bHelper.addButton(
			self,
			id=wx.ID_CLOSE,
			label=NVDAString("&Close"))
		mainSizer.Add(sHelper.sizer, border=10, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# the events
		self.audioDevicesListBox.Bind(wx.EVT_LISTBOX, self.onSelectDevice)
		quitTemporaryAudioDeviceButton.Bind(wx.EVT_BUTTON, self.onQuitTemporaryAudioDevice)
		closeButton.Bind(wx.EVT_BUTTON, self.onClose)
		self.SetEscapeId(wx.ID_CLOSE)
		self.audioDevicesListBox.SetFocus()
		if not _temporaryOutputDevice:
			quitTemporaryAudioDeviceButton.Disable()
			self.setButton.Bind(wx.EVT_BUTTON, self.onSetButton)
		elif _temporaryOutputDevice == self.curOutputDevice:
			self.setButton.Disable()

	def Destroy(self):
		TemporaryAudioDeviceManagerDialog._instance = None
		super(TemporaryAudioDeviceManagerDialog, self).Destroy()

	def onSelectDevice(self, evt):
		if self.selectDelay:
			self.selectDelay.Stop()
			self.selectDelay = None
		deviceName = self.audioDevicesListBox.GetStringSelection()
		if deviceName == _temporaryOutputDevice:
			# disable set button
			self.setButton.Disable()
			self.setButton.Unbind(wx.EVT_BUTTON)
		else:
			self.setButton.Enable()
			self.setButton.Bind(wx.EVT_BUTTON, self.onSetButton)
		# we have to wait for the device name to be said by NVDA before changing the device
		# but for bluetooth debice, we must play noise before beep
		from .bluetoothAudio import playWhiteNoise
		from threading import Thread
		th = Thread(target=playWhiteNoise, args=(deviceName,))
		th.start()
		from .beep import playTonesOnDevice
		self.selectDelay = wx.CallLater(
			4000,
			playTonesOnDevice, deviceName)

	def onSetButton(self, evt):
		if self.selectDelay is not None:
			self.selectDelay .Stop()
			self.selectDelay = None
		outputDevice = self.audioDevicesListBox.GetStringSelection()
		setTemporaryAudioOutputDevice(outputDevice)
		self.Close()

	def onQuitTemporaryAudioDevice(self, evt):
		wx.CallLater(200, cancelTemporaryAudioOutputDevice)
		self.Destroy()

	def onClose(self, evt):
		# save checked device list
		checkedDevices = self.audioDevicesListBox.GetCheckedStrings()
		devicesForLoop = {}
		for device in getDeviceNames():
			isChecked = device in checkedDevices
			devicesForLoop[device] = isChecked
		from ..settings import _addonConfigManager
		_addonConfigManager.saveAudioDevicesForCycle(devicesForLoop)
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


class ConfirmOutputDevice(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	helpObj = getHelpObj("hdr33")

	def __init__(self, parent, timeToLive=10):
		# Translators: this is the title of ConfirmOutputDevice dialog
		dialogTitle = _("Confirm")
		title = ConfirmOutputDevice.title = makeAddonWindowTitle(dialogTitle)
		super(ConfirmOutputDevice, self).__init__(parent, wx.ID_ANY, title)
		self.timeToLive = timeToLive
		# Translators: message to user to confirm the use of audio device
		self.staticTextLabel = _(
			"You have %s seconds to accept the use of this audio device for all configuration profiles "
			"regardless of the choice made in their voice settings")
		self.doGui()
		self.CentreOnScreen()
		self.timer = wx.Timer(self)
		self.timer.Start(1000)  # Generate a timer event every second
		self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		self.messageTextCtrl = sHelper.addItem(wx.StaticText(
			self,
			label=self.staticTextLabel % self.timeToLive)
		)
		bHelper = sHelper.addDialogDismissButtons(
			guiHelper.ButtonHelper(wx.HORIZONTAL))
		okButton = bHelper.addButton(self, wx.ID_OK, label=_("&Accept"))
		okButton .SetDefault()
		bHelper.addButton(self, wx.ID_CANCEL)
		mainSizer.Add(sHelper.sizer, border=10, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)

	def onTimer(self, evt):
		self.timeToLive -= 1
		self.messageTextCtrl.SetLabel(self.staticTextLabel % self.timeToLive)
		from tones import beep
		beep(100, 100)
		time.sleep(0.05)
		if self.timeToLive == 0:
			self.timer.Stop()
			self.Close()

	def Destroy(self):

		self.timer.Stop()
		wx.EvtHandler.Unbind(self.timer, wx.EVT_TIMER)
		super(ConfirmOutputDevice, self).Destroy()


def initialize():
	from . import temporaryOutputDevicePatches
	temporaryOutputDevicePatches.patche()


def terminate():
	from . import temporaryOutputDevicePatches
	temporaryOutputDevicePatches.patche(install=False)
