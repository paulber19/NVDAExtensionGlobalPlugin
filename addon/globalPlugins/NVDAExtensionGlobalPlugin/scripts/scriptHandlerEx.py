# globalPlugins\NVDAExtensionGlobalPlugin\scripts\scriptHandlerEx.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2022-2023 paulber19


# For patching executeScript and getLastRepeatCount methods
# of NVDA scriptHandler.py file
# cause of wai	ting time between script of 0.5 (500 ms)  . coded in hard.
# For some user, this delay is to small.
# So the add-on give possibility to set this delay.

from logHandler import log
import time
import weakref
from speech.sayAll import SayAllHandler as sayAllHandler

import scriptHandler


def _getMaxTimeBetweenSameScript():
	from ..settings import _addonConfigManager
	delay = _addonConfigManager.getMaximumDelayBetweenSameScript()
	return float(delay) / 1000


def myExecuteScript(script, gesture):
	"""Executes a given script (function) passing it the given gesture.
	It also keeps track of the execution of duplicate scripts with
	in a certain amount of time, and counts how many times this happens.
	Use L{getLastScriptRepeatCount} to find out this count value.
	@param script: the function or method that should be executed.
	The function or method must take an argument of 'gesture'.
	This must be the same value as gesture.script,
	# but its passed in here purely for performance.
	@type script: callable.
	@param gesture: the input gesture that activated this script
	@type gesture: L{inputCore.InputGesture}
	"""
	lastScriptRef = scriptHandler._lastScriptRef() if scriptHandler._lastScriptRef else None
	# We don't allow the same script to be executed from with in itself,
	# but we still should pass the key through
	scriptFunc = getattr(script, "__func__", script)
	if scriptHandler._isScriptRunning and lastScriptRef == scriptFunc:
		return gesture.send()
	scriptHandler._isScriptRunning = True
	resumeSayAllMode = None
	if scriptHandler.willSayAllResume(gesture):
		resumeSayAllMode = sayAllHandler.lastSayAllMode
	try:
		scriptTime = time.time()
		scriptRef = weakref.ref(scriptFunc)
		if (scriptTime - scriptHandler._lastScriptTime) <= _getMaxTimeBetweenSameScript()\
			and scriptFunc == lastScriptRef:
			scriptHandler._lastScriptCount += 1
		else:
			scriptHandler._lastScriptCount = 0
		scriptHandler._lastScriptRef = scriptRef
		scriptHandler._lastScriptTime = scriptTime
		script(gesture)
	except Exception:
		log.exception("error executing script: %s with gesture %r" % (
			script, gesture.displayName))
	finally:
		scriptHandler._isScriptRunning = False
		if resumeSayAllMode is not None:
			sayAllHandler.readText(resumeSayAllMode)


def myGetLastScriptRepeatCount():
	"""The count of how many times the most recent script has been executed.
	This should only be called from with in a script.
	@returns: a value greater or equal to 0.
	If the script has not been repeated it is 0,
	if it has been repeated once its 1, and so forth.
	@rtype: integer
	"""
	if (time.time() - scriptHandler._lastScriptTime) > _getMaxTimeBetweenSameScript():
		count = 0
	else:
		count = scriptHandler._lastScriptCount
	return count


_NVDA_exectuteScript = None
_NVDA_getLastScriptRepeatCount = None


def initialize():
	global _NVDA_exectuteScript, _NVDA_getLastScriptRepeatCount
	# if configured delay is the same as NVDA, don't patch NVDA
	if _getMaxTimeBetweenSameScript() == 0.5:
		return
	_NVDA_exectuteScript = scriptHandler.executeScript
	_NVDA_getLastScriptRepeatCount = scriptHandler.getLastScriptRepeatCount
	scriptHandler.executeScript = myExecuteScript
	scriptHandler.getLastScriptRepeatCount = myGetLastScriptRepeatCount


def terminate():
	global _NVDA_exectuteScript, _NVDA_getLastScriptRepeatCount
	if _NVDA_exectuteScript:
		scriptHandler.executeScript = _NVDA_exectuteScript
		_NVDA_exectuteScript = None
	if _NVDA_getLastScriptRepeatCount:
		scriptHandler.getLastScriptRepeatCount = _NVDA_getLastScriptRepeatCount
		_NVDA_getLastScriptRepeatCount = None
