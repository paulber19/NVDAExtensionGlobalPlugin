# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\audioDevice.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2021 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


import addonHandler
from logHandler import log
import api
import config
import speech
import time
import wx
import nvwave
from gui import nvdaControls
from synthDriverHandler import getSynth, setSynth
from gui import guiHelper, mainFrame
import synthDrivers.oneCore
from ..utils import isOpened, makeAddonWindowTitle, getHelpObj
from ..utils import contextHelpEx
from ..utils.NVDAStrings import NVDAString
from .waves import getModifiedNVDAWaveFile

addonHandler.initTranslation()


# hold the current temporary audio device, None if there is no temporary audio device
_temporaryOutputDevice = None


def _maybeInitPlayerEx(self, wav):
	"""
	patch for OneCore synthetizer
	this method use config.conf["speech"]["outputDevice"] to get the output device directly
	so if we change config.conf["speech"]["outputDevice"] after synthetizer initialization,
	it takes it as output device.
	but we don't that.
	we want change the output device of a synthetizer with no configuration change, like that:
	oldOutputDevice= config.conf["speech"]["outputDevice"]
	config.conf["speech"]["outputDevice"] = newOutputDevice
	setSynth(getSynth().name)
	config.conf["speech"]["outputDevice"] = oldOutputDevice
	We use _audioOutputDevice variable set by setSynth method
	"""

	from synthDriverHandler import _audioOutputDevice
	"""Initialize audio playback based on the wave header provided by the synthesizer.
	If the sampling rate has not changed, the existing player is used.
	Otherwise, a new one is created with the appropriate parameters.
	"""
	samplesPerSec = wav.getframerate()
	if self._player and self._player.samplesPerSec == samplesPerSec:
		return
	if self._player:
		# Finalise any pending audio.
		self._player.idle()
	bytesPerSample = wav.getsampwidth()
	self._bytesPerSec = samplesPerSec * bytesPerSample
	self._player = nvwave.WavePlayer(
		channels=wav.getnchannels(),
		samplesPerSec=samplesPerSec,
		bitsPerSample=bytesPerSample * 8,
		# my modification
		# outputDevice=config.conf["speech"]["outputDevice"]
		outputDevice=_audioOutputDevice
	)


def getDeviceNames():
	deviceNames = nvwave.getOutputDeviceNames()
	# #11349: On Windows 10 20H1 and 20H2, Microsoft Sound Mapper returns an empty string.
	if deviceNames[0] in ("", "Microsoft Sound Mapper"):
		# Translators: name for default (Microsoft Sound Mapper) audio output device.
		deviceNames[0] = NVDAString("Microsoft Sound Mapper")
	return deviceNames


def cancelTemporaryAudioOutputDevice():
	global _temporaryOutputDevice
	if not _temporaryOutputDevice:
		return
	# back to speech configuration output device
	outputDevice = config.conf["speech"]["outputDevice"]
	synth = getSynth()
	setOutputDevice(synth, outputDevice)
	_temporaryOutputDevice = None
	obj = api.getFocusObject()
	speech.speakObject(obj)


def setOutputDevice(synth, outputDevice):
	import speech
	speech.cancelSpeech()
	prevOutputDevice = config.conf["speech"]["outputDevice"]
	config.conf["speech"]["outputDevice"] = outputDevice
	# Reinitialize the tones module to update the audio device
	import tones
	tones.terminate()
	if not setSynth(synth.name):
		log.error("Could not load the %s synthesizer." % synth)
		ret = False
	else:
		ret = True
	tones.initialize()
	config.conf["speech"]["outputDevice"] = prevOutputDevice
	return ret


