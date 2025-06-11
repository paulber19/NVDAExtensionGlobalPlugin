# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\temporaryOutputDevicePatches.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2024-2025 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


import addonHandler
from logHandler import log
import tones
import synthDriverHandler
import wx
import nvwave
from versionInfo import version_year, version_major
NVDAVersion = [version_year, version_major]
import synthDrivers.oneCore
from .waves import getModifiedNVDAWaveFile
from .audioUtils import (
	isWasapiUsed,
	getOutputDevice, setOutputDevice)
from ..settings.addonConfig import FCT_TemporaryAudioDevice
from ..settings import (
	toggleAllowNVDATonesVolumeAdjustmentAdvancedOption,
	toggleAllowNVDASoundGainModificationAdvancedOption,
	isInstall
)
import os
import sys
_curAddon = addonHandler.getCodeAddon()
sharedPath = os.path.join(_curAddon.path, "shared")
sys.path.append(sharedPath)
from messages import warn
del sys.path[-1]
del sys.modules["messages"]


addonHandler.initTranslation()


# to save original NVDA patched functions
_NVDAOneCoreSynthDriverMaybeInitPlayer = None
_nvdaPlayWaveFile = None
_NVDATonesInitialize = None
_NVDASetSynth = None


def _myOneCoreSynthDriverMaybeInitPlayer(*args, **kwargs):
	"""
	synthDrivers.oneCore.SynthDriver._maybeInitPlayer must be patched to use temporary output device.
	this method use config.conf["speech"]["outputDevice"] to get the output device directly
	to reinitialize player after synthetizer initialization.
	To set temporary output device,"
	" we want change the output device of a synthetizer with no configuration change.
	Since NVDA 2025.1, "speech" must be replaced by "audio"
	currentOutputDevice= config.conf["speech"]["outputDevice"]
	config.conf["speech"]["outputDevice"] = temporaryOutputDevice
	synthDriverHandler .setSynth(getSynth().name)
	config.conf["speech"]["outputDevice"] = currentOutputDevice
	After synthezer initialization (setsynth), the _audioOutputDevice variable is the output device.
	But this method continue to use config.conf["speech"]["outputDevice"]
	We need to patch this method so that it uses _audioOutputDevice variable instead
	"""
	global _NVDAOneCoreSynthDriverMaybeInitPlayer
	from synthDriverHandler import _audioOutputDevice
	currentOutputDevice = getOutputDevice()
	setOutputDevice(_audioOutputDevice)
	_NVDAOneCoreSynthDriverMaybeInitPlayer(*args, **kwargs)
	setOutputDevice(currentOutputDevice)


def _myPlayWaveFile(fileName, *args, **kwargs):
	"""
	nvwave.playWaveFile must be patched to:
		- use temporary output device instead of config.conf["speech"]["outputDevice"]
		- use modified nvda wave files instead of original nvda wave files
	"""
	from synthDriverHandler import _audioOutputDevice
	newFileName = getModifiedNVDAWaveFile(fileName)
	if newFileName != fileName:
		log.debug("%s file has been replaced by %s modified file" % (fileName, newFileName))
	outputDevice = getOutputDevice()
	setOutputDevice(_audioOutputDevice)
	_nvdaPlayWaveFile(newFileName, *args, **kwargs)
	setOutputDevice(outputDevice)
	return


def _myTonesInitialize():
	"""
	NVDA tones initialize must be patched to use temporary output device instead of:
	config.conf["speech"]["outputDevice"]
	or for nvda versions >= 2025.1
	config.conf["audio"]["outputDevice"]

	"""
	from .temporaryOutputDevice import getTemporaryOutputDevice
	currentOutputDevice = getOutputDevice()
	temporaryOutputDevice = getTemporaryOutputDevice()
	if temporaryOutputDevice:
		device = temporaryOutputDevice[0] if NVDAVersion < [2025, 1] else temporaryOutputDevice[1]
		setOutputDevice(device)
	log.debug("myTonesInitialize: device= %s" % getOutputDevice())
	_NVDATonesInitialize()
	setOutputDevice(currentOutputDevice)


def _mySetSynth(*args, **kwargs):
	"""
	synthDriverHandler.setSynth must be patched to use temporary output device instead of:
	config.conf["speech"]["outputDevice"]
	or for nvda versions >= 2025.1
	config.conf["audio"]["outputDevice"]
	"""
	log.debug("mySetSynth")
	currentOutputDevice = getOutputDevice()
	from .temporaryOutputDevice import getTemporaryOutputDevice
	temporaryOutputDevice = getTemporaryOutputDevice()
	if temporaryOutputDevice:
		device = temporaryOutputDevice[0] if NVDAVersion < [2025, 1] else temporaryOutputDevice[1]
		setOutputDevice(device)
	res = _NVDASetSynth(*args, **kwargs)
	setOutputDevice(currentOutputDevice)
	return res


