# globalPlugins\NVDAExtensionGlobalPlugin\speechHistory\speechHistoryPatches.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2024 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

from logHandler import log
from speech import speech as speech
from ..settings import isInstall
from ..settings.addonConfig import FCT_SpeechHistory, FCT_TemporaryAudioDevice
from ..computerTools.temporaryOutputDevice import checkOutputDeviceChange
from ..speechHistory import getSpeechRecorder

# global variables to save original NVDA patched functions
_NVDASpeechSpeak = None
_NVDASpeecSpeakSpelling = None


def _mySpeechSpeak(sequence, *args, **kwargs):
	""" speech.speak must be patched to:
		- intercept and record the sequence to speak
		- redirect synthetizer and tones to temporary output device if there is
	"""
	log.debug("_mySpeechSpeak")
	# reset current output device if temporary output device is set and output device has changed
	checkOutputDeviceChange()
	_NVDASpeechSpeak(sequence, *args, **kwargs)
	if isInstall(FCT_SpeechHistory):
		text = " ".join([x for x in sequence if isinstance(x, str)])
		getSpeechRecorder().record(text)


def _mySpeechSpeakSpelling(text, *args, **kwargs):
	""" speech.speakSpelling must be patched to:
		- intercept and record the sequence to speak
		- redirect synthetizer and tones to temporary output device if there is
	"""
	log.debug("_mySpeechSpeakSpelling")
	# reset current output device if temporary output device is set and output device has changed
	checkOutputDeviceChange()
	_NVDASpeechSpeakSpelling(text, *args, **kwargs)
	if isInstall(FCT_SpeechHistory):
		getSpeechRecorder().record(text)


def patche(install=True):
	if not install:
		removePatch()
		return
	global _NVDASpeechSpeak, _NVDASpeechSpeakSpelling
	if not isInstall(FCT_SpeechHistory) and not isInstall(FCT_TemporaryAudioDevice):
		return
	# patche speech.speak
	_NVDASpeechSpeak = speech.speak
	if speech.speak.__module__ != "speech.speech":
		log.warning(
			"Incompatibility: speech.speech.speak method has also been patched probably by another add-on: %s."
			"There is a risk of malfunction" % speech.speak.__module__)
	speech.speak = _mySpeechSpeak
	log.debug(
		"For speech history functionality,"
		" speech.speech.speak method has been replaced by %s method of %s module" % (
			_mySpeechSpeak.__name__, _mySpeechSpeak.__module__)
	)
	# patce speech.speakSpelling
	_NVDASpeechSpeakSpelling = speech.speakSpelling
	if speech.speakSpelling .__module__ != "speech.speech":
		log.warning(
			"Incompatibility: speech.speech.speakSpelling method has also been atched probably by another add-on: %s."
			"There is a risk of malfunction" % speech.speakSpelling .__module__)
	speech.speakSpelling = _mySpeechSpeakSpelling
	log.debug(
		"For speech history functionality,"
		" speech.speech.speakSpelling method has been replaced by %s method of %s module" % (
			_mySpeechSpeakSpelling.__name__, _mySpeechSpeakSpelling.__module__)
	)


def removePatch():
	global _NVDASpeechSpeak, _NVDASpeechSpeakSpelling
	if _NVDASpeechSpeak:
		speech.speak = _NVDASpeechSpeak
		_NVDASpeechSpeak = None
	if _NVDASpeechSpeakSpelling:
		speech.speakSpelling = _NVDASpeechSpeakSpelling
		_NVDASpeechSpeakSpelling = None
