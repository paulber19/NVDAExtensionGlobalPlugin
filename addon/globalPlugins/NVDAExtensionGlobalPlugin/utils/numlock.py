# globalPlugins\NVDAExtensionGlobalPlugin\utils\numlock.py
# a part of NVDAExtensionGlobal add-on
# Copyright (C) 2022-2023 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
import addonHandler
from logHandler import log
import wx
import ui
import winUser
from ..settings.nvdaConfig import _NVDAConfigManager, ANL_NoChange, ANL_Off, ANL_On
addonHandler.initTranslation()


def manageNumlockActivation():
	log.debug("manageNumlockActivation")
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


def reportActivatedLockState(previousNumlockState, previousCapslockState):
	log.debug("reportActivatedLockState")
	numlockActivation = False
	capslockActivation = False
	from ..settings import (
		toggleReportNumlockStateAtStartAdvancedOption, toggleReportCapslockStateAtStartAdvancedOption)
	if toggleReportNumlockStateAtStartAdvancedOption(False):
		numlockState = winUser.getKeyState(winUser.VK_NUMLOCK)
		numlockActivation = numlockState and numlockState == previousNumlockState
	if toggleReportCapslockStateAtStartAdvancedOption(False):
		capslockState = winUser.getKeyState(winUser.VK_CAPITAL)
		capslockActivation = capslockState and capslockState == previousCapslockState
	if not numlockActivation and not capslockActivation:
		return
	msg = None
	if numlockActivation and capslockActivation:
		# Translators: message to user to warn the enabled capital and numeric lock states
		msg = _("Warning: Numeric lock and capital locks are enabled")
	elif numlockActivation:
		# Translators: message to user to warn the enabled numeric lock state
		msg = _("Warning: Numeric lock is enabled")
	else:
		# Translators: message to user to warn the enabled capital state
		msg = _("Warning: capslock is enabled")
	if msg:
		ui.message(msg)
