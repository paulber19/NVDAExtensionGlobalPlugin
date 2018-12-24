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
from ..settings import toggleSpeechRecordWithNumberOption

MAX_RECORD = 200
_speechRecorder = None
_isActive = False
_oldSpeak = None
_oldSpeakSpelling = None

def mySpeak(sequence, *args, **kwargs):
	text = "".join([x for x in sequence if isinstance(x, basestring)])
	_speechRecorder.record(text)
	_oldSpeak(sequence, *args, **kwargs)

def mySpeakSpelling(text, *args, **kwargs):
	_speechRecorder.record(text)
	_oldSpeakSpelling(text, *args, **kwargs)
	
def initialize():
	global _isActive,_oldSpeak, _oldSpeakSpelling, _speechRecorder
	if _isActive :
		return
	_speechRecorder = SpeechRecorderManager()
	_oldSpeak = speech.speak
	speech.speak = mySpeak
	_oldSpeakSpelling = speech.speakSpelling
	speech.speakSpelling = mySpeakSpelling
	_isActive = True

def terminate():
	global _isActive,_oldSpeak, _oldSpeakSpelling, _speechRecorder
	if not _isActive: return
	speech.speak = _oldSpeak
	_oldSpeak = None
	speech.speakSpelling = _oldSpeakSpelling
	_oldSpeakSpelling = None
	_speechRecorder = None
	_isActive = False
def isActive():
	return _isActive
def getSpeechRecorder():
	return _speechRecorder

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
		text = ""
		for index in range(0, len(self._speechHistory)):
			s = self._speechHistory[index]
			if toggleSpeechRecordWithNumberOption(False):
				text = u"{index}: {annonce}\r\n{text}".format(index = index+1, annonce = s, text = text)
			else:
				text = u"{annonce}\r\n{text}".format(annonce = s, text = text)			
		# Translators:  title of informations  dialog.
		dialogTitle = _("Speech history")
		# Translators: label of information area.
		informationLabel = _("Records:")
		InformationDialog.run(None, dialogTitle, informationLabel, text)
		