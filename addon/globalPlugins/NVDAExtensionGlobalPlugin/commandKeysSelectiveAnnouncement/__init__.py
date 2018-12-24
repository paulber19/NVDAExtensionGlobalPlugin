#NVDAExtensionGlobalPlugin/commandKeysSelectiveAnnouncement/__init__.py
#A part of NVDAExtensionGlobalPlugin add-on
#Copyright (C) 2018  paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import addonHandler
addonHandler.initTranslation()
from logHandler import log,_getDefaultLogFilePath
import scriptHandler
import speech
import gui
import winUser
import controlTypes
import inputCore 
import watchdog
import queueHandler
import api
import wx
import config
import sayAllHandler
from inputCore import NoInputGestureAction
from ..utils.NVDAStrings import NVDAString
from ..utils import speakLater, makeAddonWindowTitle
import  time
from vkCodes import byName
import ui
import winInputHook
from ..settings import _addonConfigManager, toggleBeepAtRemanenceStartAdvancedOption, toggleBeepAtRemanenceEndAdvancedOption
from ..settings.addonConfig import ID_CommandKeysSelectiveAnnouncement , ID_KeyRemanence
from ..utils.keyboard import getKeyboardKeys
from keyboardHandler import KeyboardInputGesture
from brailleInput import BrailleInputGesture
from braille import BrailleDisplayGesture
import tones
import core



_NVDA_InputManager = None
_myInputManager = None


_availableModifierKeysCombination = [
	["NVDA",],
	["NVDA","alt"],
	["NVDA","alt","control"],
	["NVDA","alt","control", "shift"],
	["NVDA","alt","shift"],
	["NVDA","control"],
	["NVDA","control","shift"],
	["NVDA","shift"],
	["alt",],
	["alt","control"],
	["alt","control","shift"],
	["alt","shift"],
	["control",],
	["control","shift"],
	["shift",],
	]
import tones
class MyInputManager (inputCore.InputManager):
	# gesture's sequence to set remanence's activation
	activationSequences = ["rightShift,rightControl,rightShift","leftShift,leftControl,leftShift",]
	# to save last modifiers  used for activation setting
	lastModifiersForActivation = []
	# remanence timer 
	remanenceTimer = None
	remanenceActivation = False
	lastModifiers = []
	lastGesture = None
	lastModifierForRepeat = []
	lastGestureTime = None

	
	def __init__(self):
		self.commandKeysFilter = CommandKeysFilter()
		super(MyInputManager , self).__init__()
	def stopRemanence(self, beep = False):
		if self.remanenceActivation is False:
			return
		self.lastModifiers = []
		if self.isRemanenceStarted():
			self.remanenceTimer.Stop()
		self.remanenceTimer = None
		if beep and toggleBeepAtRemanenceEndAdvancedOption(False):
			tones.beep(3000,20)
	
	def startRemanence(self, gesture):
		def endRemanence (gesture):
			self.stopRemanence(beep = True)
			gesture.noAction = False
			queueHandler.queueFunction(queueHandler.eventQueue, self.executeNewGesture, gesture)
		
		if self.remanenceActivation is False:
			return
		if not self.isRemanenceStarted() :
			if toggleBeepAtRemanenceStartAdvancedOption(False):
				tones.beep(100, 60)
		else:
			self.remanenceTimer.Stop()
		if gesture is not None:
			gesture.noAction = True
		self.remanenceTimer = core.callLater(_addonConfigManager.getRemanenceDelay(), endRemanence, gesture)
	
	def isRemanenceStarted(self):
		if self.remanenceTimer is not None:

			return True
		return False
	def toggleRemanenceActivation(self):
		if self.remanenceActivation is False:
			self.remanenceActivation = True
			queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("Keys's remanence activation on"))
