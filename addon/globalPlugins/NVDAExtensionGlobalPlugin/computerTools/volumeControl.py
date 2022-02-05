# globalPlugins\NVDAExtensionGlobalPlugin\volumeControl\volumeControl.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2017 - 2021 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


import addonHandler
from logHandler import log
import os
import ui
import ctypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import sys
import api
import wx
import nvwave
from ..utils.py3Compatibility import getUtilitiesPath, getCommonUtilitiesPath
commonUtilitiesPath = getCommonUtilitiesPath()
utilitiesPath = getUtilitiesPath()
pycawPath = os.path.join(utilitiesPath, "pycawEx")
sysPath = sys.path
sys.path.append(commonUtilitiesPath)
sys.path.append(utilitiesPath)
sys.path.append(pycawPath)
from pycawEx.pycaw import (
	AudioUtilities, IAudioEndpointVolume, IChannelAudioVolume)
sys.path = sysPath


addonHandler.initTranslation()
# indicate if module is initialized
_initialized = False

_previousAppVolumeLevel = {}
_previousSpeakersVolumeLevel = None

# Translators: part of message for announcement of application volume level.
volumeMsg = _("Volume")
# Translators: part of message for announcement of speakers volume level.
mainVolumeMsg = _("Main volume")

try:
	devices = AudioUtilities.GetSpeakers()
	interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
	_volumeObj = cast(interface, POINTER(IAudioEndpointVolume))
except Exception:
	# no supported
	_volumeObj = None
	log.warning("AudioUtilities getSpeaker not supported on this system")

# save NVDA nvwave.WavePlayer.open method
_originalWaveOpen = None
# NVDA channel  levels
_NVDAChannelsVolume = (1.0, 1.0)
# previous channel levels
_prevNVDAChannelsVolume = None
# nvda volume object
_nvdaVolumeObj = None

winmm = ctypes.windll.winmm

# Translators: part of message to report position of application on speakers
toLeftMsg = _("to left")
# Translators: part of message to report position of application on speakers
toRightMsg = _("to right")
# Translators: part of message to report position of application on speakers
inCenterMsg = _("in center")

nvdaAppName = "nvda.exe"


def isNVDA(appName):
	return True if appName.lower() == nvdaAppName else False


def toggleProcessVolume(processName):
	""" Mutes or unmute process volume """
	try:
		sessions = AudioUtilities.GetAllSessions()
	except Exception:
		# no supported
		log.warning("AudioUtilities getAllCessions not supported on this system")
		return
	for session in sessions:
		try:
			name = session.Process.name()
		except Exception:
			continue
		if name == processName:
			volume = session.SimpleAudioVolume
			mute = volume.GetMute()
			volume.SetMute(not mute, None)
			if not volume.GetMute():
				ui.message(_("Volume on"))
			else:
				ui.message(_("volume off"))
			return
	ui.message(_("No audio controller for this application"))


def setDefaultVolumeControl(addonConfigManager):
	curSpeakersVolume = getSpeakerVolume()
	if curSpeakersVolume is None:
		log.warning("Cannot establish default recovery settings: speakers volume is not available")
		return
	volume = int(curSpeakersVolume * 100)
	if volume > 50:
		volume = 50
	volume = 10 * int(volume / 10)
	if volume == 0:
		volume = 10
	addonConfigManager.setMasterVolumeLevel(volume)
	log.warning("The recovery speakers volume is set to %s" % volume)
	minThreshold = 0 if volume == 10 else 10
	addonConfigManager.setMinMasterVolumeLevel(minThreshold)
	log.warning(
		"For speakers, the min Threshold is set to %s and  recovery volume  is set to %s" % (minThreshold, volume))
	curNVDAVolume = getNVDAVolume()
	if curNVDAVolume is None:
		log.warning("Cannot establish default NVDA recovery settings: NVDAa volume is not available")
		return
	volume = int(curNVDAVolume * 100)
	volume = 10 * int(volume / 10)
	addonConfigManager.setNVDAVolumeLevel(volume)
	minThreshold = 0 if volume == 10 else 10
	addonConfigManager.setMinNVDAVolumeLevel(minThreshold)
	log.warning(
		"For NVDA, the min Threshold is set to %s and  recovery volume  is set to %s" % (minThreshold, volume))