def setTemporaryAudioOutputDevice(outputDevice):
	global _temporaryOutputDevice
	curSynth = getSynth()
	prevOutputDevice = config.conf["speech"]["outputDevice"]
	ret = setOutputDevice(curSynth, outputDevice)
	if not ret:
		return

	def confirm(synth, prevOutputDevice):
		global _temporaryOutputDevice
		from ..settings import _addonConfigManager
		timeToLive = _addonConfigManager.getConfirmAudioDeviceChangeTimeOut()
		from ..utils import PutWindowOnForeground
		dialog = ConfirmOutputDevice(None, timeToLive)
		with dialog as d:
			PutWindowOnForeground(d.GetHandle(), 10, 0.5)
			res = d.ShowModal()
			d.Destroy()
		if res == wx.ID_OK:
			_temporaryOutputDevice = outputDevice
		else:
			# return to previous output device
			setOutputDevice(synth, prevOutputDevice)
	from ..settings import toggleConfirmAudioDeviceChangeAdvancedOption
	if toggleConfirmAudioDeviceChangeAdvancedOption(False):
		wx.CallLater(50, confirm, curSynth, prevOutputDevice)
	else:
		_temporaryOutputDevice = outputDevice
		obj = api.getFocusObject()
		speech.speakObject(obj)


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
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		self.deviceNames = getDeviceNames()
		from synthDriverHandler import _audioOutputDevice
		self.curOutputDevice = _audioOutputDevice
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
		setButton = bHelper.addButton(
			self,
			# Translators: This is a label of a button appearing
			# on Temporary audio device manager dialog.
			label=_("&Set as temporary audio device"))
		setButton.SetDefault()
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
		setButton.Bind(wx.EVT_BUTTON, self.onSetButton)
		quitTemporaryAudioDeviceButton.Bind(wx.EVT_BUTTON, self.onQuitTemporaryAudioDevice)
		closeButton.Bind(wx.EVT_BUTTON, self.onClose)
		self.SetEscapeId(wx.ID_CLOSE)
		self.audioDevicesListBox.SetFocus()
		if not _temporaryOutputDevice:
			quitTemporaryAudioDeviceButton.Disable()

	def Destroy(self):
		TemporaryAudioDeviceManagerDialog._instance = None
		super(TemporaryAudioDeviceManagerDialog, self).Destroy()

	def onSelectDevice(self, evt):
		if self.selectDelay:
			self.selectDelay.Stop()
			self.selectDelay = None
		deviceName = self.audioDevicesListBox.GetStringSelection()

		def callback(deviceName):
			# to send a tone on the selected output device
			from synthDriverHandler import _audioOutputDevice
			curOutputDevice = _audioOutputDevice
			config.conf["speech"]["outputDevice"] = deviceName
			# Reinitialize the tones module to update the audio device
			import tones
			tones.terminate()
			tones.initialize()
			tones.beep(250, 100)
			time.sleep(0.3)
			tones.beep(350, 100)
			time.sleep(0.3)
			config.conf["speech"]["outputDevice"] = curOutputDevice
			# Reinitialize the tones module to update the audio device to the current output device
			import tones
			tones.terminate()
			tones.initialize()

		# we have to wait for the device name to be said by NVDA before changing the device
		self.selectDelay = wx.CallLater(3000, callback, deviceName)

	def onSetButton(self, evt):
		outputDevice = self.audioDevicesListBox.GetStringSelection()
		wx.CallLater(200, setTemporaryAudioOutputDevice, outputDevice)
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
		wx.EvtHandler.Unbind(self.timer, wx.EVT_TIMER)
		super(ConfirmOutputDevice, self).Destroy()


def handlePostConfigProfileSwitch():
	if _temporaryOutputDevice:
		synth = getSynth()
		setOutputDevice(synth, _temporaryOutputDevice)


# we must patche nvwave.playWaveFile method:
# for playing modified NVDA sound files
#  tfor using current output audio device held by synthDriverHandler
# use _audioDevice instead of config.conf["speech"]["outputDevice"]
from versionInfo import version_year, version_major
NVDAVersion = [version_year, version_major]


def myPlayWaveFile(
	fileName: str,
	asynchronous: bool = True,
	isSpeechWaveFileCommand: bool = False
):
	"""plays a specified wave file.
	@param fileName: the path to the wave file, usually absolute.
	@param asynchronous: whether the wave file should be played asynchronously
		If C{False}, the calling thread is blocked until the wave has finished playing.
	@param isSpeechWaveFileCommand: whether this wave is played as part of a speech sequence.
	"""
	from synthDriverHandler import _audioOutputDevice
	newFileName = getModifiedNVDAWaveFile(fileName)
	if newFileName != fileName:
		log.debug("%s file has been replaced by %s modified file" % (fileName, newFileName))
	outputDevice = config.conf["speech"]["outputDevice"]
	config.conf["speech"]["outputDevice"] = _audioOutputDevice
	if NVDAVersion >= [2023, 1]:
		ret = _nvdaPlayWaveFile(newFileName, asynchronous, isSpeechWaveFileCommand)
	else:
		ret = _nvdaPlayWaveFile(newFileName, asynchronous)
	config.conf["speech"]["outputDevice"] = outputDevice
	return ret


_nvdaPlayWaveFile = None


def initialize():
	global _nvdaPlayWaveFile
	from ..settings import (
		toggleAllowNVDATonesVolumeAdjustmentAdvancedOption,
		toggleAllowNVDASoundGainModificationAdvancedOption,
		isInstall
	)
	from ..settings.addonConfig import FCT_TemporaryAudioDevice
	if ((
		toggleAllowNVDATonesVolumeAdjustmentAdvancedOption(False)
		and toggleAllowNVDASoundGainModificationAdvancedOption(False))
		or isInstall(FCT_TemporaryAudioDevice)
	):
		# patche playWaveFile to use temporary audio and modified sound files
		_nvdaPlayWaveFile = nvwave.playWaveFile
		nvwave.playWaveFile = myPlayWaveFile
		log.debug(
			"nvwave.playWaveFile patched by: %s of %s module "
			% (myPlayWaveFile.__name__, myPlayWaveFile.__module__))
	if isInstall(FCT_TemporaryAudioDevice):
		config.post_configProfileSwitch.register(handlePostConfigProfileSwitch)
		synthDrivers.oneCore.SynthDriver._maybeInitPlayer = _maybeInitPlayerEx
		log.debug(
			"synthDrivers.oneCore.SynthDriver._maybeInitPlayer  patched by: %s of %s module"
			% (_maybeInitPlayerEx.__name__, _maybeInitPlayerEx.__module__))


def terminate():
	global _nvdaPlayWaveFile
	if _nvdaPlayWaveFile is not None:
		nvwave.playWaveFile = _nvdaPlayWaveFile
		_nvdaPlayWaveFile = None
