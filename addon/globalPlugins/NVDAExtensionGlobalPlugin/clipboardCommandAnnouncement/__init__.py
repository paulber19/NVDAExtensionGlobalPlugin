# globalPlugins\NVDAExtensionGlobalPlugin\clipboardCommandAnnouncement\__init__.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2023 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from logHandler import log
import wx
import gui
import api
import textInfos
import speech
import speech.speech
import ui
import time
from typing import Tuple, Optional
try:
	# for nvda version >= 2021.2
	from controlTypes.role import Role
	ROLE_DOCUMENT = Role.DOCUMENT
	ROLE_EDITABLETEXT = Role.EDITABLETEXT
	ROLE_TERMINAL = Role.TERMINAL
	ROLE_TREEVIEWITEM = Role.TREEVIEWITEM
	ROLE_LISTITEM = Role.LISTITEM
	from controlTypes.state import State
	STATE_READONLY = State.READONLY
	STATE_EDITABLE = State.EDITABLE
	STATE_MULTILINE = State.MULTILINE
	STATE_SELECTED = State.SELECTED
except (ModuleNotFoundError, AttributeError):
	from controlTypes import (
		ROLE_DOCUMENT, ROLE_EDITABLETEXT, ROLE_TERMINAL,
		ROLE_TREEVIEWITEM, ROLE_LISTITEM,
		STATE_READONLY, STATE_EDITABLE,
		STATE_MULTILINE, STATE_SELECTED)
import editableText
import braille
import config
try:
	# for nvda version >= 2021.2
	from characterProcessing import SymbolLevel
	SYMLVL_SOME = SymbolLevel.SOME
except ImportError:
	from characterProcessing import SYMLVL_SOME
from IAccessibleHandler import accNavigate
from oleacc import (
	STATE_SYSTEM_SELECTED,
	NAVDIR_PREVIOUS, NAVDIR_NEXT,
)
import UIAHandler
from NVDAObjects.UIA import UIA
import queueHandler
import eventHandler
import core
import contentRecog.recogUi
from ..utils.NVDAStrings import NVDAString
from ..utils import delayScriptTaskWithDelay, stopDelayScriptTask, clearDelayScriptTask
from ..settings import isInstall, toggleTypedWordSpeakingEnhancementAdvancedOption
from ..settings.addonConfig import (
	FCT_ClipboardCommandAnnouncement,
)
from ..utils.keyboard import getEditionKeyCommands
from . import clipboard

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
_msgSelectAll = _("select all")

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
			if STATE_READONLY in self.states or (
				STATE_EDITABLE not in self.states
				and STATE_MULTILINE not in self.states):
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
				STATE_READONLY in self.states or (
				STATE_EDITABLE not in self.states
				and not STATE_MULTILINE)):
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
				self.processGesture, textInfos.UNIT_LINE, gesture)

		stopDelayScriptTask()
		# to filter out too fast script calls while holding down the command gesture.
		delayScriptTaskWithDelay(80, callback)

	def processGesture(self, unit, gesture):
		try:
			info = self.makeTextInfo(textInfos.POSITION_CARET)
		except Exception:
			gesture.send()
			return
		bookmark = info.bookmark
		info.expand(textInfos.UNIT_WORD)
		word = info.text
		gesture.send()
		# We'll try waiting for the caret to move, but we don't care if it doesn't.
		caretMoved, newInfo = self._hasCaretMoved(bookmark, retryInterval=0.01, timeout=2.0, origWord=word)
		self._caretScriptPostMovedHelper(unit, gesture, newInfo)
		braille.handler.handleCaretMove(self)

	def script_undo(self, gesture):
		def callback():
			clearDelayScriptTask()
			if (
				STATE_READONLY in self.states or (
				STATE_EDITABLE not in self.states
				and not STATE_MULTILINE)):
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

# this code comes from leonardder  work for issue #8110, see at:
# Speak typed words based on TextInfo if possible #8110
# temporary


try:
	# for nvda version >= 2023.1
	from NVDAObjects.behaviors import EditableTextBase
except ImportError:
	from NVDAObjects.behaviors import EditableText as EditableTextBase