def getVolumeObj():
	return _volumeObj


def getSpeakerVolume():
	if _volumeObj is None:
		return None
	volumeLevel = _volumeObj.GetMasterVolumeLevelScalar()
	return volumeLevel


def getNVDAChannelsVolume():
	return _NVDAChannelsVolume


def setSpeakerVolumeToRecoveryLevel(checkThreshold=False):
	log.debug("setMasterVolume: checkThreshold = %s" % checkThreshold)
	from ..settings import _addonConfigManager
	""" Unmute speaker volume if it's mute
	and set level volume to configured volume
	if it's lowest than configured min volume level """
	if _volumeObj is None:
		return False
	volumeObj = _volumeObj
	volumeLevel = volumeObj.GetMasterVolumeLevelScalar()
	mute = volumeObj.GetMute()
	if mute:
		volumeObj.SetMute(0, None)
		log.warning(" Unmute master volume")
	minLevel = float(_addonConfigManager .getMinMasterVolumeLevel()) / 100
	if not checkThreshold or (checkThreshold and volumeLevel < minLevel):
		level = float(_addonConfigManager .getMasterVolumeLevel()) / 100
		volumeObj.SetMasterVolumeLevelScalar(level, None)
		log.warning(
			"Master volume is set to %s" % _addonConfigManager .getMasterVolumeLevel())
		return True
	return False


def getAppVolumeObjByName(appName):
	try:
		sessions = AudioUtilities.GetAllSessions()
	except Exception:
		# no supported
		log.warning("AudioUtilities getAllCessions not supported on this system")
		return None
	debugText = []
	for session in sessions:
		try:
			name = session.Process.name()
			debugText.append(name)
		except Exception:
			continue
		if name.lower() == appName.lower():
			volumeObj = session.SimpleAudioVolume
			return volumeObj
	if isNVDA(appName):
		text = "getAppVolumeObjByName for %s: "% appName  + ", ".join(debugText)
		log.debug(text)
	return None


def getNVDAVolumeObjByPid():
	try:
		sessions = AudioUtilities.GetAllSessions()
	except Exception:
		# no supported
		log.warning("AudioUtilities getAllCessions not supported on this system")
		return None
	nvdapid = os.getpid()
	for session in sessions:
		try:
			pid = session.Process.processId
		except Exception:
			continue
		if pid ==nvdapid:
			return session.SimpleAudioVolume
	return None



def getNVDAVolumeObj():
	global _nvdaVolumeObj
	if _nvdaVolumeObj is not None:
		return _nvdaVolumeObj
	_nvdaVolumeObj = getAppVolumeObjByName(nvdaAppName)
	if _nvdaVolumeObj is None:
		_nvdaVolumeObj = getNVDAVolumeObjByPid()
		if _nvdaVolumeObj is None:
			log.warning("NVDA volume object not found and cannot be initialized")
	return _nvdaVolumeObj 


def getAppVolumeObj(appName):
	if isNVDA(appName):
		return getNVDAVolumeObj()
	else:
		return getAppVolumeObjByName(appName)


def getNVDAVolume():
	volumeObj = getNVDAVolumeObj()
	if volumeObj:
		return volumeObj.GetMasterVolume()
	return None


def setNVDAVolume(volume):
	if volume is None:
		return
	volumeObj = getNVDAVolumeObj()
	if volumeObj is None:
		log.warning("NVDA volume object not initialized")
		return
	volumeObj.SetMasterVolume(volume, None)


