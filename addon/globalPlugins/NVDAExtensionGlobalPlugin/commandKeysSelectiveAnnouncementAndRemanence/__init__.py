# globalPlugins\NVDAExtensionGlobalPlugin\commandKeysSelectiveAnnouncementAndRemanence\__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2018 - 2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from logHandler import log
import winKernel
import scriptHandler
import ui
import speech
import gui
import winUser
import tones
try:
	# for nvda version >= 2021.2
	from controlTypes.state import _stateLabels as stateLabels
	from controlTypes.state import _negativeStateLabels as negativeStateLabels
	from controlTypes.state import State
	STATE_CHECKED = State.CHECKED
except (ModuleNotFoundError, AttributeError):
	from controlTypes import (
		stateLabels, negativeStateLabels,
		STATE_CHECKED)
import inputCore
import watchdog
import queueHandler
import api
import wx
import config

from speech.sayAll import SayAllHandler as sayAllHandler

import time
from vkCodes import byName
import core
from inputCore import NoInputGestureAction
from ..utils.NVDAStrings import NVDAString
from ..utils import speakLater, makeAddonWindowTitle, getHelpObj
from ..settings import (
	_addonConfigManager, toggleOnlyNVDAKeyInRemanenceAdvancedOption, toggleBeepAtRemanenceStartAdvancedOption,
	toggleBeepAtRemanenceEndAdvancedOption, isInstall)
from ..settings.addonConfig import FCT_KeyRemanence
from ..utils.keyboard import getKeyboardKeys
from keyboardHandler import KeyboardInputGesture
from . import specialForGmail
from ..utils import contextHelpEx
addonHandler.initTranslation()
_curAddon = addonHandler.getCodeAddon()

_NVDA_InputManager = None
_myInputManager = None
_NVDA_ExecuteGesture = None
WITHOUT_MODIFIER_BIT_POSITION = 63

_availableModifierKeysCombination = {
	# bit position: modifier keys list of combination
	0: ["NVDA", ],
	1: ["NVDA", "alt"],
	2: ["NVDA", "alt", "control"],
	3: ["NVDA", "alt", "control", "shift"],
	4: ["NVDA", "alt", "shift"],
	5: ["NVDA", "control"],
	6: ["NVDA", "control", "shift"],
	7: ["NVDA", "shift"],
	8: ["alt", ],
	9: ["alt", "control"],
	10: ["alt", "control", "shift"],
	11: ["alt", "shift"],
	12: ["control", ],
	13: ["control", "shift"],
	14: ["shift", ],
	15: ["windows", ],
	16: ["windows", "NVDA", ],
	17: ["windows", "alt"],
	18: ["windows", "NVDA", "alt"],
	19: ["windows", "alt", "control"],
	20: ["windows", "NVDA", "alt", "control"],
	21: ["windows", "alt", "control", "shift"],
	22: ["windows", "NVDA", "alt", "control", "shift"],
	23: ["windows", "alt", "shift"],
	24: ["windows", "NVDA", "alt", "shift"],
	25: ["windows", "control"],
	26: ["windows", "NVDA", "control"],
	27: ["windows", "control", "shift"],
	28: ["windows", "NVDA", "control", "shift"],
	29: ["windows", "shift"],
	30: ["windows", "NVDA", "shift"],
	WITHOUT_MODIFIER_BIT_POSITION: [],
}
CHECKED_KEY_BIT_POSITION = 63
# Translators: label of anyKey item in the excluded keys list.
ANYKEY_LABEL = _("Any key with modifier key combination")
try:
	# for nvda version >= 2023.1
	from inputCore import decide_executeGesture
except ImportError:
	import extensionPoints
	decide_executeGesture = extensionPoints.Decider()
	"""
	Notifies when a gesture is about to be executed,
	and allows components or add-ons to decide whether or not to execute a gesture.
	For example, when controlling a remote system with a connected local braille display,
	braille display gestures should not be executed locally.
	Handlers are called with one argument:
	@param gesture: The gesture that is about to be executed.
	@type gesture: L{InputGesture}
	"""

_numpadKeyNames = ["numpad%s" % str(x) for x in range(1, 10)]


def myExecuteGesture(gesture):
	log.debug("MyExecuteGesture: %s,%s" % (gesture.identifiers[0], gesture.__class__))
	try:
		if isinstance(gesture, KeyboardInputGesture):
			log.debug("gesture: vkCode= %s, scanCode= %s, isextended= %s, modifiers= %s" % (
				gesture.vkCode, gesture.scanCode, gesture.isExtended, gesture.modifiers))

			_myInputManager.executeKeyboardGesture(gesture)
		else:
			log.debug("Gesture executed by: %s.%s" % (_NVDA_ExecuteGesture.__module__, _NVDA_ExecuteGesture.__name__))
			_NVDA_ExecuteGesture(gesture)
	except NoInputGestureAction:
		log.debug("myExecuteGesture exception NoInputGestureAction")
		raise NoInputGestureAction


