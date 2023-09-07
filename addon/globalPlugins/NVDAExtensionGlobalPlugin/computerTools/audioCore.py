# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\audioCore.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


import addonHandler
from logHandler import log
import os
from threading import Thread
import time
import ui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL, CoCreateInstance, CLSCTX_INPROC_SERVER, CoInitialize
import sys
import wx
import tones
from ..utils.py3Compatibility import getUtilitiesPath, getCommonUtilitiesPath
commonUtilitiesPath = getCommonUtilitiesPath()
utilitiesPath = getUtilitiesPath()
pycawPath = os.path.join(utilitiesPath, "pycawEx")
sysPath = sys.path
sys.path.append(commonUtilitiesPath)
sys.path.append(utilitiesPath)
sys.path.append(pycawPath)
from pycawEx.pycaw import (
	AudioUtilities, IAudioEndpointVolume, AudioDeviceState, IChannelAudioVolume,
	IMMDeviceEnumerator, CLSID_MMDeviceEnumerator, MMNotificationClient
)
from pycawEx.constants import (
	DEVICE_STATE, EDataFlow,
)
sys.path = sysPath


addonHandler.initTranslation()


nvdaProcessName = "nvda.exe"

# Translators: part of message to report position of application on speakers
toLeftMsg = _("to left")
# Translators: part of message to report position of application on speakers
toRightMsg = _("to right")
# Translators: part of message to report position of application on speakers
inCenterMsg = _("in center")
# Translators: part of message to report position of application on speakers
channelsMutedMsg = _("channels muted")

# Translators: part of message for announcement of application volume level.
volumeMsg = _("Volume")
# Translators: part of message for announcement of speakers volume level.
mainVolumeMsg = _("Main volume")

# save nvda channel volume levels (only if no wasapi use)
_NVDAChannelsVolume = (1.0, 1.0)

_previousAppVolumeLevels = {}
_levelLimitationBeep = (400, 30)


def isWasapiUsed():
	# wasapi can be used since nvda 2023.2
	# by checking the advanced option: use wasapi for audio output
	try:
		from nvwave import WasapiWavePlayer, WavePlayer
		if WavePlayer == WasapiWavePlayer:
			return True
	except Exception:
		pass
	return False


def getCurrentNVDAChannelsVolume():
	return _NVDAChannelsVolume


def isNVDA(appName):
	return (
		appName.lower() == nvdaProcessName
		or appName.startswith("nvda_update")
	)


def getNVDASessionName():
	return nvdaProcessName


# memorize the last output audio device that was announced on volume change
_lastSpokenOutputAudioDevice = None
# memorize last application spoken on volume change
_lastAppOnVolumeChange = None


class AudioSource(object):
	def __init__(self, pycawSession, name=None):
		self.session = pycawSession
		self._name = name

	@property
	def volumeObj(self):
		return self.session.SimpleAudioVolume

	@property
	def channelVolumeObj(self):
		return self.session._ctl.QueryInterface(IChannelAudioVolume)

	def getProcessName(self):
		if self.session.Process:
			return self.session.Process.name()
		return None

	@property
	def name(self):
		if self._name is None:
			self._name = self.getProcessName()
		return self._name

	def isNVDAProcess(self):
		if self.session.Process and self.session.Process.name() == nvdaProcessName:
			return True
		return False

	@property
	def volume(self):
		return self.volumeObj.GetMasterVolume()

	def setVolume(self, level):
		log.debug("%s set volume to %s" % (self.name, level))
		self.volumeObj.SetMasterVolume(level, None)

	def getMute(self):
		return self.volumeObj.GetMute()

	def setMute(self, muteState):
		log.debug("%s set mute: %s " % (self.name, muteState))
		self.volumeObj.SetMute(muteState, None)

	def toggleMute(self, silent=True):
		self.setMute(not self.getMute())
		if silent:
			return
		if not self.getMute():
			msg = _("Volume on")
		else:
			msg = _("volume off")
		appMsg = ".".join(self._name.split(".")[:-1])
		ui.message("%s %s" % (appMsg, msg))

	@property
	def channelsCount(self):
		return self.channelVolumeObj.GetChannelCount()

	@property
	def isStereo(self):
		return self.channelsCount == 2

	@property
	def channelsVolume(self):
		if self.isStereo:
			left = self.channelVolumeObj.GetChannelVolume(0)
			right = self.channelVolumeObj.GetChannelVolume(1)
			return (left, right)
		return None

	def setChannels(self, channels):
		if not self.isStereo:
			log.debug("%s audio source is not stereo:channels count= %s" % (self.name, self.channelsCount))
			return
		log.debug("%s set Channels: left= %s, right= %s" % (self.name, channels[0], channels[1]))
		self.channelVolumeObj.SetChannelVolume(0, channels[0], None)
		self.channelVolumeObj.SetChannelVolume(1, channels[1], None)

	def getApplicationVolumeInfo(self):
		if not self.isStereo:
			return ""
		channelsVolume = self.channelsVolume
		left = int(channelsVolume[0] * 100)
		right = int(channelsVolume[1] * 100)
		if left == 0 and right == 0:
			return channelsMutedMsg
		if left == 0:
			return toRightMsg
		if right == 0:
			return toLeftMsg
		if left < right:
			return _("stronger on the right")
		if left > right:
			return _("stronger on the left")
		if left == right:
			return inCenterMsg
		return ""


