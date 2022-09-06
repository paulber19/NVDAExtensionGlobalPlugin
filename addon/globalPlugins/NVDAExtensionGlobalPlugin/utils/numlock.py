# globalPlugins\NVDAExtensionGlobalPlugin\utils\numlock.py
# a part of NVDAExtensionGlobal add-on
# Copyright (C) 2022 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
import addonHandler
import wx
import ui
import winUser
from ..settings.nvdaConfig import _NVDAConfigManager, ANL_NoChange, ANL_Off, ANL_On
addonHandler.initTranslation()


def manageNumlockActivation():
	from keyboardHandler import KeyboardInputGesture
	activateNumlockOption = _NVDAConfigManager.getActivateNumlockOption()
	curNumlockState = winUser.getKeyState(winUser.VK_NUMLOCK)
	if activateNumlockOption != ANL_NoChange:
		if (
			(curNumlockState and (activateNumlockOption == ANL_Off))
			or (not curNumlockState and (activateNumlockOption == ANL_On))
		):
			gesture = KeyboardInputGesture.fromName("numLock")
			gesture.send()
			wx.CallLater(200, gesture.reportExtra)


def reportNumLockState(oldState):
	numlockState = winUser.getKeyState(winUser.VK_NUMLOCK)
	from ..settings import toggleReportNumlockStateAtStartAdvancedOption
	if not toggleReportNumlockStateAtStartAdvancedOption(False):
		return
	if numlockState and numlockState == oldState:
		# Translators: message to user to warn the activated numeric lock state
		msg = _("Warning: Numeric lock is activated")
		ui.message(msg)
