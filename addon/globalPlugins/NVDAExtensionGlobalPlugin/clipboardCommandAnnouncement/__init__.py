# globalPlugins\NVDAExtensionGlobalPlugin\clipboardCommandAnnouncement\__init__.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2025 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from logHandler import log
import wx
import api
import textInfos
import speech
import speech.speech
from speech.priorities import SpeechPriority
import ui
import time
from controlTypes.role import Role
from controlTypes.state import State
import editableText
import NVDAObjects.behaviors
import config
from characterProcessing import SymbolLevel
from IAccessibleHandler import accNavigate
from oleacc import (
	STATE_SYSTEM_SELECTED,
	NAVDIR_PREVIOUS, NAVDIR_NEXT,
)
import UIAHandler
from NVDAObjects import NVDAObject
from NVDAObjects.UIA import UIA
import queueHandler
import eventHandler
import core
import contentRecog.recogUi
import unicodedata
from ..utils.nvdaInfos import NVDAVersion
from ..utils.NVDAStrings import NVDAString
from ..utils import delayScriptTaskWithDelay, stopDelayScriptTask, clearDelayScriptTask
from ..settings import isInstall
from ..settings.addonConfig import (
	FCT_ClipboardCommandAnnouncement,
)
from ..utils.keyboard import getEditionKeyCommands
from . import clipboard
import os
import sys
_curAddon = addonHandler.getCodeAddon()
sharedPath = os.path.join(_curAddon.path, "shared")
sys.path.append(sharedPath)
from negp_messages import confirm_YesNo, ReturnCode
del sys.path[-1]

addonHandler.initTranslation()

# Translators: message to the user on cut command activation.
_msgCut = _("Cut")
# Translators: message to the user on paste command activation.
_msgPaste = _("Paste")
# Translators: message to the user on copy command activation.
_msgCopy = _("Copy")
# Translators: message to the user on undo command activation.
_msgUnDo = _("Undo")
# Translators: message to the user on select all command activation.
_msgSelectAll = _("Select all")

_clipboardCommands = {
	# associate function to: check selection, check clipboard change, check empty clipboard
	"undo": (_msgUnDo, False, False, False),
	"cut": (_msgCut, True, True, False),
	"copy": (_msgCopy, True, True, False),
	"paste": (_msgPaste, False, False, True)
}

# task timer
_GB_taskTimer = None

_taskDelay = None
NON_BREAKING_SPACE = 160


def getWExplorerStatusBarText(foreground):
	clientObject = UIAHandler.handler.clientObject
	foregroundElement = foreground.UIAElement
	element = foregroundElement.BuildUpdatedCache(
		UIAHandler.handler.baseCacheRequest)
	element = element.FindFirstBuildCache(
		UIAHandler.TreeScope_Descendants,
		clientObject.CreatePropertyCondition(
			UIAHandler.UIA_ControlTypePropertyId,
			UIAHandler.UIA_StatusBarControlTypeId),
		UIAHandler.handler.baseCacheRequest)
	if not element:
		return ""
	o = UIA(UIAElement=element)
	return o.getChild(1).firstChild.name


def getStatusBarText():
	"""Get the text from a status bar.
	@param obj: The status bar.
	@type obj: L{NVDAObjects.NVDAObject}
	@return: The status bar text.
	@rtype: str
	"""
	foreground = api.getForegroundObject()
	if foreground is None:
		return ""
	if (
		isinstance(foreground, UIA)
		and foreground.windowClassName == "CabinetWClass"
		and foreground.appModule.appName == "explorer"):
		return getWExplorerStatusBarText(foreground)
	obj = api.getStatusBar()
	if not obj:
		return ""
	text = obj.name or ""
	if text:
		text += " "
	return text + " ".join(
		chunk for child in obj.children[:-1] for chunk in (
			child.name, child.value) if chunk and isinstance(chunk, str) and not chunk.isspace())


# for delaying the report of position
_reportPositionTimer = None


def reportPosition(pos):
	global _reportPositionTimer
	if _reportPositionTimer:
		_reportPositionTimer.Stop()
	from ..settings.nvdaConfig import _NVDAConfigManager
	if not _NVDAConfigManager.toggleReportCurrentCaretPositionOption(False):
		return
	info = pos.copy()
	from ..utils.textInfo import getRealPosition, getLineInfoMessage
	position = getRealPosition(info)
	lineNumberMessage = getLineInfoMessage(info)

	def callback(position, lineNumberMessage):
		ui.message("%s %s" % (lineNumberMessage, str(position + 1)))
	_reportPositionTimer = wx.CallLater(500, callback, position, lineNumberMessage)