class AudioSources(object):
	def __init__(self, device=None):
		self._device = device
		self._audioSources = self._getAudioSources()

	def _getAudioSources(self):
		audioSources = {}
		deviceId = self._device.id if self._device else None
		for session in AudioUtilities.GetAllSessions(deviceId):
			sourceName = session.DisplayName
			if "AudioSrv.Dll" in session.DisplayName:
				if self._device._default:
					sourceName = _("System sounds")
				else:
					sourceName = None
			elif session.Process:
				processName = session.Process.name()
				if sourceName == "":
					if not isNVDA(processName):
						sourceName = processName
					else:
						sourceName = processName
				elif sourceName != "" and not isNVDA(processName):
					sourceName = processName
			if not sourceName:
				continue
			audioSources[sourceName] = AudioSource(session, sourceName)
		log.debug("audioSources %s: id: %s, %s" % (
			self._device.name if self._device else "",
			self._device.id if self._device else "",
			audioSources))
		return audioSources

	@property
	def sources(self):
		return self._audioSources

	def getAudioSource(self, appName):
		# get audio source for a particular application on this device
		log.debug("getAudioSource: appName= %s" % appName)
		audioSource = self.sources.get(appName, None)
		if audioSource is not None:
			return audioSource
		for source in self.sources:
			audioSource = self.sources[source]
			processName = audioSource.getProcessName()
			if processName and appName == processName:
				return audioSource
		return None

	def getNVDAAudioSource(self):
		appName = getNVDASessionName()
		return self.getAudioSource(appName)

	def validateVolumeLevel(self, level, appName):
		log.debug("validateVolumeLevel: %s, level: %s" % (appName, level))
		absoluteLevel = level
		speakersVolume = self._device.getVolume()
		log.debug("speakersVolume: %s" % speakersVolume)
		relativeLevel = round(level / speakersVolume)
		maxLevel = int(round(speakersVolume * 100))
		log.debug("relativeLevel: %s, max: %s" % (relativeLevel, maxLevel))
		if relativeLevel > 100:
			from ..settings import toggleIncreaseSpeakersVolumeIfNecessaryAdvancedOption
			if toggleIncreaseSpeakersVolumeIfNecessaryAdvancedOption(False):
				offset = round((relativeLevel - 100) * (maxLevel / 100))
				self._device.changeVolume(action="increase", value=offset, reportValue=False)
			else:
				absoluteLevel = maxLevel
				tones.beep(_levelLimitationBeep[0], _levelLimitationBeep[1])
			relativeLevel = 100
		elif isNVDA(appName):
			# check if volume is not less than the configured threshold volume
			from ..settings import _addonConfigManager
			speakersRecoveryLevel = _addonConfigManager .getMasterVolumeLevel()
			NVDAMinLevel = _addonConfigManager.getMinNVDAVolumeLevel()
			minLevel = round(speakersRecoveryLevel * NVDAMinLevel / 100)
			# perhaps, minLevel is higher then current speakers volume
			if maxLevel < minLevel:
				# set minLevel to  current speakers volume
				minLevel = maxLevel
			relativeMinLevel = round(minLevel / (100 * speakersVolume) * 100)
			log.debug("relativeMinLevel: %s, minLevel: %s" % (relativeMinLevel, minLevel))
			if relativeLevel < relativeMinLevel:
				absoluteLevel = minLevel
				relativeLevel = relativeMinLevel
				tones.beep(_levelLimitationBeep[0], _levelLimitationBeep[1])
		log.debug("validateVolumeLevel return: relativeLevel= %s,absoluteLevel= %s" % (
			relativeLevel, absoluteLevel))
		return (relativeLevel, absoluteLevel)

	def announceVolumeLevel(self, level, appName=None):
		from ..settings import toggleReportVolumeChangeAdvancedOption
		if not toggleReportVolumeChangeAdvancedOption(False):
			return
		msg = "%s %s" % (volumeMsg, level)
		global _lastAppOnVolumeChange
		if appName and appName != _lastAppOnVolumeChange:
			appMsg = ".".join(appName.split(".")[:-1])

			_lastAppOnVolumeChange = appName
			msg = "%s %s" % (appMsg, msg)
		wx.CallLater(40, ui.message, msg)

	def getPreviousApplicationVolumeLevel(self, appName):
		global _previousAppVolumeLevels
		deviceName = self._device.name
		if deviceName in _previousAppVolumeLevels:
			return _previousAppVolumeLevels[deviceName].get(appName, None)
		return None

	def setPreviousApplicationVolumeLevel(self, appName, level):
		global _previousAppVolumeLevels
		global _previousAppVolumeLevels
		deviceName = self._device.name
		if deviceName not in _previousAppVolumeLevels:
			_previousAppVolumeLevels[deviceName] = {}
		_previousAppVolumeLevels[deviceName][appName] = level

	def setApplicationVolume(self, appName, level=100, report=True, reportValue=None):
		global _previousAppVolumeLevels
		global _previousAppVolumeLevels
		log.debug("setApplicationVolume: %s, level= %s, report: %s, reportValue: %s" % (
			appName, level, report, reportValue))
		audioSource = self.getAudioSource(appName)
		if audioSource is None:
			return
		audioSource.setMute(False)
		curLevel = audioSource.volume
		self.setPreviousApplicationVolumeLevel(appName.lower(), round(curLevel * 100))
		level = float(level / 100)
		audioSource.setVolume(level)
		level = audioSource.volume
		if report:
			volume = reportValue if reportValue else int(round(level * 100))
			self.announceVolumeLevel(volume, appName)
		log.warning("%s volume is set to %s" % (appName, level))

	def changeAppVolume(self, appName=None, action="increase", value=100, report=True, reportValue=None):
		log.debug("changeAppVolume: %s, action= %s, level: %s" % (appName, action, value))
		from ..settings import _addonConfigManager
		audioSource = self.getAudioSource(appName)
		if not audioSource:
			# Translators: message to user to indicate that the application don't use any output audio device
			ui.message(_("This application don't use any output audio device"))
			return
		audioSource.setMute(False)
		speakersVolume = self._device.getVolume()
		offset = _addonConfigManager.getVolumeChangeStepLevel()
		curLevel = self._device.getAbsoluteLevel(audioSource.volume)
		if action == "increase":
			level = min(100, curLevel + offset)
		elif action == "decrease":
			level = max(0, curLevel - offset)
		elif action == "max":
			level = 100
		elif action == "min":
			level = 0
		elif action == "set":
			# value = percent of speakers volume
			level = int(round(100 * speakersVolume) * value / 100)
		else:
			# unknown action
			log.warning("changeFocusedAppVolume: %s action is not known" % action)
			return
		(relativeLevel, absoluteLevel) = self.validateVolumeLevel(level, appName)
		self.setApplicationVolume(appName, relativeLevel, True, absoluteLevel)

	def setApplicationVolumeToPreviousLevel(self, appName):
		level = self.getPreviousApplicationVolumeLevel(appName.lower())
		if level is None:
			return
		self.changeAppVolume(appName=appName, action="set", value=level)

	def getNVDAVolume(self):
		audioSource = self.getNVDAAudioSource()
		if audioSource is None:
			return None
		return audioSource.volume

	def setNVDAVolume(self, volumeLevel):
		log.debug("setNVDAVolume: level= %s" % volumeLevel)
		audioSource = self.getNVDAAudioSource()
		if audioSource is None:
			return
		audioSource.setVolume(volumeLevel)

	def setNVDAVolumeToPreviousLevel(self):
		appName = getNVDASessionName()
		level = self.getPreviousApplicationVolumeLevel(appName.lower())
		if level is None:
			return
		self.changeAppVolume(appName, action="set", value=level)

	def setNVDAVolumeToRecoveryLevel(self, checkThreshold=False):
		log.debug("setNVDAVolumeToRecoveryLevel: checkThreshold = %s" % checkThreshold)
		from ..settings import _addonConfigManager
		audioSource = self.getNVDAAudioSource()
		if not audioSource:
			log.error("NVDA session cannot be found")
			return
		mute = audioSource.getMute()
		if mute:
			audioSource.setMute(False)
			log.warning("NVDA volume is unmuted")
		volumeLevel = audioSource.volume
		NVDAMinLevel = _addonConfigManager.getMinNVDAVolumeLevel()
		minLevel = float(NVDAMinLevel / 100)
		channels = (1.0, 1.0)
		audioSource.setChannels(channels)
		global _NVDAChannelsVolume
		_NVDAChannelsVolume = channels
		log.warning("NVDA  channels are set to 1.0")
		if not checkThreshold or (checkThreshold and volumeLevel <= minLevel):
			NVDARecoveryLevel = float(_addonConfigManager.getNVDAVolumeLevel() / 100)
			audioSource.setVolume(NVDARecoveryLevel)
			log.warning("NVDA volume is set to %s " % NVDARecoveryLevel)
			return True
		return False

	def toggleProcessVolumeMute(self, processName):
		""" Mutes or unmute process volume """
		if isNVDA(processName):
			ui.message(_("Unavailable for NVDA"))
			return
		for sourceName in self.sources:
			if sourceName == processName:
				audioSource = self.sources[sourceName]
				audioSource.toggleMute(silent=False)

	def splitChannels(self, NVDAChannel=None, application=None):
		log.debug("splitChannels: %s, %s" % (NVDAChannel, application))
		audioSource = None
		nvdaAudioSource = self.getNVDAAudioSource()
		if not nvdaAudioSource.isStereo:
			# Translators: message to user that NVDA is not a stereo audio source
			wx.CallLater(40, ui.message, _("Not available: %s is not a stereo audio source") % nvdaAudioSource.name)
			return
		if application:
			audioSource = self.getAudioSource(application)
		if NVDAChannel == "left":
			NVDALevels = (1.0, 0.0)
			appLevels = (0.0, 1.0)
			if application:
				if isNVDA(application) or not audioSource:
					msg = "NVDA %s" % toLeftMsg
				else:
					appMsg = ".".join(application.split(".")[:-1])
					msg = _("NVDA {to}, {app} {appTo}") .format(to=toLeftMsg, app=appMsg, appTo=toRightMsg)
			else:
				msg = _("NVDA {to} and all other audio sources {appTo}") .format(to=toLeftMsg, appTo=toRightMsg)
		elif NVDAChannel == "right":
			NVDALevels = (0.0, 1.0)
			appLevels = (1.0, 0.0)
			if application:
				if isNVDA(application) or not audioSource:
					msg = "NVDA %s" % toRightMsg
				else:
					appMsg = ".".join(application.split(".")[:-1])
					msg = _("NVDA {to}, {app} {appTo}") .format(to=toRightMsg, app=appMsg, appTo=toLeftMsg)
			else:
				msg = _("NVDA {to} and all other audio sources {appTo}") .format(to=toRightMsg, appTo=toLeftMsg)
		else:
			NVDALevels = (1.0, 1.0)
			appLevels = (1.0, 1.0)
			if application:
				if isNVDA(application) or not audioSource:
					msg = "NVDA%s" % inCenterMsg
				else:
					appMsg = ".".join(application.split(".")[:-1])
					msg = _("NVDA and {app} {to}") .format(app=appMsg, to=inCenterMsg)
			else:
				msg = _("All audio sources {appTo}") .format(appTo=inCenterMsg)
		if application:
			if not isNVDA(application):
				# split audio only for this application
				if not audioSource or not audioSource.isStereo:
					return
				audioSource.setChannels(appLevels)
				for source in self.sources:
					audioSource = self.sources[source]
					if not audioSource.isStereo:
						continue
					if audioSource.isNVDAProcess():
						audioSource.setChannels(NVDALevels)
		else:
			# split channel of all audio applications
			for source in self.sources:
				audioSource = self.sources[source]
				if not audioSource.isStereo:
					continue
				if audioSource.isNVDAProcess():
					audioSource.setChannels(NVDALevels)
					global _NVDAChannelsVolume
					_NVDAChannelsVolume = NVDALevels
				else:
					audioSource.setChannels(appLevels)
		from speech import cancelSpeech
		wx.CallLater(40, cancelSpeech)
		wx.CallLater(80, ui.message, msg)
		log.warning(msg)

	def toggleChannels(self, balance="center", application=None, silent=False):
		log.debug("toggleChannels:  %s, %s, %s" % (balance, application, silent))
		processName = application
		if processName not in self.sources.keys():
			return
		log.debug("toggleChannels: %s, %s" % (balance, application))
		audioSource = self.getAudioSource(processName)
		if not audioSource.isStereo:
			# Translators: message to user that audio source is not a stereo audio source
			wx.CallLater(40, ui.message, _("Not available: %s is not a stereo audio source") % audioSource.name)
			return
		if balance == "left":
			levels = (1.0, 0.0)
			toMsg = toLeftMsg
		elif balance == "right":
			levels = (0.0, 1.0)
			toMsg = toRightMsg
		else:
			levels = (1.0, 1.0)
			toMsg = inCenterMsg
		audioSource.setChannels(levels)
		appMsg = audioSource.name.replace(".exe", "")
		msg = "{app} {to}" .format(app=appMsg, to=toMsg)
		if not silent:
			from speech import cancelSpeech
			wx.CallLater(10, cancelSpeech)
			wx.CallLater(80, ui.message, msg)
		log.warning(msg)

	def centerAudioSources(self, onlyNVDA=True):
		if onlyNVDA:
			audioSource = self.getNVDAAudioSource()
			if audioSource:
				if not audioSource.isStereo:
					# Translators: message to user that audio source is not a stereo audio source
					wx.CallLater(40, ui.message, _("Not available: %s is not a stereo audio source") % audioSource.name)
					return
				audioSource.setChannels((1.0, 1.0))
		else:
			for source in self.sources:
				audioSource = self.sources[source]
				if audioSource.isStereo:
					audioSource.setChannels((1.0, 1.0))


