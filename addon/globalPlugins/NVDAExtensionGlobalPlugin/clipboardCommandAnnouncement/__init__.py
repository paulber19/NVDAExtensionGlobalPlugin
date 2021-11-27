# globalPlugins\NVDAExtensionGlobalPlugin\clipboardCommandAnnouncement\__init__.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2021 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import api
import textInfos
import speech
import ui
import time
try:
	# for nvda version >= 2021.2
	from controlTypes.role import Role
	ROLE_DOCUMENT = Role.DOCUMENT
	ROLE_EDITABLETEXT = Role.EDITABLETEXT
	ROLE_TREEVIEWITEM = Role.TREEVIEWITEM
	ROLE_LISTITEM = Role.LISTITEM
	from controlTypes.state import State
	STATE_READONLY = State.READONLY
	STATE_EDITABLE = State.EDITABLE
	STATE_MULTILINE = State.MULTILINE
	STATE_SELECTED = State.SELECTED
except (ModuleNotFoundError, AttributeError):
	from controlTypes import (
		ROLE_DOCUMENT, ROLE_EDITABLETEXT,
		ROLE_TREEVIEWITEM, ROLE_LISTITEM,
		STATE_READONLY, STATE_EDITABLE,
		STATE_MULTILINE, STATE_SELECTED)
from editableText import EditableText
import braille
import config
try:
	# for nvda version >= 2021.2
	from characterProcessing import SymbolLevel
	SYMLVL_SOME = SymbolLevel.SOME
except ImportError:
	from characterProcessing import SYMLVL_SOME
from IAccessibleHandler import accNavigate
from oleacc import *  # noqa:F403
import UIAHandler
from NVDAObjects.UIA import UIA
import queueHandler
import eventHandler
import core
import contentRecog.recogUi
from ..utils.NVDAStrings import NVDAString
from ..settings import *  # noqa:F403
from ..utils.keyboard import getEditionKeyCommands

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
	"undo": (_msgUnDo, False),
	"cut": (_msgCut, True),
	"copy": (_msgCopy, True),
	"paste": (_msgPaste, False)
	}

# task timer
_GB_taskTimer = None


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
		chunk for child in obj.children[:-1] for chunk in (child.name, child.value) if chunk and isinstance(chunk, str) and not chunk.isspace())  # noqa:E501


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
	try:
		if hasattr(info.bookmark, "_start"):
			start = info.bookmark._start._startOffset
		else:
			start = info.bookmark.startOffset
	except AttributeError:
		return
	lineInfo = info.copy()
	lineInfo.collapse()
	lineInfo.expand(textInfos.UNIT_LINE)
	if hasattr(lineInfo.bookmark, "_start"):
		lineStart = lineInfo.bookmark._start._startOffset
	else:
		lineStart = lineInfo.bookmark.startOffset
	index = start - lineStart

	def callback(index):
		speech.speakMessage(str(index + 1))
	_reportPositionTimer = wx.CallLater(500, callback, index)


class RecogResultNVDAObjectEx (contentRecog.recogUi.RecogResultNVDAObject):
	def _caretMovementScriptHelper(
		self,
		gesture,
		unit,
		direction=None,
		posConstant=textInfos.POSITION_SELECTION,
		posUnit=None,
		posUnitEnd=False,
		extraDetail=False,
		handleSymbols=False):
		super(RecogResultNVDAObjectEx, self)._caretMovementScriptHelper(
			gesture,
			unit,
			direction,
			posConstant,
			posUnit,
			posUnitEnd,
			extraDetail,
			handleSymbols)
		return
		curLevel = config.conf["speech"]["symbolLevel"]
		if unit == textInfos.UNIT_WORD:
			from ..settings.nvdaConfig import _NVDAConfigManager
			symbolLevelOnWordCaretMovement = _NVDAConfigManager .getSymbolLevelOnWordCaretMovement()  # noqa:E501
			if symbolLevelOnWordCaretMovement is not None:
				config.conf["speech"]["symbolLevel"] = symbolLevelOnWordCaretMovement
		super(RecogResultNVDAObjectEx, self)._caretMovementScriptHelper(
			gesture,
			unit,
			direction,
			posConstant,
			posUnit, posUnitEnd,
			extraDetail,
			handleSymbols)
		config.conf["speech"]["symbolLevel"] = curLevel


_taskDelay = None


