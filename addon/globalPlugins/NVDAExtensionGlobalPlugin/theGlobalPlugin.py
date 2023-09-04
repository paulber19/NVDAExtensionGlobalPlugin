# globalPlugins\NVDAExtensionGlobalPlugin\__init__.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2023 Paulber19
# This file is covered by the GNU General Public License.


import addonHandler
import globalPluginHandler
from logHandler import log, _getDefaultLogFilePath
import os
import globalVars
import api
import ui
import speech
import braille
import time
import gui
import wx
import appModuleHandler
import globalCommands
import scriptHandler
import queueHandler
import winUser
import NVDAObjects
import mouseHandler
import textInfos
import winKernel
import core
import inputCore
import tones
from functools import wraps
import config
try:
	# for nvda version >= 2021.2
	from characterProcessing import SymbolLevel
	SYMLVL_SOME = SymbolLevel.SOME
except ImportError:
	from characterProcessing import SYMLVL_SOME
from .activeWindowsListReport import ActiveWindowsListDisplay
from .systemTrayIconsList import DisplayNotificationIconsList
# to load configuration
from . import settings
# from .settings import *
from .settings import (
	isInstall, isInstallWithoutGesture,
	getInstallFeatureOption
)
from .settings import addonConfig
from . import commandKeysSelectiveAnnouncementAndRemanence
from . import speechHistory
from .utils.NVDAStrings import NVDAString
from .utils import maximizeWindow, makeAddonWindowTitle, isOpened, getHelpObj
from .utils.secure import inSecureMode
from .utils import getSpeechMode, setSpeechMode, setSpeechMode_off
from .utils import delayScriptTask, stopDelayScriptTask, clearDelayScriptTask
from .utils import messageBox
from .utils.informationDialog import InformationDialog
from .utils import contextHelpEx
from .computerTools.volumeControlScripts import ScriptsForVolume
from .scripts.scriptInfos import scriptsToDocInformations
# to add "run script" button in "Input gestures" dialog
# we patche it
from .userInputGestures import inputGesturesEx
inputGesturesEx.initialize()


addonHandler.initTranslation()

_curAddon = addonHandler.getCodeAddon()
_addonSummary = _curAddon.manifest['summary']
# add-on script categories
SCRCAT_MODULE = str(_addonSummary)


# Below toggle code came from Tyler Spivey's code, with enhancements by Joseph Lee.
def finally_(func, final):
	"""Calls final after func, even if it fails."""
	def wrap(f):
		@wraps(f)
		def new(*args, **kwargs):
			try:
				func(*args, **kwargs)
			finally:
				final()
		return new
	return wrap(final)


def fetchAddon(processID, appName):
	"""Returns an addon for appModule found in the appModules directory, for the given application name.
	@param processID: process ID for it to be associated with
	@type processID: integer
	@param appName: the application name for which an appModule should be found.
	@type appName: unicode or str
	@returns: the addon, or None if not found
	@rtype: addon
	"""
	# First, check whether the module exists.
	# We need to do this separately# because even though an ImportError is raised
	# when a module can't be found, it might also be raised for other reasons.
	# Python 2.x can't properly handle unicode module names, so convert them.
	modName = appName
	if appModuleHandler.doesAppModuleExist(modName):
		try:
			mod = __import__("appModules.%s" % modName, globals(), locals(), ("appModules",))
			# check if we can create appModule
			mod.AppModule(processID, appName)
			path = mod.__file__
			tempList = path.split("\\")
			for i in reversed(list(range(0, len(tempList)))):
				item = tempList[i]
				del tempList[i]
				if item == "appModules":
					break
			if len(tempList):
				path = "\\".join(tempList)
				addon = addonHandler.Addon(path)
				return addon
		except Exception:
			pass
		return None


class NVDAObjectEx (NVDAObjects.NVDAObject):
	def _reportErrorInPreviousWord(self):
		try:
			# self might be a descendant of the text control; e.g. Symphony.
			# We want to deal with the entire text, so use the caret object.
			info = api.getCaretObject().makeTextInfo(textInfos.POSITION_CARET)
			# This gets called for characters which might end a word; e.g. space.
			# The character before the caret is the word end.
			# The one before that is the last of the word, which is what we want.
			info.move(textInfos.UNIT_CHARACTER, -2)
			info.expand(textInfos.UNIT_CHARACTER)
		except Exception:
			# Focus probably moved.
			log.debugWarning("Error fetching last character of previous word", exc_info=True)
			return
		# Fetch the formatting for the last word to see if it is marked as a spelling error,
		# However perform the fetch and check in a future core cycle

		# To give the content control more time to detect and mark the error itself.
		# #12161: MS Word's UIA implementation certainly requires this delay.
		def _delayedDetection():
			try:
				fields = info.getTextWithFields()
			except Exception:
				log.debugWarning("Error fetching formatting for last character of previous word", exc_info=True)
				return
			for command in fields:
				if (
					isinstance(command, textInfos.FieldCommand)
					and command.command == "formatChange"
					and command.field.get("invalid-spelling")
				):
					break
			else:
				# No error.
				return
			#  to report  error depending user configuration: wav, beep, or message

			def reportSpellingError():
				from .settings import _addonConfigManager
				if _addonConfigManager.reportingSpellingErrorsByBeep():
					from tones import beep
					hz = 150
					length = 50
					beep(hz, length)
					from time import sleep
					sleep(2 * length / 1000)
					beep(hz, length)
				elif _addonConfigManager.reportingSpellingErrorsBySound():
					import nvwave
					nvwave.playWaveFile(os.path.join(globalVars.appDir, "waves", "textError.wav"))
				elif _addonConfigManager.reportingSpellingErrorsByMessage():
					ui.message(NVDAString("spelling error"))

			reportSpellingError()
		core.callLater(50, _delayedDetection)