def setNVDAVolumeToRecoveryLevel(checkThreshold=False):
	log.debug("setNVDAVolumeToRecoveryLevel: checkThreshold = %s" % checkThreshold)
	from ..settings import _addonConfigManager
	volumeObj = getNVDAVolumeObj()
	if not volumeObj:
		return False
	mute = volumeObj.GetMute()
	if mute:
		volumeObj.SetMute(not mute, None)
		log.warning("Unmute NVDA volume")
	volumeLevel = volumeObj.GetMasterVolume()
	NVDAMinLevel = _addonConfigManager.getMinNVDAVolumeLevel()
	minLevel = float(NVDAMinLevel / 100)
	if not checkThreshold or (checkThreshold and volumeLevel <= minLevel):
		NVDARecoveryLevel = float(_addonConfigManager.getNVDAVolumeLevel() / 100)
		volumeObj.SetMasterVolume(NVDARecoveryLevel, None)
		log.warning("NVDA volume is set to %s" % NVDARecoveryLevel)
		return True
	return False


def validateVolumeLevel(level, appName):
	log.debug("validateVolumeLevel: %s, level: %s" % (appName, level))
	absoluteLevel = level
	speakersVolume = getVolumeObj().GetMasterVolumeLevelScalar()
	log.debug("speakersVolume: %s" % speakersVolume)
	relativeLevel = round(level / speakersVolume)
	maxLevel = int(round(speakersVolume * 100))
	log.debug("relativeLevel: %s, max: %s" % (relativeLevel, maxLevel))
	if relativeLevel > 100:
		from ..settings import toggleIncreaseSpeakersVolumeIfNecessaryAdvancedOption
		if toggleIncreaseSpeakersVolumeIfNecessaryAdvancedOption(False):
			offset = round((relativeLevel - 100) * (maxLevel / 100))
			changeSpeakersVolume(action="increase", value=offset, reportValue=False)
		else:
			absoluteLevel = maxLevel
		relativeLevel = 100
	elif isNVDA(appName):
		nvdaVolume = getNVDAVolume()
		log.debug("nvdaVolume: %s" % nvdaVolume)
		# check if volume is not less than the configured threshold volume
		from ..settings import _addonConfigManager
		speakersRecoveryLevel = _addonConfigManager .getMasterVolumeLevel()
		NVDAMinLevel = _addonConfigManager.getMinNVDAVolumeLevel()
		minLevel = int(round(speakersRecoveryLevel * NVDAMinLevel / 100))
		# perhaps, minLevel is higher then current speakers volume
		if maxLevel < minLevel:
			# set minLevel to  current speakers volume
			minLevel = maxLevel
		relativeMinLevel = round(minLevel / (100 * speakersVolume) * 100)
		log.debug("relativeMinLevel: %s, minLevel: %s" % (relativeMinLevel, minLevel))
		if relativeLevel < relativeMinLevel:
			absoluteLevel = minLevel
			relativeLevel = relativeMinLevel
	return (relativeLevel, absoluteLevel)


def getAbsoluteLevel(volumeLevel):
	if _volumeObj is None:
		speakersVolume = 1.0
	else:
		speakersVolume = _volumeObj.GetMasterVolumeLevelScalar()
	level = int(round(volumeLevel * 100 * speakersVolume))
	return level


def announceVolumeLevel(level):
	from ..settings import toggleReportVolumeChangeAdvancedOption
	if not toggleReportVolumeChangeAdvancedOption(False):
		return
	msg = "%s %s" % (volumeMsg, level)
	wx.CallLater(40, ui.message, msg)


def setAppVolume(appName, level=100, report=True, reportValue=None):
	global _previousAppVolumeLevel
	volumeObj = getAppVolumeObj(appName)
	if not volumeObj:
		return
	mute = volumeObj.GetMute()
	if mute:
		volumeObj.SetMute(not mute, None)
	curLevel = volumeObj.GetMasterVolume()
	_previousAppVolumeLevel[appName.lower()] = curLevel
	level = float(level / 100)
	volumeObj.SetMasterVolume(level, None)
	level = volumeObj.GetMasterVolume()
	if report:
		volume = reportValue if reportValue else int(round(level * 100))
		announceVolumeLevel(volume)
	log.warning("%s volume is set to %s" % (appName, level))