class RecogResultNVDAObjectEx (contentRecog.recogUi.RecogResultNVDAObject):
	def _caretMovementScriptHelper(
		self, gesture, unit, *args, **kwargs):
		curLevel = config.conf["speech"]["symbolLevel"]
		if unit == textInfos.UNIT_WORD:
			from ..settings.nvdaConfig import _NVDAConfigManager
			# save current symbol level
			symbolLevelOnWordCaretMovement = _NVDAConfigManager .getSymbolLevelOnWordCaretMovement()
			if symbolLevelOnWordCaretMovement is not None:
				config.conf["speech"]["symbolLevel"] = symbolLevelOnWordCaretMovement
		try:
			# also patched by NAO add-on  which return error when unit is sentence.
			super(RecogResultNVDAObjectEx, self)._caretMovementScriptHelper(
				gesture, unit, *args, **kwargs)
		except Exception:
			pass
		# restore current symbol level
		config.conf["speech"]["symbolLevel"] = curLevel


class EditableTextEx(editableText.EditableText):
	characterTyped = False
	_commandToScript = {
		"copy": "copyToClipboard",
		"cut": "cutAndCopyToClipboard",
		"paste": "pasteFromClipboard",
		"undo": "undo",
	}

	def initOverlayClass(self):
		if isInstall(FCT_ClipboardCommandAnnouncement):
			d = getEditionKeyCommands(self)
			for command in self._commandToScript:
				key = d[command]
				if key != "":
					self.bindGesture("kb:%s" % key, self._commandToScript[command])

	def getSelectionInfo(self):
		obj = api.getFocusObject()
		treeInterceptor = obj.treeInterceptor
		if hasattr(treeInterceptor, 'TextInfo') and not treeInterceptor.passThrough:
			obj = treeInterceptor
		try:
			info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
		except (RuntimeError, NotImplementedError):
			info = None
		if not info or info.isCollapsed:
			return None
		return info

	def script_copyToClipboard(self, gesture):
		def callback(gesture):
			clearDelayScriptTask()
			info = self.getSelectionInfo()
			if not info:
				# Translators: Reported when there is no text selected (for copying).
				ui.message(NVDAString("No selection"))
				gesture.send()
				return

			def finaly():
				cm = clipboard.ClipboardManager()
				gesture.send()
				time.sleep(0.1)
				if cm.changed():
					queueHandler.queueFunction(
						queueHandler.eventQueue,
						ui.message, _msgCopy)
			# to check if clipboard has changed, we, now (nvda 2023.2), must use a thread !!!!
			from threading import Thread
			Thread(target=finaly).start()

		stopDelayScriptTask()
		# to filter out too fast script calls while holding down the command gesture.
		delayScriptTaskWithDelay(80, callback, gesture)

	def script_cutAndCopyToClipboard(self, gesture):
		def callback():
			clearDelayScriptTask()
			if State.READONLY in self.states or (
				State.EDITABLE not in self.states
				and State.MULTILINE not in self.states):
				gesture.send()
				return
			info = self.getSelectionInfo()
			if not info:
				# Translators: Reported when there is no text selected (for copying).
				ui.message(NVDAString("No selection"))
				gesture.send()
				return
			cm = clipboard.ClipboardManager()
			gesture.send()
			time.sleep(0.1)
			if cm.changed():
				queueHandler.queueFunction(
					queueHandler.eventQueue,
					ui.message, _msgCut)

		stopDelayScriptTask()
		# to filter out too fast script calls while holding down the command gesture.
		delayScriptTaskWithDelay(80, callback)

	def script_pasteFromClipboard(self, gesture):
		def callback():
			clearDelayScriptTask()
			if (
				State.READONLY in self.states or (
				State.EDITABLE not in self.states
				and not State.MULTILINE)):
				gesture.send()
				return
			cm = clipboard.ClipboardManager()
			time.sleep(0.1)
			if cm.isEmpty:
				# Translators: message to report clipboard is empty
				ui.message(_("Clipboard is empty"))
				gesture.send()
				return
			queueHandler.queueFunction(
				queueHandler.eventQueue,
				ui.message, _msgPaste)
			queueHandler.queueFunction(
				queueHandler.eventQueue,
				gesture.send)
			wx.CallLater(400, self.reportCurrentLine)

		stopDelayScriptTask()
		# to filter out too fast script calls while holding down the command gesture.
		delayScriptTaskWithDelay(80, callback)

	def reportCurrentLine(self):
		import treeInterceptorHandler
		import controlTypes
		obj = api.getFocusObject()
		treeInterceptor = obj.treeInterceptor
		if (
			isinstance(treeInterceptor, treeInterceptorHandler.DocumentTreeInterceptor)
			and not treeInterceptor.passThrough
		):
			obj = treeInterceptor
		try:
			info = obj.makeTextInfo(textInfos.POSITION_CARET)
		except (NotImplementedError, RuntimeError):
			info = obj.makeTextInfo(textInfos.POSITION_FIRST)
		info.expand(textInfos.UNIT_LINE)
		ui.message(info.text)

	def script_undo(self, gesture):
		def callback():
			clearDelayScriptTask()
			if (
				State.READONLY in self.states or (
				State.EDITABLE not in self.states
				and not State.MULTILINE)):
				gesture.send()
				return
			queueHandler.queueFunction(
				queueHandler.eventQueue,
				ui.message, _msgUnDo)
			gesture.send()

		stopDelayScriptTask()
		# to filter out too fast script calls while holding down the command gesture.
		delayScriptTaskWithDelay(80, callback)

	def _caretScriptPostMovedHelper(self, speakUnit, gesture, info=None):
		# Forget the word currently being typed as the user has moved the caret somewhere else.
		speech.speech.clearTypedWordBuffer()
		super(EditableTextEx, self)._caretScriptPostMovedHelper(speakUnit, gesture, info)
		try:
			info = self.makeTextInfo(textInfos.POSITION_CARET)
		except Exception:
			return
		global _taskDelay
		if _taskDelay:
			_taskDelay.Stop()
		from ..textAnalysis.textAnalyzer import analyzeText
		_taskDelay = wx.CallLater(400, analyzeText, info, speakUnit)

	def _caretMovementScriptHelper(self, gesture, unit):
		# caret move but no character is typed. moving by arrow keys for exemple
		self.characterTyped = False
		try:
			info = self.makeTextInfo(textInfos.POSITION_CARET)
		except Exception:
			gesture.send()
			return
		bookmark = info.bookmark
		curLevel = config.conf["speech"]["symbolLevel"]
		if unit == textInfos.UNIT_WORD:
			from ..settings.nvdaConfig import _NVDAConfigManager
			symbolLevelOnWordCaretMovement = _NVDAConfigManager .getSymbolLevelOnWordCaretMovement()
			if symbolLevelOnWordCaretMovement is not None:
				config.conf["speech"]["symbolLevel"] = symbolLevelOnWordCaretMovement
		gesture.send()
		caretMoved, newInfo = self._hasCaretMoved(bookmark)
		if not caretMoved and self.shouldFireCaretMovementFailedEvents:
			eventHandler.executeEvent("caretMovementFailed", self, gesture=gesture)
		reportPosition(newInfo)
		self._caretScriptPostMovedHelper(unit, gesture, newInfo)
		config.conf["speech"]["symbolLevel"] = curLevel