def isSameGesture(gesture1, gesture2):
	gest1 = (gesture1.vkCode, gesture1.scanCode, gesture1.isExtended)
	gest2 = (gesture2.vkCode, gesture2.scanCode, gesture2.isExtended)
	return gest1 == gest2


_prevGesture = None
_lastPrevGestureTime = time.time()


def shouldTrapGestureRepeat(gesture):
	global _prevGesture, _lastPrevGestureTime
	delay = time.time() - _lastPrevGestureTime
	ret = False
	from ..settings import toggleLimitKeyRepeatsAdvancedOption
	trapOption = toggleLimitKeyRepeatsAdvancedOption(False)
	if trapOption and isinstance(
		gesture, KeyboardInputGesture) and _prevGesture and isinstance(_prevGesture, KeyboardInputGesture):
		from ..settings import _addonConfigManager
		keyRepeatDelay = _addonConfigManager.getKeyRepeatDelay()
		if isSameGesture(gesture, _prevGesture) and delay < keyRepeatDelay / 1000:
			ret = True
	_prevGesture = gesture
	_lastPrevGestureTime = time.time()
	return ret


def shouldExecuteGesture(gesture):
	if not isinstance(gesture, KeyboardInputGesture):
		return True
	if not gesture.isModifier and shouldTrapGestureRepeat(gesture):
		# trap this gesture
		return False
	from ..settings.nvdaConfig import _NVDAConfigManager
	# A part of  Tony's Enhancements addon for NVDA
	# Copyright (C) 2019 Tony Malykh
	if (
		_NVDAConfigManager .toggleBlockInsertKeyOption(False)
		and gesture.vkCode == winUser.VK_INSERT
		and not gesture.isNVDAModifierKey
	):
		tones.beep(500, 50)
		return False
	if (
		_NVDAConfigManager .toggleBlockCapslockKeyOption(False)
		and gesture.vkCode == winUser.VK_CAPITAL and not gesture.isNVDAModifierKey
	):
		tones.beep(500, 50)
		return False
	return True


decide_executeGesture .register(shouldExecuteGesture)