class AudioDevice(object):
	_previousSpeakersVolumeLevel = None

	def __init__(
		self,
		id,
		name,
		interface=None
	):
		self._id = id
		self._name = name
		self._interface = interface
		self._volumeObj = None
		self._channel: int = 0
		self._default: bool = False

	@property
	def id(self) -> str:
		"""ID of the current audio source.
		@return: device ID or audio session name
		@rtype: str
		"""
		return self._id

	@property
	def name(self) -> str:
		"""Name of the current audio source.
		@return: audio source name
		@rtype: str
		"""
		return self._name

	@property
	def volumeObj(self):
		if self._volumeObj is None:
			self._volumeObj = self._interface.QueryInterface(IAudioEndpointVolume)
		return self._volumeObj

	def getVolume(self):
		return self.volumeObj.GetMasterVolumeLevelScalar()

	def changeVolume(self, action="increase", value=None, reportValue=True):
		from ..settings import (
			_addonConfigManager,
			toggleReportVolumeChangeAdvancedOption)
		if self.volumeObj is None:
			return False

		mute = self.volumeObj.GetMute()
		if mute:
			self.volumeObj.SetMute(not mute, None)
			log.warning(" Unmute master volume")
		defaultOffset = 0.01 * _addonConfigManager.getVolumeChangeStepLevel()
		minLevel = float(_addonConfigManager .getMinMasterVolumeLevel()) / 100
		speakersVolume = self.volumeObj.GetMasterVolumeLevelScalar()
		if action == "increase":
			offset = value / 100 if value else defaultOffset
			level = min(1, speakersVolume + offset)
		elif action == "decrease":
			offset = value / 100 if value else defaultOffset
			level = max(minLevel, speakersVolume - offset)
		elif action == "max":
			level = 1.0
		elif action == "min":
			level = float(_addonConfigManager .getMinMasterVolumeLevel()) / 100
		elif action == "set":
			minimumLevel = _addonConfigManager .getMinMasterVolumeLevel()
			if value < minimumLevel:
				# Translators: message to user to indicate command reject.
				ui.message(
					_(
						"Impossible, the volume level cannot be lower than the configured recovery threshold equal to %s"
					) % minimumLevel
				)
				return
			level = round(value) / 100
		else:
			log.warning("changeSpeakerVolume: %s action is not known" % action)
			return
		self._previousSpeakersVolumeLevel = round(speakersVolume * 100)
		msg = "%s %s" % (mainVolumeMsg, int(round(level * 100)))
		global _lastSpokenOutputAudioDevice
		if self != _lastSpokenOutputAudioDevice:
			msg = "%s, %s" % (self.name, msg)
			_lastSpokenOutputAudioDevice = self
		self.volumeObj.SetMasterVolumeLevelScalar(level, None)
		if reportValue and toggleReportVolumeChangeAdvancedOption(False):
			ui.message(msg)
			log.warning("Master volume is set to %s" % level)
		return True

	def getAbsoluteLevel(self, volumeLevel):
		log.debug("getAbsoluteLevel level= %s" % volumeLevel)
		speakersVolume = self.getVolume()
		level = round(volumeLevel * 100 * speakersVolume)
		return level

	def getRelativeLevel(self, level):
		speakersVolume = self.getVolume()
		relativeLevel = round(level / speakersVolume)
		return relativeLevel

	def setVolumeToRecoveryLevel(self, checkThreshold=False):
		log.debug("setVolumeToRecoveryLevel: %s, checkThreshold = %s" % (self.name, checkThreshold))
		from ..settings import _addonConfigManager
		""" Unmute speaker volume if it's mute
		and set level volume to configured volume
		if it's lowest than configured min volume level
		"""
		volumeLevel = self.volumeObj.GetMasterVolumeLevelScalar()
		mute = self.volumeObj.GetMute()
		if mute:
			self.volumeObj.SetMute(0, None)
			log.warning("%s  master volume unmuted" % self.name)
		minLevel = float(_addonConfigManager .getMinMasterVolumeLevel()) / 100
		if not checkThreshold or (checkThreshold and volumeLevel < minLevel):
			level = float(_addonConfigManager .getMasterVolumeLevel()) / 100
			self.volumeObj.SetMasterVolumeLevelScalar(level, None)
			log.warning(
				"%s Master volume is set to %s" % (self.name, _addonConfigManager .getMasterVolumeLevel()))
			return True
		return False

	def setVolumeLevelToPreviousLevel(self, ):
		if self._previousSpeakersVolumeLevel is None:
			return
		self.changeVolume(action="set", value=self._previousSpeakersVolumeLevel)