class NVDAObjectExBase(NVDAObject):
	def _reportErrorInPreviousWord(self, typedWord=None):
		try:
			# self might be a descendant of the text control; e.g. Symphony.
			# We want to deal with the entire text, so use the caret object.
			info = api.getCaretObject().makeTextInfo(textInfos.POSITION_CARET)
			# This gets called for characters which might end a word; e.g. space.
			# The character before the caret is the word end.
			# The one before that is the last of the word, which is what we want.
			info.move(textInfos.UNIT_CHARACTER, -2)
			info.expand(textInfos.UNIT_CHARACTER)
		except Exception:
			# Focus probably moved.
			log.debugWarning("Error fetching last character of previous word", exc_info=True)
			return

		# Fetch the formatting for the last word to see if it is marked as a spelling error,
		# However perform the fetch and check in a future core cycle
		# To give the content control more time to detect and mark the error itself.
		# #12161: MS Word's UIA implementation certainly requires this delay.
		def _detection(ch):
			try:
				formatConfig = config.conf["documentFormatting"].copy()
				formatConfig["reportSpellingErrors"] = True
				fields = info.getTextWithFields(formatConfig=formatConfig)
			except Exception:
				log.debugWarning("Error fetching formatting for last character of previous word", exc_info=True)
				return
			for command in fields:
				if (
					isinstance(command, textInfos.FieldCommand)
					and command.command == "formatChange"
					and command.field.get("invalid-spelling")
				):
					break
			else:
				# No error.
				return False

			#  to warn  error depending user configuration: wav, beep, message or error reporting
			def warnSpellingError(typedWord):
				from ..settings import _addonConfigManager
				from ..speech.sayError import getErrorSpeechSequence, getErrorSoundSpeechSequence
				if _addonConfigManager.reportingSpellingErrorsByMessage():
					queueHandler.queueFunction(
						queueHandler.eventQueue,
						ui.message, NVDAString("spelling error"))
					return
				if _addonConfigManager.reportingSpellingErrorsByErrorReporting():
					if typedWord is None:
						seq = getErrorSoundSpeechSequence(typedWord)
					else:
						seq = getErrorSpeechSequence(typedWord)
				else:
					seq = getErrorSpeechSequence(reading=False)
				if seq:
					queueHandler.queueFunction(
						queueHandler.eventQueue,
						speech.speech.speak, seq, priority=SpeechPriority.NORMAL)

			warnSpellingError(typedWord)

		# #12161: MS Word's UIA implementation certainly requires this delay.
		core.callLater(50, _detection, typedWord)

	def _delayedReportErrorInPreviousWord(self, ch):
		typedWord = self.hasWordTyped(ch)
		self._reportErrorInPreviousWord(typedWord)

	def hasWordTyped(self, ch: str):
		typingIsProtected = api.isTypingProtected()
		if typingIsProtected:
			realChar = speech.speech.PROTECTED_CHAR
		else:
			realChar = ch
		curWordChars = speech.speech._curWordChars[:]
		if unicodedata.category(ch)[0] in "LMN":
			curWordChars.append(realChar)
		elif ch == "\b":
			# Backspace, so remove the last character from our buffer.
			del curWordChars[-1:]
		elif ch == "\u007f":
			# delete character produced in some apps with control+backspace
			pass
		elif len(curWordChars) > 0:
			return "".join(curWordChars)
		return None


