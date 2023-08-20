# globalPlugins\NVDAExtensionGlobalPlugin\speechHistory\__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from logHandler import log
from speech import speech as speech
import tones
import ui
import api
from ..utils.informationDialog import InformationDialog
from ..utils.NVDAStrings import NVDAString
from ..settings import toggleSpeechRecordWithNumberOption, toggleSpeechRecordInAscendingOrderOption

addonHandler.initTranslation()

# constants
MAX_RECORD = 200
# global variables
_speechRecorder = None
_oldSpeak = None
_oldSpeakSpelling = None


def mySpeak(sequence, *args, **kwargs):
	_oldSpeak(sequence, *args, **kwargs)
	text = " ".join([x for x in sequence if isinstance(x, str)])
	_speechRecorder.record(text)


def mySpeakSpelling(text, *args, **kwargs):
	_oldSpeakSpelling(text, *args, **kwargs)
	_speechRecorder.record(text)


def initialize():
	global _speechRecorder, _oldSpeak, _oldSpeakSpelling
	if _speechRecorder is not None:
		return
	_speechRecorder = SpeechRecorderManager()
	_oldSpeak = speech.speak
	if speech.speak.__module__ != "speech.speech":
		log.warning(
			"Incompatibility: speech.speech.speak method has been also patched probably by another add-on: %s."
			"There is a risk of malfunction" % speech.speak.__module__)
	_oldSpeakSpelling = speech.speakSpelling
	if speech.speakSpelling.__module__ != "speech.speech":
		log.warning(
			"Incompatibility: speech.speech.speakSpelling method has been also patched probably by another add-on: %s."
			"There is a risk of malfunction" % speech.speakSpelling.__module__)
	speech.speak = mySpeak
	log.debug(
		"speech.speech.speak method has been replaced by %s method of %s module" % (
			mySpeak.__name__, mySpeak.__module__)
	)
	speech.speakSpelling = mySpeakSpelling
	log.debug(
		"speech.speech.speakSpelling  method has been replaced by %s method of %s module" % (
			mySpeakSpelling.__name__, mySpeakSpelling.__module__)
	)
	log.warning("speechHistory initialized")


def terminate():
	global _speechRecorder
	if _speechRecorder is None:
		return
	speech.speak = _oldSpeak
	speech.speakSpelling = _oldSpeakSpelling
	_speechRecorder = None


def getSpeechRecorder():
	return _speechRecorder


def isActive():
	return _speechRecorder is not None


class SpeechRecorderManager(object):
	def __init__(self):
		self._speechHistory = []
		self._lastSpeechHistoryReportIndex = None
		self._onMonitoring = True

	def record(self, text):
		if not text or not self._onMonitoring:
			return
		text = text.replace("\r", "")
		text = text.replace("\n", "")
		if len(text.strip()) == 0:
			return
		self._speechHistory.append(text)
		if len(self._speechHistory) > MAX_RECORD:
			self._speechHistory.pop(0)
		self._lastSpeechHistoryReportIndex = len(self._speechHistory) - 1

	def reportSpeechHistory(self, position, toClip=False):
		index = self._lastSpeechHistoryReportIndex
		if index is None:
			return
		oldOnMonitoring = self._onMonitoring
		self._onMonitoring = False
		if position == "previous" and index > 0:
			index -= 1
		elif position == "next" and index < len(self._speechHistory) - 1:
			index += 1
		if (position != "current") and (index == self._lastSpeechHistoryReportIndex):
			tones.beep(100, 40)
		self._lastSpeechHistoryReportIndex = index
		text = self._speechHistory[index]
		if not toClip:
			ui.message(text)
			self._onMonitoring = oldOnMonitoring
			return
		if not api.copyToClip(text):
			# Translators: Presented when unable to copy to the clipboard because of an error.
			ui.message(NVDAString("Unable to copy"))
		# Translators: message to user to report copy to clipboard
		ui.message(_("{0} copied to clipboard") .format(text))
		self._onMonitoring = oldOnMonitoring

	def displaySpeechHistory(self):
		text = []
		for index in range(0, len(self._speechHistory)):
			s = self._speechHistory[index]
			if toggleSpeechRecordWithNumberOption(False):
				text.append(str(" {index}: {annonce}").format(
					index=index + 1, annonce=s))
			else:
				text .append(str(s))
		if not toggleSpeechRecordInAscendingOrderOption(False):
			text.reverse()
		text = "\r\n".join(text)
		# Translators: title of informations dialog.
		dialogTitle = _("Speech history")
		if toggleSpeechRecordInAscendingOrderOption(False):
			insertionPointOnLastLine = True
		else:
			insertionPointOnLastLine = False
		# Translators: label of information area.
		informationLabel = _("Records:")
		InformationDialog.run(
			None, dialogTitle, informationLabel, text, insertionPointOnLastLine)