_deviceEnumerator = None


class AudioOutputDevicesManager(object):
	def __init__(self):
		super().__init__()
		self.initialized = False

	def getDeviceFromName(self, deviceName):
		global _audioOutputDevice
		for device in self._devices:
			if device.name.startswith(deviceName):
				return device
		return None
		return self.getDeviceFromName(_audioOutputDevice)

	def findDeviceFromApplicationName(self, appName):
		log.debug("findDeviceFromApplicationName: %s, devices= %s" % (appName, self._devices))
		for device in self._devices:
			audioSources = AudioSources(device)
			if audioSources.getAudioSource(appName):
				return device
		return None

	def getCurrentNVDADevice(self):
		from synthDriverHandler import _audioOutputDevice
		if _audioOutputDevice is None:
			return None
		for device in self._devices:
			if device.name.startswith(_audioOutputDevice):
				return device
		return self.getDefaultDevice()

	def getDefaultDevice(self):
		for device in self._devices:
			if device._default:
				return device
		return None

	def getDeviceNames(self):
		names = []
		for device in self._devices:
			name = device._name
			if name:
				names.append(name)
		return names

	def getDevices(self):
		return self._devices

	def setSpeakersVolumeLevelToPreviousLevel(self):
		# back the volume of last modified audio device to itthe previous level
		global _lastSpokenOutputAudioDevice
		if _lastSpokenOutputAudioDevice:
			_lastSpokenOutputAudioDevice .setVolumeLevelToPreviousLevel()

	def setRecoveryDefaultVolumes(self):
		from ..settings import _addonConfigManager
		nvdaAudioDevice = self.getCurrentNVDADevice()
		curSpeakersVolume = nvdaAudioDevice.getVolume()
		if curSpeakersVolume is None:
			log.warning("Cannot establish default recovery settings: speakers volume is not available")
			return
		volume = int(curSpeakersVolume * 100)
		if volume > 50:
			volume = 50
		volume = 10 * int(volume / 10)
		if volume == 0:
			volume = 10
		_addonConfigManager.setMasterVolumeLevel(volume)
		log.warning("The recovery speakers volume is set to %s" % volume)
		minThreshold = 0 if volume == 10 else 10
		_addonConfigManager.setMinMasterVolumeLevel(minThreshold)
		log.warning(
			"For speakers, the min Threshold is set to %s and  recovery volume  is set to %s" % (minThreshold, volume))
		audioSources = AudioSources(nvdaAudioDevice)
		curNVDAVolume = audioSources.getNVDAVolume()
		if curNVDAVolume is None:
			log.warning("Cannot establish default NVDA recovery settings: NVDAa volume is not available")
			return
		volume = int(curNVDAVolume * 100)
		volume = 10 * int(volume / 10)
		_addonConfigManager.setNVDAVolumeLevel(volume)
		minThreshold = 0 if volume == 10 else 10
		_addonConfigManager.setMinNVDAVolumeLevel(minThreshold)
		log.warning(
			"For NVDA, the min Threshold is set to %s and  recovery volume  is set to %s" % (minThreshold, volume))

	def runNewDevicesScan(self):
		# perhaps scan is running. Try to stop it
		self.shouldStopScan = True
		time.sleep(0.5)
		self.shouldStopScan = False
		Thread(target=self.scan).start()

	def deviceStateChanged(self, deviceId, state):
		log.debug("deviceStateChanged: %s, state: %s" % (deviceId, state))
		self.runNewDevicesScan()

	def installAudioDeviceChangesMonitoring(self):
		self.deviceEnumerator = CoCreateInstance(
			CLSID_MMDeviceEnumerator, IMMDeviceEnumerator, CLSCTX_INPROC_SERVER)
		self.callback = AudioDeviceChangesNotification()
		self.deviceEnumerator.RegisterEndpointNotificationCallback(self.callback)

	def scan(self):
		log.debug("Starting devices scan")
		self.scanDone = False
		# for garbage collector
		if hasattr(self, "_devices"):
			for device in self._devices:
				del device
		self._devices = []
		CoInitialize()
		defaultDevice = AudioUtilities.GetSpeakers()
		devices = []
		defaultDeviceDecected = False
		try:
			flow = EDataFlow.eRender
			state = DEVICE_STATE.ACTIVE
			mixers = [mx for mx in AudioUtilities.GetAllDevices(flow, state) if mx]
		except Exception:
			mixers = []
		for mixer in mixers:
			time.sleep(0.05)
			if self.shouldStopScan:
				log.debug("Scanning stopped")
				return self
			if mixer.state != AudioDeviceState.Active:
				continue
			immDevice = AudioUtilities.GetSpeakers(mixer.id)
			try:
				interface = immDevice.Activate(
					IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
			except Exception:
				continue
			device = AudioDevice(
				id=mixer.id or '',
				name=mixer.FriendlyName or mixer.id or '',
				interface=interface
				# volume=cast(interface, POINTER(IAudioEndpointVolume))
			)
			device._default = False
			if device.id and device.name:
				if device.id == defaultDevice .GetId():
					device._default = True
					defaultDeviceDecected = True
					devices.insert(0, device)
				else:
					devices.append(device)
		# Insert to the list the default audio output device if it is not listed
		# for some reason on some systems it is not determined in the standard way
		if not defaultDeviceDecected:
			device = AudioDevice(
				id=defaultDevice.GetId() or '',
				name=self.getDeviceNameByID(defaultDevice.GetId()) or '',
				volume=cast(
					defaultDevice.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None),
					POINTER(IAudioEndpointVolume))
			)
			device._default = True
			devices.insert(0, device)

		# we want the same devices that NVDA
		from nvwave import _getOutputDevices
		nvdaAudioDevices = _getOutputDevices()
		for deviceID, deviceName in nvdaAudioDevices:
			for device in devices:
				time.sleep(0.05)
				if self.shouldStopScan:
					self._devices = []
					log.debug("Scanning stopped")
					return self
				if device.name.startswith(deviceName):
					# nvda device name are truncated if no wasapi, so memorize it in device object
					device.nvdaDeviceName = deviceName
					self._devices.append(device)
		self.scanDone = True
		log.debug("Devices scan terminated")
		return self

	def initialize(self):
		self.scanDone = False
		self.shouldStopScan = False
		self.installAudioDeviceChangesMonitoring()
		Thread(target=self.scan).start()
		# wait for 5 seconds
		i = 50
		from time import sleep
		while not self.scanDone and i:
			sleep(0.1)
			i -= 1
		if i == 0:
			log.debug(" end of scan too long")
			return
		from ..settings import _addonConfigManager
		if _addonConfigManager.shouldSetRecoveryDefaultVolumes:
			# after new add-on installation, we must save current nvda and nvda audio output device volumes
			self.setRecoveryDefaultVolumes()
			_addonConfigManager.shouldSetRecoveryDefaultVolumes = False
			return
		from ..settings import toggleSetOnMainAndNVDAVolumeAdvancedOption
		if toggleSetOnMainAndNVDAVolumeAdvancedOption(False):
			device = self.getCurrentNVDADevice()
			device.setVolumeToRecoveryLevel(checkThreshold=True)
			audioSources = AudioSources(device)
			audioSources.setNVDAVolumeToRecoveryLevel(checkThreshold=True)

	def terminate(self):
		if self.initialized:
			nvdaDevice = audioOutputDevicesManager.getCurrentNVDADevice()
			audioSources = AudioSources(nvdaDevice)
			audioSources.centerAudioSources()
			self.deviceEnumerator.UnRegisterEndpointNotificationCallback(audioOutputDevicesManager.callback)
			del self.deviceEnumerator


class AudioDeviceChangesNotification(MMNotificationClient):

	def on_device_state_changed(self, device_id, new_state, new_state_id):
		log.debug(
			"device state changed: device_id: %s, new state: %s, new state id: %s" % (
				device_id, new_state, new_state_id))
		audioOutputDevicesManager.deviceStateChanged(device_id, new_state)

	def on_device_added(self, added_device_id):
		log.debug("device added: %s" % added_device_id)

	def on_device_removed(self, removed_device_id):
		log.debug("device removed: %s" % removed_device_id)

	def on_default_device_changed(self, flow, flow_id, role, role_id, default_device_id):
		log.debug(
			"on_default_device_changed: flow: %s, flow_id: %s, role: %s, role_id: %s, default_device_id: %s" % (
				flow, flow_id, role, role_id, default_device_id))

	def on_property_value_changed(self, device_id, property_struct, fmtid, pid):
		return

		log.debug("on_property_value_changed")


def initialize():
	wx.CallAfter(audioOutputDevicesManager.initialize)


def terminate():
	audioOutputDevicesManager.terminate()


audioOutputDevicesManager = AudioOutputDevicesManager()
