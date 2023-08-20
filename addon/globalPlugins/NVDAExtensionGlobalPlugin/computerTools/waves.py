# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\waves.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from logHandler import log
import os
import globalVars
import sys
from ..utils.py3Compatibility import getUtilitiesPath
utilitiesPath = getUtilitiesPath()
pydubPath = os.path.join(utilitiesPath, "pydub")
sysPath = sys.path
sys.path.append(utilitiesPath)
sys.path.append(pydubPath)
import pydub
sys.path = sysPath


# NVDA application path
_NVDAAppPath = os.getcwd()

# modified waves directory
_addon = addonHandler.getCodeAddon()
_modifiedWavesPath = os.path.join(
	os.path.abspath(globalVars.appArgs.configPath),
	"%s-NVDAWaves" % _addon.manifest['name']
)


def getSoundNameFromID(soundID):
	return soundID.split("_")[-1]


def getFileNameIdentification(fileName):
	baseName = os.path.basename(fileName)
	if isNVDAWaveFile(fileName):
		id = "NVDAWaves_%s" % baseName
	elif isAddonSoundFile(fileName):
		temp = fileName[len(_addon.path) + 1:].split("\\")[:-1]
		id = "%s%s_%s" % (_addon.manifest["name"], "".join(temp), baseName)
	else:
		id = None
	return id


def getModifiedWavesPath():
	return _modifiedWavesPath


def getModifiedNVDAWaveFile(fileName):
	from ..settings import (
		toggleAllowNVDATonesVolumeAdjustmentAdvancedOption,
		toggleAllowNVDASoundGainModificationAdvancedOption
	)
	if (
		not toggleAllowNVDATonesVolumeAdjustmentAdvancedOption(False)
		or not toggleAllowNVDASoundGainModificationAdvancedOption(False)
	):
		return fileName
	if not isNVDAWaveFile(fileName) and not isAddonSoundFile(fileName):
		return fileName
	if not os.path.exists(_modifiedWavesPath):
		return fileName
	soundID = getFileNameIdentification(fileName)
	newFileName = os.path.join(_modifiedWavesPath, soundID)
	if os.path.exists(newFileName):
		return newFileName
	return fileName


def isNVDAWaveFile(fileName):
	NVDAWavesPath = os.path.join(_NVDAAppPath, "waves")
	return fileName.startswith(NVDAWavesPath)


def isAddonSoundFile(fileName):
	addonSoundsPath = os.path.join(_addon.path, "sounds")
	return addonSoundsPath in fileName


def applyGain(gain, source, target=None):
	try:
		song = pydub.AudioSegment.from_wav(source)
		mod = song + gain
		if target:
			mod.export(target, format="wav")
		return mod
	except Exception:
		log.error("Cannott modify gain: gain =  %s, source = %s, target = %s" % (gain, source, target))
	return None


def exportSong(song, target):
	if not target:
		return False
	try:
		song.export(target, format="wav")
		return True
	except Exception:
		log.error("Cannot exporte to %s" % target)
	return False