class NVDAObjectEx(NVDAObjectExBase):

	def event_typedCharacter(self, ch: str):
		if (
			config.conf["keyboard"]["alertForSpellingErrors"]
			and (
			# Not alpha, apostrophe or control.
				ch.isspace() or (ch >= " " and ch not in "'\x7f" and not ch.isalpha())
			)
		):
			# Reporting of spelling errors is enabled and this character ends a word.
			self._delayedReportErrorInPreviousWord(ch)
		self.NVDAObject_event_typedCharacter(ch)

	def NVDAObject_event_typedCharacter(self, ch):
		from ..settings.nvdaConfig import _NVDAConfigManager
		if not (ch.isalnum() or ch.isspace()):
			typingEchoMode = config.conf["keyboard"]["speakTypedCharacters"]
			if _NVDAConfigManager.toggleSpeakAlphaNumCharsOption(False):
				if NVDAVersion < [2025, 1]:
					# for nvda versions < 2025.1
					config.conf["keyboard"]["speakTypedCharacters"] = True
				else:
					# for nvda versions >= 2025.1
					from config.configFlags import TypingEcho
					config.conf["keyboard"]["speakTypedCharacters"] = TypingEcho.ALWAYS.value
			speech.speakTypedCharacters(ch)
			config.conf["keyboard"]["speakTypedCharacters"] = typingEchoMode
		else:
			speech.speakTypedCharacters(ch)
		import winUser

		if (
			config.conf["keyboard"]["beepForLowercaseWithCapslock"]
			and ch.islower()
			and winUser.getKeyState(winUser.VK_CAPITAL) & 1
		):
			import tones
			tones.beep(3000, 40)


