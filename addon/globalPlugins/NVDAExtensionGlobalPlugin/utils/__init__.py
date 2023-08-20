# globalPlugins\NVDAExtensionGlobalPlugin/utils/__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016-2023  paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import wx
import api
import ui
import speech
import winUser
import time
from keyboardHandler import KeyboardInputGesture
from logHandler import log
import queueHandler
import config
import core
from ..settings import toggleDialogTitleWithAddonSummaryAdvancedOption

addonHandler.initTranslation()

_curAddon = addonHandler.getCodeAddon()
# addon informations
_addonSummary = _curAddon.manifest['summary']
_addonDocFile = _curAddon.getDocFilePath()


# winuser.h constant
SC_MAXIMIZE = 0xF030
WS_MAXIMIZE = 0x01000000
WM_SYSCOMMAND = 0x112
# window style
# WS_MAXIMIZE:The window is initially maximized
WS_MAXIMIZE = 0x01000000
#  WS_MAXIMIZEBOX: The window has a maximize button.
# Cannot be combined with the WS_EX_CONTEXTHELP style.
# The WS_SYSMENU style must also be specif
WS_MAXIMIZEBOX = 0x00010000
# WS_MINIMIZE : The window is initially minimized.
# ame as the WS_ICONIC style.
WS_MINIMIZE = 0x20000000
# WS_MINIMIZEBOX: The window has a minimize button.
# Cannot be combined with the WS_EX_CONTEXTHELP style.
# The WS_SYSMENU style must also be specif
WS_MINIMIZEBOX = 0x00020000
# global timer
_speakTimer = None


# timer for repeatCount management
GB_scriptTaskTimer = None

_audioOutputDevice = None


def delayScriptTask(func, *args, **kwargs):
	global GB_scriptTaskTimer
	from ..settings import _addonConfigManager
	delay = _addonConfigManager.getMaximumDelayBetweenSameScript()
	GB_scriptTaskTimer = wx.CallLater(delay, func, *args, **kwargs)


def delayScriptTaskWithDelay(delay, func, *args, **kwargs):
	global GB_scriptTaskTimer
	GB_scriptTaskTimer = wx.CallLater(delay, func, *args, **kwargs)


def stopDelayScriptTask():
	global GB_scriptTaskTimer
	if GB_scriptTaskTimer is not None:
		GB_scriptTaskTimer.Stop()
		GB_scriptTaskTimer = None


def clearDelayScriptTask():
	global GB_scriptTaskTimer
	GB_scriptTaskTimer = None


def setAudioOutputDevice(device):
	global _audioOutputDevice
	_audioOutputDevice = device


def getAudioOutputDevice():
	if _audioOutputDevice is None:
		return config.conf["speech"]["outputDevice"]
	return _audioOutputDevice


def isMaximized(hWnd):
	windowStyle = winUser.getWindowStyle(hWnd)
	return (windowStyle & WS_MAXIMIZE)


def maximizeWindow(hWnd):
	windowStyle = winUser.getWindowStyle(hWnd)
	maximized = windowStyle & WS_MAXIMIZE
	if not maximized and windowStyle & WS_MAXIMIZEBOX:
		try:
			winUser.PostMessage(hWnd, WM_SYSCOMMAND, SC_MAXIMIZE, 0)
			log.warning("Window maximized: %s" % winUser.getWindowText(hWnd))
		except Exception:
			pass


def PutWindowOnForeground(hwnd, sleepNb, sleepTime):
	winUser.setForegroundWindow(hwnd)
	for i in [sleepTime] * (sleepNb - 1):
		time.sleep(i)
		if winUser.getForegroundWindow() == hwnd:
			return True
	# last chance
	KeyboardInputGesture.fromName("alt+Tab").send()
	time.sleep(sleepTime)
	if winUser.getForegroundWindow() == hwnd:
		return True
	return False


def isInteger(stringToTest):
	try:
		int(stringToTest)
		return True
	except Exception:
		return False


def speakLater(delay=0, msg=""):
	global _speakTimer

	def callback(msg):
		speech.cancelSpeech()
		queueHandler.queueFunction(queueHandler.eventQueue, ui.message, msg)
	if _speakTimer:
		_speakTimer.Stop()
	if delay == 0 or msg == "":
		return
	_speakTimer = core.callLater(delay, callback, msg)


def isOpened(dialog):
	if dialog._instance is None:
		return False
	# Translators: the label of a message box dialog.
	msg = _(""""%s" dialog is already open""") % dialog.title
	queueHandler.queueFunction(queueHandler.eventQueue, ui.message, msg)
	return True


def makeAddonWindowTitle(dialogTitle):
	if not toggleDialogTitleWithAddonSummaryAdvancedOption(False):
		return dialogTitle
	return "%s - %s" % (_addonSummary, dialogTitle)


def getHelpObj(helpId):
	if helpId is None:
		return None
	return (helpId, _addonDocFile)


def getPositionXY(obj):
	location = obj.location
	(x, y) = (
		int(location[0]) + int(location[2] / 2),
		int(location[1]) + int(location[3] / 2))
	return (x, y)


def mouseClick(obj, rightButton=False, twice=False):
	api.moveMouseToNVDAObject(obj)
	api.setMouseObject(obj)
	if not rightButton:
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN, 0, 0, None, None)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP, 0, 0, None, None)
		if twice:
			time.sleep(0.1)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN, 0, 0, None, None)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP, 0, 0, None, None)
	else:
		winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTDOWN, 0, 0, None, None)
		winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTUP, 0, 0, None, None)
		if twice:
			time.sleep(0.1)
			winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTDOWN, 0, 0, None, None)
			winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTUP, 0, 0, None, None)


def getSpeechMode():
	return speech.getState().speechMode


def setSpeechMode(mode):
	speech.setSpeechMode(mode)


def setSpeechMode_off():
	speech.setSpeechMode(speech.SpeechMode.off)
