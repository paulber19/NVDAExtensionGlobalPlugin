#NVDAExtensionGlobalPlugin/clipboardCommandAnnouncement/__init__.py
# a part of NVDAExtensionGlobalPlugin add-on
#Copyright (C) 2016-2018 Paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import addonHandler
addonHandler.initTranslation()
import api
import textInfos
import speech
import time
from ..utils.NVDAStrings import NVDAString
import controlTypes
from ..settings import *
from editableText import EditableText
import braille
import config
from characterProcessing import SYMLVL_SOME, SYMLVL_ALL
import eventHandler
from ..__init__ import GB_taskTimer
import NVDAObjects.IAccessible.sysListView32
from scriptHandler import isScriptWaiting, willSayAllResume
import wx
from IAccessibleHandler import accNavigate, splitIA2Attribs
from oleacc import *
from textInfos import DocumentWithPageTurns
import UIAHandler
from NVDAObjects.UIA import UIA
import queueHandler
import core
import contentRecog.recogUi

def getWExplorerStatusBarText(foreground):
	clientObject = UIAHandler.handler.clientObject
	foregroundElement = foreground.UIAElement
	element =foregroundElement.BuildUpdatedCache(UIAHandler.handler.baseCacheRequest)
	element = element.FindFirstBuildCache(UIAHandler.TreeScope_Descendants, clientObject.CreatePropertyCondition(UIAHandler.UIA_ControlTypePropertyId, UIAHandler.UIA_StatusBarControlTypeId), UIAHandler.handler.baseCacheRequest)
	if not element:
		return ""
	o = UIA(UIAElement = element)
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
	if  isinstance(foreground, UIA) and foreground.windowClassName == "CabinetWClass" and foreground.appModule.appName == "explorer":
		return getWExplorerStatusBarText(foreground)
	obj = api.getStatusBar()
	if not obj: return ""
	text = obj.name or ""
	if text:
		text += " "
	return text + " ".join(chunk for child in obj.children[:-1] for chunk in (child.name, child.value) if chunk and isinstance(chunk, basestring) and not chunk.isspace())
	
# Translators: message to the user on cut command activation.
_msgCut = _("Cut")
# Translators: message to the user on paste command activation.
_msgPaste = _("Paste")
# Translators: message to the user on copy command activation.
_msgCopy = _("Copy")
# Translators: message to the user on undo command activation.
_msgUnDo = _("UnDo")
# Translators: message to the user on  select all command activation.
_msgSelectAll = _("select all")

class RecogResultNVDAObjectEx (contentRecog.recogUi.RecogResultNVDAObject ):
	
	def _caretMovementScriptHelper(self,gesture,unit,direction=None,posConstant=textInfos.POSITION_SELECTION,posUnit=None,posUnitEnd=False,extraDetail=False,handleSymbols=False):
		super(RecogResultNVDAObjectEx , self)._caretMovementScriptHelper(gesture,unit,direction,posConstant,posUnit,posUnitEnd,extraDetail,handleSymbols)
		return
		curLevel = config.conf["speech"]["symbolLevel"]
		if unit == textInfos.UNIT_WORD :
			from ..settings import _addonConfigManager
			symbolLevelOnWordCaretMovement = _addonConfigManager .getSymbolLevelOnWordCaretMovement()
			if symbolLevelOnWordCaretMovement  is not None:
				config.conf["speech"]["symbolLevel"] = symbolLevelOnWordCaretMovement
		super(RecogResultNVDAObjectEx , self)._caretMovementScriptHelper(gesture,unit,direction,posConstant,posUnit,posUnitEnd,extraDetail,handleSymbols)
		config.conf["speech"]["symbolLevel"] = curLevel



from ..utils.keyboard import getEditionKeyCommands