#			tones.beep(400, 150)
		else:
			self.stopRemanence()
			self.remanenceActivation = False
			queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("Keys's remanence activation off"))
			#tones.beep(1400, 150)
	
	
	def manageRemanenceActivation(self, modifier):
		self.lastModifiersForActivation.append(modifier)
		if len(self.lastModifiersForActivation) >5:
			self.lastModifiersForActivation = self.lastModifiersForActivation[1:]
		if len(self.lastModifiersForActivation) <3:
			return False
		l = self.lastModifiersForActivation[-3:]
		s = ""
		for modifier in l:
			s  = s+","+modifier.mainKeyName
		if s[1:] not in self.activationSequences:
			return False
			
		self.lastModifiersForActivation = []
		self.toggleRemanenceActivation()
		return True
		
	
	def manageRemanence(self, currentGesture):
		from ..settings import isInstall
		if not isInstall(ID_KeyRemanence):
			return None
		delayBetweenGestures = time.time() - self.lastGestureTime if self.lastGestureTime else time.time()
		self.lastGestureTime = time.time()
		lastGesture = self.lastGesture
		self.lastGesture = currentGesture
		if currentGesture.isModifier:
			# only modifier key can be in activation sequence
			if self.manageRemanenceActivation(currentGesture):
				self.stopRemanence()
				return None
		else:
			# it's not a modifier key, so forget all previous saved modifiers for activation.
			self.lastModifiersForActivation = []
		if not self.remanenceActivation:
			return None
		if currentGesture.isModifier:
			# if gesture is the same than last saved modifier , stop remanence
			if self.isRemanenceStarted() and currentGesture.displayName == self.lastModifiers[-1].displayName:
				self.stopRemanence(beep = True)
				return None
			self.lastModifiers.append(currentGesture)
			queueHandler.queueFunction(queueHandler.eventQueue, self.startRemanence, currentGesture)
			currentGesture.noAction = True
			return None
		
		if (currentGesture.mainKeyName.lower() == "capslock" ):
			self.stopRemanence()
		if not self.isRemanenceStarted():
			# perhaps it's a gesture repeat
			if (delayBetweenGestures > 0.5) or lastGesture is None or (lastGesture  and (currentGesture.displayName != lastGesture.displayName )):
				# no, it's a normal gesture
				# no, it's a normal gesture
				self.lastModifiersForRepeat = []
				return None
		else:
			#remanence is started, so saved last modifiers for repeat
			self.lastModifiersForRepeat = self.lastModifiers[:]
			self.stopRemanence()
		#calculate new gesture with all saved modifier keys

		modifiers = set()
		for modifier in self.lastModifiersForRepeat:
			modifiers.add((modifier.vkCode , modifier.isExtended))
		vkCode  = currentGesture.vkCode 
		scanCode= currentGesture.scanCode 
		extended = currentGesture.isExtended
		for modifier in self.lastModifiersForRepeat:
			extended = extended or modifier.isExtended
		extended = True
		newGesture = KeyboardInputGesture(modifiers, vkCode, scanCode, extended)
		return newGesture
	
	def executeNewGesture(self, gesture):
		try:
			self.executeGesture(gesture, bypassRemanence = True)
		except inputCore.NoInputGestureAction:
			gesture.send()

		except:
			log.error("internal_keyDownEvent", exc_info=True)

	
	def executeGesture(self, gesture, bypassRemanence = False):
		"""Perform the action associated with a gesture.
		@param gesture: The gesture to execute.
		@type gesture: L{InputGesture}
		@raise NoInputGestureAction: If there is no action to perform.
		"""
		if not hasattr(gesture, "noAction"):
			gesture.noAction = False
		if watchdog.isAttemptingRecovery:
			# The core is dead, so don't try to perform an action.
			# This lets gestures pass through unhindered where possible,
			# as well as stopping a flood of actions when the core revives.
			raise NoInputGestureAction
		if  isinstance(gesture, KeyboardInputGesture):
			newGesture = self.manageRemanence(gesture) if not bypassRemanence else None
			if newGesture is not None:
				queueHandler.queueFunction(queueHandler.eventQueue, self.executeNewGesture, newGesture)
				return
		
		script = gesture.script
		focus = api.getFocusObject()
		if focus.sleepMode is focus.SLEEP_FULL or (focus.sleepMode and not getattr(script, 'allowInSleepMode', False)):
			raise NoInputGestureAction
	
		wasInSayAll=False
		if gesture.isModifier:
			if not self.lastModifierWasInSayAll:
				wasInSayAll=self.lastModifierWasInSayAll=sayAllHandler.isRunning()
		elif self.lastModifierWasInSayAll:
			wasInSayAll=True
			self.lastModifierWasInSayAll=False
		else:
			wasInSayAll=sayAllHandler.isRunning()
		if wasInSayAll:
			gesture.wasInSayAll=True
	
		speechEffect = gesture.speechEffectWhenExecuted
		if speechEffect == gesture.SPEECHEFFECT_CANCEL:
			queueHandler.queueFunction(queueHandler.eventQueue, speech.cancelSpeech)
		elif speechEffect in (gesture.SPEECHEFFECT_PAUSE, gesture.SPEECHEFFECT_RESUME):
			queueHandler.queueFunction(queueHandler.eventQueue, speech.pauseSpeech, speechEffect == gesture.SPEECHEFFECT_PAUSE)
	
		if log.isEnabledFor(log.IO) and not gesture.isModifier:
				log.io("Input: %s" % gesture.identifiers[0])
		
		if self._captureFunc:
			try:
				if self._captureFunc(gesture) is False:
					return
			except:
				log.error("Error in capture function, disabling", exc_info=True)
				self._captureFunc = None
		
		if gesture.isModifier:
			if  gesture.noAction :
				gesture.normalizedModifiers = []
				return 
			raise NoInputGestureAction
		log.debug ("MyInputGesture: gesture = %s"%gesture)
		if  isinstance(gesture, KeyboardInputGesture) or isinstance(gesture, BrailleInputGesture) or isinstance(gesture, BrailleDisplayGesture): 
			self.speakGesture(gesture)
		elif config.conf["keyboard"]["speakCommandKeys"] and gesture.shouldReportAsCommand:
			queueHandler.queueFunction(queueHandler.eventQueue, speech.speakMessage, gesture.displayName)
		
		gesture.reportExtra()
	
		# #2953: if an intercepted command Script (script that sends a gesture) is queued
		# then queue all following gestures (that don't have a script) with a fake script so that they remain in order.
		if not script and(bypassRemanence or scriptHandler._numIncompleteInterceptedCommandScripts):
			script=lambda gesture: gesture.send()
	
		if script:
			scriptHandler.queueScript(script, gesture)
			return

		raise NoInputGestureAction
		
	def speakGesture(self, gesture):
		if not gesture.shouldReportAsCommand:
			return
		if self.commandKeysFilter.canSpeakGesture(gesture):
			queueHandler.queueFunction(queueHandler.eventQueue, speech.speakMessage, gesture.displayName)
	
