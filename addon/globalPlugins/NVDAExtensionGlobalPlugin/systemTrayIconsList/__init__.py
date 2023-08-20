# globalPlugins\NVDAExtensionGlobalPlugin\systemTrayIconsList\__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Script originaly written by Yannick Mayot

import addonHandler
from logHandler import log
import wx
import time
import winUser
import NVDAObjects
import ctypes
from gui import guiHelper, mainFrame
from ..utils.NVDAStrings import NVDAString
from ..utils import isOpened, makeAddonWindowTitle, getHelpObj
from ..utils import contextHelpEx

addonHandler.initTranslation()

import windowUtils


def findWindow(windowClassPath):
	hd = 0
	for className in windowClassPath:
		hd = ctypes.windll.user32.FindWindowExA(hd, 0, className, 0)
		if not hd:
			log.warning("search is aborted at className: %s" % str(className))
			break
	return hd


class DisplayNotificationIconsList(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	_instance = None
	# help in the user manual.
	helpObj = getHelpObj("hdr1-1")

	def __new__(cls, *args, **kwargs):
		if DisplayNotificationIconsList._instance is None:
			return wx.Dialog.__new__(cls)
		return DisplayNotificationIconsList._instance

	def __init__(self, parent):
		if DisplayNotificationIconsList._instance is not None:
			return
		DisplayNotificationIconsList._instance = self
		# Translators: this is the title of NVDA - System tray icons 's list dialog.
		dialogTitle = _("System tray icons 's list")
		title = DisplayNotificationIconsList.title = makeAddonWindowTitle(dialogTitle)
		super(DisplayNotificationIconsList, self).__init__(parent, wx.ID_ANY, title)
		# init icons list
		self.icons = []
		from winVersion import getWinVer, WinVersion
		winver = getWinVer()
		# w11 22h2 and upper
		if winver >= WinVersion(major=10, minor=0, build=22000):
			# w11 and upper
			self.updateIconsList_w11()
		else:
			# w10 and lower
			self.updateIconsList_w10()
		self.doGui()

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# the list box
		# Translators: this is the label of the list appearing
		# in NVDA - System tray icons 's list dialog.
		labelText = _("&Icons") + ":"
		self.iconsListBox = sHelper.addLabeledControl(
			labelText,
			wx.ListBox,
			id=wx.ID_ANY,
			style=wx.LB_SINGLE,
			size=(700, 280))
		self.iconsListBox.AppendItems([x.name for x in self.icons])

		if self.iconsListBox.Count:
			self.iconsListBox.Select(0)
		# the buttons
		bHelper = guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: this is a button appearing
		# in NVDA - System tray icons 's list dialog.
		rightClickButton = bHelper.addButton(self, label=_("&Right click"))
		rightClickButton.SetDefault()
		# Translators: this is a button appearing
		# in NVDA - System tray icons 's list dialog.
		leftClickButton = bHelper.addButton(self, label=_("&Left click"))
		# Translators: this is a button appearing
		# in NVDA - System tray icons 's list dialog.
		doubleLeftClickButton = bHelper.addButton(
			self, label=_("Dou&ble left click"))
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			guiHelper.ButtonHelper(wx.HORIZONTAL))
		closeButton = bHelper.addButton(
			self, id=wx.ID_CLOSE, label=NVDAString("&Close"))
		mainSizer.Add(
			sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS,
			flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# the events
		rightClickButton.Bind(wx.EVT_BUTTON, self.onRightClickButton)
		leftClickButton.Bind(wx.EVT_BUTTON, self.onLeftClickButton)
		doubleLeftClickButton.Bind(wx.EVT_BUTTON, self.onDoubleLeftClickButton)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)
		self.iconsListBox.SetFocus()

	def Destroy(self):
		DisplayNotificationIconsList._instance = None
		super(DisplayNotificationIconsList, self).Destroy()

	def updateIconsList_w10(self):
		path = (b"Shell_TrayWnd", b"TrayNotifyWnd", b"SysPager", b"ToolbarWindow32")
		hd = findWindow(path)
		if hd:
			window = NVDAObjects.IAccessible.getNVDAObjectFromEvent(hd, -4, 0)
			self.icons.extend([obj for obj in window.children])
		else:
			log.warning("Cannot find window: %s" % ", ".join([str(x) for x in path]))

	def updateIconsList_w11(self):
		self.updateIconsList_w10()
		path = (b"Shell_TrayWnd", b"TrayNotifyWnd", b"Windows.UI.Composition.DesktopWindowContentBridge")
		hd = findWindow(path)
		if hd:
			window = NVDAObjects.IAccessible.getNVDAObjectFromEvent(hd, -4, 0).firstChild
			self.icons.extend([obj for obj in window.children])
		else:
			# after 22h2 build 22621.1344, new object hierarchy
			self.updateIconsList_w11_22h2_22621_1344()

	def updateIconsList_w11_22h2_22621_1344(self):
		h = winUser.FindWindow("Shell_TrayWnd", None)
		# next line from systemTrayList add-on
		hd = windowUtils.findDescendantWindow(
			h, visible=None, controlID=None,
			className="Windows.UI.Input.InputSite.WindowClass")
		if hd:
			window = NVDAObjects.IAccessible.getNVDAObjectFromEvent(hd, -4, 0)
			objs = []
			for obj in window.children:
				if obj.name:
					objs.append(obj)
			self.icons.extend(objs)
		else:
			log.warning("Cannot find window: %s" % "Windows.UI.Input.InputSite.WindowClass")

	def getPosition(self):
		index = self.iconsListBox.GetSelection()
		location = self.icons[index].location
		x = int(location[0] + location[2] / 2)
		y = int(location[1] + location[3] / 2)
		return (x, y)

	def onRightClickButton(self, event):
		(x, y) = self.getPosition()
		self.Close()
		winUser.setCursorPos(x, y)
		winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTDOWN, 0, 0, None, None)
		time.sleep(0.01)
		winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTUP, 0, 0, None, None)

	def onLeftClickButton(self, event):
		self.clickLeftMouseButton(1)

	def onDoubleLeftClickButton(self, event):
		self.clickLeftMouseButton(2)

	def clickLeftMouseButton(self, nb):
		self.Close()
		(x, y) = self.getPosition()
		winUser.setCursorPos(x, y)
		for i in range(nb):
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN, 0, 0, None, None)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP, 0, 0, None, None)

	@classmethod
	def run(cls):
		if isOpened(cls):
			return
		mainFrame.prePopup()
		d = cls(mainFrame)
		d.CentreOnScreen()
		d.Show()
		mainFrame.postPopup()