class EditableTextEx(EditableText): 
	_commandToScript= {
		"copy": "copyToClipboard",
		"cut": "cutAndCopyToClipboard",
		"paste": "pasteFromClipboard",
		"undo": "undo",
		}
	
	def initOverlayClass(self):
		if isInstall(ID_ClipboardCommandAnnouncement  ):
			d = getEditionKeyCommands(self)
			for command in self._commandToScript.keys():
				key = d[command]
				if key != "":
					self.bindGesture("kb:%s"%key, self._commandToScript[command])
		if toggleReportNextWordOnDeletionOption(False):
			self.bindGesture("kb:control+numpadDelete", "controlDelete")
			self.bindGesture("kb:control+delete", "controlDelete")
			
	def getSelectionInfo(self):
		obj=api.getFocusObject()
		treeInterceptor=obj.treeInterceptor
		if hasattr(treeInterceptor,'TextInfo') and not treeInterceptor.passThrough:
			obj=treeInterceptor
		try:
			info=obj.makeTextInfo(textInfos.POSITION_SELECTION)
		except (RuntimeError, NotImplementedError):
			info=None
		if not info or info.isCollapsed:
			return None
		return info
	
	def script_copyToClipboard(self,gesture):
		info = self.getSelectionInfo()
		if not info:
			# Translators: Reported when there is no text selected (for copying).
			speech.speakMessage(NVDAString("No selection"))
			gesture.send()
			return
			

		# Translators: Message presented when text has been copied to clipboard.
		speech.speakMessage(NVDAString("Copied to clipboard"))
		gesture.send()
	
	def script_cutAndCopyToClipboard(self,gesture):
		if controlTypes.STATE_READONLY in self.states or (controlTypes.STATE_EDITABLE not in self.states and controlTypes.STATE_MULTILINE not in self.states):
			gesture.send()
			return
		
		info = self.getSelectionInfo()

		if not info:
			# Translators: Reported when there is no text selected (for copying).
			speech.speakMessage(NVDAString("No selection"))
			gesture.send()
			return
		
		speech.speakMessage(_msgCut)
		gesture.send()
	
	def script_pasteFromClipboard(self, gesture):
		if controlTypes.STATE_READONLY in self.states or (controlTypes.STATE_EDITABLE not in self.states and not controlTypes.STATE_MULTILINE):
			gesture.send()
			return
		
		speech.speakMessage(_msgPaste)
		gesture.send()
		time.sleep(0.1)
		from globalCommands import commands
		commands.script_reportCurrentLine(None)
	
	def script_undo(self, gesture):
		if controlTypes.STATE_READONLY in self.states or (controlTypes.STATE_EDITABLE not in self.states and not controlTypes.STATE_MULTILINE):
			gesture.send()
			return
			
		speech.speakMessage(_msgUnDo)
		gesture.send()


	def script_controlDelete(self,gesture):
		from editableText import EditableText
		gesture.send()
		if not isinstance(self,EditableText):
			log.warning("Not EtitableText class instance ")
			return
		
		time.sleep(0.3)
		try:
			info=self.makeTextInfo(textInfos.POSITION_CARET)
		except:
			log.warning("not makeTextInfo")
			return

		self._caretScriptPostMovedHelper(textInfos.UNIT_WORD,gesture,info)
		braille.handler.handleCaretMove(self)

	def _caretMovementScriptHelper(self, gesture, unit):
		curLevel = config.conf["speech"]["symbolLevel"]
		if unit == textInfos.UNIT_WORD :
			from ..settings import _addonConfigManager
			symbolLevelOnWordCaretMovement = _addonConfigManager .getSymbolLevelOnWordCaretMovement()
			if symbolLevelOnWordCaretMovement  is not None:
				config.conf["speech"]["symbolLevel"] = symbolLevelOnWordCaretMovement
		super(EditableTextEx, self)._caretMovementScriptHelper(gesture, unit)
		config.conf["speech"]["symbolLevel"] = curLevel

_clipboardCommands ={
"undo": (_msgUnDo, False),
	"cut": (_msgCut, True),
	"copy": (_msgCopy, True),
	"paste": (_msgPaste, False)
	}

