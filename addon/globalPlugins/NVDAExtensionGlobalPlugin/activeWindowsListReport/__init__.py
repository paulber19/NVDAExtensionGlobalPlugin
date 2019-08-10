#NVDAExtensionGlobalPlugin/activeWindowsListReport/__init__.py
#A part of NVDAExtensionGlobalPlugin add-on
#Copyright (C) 2016  paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import addonHandler
addonHandler.initTranslation()
from logHandler import log
import api
import winUser
import time
import wx
from keyboardHandler import KeyboardInputGesture
import speech
import oleacc
from ..utils.NVDAStrings import NVDAString
from ..utils import isOpened, makeAddonWindowTitle
from gui import guiHelper, mainFrame
import NVDAObjects.window
import queueHandler
import os
import sys
_curAddon = addonHandler.getCodeAddon()
utilitiesPath= os.path.join(_curAddon.path, "utilities")
sys.path.append(utilitiesPath)
import win32gui
del sys.path[-1]
# win32con constant
GW_OWNER = 4
WS_EX_APPWINDOW = 262144
GWL_EXSTYLE = (-20)
WS_EX_TOOLWINDOW = 128
SW_MAXIMIZE = 3


# flags  placement

WPF_RESTORETOMAXIMIZED= 0x0002 
SW_SHOWNORMAL= 1
SW_SHOWMINIMIZED = 2
SW_SHOWMAXIMIZED = 3 

# Translators: this is the list  of  windows titles which do not be displayed.
_windowsToIgnore = _("Start menu|Charm Bar")

def isRealWindow(hWnd): 
	if not winUser.isWindowVisible(hWnd): 
		return False 
	if win32gui.GetParent(hWnd) != 0: 
		return False 
	hasNoOwner = win32gui.GetWindow(hWnd, GW_OWNER) == 0 
	lExStyle = win32gui.GetWindowLong(hWnd, GWL_EXSTYLE) 
	if (((lExStyle & WS_EX_TOOLWINDOW) == 0 and hasNoOwner) 
	or ((lExStyle & WS_EX_APPWINDOW != 0) and not hasNoOwner)): 
		if winUser.getWindowText(hWnd): 
			return True 

	return False 

def getactiveWindows():
	def callback(hWnd, windows):
		# we exclude non real windows
		if not isRealWindow(hWnd):
			return True
		
		title = winUser.getWindowText(hWnd)
		if title in _windowsToIgnore.split("|"):
			return True
		
		placement = win32gui.GetWindowPlacement(hWnd)
		windows.append((title,hWnd )) 
		return True
	
	# search for active windows
	windowsList=[]
	# we put desktop window at the top of the list
	desktopWindowName = api.getDesktopObject().name
	desktopWindowHandle = api.getDesktopObject().windowHandle
	windowsList.append((desktopWindowName, desktopWindowHandle))
	# we start enumeration
	win32gui.EnumWindows(callback, windowsList)
	return windowsList 