def changeAppVolume(appName=None, action="increase", value=100, report=True, reportValue=None):
	log.debug("changeFocusedAppVolume: %s, action= %s, level: %s" % (appName, action, value))
	from ..settings import _addonConfigManager
	global _previousAppVolumeLevel
	if appName is None:
		focus = api.getFocusObject()
		from appModuleHandler import getAppNameFromProcessID
		appName = getAppNameFromProcessID(focus.processID, True)
	volumeObj = getAppVolumeObj(appName)
	if not volumeObj:
		return
	mute = volumeObj.GetMute()
	if mute:
		volumeObj.SetMute(not mute, None)
	speakersVolume = getVolumeObj().GetMasterVolumeLevelScalar()
	offset = _addonConfigManager.getVolumeChangeStepLevel()
	curLevel = getAbsoluteLevel(volumeObj.GetMasterVolume())
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
	(relativeLevel, absoluteLevel) = validateVolumeLevel(level, appName)
	setAppVolume(appName, relativeLevel, True, absoluteLevel)


def changeSpeakersVolume(action="increase", value=None, reportValue=True):
	global _previousSpeakersVolumeLevel
	from ..settings import (
		_addonConfigManager,
		toggleReportVolumeChangeAdvancedOption)
	if _volumeObj is None:
		return False
	volumeObj = _volumeObj
	mute = volumeObj.GetMute()
	if mute:
		volumeObj.SetMute(not mute, None)
		log.warning(" Unmute master volume")
	defaultOffset = 0.01 * _addonConfigManager.getVolumeChangeStepLevel()
	minLevel = float(_addonConfigManager .getMinMasterVolumeLevel()) / 100
	speakersVolume = volumeObj.GetMasterVolumeLevelScalar()
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
	_previousSpeakersVolumeLevel = speakersVolume
	msg = "%s %s" % (mainVolumeMsg, int(round(level * 100)))
	volumeObj.SetMasterVolumeLevelScalar(level, None)
	if reportValue and toggleReportVolumeChangeAdvancedOption(False):
		ui.message(msg)
		log.warning("Master volume is set to %s" % level)
	return True


def setFocusedAppVolumeToPreviousLevel():
	focus = api.getFocusObject()
	from appModuleHandler import getAppNameFromProcessID
	appName = getAppNameFromProcessID(focus.processID, True)
	level = _previousAppVolumeLevel.get(appName.lower())
	if level is None:
		return
	level = int(level * 100)
	changeAppVolume(appName=appName, action="set", value=level)


def setNVDAVolumeToPreviousLevel():
	appName = nvdaAppName
	level = _previousAppVolumeLevel.get(appName.lower())
	if level is None:
		return
	level = int(level * 100)
	changeAppVolume(appName, action="set", value=level)


def setSpeakersVolumeLevelToPreviousLevel():
	level = _previousSpeakersVolumeLevel
	if level is None:
		return
	level = int(level * 100)
	changeSpeakersVolume(action="set", value=level)


def getChannels():
	audioSessions = AudioUtilities.GetAllSessions()
	channels = {}
	for s in audioSessions:
		try:
			name = s.Process.name()
		except Exception:
			name = None
		if not name or "nvda" in name.lower():
			continue
		channelVolume = s._ctl.QueryInterface(IChannelAudioVolume)
		channelsCount = channelVolume.GetChannelCount()
		if channelsCount != 2:
			continue
		leftVolume = channelVolume.GetChannelVolume(0)
		rightVolume = channelVolume.GetChannelVolume(1)
		channels[name] = (leftVolume, rightVolume)
	return channels


