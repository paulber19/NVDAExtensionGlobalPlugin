# globalPlugins\NVDAExtensionGlobalPlugin\commandKeysSelectiveAnnouncementAndRemanence\specialForGmail.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2019 - 2024 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import keyboardHandler
from logHandler import log
import queueHandler
import tones
import wx
from controlTypes.role import Role
from controlTypes.state import State
import api
import winInputHook
from ..settings import toggleRemanenceForGmailAdvancedOption


# to save current winInputHook keyDownCallback function before hook
_winInputHookKeyDownCallback = None

_remanenceCharacter = None
_taskTimer = None
_trapNextKey = False
_shouldProcessRemanence = False


def setShouldProcessRemanence():
	global _shouldProcessRemanence
	if not toggleRemanenceForGmailAdvancedOption(False):
		return
	try:
		obj = api.getFocusObject()
		ti = obj.treeInterceptor
	except Exception:
		ti = None
	if (
		obj.role == Role.EDITABLETEXT
		or State.EDITABLE in obj.states
		or ti is None
		or not ti.passThrough):
		_shouldProcessRemanence = False
		return


	dci = ti.get("documentConstantIdentifier", None)
	if dci is None:
		return
	gmail = "https://mail.google.com/mail/"
	if dci[: len(gmail)] != gmail:
		_shouldProcessRemanence = False
		return
	_shouldProcessRemanence = True


def manageRemanenceForGmail(vkCode, scanCode, extended):
	log.debug("manageRemanenceForGmail:  _shouldProcessRemanence = %s" % _shouldProcessRemanence)
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
		log.debug("sending: %s" % ch)
		tones.beep(3000, 20)
	if not _shouldProcessRemanence:
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
		log.debug("sending ch0: %s" % ch0)
		queueHandler.queueFunction(queueHandler.eventQueue, startTrapNextKey)
		queueHandler.queueFunction(
			queueHandler.eventQueue,
			keyboardHandler.KeyboardInputGesture.fromName(ch).send)
		log.debug("sending after ch0: %s" % ch)
		return True
	return False


def internal_keyDownEventEx(vkCode, scanCode, extended, injected):
	if manageRemanenceForGmail(vkCode, scanCode, extended):
		return False
	else:
		return _winInputHookKeyDownCallback(vkCode, scanCode, extended, injected)


def handleRawKey(vkCode, scanCode, extended, pressed):
	log.debug("handleRawKey: %s, pressed= %s" % (vkCode, pressed))
	if pressed and manageRemanenceForGmail(vkCode, scanCode, extended):
		return False
	return True


def initialize():
	log.debug("specialForGMail initialization")
	if not toggleRemanenceForGmailAdvancedOption(False):
		return
	try:
		# for nvda version >= 2025.1
		from inputCore import decide_handleRawKey
		decide_handleRawKey.register(handleRawKey)
		return
	except ImportError:
		global _winInputHookKeyDownCallback
		_winInputHookKeyDownCallback = winInputHook.keyDownCallback
		winInputHook.setCallbacks(keyDown=internal_keyDownEventEx)


def terminate():
	log.debug("specialForGMail terminate")
	try:
		# for nvda version >= 2025.1
		from inputCore import decide_handleRawKey
		decide_handleRawKey.unregister(handleRawKey)
		return
	except ImportError:
		global _winInputHookKeyDownCallback
		if _winInputHookKeyDownCallback is not None:
			winInputHook.setCallbacks(keyDown=_winInputHookKeyDownCallback)
			_winInputHookKeyDownCallback = None