class EditableTextBaseEx(EditableTextEx, EditableTextBase):
	#: A cached bookmark for the caret.
	#: This is cached until L{hasNewWordBeenTyped} clears it
	_cachedCaretBookmark = None

	def _caretScriptPostMovedHelper(self, speakUnit, gesture, info=None):
		# Forget the word currently being typed as the user has moved the caret somewhere else.
		speech.speech.clearTypedWordBuffer()
		# Also clear our latest cachetd caret bookmark
		self._clearCachedCaretBookmark()
		super()._caretScriptPostMovedHelper(speakUnit, gesture, info)

	def getScript(self, gesture):
		script = super().getScript(gesture)
		if script or not self.useTextInfoToSpeakTypedWords:
			return script
		if gesture.isCharacter and gesture.vkCode != 231:
			return self.script_preTypedCharacter
		return None

	def script_preTypedCharacter(self, gesture):
		try:
			self._cachedCaretBookmark = self.caret.bookmark
		except (LookupError, RuntimeError):
			pass  # Will still be None

		gesture.send()

	def _get_caretMovementDetectionUsesEvents(self) -> bool:
		"""Returns whether or not to rely on caret and textChange events when
		finding out whether the caret position has changed after pressing a caret movement gesture.
		Note that if L{_useEvents_maxTimeoutMs} is elapsed,
		relying on events is no longer reliable in most situations.
		Therefore, any event should occur before that timeout elapses.
		"""
		# This class is a mixin that usually comes before other relevant classes in the mro.
		# Therefore, try to call super first, and if that fails, return the default (C{True}.
		try:
			res = super().caretMovementDetectionUsesEvents
			log.debug("_get_caretMovementDetectionUsesEvents super res: %s" % res)
			return res
		except AttributeError:
			log.debug("_get_caretMovementDetectionUsesEvents exception")
			return True

	def _get_useTextInfoToSpeakTypedWords(self) -> bool:
		"""Returns whether or not to use textInfo to announce newly typed words."""
		# This class is a mixin that usually comes before other relevant classes in the mro.
		# Therefore, try to call super first, and if that fails, return the default (C{True}.
		try:
			return super().useTextInfoToSpeakTypedWords
		except AttributeError:
			return True

	def _clearCachedCaretBookmark(self):
		self._cachedCaretBookmark = None

	def hasNewWordBeenTyped(self, wordSeparator: str) -> Tuple[Optional[bool], textInfos.TextInfo]:
		"""
		Returns whether a new word has been typed during this core cycle.
		It relies on self._cachedCaretBookmark, which is cleared after every core cycle.
		@param wordSeparator: The word seperator that has just been typed.
		@returns: a tuple containing the following two values:
			1. Whether a new word has been typed. This could be:
				* False if a caret move has been detected, but no word has been typed.
				* True if a caret move has been detected and a new word has been typed.
				* None if no caret move could be detected.
			2. If the caret has moved and a new word has been typed, a TextInfo
				expanded to the word that has just been typed.
		"""
		log.debug("hasNewWordBeenTyped: wordSeparator= %s" % wordSeparator)
		if not self.useTextInfoToSpeakTypedWords:
			return (None, None)
		bookmark = self._cachedCaretBookmark
		if not bookmark:
			return (None, None)
		self._clearCachedCaretBookmark()
		log.debug("bookmark: %s" % bookmark)
		caretMoved, caretInfo = self._hasCaretMoved(bookmark, retryInterval=0.005, timeout=0.030)
		if not caretMoved or not caretInfo or not caretInfo.obj:
			log.debug("not caret moved")
			return (None, None)
		info = caretInfo.copy()
		info.expand(textInfos.UNIT_LINE)
		log.debug("caretInfo: %s, bookmark= %s" % (info.text, info.bookmark))
		tempInfo = caretInfo.copy()
		res = tempInfo.move(textInfos.UNIT_CHARACTER, -2)
		if res != 0:
			tempInfo.expand(textInfos.UNIT_CHARACTER)
			ch = tempInfo.text
			log.debug("character caret-2: %s" % ch)
			# if there is a space (but no a Non-breaking space) before last character, return no word
			if len(ch) and ord(ch) != NON_BREAKING_SPACE and ch.isspace():
				log.debug("caret-2 is a space")
				return (False, None)
			# if the last character typed is not a letter or number, the word has been probably already reported
			if not ch.isalnum() and ord(ch) != NON_BREAKING_SPACE:
				log.debug("caret-2 is not alphanumericc")
				return (False, None)

		wordInfo = self.makeTextInfo(bookmark)
		info = wordInfo.copy()
		info.expand(textInfos.UNIT_WORD)
		log.debug("wordInfo: %s" % info.text)
		# The bookmark is positioned after the end of the word.
		# Therefore, we need to move it one character backwards.
		res = wordInfo.move(textInfos.UNIT_CHARACTER, -1)
		wordInfo.expand(textInfos.UNIT_WORD)
		log.debug("wordInfo moved: %s, %s" % (res, wordInfo.text))
		diff = wordInfo.compareEndPoints(caretInfo, "endToStart")
		log.debug("diff: %s" % diff)
		# if diff >= 0 and not wordSeparator.isspace():
		if diff >= 0 and wordSeparator.isalnum():
			# This is no word boundary.
			return (False, None)
		elif wordInfo.text.isspace():
			# There is only space, which is not considered a word.
			# For example, this can occur in Notepad++ when auto indentation is on.
			log.debug("Word before caret contains only spaces")
			return (None, None)
		wordInfo.collapse()
		wordInfo.expand(textInfos.UNIT_WORD)
		log.debug("word1: %s" % wordInfo.text)
		# with notepad editor, wordSeparator is at the end of word.  So we need to suppress it
		# not same thing with other editor as notepad++, wordpad, word.
		if wordInfo.text[-1] == wordSeparator:
			# the word is before the wordSeparator
			res = wordInfo.move(textInfos.UNIT_CHARACTER, -1, endPoint="end")
			log.debug("word2: %s, %s" % (res, wordInfo.text))
		return (True, wordInfo)

	def _get_caret(self):
		return self.makeTextInfo(textInfos.POSITION_CARET)

	def _updateSelectionAnchor(self, oldInfo, newInfo):
		# Only update the value if the selection changed.
		try:
			if newInfo.compareEndPoints(oldInfo, "startToStart") != 0:
				self.isTextSelectionAnchoredAtStart = False
			elif newInfo.compareEndPoints(oldInfo, "endToEnd") != 0:
				self.isTextSelectionAnchoredAtStart = True
		except Exception:
			pass

	def event_typedCharacter(self, ch: str):
		if(
			config.conf["documentFormatting"]["reportSpellingErrors"]
			and config.conf["keyboard"]["alertForSpellingErrors"]
			and (
				# Not alpha, apostrophe or control.
				ch.isspace() or (ch >= " " and ch not in "'\x7f" and not ch.isalpha())
			)
		):
			# Reporting of spelling errors is enabled and this character ends a word.
			self._reportErrorInPreviousWord()
		from .speechEx import speakTypedCharacters
		speakTypedCharacters(ch)
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
			if STATE_SELECTED in o.states:
				count += 1
			try:
				o = o._get_next()
			except Exception:
				o = None

		o = obj
		while o:
			try:
				o = o.previous
				if STATE_SELECTED in o.states:
					count += 1
			except Exception:
				o = None
		return count

	def isThereASelection(self):
		obj = api.getFocusObject()
		o = obj
		while o:
			if STATE_SELECTED in o.states:
				return True
			o = o._get_next()
		o = obj.previous
		while o:
			if STATE_SELECTED in o.states:
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
			text = _(" one selected object")
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
					queueHandler.eventQueue, speech.speakText, text, symbolLevel=SYMLVL_SOME)

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
_rolesToCheck = [ROLE_DOCUMENT, ROLE_EDITABLETEXT, ROLE_TERMINAL]