class NVDAExtensionGlobalPlugin(ScriptsForVolume, globalPluginHandler.GlobalPlugin):
	_remanenceCharacter = None
	_trapNextGainFocus = False
	# timer to skip fast caret events
	eventCaretTimer = None
	_repeatBeepOnAudio = None
	scriptCategory = SCRCAT_MODULE
	# a dictionnary to map main script to gestures and install feature option
	_shellGestures = {}
	_mainScriptToGestureAndfeatureOption = {
		"test": (("kb:nvda+control+shift+f11",), None),
		"moduleLayer": (("kb:NVDA+j",), None),
		"reportAppModuleInfoEx": (("kb:nvda+control+f1",), addonConfig.FCT_FocusedApplicationInformations),
		"reportAppProductNameAndVersion": (("kb:nvda+shift+f1",), addonConfig.FCT_FocusedApplicationInformations),
		"ComplexSymbolHelp": (("kb:nvda+shift+f4",), addonConfig.FCT_ComplexSymbols),
		"lastUsedComplexSymbolsList": (None, addonConfig.FCT_ComplexSymbols),
		"report_SystrayIconsOrWindowsList": (("kb:nvda+F11",), addonConfig.FCT_SystrayIconsAndActiveWindowsList),
		"reportCurrentFolder": (("kb:nvda+o",), addonConfig.FCT_CurrentFolderReport),
		"reportPreviousSpeechHistoryRecord": (("kb:nvda+control+f8",), addonConfig.FCT_SpeechHistory),
		"reportCurrentSpeechHistoryRecord": (("kb:nvda+control+f9",), addonConfig.FCT_SpeechHistory),
		"reportNextSpeechHistoryRecord": (("kb:nvda+control+f10",), addonConfig.FCT_SpeechHistory),
		"minuteTimer": (("kb:nvda+shift+f12",), addonConfig.FCT_MinuteTimer),
		"speakForegroundEx": (("kb:nvda+b",), addonConfig.FCT_ForegroundWindowObjectsList),
		"dateTimeEx": (("kb:nvda+f12",), addonConfig.FCT_DateAndTime),
		"copyDateAndTimeToClip": (None, addonConfig.FCT_DateAndTime),
		"restartEx": (("kb:nvda+control+f4",), addonConfig.FCT_RestartInDebugMode),
		"keyboardKeyRenaming": (None, addonConfig.FCT_KeyboardKeyRenaming),
		"commandKeySelectiveAnnouncement": (None, addonConfig.FCT_CommandKeysSelectiveAnnouncement),
		"exploreUserConfigFolder": (None, addonConfig.FCT_ExploreNVDA),
		"exploreProgramFiles": (None, addonConfig.FCT_ExploreNVDA),
		"toggleSwitchVoiceProfileMode": (("kb:nvda+control+shift+p",), addonConfig.FCT_VoiceProfileSwitching),
		"manageVoiceProfileSelectors": (("kb:nvda+shift+control+m",), addonConfig.FCT_VoiceProfileSwitching),
		"previousVoiceProfile": (
			("kb(desktop):nvda+shift+control+leftArrow", "kb(laptop):nvda+control+upArrow",),
			addonConfig.FCT_VoiceProfileSwitching),
		"nextVoiceProfile": (
			("kb(desktop):nvda+shift+control+rightArrow", "kb(laptop):nvda+control+downArrow",),
			addonConfig.FCT_VoiceProfileSwitching),
		"setVoiceProfileSelector1": (("kb:nvda+shift+control+1",), addonConfig.FCT_VoiceProfileSwitching),
		"setVoiceProfileSelector2": (("kb:nvda+shift+control+2",), addonConfig.FCT_VoiceProfileSwitching),
		"setVoiceProfileSelector3": (("kb:nvda+shift+control+3",), addonConfig.FCT_VoiceProfileSwitching),
		"setVoiceProfileSelector4": (("kb:nvda+shift+control+4",), addonConfig.FCT_VoiceProfileSwitching),
		"setVoiceProfileSelector5": (("kb:nvda+shift+control+5",), addonConfig.FCT_VoiceProfileSwitching),
		"setVoiceProfileSelector6": (("kb:nvda+shift+control+6",), addonConfig.FCT_VoiceProfileSwitching),
		"setVoiceProfileSelector7": (("kb:nvda+shift+control+7",), addonConfig.FCT_VoiceProfileSwitching),
		"setVoiceProfileSelector8": (("kb:nvda+shift+control+8",), addonConfig.FCT_VoiceProfileSwitching),
		"openCurrentOrOldNVDALogFile": (("kb:nvda+shift+j",), addonConfig.FCT_OpenCurrentOrOldNVDALogFile),
		"toolsForAddon": (None, addonConfig.FCT_Tools),
		"leftClickAtNavigatorObjectPosition": (("kb:nvda+,",), None),
		"rightClickAtNavigatorObjectPosition": (("kb:nvda+shift+,",), None),
		"globalSettingsDialog": (None, None),
		"profileSettingsDialog": (None, None),
		"toggleNumpadStandardUse": (None, None),
		"toggleNumpadStandardUseWithNumlockKey": (("kb:numlock",), None),
		"reportOrDisplayCurrentSpeechSettings": (None, None),
		"toggleTextAnalyzer": (("kb:nvda+f6",), addonConfig.FCT_TextAnalysis),
		"analyzeCurrentWord": (("kb:nvda+shift+f6",), addonConfig.FCT_TextAnalysis),
		"analyzeCurrentLine": (("kb:nvda+control+f6",), addonConfig.FCT_TextAnalysis),
		"analyzeCurrentSentence": (("kb:nvda+windows+f6",), addonConfig.FCT_TextAnalysis),
		"analyzeCurrentParagraph": (("kb:nvda+shift+control+f6",), addonConfig.FCT_TextAnalysis),
		"findNextTextAnalyzerAlert": (None, addonConfig.FCT_TextAnalysis),
		"findPreviousTextAnalyzerAlert": (None, addonConfig.FCT_TextAnalysis),
		"manageUserConfigurations": (None, None),
		"toggleReportCurrentCaretPosition": (None, None),
		"reportClipboardTextEx": (("kb:nvda+c",), addonConfig.FCT_ClipboardCommandAnnouncement),
		"addToClip": (None, addonConfig.FCT_ClipboardCommandAnnouncement),
		"emptyClipboard": (None, addonConfig.FCT_ClipboardCommandAnnouncement),
		"temporaryAudioOutputDeviceManager": (None, addonConfig.FCT_TemporaryAudioDevice),
		"cancelTemporaryAudioOutputDevice": (None, addonConfig.FCT_TemporaryAudioDevice),
		"setTemporaryAudioOutputDevice": (None, addonConfig.FCT_TemporaryAudioDevice),
		"setOrCancelTemporaryAudioOutputDevice": (None, addonConfig.FCT_TemporaryAudioDevice),
		"activateAddonsActivationDialog": (None, addonConfig.FCT_VariousOutSecureMode),
	}

	# a dictionnary to map shell script to gesture and fonctionality IDs
	_shellScriptToGestureAndFeatureOption = {
		"DisplayAppModuleInfo": ("kb:a", None),
		"foregroundWindowObjectsList": ("kb:b", addonConfig.FCT_ForegroundWindowObjectsList),
		"temporaryAudioOutputDeviceManager": ("kb:c", addonConfig.FCT_TemporaryAudioDevice),
		"cancelTemporaryAudioOutputDevice": ("kb:control+c", addonConfig.FCT_TemporaryAudioDevice),
		"setTemporaryAudioOutputDevice": ("kb:shift+c", addonConfig.FCT_TemporaryAudioDevice),
		"copyDateAndTimeToClip": ("kb:d", addonConfig.FCT_DateAndTime),
		"displayRunningAddonsList": ("kb:e", None),
		"displayFormatting": ("kb:f", None),
		"globalSettingsDialog": ("kb:f1", None),
		"profileSettingsDialog": ("kb:control+f1", None),
		"keyboardKeyRenaming": ("kb:f2", addonConfig.FCT_KeyboardKeyRenaming),
		"commandKeySelectiveAnnouncement": ("kb:f3", addonConfig.FCT_CommandKeysSelectiveAnnouncement),
		"ComplexSymbolHelp": ("kb:f4", addonConfig.FCT_ComplexSymbols,),
		"lastUsedComplexSymbolsList": ("kb:control+f4", addonConfig.FCT_ComplexSymbols,),
		"toggleNumpadStandardUse": ("kb:f5", None),
		"toggleReportCurrentCaretPosition": ("kb:f7", None),
		"toggleTextAnalyzer": ("kb:f6", addonConfig.FCT_TextAnalysis),
		"analyzeCurrentWord": ("kb:shift+f6", addonConfig.FCT_TextAnalysis),
		"analyzeCurrentLine": ("kb:control+f6", addonConfig.FCT_TextAnalysis),
		"analyzeCurrentSentence": ("kb:windows+f6", addonConfig.FCT_TextAnalysis),
		"analyzeCurrentParagraph": ("kb:shift+control+f6", addonConfig.FCT_TextAnalysis),
		"findNextTextAnalyzerAlert": ("kb:alt+f6", addonConfig.FCT_TextAnalysis),
		"findPreviousTextAnalyzerAlert": ("kb:alt+shift+f6", addonConfig.FCT_TextAnalysis),
		"displaySpeechHistoryRecords": ("kb:f9", addonConfig.FCT_SpeechHistory),
		"report_WindowsList": ("kb:f10", addonConfig.FCT_SystrayIconsAndActiveWindowsList),
		"report_SystrayIcons": ("kb:f11", addonConfig.FCT_SystrayIconsAndActiveWindowsList),
		"minuteTimer": ("kb:f12", addonConfig.FCT_MinuteTimer),
		"displayModuleUserGuide": ("kb:g", addonConfig.FCT_VariousOutSecureMode),
		"displayHelp": ("kb:h", None),
		"NVDALogsManagement": ("kb:j", addonConfig.FCT_OpenCurrentOrOldNVDALogFile),
		"closeAllWindows": ("kb:k", addonConfig.FCT_VariousOutSecureMode),
		"manageUserConfigurations": ("kb:n", addonConfig.FCT_VariousOutSecureMode),
		"reportCurrentFolderName": ("kb:o", addonConfig.FCT_CurrentFolderReport),
		"reportCurrentFolderFullPath": ("kb:control+o", addonConfig.FCT_CurrentFolderReport),
		"toggleSwitchVoiceProfileMode": ("kb:p", addonConfig.FCT_VoiceProfileSwitching),
		"activateQuickAddonsActivationDialog": ("kb:q", addonConfig.FCT_VariousOutSecureMode),
		"shutdownComputerDialog": ("kb:r", None),
		"toggleCurrentAppVolumeMute": ("kb:s", addonConfig.FCT_VolumeControl),
		"toolsForAddon": ("kb:t", addonConfig.FCT_Tools),
		"activateUserInputGesturesDialog": ("kb:u", addonConfig.FCT_VariousOutSecureMode),
		"manageVoiceProfileSelectors": ("kb:v", addonConfig.FCT_VoiceProfileSwitching),
		"addToClip": ("kb:x", addonConfig.FCT_ClipboardCommandAnnouncement),
		"emptyClipboard": ("kb:control+x", addonConfig.FCT_ClipboardCommandAnnouncement),
		"reportCurrentSpeechSettings": ("kb:z", None),
		"displayCurrentSpeechSettings": ("kb:control+z", None),
	}

	def __init__(self, *args, **kwargs):
		log.debug("Initializing %s version %s" % (_curAddon.manifest["name"], _curAddon.manifest["version"]))
		super(NVDAExtensionGlobalPlugin, self).__init__(*args, **kwargs)
		# update dictionaries for volume control scripts
		self._mainScriptToGestureAndfeatureOption .update(self._volumeControlMainScriptToGestureAndfeatureOption)
		self._shellScriptToGestureAndFeatureOption .update(self._volumeControlShellScriptToGestureAndFeatureOption)
		self.maximizeWindowTimer = None
		self.installSettingsMenu()
		if isInstall(addonConfig.FCT_CommandKeysSelectiveAnnouncement) or\
			isInstall(addonConfig.FCT_KeyRemanence):
			wx.CallLater(800, commandKeysSelectiveAnnouncementAndRemanence.initialize)
		if isInstall(addonConfig.FCT_ExtendedVirtualBuffer):
			from . import browseModeEx
			self.browseModeExChooseNVDAObjectOverlayClasses = browseModeEx.chooseNVDAObjectOverlayClasses
		from .clipboardCommandAnnouncement import chooseNVDAObjectOverlayClasses
		self.clipboardCommandAnnouncementChooseNVDAObjectOverlayClasses = chooseNVDAObjectOverlayClasses
		if settings.toggleNoDescriptionReportInRibbonOption(False):
			from . import extendedNetUIHWND
			self.extendedNetUIHWNDChooseNVDAObjectOverlayClasses = extendedNetUIHWND.chooseNVDAObjectOverlayClasses
		if isInstall(addonConfig.FCT_SpeechHistory):
			wx.CallLater(800, speechHistory.initialize)
		if isInstall(addonConfig.FCT_KeyboardKeyRenaming):
			settings._addonConfigManager.reDefineKeyboardKeyLabels()
		self.toggling = False
		self._bindGestures()
		self._setShellGestures()
		core.callLater(200, self.installMainAndShellScriptDocs)
		self.switchVoiceProfileMode = "off"
		from .computerTools import audioDevice
		audioDevice.initialize()
		if settings.toggleByPassNoDescriptionAdvancedOption(False):
			messageBox.initialize()
		from .scripts import scriptHandlerEx
		scriptHandlerEx.initialize()
		# start update check if not in secur mode and option is set
		if not inSecureMode():
			from .settings import toggleAutoUpdateGeneralOptions
			if toggleAutoUpdateGeneralOptions(False):
				from .settings import toggleUpdateReleaseVersionsToDevVersionsGeneralOptions
				from . updateHandler import autoUpdateCheck
				autoUpdateCheck(
					toggleUpdateReleaseVersionsToDevVersionsGeneralOptions(False))
		from .ComplexSymbols import newSymbolsHandler
		newSymbolsHandler.initialize()
		config.post_configProfileSwitch .register(self.handlePostConfigProfileSwitch)
		self.handlePostConfigProfileSwitch()
		# dont't use text info to speak typed word  for winConsoleUIA
		from NVDAObjects.UIA.winConsoleUIA import WinConsoleUIA
		WinConsoleUIA.useTextInfoToSpeakTypedWords = False
		# for tonalities volume changes
		from .computerTools import tonesEx
		tonesEx.initialize()
		from core import postNvdaStartup
		postNvdaStartup .register(self.handlePostNVDAStartup)

	def handlePostNVDAStartup(self):
		log.debug("Terminating initialization %s version %s" % (
			_curAddon.manifest["name"], _curAddon.manifest["version"]))
		from . import clipboardCommandAnnouncement
		clipboardCommandAnnouncement .initialize()
		from .computerTools import audioCore
		audioCore.initialize()
		from .utils import numlock
		# to report activated numlock and capslock state
		wx.CallLater(
			2000, numlock.reportActivatedLockState, winUser.getKeyState(
				winUser.VK_NUMLOCK), winUser.getKeyState(winUser.VK_CAPITAL))

		log.info("Loaded %s version %s" % (_curAddon.manifest["name"], _curAddon.manifest["version"]))

	def updateSettingOfSynthSettingsRing(self):

		from .settings.nvdaConfig import _NVDAConfigManager
		from synthDriverHandler import getSynth
		synthName = getSynth().name
		id = _NVDAConfigManager.getLastSelectedSettingInSynthSettingsRing(synthName)
		if id is None:
			return
		from globalVars import settingsRing
		settings = settingsRing.settings
		for s in settings:
			if s.setting.id == id:
				globalVars.settingsRing._current = settings.index(s)

	def handlePostConfigProfileSwitch(self):
		from .utils import numlock
		wx.CallLater(400, numlock.manageNumlockActivation)
		from .textAnalysis.textAnalyzer import updateProfileConfiguration
		updateProfileConfiguration()
		self.updateSettingOfSynthSettingsRing()

	def _bindGestures(self):
		for script in self._mainScriptToGestureAndfeatureOption:
			(gestures, featureID) = self._mainScriptToGestureAndfeatureOption[script]
			if gestures is None:
				continue
			if featureID:
				if not isInstall(featureID) or isInstallWithoutGesture(featureID):
					continue
			for gest in gestures:
				self.bindGesture(gest, script)

	def _setShellGestures(self):
		for script in self._shellScriptToGestureAndFeatureOption:
			(gesture, featureID) = self._shellScriptToGestureAndFeatureOption[script]
			if featureID:
				if not isInstall(featureID):
					continue
			self._shellGestures[gesture] = script

	def installMainAndShellScriptDocs(self):
		for script in scriptsToDocInformations:
			(doc, category, helpId) = self._getScriptDocAndCategory(script)
			commandText = None
			if script in self._shellScriptToGestureAndFeatureOption:
				(identifier, featureID) = self._shellScriptToGestureAndFeatureOption[script]
				source, main = inputCore.getDisplayTextForGestureIdentifier(identifier.lower())
				# Translators: message for indicate shell command in input help mode.
				commandText = _("(command: %s)") % main
			elif script in self._mainScriptToGestureAndfeatureOption:
				(identifier, featureID) = self._mainScriptToGestureAndfeatureOption[script]
			else:
				(identifier, featureID) = (None, None)
			if featureID:
				if not isInstall(featureID):
					continue
			if commandText is not None:
				doc = "%s %s" % (doc, commandText)
			scr = "script_%s" % script
			func = getattr(self, scr)
			func.__func__.__doc__ = doc
			func.__func__.category = category
			# we must remove documentation of replaced nvda global commands scripts
			if hasattr(func, "removeCommandsScript") and (
				(featureID is None) or (
					featureID and not isInstallWithoutGesture(featureID))):
				globalCommandsFunc = getattr(func, "removeCommandsScript")
				globalCommandsFunc.__func__.__doc__ = None

	def _getScriptDocAndCategory(self, script):
		(doc, category, helpId) = scriptsToDocInformations[script]
		if category is None:
			category = SCRCAT_MODULE
		return (doc, category, helpId)

	def installSettingsMenu(self):
		self.prefsMenu = gui.mainFrame.sysTrayIcon.preferencesMenu
		menu = wx.Menu()
		self.NVDAExtensionGlobalPluginSettingsMenu = self.prefsMenu .AppendSubMenu(
			menu,
			"%s..." % _addonSummary,
			# Translators: the tooltip text for addon submenu.
			_("%s add-on configuration menu") % _addonSummary)
		settingsSubMenu = menu.Append(
			wx.ID_ANY,
			# Translators: name of the option in the menu.
			_("Global settings..."),
			"")
		gui.mainFrame.sysTrayIcon.Bind(
			wx.EVT_MENU, self.onSettingsSubMenu, settingsSubMenu)
		profileSettingsSubMenu = menu.Append(
			wx.ID_ANY,
			# Translators: name of the option in the menu.
			_("Current configuration profile settings..."),
			"")
		gui.mainFrame.sysTrayIcon.Bind(
			wx.EVT_MENU, self.onProfileSettingsSubMenu, profileSettingsSubMenu)

		if isInstall(addonConfig.FCT_KeyboardKeyRenaming):
			self.keyboardKeysRenamingMenu = menu.Append(
				wx.ID_ANY,
				# Translators: name of the option in the menu.
				_("Keyboard Keys renaming..."),
				"")
			gui.mainFrame.sysTrayIcon.Bind(
				wx.EVT_MENU,
				self.onKeyboardKeysRenamingMenu,
				self.keyboardKeysRenamingMenu)
		if isInstall(addonConfig.FCT_CommandKeysSelectiveAnnouncement):
			self.commandKeysSelectiveAnnouncementMenu = menu.Append(
				wx.ID_ANY,
				# Translators: name of the option in the menu.
				_("Command keys selective announcement..."),
				"")
			gui.mainFrame.sysTrayIcon.Bind(
				wx.EVT_MENU,
				self.onCommandKeysSelectiveAnnouncementMenu,
				self.commandKeysSelectiveAnnouncementMenu)
		self.resetConfigurationMenu = menu.Append(
			wx.ID_ANY,
			# Translators: name of the option in the menu.
			_("Reset configuration to default values"),
			"")
		gui.mainFrame.sysTrayIcon.Bind(
			wx.EVT_MENU, self.onResetConfiguration, self.resetConfigurationMenu)
		self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
		if isInstall(addonConfig.FCT_ExploreNVDA):
			menu = wx.Menu()
			self.exploreNVDAMenu = self.toolsMenu .AppendSubMenu(
				menu,
				# Translators: the name of addon submenu.
				_("Explore &NVDA"),
				# Translators: the tooltip text for addon submenu.
				_("Menu to explore the NVDA program folder or the user configuration folder"))
			exploreUserConfigFolderMenu = menu.Append(
				wx.ID_ANY,
				# Translators: name of the option in the menu.
				_("My &configuration's folder"),
				"")
			gui.mainFrame.sysTrayIcon.Bind(
				wx.EVT_MENU,
				self.onExploreUserConfigFolderMenu,
				exploreUserConfigFolderMenu)
			exploreProgramFilesMenu = menu.Append(
				wx.ID_ANY,
				# Translators: name of the option in the menu.
				_("NVDA &Program folder"),
				"")
			gui.mainFrame.sysTrayIcon.Bind(
				wx.EVT_MENU, self.onExploreProgramFilesMenu, exploreProgramFilesMenu)
		if isInstall(addonConfig.FCT_ManageUserConfigurations):
			menu = wx.Menu()
			self.manageUserConfigurationMenu = self.toolsMenu .Append(
				wx.ID_ANY,
				# Translators: name of the option in the menu.
				_("Manage user configurations"),
				"")
			gui.mainFrame.sysTrayIcon.Bind(
				wx.EVT_MENU, self.onManageUserConfigurationsMenu, self.manageUserConfigurationMenu)

	def onManageUserConfigurationsMenu(self, evt):
		from .settings.userConfigManager import UserConfigManagementDialog
		wx.CallAfter(UserConfigManagementDialog.run)

	def script_manageUserConfigurations(self, gesture):
		self.onManageUserConfigurationsMenu(None)

	def script_moduleLayer(self, gesture):
		# A run-time binding will occur
		# from which we can perform various layered script commands
		if self.switchVoiceProfileMode == "on":
			self._setSwitchVoiceProfileMode("off")
			return
		# First, check if a second press of the script was done.
		if self.toggling:
			self.script_error(gesture)
			return
		self.bindGestures(self._shellGestures)
		self.toggling = True
		tones.beep(200, 40)

	def getScript(self, gesture):
		from keyboardHandler import KeyboardInputGesture
		if not self.toggling or not isinstance(gesture, KeyboardInputGesture):
			script = globalPluginHandler.GlobalPlugin.getScript(self, gesture)
			return script
		script = globalPluginHandler.GlobalPlugin.getScript(self, gesture)
		if not script:
			script = finally_(self.script_error, self.finish)
			return finally_(script, self.finish)
		if hasattr(script, "noFinish") and script.noFinish:
			return finally_(script, self.noFinish)
		return finally_(script, self.finish)

	def finish(self):
		self.toggling = False
		self.clearGestureBindings()
		self._bindGestures()

	def noFinish(self):
		return

	def script_error(self, gesture):
		tones.beep(420, 40)

	def terminate(self):
		log.debug("Terminating %s" % _curAddon.manifest["name"])
		from .scripts import scriptHandlerEx
		scriptHandlerEx.terminate()
		commandKeysSelectiveAnnouncementAndRemanence.terminate()
		if self._repeatBeepOnAudio is not None:
			self._repeatBeepOnAudio .stop()
			self._repeatBeepOnAudio = None
		from .settings import _addonConfigManager
		_addonConfigManager.terminate()
		speechHistory.terminate()
		for item in ["NVDAExtensionGlobalPluginSettingsMenu", ]:
			if hasattr(self, item):
				self.prefsMenu.Remove(getattr(self, item))
		if hasattr(self, "exploreNVDAMenu"):
			self.toolsMenu .Remove(getattr(self, "exploreNVDAMenu"))
		if hasattr(self, "manageUserConfigurationMenu"):
			self.toolsMenu .Remove(getattr(self, "manageUserConfigurationMenu"))
		messageBox.terminate()
		from .computerTools import tonesEx, audioDevice, audioCore
		audioCore.terminate()
		tonesEx.terminate()
		audioDevice.terminate()
		config.post_configProfileSwitch .unregister(self.handlePostConfigProfileSwitch)
		from core import postNvdaStartup
		postNvdaStartup .unregister(self.handlePostNVDAStartup)
		super(NVDAExtensionGlobalPlugin, self).terminate()

	def _popupSettingsDialog(self, settingsDialog):
		try:
			gui.mainFrame.popupSettingsDialog(settingsDialog)
		except AttributeError:
			gui.mainFrame._popupSettingsDialog(settingsDialog)

	def onSettingsSubMenu(self, evt):
		from .settings.dialog import GlobalSettingsDialog
		wx.CallAfter(self._popupSettingsDialog, GlobalSettingsDialog)

	def onProfileSettingsSubMenu(self, evt):
		from .settings.dialog import ProfileSettingsDialog
		wx.CallAfter(self._popupSettingsDialog, ProfileSettingsDialog)

	def script_globalSettingsDialog(self, gesture):
		from .settings.dialog import GlobalSettingsDialog
		wx.CallAfter(self._popupSettingsDialog, GlobalSettingsDialog)

	def script_profileSettingsDialog(self, gesture):
		from .settings.dialog import ProfileSettingsDialog
		wx.CallAfter(self._popupSettingsDialog, ProfileSettingsDialog)

	def onKeyboardKeysRenamingMenu(self, evt):
		from .keyboardKeyRenaming import KeyboardKeyRenamingDialog
		self._popupSettingsDialog(KeyboardKeyRenamingDialog)

	def onResetConfiguration(self, evt):
		from .settings import _addonConfigManager
		wx.CallAfter(_addonConfigManager.resetConfiguration)

	def exploreFolder(self, path):
		import subprocess
		windir = os.environ["WINDIR"]
		cmd = "{windir}\\explorer.exe \"{path}\"" .format(windir=windir, path=path)
		subprocess.call(cmd, shell=True)

	def onExploreUserConfigFolderMenu(self, evt):
		"""Opens directory containing config files for the current user"""
		import globalVars
		try:
			# configPath is guaranteed to be correct for NVDA, however it will not exist for NVDA_slave.
			path = os.path.abspath(globalVars.appArgs.configPath)
		except AttributeError:
			path = config.getUserDefaultConfigPath()
			if not path:
				log.error("openUserConfigurationDirectory: no user default config path")
				return
			config.initConfigPath(path)
		wx.CallAfter(self.exploreFolder, path)

	def script_exploreUserConfigFolder(self, gesture):
		ui.message(_("Please wait"))
		self.onExploreUserConfigFolderMenu(None)

	def onExploreProgramFilesMenu(self, evt):
		path = os.getcwd()
		wx.CallAfter(self.exploreFolder, path)

	def script_exploreProgramFiles(self, gesture):
		ui.message(_("Please wait"))
		self.onExploreProgramFilesMenu(None)

	def onCommandKeysSelectiveAnnouncementMenu(self, evt):
		self._popupSettingsDialog(
			commandKeysSelectiveAnnouncementAndRemanence.CommandKeysSelectiveAnnouncementDialog)

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		clsList.insert(0, NVDAObjectEx)
		from .WindowsExplorer import updateChooseNVDAOverlayClass
		updateChooseNVDAOverlayClass(obj, clsList)
		self.clipboardCommandAnnouncementChooseNVDAObjectOverlayClasses(obj, clsList)
		if hasattr(self, "extendedNetUIHWNDChooseNVDAObjectOverlayClasses"):
			self.extendedNetUIHWNDChooseNVDAObjectOverlayClasses(obj, clsList)
		if hasattr(self, "browseModeExChooseNVDAObjectOverlayClasses"):
			self.browseModeExChooseNVDAObjectOverlayClasses(obj, clsList)
		try:
			# for nvda version >= 2021.3
			# code comes from  officeDesk.py module of nvda office desk add-on written by Joseph Lee.
			from NVDAObjects.UIA import UIA, SearchField, SuggestionsList, SuggestionListItem
			if isinstance(obj, UIA):
				# Recognize search field found in backstage view.
				if obj.UIAAutomationId == "HomePageSearchBox":
					clsList.insert(0, SearchField)
				# Also recognize suggestions list and its items.
				elif obj.UIAElement.cachedClassName == "NetUIListView" and isinstance(obj.parent.previous, SearchField):
					clsList.insert(0, SuggestionsList)
				elif obj.UIAElement.cachedClassName == "NetUIListViewItem" and isinstance(obj.parent, SuggestionsList):
					clsList.insert(0, SuggestionListItem)
		except ImportError:
			pass

	def maximizeForegroundWindow(self):
		self.maximizeWindowTimer = None
		oForeground = api.getForegroundObject()
		maximizeWindow(oForeground.windowHandle)

	def event_typedCharacter(self, obj, nextHandler, ch):
		from .settings.nvdaConfig import _NVDAConfigManager
		if ch.isalnum() or ch.isspace():
			nextHandler()
			return
		speakCharacter = config.conf["keyboard"]["speakTypedCharacters"]
		if _NVDAConfigManager.toggleSpeakAlphaNumCharsOption(False):
			config.conf["keyboard"]["speakTypedCharacters"] = True
		nextHandler()
		config.conf["keyboard"]["speakTypedCharacters"] = speakCharacter

	def event_foreground(self, obj, nextHandler):
		if settings.toggleAutomaticWindowMaximizationOption(False):
			if self.maximizeWindowTimer is not None:
				self.maximizeWindowTimer.Stop()
			self.maximizeWindowTimer = core.callLater(
				100, self.maximizeForegroundWindow)
		nextHandler()

	def event_gainFocus(self, obj, nextHandler):
		if self._trapNextGainFocus:
			self._trapNextGainFocus = False
			return
		nextHandler()

	def event_caret(self, obj, nextHandler):

		if self.eventCaretTimer is not None:
			self.eventCaretTimer.Stop()
			self.eventCaretTimer = None
		nextHandler()

	def script_copyDateAndTimeToClip(self, gesture):
		dateText = winKernel.GetDateFormatEx(
			winKernel.LOCALE_NAME_USER_DEFAULT, winKernel.DATE_LONGDATE, None, None)
		if settings.toggleReportTimeWithSecondsOption(False):
			timeText = winKernel.GetTimeFormatEx(
				winKernel.LOCALE_NAME_USER_DEFAULT, None, None, None)
		else:
			timeText = winKernel.GetTimeFormatEx(
				winKernel.LOCALE_NAME_USER_DEFAULT, winKernel.TIME_NOSECONDS, None, None)
		msg = "%s %s" % (dateText, timeText)
		if api.copyToClip(msg):
			# Translators: message to report date and time copy to clipboard.
			ui.message(_("{0} copied to clipboard").format(msg))
		else:
			# Translators: Presented when unable to copy to the clipboard because of an error.
			ui.message(NVDAString("Unable to copy"))

	# modified nvda scripts
	def script_dateTimeEx(self, gesture):
		def callback(action="time"):
			speech.cancelSpeech()
			if action == "copyToClip":
				self.script_copyDateAndTimeToClip(gesture)
				return
			if action == "date":
				text = winKernel.GetDateFormatEx(winKernel.LOCALE_NAME_USER_DEFAULT, winKernel.DATE_LONGDATE, None, None)
				ui.message(text)
				return
			curLevel = config.conf["speech"]["symbolLevel"]
			config.conf["speech"]["symbolLevel"] = SYMLVL_SOME
			if settings.toggleReportTimeWithSecondsOption(False):
				text = winKernel.GetTimeFormatEx(
					winKernel.LOCALE_NAME_USER_DEFAULT, None, None, None)
			else:
				text = winKernel.GetTimeFormatEx(
					winKernel.LOCALE_NAME_USER_DEFAULT, winKernel.TIME_NOSECONDS, None, None)
			ui.message(text)
			config.conf["speech"]["symbolLevel"] = curLevel
		count = scriptHandler.getLastScriptRepeatCount()
		if count == 0:
			# say time
			callback()
		elif count == 1:
			# say date
			callback("date")
		else:
			# copyt date and time to clipboard
			callback("copyToClip")
	if getInstallFeatureOption(addonConfig.FCT_DateAndTime):
		script_dateTimeEx.removeCommandsScript = globalCommands.commands.script_dateTime

	def script_reportAppModuleInfoEx(self, gesture):
		def reportAppModuleInfo():
			globalCommands.commands.script_reportAppModuleInfo(None)

		def getProfileStates(name):
			try:
				profile = config.conf.getProfile(name)
			except KeyError:
				return ""
			states = []
			editProfile = config.conf.profiles[-1]
			if profile is editProfile:
				# Translators: Reported for a profile which is being edited.
				states.append(NVDAString("editing"))
			if name:
				# This is a profile (not the normal configuration).
				if profile.manual:
					# Translators: Reported for a profile which has been manually activated.
					states.append(NVDAString("manual"))
				if profile.triggered:
					# Translators: Reported for a profile which is currently triggered.
					states.append(NVDAString("triggered"))
			if states:
				return " (%s)" % ", ".join(states)
			return ""

		def reportCurrentVoiceProfil():
			speech.cancelSpeech()
			profileName = config.conf.profiles[-1].name
			stateText = getProfileStates(profileName)
			if profileName is None:
				profileName = NVDAString("(normal configuration)")
			# Translators: Indicates the name of the configuration profile trigger
				# for the current program.
			message = _("Configuration's profile {profileName} {state}").format(
				profileName=profileName, state=stateText)
			ui.message(message)
		if scriptHandler.getLastScriptRepeatCount() == 0:
			reportAppModuleInfo()
		else:
			reportCurrentVoiceProfil()
	script_reportAppModuleInfoEx.removeCommandsScript = globalCommands.commands.script_reportAppModuleInfo

	def script_restartEx(self, gesture):
		def callback():
			clearDelayScriptTask()
			queueHandler.queueFunction(queueHandler.eventQueue, core.restart)
		stopDelayScriptTask()
		count = scriptHandler.getLastScriptRepeatCount()
		if count == 0:
			delayScriptTask(callback)
		else:
			queueHandler.queueFunction(
				queueHandler.eventQueue, core.restart, debugLogging=True)
	script_restartEx.removeCommandsScript = globalCommands.commands.script_restart

	# new scripts
	def script_report_SystrayIcons(self, gesture):
		wx.CallAfter(DisplayNotificationIconsList.run)

	def script_report_WindowsList(self, gesture):
		wx.CallAfter(ActiveWindowsListDisplay.run)

	def script_report_SystrayIconsOrWindowsList(self, gesture):
		def callback():
			clearDelayScriptTask()
			wx.CallAfter(DisplayNotificationIconsList.run)

		stopDelayScriptTask()
		if scriptHandler.getLastScriptRepeatCount() == 0:
			delayScriptTask(callback)
		else:
			wx.CallAfter(ActiveWindowsListDisplay.run)

	def script_ComplexSymbolHelp(self, gesture):
		from . import ComplexSymbols
		wx.CallAfter(ComplexSymbols.complexSymbolsDialog.run)

	def script_lastUsedComplexSymbolsList(self, gesture):
		from . import ComplexSymbols
		wx.CallAfter(ComplexSymbols.LastUsedComplexSymbolsDialog.run)

	def _getProductNameAndVersion(self, obj):
		productName = ""
		# for some software,  procuttName contains control characters. Must be deleted.
		for ch in obj.appModule.productName:
			if ord(ch) < 32:
				break
			productName = productName + ch
		appVersion = ""
		# for some software, version contains control characters. Must be deleted.
		for ch in obj.appModule.productVersion:
			if ord(ch) < 32:
				break
			appVersion += ch
		return(productName, appVersion)

	def script_reportAppProductNameAndVersion(self, gesture):
		def callback(repeatCount):
			clearDelayScriptTask()
			(productName, appVersion) = self._getProductNameAndVersion(api.getFocusObject())

			# Translators: message to report app version.
			text = _("{0} version {1}") .format(productName, appVersion)
			if repeatCount == 0:
				ui.message(text)
			else:
				if api.copyToClip(text):
					# Translators: message to report that product name and version are copied to clipboard.
					ui.message(_("Product name and version has been copied to clipboard"))
				else:
					# Translators: Presented when unable to copy to the clipboard because of an error.
					ui.message(NVDAString("Unable to copy"))
		stopDelayScriptTask()
		repeatCount = scriptHandler.getLastScriptRepeatCount()
		if repeatCount == 0:
			delayScriptTask(callback, repeatCount)
		else:
			callback(repeatCount)

	def script_reportCurrentAddonNameAndVersion(self, gesture):
		focus = api.getFocusObject()
		mod = focus.appModule
		if isinstance(mod, appModuleHandler.AppModule) and\
			type(mod) != appModuleHandler.AppModule:
			addon = fetchAddon(focus.processID, focus.appModule.appName)
			if addon is not None:
				# Translators: indicate name and version of active addon
				# for current focused application.
				msg = _("add-on: {name}, version: {version}").format(
					name=addon.manifest["name"], version=addon.manifest["version"])
				ui.message(msg)
				return
		# Translators: indicates that there is no active addon
				# for current focused application.
		msg = _("No add-on")
		ui.message(msg)

	def script_DisplayAppModuleInfo(self, gesture):
		def getProfileStates(name):
			try:
				profile = config.conf.getProfile(name)
			except KeyError:
				return ""
			states = []
			editProfile = config.conf.profiles[-1]
			if profile is editProfile:
				# Translators: Reported for a profile which is being edited.
				states.append(NVDAString("editing"))
			if name:
				# This is a profile (not the normal configuration).
				if profile.manual:
					# Translators: Reported for a profile which has been manually activated.
					states.append(NVDAString("manual"))
				if profile.triggered:
					# Translators: Reported for a profile which is currently triggered.
					states.append(NVDAString("triggered"))
			if states:
				return " (%s)" % ", ".join(states)
			return ""

		def getCurrentProfile():
			profileName = config.conf.profiles[-1].name
			if profileName is None:
				profileName = NVDAString("(normal configuration)")
				stateText = ""
			else:
				stateText = getProfileStates(profileName)
			# Translators: Indicates the name of the configuration profile trigger
				# for the current program.
			message = _("Configuration profile: {profileName} {state}").format(
				profileName=profileName, state=stateText)
			return message
		textList = []
		focus = api.getFocusObject()
		appProcessName = appModuleHandler.getAppNameFromProcessID(
			focus.processID, True)
		(productName, appVersion) = self._getProductNameAndVersion(focus)
		appName = "%s, %s" % (appProcessName, productName)
		# Translators: Indicates the name of the current program and it version.
		msg = _("Application: {appName} {appVersion}") .format(
			appName=appName, appVersion=appVersion)
		textList.append(msg)
		msg = getCurrentProfile()
		textList.append(msg)
		mod = focus.appModule
		modName = NVDAString("none")
		if isinstance(mod, appModuleHandler.AppModule) and\
			type(mod) != appModuleHandler.AppModule:
			modName = mod.appModuleName.split(".")[0]
		modPath = mod.__module__.replace(".", "\\")
		addons = []
		for addon in addonHandler.getRunningAddons():
			path = os.path.join(addon.path, modPath)
			if os.path.exists(path):
				addons.append(addon)
				continue
			path = os.path.join(addon.path, modPath + ".py")
			if os.path.exists(path):
				addons.append(addon)
		info = ""
		path = ""
		currentAddon = fetchAddon(focus.processID, focus.appModule.appName)
		if currentAddon is not None:
			# Translators: indicates name and version of current add-on.
			info = _("{summary}, version: {version}").format(
				summary=currentAddon.manifest["summary"],
				version=currentAddon.manifest["version"])
			path = currentAddon.path
		# Translators: indicates summary of current add-on.
		text = _("Active add-on: %s") % info
		textList.append(text)
		# Translators: path of current add-on
		text = _("add-on's path: %s") % path
		textList.append(text)
		if len(addons) > 1:
			# Translators: indicate that others add-ons are installed
			# and activated for this application.
			text = _("Warning: it seems that others add-ons are installed and activated for this application")
			textList.append(text)
		# Translators: Indicates the name of the appModule for the current program.
		msg = _("Loaded python module: %s") % modName
		textList.append(msg)
		# Translators: title of informationdialog box to show appModule informations.
		dialogTitle = _("Application context's informations")
		InformationDialog.run(None, dialogTitle, "", "\r\n".join(textList))

	def script_reportCurrentFolderName(self, gesture):
		stopDelayScriptTask()
		from .currentFolder import reportCurrentFolder
		reportCurrentFolder(False)

	def script_reportCurrentFolderFullPath(self, gesture):
		stopDelayScriptTask()
		from .currentFolder import reportCurrentFolder
		reportCurrentFolder(True)

	def script_reportCurrentFolder(self, gesture):
		stopDelayScriptTask()
		from .currentFolder import reportCurrentFolder
		if scriptHandler.getLastScriptRepeatCount() == 0:
			reportCurrentFolder()
		else:
			reportCurrentFolder(True)

	def script_NVDALogsManagement(self, gesture):
		from .NVDALogs import NVDALogsManagementDialog
		wx.CallAfter(NVDALogsManagementDialog.run)

	def script_openCurrentOrOldNVDALogFile(self, gesture):
		def callback(action):
			clearDelayScriptTask()
			if action == "copyPath":
				logFile = os.path.join(
					os.path.dirname(_getDefaultLogFilePath()), "nvda.log")
				path = logFile
				if api.copyToClip(path):
					ui.message(_("Current log file path copied to clipboard"))
				else:
					ui.message(_("Current log file path cannot be copied to clipboard"))
				return
			elif action == "openOld":
				logFile = os.path.join(
					os.path.dirname(_getDefaultLogFilePath()), "nvda-old.log")
				errorMsg = _("Previous log file cannot be opened")
			elif action == "openCurrent":
				logFile = os.path.join(
					os.path.dirname(_getDefaultLogFilePath()), "nvda.log")
				errorMsg = _("Current log file cannot be opened")
			try:
				os.startfile(logFile)
			except Exception:
				wx.CallAfter(
					gui.messageBox,
					errorMsg,
					# Translators: dialog title.
					_("File open Error"),
					wx.OK | wx.ICON_ERROR)
		stopDelayScriptTask()
		count = scriptHandler.getLastScriptRepeatCount()
		if count == 0:
			delayScriptTask(callback, "openCurrent")
		elif count == 1:
			delayScriptTask(callback, "openOld")
		else:
			callback("copyPath")

	def script_reportPreviousSpeechHistoryRecord(self, gesture):
		stopDelayScriptTask()
		if speechHistory.isActive():
			speechHistory.getSpeechRecorder().reportSpeechHistory("previous", toClip=False)

	def script_reportNextSpeechHistoryRecord(self, gesture):
		stopDelayScriptTask()
		if speechHistory.isActive():
			speechHistory.getSpeechRecorder().reportSpeechHistory("next", toClip=False)

	def script_reportCurrentSpeechHistoryRecord(self, gesture):
		def callback(count):
			clearDelayScriptTask()
			if speechHistory.isActive():
				speechHistory.getSpeechRecorder().reportSpeechHistory("current", toClip=True if count == 1 else False)
		stopDelayScriptTask()
		count = scriptHandler.getLastScriptRepeatCount()
		if count < 2:
			delayScriptTask(callback, count)
		else:
			speechHistory.getSpeechRecorder().displaySpeechHistory()

	def script_displaySpeechHistoryRecords(self, gesture):
		speechHistory.getSpeechRecorder().displaySpeechHistory()

	def script_displayFormatting(self, gesture):
		from .reportFormatting import getReportFormattingOptions
		reportFormattingOptions = getReportFormattingOptions()
		# Create a dictionary to replace the config section that would normally be
		# passed to getFormatFieldsSpeech / getFormatFieldsBraille
		formatConfig = dict()
		from config import conf
		for i in conf["documentFormatting"]:
			formatConfig[i] = i in reportFormattingOptions
		textList = []
		info = api.getReviewPosition()
		# First, fetch indentation.
		line = info.copy()
		if line is None:
			return
		line.expand(textInfos.UNIT_LINE)
		indentation, content = speech.splitTextIndentation(line.text)
		if indentation:
			textList.extend(speech.getIndentationSpeech(indentation, formatConfig))
		info.expand(textInfos.UNIT_CHARACTER)
		formatField = textInfos.FormatField()
		for field in info.getTextWithFields(formatConfig):
			if isinstance(field, textInfos.FieldCommand) and\
				isinstance(field.field, textInfos.FormatField):
				formatField.update(field.field)
		text = speech.getFormatFieldSpeech(
			formatField, formatConfig=formatConfig) if formatField else None
		if text:
			textList.append(text)
		if not textList:
			# Translators: Reported when trying to obtain formatting information
			# (such as font name, indentation and so on)
			# but there is no formatting information for the text under cursor.
			ui.message(NVDAString("No formatting information"))
			return
		from .reportFormatting import displayFormattingInformations
		displayFormattingInformations(speech.getIndentationSpeech(
			indentation, formatConfig), formatField)

	def script_keyboardKeyRenaming(self, gesture):
		from .keyboardKeyRenaming import KeyboardKeyRenamingDialog
		wx.CallAfter(self._popupSettingsDialog, KeyboardKeyRenamingDialog)

	def script_commandKeySelectiveAnnouncement(self, gesture):
		from .commandKeysSelectiveAnnouncementAndRemanence import CommandKeysSelectiveAnnouncementDialog
		wx.CallAfter(
			self._popupSettingsDialog, CommandKeysSelectiveAnnouncementDialog)

	def script_minuteTimer(self, gesture):
		from .minuteTimer import minuteTimer
		wx.CallAfter(minuteTimer)

	def script_foregroundWindowObjectsList(self, gesture):
		from . import winExplorer
		obj = api.getForegroundObject()
		if obj:
			wx.CallAfter(winExplorer.findAllNVDAObjects, obj)

	def script_speakForegroundEx(self, gesture):
		def callback(twice=False):
			speech.cancelSpeech()
			if twice:
				obj = api.getForegroundObject()
				if obj:
					from . import winExplorer
					wx.CallAfter(winExplorer.findAllNVDAObjects, obj)
			else:
				globalCommands.commands.script_speakForeground(gesture)
		count = scriptHandler.getLastScriptRepeatCount()
		if count == 0:
			callback(False)
		else:
			callback(True)
	script_speakForegroundEx.removeCommandsScript = globalCommands.commands.script_speakForeground

	def script_displayModuleUserGuide(self, gesture):
		path = _curAddon.getDocFilePath()
		ui.message(_("Please wait"))
		os.startfile(path)

	def script_shutdownComputerDialog(self, gesture):
		from .computerTools import shutdown_gui as shutdown_gui
		shutdown_gui.ComputerShutdownDialog.run()

	def script_shutdownComputer(self, gesture):
		def callback():
			if gui.messageBox(
				# Translators: message to confirm computer shutdown.
				_("Are you sure you want to shutdown immediately the computer ?"),
				# Translators: dialog title.
				_("Confirmation"),
				wx.YES | wx.NO | wx.CANCEL | wx.ICON_WARNING) != wx.YES:
				return
			from .computerTools.shutdown_util import shutdown as shutdown
			forceClose = True
			timeout = 0
			shutdown(timeout, forceClose)
		# we must delay script execution cause messageBox
		wx.CallAfter(callback)

	def script_rebootComputer(self, gesture):
		def callback():
			if gui.messageBox(
				# Translators: message to confirm computer reboot.
				_("Are you sure you want to reboot immediately the computer ?"),
				# Translators: dialog title.
				_("Confirmation"),
				wx.YES | wx.NO | wx.CANCEL | wx.ICON_WARNING) != wx.YES:
				return
			from .computerTools.shutdown_util import reboot as reboot
			forceClose = True
			timeout = 0
			reboot(timeout, forceClose)
		# we must delay script execution cause messageBox
		wx.CallAfter(callback)

	def script_hibernateComputer(self, gesture):
		def callback():
			if gui.messageBox(
				# Translators: message to confirm computer hibernation.
				_("Are you sure you want to hibernate immediately the computer ?"),
				# Translators: dialog title.
				_("Confirmation"),
				wx.YES | wx.NO | wx.CANCEL | wx.ICON_WARNING) != wx.YES:
				return
			from .computerTools.shutdown_util import suspend as suspend
			suspend(hibernate=True)
		# we must delay script execution cause messageBox
		wx.CallAfter(callback)

	def _reportOrDisplayCurrentSpeechSettings(self, display=False):
		from . import switchVoiceProfile
		textList = switchVoiceProfile.SwitchVoiceProfilesManager().getSynthInformations()
		text = "\r\n".join(textList)
		if not display:
			for item in textList:
				speech.speakMessage(item)
			braille.handler.message(text)
		else:
			# Translators: this is the title <of informationdialog box
			# to show current speech settings.
			dialogTitle = _("Current speech settings")
			InformationDialog.run(None, dialogTitle, "", text)

	def script_reportOrDisplayCurrentSpeechSettings(self, gesture):
		stopDelayScriptTask()
		if scriptHandler.getLastScriptRepeatCount() == 0:
			delayScriptTask(self._reportOrDisplayCurrentSpeechSettings)
		else:
			wx.CallAfter(self._reportOrDisplayCurrentSpeechSettings, True)

	def script_reportCurrentSpeechSettings(self, gesture):
		stopDelayScriptTask()
		wx.CallAfter(self._reportOrDisplayCurrentSpeechSettings)

	def script_displayCurrentSpeechSettings(self, gesture):
		stopDelayScriptTask()
		wx.CallAfter(self._reportOrDisplayCurrentSpeechSettings, True)

	def script_manageVoiceProfileSelectors(self, gesture):
		from . import switchVoiceProfile
		wx.CallAfter(switchVoiceProfile.SelectorsManagementDialog .run, self)

	def script_nextVoiceProfile(self, gesture):
		from . import switchVoiceProfile
		switchManager = switchVoiceProfile.SwitchVoiceProfilesManager()
		switchManager .updateCurrentVoiceProfilSettings()
		switchManager.nextVoiceProfile(forward=True)

	def script_previousVoiceProfile(self, gesture):
		from . import switchVoiceProfile
		switchManager = switchVoiceProfile.SwitchVoiceProfilesManager()
		switchManager .updateCurrentVoiceProfilSettings()
		switchManager.nextVoiceProfile(forward=False)

	def _setSwitchVoiceProfileMode(self, mode=None):
		__switchVoiceProfileModeGestures = {
			"kb:leftArrow": "previousVoiceProfile",
			"kb:rightArrow": "nextVoiceProfile",
			"kb:escape": "toggleSwitchVoiceProfileMode",
			"kb:1": "setVoiceProfileSelector1",
			"kb:2": "setVoiceProfileSelector2",
			"kb:3": "setVoiceProfileSelector3",
			"kb:4": "setVoiceProfileSelector4",
			"kb:5": "setVoiceProfileSelector5",
			"kb:6": "setVoiceProfileSelector6",
			"kb:7": "setVoiceProfileSelector7",
			"kb:8": "setVoiceProfileSelector8",
		}
		if mode:
			self.switchVoiceProfileMode = "on" if mode == "off" else "off"
		if self.switchVoiceProfileMode == "off":
			self.switchVoiceProfileMode = "on"
			ui.message(_("Voice profile switch mode on"))
			self.bindGestures(__switchVoiceProfileModeGestures)
		else:
			self.switchVoiceProfileMode = "off"
			ui.message(_("Voice profile switch mode off"))
			self.clearGestureBindings()
		self._bindGestures()

	def script_toggleSwitchVoiceProfileMode(self, gesture):
		mode = None
		if gesture.displayName == "escape":
			mode = "off"
		wx.CallAfter(self._setSwitchVoiceProfileMode, mode)

	def setVoiceProfileSelector(self, selector):
		from . import switchVoiceProfile
		switchManager = switchVoiceProfile.SwitchVoiceProfilesManager()
		switchManager .updateCurrentVoiceProfilSettings()
		switchManager.setLastSelector(selector)
		if switchManager.isSet(selector):
			wx.CallAfter(switchManager.switchToVoiceProfile, selector)
			return
		# Translators: message to user that the selector is not set.
		ui.message(_("Selector %s is free") % selector)

	def script_setVoiceProfileSelector1(self, gesture):
		wx.CallAfter(self.setVoiceProfileSelector, "1")

	def script_setVoiceProfileSelector2(self, gesture):
		wx.CallAfter(self.setVoiceProfileSelector, "2")

	def script_setVoiceProfileSelector3(self, gesture):
		wx.CallAfter(self.setVoiceProfileSelector, "3")

	def script_setVoiceProfileSelector4(self, gesture):
		wx.CallAfter(self.setVoiceProfileSelector, "4")

	def script_setVoiceProfileSelector5(self, gesture):
		wx.CallAfter(self.setVoiceProfileSelector, "5")

	def script_setVoiceProfileSelector6(self, gesture):
		wx.CallAfter(self.setVoiceProfileSelector, "6")

	def script_setVoiceProfileSelector7(self, gesture):
		wx.CallAfter(self.setVoiceProfileSelector, "7")

	def script_setVoiceProfileSelector8(self, gesture):
		wx.CallAfter(self.setVoiceProfileSelector, "8")

	def script_activateUserInputGesturesDialog(self, gesture):
		from .userInputGestures import UserInputGesturesDialog
		if inputCore.manager.userGestureMap._map == {}:
			ui.message(
				# Translators: message to user no configuration change made.
				_("There was no change of input gesture made by the user"))
			return
		wx.CallAfter(self._popupSettingsDialog, UserInputGesturesDialog)

	def script_toolsForAddon(self, gesture):
		from . import tools
		wx.CallAfter(tools.ToolsForAddonDialog.run)

	def runScript(self, gesture):
		self.bindGestures(self._shellGestures)
		script = self.getScript(gesture)
		self.clearGestureBindings()
		self._bindGestures()
		queueHandler.queueFunction(queueHandler.eventQueue, script, gesture)

	def script_displayHelp(self, gesture):
		HelperDialog.run(self)

	def script_leftClickAtNavigatorObjectPosition(self, gesture):
		def callback(twice=False):
			clearDelayScriptTask()
			# Translators: Reported when left mouse button is clicked.
			msg = NVDAString("Left click") if not twice else _("Double left click")
			ui.message(msg)
			time.sleep(0.3)
			try:
				p = api.getReviewPosition().pointAtStart
			except (NotImplementedError, LookupError):
				p = None
			if p:
				x = p.x
				y = p.y
			else:
				try:
					(left, top, width, height) = api.getNavigatorObject().location
				except Exception:
					# Translators: Reported when the object has no location
					# for the mouse to move to it.
					ui.message(_("Object has no location"))
					return
				x = int(left + (width / 2))
				y = int(top + (height / 2))
			oldSpeechMode = getSpeechMode()
			setSpeechMode_off()
			winUser.setCursorPos(x, y)
			mouseHandler.executeMouseMoveEvent(x, y)
			time.sleep(0.2)
			setSpeechMode(oldSpeechMode)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN, 0, 0, None, None)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP, 0, 0, None, None)
			if twice:
				time.sleep(0.1)
				winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN, 0, 0, None, None)
				winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP, 0, 0, None, None)
		stopDelayScriptTask()
		count = scriptHandler.getLastScriptRepeatCount()
		if count == 0:
			delayScriptTask(callback, False)
		else:
			callback(True)

	def script_rightClickAtNavigatorObjectPosition(self, gesture):
		def callback(twice=False):
			clearDelayScriptTask()
			# Translators: Reported when right mouse button is clicked.
			msg = NVDAString("Right click") if not twice else _("Double right click")
			ui.message(msg)
			time.sleep(0.3)
			try:
				p = api.getReviewPosition().pointAtStart
			except (NotImplementedError, LookupError):
				p = None
			if p:
				x = p.x
				y = p.y
			else:
				try:
					(left, top, width, height) = api.getNavigatorObject().location
				except Exception:
					# Translators: Reported when the object has no location
					# for the mouse to move to it.
					ui.message(_("Object has no location"))
					return
				x = int(left + (width / 2))
				y = int(top + (height / 2))
			oldSpeechMode = getSpeechMode()
			setSpeechMode_off()
			winUser.setCursorPos(x, y)
			mouseHandler.executeMouseMoveEvent(x, y)
			time.sleep(0.2)
			setSpeechMode(oldSpeechMode)
			winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTDOWN, 0, 0, None, None)
			winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTUP, 0, 0, None, None)
			if twice:
				time.sleep(0.1)
				winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTDOWN, 0, 0, None, None)
				winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTUP, 0, 0, None, None)
		stopDelayScriptTask()
		count = scriptHandler.getLastScriptRepeatCount()
		if count == 0:
			delayScriptTask(callback, False)
		else:
			callback(True)
	enableNumpadNnavigationKeys = False

	def checkInstallationForNumpadFunctionnality(self):
		if isInstall(addonConfig.FCT_CommandKeysSelectiveAnnouncement) or\
			isInstall(addonConfig.FCT_KeyRemanence):
			return True
		ui.message(
			# Translators: message to user the fonctionnality is not available.
			_(
				"""This functionnality is only available if "command keys selective announcement" functionnality """
				"""or "keys's remanence" functionnality is installed"""))
		return False

	def script_toggleNumpadStandardUse(self, gesture):
		if not self.checkInstallationForNumpadFunctionnality():
			return
		from .settings import toggleEnableNumpadNavigationModeToggleAdvancedOption
		if not toggleEnableNumpadNavigationModeToggleAdvancedOption(False):
			ui.message(
				# Translators: message to user the fonctionnality is not available.
				_("The standard use of the numeric keypad is not allowed"))
			return
		from .commandKeysSelectiveAnnouncementAndRemanence import _myInputManager
		_myInputManager .toggleNavigationNumpadMode()

	def script_toggleNumpadStandardUseWithNumlockKey(self, gesture):

		def callback(gesture):
			clearDelayScriptTask()
			if isInstall(addonConfig.FCT_CommandKeysSelectiveAnnouncement) or\
				isInstall(addonConfig.FCT_KeyRemanence):
				gesture.reportExtra()
		stopDelayScriptTask()
		if not settings.toggleEnableNumpadNavigationModeToggleAdvancedOption(False) or\
			not settings.toggleActivateNumpadStandardUseWithNumLockAdvancedOption(False):
			gesture.send()
			callback(gesture)
			return
		gesture.send()
		if scriptHandler.getLastScriptRepeatCount() == 0:
			delayScriptTask(callback, gesture)
		else:
			if not self.checkInstallationForNumpadFunctionnality():
				return
			self.script_toggleNumpadStandardUse(gesture)

	def script_closeAllWindows(self, gesture):
		def closeAll():
			if gui.messageBox(
				# Translators: message to confirm closing all windows
				_("Are you sure you want to close all windows?"),
				# Translators: dialog title.
				_("Confirmation"),
				wx.YES | wx.NO | wx.CANCEL | wx.ICON_WARNING) != wx.YES:
				return
			from .activeWindowsListReport import getactiveWindows, closeAllWindows
			windowsList = getactiveWindows()
			closeAllWindows(windowsList)
		wx.CallAfter(closeAll)

	def script_EmulateApplicationsKey(self, gesture):
		from keyboardHandler import KeyboardInputGesture
		KeyboardInputGesture.fromName("Applications").send()
		# Translators: Input help mode message for a keyboard command.
	script_EmulateApplicationsKey.__doc__ = NVDAString("Emulate key press: {emulateGesture}").format(
		emulateGesture="Applications")
	script_EmulateApplicationsKey.category = inputCore.SCRCAT_KBEMU

	def script_displayRunningAddonsList(self, gesture):
		from locale import strxfrm
		# Translators: extension type tag.
		globalTag = _("global")
		# Translators: extension type tag.
		appModuleTag = _("application")
		# Translators: extension type tag.
		synthetizerTag = _("speech synthesizer driver")
		# Translators: extension type tag.
		brailleDisplayDriverTag = _("braille display driver")
		# Translators: extension type tag.
		mixedTag = _("mixed")
		# Translators: add-on type.
		addonTypeLabel = _("%s add-on type:")
		# Translators: no add-on
		noAddonText = _("any")
		globalPlugins = []
		mixes = []
		appModules = []
		synthetizers = []
		brailles = []
		runningAddons = sorted(addonHandler.getRunningAddons(), key=lambda a: strxfrm(a.manifest['summary']))
		for addon in runningAddons:
			addonName = "%s %s" % (addon.manifest["summary"], addon.manifest["version"])
			globalPlugin = os.path.exists(os.path.join(addon.path, "globalPlugins"))
			tag = globalTag if globalPlugin else ""
			appModule = os.path.exists(os.path.join(addon.path, "appModules"))
			tag = "%s, %s" % (tag, appModuleTag) if appModule else tag
			synthDriver = os.path.exists(os.path.join(addon.path, "synthDrivers"))
			tag = "%s, %s" % (tag, synthetizerTag) if synthDriver else tag
			brailleDisplayDriver = os.path.exists(os.path.join(addon.path, "brailleDisplayDrivers"))
			tag = "%s, %s" % (tag, brailleDisplayDriverTag) if brailleDisplayDriver else tag
			if globalPlugin:
				if appModule or synthDriver or brailleDisplayDriver:
					mixes.append("%s (%s)" % (addonName, tag))
				else:
					globalPlugins.append(addonName)
			elif appModule:
				if synthDriver or brailleDisplayDriver:
					mixes.append("%s (%s)" % (addonName, tag))
				else:
					appModules.append(addonName)
			elif synthDriver:
				if brailleDisplayDriver:
					mixes.append("%s (%s)" % (addonName, tag))
				else:
					synthetizers.append(addonName)
			elif brailleDisplayDriver:
				brailles.append(addonName)

		textList = [(addonTypeLabel % globalTag).capitalize(), ]
		if len(globalPlugins):
			textList.extend(globalPlugins)
		else:
			textList.append(noAddonText)
		textList.append("")
		textList.append((addonTypeLabel % appModuleTag).capitalize())
		if len(appModules):
			textList.extend(appModules)
		else:
			textList.append(noAddonText)
		textList.append("")
		textList.append(addonTypeLabel % synthetizerTag)
		if len(synthetizers):
			textList.extend(synthetizers)
		else:
			textList.append(noAddonText)
		textList.append("")
		textList.append((addonTypeLabel % brailleDisplayDriverTag).capitalize())
		if len(brailles):
			textList.extend(brailles)
		else:
			textList.append(noAddonText)
		textList.append((addonTypeLabel % mixedTag).capitalize())
		if len(mixes):
			textList.extend(mixes)
		else:
			textList.append(noAddonText)
		textList.append("")
		# Translators: title of informationdialog box to show active add-ons.
		dialogTitle = _("Running add-ons")
		InformationDialog.run(None, dialogTitle, "", "\r\n".join(textList))

	def checkUpdateWithLocalMyAddonsFile(self, auto=False):
		path = "F:\\nvdaprojet\\paulber007Repositories\\myAddons.latest"
		from .settings import toggleUpdateReleaseVersionsToDevVersionsGeneralOptions
		from .updateHandler.update_check import CheckForAddonUpdate
		wx.CallAfter(
			CheckForAddonUpdate,
			addonName=None,
			updateInfosFile=path,
			auto=auto,
			releaseToDev=toggleUpdateReleaseVersionsToDevVersionsGeneralOptions(False))

	def script_toggleTextAnalyzer(self, gesture):
		from .settings.nvdaConfig import _NVDAConfigManager
		_NVDAConfigManager.toggleTextAnalyzerActivationOption()

	def analyzeText(self, unit):
		focus = api.getFocusObject()
		try:
			info = focus.makeTextInfo(textInfos.POSITION_CARET)
		except Exception:
			return
		from .textAnalysis.textAnalyzer import getAnalyze, reportAnalysis
		textInfo = info.copy()
		try:
			textInfo.expand(unit)
		except Exception:
			# Translators: message to user when text analysis is not available (for example by sentence).
			ui.message(_("Text analysis not available"))
			return
		if unit in [textInfos.UNIT_SENTENCE, textInfos.UNIT_PARAGRAPH] and len(textInfo.text) > 80:
			ui.message(_("Please wait"))

		(alertCount, textList) = getAnalyze(textInfo, unit)
		if alertCount:
			reportAnalysis(alertCount, textList, description=True)
		else:
			# Translators: message to user to report no analysis alert.
			ui.message(_("Nothing to report"))

	def script_analyzeCurrentWord(self, gesture):
		wx.CallAfter(self.analyzeText, textInfos.UNIT_WORD)

	def script_analyzeCurrentLine(self, gesture):
		wx.CallAfter(self.analyzeText, textInfos.UNIT_LINE)

	def script_analyzeCurrentSentence(self, gesture):
		wx.CallAfter(self.analyzeText, textInfos.UNIT_SENTENCE)

	def script_analyzeCurrentParagraph(self, gesture):
		wx.CallAfter(self.analyzeText, textInfos.UNIT_PARAGRAPH)

	def script_findNextTextAnalyzerAlert(self, gesture):
		from .textAnalysis.textAnalyzer import moveToAlert
		wx.CallAfter(moveToAlert, next=True),

	def script_findPreviousTextAnalyzerAlert(self, gesture):
		from .textAnalysis.textAnalyzer import moveToAlert
		wx.CallAfter(moveToAlert, next=False)

	def script_toggleReportCurrentCaretPosition(self, gesture):
		from .settings.nvdaConfig import _NVDAConfigManager
		state = _NVDAConfigManager.toggleReportCurrentCaretPositionOption()
		if state:
			# Translators: message to indicate then report current caret position is on.
			msg = _("report current caret position on")
		else:
			# Translators: message to indicate then report current caret position is off.
			msg = _("report current caret position off")
		ui.message(msg)

	def script_reportClipboardTextEx(self, gesture):
		from .clipboardCommandAnnouncement import clipboard
		cm = clipboard.ClipboardManager()
		if cm.isEmpty:
			ui.message(_("Clipboard is empty"))
			return
		try:
			text = api.getClipData()
		except Exception:
			text = None
		if not text or not isinstance(text, str) or text.isspace():
			noTextMsg = NVDAString("There is no text on the clipboard")
			# Translators: Presented when there is no text on the clipboard, but clipboard is not empty.
			noEmptyMsg = _("but the clipboard is not empty")
			ui.message("%s, %s" % (noTextMsg, noEmptyMsg))
			return
		from .settings import _addonConfigManager
		max = _addonConfigManager.getMaximumClipboardReportedCharacters()
		if not max or (max and len(text) < max):
			brailleText = text
			while len(text) / 1024:
				speech.speakMessage(text[:1025])
				text = text[1025:]
			if len(text):
				speech.speakMessage(text)
			braille.handler.message(brailleText)
		else:
			# Translators: If the number of characters on the clipboard is greater than about 1000,
			# it reports this message and gives number of characters on the clipboard.
			# Example output: The clipboard contains a large portion of text. It is 2300 characters long.
			ui.message(
				NVDAString("The clipboard contains a large portion of text. It is %s characters long") % len(text))

	script_reportClipboardTextEx.removeCommandsScript = globalCommands.commands.script_reportClipboardText

	def script_addToClip(self, gesture):
		from .clipboardCommandAnnouncement .addToClip import addToClip
		wx.CallAfter(addToClip)

	def script_emptyClipboard(self, gesture):
		from .clipboardCommandAnnouncement import clipboard
		cm = clipboard.ClipboardManager()
		if cm.clear():
			# Translators: message to user to report clipboard
			ui.message(_("Clipboard cleared"))
		else:
			# Translators: message to user because of error on clipboard clearing
			ui.message(_("Error: clipboard cannot cleared"))

	def script_temporaryAudioOutputDeviceManager(self, gesture):
		from .computerTools.audioDevice import TemporaryAudioDeviceManagerDialog
		TemporaryAudioDeviceManagerDialog.run()

	def script_cancelTemporaryAudioOutputDevice(self, gesture):
		from .computerTools.audioDevice import cancelTemporaryAudioOutputDevice
		wx.CallAfter(cancelTemporaryAudioOutputDevice)

	def script_setTemporaryAudioOutputDevice(self, gesture):
		from .computerTools.audioDevice import setTemporaryAudioOutputDevice
		from .settings import _addonConfigManager
		deviceNames = _addonConfigManager.getAudioDevicesForCycle()
		if not deviceNames or len(deviceNames) == 1:
			# Translators: message to user when cycle is not possible
			ui.message(_("cycle is not possible on audio output device"))
			return
		from synthDriverHandler import _audioOutputDevice
		curOutputDevice = _audioOutputDevice
		try:
			selection = deviceNames.index(curOutputDevice)
		except ValueError:
			selection = 0
		selection = (selection + 1) % len(deviceNames)
		audioDevice = deviceNames[selection]
		setTemporaryAudioOutputDevice(audioDevice)

	def script_setOrCancelTemporaryAudioOutputDevice(self, gesture):
		stopDelayScriptTask()
		if scriptHandler.getLastScriptRepeatCount():
			self.script_cancelTemporaryAudioDevice(None)
		else:
			delayScriptTask(self.script_setTemporaryAudioOutputDevice, None)

	def script_activateQuickAddonsActivationDialog(self, gesture):
		from .settings.quickAddonsActivation import QuickAddonsActivationDialog
		wx.CallAfter(QuickAddonsActivationDialog.run)

	def saveCurrentSettingRing(self):
		settings = globalVars.settingsRing
		id = (
			settings.settings[settings._current].setting.id
			if settings._current is not None and hasattr(settings, 'settings')
			else None
		)
		if id is None:
			return
		from synthDriverHandler import getSynth
		synthName = getSynth().name
		from .settings.nvdaConfig import _NVDAConfigManager
		_NVDAConfigManager.saveLastSelectedSettingInSynthSettingsRing(synthName, id)

	@scriptHandler.script(
		# Translators: Input help mode message for increase synth setting value command.
		description=NVDAString("Increases the currently active setting in the synth settings ring"),
		category=globalCommands.SCRCAT_SPEECH,
		gestures=("kb(desktop):NVDA+control+upArrow", "kb(laptop):NVDA+shift+control+upArrow")
	)
	def script_increaseSynthSetting(self, gesture):
		globalCommands.commands.script_increaseSynthSetting(gesture)
		self.saveCurrentSettingRing()

	@scriptHandler.script(
		# Translators: Input help mode message for decrease synth setting value command.
		description=NVDAString("Decreases the currently active setting in the synth settings ring"),
		category=globalCommands.SCRCAT_SPEECH,
		gestures=("kb(desktop):NVDA+control+downArrow", "kb(laptop):NVDA+control+shift+downArrow")
	)
	def script_decreaseSynthSetting(self, gesture):
		globalCommands.commands.script_decreaseSynthSetting(gesture)
		self.saveCurrentSettingRing()

	@scriptHandler.script(
		# Translators: Input help mode message for next synth setting command.
		description=NVDAString("Moves to the next available setting in the synth settings ring"),
		category=globalCommands.SCRCAT_SPEECH,
		gestures=("kb(desktop):NVDA+control+rightArrow", "kb(laptop):NVDA+shift+control+rightArrow")
	)
	def script_nextSynthSetting(self, gesture):
		globalCommands.commands.script_nextSynthSetting(gesture)
		self.saveCurrentSettingRing()

	@scriptHandler.script(
		# Translators: Input help mode message for previous synth setting command.
		description=NVDAString("Moves to the previous available setting in the synth settings ring"),
		category=globalCommands.SCRCAT_SPEECH,
		gestures=("kb(desktop):NVDA+control+leftArrow", "kb(laptop):NVDA+shift+control+leftArrow")
	)
	def script_previousSynthSetting(self, gesture):
		globalCommands.commands.script_previousSynthSetting(gesture)
		self.saveCurrentSettingRing()

	def script_test(self, gesture):
		log.info("NVDAExtensionGlobalPlugin  test")
		ui.message("NVDAExtensionGlobalPlugin test")


class HelperDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	_instance = None
	title = None
	# help in the user manual.
	helpObj = getHelpObj("hdr0-2")

	def __new__(cls, *args, **kwargs):
		if HelperDialog._instance is None:
			return wx.Dialog.__new__(cls)
		return HelperDialog._instance

	def __init__(self, parent, globalPlugin):
		if HelperDialog._instance is not None:
			return
		HelperDialog._instance = self
		self.focusObject = api.getFocusObject()
		# Translators: this is the title of Helper dialog.
		dialogTitle = _("Shell's scripts")
		HelperDialog.title = makeAddonWindowTitle(dialogTitle)
		super(HelperDialog, self).__init__(parent, wx.ID_ANY, HelperDialog.title)
		self.globalPlugin = globalPlugin
		self.doGui()

	def initList(self):
		self.docToScript = {}
		self.scriptToIdentifier = {}
		for script in scriptsToDocInformations:
			if script not in self.globalPlugin._shellScriptToGestureAndFeatureOption:
				continue
			identifier = self.globalPlugin._shellScriptToGestureAndFeatureOption[script][0]
			if identifier in self.globalPlugin._shellGestures:
				(doc, category, helpId) = scriptsToDocInformations[script]
				self.scriptToIdentifier[script] = identifier
				self.docToScript[doc] = script

	def doGui(self):
		self.initList()
		self.docList = sorted([doc for doc in self.docToScript])
		choice = []
		for doc in self.docList:
			script = self.docToScript[doc]
			identifier = self.scriptToIdentifier[script]
			source, main = inputCore.getDisplayTextForGestureIdentifier(identifier.lower())
			choice.append("%s: %s" % (doc, main))
		from gui import guiHelper
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# the list box
		# Translators: This is the label of the list appearing
		# on HelperDialog
		labelText = _("Description: command")
		self.scriptsListBox = sHelper.addLabeledControl(
			labelText,
			wx.ListBox,
			choices=choice,
			style=wx.LB_SINGLE,
			size=(700, 280))
		if self.scriptsListBox.GetCount():
			self.scriptsListBox.SetSelection(0)
		# Buttons
		bHelper = guiHelper.ButtonHelper(wx.HORIZONTAL)
		runScriptButton = bHelper.addButton(
			self,
			# Translators: This is a label of a button appearing
			# on HelperDialog
			label=_("&Execute the script"))
		runScriptButton.SetDefault()
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			guiHelper.ButtonHelper(wx.HORIZONTAL))
		closeButton = bHelper.addButton(
			self, id=wx.ID_CLOSE, label=NVDAString("&Close"))
		mainSizer.Add(
			sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# Events
		runScriptButton.Bind(wx.EVT_BUTTON, self.onRunScriptButton)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.scriptsListBox.Bind(wx.EVT_LISTBOX, self.onSelectScript)
		self.Bind(wx.EVT_ACTIVATE, self.onActivate)
		self.SetEscapeId(wx.ID_CLOSE)

	def Destroy(self):
		HelperDialog._instance = None
		super(HelperDialog, self).Destroy()

	def onActivate(self, evt):
		evt.Skip()

	def onSelectScript(self, evt):
		index = self.scriptsListBox.GetSelection()
		doc = self.docList[index]
		script = self.docToScript[doc]
		(doc, category, helpId) = scriptsToDocInformations[script]
		self.bindHelpEvent(getHelpObj(helpId), self)
		evt.Skip()

	def onRunScriptButton(self, evt):
		index = self.scriptsListBox.GetSelection()
		doc = self.docList[index]
		script = self.docToScript[doc]
		identifier = self.scriptToIdentifier[script]
		from keyboardHandler import KeyboardInputGesture
		gesture = KeyboardInputGesture.fromName(identifier[3:])
		self.globalPlugin._trapNextGainFocus = True
		wx.CallLater(1000, self.globalPlugin.runScript, gesture)
		self.Close()

	@classmethod
	def run(cls, globalPlugin):
		if isOpened(cls):
			return
		gui.mainFrame.prePopup()
		d = cls(gui.mainFrame, globalPlugin)
		d.CentreOnScreen()
		d.Show()
		gui.mainFrame.postPopup()
