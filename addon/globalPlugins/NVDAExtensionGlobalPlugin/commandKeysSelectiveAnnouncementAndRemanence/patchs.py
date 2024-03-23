# globalPlugins\NVDAExtensionGlobalPlugin\commandKeysSelectiveAnnouncementAndRemanence\commandKeysSelectiveAnnouncementAndRemanencePatches.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2024 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

from logHandler import log
import inputCore
from inputCore import NoInputGestureAction
from ..settings import isInstall
from ..settings import addonConfig
from keyboardHandler import KeyboardInputGesture


# global variables to save NVDA patched variables and methods
_NVDAInputCoreManager = None
_NVDAInputCoreManagerExecuteGesture = None


def myExecuteGesture(gesture):
	log.debug("MyExecuteGesture: %s,%s" % (gesture.identifiers[0], gesture.__class__))
	try:
		if isinstance(gesture, KeyboardInputGesture):
			log.debug("gesture: vkCode= %s, scanCode= %s, isextended= %s, modifiers= %s" % (
				gesture.vkCode, gesture.scanCode, gesture.isExtended, gesture.modifiers))
			from ..commandKeysSelectiveAnnouncementAndRemanence import _myInputManager
			_myInputManager.executeKeyboardGesture(gesture)
		else:
			log.debug("Gesture executed by: %s.%s" % (
				_NVDAInputCoreManagerExecuteGesture.__module__, _NVDAInputCoreManagerExecuteGesture.__name__))
			_NVDAInputCoreManagerExecuteGesture(gesture)
	except NoInputGestureAction:
		log.debug("myExecuteGesture exception NoInputGestureAction")
		raise NoInputGestureAction


def patche(install=True):
	if not install:
		removePatch()
		return
	if not (
		isInstall(addonConfig.FCT_CommandKeysSelectiveAnnouncement)
		or isInstall(addonConfig.FCT_KeyRemanence)):
		return
	global _NVDAInputCoreManager, _NVDAInputCoreManagerExecuteGesture
	_NVDAInputCoreManager = inputCore.manager
	if _NVDAInputCoreManager .__module__ != "inputCore":
		log.warning(
			"Incompatibility: imput.manager variable has also been patched"
			" probably by another add-on: %s of %s module. "
			"There is a risk of malfunction" % (_NVDAInputCoreManager.__name__, _NVDAInputCoreManager.__module__))
	_NVDAInputCoreManagerExecuteGesture = inputCore.manager.executeGesture
	if _NVDAInputCoreManagerExecuteGesture .__module__ != "inputCore":
		log.warning(
			"Incompatibility: inputCore.manager.executeGesture manager has also been patched probably"
			" by another add-on:"
			" %s of %s. There is a risk of malfunction" % (
				_NVDAInputCoreManagerExecuteGesture .__name__, _NVDAInputCoreManagerExecuteGesture .__module__))
	inputCore.manager.executeGesture = myExecuteGesture
	log.debug(
		"For command selective announcement and key remanence functionnalities,"
		" NVDA core manager executeGesture method has been replaced"
		" by %s method of %s module" % (
			inputCore.manager.executeGesture.__name__, inputCore.manager.executeGesture .__module__))


def removePatch():
	global _NVDAInputCoreManager
	global _NVDAInputCoreManagerExecuteGesture
	if _NVDAInputCoreManager is not None:
		inputCore.manager = _NVDAInputCoreManager
		_NVDAInputCoreManager = None
	if _NVDAInputCoreManagerExecuteGesture is not None:
		inputCore.manager.executeGesture = _NVDAInputCoreManagerExecuteGesture
		_NVDAInputCoreManagerExecuteGesture = None