def chooseNVDAObjectOverlayClasses(obj, clsList):
	useRecogResultNVDAObjectEx = False
	useEditableTextBaseEx = False
	for cls in clsList:
		if contentRecog.recogUi.RecogResultNVDAObject in cls.__mro__:
			useRecogResultNVDAObjectEx = True
		if EditableTextBase in cls.__mro__:
			useEditableTextBaseEx = True
	if useRecogResultNVDAObjectEx:
		clsList.insert(0, RecogResultNVDAObjectEx)
	# to fix the Access8Math  problem with the "alt+m" virtual menu
	# for the obj, the informations are bad: role= Window, className= Edit, not states
	#  tand with no better solution, we check the length of obj.states
	elif (obj.role in _rolesToCheck or obj.windowClassName in _classNamesToCheck) and len(obj.states):
		# newer revisions of Windows 11 build 22000 moves focus to emoji search field.
		# However this means NVDA's own edit field scripts will override emoji panel commands.
		# Therefore remove text field movement commands so emoji panel commands can be used directly.
		if hasattr(obj, "UIAAutomationId")\
			and obj.UIAAutomationId == "Windows.Shell.InputApp.FloatingSuggestionUI.DelegationTextBox":
			pass
		else:
			if toggleTypedWordSpeakingEnhancementAdvancedOption(False) and useEditableTextBaseEx:
				clsList.insert(0, EditableTextBaseEx)
			else:
				clsList.insert(0, EditableTextEx)
		return
	elif isInstall(FCT_ClipboardCommandAnnouncement):
		clsList.insert(0, ClipboardCommandAnnouncement)
		obj.checkSelection = False
		if obj.role in (ROLE_TREEVIEWITEM, ROLE_LISTITEM):
			obj.checkSelection = True


def initialize():
	def callback():
		result = gui.messageBox(
			# Translators: message asking the user wether
			# the clipboard command announcements feature should be disabled
			# or not
			_(
				"clipspeak add-on has been detected on your system. "
				"In order for Clipboard command announcement feature to work without conflicts, "
				"clipSpeak add-on must be desactivated or uninstalled."
				"But if you want to use clipSpeak add-on, Clipboard command announcement feature must be uninstalled."
				" Would you like to uninstall this feature now?"),
			# Translators: question title
			_("clipSpeak add-on detection"),
			wx.YES_NO | wx.ICON_QUESTION, gui.mainFrame)
		if result == wx.NO:
			return
		from ..settings.addonConfig import C_DoNotInstall
		from ..settings import setInstallFeatureOption
		setInstallFeatureOption(FCT_ClipboardCommandAnnouncement, C_DoNotInstall)
		from ..settings.dialog import askForNVDARestart
		askForNVDARestart()
	if isInstall(FCT_ClipboardCommandAnnouncement):
		for addon in addonHandler.getAvailableAddons():
			if addon.name == "clipspeak" and not addon.isDisabled:
				wx.CallAfter(callback)
