# globalPlugins\NVDAExtensionGlobalPlugin\commandKeysSelectiveAnnouncementAndRemanence\specialForGmail.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2019 - 2021 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import keyboardHandler
import queueHandler
import tones
import wx
try:
	# for nvda version >= 2021.2
	from controlTypes.role import Role
	ROLE_EDITABLETEXT = Role.EDITABLETEXT
	from controlTypes.state import State
	STATE_EDITABLE = State.EDITABLE
except (ModuleNotFoundError, AttributeError):
	from controlTypes import STATE_EDITABLE
except AttributeError:
	from controlTypes import ROLE_EDITABLETEXT
import api
import winInputHook
from ..settings import toggleRemanenceForGmailAdvancedOption


# to save current winInputHook keyDownCallback function before hook
_winInputHookKeyDownCallback = None

_remanenceCharacter = None
_taskTimer = None
_trapNextKey = False


def manageRemanenceForGmail(vkCode, scanCode, extended, injected):
	global _remanenceCharacter, _taskTimer, _trapNextKey
	if _taskTimer:
		_taskTimer.Stop()
		_taskTimer = None

	if len(keyboardHandler.currentModifiers):
		return False
	if _trapNextKey:
		_trapNextKey = False
		return False
	gesture = keyboardHandler.KeyboardInputGesture(
		keyboardHandler.currentModifiers, vkCode, scanCode, extended)
	ch = gesture.mainKeyName

	def startTrapNextKey():
		global _trapNextKey
		_trapNextKey = True

	def startRemanence():
		global _taskTimer
		tones.beep(100, 60)
		from ..settings import _addonConfigManager
		delay = _addonConfigManager.getRemanenceDelay()
		_taskTimer = wx.CallLater(delay, stopRemanenceChar)

	def stopRemanenceChar():
		global _remanenceCharacter, _trapNextKey, _taskTimer
		_taskTimer = None
		_trapNextKey = True
		ch = _remanenceCharacter
		_remanenceCharacter = None
		queueHandler.queueFunction(
			queueHandler.eventQueue,
			keyboardHandler.KeyboardInputGesture.fromName(ch).send)

		tones.beep(3000, 20)

	try:
		obj = api.getFocusObject()
		ti = obj.treeInterceptor
	except Exception:
		ti = None
	if (
		obj.role == ROLE_EDITABLETEXT
		or STATE_EDITABLE in obj.states
		or ti is None
		or not ti.passThrough):
		return False
	dci = ti.documentConstantIdentifier
	gmail = "https://mail.google.com/mail/"
	if dci[: len(gmail)] != gmail:
		return False
	if _remanenceCharacter is None and ch in ["g", "h", "*"]:
		_remanenceCharacter = ch
		queueHandler.queueFunction(queueHandler.eventQueue, startRemanence)
		return True
	if _remanenceCharacter is not None:
		_trapNextKey = True
		ch0 = _remanenceCharacter
		_remanenceCharacter = None
		queueHandler.queueFunction(
			queueHandler.eventQueue,
			keyboardHandler.KeyboardInputGesture.fromName(ch0).send)
		queueHandler	.queueFunction(queueHandler.eventQueue, startTrapNextKey)
		queueHandler.queueFunction(
			queueHandler.eventQueue,
			keyboardHandler.KeyboardInputGesture.fromName(ch).send)
		return True
	return False


def internal_keyDownEventEx(vkCode, scanCode, extended, injected):
	if manageRemanenceForGmail(vkCode, scanCode, extended, injected):
		return False
	else:
		return _winInputHookKeyDownCallback(vkCode, scanCode, extended, injected)


def initialize():
	global _winInputHookKeyDownCallback
	if not toggleRemanenceForGmailAdvancedOption(False):
		return
	_winInputHookKeyDownCallback = winInputHook.keyDownCallback
	winInputHook.setCallbacks(keyDown=internal_keyDownEventEx)


def terminate():
	global _winInputHookKeyDownCallback
	if _winInputHookKeyDownCallback is not None:
		winInputHook.setCallbacks(keyDown=_winInputHookKeyDownCallback)
		_winInputHookKeyDownCallback = None