class EditableTextEx(EditableText):
	_commandToScript = {
		"copy": "copyToClipboard",
		"cut": "cutAndCopyToClipboard",
		"paste": "pasteFromClipboard",
		"undo": "undo",
		}

	def initOverlayClass(self):
		if isInstall(ID_ClipboardCommandAnnouncement):
			d = getEditionKeyCommands(self)
			for command in self._commandToScript:
				key = d[command]
				if key != "":
					self.bindGesture("kb:%s" % key, self._commandToScript[command])
		# bug fix in nvda 2020.3
					# so toggleReportNextWordOnDeletionOption return always since this version.
		if toggleReportNextWordOnDeletionOption(False):
			self.bindGesture("kb:control+numpadDelete", "controlDelete")
			self.bindGesture("kb:control+delete", "controlDelete")

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
		info = self.getSelectionInfo()
		if not info:
			# Translators: Reported when there is no text selected (for copying).
			ui.message(NVDAString("No selection"))
			gesture.send()
			return
		# Translators: Message presented when text has been copied to clipboard.
		ui.message(_msgCopy)
		gesture.send()

	def script_cutAndCopyToClipboard(self, gesture):
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
		ui.message(_msgCut)
		gesture.send()

	def script_pasteFromClipboard(self, gesture):
		if (
			STATE_READONLY in self.states or (
			STATE_EDITABLE not in self.states
			and not STATE_MULTILINE)):
			gesture.send()
			return
		ui.message(_msgPaste)
		gesture.send()
		from globalCommands import commands
		wx.CallLater(100, commands.script_reportCurrentLine, None)

	def script_undo(self, gesture):
		if (
			STATE_READONLY in self.states or (
			STATE_EDITABLE not in self.states
			and not STATE_MULTILINE)):
			gesture.send()
			return
		ui.message(_msgUnDo)
		gesture.send()

	def script_controlDelete(self, gesture):
		from editableText import EditableText
		gesture.send()
		if not isinstance(self, EditableText):
			log.warning("Not EtitableText class instance ")
			return
		time.sleep(0.3)
		try:
			info = self.makeTextInfo(textInfos.POSITION_CARET)
		except Exception:
			log.warning("not makeTextInfo")
			return
		self._caretScriptPostMovedHelper(textInfos.UNIT_WORD, gesture, info)
		braille.handler.handleCaretMove(self)

	def _caretScriptPostMovedHelper(self, speakUnit, gesture, info=None):
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
			symbolLevelOnWordCaretMovement = _NVDAConfigManager .getSymbolLevelOnWordCaretMovement()  # noqa:E501
			if symbolLevelOnWordCaretMovement is not None:
				config.conf["speech"]["symbolLevel"] = symbolLevelOnWordCaretMovement
		gesture.send()
		caretMoved, newInfo = self._hasCaretMoved(bookmark)
		if not caretMoved and self.shouldFireCaretMovementFailedEvents:
			eventHandler.executeEvent("caretMovementFailed", self, gesture=gesture)
		reportPosition(newInfo)
		self._caretScriptPostMovedHelper(unit, gesture, newInfo)
		config.conf["speech"]["symbolLevel"] = curLevel


class ClipboardCommandAnnouncement(object):
	_changeSelectionGestureToMessage = {
		"shift+upArrow": None,
		"shift+downArrow": None,
		"shift+pageUp": None,
		"shift+pageDown": None,
		"shift+home": None,
		"shift+end": None,
	}

	def initOverlayClass(self):
		if isInstall(ID_ClipboardCommandAnnouncement):
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
				gesture.modifierNames) + "+"+gesture.mainKeyName]
		except Exception:
			msg = None
		if msg:
			ui.message(msg)
		_GB_taskTimer = core.callLater(800, callback)

	def script_clipboardCommandAnnouncement(self, gesture):
		editionKeyCommands = getEditionKeyCommands(self)
		d = {}
		for item in _clipboardCommands:
			d[editionKeyCommands[item]] = _clipboardCommands[item]
		(msg, checkSelection) = d["+".join(gesture.modifierNames)+"+"+gesture.mainKeyName]  # noqa:E501
		if self.checkSelection and checkSelection:
			if not self.isThereASelection():
				ui.message(NVDAString("No selection"))
			else:
				ui.message(msg)
				# we send always command key
				gesture.send()
			return
		ui.message(msg)
		gesture.send()


_classNamesToCheck = [
	"Edit", "RichEdit", "RichEdit20", "REComboBox20W", "RICHEDIT50W",
	"Scintilla", "TScintilla", "AkelEditW", "AkelEditA", "_WwG", "_WwN", "_WwO",
	"SALFRAME"]
_rolesToCheck = [ROLE_DOCUMENT, ROLE_EDITABLETEXT]


def chooseNVDAObjectOverlayClasses(obj, clsList):
	if contentRecog.recogUi.RecogResultNVDAObject in clsList:
		clsList.insert(0, RecogResultNVDAObjectEx)
	elif obj.role in _rolesToCheck or obj.windowClassName in _classNamesToCheck:
		clsList.insert(0, EditableTextEx)
	elif isInstall(ID_ClipboardCommandAnnouncement):
		clsList.insert(0, ClipboardCommandAnnouncement)
		obj.checkSelection = False
		if obj.role in (ROLE_TREEVIEWITEM, ROLE_LISTITEM):
			obj.checkSelection = True
