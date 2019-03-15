#NVDAExtensionGlobalPlugin/speechHistory/__init__.py
#A part of NVDAExtensionGlobalPlugin add-on
#Copyright (C) 2016  paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import addonHandler
addonHandler.initTranslation()
import speech
import ui
import api
from ..utils.informationDialog import InformationDialog
from ..settings import toggleSpeechRecordWithNumberOption, toggleSpeechRecordInAscendingOrderOption
from ..utils.py3Compatibility import baseString, _unicode

# constants
MAX_RECORD = 200
# global variables
_speechRecorder = None
_oldSpeak = speech.speak
_oldSpeakSpelling = speech.speakSpelling

def mySpeak(sequence, *args, **kwargs):
	text = "".join([x for x in sequence if isinstance(x, baseString)])
	_speechRecorder.record(text)
	_oldSpeak(sequence, *args, **kwargs)

def mySpeakSpelling(text, *args, **kwargs):
	_speechRecorder.record(text)
	_oldSpeakSpelling(text, *args, **kwargs)
	
def initialize():
	global _speechRecorder
	if _speechRecorder  is not None: return
	_speechRecorder = SpeechRecorderManager()
	speech.speak = mySpeak
	speech.speakSpelling = mySpeakSpelling

def terminate():
	global _speechRecorder
	if _speechRecorder  is  None: return
	speech.speak = _oldSpeak
	speech.speakSpelling = _oldSpeakSpelling
	_speechRecorder = None

def getSpeechRecorder():
	return _speechRecorder
def isActive():
	return _speechRecorder is not None

class SpeechRecorderManager(object):
	def __init__ (self):
		self._speechHistory = []
		self._lastSpeechHistoryReportIndex = None
		self._onMonitoring = True
		
	
	def record(self, text):
		if not text or not self._onMonitoring:
			return
		text = text.replace("\r","")
		text = text.replace("\n","")
		if len(text.strip()) == 0:
			return
		self._speechHistory.append(text)
		if len(self._speechHistory) >MAX_RECORD:
			self._speechHistory.pop(0)
		self._lastSpeechHistoryReportIndex = len(self._speechHistory)-1
		
	def reportSpeechHistory(self, position, toClip = False):
		oldOnMonitoring = self._onMonitoring
		self._onMonitoring = False
		index = self._lastSpeechHistoryReportIndex
		if position == "previous" and index >0:
			index -= 1
		elif position == "next" and index < len(self._speechHistory) -1:
			index+= 1
		if (position != "current") and (index == self._lastSpeechHistoryReportIndex):
			# Translators: message presented when there is no more record in speech history.
			speech.speakMessage(_("No more recorded vocal announce"))
			# Translators: message presented when the record is on the top or bottom of the speech history.
			msg = _("Oldest recorded announce") if (position == "previous") else _("Last recorded announce")
			ui.message("%s: %s" %(msg,self._speechHistory[index]))
		
		else:
			self._lastSpeechHistoryReportIndex = index
			text= self._speechHistory[index]
			ui.message(text)

			if toClip and position == "current":
				if api.copyToClip(text):
					# Translators: message presented when the text is copied to the clipboard.
					speech.speakMessage(_("Copied to clipboard"))
				else:
					# Translators: message presented when the text cannot be copied to the clipboard.
					speech.speakMessage(_("Cannot copy to clipboard"))
			
		self._onMonitoring = oldOnMonitoring
		
	def displaySpeechHistory(self):
		text = []
		for index in range(0, len(self._speechHistory)):
			s = self._speechHistory[index]
			if toggleSpeechRecordWithNumberOption(False):
				text.append( _unicode(" {index}: {annonce}").format(index = index+1, annonce = s))
			else:
				text .append(_unicode(s))
		if not toggleSpeechRecordInAscendingOrderOption (False):
			text.reverse()
		text = "\r\n".join(text)

		# Translators:  title of informations  dialog.
		dialogTitle = _("Speech history")
		insertionPointOnLastLine = True if toggleSpeechRecordInAscendingOrderOption (False) else False
		# Translators: label of information area.
		informationLabel = _("Records:")
		InformationDialog.run(None, dialogTitle, informationLabel, text, insertionPointOnLastLine)
		