def setApplicationChannelsLevels(applicationVolumes):
	log.debug("setApplicationChannelsLevels")
	applications = list(applicationVolumes.keys())
	audioSessions = AudioUtilities.GetAllSessions()
	for s in audioSessions:
		try:
			name = s.Process.name()
		except Exception:
			name = None
		if not name or name not in applications:
			continue
		channelVolumeObj = s._ctl.QueryInterface(IChannelAudioVolume)
		channelsCount = channelVolumeObj.GetChannelCount()
		if channelsCount != 2:
			continue
		leftVolume, rightVolume = applicationVolumes[name]
		channelVolumeObj.SetChannelVolume(0, leftVolume, None)
		channelVolumeObj.SetChannelVolume(1, rightVolume, None)
		log.debug("Setting of %s channels levels : left = %s, right = %s" % (name, leftVolume, rightVolume))


def updateNVDAAndApplicationsChannelsLevels(applicationsChannelsVolumes):
	global _NVDAChannelsVolume
	_NVDAChannelsVolume = applicationsChannelsVolumes[nvdaAppName]
	appVolumes = applicationsChannelsVolumes.copy()
	del appVolumes[nvdaAppName]
	setApplicationChannelsLevels(appVolumes)


def getApplicationVolumeInfo(application):
	applicationsChannelsVolumes = getChannels()
	applicationsChannelsVolumes[nvdaAppName] = getNVDAChannelsVolume()
	channelsVolume = applicationsChannelsVolumes[application]
	if channelsVolume[0] == 0.0:
		msg = toRightMsg
	elif channelsVolume[1] == 0.0:
		msg = toLeftMsg
	elif channelsVolume[1] == 0.0:
		msg = inCenterMsg
	elif channelsVolume[0] < channelsVolume[1]:
		msg = _("stronger on the right")
	elif channelsVolume[0] > channelsVolume[1]:
		msg = _("stronger on the left")
	else:
		msg = inCenterMsg
	return msg


def splitChannels(NVDAChannel=None, application=None):
	log.debug("splitChannels: %s, %s" % (NVDAChannel, application))
	if not _initialized:
		# cannot split sound for NVDA
		wx.CallLater(40, ui.message, _("Not available cause of conflict with another add-on. See NVDA log"))
		return
	applicationsVolumes = getChannels()
	applicationsVolumes[nvdaAppName] = _NVDAChannelsVolume
	if NVDAChannel == "left":
		NVDALevels = (1.0, 0.0)
		appLevels = (0.0, 1.0)
		if application:
			if isNVDA(application) or application not in applicationsVolumes:
				msg = "NVDA %s" % toLeftMsg
			else:
				appMsg = ".".join(application.split(".")[:-1])
				msg = _("NVDA {to}, {app} {appTo}") .format(to=toLeftMsg, app=appMsg, appTo=toRightMsg)
		else:
			msg = _("NVDA {to} and all applications {appTo}") .format(to=toLeftMsg, appTo=toRightMsg)
	elif NVDAChannel == "right":
		NVDALevels = (0.0, 1.0)
		appLevels = (1.0, 0.0)
		if application:
			if isNVDA(application) or application not in applicationsVolumes:
				msg = "NVDA %s" % toRightMsg
			else:
				appMsg = ".".join(application.split(".")[:-1])
				msg = _("NVDA {to}, {app} {appTo}") .format(to=toRightMsg, app=appMsg, appTo=toLeftMsg)
		else:
			msg = _("NVDA {to} and all applications {appTo}") .format(to=toRightMsg, appTo=toLeftMsg)
	else:
		NVDALevels = (1.0, 1.0)
		appLevels = (1.0, 1.0)
		if application:
			if isNVDA(application) or application not in applicationsVolumes:
				msg = "NVDA%s" % inCenterMsg
			else:
				appMsg = ".".join(application.split(".")[:-1])
				msg = _("NVDA and {app} {to}") .format(app=appMsg, to=inCenterMsg)
		else:
			msg = _("NVDA and all applications {appTo}") .format(appTo=inCenterMsg)
	if application:
		if "application != nvda.exe":
			# split audio only for this application
			applicationsVolumes[application] = appLevels
	else:
		# split channel of all audio applications
		for app in applicationsVolumes:
			if isNVDA(app):
				continue
			applicationsVolumes[app] = appLevels
	applicationsVolumes[nvdaAppName] = NVDALevels
	updateNVDAAndApplicationsChannelsLevels(applicationsVolumes)
	from speech import cancelSpeech
	wx.CallLater(40, cancelSpeech)
	wx.CallLater(80, ui.message, msg)
	log.warning(msg)