class ClipboardCommandAnnouncement(object):
	scriptDelay = None
	_changeSelectionGestureToMessage = {
		"shift+upArrow": None,
		"shift+downArrow": None,
		"shift+pageUp": None,
		"shift+pageDown": None,
		"shift+home": None,
		"shift+end": None,
	}

	def initOverlayClass(self):
		editionKeyCommands = getEditionKeyCommands(self)
		if self.checkSelection:
			d = self._changeSelectionGestureToMessage .copy()
			selectAllKey = editionKeyCommands["selectAll"]
			if selectAllKey != "":
				d[selectAllKey] = _msgSelectAll,
			for key in d:
				self.bindGesture("kb:%s" % key, "reportChangeSelection")
		for item in _clipboardCommands:
			key = editionKeyCommands[item]
			if key != "":
				self.bindGesture("kb:%s" % key, "clipboardCommandAnnouncement")

	def getSelectionCountByIA(self, obj):
		count = 0
		try:
			o = obj.IAccessibleObject
			id = obj.IAccessibleChildID
		except Exception:
			log.warning("getSelectionCountByIA: error")
			return -1
		while o:
			if o.accState(id) & STATE_SYSTEM_SELECTED:
				count += 1
			try:
				(o, id) = accNavigate(o, id, NAVDIR_NEXT)
			except Exception:
				o = None

		o = obj.IAccessibleObject
		id = obj.IAccessibleChildID
		while o:
			try:
				(o, id) = accNavigate(o, id, NAVDIR_PREVIOUS)
			except Exception:
				o = None
			if o and o.accState(id) & STATE_SYSTEM_SELECTED:
				count += 1
		return count

	def getSelectionCount(self):
		obj = api.getFocusObject()
		if hasattr(obj, "IAccessibleObject"):
			return self.getSelectionCountByIA(obj)

		count = 0
		o = obj
		while o:
			if State.SELECTED in o.states:
				count += 1
			try:
				o = o._get_next()
			except Exception:
				o = None

		o = obj
		while o:
			try:
				o = o.previous
				if State.SELECTED in o.states:
					count += 1
			except Exception:
				o = None
		return count

	def isThereASelection(self):
		obj = api.getFocusObject()
		o = obj
		while o:
			if State.SELECTED in o.states:
				return True
			o = o._get_next()
		o = obj.previous
		while o:
			if State.SELECTED in o.states:
				return True
			o = o.previous
		return False

	def getSelectionInfo(self):
		text = getStatusBarText()
		if text != "":
			return text
		count = self.getSelectionCount()
		if count == 0:
			text = NVDAString("No selection")
		elif count == 1:
			# Translators: no comment.
			text = _("One selected object")
		elif count > 1:
			# Translators: no comment.
			text = _("%s selected objects") % count
		return text

	def script_reportChangeSelection(self, gesture):
		global _GB_taskTimer

		def callback():
			global _GB_taskTimer
			_GB_taskTimer = None

			text = self.getSelectionInfo()
			if text != "":
				queueHandler.queueFunction(
					queueHandler.eventQueue, speech.speakText, text, symbolLevel=SymbolLevel.SOME)

		if _GB_taskTimer:
			_GB_taskTimer.Stop()
			_GB_taskTimer = None
		gesture.send()
		try:
			msg = self.__changeSelectionGestures["+".join(
				gesture.modifierNames) + "+" + gesture.mainKeyName]
		except Exception:
			msg = None
		if msg:
			ui.message(msg)
		_GB_taskTimer = core.callLater(800, callback)

	def script_clipboardCommandAnnouncement(self, gesture):
		stopDelayScriptTask()

		def callback():
			clearDelayScriptTask()
			editionKeyCommands = getEditionKeyCommands(self)
			d = {}
			for item in _clipboardCommands:
				d[editionKeyCommands[item]] = _clipboardCommands[item]
			(msg, checkSelection, checkClipChange, checkClipEmpty) = d["+".join(
				gesture.modifierNames) + "+" + gesture.mainKeyName]
			cm = clipboard.ClipboardManager()
			clipEmpty = cm.isEmpty if checkClipEmpty else None
			selection = self.checkSelection if checkSelection else None
			# we send always command key
			gesture.send()
			if selection:
				if not self.isThereASelection():
					ui.message(NVDAString("No selection"))
					return

			if clipEmpty:
				# Translators: message to report clipboard is empty
				ui.message(_("Clipboard is empty"))
				return
			if checkClipChange:
				time.sleep(0.1)
				if not cm.changed():
					return
			ui.message(msg)
		delayScriptTaskWithDelay(80, callback)


