# globalPlugins\NVDAExtensionGlobalPlugin\systemTrayIconsList\__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2020 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

# Script originaly written by Yannick Mayot
import addonHandler
import wx
from oleacc import AccessibleObjectFromWindow, STATE_SYSTEM_INVISIBLE
import time
import winUser
import ctypes
from ..utils.NVDAStrings import NVDAString
from ..utils import isOpened, makeAddonWindowTitle
from gui import guiHelper, mainFrame

addonHandler.initTranslation()


class ListeNotification(wx.Dialog):
	_instance = None

	def __new__(cls, *args, **kwargs):
		if ListeNotification._instance is None:
			return wx.Dialog.__new__(cls)
		return ListeNotification._instance

	def __init__(self, parent):
		if ListeNotification._instance is not None:
			return
		ListeNotification._instance = self
		# Translators: this is the title of NVDA - System tray icons 's list dialog.
		dialogTitle = _("NVDA - System tray icons 's list")
		title = ListeNotification.title = makeAddonWindowTitle(dialogTitle)
		super(ListeNotification, self).__init__(parent, wx.ID_ANY, title)
		self.doGui()

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# the list box
		# Translators: this is the label of the list appearing
		# in NVDA - System tray icons 's list dialog.
		labelText = _("&Icons") + ":"
		self.iconsList = sHelper.addLabeledControl(
			labelText,
			wx.ListBox,
			id=wx.ID_ANY,
			style=wx.LB_SINGLE,
			size=(700, 280))
		self.iconsList.AppendItems(self.getIconsList())
		if self.iconsList.Count:
			self.iconsList.Select(0)
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
		rightClickButton.Bind(wx.EVT_BUTTON, self.onRightMouseButton)
		leftClickButton.Bind(wx.EVT_BUTTON, self.onLeftClick)
		doubleLeftClickButton.Bind(wx.EVT_BUTTON, self.onDoubleLeftClick)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)
		self.iconsList.SetFocus()

	def Destroy(self):
		ListeNotification._instance = None
		super(ListeNotification, self).Destroy()

	def getIconsList(self):
		hd = ctypes.windll.user32.FindWindowExA(None, None, b"Shell_TrayWnd", None)
		path = (b"TrayNotifyWnd", b"SysPager", b"ToolbarWindow32")
		for element in path:
			hd = ctypes.windll.user32.FindWindowExA(hd, 0, element, 0)
		oListe = AccessibleObjectFromWindow(hd, -4)
		location, self.PositionXY = None, []
		max = oListe.accChildCount
		name = ""
		namesList = []
		for i in range(1, max + 1):
			if (oListe.accState(i) & STATE_SYSTEM_INVISIBLE):
				continue
			name = oListe.accName(i)
			if name:
				name = name.replace("\n", ". ")
				name = name.replace("\r", "")
				location = oListe.accLocation(i)
				x = int(location[0]+location[2]/2)
				y = int(location[1] + location[3] / 2)
				self.PositionXY.append((x, y))
				namesList.append(name)
		return namesList

	def getPositionXY(self):
		itemSelected = self.iconsList.GetSelection()
		xyItem = self.PositionXY[itemSelected]
		return xyItem

	def onLeftClick(self, event):
		self.clickLeftMouseButton(1)

	def onRightMouseButton(self, event):
		(x, y) = self.getPositionXY()
		self.Close()
		winUser.setCursorPos(x, y)
		winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTDOWN, 0, 0, None, None)
		time.sleep(0.01)
		winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTUP, 0, 0, None, None)

	def onDoubleLeftClick(self, event):
		self.clickLeftMouseButton(2)

	def clickLeftMouseButton(self, nb):
		self.Close()
		(x, y) = self.getPositionXY()
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
