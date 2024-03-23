# globalPlugins\NVDAExtensionGlobalPlugin\userInputGestures\inputGesturesExPatches.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2024 Paulber19
# This file is covered by the GNU General Public License.


from logHandler import log
import gui
import wx
from ..utils.NVDAStrings import NVDAString

# global variable to save NVDA patched method
_NVDAGuiMainFrameOnInputGesturesCommand = None


def onInputGesturesCommandEx(evt):
	from .inputGesturesEx import InputGesturesDialogEx
	gui.mainFrame._popupSettingsDialog(InputGesturesDialogEx)


def patche(install=True):
	if not install:
		removePatch()
		return
	global _NVDAGuiMainFrameOnInputGesturesCommand
	if _NVDAGuiMainFrameOnInputGesturesCommand is not None:
		return
	_NVDAGuiMainFrameOnInputGesturesCommand = gui.mainFrame.onInputGesturesCommand
	gui.mainFrame.onInputGesturesCommand = onInputGesturesCommandEx
	log.debug(
		"For user input gestures functionality,"
		" fgui.mainFrame.onInputGesturesCommand has been patched by: %s of %s module "
		% (onInputGesturesCommandEx.__name__, onInputGesturesCommandEx.__module__))

	menus = gui.mainFrame.sysTrayIcon.preferencesMenu.GetMenuItems()
	item = None
	for menuItem in menus:
		if menuItem.GetItemLabel() == NVDAString("I&nput gestures..."):
			item = menuItem
			break
	if item is not None:
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, onInputGesturesCommandEx, item)
		log.debug(
			"For user input gesture functionality,"
			" %s of %s module is now the action for the Input gestures sub-menu " % (
				onInputGesturesCommandEx.__name__, onInputGesturesCommandEx.__module__))


def removePatch():
	global _NVDAGuiMainFrameOnInputGesturesCommand
	if _NVDAGuiMainFrameOnInputGesturesCommand is not None:
		gui.mainFrame.onInputGesturesCommand = _NVDAGuiMainFrameOnInputGesturesCommand
	_NVDAGuiMainFrameOnInputGesturesCommand = None
