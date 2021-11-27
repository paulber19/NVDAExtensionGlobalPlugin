# globalPlugins\NVDAExtensionGlobalPlugin\volumeControl\__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2017 - 2020 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


import addonHandler
from logHandler import log
import os
import ui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import sys
import api
import appModuleHandler
from ..utils.py3Compatibility import getUtilitiesPath, getCommonUtilitiesPath
commonUtilitiesPath = getCommonUtilitiesPath()
utilitiesPath = getUtilitiesPath()
pycawPath = os.path.join(utilitiesPath, "pycaw")
sysPath = sys.path
sys.path.append(commonUtilitiesPath)
sys.path.append(utilitiesPath)
sys.path.append(pycawPath)
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # noqa:E402
sys.path = sysPath

_previousAppVolumeLevel = {}
_previousSpeakersVolumeLevel = None
addonHandler.initTranslation()
# Translators: part of message for announcement of volume level.
volumeMsg = _("Volume")

try:
	devices = AudioUtilities.GetSpeakers()
	interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
	_volume = cast(interface, POINTER(IAudioEndpointVolume))
except Exception:
	# no supported
	_volume = None
	log.warning("AudioUtilities getSpeaker not supported on this system")


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


def getSpeakerVolume():
	if _volume is None:
		return None
	volumeLevel = _volume.GetMasterVolumeLevelScalar()
	return volumeLevel


def setSpeakerVolume(withMin=False):
	from ..settings import _addonConfigManager
	""" Unmute speaker volume if it's mute
	and set level volume to configured volume
	if it's lowest than configured min volume level """
	if _volume is None:
		return False
	volume = _volume
	volumeLevel = volume.GetMasterVolumeLevelScalar()
	mute = volume.GetMute()
	if mute:
		volume.SetMute(0, None)
		log.warning(" Unmute master volume")
	minLevel = float(_addonConfigManager .getMinMasterVolumeLevel())/100
	if not withMin or (withMin and volumeLevel <= minLevel):
		level = float(_addonConfigManager .getMasterVolumeLevel())/100
		volume.SetMasterVolumeLevelScalar(level, None)
		log.warning(
			"Master volume is set to %s" % _addonConfigManager .getMasterVolumeLevel())
	return True


def getNVDAVolume():
	try:
		sessions = AudioUtilities.GetAllSessions()
	except Exception:
		# no supported
		log.warning("AudioUtilities getAllCessions not supported on this system")
		return False
	for session in sessions:
		try:
			name = session.Process.name()
		except Exception:
			continue
		if name.lower() == "nvda.exe":
			volume = session.SimpleAudioVolume
			volumeLevel = volume.GetMasterVolume()
			return volumeLevel
	return None


def setNVDAVolume(withMin=False):
	from ..settings import _addonConfigManager
	try:
		sessions = AudioUtilities.GetAllSessions()
	except Exception:
		# no supported
		log.warning("AudioUtilities getAllCessions not supported on this system")
		return False
	for session in sessions:
		try:
			name = session.Process.name()
		except Exception:
			continue
		if name.lower() == "nvda.exe":
			volume = session.SimpleAudioVolume
			mute = volume.GetMute()
			if mute:
				volume.SetMute(not mute, None)
				log.warning("Unmute NVDA volume")
			volumeLevel = volume.GetMasterVolume()
			minLevel = float(_addonConfigManager.getMinNVDAVolumeLevel())/100
			if not withMin or (withMin and volumeLevel <= minLevel):
				levels = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
				index = _addonConfigManager.getNVDAVolumeLevel()/10
				level = float(levels[int(index)])
				volume.SetMasterVolume(level, None)
				log.warning("NVDA volume is set to %s" % level)
			return True
	return False


