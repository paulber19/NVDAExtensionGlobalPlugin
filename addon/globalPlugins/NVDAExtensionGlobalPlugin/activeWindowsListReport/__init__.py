# globalplugins\NVDAExtensionGlobalPlugin\activeWindowsListReport\__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2020 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import api
import winUser
import time
import wx
from keyboardHandler import KeyboardInputGesture
import ui
import oleacc
from gui import guiHelper, mainFrame
import NVDAObjects.window
import queueHandler
from ..utils.NVDAStrings import NVDAString
from ..utils import isOpened, makeAddonWindowTitle, getHelpObj
from ..utils import contextHelpEx
from .user32 import (
	SW_SHOWMAXIMIZED, SW_SHOWMINIMIZED, getWindowPlacement, enumWindows,
	getParent, getExtendedWindowStyle,
	WS_EX_APPWINDOW, WS_EX_TOOLWINDOW,
	WS_EX_NOACTIVATE, WS_EX_NOREDIRECTIONBITMAP
)

addonHandler.initTranslation()

# Translators: this is the list of windows titles which do not be displayed.
_windowsToIgnore = _("Start menu|Charm Bar")


def isRealWindow(hWnd):
	lExStyle = getExtendedWindowStyle(hWnd)
	isToolWindow = (lExStyle & WS_EX_TOOLWINDOW) == 0
	isAppWindow = (lExStyle & WS_EX_APPWINDOW) == 0
	hasOwner = winUser.getWindow(hWnd, winUser.GW_OWNER)
	if not winUser.isWindowVisible(hWnd):
		return False
	if getParent(hWnd):
		return False
	if (
		lExStyle & WS_EX_NOACTIVATE
		or lExStyle & WS_EX_NOREDIRECTIONBITMAP
	):
		return False

	if (isToolWindow and not hasOwner) or (
		(isAppWindow and hasOwner)):
		if winUser.getWindowText(hWnd):
			return True
	return False


def getactiveWindows():

	def callback(hWnd, windows):
		# we exclude non real windows
		if not isRealWindow(hWnd):
			return True
		title = winUser.getWindowText(hWnd)
		placement = getWindowPlacement(hwnd)
		if not placement or title in _windowsToIgnore.split("|"):
			return True
		windows.append((title, hWnd))
		return True
	# search for active windows
	windowsList = []
	# we put desktop window at the top of the list
	desktopWindowName = api.getDesktopObject().name
	desktopWindowHandle = api.getDesktopObject().windowHandle
	windowsList.append((desktopWindowName, desktopWindowHandle))
	# we start enumeration
	handlesList = enumWindows()
	for hwnd in handlesList:
		callback(hwnd, windowsList)
	return windowsList


def closeAllWindows(windowsList):
	for f in windowsList:
		if f[0] == api.getDesktopObject().name:
			# it is desktop window, destroy is not possible
			continue
		# window handle to destroy
		hwnd = f[1]
		obj = NVDAObjects.window.Window(windowHandle=hwnd)
		if obj.appModule.appName == "nvda":
			# we cannot destroy nvda windows
			continue
		# we destroy it
		oleacc.AccessibleObjectFromWindow(hwnd, -2).accDoDefaultAction(5)


