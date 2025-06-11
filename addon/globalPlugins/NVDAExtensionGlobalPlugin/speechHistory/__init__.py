# globalPlugins\NVDAExtensionGlobalPlugin\speechHistory\__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2025 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
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
_NVDASpeak = None
_NVDASpeakSpelling = None


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
		while len(text):
			if text[-1] not in ["\n", "\r"]:
				break
			text = text[:-1]

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


def initialize():
	from . import speechHistoryPatches
	from ..settings import isInstall
	from ..settings.addonConfig import FCT_SpeechHistory, FCT_TemporaryAudioDevice
	global _NVDASpeak, _NVDASpeakSpelling
	global _speechRecorder
	if _speechRecorder is not None:
		return
	if not isInstall(FCT_SpeechHistory) and not isInstall(FCT_TemporaryAudioDevice):
		return
	_speechRecorder = SpeechRecorderManager()
	speechHistoryPatches.patche(install=True)


def terminate():
	global _speechRecorder
	if _speechRecorder is None:
		return
	from . import speechHistoryPatches
	speechHistoryPatches.patche(install=False)
	_speechRecorder = None
