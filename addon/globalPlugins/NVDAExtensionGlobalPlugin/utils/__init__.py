#NVDAExtensionGlobalPlugin/utils/__init__.py
#A part of NVDAExtensionGlobalPlugin add-on
#Copyright (C) 2016  paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
import addonHandler
addonHandler.initTranslation()
import wx
import api
import speech
import winUser
import time
from keyboardHandler import KeyboardInputGesture
from logHandler import log
import queueHandler
import config
from gui import messageBox
import core
from .py3Compatibility import longint

# winuser.h constant
SC_MAXIMIZE     = 0xF030
WS_MAXIMIZE         = 0x01000000
WM_SYSCOMMAND = 0x112
# window style
WS_MAXIMIZE = longint(0x01000000) #The window is initially maximized
WS_MAXIMIZEBOX = longint(0x00010000) #The window has a maximize button. Cannot be combined with the WS_EX_CONTEXTHELP style. The WS_SYSMENU style must also be specif 
WS_MINIMIZE = longint(0x20000000) # The window is initially minimized. Same as the WS_ICONIC style.
WS_MINIMIZEBOX= longint(0x00020000) #The window has a minimize button. Cannot be combined with the WS_EX_CONTEXTHELP style. The WS_SYSMENU style must also be specif
# global timer
_speakTimer= None


# timer for repeatCount management
GB_scriptTaskTimer= None

_audioOutputDevice = None

def delayScriptTask( func, *args, **kwargs):		
	global GB_scriptTaskTimer
	from ..settings import _addonConfigManager
	delay= _addonConfigManager.getDelayBetweenSameGesture()
	GB_scriptTaskTimer = wx.CallLater(delay,  func, *args, **kwargs)
	
def stopDelayScriptTask():
	global GB_scriptTaskTimer
	if GB_scriptTaskTimer is not None:
		GB_scriptTaskTimer.Stop()
		GB_scriptTaskTimer = None

def clearDelayScriptTask():
	global GB_scriptTaskTimer
	GB_scriptTaskTimer= None


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
	if not maximized and windowStyle & WS_MAXIMIZEBOX :
		try:
			winUser.PostMessage (hWnd, WM_SYSCOMMAND, SC_MAXIMIZE,0)
			log.warning("Window maximized: %s"%winUser.getWindowText(hWnd))
		except:
			pass


def PutWindowOnForeground(hwnd, sleepNb, sleepTime):
	winUser.setForegroundWindow(hwnd)
	for i in [sleepTime]*(sleepNb-1):
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
	except:
		return False
			
def speakLater(delay = 0, msg = ""):
	global _speakTimer
	def callback(msg):
		speech.cancelSpeech()
		queueHandler.queueFunction(queueHandler.eventQueue, speech.speakMessage, msg)
	
	if _speakTimer:
		_speakTimer.Stop()
	if delay == 0 or msg == "":
		return
	_speakTimer = core.callLater(delay, callback, msg)
def isOpened(dialog, putOnForeground = True):
	if dialog._instance is None:
		return False
	# Translators: the label of a message box dialog.
	msg = _("%s dialog is allready open") %dialog.title
	queueHandler.queueFunction(queueHandler.eventQueue, speech.speakMessage, msg)
	return True
from ..settings  import toggleDialogTitleWithAddonSummaryAdvancedOption 
def makeAddonWindowTitle(dialogTitle):
	if not toggleDialogTitleWithAddonSummaryAdvancedOption (False):
		return dialogTitle
	curAddon = addonHandler.getCodeAddon()
	addonSummary = curAddon.manifest['summary']
	return "%s - %s"%(addonSummary, dialogTitle)



def getPositionXY (obj):
	location=obj.location
	(x, y)=(int(location[0])+int(location[2]/2),int(location[1])+int(location[3]/2))
	return (x, y)

def mouseClick(obj, rightButton=False, twice = False):
	api.moveMouseToNVDAObject(obj)
	api.setMouseObject(obj)
	if not rightButton :
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
		if twice:
			time.sleep(0.1)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
	
	else:
		winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTDOWN,0,0,None,None)
		winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTUP,0,0,None,None)
		if twice:
			time.sleep(0.1)
			winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTDOWN,0,0,None,None)
			winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTUP,0,0,None,None)