_classNamesToCheck = [
	"Edit", "RichEdit", "RichEdit20", "REComboBox20W", "RICHEDIT50W", "RichEditD2DPT",
	"Scintilla", "TScintilla", "AkelEditW", "AkelEditA", "_WwG", "_WwN", "_WwO",
	"SALFRAME", "ConsoleWindowClass"]
_rolesToCheck = [Role.DOCUMENT, Role.EDITABLETEXT, Role.TERMINAL]


def chooseNVDAObjectOverlayClasses(obj, clsList):
	useRecogResultNVDAObjectEx = False
	useEditableTextBaseEx = False
	for cls in clsList:
		if contentRecog.recogUi.RecogResultNVDAObject in cls.__mro__:
			useRecogResultNVDAObjectEx = True
		if NVDAObjects.behaviors.EditableTextBase in cls.__mro__:
			useEditableTextBaseEx = True

	if useEditableTextBaseEx:
		if canInstallSpellingAtTypingFunctionnality:
			clsList.insert(0, NVDAObjectEx)
		else:
			clsList.insert(0, NVDAObjectExBase)
	if useRecogResultNVDAObjectEx:
		clsList.insert(0, RecogResultNVDAObjectEx)
	# to fix the Access8Math  problem with the "alt+m" virtual menu
	# for the obj, the informations are bad: role= Window, className= Edit, not states
	#  tand with no better solution, we check the length of obj.states
	elif (
		(
			obj.role in _rolesToCheck
			or hasattr(obj, "windowClassName")
		and obj.windowClassName in _classNamesToCheck
		)
		and len(obj.states)
	):
		# newer revisions of Windows 11 build 22000 moves focus to emoji search field.
		# However this means NVDA's own edit field scripts will override emoji panel commands.
		# Therefore remove text field movement commands so emoji panel commands can be used directly.
		if (
			hasattr(obj, "UIAAutomationId")
			and obj.UIAAutomationId == "Windows.Shell.InputApp.FloatingSuggestionUI.DelegationTextBox"
		):
			pass
		else:
			clsList.insert(0, EditableTextEx)
		return
	elif isInstall(FCT_ClipboardCommandAnnouncement):
		clsList.insert(0, ClipboardCommandAnnouncement)
		obj.checkSelection = False
		if obj.role in (Role.TREEVIEWITEM, Role.LISTITEM):
			obj.checkSelection = True


def initialize():
	setCanInstallSpellingAtTypingFunctionnality()

	def callback():
		if confirm_YesNo(
			# Translators: message asking the user wether
			# the clipboard command announcements feature should be disabled or not
			_(
				"The clipspeak add-on has been detected on your system. "
				"In order for Clipboard command announcement feature to work without conflicts, "
				"clipSpeak add-on must be desactivated or uninstalled."
				"But if you want to use clipSpeak add-on, Clipboard command announcement feature must be uninstalled."
				" Would you like to uninstall this feature now?"),
			# Translators: warning dialog title
			_("Warning"),
		) != ReturnCode.YES:
			return
		from ..settings.addonConfig import C_DoNotInstall
		from ..settings import setInstallFeatureOption
		setInstallFeatureOption(FCT_ClipboardCommandAnnouncement, C_DoNotInstall)
		from ..settings.dialog import askForNVDARestart
		askForNVDARestart()
	if isInstall(FCT_ClipboardCommandAnnouncement):
		for addon in addonHandler.getRunningAddons():
			if addon.name == "clipspeak":
				wx.CallAfter(callback)
				break


canInstallSpellingAtTypingFunctionnality = None


def setCanInstallSpellingAtTypingFunctionnality():
	global canInstallSpellingAtTypingFunctionnality
	try:
		# if speakTypingWords add-on is running, spelling at typing functionnality can not be installed
		m = next(filter (lambda a: a.name == "speakTypingWords", addonHandler.getRunningAddons ()))
		canInstallSpellingAtTypingFunctionnality = False
		log.info(
			"""The add-on "%s" being running, the functionality concerning the reporting of spelling errors when typing is restricted (see the "NVDAExtensionGlobalPlugin" user manual).""" % m.manifest["name"])
	except Exception:
		# speakTypingWords add-on is not running
		canInstallSpellingAtTypingFunctionnality = True
	from . import settingsDialogsPatche