def announceAppVolumeLevel(appVolumeLevel):
	from ..settings import toggleReportVolumeChangeAdvancedOption, toggleAppVolumeLevelAnnouncementInPercentAdvancedOption
	if not toggleReportVolumeChangeAdvancedOption(False):
		return
	if _volume is None:
		speakersVolume = 1.0
	else:
		volume = _volume
		speakersVolume = volume.GetMasterVolumeLevelScalar()
	if toggleAppVolumeLevelAnnouncementInPercentAdvancedOption(False):
		level = int(appVolumeLevel*100)
		# Translators: part of message for announcement of volume level in percent.
		percentMsg = _("percent")
		msg = "%s %s %s" % (volumeMsg, level, percentMsg)
	else:
		level = int(round((appVolumeLevel*100)*speakersVolume))
		msg = "%s %s" % (volumeMsg, level)
	ui.message(msg)


def changeFocusedAppVolume(appName=None, action="increase", value=None):
	global _previousAppVolumeLevel
	if appName is None:
		focus = api.getFocusObject()
		appName = appModuleHandler.getAppNameFromProcessID(focus.processID, True)
	if appName == "nvda.exe":
		ui.message(_("Unavailable for NVDA"))
		return
	from ..settings import _addonConfigManager
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
		if name.lower() == appName.lower():
			volume = session.SimpleAudioVolume
			mute = volume.GetMute()
			if mute:
				volume.SetMute(not mute, None)
			offset = 0.01*_addonConfigManager.getVolumeChangeStepLevel()
			curLevel = volume.GetMasterVolume()
			if action == "increase":
				level = min(1, curLevel+offset)
			elif action == "decrease":
				level = max(0, curLevel-offset)
			elif action == "max":
				level = 1.0
			elif action == "min":
				level = 0.0
			elif action == "set":
				level = float(value)/100
			else:
				# no action
				log.warning("changeFocusedAppVolume: %s action is not known" % action)
				return
			_previousAppVolumeLevel[appName.lower()] = curLevel
			volume.SetMasterVolume(level, None)
			level = volume.GetMasterVolume()
			announceAppVolumeLevel(level)
			log.warning("%s volume is set to %s" % (appName, level))
			return


def changeSpeakersVolume(action="increase", value=None):
	global _previousSpeakersVolumeLevel
	from ..settings import (
		_addonConfigManager,
		toggleReportVolumeChangeAdvancedOption)
	if _volume is None:
		return False
	volume = _volume
	mute = volume.GetMute()
	if mute:
		volume.SetMute(not mute, None)
		log.warning(" Unmute master volume")
	offset = 0.01*_addonConfigManager.getVolumeChangeStepLevel()
	minLevel = float(_addonConfigManager .getMinMasterVolumeLevel())/100
	speakersVolume = volume.GetMasterVolumeLevelScalar()
	if action == "increase":
		level = min(1, speakersVolume + offset)
	elif action == "decrease":
		level = max(minLevel, speakersVolume - offset)
	elif action == "max":
		level = 1.0
	elif action == "min":
		level = loat(_addonConfigManager .getMinMasterVolumeLevel())/100
	elif action == "set":
		minimumLevel = _addonConfigManager .getMinMasterVolumeLevel()
		if value < minimumLevel:
			# Translators: message to user to indicate command reject.
			ui.message(_("Impossible, the volume level cannot be lower than the configured recovery threshold equal to %s") % minimumLevel)
			return
		level = float(value)/100
	else:
		log.warning("changeSpeakerVolume: %s action is not known" % action)
		return
	_previousSpeakersVolumeLevel = speakersVolume
	msg = "%s %s" % (volumeMsg, int(round(level*100)))
	volume.SetMasterVolumeLevelScalar(level, None)

	if toggleReportVolumeChangeAdvancedOption(False):
		ui.message(msg)
		log.warning("Master volume is set to %s" % level)
	return True


def setFocusedAppVolumeToPreviousLevel():
	focus = api.getFocusObject()
	appName = appModuleHandler.getAppNameFromProcessID(focus.processID, True)
	level = _previousAppVolumeLevel.get(appName.lower())
	if level is None:
		return
	level = int(level*100)
	changeFocusedAppVolume(appName=appName, action="set", value=level)


def setSpeakersVolumeLevelToPreviousLevel():
	level = _previousSpeakersVolumeLevel
	if level is None:
		return
	level = int(level*100)
	changeSpeakersVolume(action="set", value=level)