class CommandKeysFilter(object):
	def __init__(self):
		pass

	def checkModifiers(self, modifiers, keyLabel):
		index = -1
		for item in _availableModifierKeysCombination:
			if set(modifiers) == set(item):
				index = _availableModifierKeysCombination.index(item)
				break
		if index>= 0:
			mask = int(self.keysDic[keyLabel.lower()])

			if not mask & (2 ** index):
				return False
				
		return True
		
	def canSpeakGesture(self, gesture):
		speakCommandKeysOption =  config.conf["keyboard"]["speakCommandKeys"] 
		self.keysDic = _addonConfigManager.getCommandKeysSelectiveAnnouncement(speakCommandKeysOption)
		self.keys = []
		for  key in self.keysDic.keys():
			if  int(self.keysDic[key] ):
				self.keys.append(key)
		
		try:
			modifiers = gesture._get_modifierNames()
			keyLabel = gesture._get_mainKeyName()
		except:
			return True

		if not speakCommandKeysOption :
			if keyLabel.lower() in self.keys:
				return self.checkModifiers(modifiers, keyLabel)
			else:
				return False
		
		else:
			if keyLabel.lower() in self.keys:
				return not self.checkModifiers(modifiers, keyLabel)
			else:
				return True
		
		return True
	def updateCommandKeysSelectiveAnnouncement(self, keys, speakCommandKeysOption):
		_addonConfigManager.saveCommandKeysSelectiveAnnouncement(keys, speakCommandKeysOption)