class ClipboardCommandAnnouncement(object):

	_changeSelectionGestureToMessage = {
		"shift+upArrow": None,
		"shift+downArrow" : None,
		"shift+pageUp" : None,
		"shift+pageDown" : None,
		"shift+home" : None,
		"shift+end" : None,
	}
	
	def initOverlayClass(self):
		if isInstall(ID_ClipboardCommandAnnouncement  ):
			editionKeyCommands = getEditionKeyCommands(self)
			if self.checkSelection:
				d = self._changeSelectionGestureToMessage .copy()
				selectAllKey = editionKeyCommands["selectAll"]
				if selectAllKey != "":
					d[selectAllKey] = _msgSelectAll,
				for key in d:
					self.bindGesture("kb:%s"%key, "reportChangeSelection")
			for item in _clipboardCommands.keys():
				key = editionKeyCommands[item]
				if key != "":
					self.bindGesture("kb:%s"%key, "clipboardCommandAnnouncement")
	
	def getSelectionCountByIA(self, obj):
		count = 0
		try:
			o= obj.IAccessibleObject
			id = obj.IAccessibleChildID
		except:
			log.warning("getSelectionCountByIA: error")
			return -1
		while o:
			if o.accState(id) & STATE_SYSTEM_SELECTED:
				count += 1
			try:
				(o, id) = accNavigate(o,id,NAVDIR_NEXT)
			except:
				o = None

		o= obj.IAccessibleObject
		id = obj.IAccessibleChildID
		while o:
			try:
				(o, id) = accNavigate(o,id,NAVDIR_PREVIOUS)
			except:
				o = None
			if o and  o.accState(id) & STATE_SYSTEM_SELECTED:
				count += 1
		return count
	
	def getSelectionCount(self):
		obj = api.getFocusObject()
		if hasattr(obj, "IAccessibleObject"):
			return self.getSelectionCountByIA(obj)

		count = 0
		o = obj
		while o:
			if controlTypes.STATE_SELECTED in o.states:
				count += 1
			try:
				o = o.next
			except:
				o = None

		o= obj
		while o:
			try:
				o = o.previous
				if controlTypes.STATE_SELECTED in o.states:
					count += 1
			except:
				o = None		
		return count
	
	def isThereASelection(self):
		obj = api.getFocusObject()
		o = obj
		while o:
			if controlTypes.STATE_SELECTED in o.states:
				return True
			o = o.next
		o= obj.previous
		while o:
			if controlTypes.STATE_SELECTED in o.states:
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
		elif count== 1:
			# Translators: no comment.
			text = _(" one selected object")
		elif count > 1:
			# Translators: no comment.
			text = _("%s selected objects")%count
		return text
	
	def script_reportChangeSelection(self,gesture):
		global GB_taskTimer
		def callback():
			global GB_taskTimer
			GB_taskTimer = None
			text = self.getSelectionInfo()
			if text != "":
				queueHandler.queueFunction(queueHandler.eventQueue, speech.speakText, text, symbolLevel=SYMLVL_SOME)

		if GB_taskTimer:
			GB_taskTimer.Stop()
			GB_taskTimer = None
		gesture.send()
		try:
			msg = self.__changeSelectionGestures ["+".join(gesture.modifierNames)+"+"+gesture.mainKeyName]
		except:
			msg = None
		if msg: speech.speakMessage(msg)
		GB_taskTimer = core.callLater(800, callback)
	
	def script_clipboardCommandAnnouncement(self,gesture):
		editionKeyCommands = getEditionKeyCommands(self)
		d = {}
		for item in _clipboardCommands.keys():
			d[editionKeyCommands[item]] = _clipboardCommands[item]
		(msg, checkSelection) = d["+".join(gesture.modifierNames)+"+"+gesture.mainKeyName]
		if self.checkSelection and checkSelection:
			if not self.isThereASelection():
				speech.speakMessage(NVDAString("No selection"))
			else:
				speech.speakMessage(msg)
				# we send always command key
				gesture.send()
			return
		speech.speakMessage(msg)
		gesture.send()


def chooseNVDAObjectOverlayClasses(obj, clsList):
	if contentRecog.recogUi.RecogResultNVDAObject in clsList:
		clsList.insert(0, RecogResultNVDAObjectEx)
	elif obj.role in (controlTypes.ROLE_DOCUMENT, controlTypes.ROLE_EDITABLETEXT,) or obj.windowClassName in ("Edit", "RichEdit", "RichEdit20","REComboBox20W", "RICHEDIT50W", "Scintilla","TScintilla", "AkelEditW", "AkelEditA", "_WwG", "_WwN","_WwO", "SALFRAME"):
		clsList.insert(0, EditableTextEx)
	elif isInstall(ID_ClipboardCommandAnnouncement  ):
		clsList.insert(0, ClipboardCommandAnnouncement)
		obj.checkSelection = False
		if  obj.role  in (controlTypes.ROLE_TREEVIEWITEM, controlTypes.ROLE_LISTITEM):
			obj.checkSelection = True