def centerFocusedApplication():
		focus = api.getFocusObject()
		from appModuleHandler import getAppNameFromProcessID
		appName = getAppNameFromProcessID(focus.processID, True)
		toggleChannels(application=appName, balance="center")


def toggleChannels(balance="center", application=None):
	log.debug("toggleChannels: %s, %s" % (balance, application))
	if not _initialized and isNVDA(application):
		# cannot toggle sound
		wx.CallLater(40, ui.message, _("Not available cause of conflict with another add-on. See NVDA log"))
		return
	applicationsVolumes = getChannels()
	appMsg = ".".join(application.split(".")[:-1])
	applicationsVolumes[nvdaAppName] = _NVDAChannelsVolume
	if balance == "left":
		levels = (1.0, 0.0)
		toMsg = toLeftMsg
	elif balance == "right":
		levels = (0.0, 1.0)
		toMsg = toRightMsg
	else:
		levels = (1.0, 1.0)
		toMsg = inCenterMsg
	applicationsVolumes[application] = levels
	updateNVDAAndApplicationsChannelsLevels(applicationsVolumes)
	msg = "{app} {to}" .format(app=appMsg, to=toMsg)
	from speech import cancelSpeech
	wx.CallLater(40, cancelSpeech)
	wx.CallLater(80, ui.message, msg)
	log.warning(msg)

# some parts of following code comes from Tony's Enhancements addon for NVDA (author: Tony Malykh)
def waveOutSetVolume(wavePlayer):
	global _prevNVDAChannelsVolume
	if _NVDAChannelsVolume == _prevNVDAChannelsVolume:
		return
	# The low-order word contains the left-channel volume setting,
		# and the high-order word contains the right-channel setting.
	# A value of 0xFFFF represents full volume, and a value of 0x0000 is silence
	leftVolume, rightVolume = _NVDAChannelsVolume
	leftVolume2 = int(0xFFFF * (leftVolume))
	rightVolume2 = int(0xFFFF * (rightVolume))
	volume2 = leftVolume2
	volume2 = volume2 | (rightVolume2 << 16)
	nvdaVolume = getNVDAVolume()
	winmm.waveOutSetVolume(wavePlayer._waveout, volume2)
	setNVDAVolume(nvdaVolume)
	_prevNVDAChannelsVolume = _NVDAChannelsVolume
	log.debug("NVDA channel levels set to %s, %s" % (_NVDAChannelsVolume[0], _NVDAChannelsVolume[1]))


def preWaveOpen(wavePlayer, *args, **kwargs):
	global _originalWaveOpen
	result = _originalWaveOpen(wavePlayer, *args, **kwargs)
	waveOutSetVolume(wavePlayer)
	return result


def isInitialized():
	return _initialized


def initialize():
	global _originalWaveOpen, _initialized
	from ..settings import  isInstall
	from ..settings.addonConfig import FCT_SplitAudio
	if not isInstall(FCT_SplitAudio):
		_initialized = True
		return
	if nvwave.WavePlayer.open.__module__ != "nvwave":
		log.error(
			"Initialization failed: nvwave.WavePlayer.open already patched by: %s" % nvwave.WavePlayer.open.__module__
		)
		return
	if not _originalWaveOpen:
		_originalWaveOpen = nvwave.WavePlayer.open
		nvwave.WavePlayer.open = preWaveOpen
		_initialized = True
		log.debug("volumeControl initialization: nvwave.WavePlayer.open  patched")


def terminate():
	global _originalWaveOpen
	if _originalWaveOpen:
		nvwave.WavePlayer.open = _originalWaveOpen
		_originalWaveOpen = None