class CommandKeysSelectiveAnnouncementDialog(gui.SettingsDialog):
	# Translators: This is the title for the Command Keys Selective Announcement Dialog.
	title = _("Command keys selective Announcement")

	def __init__(self, parent):
		self.title = makeAddonWindowTitle(self.title)
		super(CommandKeysSelectiveAnnouncementDialog, self).__init__(parent)
	def listInit(self):
		self.keysDic = _addonConfigManager.getCommandKeysSelectiveAnnouncement(self.speakCommandKeysOption)
		self.NVDAKeys = byName.keys()
		from keyLabels import localizedKeyLabels
		self.localizedKeyboardKeyNames= []
		self.keyboardKeys = {}
		for key in self.NVDAKeys:
			if self.isModifier(key):
				continue
			if key in localizedKeyLabels:
				label = localizedKeyLabels[key]
			else:
				label = key
			self.localizedKeyboardKeyNames.append(label)
			self.keyboardKeys[label] = key
		self.localizedKeyboardKeyNames.sort()
		for key in self._keyboardKeys:
			self.localizedKeyboardKeyNames.append(key)
	
	def modifierKeysCombinationListInit (self):
		from keyLabels import localizedKeyLabels
		self.modifierKeys = []
		for item in _availableModifierKeysCombination:
			modifiers = ""
			for key in item:
				label = localizedKeyLabels[key] if key in localizedKeyLabels.keys() else key
				modifiers =  modifiers + "+" +label
			
			modifiers = modifiers[1:]
			self.modifierKeys.append(modifiers)
	
	def updateCheckedKeys(self):
		keys = self.keysDic.keys()
		for index in range(0,self.keyboardKeysListBox.GetCount()):
			label = self.keyboardKeysListBox.GetString(index)
			key = label
			if label in self.keyboardKeys:
				key = self.keyboardKeys[label]
			if key in keys and int(self.keysDic[key]):
				self.keyboardKeysListBox.Check(index)

	def updateModifierKeysList(self, key):
		modifierKeys = int(self.keysDic[key])
		for i in range(0, len(_availableModifierKeysCombination)):
			mask = 2 ** i
			if modifierKeys & mask:
				self.modifierKeysListBox.Check(i)
		
		self.modifierKeysListBox.SetSelection(0)
	
	def makeSettings(self, settingsSizer):
		# init
		self._keyboardKeys  = getKeyboardKeys()
		self.noChange = True
		self.speakCommandKeysOption = config.conf["keyboard"]["speakCommandKeys"] 
		self.listInit()
		self.modifierKeysCombinationListInit()
		# gui
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# the speak command  key flag
		self.commandKeysCheckBox=sHelper.addItem(wx.CheckBox(self,wx.ID_ANY,label=NVDAString("Speak command &keys")))
		self.commandKeysCheckBox.SetValue(config.conf["keyboard"]["speakCommandKeys"])
		# the keyboard key list box
		# Translators: This is a label appearing on Command Keys Selective Announcement Dialog.
		keyboardKeysListText = _("Check &excluded keys:")
		if wx.version().startswith("4"):
			# for wxPython 4
			self.keyboardKeysListBox_ID = wx.NewIdRef()
		else:
			# for wxPython 3
			self.keyboardKeysListBox_ID = wx.NewId()
		self.keyboardKeysListBox  = sHelper.addLabeledControl (keyboardKeysListText ,wx.CheckListBox, id = self.keyboardKeysListBox_ID,name= "KeyboardKeysList" ,choices=self.localizedKeyboardKeyNames, style = wx.LB_SINGLE |wx.WANTS_CHARS)
		if self.keyboardKeysListBox.GetCount():
			self.keyboardKeysListBox.SetSelection(0)

		# the modifiers keys list box
		# Translators: This is a label appearing on Command Keys Selective Announcement Dialog.
		modifierKeysListLabelText = _("W&ith key combination:")
		try:
			self.modifierKeysListBox_ID = wx.NewIdRef()
		except:
			self.modifierKeysListBox_ID = wx.NewId()
		self.modifierKeysListBox  = sHelper.addLabeledControl (modifierKeysListLabelText , wx.CheckListBox, id = self.modifierKeysListBox_ID,name= "ModifierKeysList" ,choices=self.modifierKeys, style = wx.LB_SINGLE |wx.WANTS_CHARS)
		if self.modifierKeysListBox.GetCount():
			self.modifierKeysListBox.SetSelection(0)

		
		# Events
		self.commandKeysCheckBox.Bind(wx.EVT_CHECKBOX,self.onCheckCommandKeysCheckBox)
		self.keyboardKeysListBox.Bind(wx.EVT_LISTBOX, self.onSelectKey)
		self.keyboardKeysListBox.Bind(wx.EVT_CHECKLISTBOX,self.onCheckListBox)
		self.keyboardKeysListBox.Bind(wx.EVT_KEY_DOWN, self.onKeydown)
		self.keyboardKeysListBox.Bind(wx.EVT_SET_FOCUS, self.focusOnCommandKey)
		self.modifierKeysListBox.Bind(wx.EVT_LISTBOX, self.onSelectModifierKeysCombination)
		self.modifierKeysListBox.Bind(wx.EVT_CHECKLISTBOX,self.onCheckModifierKey)
		self.modifierKeysListBox.Bind(wx.EVT_KEY_DOWN, self.onKeydown)
		self.modifierKeysListBox.Bind(wx.EVT_SET_FOCUS, self.focusOnModifierKeysCombination)
		self.updateCheckedKeys()
	
	def postInit(self):
		self.commandKeysCheckBox.SetFocus()

	def reportCheckedState(self, checked = True):
		stateText = controlTypes.stateLabels[controlTypes.STATE_CHECKED] if checked else controlTypes.negativeStateLabels[controlTypes.STATE_CHECKED]
		speakLater(300, stateText)
		
	def onCheckCommandKeysCheckBox(self, evt):
		self.speakCommandKeysOption  = self.commandKeysCheckBox.GetValue()
		modeText = NVDAString("Speak command &keys") if not self.speakCommandKeysOption  else _("Do not speak command &keys") 
		res=  (self.noChange == False) and gui.messageBox(
			# Translators: the text of a message box dialog in Command keys selective announcement dialog.
			_("""Do you want save changes made in "%s" mode""")%modeText,
			# Translators: the title of a message box dialog in command keys selective announcement dialog.
			_("Confirmation"),
			wx.OK|wx.NO|wx.CANCEL|wx.ICON_WARNING)
		if res == wx.CANCEL:
			return
		
		elif res == wx.OK:
			#self.saveCheckedKeys(not self.speakCommandKeysOption  )
			_myInputManager.commandKeysFilter.updateCommandKeysSelectiveAnnouncement(self.keysDic, not speakCommandKeysOption)
		
		self.listInit()
		self.keyboardKeysListBox.SetItems(self.localizedKeyboardKeyNames)
		self.keyboardKeysListBox.SetSelection(0)
		self.updateCheckedKeys()
		self.noChange = True
		evt.Skip()
	
	def onSelectKey(self,evt):
		index = self.keyboardKeysListBox.GetSelection()
		if index >= 0 and self.keyboardKeysListBox.IsChecked(index):
			self.reportCheckedState()
			label = self.keyboardKeysListBox.GetStringSelection()
			key = label
			if label in self.keyboardKeys:
				key = self.keyboardKeys[label]
			self.updateModifierKeysList(key)
			self.modifierKeysListBox.Enable()

				
		elif index >= 0:
			speakLater()
			self.modifierKeysListBox.SetItems(self.modifierKeys)
			self.modifierKeysListBox.Disable()
	
	def onSelectModifierKeysCombination(self,evt):
		index = self.modifierKeysListBox.GetSelection()
		if index >= 0 and self.modifierKeysListBox.IsChecked(index):
			self.reportCheckedState()
		else:
			speakLater()

	
	def focusOnCommandKey(self, evt):
		self.onSelectKey(evt)
	
	def focusOnModifierKeysCombination (self, evt):
		self.onSelectModifierKeysCombination(evt)

	def isModifier(self, key):
		if key.lower()  in ["nvda", "alt", "rightalt", "leftalt", "control","rightcontrol", "leftcontrol", "shift" "rightshift", "leftshift"]:
			return True
		return False
	
	def onCheckListBox(self, evt):
		index = self.keyboardKeysListBox.GetSelection()
		label = self.keyboardKeysListBox.GetStringSelection()
		key = label
		if label in self.keyboardKeys:
			key = self.keyboardKeys[label]
		if self.keyboardKeysListBox.IsChecked(index):
			self.reportCheckedState()
			mask = int()
			for i in range(0, len(_availableModifierKeysCombination)):
				mask = mask + (2 **i)
				
			mask = mask + (2 **len(_availableModifierKeysCombination))
			self.keysDic[key] = mask
			self.updateModifierKeysList(key)
			self.modifierKeysListBox.Enable()
		
		else:
			#del self.keysDic[key]
			self.keysDic[key] = int(0)
			self.reportCheckedState(False)
			self.modifierKeysListBox.SetItems(self.modifierKeys)
			self.modifierKeysListBox.Disable()
		self.noChange = False
		evt.Skip()
	def onCheckModifierKey (self, evt):
		index = self.modifierKeysListBox.GetSelection()
		label = self.keyboardKeysListBox.GetStringSelection()
		key = label
		if label in self.keyboardKeys:
				key = self.keyboardKeys[label]
		if self.modifierKeysListBox.IsChecked(index):
			self.keysDic[key] = int(self.keysDic[key]) | (int(2 ** index))
			self.reportCheckedState()
		else:
			mask = ~(2 ** index)
			self.keysDic[key] = int(self.keysDic[key]) & mask
			self.reportCheckedState(False)
		self.noChange = False
		evt.Skip()
	def onKeydown(self, evt):
		keyCode= evt.GetKeyCode()
		id = evt.GetId()
		if keyCode == wx.WXK_F1: # 340
			# go to next checked key
			if id == self.keyboardKeysListBox_ID:
				l = self.keyboardKeysListBox
				onSelect = self.onSelectKey
			elif id == self.modifierKeysListBox_ID :
				l = self.modifierKeysListBox
				onSelect = self.onSelectModifierKeysCombination
			index = l.GetSelection()
			count = l.GetCount()
			if index < count -1:
				for i in range(index+1, count):
					if l.IsChecked(i):
						l.SetSelection(i)
						onSelect(evt)
						return
			# Translators:  message to the user when there is no more checked command key.
			speakLater(300,_("No more checked command key"))
			return
		
		if keyCode == wx.WXK_F2:# 341
			# go to previous checked key
			if id == self.keyboardKeysListBox_ID:
				l = self.keyboardKeysListBox
				onSelect = self.onSelectKey
			elif id == self.modifierKeysListBox_ID :
				l = self.modifierKeysListBox
				onSelect = self.onSelectModifierKeysCombination
			
			index = l.GetSelection()
			if index > 0:
				while index> 0:
					index = index-1
					if l.IsChecked(index):
						l.SetSelection(index)
						onSelect(evt)
						return
			# Translators: message to the user when there is no more checked command key .
			speakLater(300,_("No more checked command key"))
			return
		
		if keyCode == wx.WXK_TAB:
			shiftDown = evt.ShiftDown()
			if shiftDown:
				wx.Window.Navigate(self.keyboardKeysListBox,wx.NavigationKeyEvent.IsBackward)
			else:
				wx.Window.Navigate(self.keyboardKeysListBox,wx.NavigationKeyEvent.IsForward)
			return
		
		if keyCode == wx.WXK_RETURN and (id == self.keyboardKeysListBox_ID or id == self.modifierKeysListBox_ID):
			self.onOk(evt)
			return
		
		evt.Skip()
	
	def onOk (self, evt):
		speakCommandKeysOption = self.commandKeysCheckBox.GetValue()
		_myInputManager.commandKeysFilter.updateCommandKeysSelectiveAnnouncement(self.keysDic, speakCommandKeysOption)
		super(CommandKeysSelectiveAnnouncementDialog, self).onOk(evt)

	
def initialize():
	global _NVDA_InputManager, _myInputManager
	_NVDA_InputManager = inputCore.manager
	_myInputManager = MyInputManager()
	inputCore.manager = _myInputManager

def terminate():
	global _NVDA_InputManager, _myInputManager
	inputCore.manager = _NVDA_InputManager
	_NVDAInputManager = None
	_myInputManager = None