class ActiveWindowsListDisplay(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	_instance = None
	# help id in the user manual.
	helpObj = getHelpObj("hdr1-2")
	title = None
	delayTimer = None
	lastTypedKeys = ""

	def __new__(cls, *args, **kwargs):
		if ActiveWindowsListDisplay._instance is None:
			return wx.Dialog.__new__(cls)
		return ActiveWindowsListDisplay._instance

	def __init__(self, parent):
		if ActiveWindowsListDisplay._instance is not None:
			return
		ActiveWindowsListDisplay._instance = self
		# Translators: this is the title of active windows list display dialog.
		dialogTitle = _("List of windows")
		ActiveWindowsListDisplay.title = makeAddonWindowTitle(dialogTitle)
		super(ActiveWindowsListDisplay, self).__init__(
			parent,
			wx.ID_ANY,
			ActiveWindowsListDisplay.title,)
		self.activeWindows = []
		self.windowNamesList = []
		self.doGui()

	def windowsListInit(self):
		windowsList = getactiveWindows()
		windowsList.sort()
		self.windowsList = windowsList
		self.activeWindows = []
		self.windowNamesList = []
		for f in windowsList:
			hwnd = f[1]
			# we exclude our window
			myHwnd = self.GetHandle()
			if hwnd == myHwnd:
				continue
			# we fill the list
			placement = getWindowPlacement(hwnd)
			showCmd = placement.showCmd
			self.activeWindows.append(f)
			# normal state, restored state is not signaled
			state = ""
			if showCmd == SW_SHOWMINIMIZED:
				# minimized window
				# Translators: no comment.
				state = _("Minimized")
			elif showCmd == SW_SHOWMAXIMIZED:
				# maximized window
				# Translators: no comment.
				state = _("Maximized")
			# we fill window name list
			self.windowNamesList.append(f[0] + " " + state)

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# the list box
		# Translators: This is the label of the list appearing
		# on Active Windows List Display dialog.
		windowsListLabelText = _("Current &applications") + ":"
		self.windowsListBox = sHelper.addLabeledControl(
			windowsListLabelText,
			wx.ListBox,
			id=wx.ID_ANY,
			choices=self.windowNamesList,
			style=wx.LB_SINGLE,
			size=(700, 280))
		if self.windowsListBox.GetCount():
			self.windowsListBox.SetSelection(0)
		# Buttons
		bHelper = guiHelper.ButtonHelper(wx.HORIZONTAL)
		switchToButton = bHelper.addButton(
			parent=self,
			# Translators: This is a label of a button appearing
			# on active windows list display dialog.
			label=_("&Switch to"))
		switchToButton.SetDefault()
		destroyButton = bHelper.addButton(
			parent=self,
			# Translators: This is a label of a button appearing
			# on active windows list display dialog.
			label=_("&Destroy"))
		destroyAllButton = bHelper.addButton(
			parent=self,
			# Translators: This is a label of a button appearing
			# on active windows list display dialog.
			label=_("Destro&y all"))
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			guiHelper.ButtonHelper(wx.HORIZONTAL))
		closeButton = bHelper.addButton(
			self,
			id=wx.ID_CLOSE,
			label=NVDAString("&Close"))
		mainSizer.Add(sHelper.sizer, border=10, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# Events
		switchToButton.Bind(wx.EVT_BUTTON, self.onSwitchToButton)
		destroyButton.Bind(wx.EVT_BUTTON, self.onDestroyButton)
		destroyAllButton.Bind(wx.EVT_BUTTON, self.onDestroyAllButton)
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

	def selectNextWindow(self, keys):
		curIndex = self.windowsListBox .GetSelection()
		for windowName in self.windowNamesList[curIndex + 1:]:
			if windowName.lower().startswith(self.lastTypedKeys):
				index = self.windowNamesList.index(windowName)
				self.windowsListBox .SetSelection(index)
				return True
		for windowName in self.windowNamesList[:curIndex:]:
			if windowName.lower().startswith(self.lastTypedKeys):
				index = self.windowNamesList.index(windowName)
				self.windowsListBox .SetSelection(index)
				return True
		return False

	def onKeydown(self, evt):
		from ..settings import _addonConfigManager
		keyCode = evt.GetKeyCode()
		if self.delayTimer is not None:
			self.delayTimer.Stop()
			self.delayTimer = None
		if keyCode in [wx.WXK_NUMPAD_DELETE, wx.WXK_DELETE]:  # touche delete
			self.onDestroyButton(0)
			return
		if not (30 <= keyCode <= 255):
			# no alphanumeric character, so  ignore it
			self.lastTypedKeys = ""
			evt.Skip()
			return
		curTime = time.time() * 1000
		if not hasattr(self, "lastKeyDownTime"):
			self.lastKeyDownTime = 0
			self.lastTypedKeys = ""
		delayBetweenKeys = curTime - self.lastKeyDownTime
		self.lastKeyDownTime = curTime
		if delayBetweenKeys > _addonConfigManager.getMaximumDelayBetweenSameScript():
			self.lastTypedKeys = chr(keyCode).lower()
			evt.Skip()
			return
		self.lastTypedKeys += chr(keyCode).lower()
		if len(self.lastTypedKeys) > 1:
			# check if we are already on windowName starting with typed keys
			if self.windowsListBox .GetStringSelection().lower().startswith(self.lastTypedKeys):
				# nothing to do. We are on the good item, just speak it
				wx.CallLater(
					50,
					queueHandler.queueFunction,
					queueHandler.eventQueue,
					ui.message,
					self.windowsListBox .GetStringSelection())
				return
			# set selection on next window  with name starting with lastTypedKeys
			if not self.selectNextWindow(self.lastTypedKeys):
				wx.CallLater(
					50,
					queueHandler.queueFunction,
					queueHandler.eventQueue,
					ui.message,
					self.windowsListBox .GetStringSelection())
			return
		evt.Skip()

	def onDestroyButton(self, evt):
		index = self.windowsListBox.GetSelection()
		# we memorize windows count
		oldWindowsCount = self.windowsListBox.GetCount()
		if self.activeWindows[index][0] == api.getDesktopObject().name:
			# it is desktop window, destroy is not possible
			# Translators: a message announced in active windows list display dialog.
			msg = _("Impossible to destroy desktop window")
			queueHandler.queueFunction(
				queueHandler.eventQueue, ui.message, msg)
			self.windowsListBox.SetSelection(index)
			if not self.windowsListBox.HasFocus():
				self.windowsListBox.SetFocus()
			return
		# window handle to destroy
		hwnd = self.activeWindows[index][1]
		obj = NVDAObjects.window.Window(windowHandle=hwnd)
		if obj.appModule.appName == "nvda":
			# we cannot destroy nvda windows
			# Translators: message to user to announce the window cannot be destroyed.
			msg = _("Impossible to destroy the window")
			queueHandler.queueFunction(
				queueHandler.eventQueue, ui.message, msg)
			self.windowsListBox.SetFocus()
			return
		# we destroy it
		oleacc.AccessibleObjectFromWindow(hwnd, -2).accDoDefaultAction(5)
		time.sleep(0.5)
		# windows list update
		self.windowsListInit()
		self.windowsListBox.Clear()
		time.sleep(0.1)
		self.windowsListBox.AppendItems(self.windowNamesList)
		# check if window is really destroyed
		newWindowsCount = self.windowsListBox.GetCount()
		if oldWindowsCount == newWindowsCount:
			# Translators: message to user to announce the window cannot be destroyed.
			msg = _("Impossible to destroy the window")
			queueHandler.queueFunction(
				queueHandler.eventQueue, ui.message, msg)
			self.windowsListBox.SetSelection(index)
			if not self.windowsListBox.HasFocus():
				self.windowsListBox.SetFocus()
			return
		# we must select the next window
		if newWindowsCount > index + 1:
			self.windowsListBox.SetSelection(index)
		else:
			self.windowsListBox.SetSelection(newWindowsCount - 1)
		# focus on windows list
		self.windowsListBox.SetFocus()

	def onSwitchToButton(self, evt):
		index = self.windowsListBox.GetSelection()
		self.Close()
		if self.activeWindows[index][0] == api.getDesktopObject().name:
			# it is the desktop window, all other windows are minimized
			time.sleep(0.3)
			KeyboardInputGesture.fromName("windows+m").send()
			return

		# handle of the window to put on foreground
		hwnd = self.activeWindows[index][1]
		# we put it on foreground with the focus
		winUser.setForegroundWindow(hwnd)
		time.sleep(0.1)
		winUser.setFocus(hwnd)
		from ..utils import maximizeWindow
		maximizeWindow(hwnd)

	def onDestroyAllButton(self, evt):
		from gui import messageBox
		if messageBox(
			# Translators: message to confirm closing all windows
			_("Are you sure you want to close all windows?"),
			# Translators: dialog title.
			_("Warning"),
			wx.YES | wx.NO | wx.CANCEL | wx.ICON_WARNING) != wx.YES:
			return
		closeAllWindows(self.windowsList)
		self.Close()

	@classmethod
	def run(cls):
		if isOpened(cls):
			return
		mainFrame.prePopup()
		d = cls(mainFrame)
		d.CentreOnScreen()
		d.Show()
		mainFrame.postPopup()