def _patcePlayWaveFile(install=True):
	global _nvdaPlayWaveFile
	if install:
		needPatch = (
			(not isWasapiUsed() and toggleAllowNVDATonesVolumeAdjustmentAdvancedOption(False))
			or toggleAllowNVDASoundGainModificationAdvancedOption(False)
			or isInstall(FCT_TemporaryAudioDevice)
		)
		if not needPatch:
			return
		# install patch
		_nvdaPlayWaveFile = nvwave.playWaveFile
		if nvwave.playWaveFile.__module__ != "nvwave":
			log.warning(
				"Incompatibility: nvwave.playWaveFile method has also been patched probably by another add-on: %s."
				"There is a risk of malfunction" % nvwave.playWaveFile.__module__)
		if nvwave.WavePlayer.open.__module__ == "globalPlugins.soundSplitter":
			log.debug("Potential incompatibility: nvwave.WavePlayer function patched by soundSplitter add-on")
			wx.CallAfter(
				warn,
				# Translators: message to warn the user of a potential incompatibility with the soundSplitter add-on
				_(
					"The soundSplitter add-on may cause the add-on to malfunction. It is better to uninstall it."),
				# Translators: warning dialog title
				_("Warning"),
			)
		nvwave.playWaveFile = _myPlayWaveFile
		log.debug(
			"To allow use of temporary output device or NVDA file gain modification,"
			" nvwave.playWaveFile has been patched by: %s of %s module "
			% (_myPlayWaveFile.__name__, _myPlayWaveFile.__module__))
	else:
		# remove patch
		if _nvdaPlayWaveFile is not None:
			nvwave.playWaveFile = _nvdaPlayWaveFile
			_nvdaPlayWaveFile = None


def patche(install=True):
	if not install:
		removePatch()
		return
	# patche playWaveFile to use temporary audio and modified sound files
	_patcePlayWaveFile(install=True)
	if not isInstall(FCT_TemporaryAudioDevice):
		return
	# patche synthDrivers.oneCore.SynthDriver._maybeInitPlayer
	global _NVDAOneCoreSynthDriverMaybeInitPlayer
	_NVDAOneCoreSynthDriverMaybeInitPlayer = synthDrivers.oneCore.SynthDriver._maybeInitPlayer
	if synthDrivers.oneCore.SynthDriver._maybeInitPlayer .__module__ != "synthDrivers.oneCore":
		log.warning(
			"Incompatibility: synthDrivers.oneCore.SynthDriver._maybeInitPlayer method has also been patched"
			" probably by another add-on:"
			" %s. There is a risk of malfunction"
			% synthDrivers.oneCore.SynthDriver._maybeInitPlayer.__module__)
	synthDrivers.oneCore.SynthDriver._maybeInitPlayer = _myOneCoreSynthDriverMaybeInitPlayer
	log.debug(
		"To allow use of temporary output device,"
		" synthDrivers.oneCore.SynthDriver._maybeInitPlayer has been patched by: %s of %s module"
		% (_myOneCoreSynthDriverMaybeInitPlayer.__name__, _myOneCoreSynthDriverMaybeInitPlayer.__module__))
	# patche tones.initialize
	global _NVDATonesInitialize
	_NVDATonesInitialize = tones.initialize
	if tones.initialize.__module__ != "tones":
		log.warning(
			"Incompatibility: tones.initialize method has also been patched probably by another add-on: %s."
			"There is a risk of malfunction" % tones.initialize .__module__)
	tones.initialize = _myTonesInitialize
	log.debug(
		"To allow NVDA tones to use temporary audio device,"
		" tones.initialize function has been patched by %s function of %s module"
		% (_myTonesInitialize.__name__, _myTonesInitialize.__module__))
	tones.terminate()
	tones.initialize()
	# patche synthDriverHandler .setSynth
	global _NVDASetSynth
	_NVDASetSynth = synthDriverHandler .setSynth
	if synthDriverHandler .setSynth.__module__ != "synthDriverHandler":
		log.warning(
			"Incompatibility: synthDriverHandler .setSynth method has also been patched "
			"probably by another add-on: %s."
			"There is a risk of malfunction" % synthDriverHandler .setSynth._maybeInitPlayer.__module__)
	synthDriverHandler .setSynth = _mySetSynth
	log.debug(
		"To allow NVDA set synth to use temporary audio device,"
		" synthDriverHandler.setSynth unction has been patched by %s function of %s module"
		% (synthDriverHandler .setSynth .__name__, synthDriverHandler .setSynth .__module__))


def removePatch():
	_patcePlayWaveFile(install=False)
	global _NVDAOneCoreSynthDriverMaybeInitPlayer
	if _NVDAOneCoreSynthDriverMaybeInitPlayer is not None:
		synthDrivers.oneCore.SynthDriver._maybeInitPlayer = _NVDAOneCoreSynthDriverMaybeInitPlayer
		_NVDAOneCoreSynthDriverMaybeInitPlayer = None
	global _NVDATonesInitialize
	if _NVDATonesInitialize is not None:
		tones.initialize = _NVDATonesInitialize
		_NVDATonesInitialize = None
	global _NVDASetSynth
	if _NVDASetSynth is not None:
		synthDriverHandler .setSynth = _NVDASetSynth
		_NVDASetSynth = None