class ActiveWindowsListDisplay(wx.Dialog):
	_instance = None
	title = None

	
	def __new__(cls, *args, **kwargs):
		if ActiveWindowsListDisplay._instance is None:
			return wx.Dialog.__new__(cls)
		return ActiveWindowsListDisplay._instance
	
	def __init__(self, parent ): 
		if ActiveWindowsListDisplay._instance is not None:
			return
		ActiveWindowsListDisplay._instance = self
		# Translators: this is the title of active windows list display dialog.
		dialogTitle = _("Windows'list")
		title = ActiveWindowsListDisplay.title =makeAddonWindowTitle(dialogTitle)
		super(ActiveWindowsListDisplay, self).__init__(parent, wx.ID_ANY, title)
		self.activeWindows = []
		self.windowNamesList= []
		self.doGui()
		
	def windowsListInit(self):
		windowsList  = getactiveWindows()
		windowsList.sort()
		self.activeWindows = []
		self.windowNamesList= []
		for  f in windowsList:
			hwnd = f[1]
			# we exclude our window
			myHwnd = self.GetHandle()
			if hwnd == myHwnd:
				continue
			# we fill the list
			self.activeWindows.append(f)
			placement = win32gui.GetWindowPlacement(hwnd)
			flags = placement[0]
			showCmd = placement[1]
			# normal state, restored state is not signaled
			state= ""
			if showCmd == SW_SHOWMINIMIZED:
				# minimized window
				# Translators: no comment.
				state = _("Minimized")
			elif showCmd== SW_SHOWMAXIMIZED:
				# maximized window
				# Translators: no comment.
				state = _("Maximized")
			# we fill window name list
			self.windowNamesList.append(f[0]+ " "+ state)
	
	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# the list box
		# Translators: This is the label of the list  appearing on Active Windows List Display dialog.
		windowsListLabelText=_("Current &applications") +":"
		self.windowsListBox =sHelper.addLabeledControl(windowsListLabelText, wx.ListBox, id = wx.ID_ANY, choices=self.windowNamesList, style = wx.LB_SINGLE, size = (700,280))
		if self.windowsListBox.GetCount():
			self.windowsListBox.SetSelection(0)
		# Buttons
		bHelper= guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: This is a label of a button appearing on active windows list display dialog.
		switchToButton =  bHelper.addButton(self, id = wx.ID_ANY, label=_("&Switch to"))
		switchToButton.SetDefault()
		# Translators: This is a label of a button appearing on active windows list display dialog.
		destroyButton= bHelper.addButton(self, id = wx.ID_ANY, label=_("&Destroy"))
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(guiHelper.ButtonHelper(wx.HORIZONTAL))
		closeButton= bHelper.addButton(self, id = wx.ID_CLOSE, label = NVDAString("&Close"))
		mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# Events
		switchToButton.Bind(wx.EVT_BUTTON,self.onSwitchToButton)
		destroyButton.Bind(wx.EVT_BUTTON,self.onDestroyButton)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.windowsListBox.Bind(wx.EVT_KEY_DOWN, self.onKeydown)
		self.Bind(wx.EVT_ACTIVATE, self.onActivate)
		self.SetEscapeId(wx.ID_CLOSE)
	
	def Destroy(self):
		ActiveWindowsListDisplay._instance = None
		super(ActiveWindowsListDisplay, self).Destroy()

	
	def onActivate(self, evt):
		isActive = evt.GetActive()
		if isActive:
			self.windowsListInit()
			self.windowsListBox.Clear()
			self.windowsListBox.AppendItems(self.windowNamesList)
			if self.windowsListBox.GetCount():
				self.windowsListBox.SetSelection(0)
			self.windowsListBox.SetFocus()
		evt.Skip()
	
	def onKeydown(self, evt):
		keyCode= evt.GetKeyCode()
		if keyCode in  [wx.WXK_NUMPAD_DELETE, wx.WXK_DELETE]: # touche delete
			self.onDestroyButton(0)
			return
		
		evt.Skip()
	
	def onDestroyButton(self, evt):
		index = self.windowsListBox.GetSelection()
		# we memorize windows count
		oldWindowsCount = self.windowsListBox.GetCount()
		if self.activeWindows[index][0] == api.getDesktopObject().name:
			# it is desktop window, destroy is not possible
			# Translators: this is a message announced in active windows list display dialog.
			msg= _("Impossible to destroy desktop window")
			queueHandler.queueFunction(queueHandler.eventQueue,speech.speakMessage, msg)
			#time.sleep(1.6)
			self.windowsListBox.SetSelection(index)
			if not self.windowsListBox.HasFocus():
				self.windowsListBox.SetFocus()
			return
		
		# window handle to destroy
		hwnd = self.activeWindows[index][1]
		obj = NVDAObjects.window.Window(windowHandle = hwnd)
		if obj.appModule.appName == "nvda":
			# we cannot destroy nvda windows
			# Translators: message to the user to announce the window cannot be destroyed.
			msg = _("Impossible to destroy the window")
			queueHandler.queueFunction(queueHandler.eventQueue,speech.speakMessage, msg)
			self.windowsListBox.SetFocus()
			return
		# we destroy it
		oleacc.AccessibleObjectFromWindow(hwnd,-2).accDoDefaultAction (5)
		time.sleep(0.5)
		# windows list update
		self.windowsListInit()
		self.windowsListBox.Clear()
		time.sleep(0.1)
		self.windowsListBox.AppendItems(self.windowNamesList)
		# check if window is really destroyed
		newWindowsCount = self.windowsListBox.GetCount()
		if oldWindowsCount == newWindowsCount:
			# Translators: message to the user to announce the window cannot be destroyed.
			msg= _("Impossible to destroy the window")
			queueHandler.queueFunction(queueHandler.eventQueue,speech.speakMessage, msg)
			self.windowsListBox.SetSelection(index)
			if not self.windowsListBox.HasFocus():
				self.windowsListBox.SetFocus()
			return
			
		# we must select the next window
		if  newWindowsCount > index+1:
			self.windowsListBox.SetSelection(index)
		else:
			self.windowsListBox.SetSelection(newWindowsCount-1)
	
		
		# focus on windows list
		self.windowsListBox.SetFocus()
	
	def onSwitchToButton(self, evt):
		index = self.windowsListBox.GetSelection()
		self.Close()
		# Translators: this is the title of desktop window.
		if self.activeWindows[index][0] == api.getDesktopObject().name:
		# it is the desktop window, all other windows are minimized
			time.sleep(0.3)
			KeyboardInputGesture.fromName("windows+m").send()
			#self.Destroy()
			return

		# handle of the window to put on foreground
		hwnd = self.activeWindows[index][1]
		# we put it on foreground with the focus
		winUser.setForegroundWindow(hwnd)
		time.sleep(0.1)
		winUser.setFocus(hwnd)
		win32gui.ShowWindow(hwnd, SW_MAXIMIZE) 
		
	@classmethod
	def run(cls):
		if isOpened(cls):
			return
		mainFrame.prePopup()
		d = cls(mainFrame)
		d.CentreOnScreen()
		d.Show()
		mainFrame.postPopup()