class MyInputManager (object):
	# gesture's sequence to set remanence's activation
	activationSequences = [
		"rightShift,rightControl,rightShift",
		"leftShift,leftControl,leftShift",
	]
	# to save last modifiers used for activation setting
	lastModifiersForActivation = []
	# remanence timer
	remanenceTimer = None
	remanenceActivation = False
	lastModifiers = []
	lastGesture = None
	lastModifierForRepeat = []
	lastGestureTime = None
	enableNumpadNnavigationKeys = False

	def __init__(self):
		super(MyInputManager, self).__init__()
		self.commandKeysFilter = CommandKeysFilter()
		from ..settings import _addonConfigManager
		self.taskTimer = None
		if _addonConfigManager.getRemanenceAtNVDAStart():
			self.taskTimer = wx.CallLater(4000, self.toggleRemanenceActivation)
		self.hasPreviousRemanenceActivationOn = False
		from ..settings import (
			toggleEnableNumpadNavigationModeToggleAdvancedOption,
			toggleActivateNumpadNavigationModeAtStartAdvancedOption)
		if (
			toggleEnableNumpadNavigationModeToggleAdvancedOption(False)
			and toggleActivateNumpadNavigationModeAtStartAdvancedOption(False)):
			self.setNumpadNavigationMode(True)

	def stopRemanence(self, beep=False):
		if self.remanenceActivation is False:
			return
		self.lastModifiers = []
		if self.isRemanenceStarted():
			self.remanenceTimer.Stop()
		self.remanenceTimer = None
		if beep and toggleBeepAtRemanenceEndAdvancedOption(False):
			tones.beep(3000, 20)

	def startRemanence(self, gesture):
		def endRemanence(gesture):
			self.stopRemanence(beep=True)
			if gesture.isNVDAModifierKey:
				gesture.noAction = True
			else:
				gesture.noAction = False
			queueHandler.queueFunction(
				queueHandler.eventQueue, self.executeNewGesture, gesture)
		if self.remanenceActivation is False:
			return
		if not self.isRemanenceStarted():
			if toggleBeepAtRemanenceStartAdvancedOption(False):
				tones.beep(100, 60)
		else:
			self.remanenceTimer.Stop()
		self.remanenceTimer = core.callLater(
			_addonConfigManager.getRemanenceDelay(), endRemanence, gesture)

	def isRemanenceStarted(self):
		if self.remanenceTimer is not None:

			return True
		return False

	def toggleRemanenceActivation(self):
		if self.taskTimer is not None:
			self.taskTimer.Stop()
			self.TaskTimer = None
		if self.remanenceActivation is False:
			self.remanenceActivation = True
			if (
				_addonConfigManager.getRemanenceAtNVDAStart()
				and not self.hasPreviousRemanenceActivationOn):
				# don's say first activation
				msg = None
				self.hasPreviousRemanenceActivationOn = True
			else:
				# Translators: message to user to report keys remanence is on.
				msg = _("Keys's remanence activation on")
			specialForGmail.initialize()
		else:
			self.stopRemanence()
			self.remanenceActivation = False
			# Translators: message to user to report keys remanence is off.
			msg = _("Keys's remanence activation off")
			specialForGmail.terminate()
		addonSummary = _curAddon.manifest['summary']
		if msg is not None:
			queueHandler.queueFunction(
				queueHandler.eventQueue,
				ui.message,
				"%s - %s" % (addonSummary, msg))
			core.callLater(30, ui.message, "%s - %s" % (addonSummary, msg))

	def manageRemanenceActivation(self, gesture):
		if not gesture.isModifier:
			# it's not a modifier key,
			# so forget all previous saved modifiers for activation.
			self.lastModifiersForActivation = []
			return False
		# only modifier key can be in activation sequence
		self.lastModifiersForActivation.append(gesture)
		if len(self.lastModifiersForActivation) > 5:
			self.lastModifiersForActivation = self.lastModifiersForActivation[1:]
		if len(self.lastModifiersForActivation) < 3:
			return False
		tempList = self.lastModifiersForActivation[-3:]
		s = ""
		for modifier in tempList:
			s = s + "," + modifier.mainKeyName
		if s[1:] not in self.activationSequences:
			return False
		self.lastModifiersForActivation = []
		self.toggleRemanenceActivation()
		self.stopRemanence()
		return True

	def isRemanenceKey(self, gesture):
		if (
			toggleOnlyNVDAKeyInRemanenceAdvancedOption(False)
			and gesture.mainKeyName.lower() == "nvda"
			or not toggleOnlyNVDAKeyInRemanenceAdvancedOption(False)
			and gesture.isModifier):
			return True
		return False

	def manageRemanence(self, currentGesture):
		if not isInstall(FCT_KeyRemanence):
			return None
		delayBetweenGestures = time.time() - self.lastGestureTime\
			if self.lastGestureTime else time.time()
		self.lastGestureTime = time.time()
		lastGesture = self.lastGesture
		self.lastGesture = currentGesture
		if self.manageRemanenceActivation(currentGesture):
			return None
		if not self.remanenceActivation:
			return None
		if self.isRemanenceKey(currentGesture):
			# if gesture is the same than last saved modifier , stop remanence
			if self.isRemanenceStarted()\
				and len(self.lastModifiers)\
				and currentGesture.displayName == self.lastModifiers[-1].displayName:
				self.stopRemanence(beep=True)
				return None
			self.lastModifiers.append(currentGesture)
			queueHandler.queueFunction(
				queueHandler.eventQueue, self.startRemanence, currentGesture)
			if not currentGesture.isNVDAModifierKey:
				currentGesture.noAction = True
			return None
		if (currentGesture.mainKeyName.lower() == "capslock"):
			self.stopRemanence()
		if not self.isRemanenceStarted():
			# perhaps it's a gesture repeat
			if (
				(delayBetweenGestures > 0.5)
				or lastGesture is None
				or (
					lastGesture and (currentGesture.displayName) != lastGesture.displayName)
			):
				# no, it's a normal gesture
				self.lastModifiersForRepeat = []
				return None
		else:
			if currentGesture.isModifier:
				self.lastModifiers.append(currentGesture)
				currentGesture.noAction = True
				return None
			# remanence is started, so saved last modifiers for repeat
			self.lastModifiersForRepeat = self.lastModifiers[:]
			self.stopRemanence()
		if len(self.lastModifiersForRepeat) == 0:
			return None

		# calculate new gesture with all saved modifier keys
		modifiers = set()
		for modifier in self.lastModifiersForRepeat:
			modifiers.add((modifier.vkCode, modifier.isExtended))
		vkCode = currentGesture.vkCode
		scanCode = currentGesture.scanCode
		extended = currentGesture.isExtended
		newGesture = KeyboardInputGesture(modifiers, vkCode, scanCode, extended)
		return newGesture

	def executeNewGesture(self, gesture):
		try:
			self.executeKeyboardGesture(gesture, bypassRemanence=True)
		except inputCore.NoInputGestureAction:
			gesture.send()
		except Exception:
			log.error("internal_keyDownEvent", exc_info=True)

	def setNumpadNavigationMode(self, state):
		self.enableNumpadNnavigationKeys = state
		if state:
			# unbind nvda object navigation script keystroke bound to numpad keys
			numpadKeyNames = ["kb:numpad%s" % str(x) for x in range(1, 10)]
			numpadKeyNames.extend(
				["kb:control+numpad%s" % str(x) for x in range(1, 10)])
			numpadKeyNames.extend(["kb:shift+numpad%s" % str(x) for x in range(1, 10)])
			numpadKeyNames .extend(
				["kb:numpadMultiply", "kb:numpadDivide", "kb:numpadPlus"])
			numpadKeyNames .extend(["kb:control+numpadMultiply", "kb:control+numpadDivide", "kb:control+numpadPlus"])
			numpadKeyNames .extend(["kb:shift+numpadMultiply", "kb:shift+numpadDivide", "kb:shift+numpadPlus"])
			d = {"globalCommands.GlobalCommands": {
				"None": numpadKeyNames}}
			_NVDA_InputManager.localeGestureMap.update(d)
		else:
			_NVDA_InputManager.loadLocaleGestureMap()

	def toggleNavigationNumpadMode(self):
		state = not self.enableNumpadNnavigationKeys
		self.setNumpadNavigationMode(state)
		if state:
			# Translators: message to user to report numpad navigation mode change.
			msg = _("Standard use of the numeric keypad enabled")
		else:
			# Translators: message to user to report numpad navigation mode change.
			msg = _("Standard use of the numeric keypad disabled")
		queueHandler.queueFunction(queueHandler.eventQueue, ui.message, msg)

	def getNumpadKeyReplacement(self, gesture):
		if not self.enableNumpadNnavigationKeys:
			return None
		if gesture.isModifier or "nvda" in gesture.displayName.lower():
			# excluded modifier key and numpad keys with NVDA modifiers
			return None
		numpadKeyNames = _numpadKeyNames.copy()
		numpadKeyNames .remove("numpad5")
		if gesture.mainKeyName in numpadKeyNames:
			vkCode = gesture.vkCode
			scanCode = gesture.scanCode
			extended = not gesture.isExtended
			newGesture = KeyboardInputGesture(gesture.modifiers, vkCode, scanCode, extended)
			return newGesture
		return None

	def executeKeyboardGesture(self, gesture, bypassRemanence=False):
		"""Perform the action associated with a gesture.
		@param gesture: The gesture to execute
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

		newGesture = self.manageRemanence(gesture) if not bypassRemanence else None
		if newGesture is not None:
			queueHandler.queueFunction(
				queueHandler.eventQueue, self.executeNewGesture, newGesture)
			return
		newGesture = self.getNumpadKeyReplacement(gesture)
		if newGesture is not None:
			queueHandler.queueFunction(
				queueHandler.eventQueue, self.executeNewGesture, newGesture)
			return

		if not decide_executeGesture.decide(gesture=gesture):
			# A registered handler decided that this gesture shouldn't be executed.
			# Purposely do not raise a NoInputGestureAction here, as that could
			# lead to unexpected behavior for gesture emulation, i.e. the gesture will be send to the system
			# when the decider decided not to execute it.
			log.debug(
				"Gesture execution canceled by handler registered to decide_executeGesture extension point"
			)
			return
		script = gesture.script
		focus = api.getFocusObject()
		if focus.sleepMode is focus.SLEEP_FULL\
			or (focus.sleepMode and not getattr(script, 'allowInSleepMode', False)):
			raise NoInputGestureAction
		wasInSayAll = False
		if gesture.isModifier:
			if not _NVDA_InputManager.lastModifierWasInSayAll:
				wasInSayAll = _NVDA_InputManager.lastModifierWasInSayAll = sayAllHandler.isRunning()
		elif _NVDA_InputManager.lastModifierWasInSayAll:
			wasInSayAll = True
			_NVDA_InputManager.lastModifierWasInSayAll = False
		else:
			wasInSayAll = sayAllHandler.isRunning()
		if wasInSayAll:
			gesture.wasInSayAll = True
		speechEffect = gesture.speechEffectWhenExecuted
		if speechEffect == gesture.SPEECHEFFECT_CANCEL:
			queueHandler.queueFunction(queueHandler.eventQueue, speech.cancelSpeech)
		elif speechEffect in (gesture.SPEECHEFFECT_PAUSE, gesture.SPEECHEFFECT_RESUME):
			queueHandler.queueFunction(
				queueHandler.eventQueue,
				speech.pauseSpeech,
				speechEffect == gesture.SPEECHEFFECT_PAUSE)
		if gesture.shouldPreventSystemIdle:
			winKernel.SetThreadExecutionState(
				winKernel.ES_SYSTEM_REQUIRED | winKernel.ES_DISPLAY_REQUIRED)
		if log.isEnabledFor(log.IO) and not gesture.isModifier:
			_NVDA_InputManager._lastInputTime = time.time()
			log.io("Input: %s" % gesture.identifiers[0])
		if _NVDA_InputManager._captureFunc:
			try:
				if _NVDA_InputManager._captureFunc(gesture) is False:
					return
			except Exception:
				log.error("Error in capture function, disabling", exc_info=True)
				_NVDA_InputManager._captureFunc = None
		if gesture.isModifier:
			if gesture.noAction:
				gesture.normalizedModifiers = []
				return
			raise NoInputGestureAction
		self.speakGesture(gesture)
		if not script:
			gesture.reportExtra()
		# then queue all following gestures
			# (that don't have a script
			# ) with a fake script so that they remain in order.
		if not script and (
			bypassRemanence
			or scriptHandler._numIncompleteInterceptedCommandScripts):
			script = lambda gesture: gesture.send()
		if script:
			scriptHandler.queueScript(script, gesture)
			return
		# Clear memorized last script to avoid getLastScriptRepeatCount detect a repeat
		# in case an unbound gesture is executed between two identical bound gestures.
		queueHandler.queueFunction(queueHandler.eventQueue, scriptHandler.clearLastScript)
		raise NoInputGestureAction

	def speakGesture(self, gesture):
		if not gesture.shouldReportAsCommand:
			return
		if self.commandKeysFilter.forceSpeakGesture(gesture):
			log.warning("Gesture display name spoken: %s" % gesture.displayName)
			queueHandler.queueFunction(
				queueHandler.eventQueue, speech.speakMessage, gesture.displayName)


class CommandKeysFilter(object):
	def __init__(self):
		pass

	def modifiersInAllKeysModifierCombinations(self, modifiers):
		if "anykey" not in self.keysDic:
			return False
		if len(modifiers) == 0 and self.keysDic["anykey"] == 0:
			return True
		index = None
		for (bitPosition, modifierKeys) in _availableModifierKeysCombination.items():
			if set(modifiers) == set(modifierKeys):
				index = bitPosition
				break
		if index is not None:
			mask = abs(int(self.keysDic["anykey"]))
			if mask & int(2 ** index):
				return True
		return False

	def modifiersInKeyModifierCombinations(self, modifiers, keyLabel):
		if keyLabel not in self.keysDic:
			return False
		if keyLabel in self.keysDic and self.keysDic[keyLabel] == 0:
			return False
		index = None
		for (bitPosition, modifierKeys) in _availableModifierKeysCombination.items():
			if set(modifiers) == set(modifierKeys):
				index = bitPosition
				break
		if index is not None:
			mask = abs(int(self.keysDic[keyLabel.lower()]))
			if mask & (2 ** index):
				return True
		return False

	def forceSpeakGesture(self, gesture):
		NVDASpeakCommandKeysOption = config.conf["keyboard"]["speakCommandKeys"]
		from ..settings.nvdaConfig import _NVDAConfigManager
		self.keysDic = _NVDAConfigManager.getCommandKeysSelectiveAnnouncement(
			NVDASpeakCommandKeysOption)
		try:
			modifiers = gesture._get_modifierNames()
			keyLabel = gesture._get_mainKeyName().lower()
		except Exception:
			return True
		if not NVDASpeakCommandKeysOption:
			# we don't speak gesture, check if we must exclude this gesture
			if self.modifiersInAllKeysModifierCombinations(modifiers):
				return True
			force = self.modifiersInKeyModifierCombinations(modifiers, keyLabel)
			return force
		else:
			# we speak gesture, find if we exclude this gesture
			if self.modifiersInAllKeysModifierCombinations(modifiers):
				return False
			force = not self.modifiersInKeyModifierCombinations(modifiers, keyLabel)
			return force

	def updateCommandKeysSelectiveAnnouncement(
		self, keys, speakCommandKeysOption):
		from ..settings.nvdaConfig import _NVDAConfigManager
		_NVDAConfigManager.saveCommandKeysSelectiveAnnouncement(
			keys, speakCommandKeysOption)


class CommandKeysSelectiveAnnouncementDialog(
	contextHelpEx.ContextHelpMixinEx,
	gui.SettingsDialog):
	# Translators: title for the Command Keys Selective Announcement Dialog.
	title = _("Command keys selective Announcement")
	speakTimer = None
	# help in the addon user manual.
	helpObj = getHelpObj("hdr13")

	def __init__(self, parent):
		self.title = makeAddonWindowTitle(self.title)
		super(CommandKeysSelectiveAnnouncementDialog, self).__init__(parent)

	def listInit(self):
		from ..settings.nvdaConfig import _NVDAConfigManager
		self.keysDic = _NVDAConfigManager.getCommandKeysSelectiveAnnouncement(
			self.speakCommandKeysOption)
		self.NVDAKeys = [x for x in byName]
		from keyLabels import localizedKeyLabels

		self.localizedKeyboardKeyNames = []
		self.keyboardKeys = {}
		# label of the first item in the key list
		# if this item is checked, the modifiers key combinations are available for all keys.
		self.localizedKeyboardKeyNames.append(ANYKEY_LABEL)
		self.keyboardKeys[ANYKEY_LABEL] = "anykey"
		for key in self.NVDAKeys:
			# we must exclude some key because shouldReportAsCommand is False
			if key in ["numlock", "capslock"]:
				continue
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

	def modifierKeysCombinationListInit(self):
		from keyLabels import localizedKeyLabels
		self.modifierKeys = [_("any"), ]
		self.modifierKeyBitPositions = [WITHOUT_MODIFIER_BIT_POSITION, ]
		for (bitPosition, modifierKeys) in _availableModifierKeysCombination.items():
			if bitPosition == WITHOUT_MODIFIER_BIT_POSITION:
				# already treated
				continue
			modifiersList = []
			for key in modifierKeys:
				label = localizedKeyLabels[key] if key in localizedKeyLabels else key
				modifiersList.append(label)
			modifiers = " + ".join(modifiersList)
			self.modifierKeys.append(modifiers)
			self.modifierKeyBitPositions.append(bitPosition)

	def updateCheckedKeys(self):
		keys = []
		for key in self.keysDic:
			if self.keysDic[key]:
				keys.append(key)
		for index in range(0, self.keyboardKeysListBox.GetCount()):
			label = self.keyboardKeysListBox.GetString(index)
			key = label
			if label in self.keyboardKeys:
				key = self.keyboardKeys[label]
			if key in keys:
				self.keyboardKeysListBox.Check(index)

	def updateModifierKeysList(self, key):
		modifierKeysMask = abs(int(self.keysDic[key]))
		for bitPosition in self.modifierKeyBitPositions:
			mask = 2 ** bitPosition
			index = self.modifierKeyBitPositions .index(bitPosition)
			if modifierKeysMask & mask:
				self.modifierKeysListBox.Check(index)
			else:
				self.modifierKeysListBox.Check(index, False)
		self.modifierKeysListBox.SetSelection(0)

	def makeSettings(self, settingsSizer):
		# init
		self._keyboardKeys = getKeyboardKeys()
		self.noChange = True
		self.speakCommandKeysOption = config.conf["keyboard"]["speakCommandKeys"]
		self.listInit()
		self.modifierKeysCombinationListInit()
		# gui
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# the speak command key flag
		labelText = NVDAString("Speak c&ommand keys")
		self.commandKeysCheckBox = sHelper.addItem(wx.CheckBox(
			self,
			wx.ID_ANY,
			label=labelText))
		self.commandKeysCheckBox.SetValue(
			config.conf["keyboard"]["speakCommandKeys"])
		# the keyboard key list box
		# Translators: This is a label appearing
		# on Command Keys Selective Announcement Dialog.
		keyboardKeysListText = _("Check &excluded keys:")
		self.keyboardKeysListBox_ID = wx.NewIdRef()
		self.keyboardKeysListBox = sHelper.addLabeledControl(
			keyboardKeysListText,
			wx.CheckListBox,
			id=self.keyboardKeysListBox_ID,
			name="KeyboardKeysList",
			choices=self.localizedKeyboardKeyNames,
			style=wx.LB_SINGLE | wx.WANTS_CHARS)
		if self.keyboardKeysListBox.GetCount():
			self.keyboardKeysListBox.SetSelection(0)

		# the modifiers keys list box
		# Translators: This is a label appearing
		# on Command Keys Selective Announcement Dialog.
		modifierKeysListLabelText = _("Pressed W&ith modifier key combination:")
		try:
			self.modifierKeysListBox_ID = wx.NewIdRef()
		except Exception:
			self.modifierKeysListBox_ID = wx.NewId()
		self.modifierKeysListBox = sHelper.addLabeledControl(
			modifierKeysListLabelText,
			wx.CheckListBox,
			id=self.modifierKeysListBox_ID,
			name="ModifierKeysList",
			choices=self.modifierKeys,
			style=wx.LB_SINGLE | wx.WANTS_CHARS)
		if self.modifierKeysListBox.GetCount():
			self.modifierKeysListBox.SetSelection(0)
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		self.checkAllButton = bHelper.addButton(
			parent=self,
			# Translators: This is a label of a button appearing
			# on Command Keys Selective Announcement Dialog.
			label=_("&Check all modifier combinations"))
		self.checkAllButton.Disable()
		self.unCheckAllButton = bHelper.addButton(
			parent=self,
			# Translators: This is a label of a button appearing
			# on Command Keys Selective Announcement Dialog.
			label=_("&Uncheck all modifier combinations"))
		self.unCheckAllButton.Disable()
		sHelper.addItem(bHelper)
		# Events
		self.commandKeysCheckBox.Bind(
			wx.EVT_CHECKBOX, self.onCheckCommandKeysCheckBox)
		self.keyboardKeysListBox.Bind(wx.EVT_LISTBOX, self.onSelectKey)
		self.keyboardKeysListBox.Bind(wx.EVT_CHECKLISTBOX, self.onCheckListBox)
		self.keyboardKeysListBox.Bind(wx.EVT_KEY_DOWN, self.onKeydown)
		self.keyboardKeysListBox.Bind(wx.EVT_SET_FOCUS, self.focusOnCommandKey)
		self.modifierKeysListBox.Bind(
			wx.EVT_LISTBOX, self.onSelectModifierKeysCombination)
		self.modifierKeysListBox.Bind(wx.EVT_CHECKLISTBOX, self.onCheckModifierKey)
		self.modifierKeysListBox.Bind(wx.EVT_KEY_DOWN, self.onKeydown)
		self.modifierKeysListBox.Bind(
			wx.EVT_SET_FOCUS, self.focusOnModifierKeysCombination)
		self.checkAllButton.Bind(wx.EVT_BUTTON, self.onCheckAllButton)
		self.unCheckAllButton.Bind(wx.EVT_BUTTON, self.onUnCheckAllButton)
		self.updateCheckedKeys()

	def postInit(self):
		self.commandKeysCheckBox.SetFocus()

	def reportCheckedState(self, checked=True):
		def callback(stateText):
			self.speakTimer = None
			queueHandler.queueFunction(
				queueHandler.eventQueue,
				speech.speakMessage,
				stateText)
		stateText = stateLabels[STATE_CHECKED] if checked\
			else negativeStateLabels[STATE_CHECKED]
		if self.speakTimer is not None:
			self.speakTimer.Stop()
		self.speakTimer = wx.CallLater(300, callback, stateText)

	def onCheckCommandKeysCheckBox(self, evt):
		self.speakCommandKeysOption = self.commandKeysCheckBox.GetValue()
		modeText = NVDAString("Speak command &keys")\
			if not self.speakCommandKeysOption else _("Do not speak command &keys")
		if not self.noChange:
			res = gui.messageBox(
				# Translators: the text of a message box dialog
				# in Command keys selective announcement dialog.
				_("""Do you want to save changes made in "%s" mode?""") % modeText,
				# Translators: the title of a message box dialog
				# in command keys selective announcement dialog.
				_("Confirmation"),
				wx.YES | wx.NO | wx.CANCEL | wx.ICON_WARNING)
			if res == wx.YES:
				_myInputManager.commandKeysFilter.updateCommandKeysSelectiveAnnouncement(
					self.keysDic, not self.speakCommandKeysOption)
		self.listInit()
		self.keyboardKeysListBox.SetItems(self.localizedKeyboardKeyNames)
		self.keyboardKeysListBox.SetSelection(0)
		self.updateCheckedKeys()
		self.noChange = True
		evt.Skip()

	def onSelectKey(self, evt):
		index = self.keyboardKeysListBox.GetSelection()
		if index < 0:
			return
		label = self.keyboardKeysListBox.GetStringSelection()
		key = label
		if label in self.keyboardKeys:
			key = self.keyboardKeys[label]
		# to be checked, mask must be not 0
		# possible after unchecking all modifier combination
		mask = self.keysDic[key] if key in self.keysDic else None
		if mask == 0:
			self.keyboardKeysListBox.Check(index, False)
		if self.keyboardKeysListBox.IsChecked(index):
			self.reportCheckedState()
			self.updateModifierKeysList(key)
			self.modifierKeysListBox.Enable()
			self.checkAllButton.Enable()
			self.unCheckAllButton.Enable()
		else:
			speakLater()
			self.modifierKeysListBox.SetItems(self.modifierKeys)
			self.modifierKeysListBox.Disable()
			self.checkAllButton.Disable()
			self.unCheckAllButton.Disable()

	def onSelectModifierKeysCombination(self, evt):
		index = self.modifierKeysListBox.GetSelection()
		if index >= 0 and self.modifierKeysListBox.IsChecked(index):
			self.reportCheckedState()
		else:
			speakLater()

	def focusOnCommandKey(self, evt):
		self.onSelectKey(evt)

	def focusOnModifierKeysCombination(self, evt):
		self.onSelectModifierKeysCombination(evt)

	def isModifier(self, key):
		modifierKeys = [
			"nvda",
			"alt", "rightalt", "leftalt",
			"control", "rightcontrol", "leftcontrol",
			"shift", "rightshift", "leftshift",
			"windows", "leftwindows", "rightwindows",
		]

		if key.lower() in modifierKeys:
			return True
		return False

	def onCheckListBox(self, evt):
		index = self.keyboardKeysListBox.GetSelection()
		keyLabel = self.keyboardKeysListBox.GetStringSelection()
		if keyLabel in self.keyboardKeys:
			keyLabel = self.keyboardKeys[keyLabel]
		if self.keyboardKeysListBox.IsChecked(index):
			self.reportCheckedState()
			mask = int(0)
			for (bitPosition, modifierKeys) in _availableModifierKeysCombination.items():
				mask = mask | int(2 ** bitPosition)
			mask = mask | 2**CHECKED_KEY_BIT_POSITION
			self.keysDic[keyLabel] = mask
			self.updateModifierKeysList(keyLabel)
			self.modifierKeysListBox.Enable()
			self.checkAllButton.Enable()
			self.unCheckAllButton.Enable()
		else:
			mask = int(0)
			self.keysDic[keyLabel] = mask
			self.reportCheckedState(False)
			self.modifierKeysListBox.SetItems(self.modifierKeys)
			self.modifierKeysListBox.Disable()
			self.checkAllButton.Disable()
			self.unCheckAllButton.Disable()
		self.noChange = False
		evt.Skip()

	def onCheckModifierKey(self, evt):
		index = self.modifierKeysListBox.GetSelection()
		label = self.keyboardKeysListBox.GetStringSelection()
		key = label
		if label in self.keyboardKeys:
			key = self.keyboardKeys[label]
		bitPosition = self.modifierKeyBitPositions[index]
		if self.modifierKeysListBox.IsChecked(index):
			mask = abs(int(2 ** bitPosition))
			self.keysDic[key] = int(self.keysDic[key]) | mask
			self.reportCheckedState(True)
		else:
			mask = ~(2 ** bitPosition)
			self.keysDic[key] = abs(int(self.keysDic[key]) & mask)
			self.reportCheckedState(False)
		self.noChange = False
		evt.Skip()

	def onKeydown(self, evt):
		keyCode = evt.GetKeyCode()
		shiftDown = evt.ShiftDown()
		id = evt.GetId()
		if keyCode == wx.WXK_F2 and not shiftDown:  # 340
			# go to next checked key
			if id == self.keyboardKeysListBox_ID:
				tempList = self.keyboardKeysListBox
				onSelect = self.onSelectKey
			elif id == self.modifierKeysListBox_ID:
				tempList = self.modifierKeysListBox
				onSelect = self.onSelectModifierKeysCombination
			index = tempList.GetSelection()
			count = tempList.GetCount()
			if index < count - 1:
				for i in range(index + 1, count):
					if tempList.IsChecked(i):
						tempList.SetSelection(i)
						onSelect(evt)
						return
			# Translators: message to user when there is no more checked command key.
			speakLater(300, _("No more checked command key"))
			return
		if keyCode == wx.WXK_F2 and shiftDown:  # 341
			# go to previous checked key
			if id == self.keyboardKeysListBox_ID:
				tempList = self.keyboardKeysListBox
				onSelect = self.onSelectKey
			elif id == self.modifierKeysListBox_ID:
				tempList = self.modifierKeysListBox
				onSelect = self.onSelectModifierKeysCombination
			index = tempList.GetSelection()
			if index > 0:
				while index > 0:
					index = index - 1
					if tempList.IsChecked(index):
						tempList.SetSelection(index)
						onSelect(evt)
						return
			# Translators: message to user when there is no more checked command key .
			speakLater(300, _("No more checked command key"))
			return
		if keyCode == wx.WXK_TAB:
			shiftDown = evt.ShiftDown()
			if shiftDown:
				wx.Window.Navigate(
					self.keyboardKeysListBox, wx.NavigationKeyEvent.IsBackward)
			else:
				wx.Window.Navigate(
					self.keyboardKeysListBox, wx.NavigationKeyEvent.IsForward)
			return
		if keyCode == wx.WXK_RETURN and (
			id == self.keyboardKeysListBox_ID
			or id == self.modifierKeysListBox_ID):
			self.onOk(evt)
			return
		evt.Skip()

	def CheckOrUnCheckAllModifierCombinationList(self, check=False):
		for index in range(0, self.modifierKeysListBox.Count):
			self.modifierKeysListBox.Check(index, check)
		label = self.keyboardKeysListBox.GetStringSelection()
		key = label
		if label in self.keyboardKeys:
			key = self.keyboardKeys[label]
		mask = int(0)
		for bitPosition in self.modifierKeyBitPositions:
			mask = mask | int(2 ** bitPosition)
		if not check:
			mask = ~mask & mask
		self.keysDic[key] = mask
		self.noChange = False

	def onCheckAllButton(self, evt):
		self.CheckOrUnCheckAllModifierCombinationList(True)

	def onUnCheckAllButton(self, evt):
		self.CheckOrUnCheckAllModifierCombinationList(False)

	def onOk(self, evt):
		speakCommandKeysOption = self.commandKeysCheckBox.GetValue()
		_myInputManager.commandKeysFilter.updateCommandKeysSelectiveAnnouncement(
			self.keysDic, speakCommandKeysOption)
		super(CommandKeysSelectiveAnnouncementDialog, self).onOk(evt)


def initialize():
	global _NVDA_InputManager, _myInputManager, _NVDA_ExecuteGesture
	from inputCore import manager
	_NVDA_InputManager = manager
	if _NVDA_InputManager .__module__ != "inputCore":
		log.warning(
			"Incompatibility: manager of inputCore has been also patched probably by another add-on: %s of %s module. "
			"There is a risk of malfunction" % (_NVDA_InputManager.__name__, _NVDA_InputManager.__module__))
	_NVDA_ExecuteGesture = manager.executeGesture
	if _NVDA_ExecuteGesture .__module__ != "inputCore":
		log.warning(
			"Incompatibility: executeGesture of inputCore manager has been also patched probably by another add-on:"
			" %s of %s. There is a risk of malfunction" % (
				_NVDA_ExecuteGesture .__name__, _NVDA_ExecuteGesture .__module__))
	manager.executeGesture = myExecuteGesture
	log.debug("NVDA core manager executeGesture method has been replaced by %s method of %s module" % (
		manager.executeGesture.__name__, manager.executeGesture .__module__))
	_myInputManager = MyInputManager()
	log.warning("commandKeysSelectiveAnnouncementAndRemanence initialized")


def terminate():
	global _NVDA_InputManager, _myInputManager, _NVDA_ExecuteGesture
	if _NVDA_ExecuteGesture is not None:
		from inputCore import manager
		manager.executeGesture = _NVDA_ExecuteGesture
		_NVDA_ExecuteGesture = None
	specialForGmail.terminate()
	_NVDA_InputManager = None
	_myInputManager = None
