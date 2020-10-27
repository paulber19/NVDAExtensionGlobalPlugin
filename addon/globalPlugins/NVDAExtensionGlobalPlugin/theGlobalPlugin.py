# globalPlugins\NVDAExtensionGlobalPlugin\theGlobalPlugin.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2020 Paulber19
# This file is covered by the GNU General Public License.


import addonHandler
import globalPluginHandler
from logHandler import log, _getDefaultLogFilePath
import os
import globalVars
import api
import ui
import speech
import time
import gui
import wx
import appModuleHandler
import globalCommands
import scriptHandler
import queueHandler
import winUser
import mouseHandler
import textInfos
import winKernel
import core
import inputCore
import tones
from functools import wraps
import config
from characterProcessing import SYMLVL_SOME
from .activeWindowsListReport import ActiveWindowsListDisplay
from .systemTrayIconsList import ListeNotification
# to load configuration
from . import settings
from .settings import *  # noqa:F403
from .settings.dialog import AddonSettingsDialog
from . import commandKeysSelectiveAnnouncementAndRemanence
from . import speechHistory
from .computerTools import volumeControl as volumeControl
from .utils.NVDAStrings import NVDAString
from .utils import maximizeWindow, makeAddonWindowTitle, isOpened
from .utils import delayScriptTask, stopDelayScriptTask, clearDelayScriptTask
from .utils import special
from .utils.informationDialog import InformationDialog
from .utils.py3Compatibility import py3, _unicode

addonHandler.initTranslation()

_curAddon = addonHandler.getCodeAddon()
_addonSummary = _curAddon.manifest['summary']
# module script categories
SCRCAT_MODULE = _unicode(_addonSummary)
# Translators: The name of a category of NVDA commands.
SCRCAT_SWITCH_VOICE_PROFILE = _("Switch voice profile")
# Translators: The name of a category of NVDA commands.
SCRCAT_VOLUME_CONTROL = _("Volume control")


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
	# We need to do this separately because even though an ImportError is raised when a module can't be found, it might also be raised for other reasons.
	# Python 2.x can't properly handle unicode module names, so convert them.
	modName = appName if py3 else appName.encode("mbcs")
	if appModuleHandler.doesAppModuleExist(modName):
		try:
			mod = __import__("appModules.%s" % modName, globals(), locals(), ("appModules",))
			# check if we can create appModule
			mod.AppModule(processID, appName)
			if py3:
				path = mod.__file__
			else:
				path = mod.__file__.decode("mbcs")
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
		except:  # noqa:E722
			pass
		return None


class NVDAExtensionGlobalPlugin(globalPluginHandler.GlobalPlugin):
	_remanenceCharacter = None
	_trapNextGainFocus = False
	_repeatBeepOnAudio = None
	criptCategory = SCRCAT_MODULE
	# a dictionnary to map main script to gestures and install feature option
	_shellGestures = {}
	_mainScriptToGestureAndfeatureOption = {
		# "test": (("kb:nvda+control+shift+f11",) , None),
		"moduleLayer": (("kb:NVDA+j",), None),
		"reportAppModuleInfoEx": (("kb:nvda+control+f1",), ID_FocusedApplicationInformations),
		"reportAppProductNameAndVersion": (("kb:nvda+shift+f1",), ID_FocusedApplicationInformations),
		"ComplexSymbolHelp": (("kb:nvda+shift+f4",), ID_ComplexSymbols),
		"lastUsedComplexSymbolsList": (None, ID_ComplexSymbols),
		"report_SystrayIconsOrWindowsList": (("kb:nvda+F11",), ID_SystrayIconsAndActiveWindowsList),
		"reportCurrentFolder": (("kb:nvda+o",), ID_CurrentFolderReport),
		"reportPreviousSpeechHistoryRecord": (("kb:nvda+control+f8",), ID_SpeechHistory),
		"reportCurrentSpeechHistoryRecord": (("kb:nvda+control+f9",), ID_SpeechHistory),
		"reportNextSpeechHistoryRecord": (("kb:nvda+control+f10",), ID_SpeechHistory),
		"minuteTimer": (("kb:nvda+shift+f12",), ID_MinuteTimer),
		"speakForegroundEx": (("kb:nvda+b",), ID_ForegroundWindowObjectsList),
		"dateTimeEx": (("kb:nvda+f12",), ID_DateAndTime),
		"copyDateAndTimeToClip": (None, ID_DateAndTime),
		"restartEx": (("kb:nvda+control+f4",), ID_RestartInDebugMode),
		"keyboardKeyRenaming": (None, ID_KeyboardKeyRenaming),
		"commandKeySelectiveAnnouncement": (None, ID_CommandKeysSelectiveAnnouncement),
		"exploreUserConfigFolder": (None, ID_ExploreNVDA),
		"exploreProgramFiles": (None, ID_ExploreNVDA),
		"toggleSwitchVoiceProfileMode": (("kb:nvda+control+shift+p",), ID_VoiceProfileSwitching),
		"manageVoiceProfileSelectors": (("kb:nvda+shift+control+m",), ID_VoiceProfileSwitching),
		"previousVoiceProfile": (("kb(desktop):nvda+shift+control+leftArrow", "kb(laptop):nvda+control+upArrow",), ID_VoiceProfileSwitching),
		"nextVoiceProfile": (("kb(desktop):nvda+shift+control+rightArrow", "kb(laptop):nvda+control+downArrow",), ID_VoiceProfileSwitching),
		"setVoiceProfileSelector1": (("kb:nvda+shift+control+1",), ID_VoiceProfileSwitching),
		"setVoiceProfileSelector2": (("kb:nvda+shift+control+2",), ID_VoiceProfileSwitching),
		"setVoiceProfileSelector3": (("kb:nvda+shift+control+3",), ID_VoiceProfileSwitching),
		"setVoiceProfileSelector4": (("kb:nvda+shift+control+4",), ID_VoiceProfileSwitching),
		"setVoiceProfileSelector5": (("kb:nvda+shift+control+5",), ID_VoiceProfileSwitching),
		"setVoiceProfileSelector6": (("kb:nvda+shift+control+6",), ID_VoiceProfileSwitching),
		"setVoiceProfileSelector7": (("kb:nvda+shift+control+7",), ID_VoiceProfileSwitching),
		"setVoiceProfileSelector8": (("kb:nvda+shift+control+8",), ID_VoiceProfileSwitching),
		"openCurrentOrOldNVDALogFile": (("kb:nvda+shift+j",), ID_OpenCurrentOrOldNVDALogFile),
		"setMainAndNVDAVolume": (("kb:nvda+escape",), ID_VolumeControl),
		"toggleCurrentAppVolumeMute": (("kb:nvda+pause",), ID_VolumeControl),
		"increaseFocusedAppVolume": (None, ID_VolumeControl),
		"decreaseFocusedAppVolume": (None, ID_VolumeControl),
		"maximizeFocusedAppVolume": (None, ID_VolumeControl),
		"minimizeFocusedAppVolume": (None, ID_VolumeControl),
		"increaseSpeakersVolume": (None, ID_VolumeControl),
		"decreaseSpeakersVolume": (None, ID_VolumeControl),
		"maximizeSpeakersVolume": (None, ID_VolumeControl),
		"minimizeSpeakersVolume": (None, ID_VolumeControl),
		"toolsForAddon": (None, ID_Tools),
		"leftClickAtNavigatorObjectPosition": (("kb:nvda+,",), None),
		"rightClickAtNavigatorObjectPosition": (("kb:nvda+shift+,",), None),
		"addonSettingsDialog": (None, None),
		"toggleNumpadStandardUse": (None, None),
		"toggleNumpadStandardUseWithNumlockKey": (("kb:numlock",), None),
		}

	# a dictionnary to map shell script to gesture and installation check function
	_shellScriptToGestureAndFeatureOption = {
		"DisplayAppModuleInfo": ("kb:a", None),
		"foregroundWindowObjectsList": ("kb:b", ID_ForegroundWindowObjectsList),
		"copyDateAndTimeToClip": ("kb:c", ID_DateAndTime),
		"displayFormatting": ("kb:f", None),
		"addonSettingsDialog": ("kb:f1", None),
		"keyboardKeyRenaming": ("kb:f2", ID_KeyboardKeyRenaming),
		"commandKeySelectiveAnnouncement": ("kb:f3", ID_CommandKeysSelectiveAnnouncement),
		"ComplexSymbolHelp": ("kb:f4", ID_ComplexSymbols,),
		"lastUsedComplexSymbolsList": ("kb:control+f4", ID_ComplexSymbols,),
		"toggleNumpadStandardUse": ("kb:f5", None),
		"displaySpeechHistoryRecords": ("kb:f9", ID_SpeechHistory),
		"report_WindowsList": ("kb:f10", ID_SystrayIconsAndActiveWindowsList),
		"report_SystrayIcons": ("kb:f11", ID_SystrayIconsAndActiveWindowsList),
		"minuteTimer": ("kb:f12", ID_MinuteTimer),
		"displayModuleUserGuide": ("kb:g", None),
		"displayHelp": ("kb:h", None),
		"NVDALogsManagement": ("kb:j", ID_OpenCurrentOrOldNVDALogFile),
		"reportCurrentFolderName": ("kb:o", ID_CurrentFolderReport),
		"reportCurrentFolderFullPath": ("kb:control+o", ID_CurrentFolderReport),
		"toggleSwitchVoiceProfileMode": ("kb:p", ID_VoiceProfileSwitching),
		"shutdownComputerDialog": ("kb:r", None),
		"toggleCurrentAppVolumeMute": ("kb:s", ID_VolumeControl),
		"setMainAndNVDAVolume": ("kb:control+s", ID_VolumeControl),
		"increaseFocusedAppVolume": ("kb:upArrow", ID_VolumeControl),
		"decreaseFocusedAppVolume": ("kb:downArrow", ID_VolumeControl),
		"maximizeFocusedAppVolume": ("kb:pageUp", ID_VolumeControl),
		"minimizeFocusedAppVolume": ("kb:pageDown", ID_VolumeControl),
		"increaseSpeakersVolume": ("kb:control+upArrow", ID_VolumeControl),
		"decreaseSpeakersVolume": ("kb:control+downArrow", ID_VolumeControl),
		"maximizeSpeakersVolume": ("kb:control+pageUp", ID_VolumeControl),
		"minimizeSpeakersVolume": ("kb:control+pageDown", ID_VolumeControl),
		"toolsForAddon": ("kb:t", ID_Tools),
		"activateUserInputGesturesDialog": ("kb:u", None),
		"manageVoiceProfileSelectors": ("kb:v", ID_VoiceProfileSwitching),
		}

	# Translators: Input help mode message
	# for display active windows 's list dialog command.
	activeWindowsDoc = _("Display the running application windows's list with opportunity to put one of them on the foreground or destroy it")
	# Translators: Input help mode message
	# for display systray icons list dialog command.
	systrayIconsDoc = _("Shows the list of buttons on the System Tray")
	_scriptsToDocsAndCategory = {
		# Translators: Input help mode message
		# for display shut down , reboot or hibernate computer dialog command.
		"shutdownComputerDialog": (_("Display dialog to shut down, reboot or hibernate the computer"), None),
		# Translators: Input help mode message
		# for shut down computer command.
		"shutdownComputer": (_("Shutt down the computer"), None),
		# Translators: Input help mode message
		# for reboot computer command.
		"rebootComputer": (_("Reboot the computer"), None),
		# Translators: Input help mode message
		# for hibernate computer command.
		"hibernateComputer": (_("Hibernate the computer"), None),
		# Translators: Input help mode message
		# for display complex symbols help dialog command.
		"ComplexSymbolHelp": (_("Allow you to copy or type complex symbol"), None),
		# Translators: Input help mode message
		# for lastUsedComplexSymbolsList.
		"lastUsedComplexSymbolsList": (_("Display the list of last used symbols"), None),
		# Translators: Input help mode message
		# for list foreground object command (usually the foreground window).
		"foregroundWindowObjectsList": (_("Display the list's visible items making up current foreground object"), globalCommands.SCRCAT_FOCUS),
		# Translators: Input help mode message
		# for read or list foreground object command (usually the foreground window).
		"speakForegroundEx": ("%s. %s" % (globalCommands.commands.script_speakForeground.__func__.__doc__, _("If pressed twice: display the list's visible items making up it")), globalCommands.SCRCAT_FOCUS),
		"report_WindowsList": (activeWindowsDoc, None),
		"report_SystrayIcons": (systrayIconsDoc, None),
		# Translators: Input help mode message
		# for display systray icons list or active windows list dialog command.
		"report_SystrayIconsOrWindowsList": (_("{systrayIconsDoc}. Twice, {activeWindowsDoc}").format(systrayIconsDoc=systrayIconsDoc, activeWindowsDoc=activeWindowsDoc), None),
		# Translators: Input help mode message
		# for report current application name and version command.
		"reportAppProductNameAndVersion": (_("Report the application 's name and version"), globalCommands.SCRCAT_TOOLS),
		# Translators: Input help mode message
		# for report current program name and app module name or current configuration profile name command.
		"reportAppModuleInfoEx": (_("Speaks the filename of the active application along with the name of the currently loaded appModule python file. Pressing this key twice,speak the name and state of the current configuration profile"), globalCommands.SCRCAT_TOOLS),
		# Translators: Input help mode message
		# for report current addon's name and version command.
		"reportCurrentAddonNameAndVersion": (_("Report the name and version number of add-on activated for focused application"), globalCommands.SCRCAT_TOOLS),
		# Translators: Input help mode message
		# for displayt current program informations dialog command.
		"DisplayAppModuleInfo": (_("Display informations about the focused application"), globalCommands.SCRCAT_TOOLS),
		# Translators: Input help mode message
		# for display minute timer dialog command.
		"minuteTimer": (_("Display dialog to start the minute timer.If minute timer already started, display dialog to report duration "), None),
		# Translators: Input help mode message
		# for display addon user guide command.
		"displayModuleUserGuide": (_("Display add-on user's guide"), None),
		# Translators: Input help mode message
		# for display shell command help dialog command.
		"displayHelp": (_("Display commands shell's list"), None),
		# Translators: Input help mode message
		# for display log management dialog command.
		"NVDALogsManagement": (_("Open a dialog to manage NVDA logs"), globalCommands.SCRCAT_TOOLS),
		# Translators: Input help mode message
		# for open current or old log command.
		"openCurrentOrOldNVDALogFile": (_("Open current NVDA log file. Pressing this key twice, open the old NVDA log file. Pressing third, copy current log path to the clipboard"), globalCommands.SCRCAT_TOOLS),
		# Translators: Input help mode message
		# for report current folder command in open or save dialog box.
		"reportCurrentFolder": (_("report the name of current selected folder in the open or Save dialog box. Twice: report full path"), None),
		# Translators: Input help mode message
		# for report current folder name command in open or save dialog box.
		"reportCurrentFolderName": (_("report the name of current selected folder in the open or Save dialog box"), None),
		# Translators: Input help mode message
		# for report current folder path command in open or save dialog box.
		"reportCurrentFolderFullPath": (_("report the full path of current selected folder in the open or Save dialog box"), None),
		# Translators: Input help mode message
		# for open user config folder command.
		"exploreUserConfigFolder": (_("Explor my user configuration's folder"), None),
		# Translators: Input help mode message
		# for open NVDA program files folder command.
		"exploreProgramFiles": (_("Explore NVDA programs's folder"), None),
		# Translators: Input help mode message
		# for display speech history records list dialog command.
		"displaySpeechHistoryRecords": (_("display speech history records"), globalCommands.SCRCAT_SPEECH),
		# Translators: Input help mode message
		# for report previous speech history record command.
		"reportPreviousSpeechHistoryRecord": (_("Report previous record of the speech history and copy it to clipboard"), globalCommands.SCRCAT_SPEECH),
		# Translators: Input help mode message
		# for report current speech history record command.
		"reportCurrentSpeechHistoryRecord": (_("Report current record of the speech history and copy it to clipboard. Twice: display speech history"), globalCommands.SCRCAT_SPEECH),
		# Translators: Input help mode  message
		# for report next speech history record command.
		"reportNextSpeechHistoryRecord": (_("Report next record of the speech history and copy it to clipboard"), globalCommands.SCRCAT_SPEECH),
		# Translators: Input help mode message
		# for restart NVDA in default or debug log level command.
		"restartEx": (_("Restart NVDA. Twice: restart with log levelset to debug"), inputCore.SCRCAT_MISC),
		# Translators: Input help mode message
		# for toggle switch voice profile mode command.
		"toggleSwitchVoiceProfileMode": (_("Toggle voice profile switch mode"), SCRCAT_SWITCH_VOICE_PROFILE),
		# Translators: Input help mode message
		# for display voice profile management dialog command.
		"manageVoiceProfileSelectors": (_("Display dialog to manage voice profile selectors"), SCRCAT_SWITCH_VOICE_PROFILE),
		# Translators: Input help mode message
		# for go to previous voice profile selector command.
		"previousVoiceProfile": (_("Go backward to the first selector associated to a voice profile and set this voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE),
		# Translators: Input help mode message
		# for go to next voice profile selector command.
		"nextVoiceProfile": (_("Go to forward to the first selector associated to a voice profile and set this voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE),
		# Translators: Input help mode message
		# for display keyboard key renaming dialog command.
		"keyboardKeyRenaming": (_("Display keyboard key renaming dialog"), None),
		# Translators: Input help mode message
		# for command key selective announcement dialog command.
		"commandKeySelectiveAnnouncement": (_("Display command key selective announcement dialog"), None),
		# Translators: Input help mode message
		# for report or copy to clipboard date and time command.
		"dateTimeEx": (_("Reports the current time. Twice, reports the current date. Third: copy date and time to the clipboard"), globalCommands.SCRCAT_SYSTEM),
		# Translators: Input help mode message
		# for copy date and time to clipboard command.
		"copyDateAndTimeToClip": (_("Copy date and time to the clipboard"), globalCommands.SCRCAT_SYSTEM),
		# Translators: Input help mode message
		# for display formatting dialog command.
		"displayFormatting": (_("Display formatting info for the current review cursor position within a document in dialog box"), None),
		# Translators: Input help mode message
		# for launch module layer command.
		"moduleLayer": (_("Launch %s commands's shell") % _addonSummary, None),
		# Translators: Input help mode message
		# for set VoiceProfile Selector 1 command.
		"setVoiceProfileSelector1": (_("Set selector 1 as current selector and Sets , if possible, it associated voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE),
		# Translators: Input help mode message
		# for set VoiceProfile Selector 2 command.
		"setVoiceProfileSelector2": (_("Set selector 2 as current selector and Sets , if possible, it associated voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE),
		# Translators: Input help mode message
		# for set VoiceProfile Selector 3 command.
		"setVoiceProfileSelector3": (_("Set selector 3 as current selector and Sets , if possible, it associated voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE),
		# Translators: Input help mode message
		# for set VoiceProfile Selector 4 command.
		"setVoiceProfileSelector4": (_("Set selector 4 as current selector and Sets , if possible, it associated voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE),
		# Translators: Input help mode message
		# for set VoiceProfile Selector 5 command.
		"setVoiceProfileSelector5": (_("Set selector 5 as current selector and Sets , if possible, it associated voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE),
		# Translators: Input help mode message
		# for set VoiceProfile Selector 6 command.
		"setVoiceProfileSelector6": (_("Set selector 6 as current selector and Sets , if possible, it associated voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE),
		# Translators: Input help mode message
		# for set VoiceProfile Selector 7 command.
		"setVoiceProfileSelector7": (_("Set selector 7 as current selector and Sets , if possible, it associated voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE),
		# Translators: Input help mode message
		# for set VoiceProfile Selector 8 command.
		"setVoiceProfileSelector8": (_("Set selector 8 as current selector and Sets , if possible, it associated voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE),
		# Translators: Input help mode message
		# for activate user input gesture dialog command.
		"activateUserInputGesturesDialog": (_("Displays the dialog to manage the input gestures configured by user"), None),
		# Translators: Input help mode message
		# for set on main and NVDA volume command.
		"setMainAndNVDAVolume": (_("Set on main and NVDA volume"), SCRCAT_VOLUME_CONTROL),
		# Translators: Input help mode message
		# for toggle current focused application's volume command.
		"toggleCurrentAppVolumeMute": (_("Toggle current focused application volume mute"), SCRCAT_VOLUME_CONTROL),
		# Translators: Input help mode message
		# for increase volume of current focused application command.
		"increaseFocusedAppVolume": (_("Increase volume of current focused application"), SCRCAT_VOLUME_CONTROL),
		# Translators: Input help mode message
		# for decrease volume of current focused application command.
		"decreaseFocusedAppVolume": (_("Decrease volume of current focused application"), SCRCAT_VOLUME_CONTROL),
		# Translators: Input help mode message
		# for maximize volume of current focused application command.
		"maximizeFocusedAppVolume": (_("Maximize volume of current focused application"), SCRCAT_VOLUME_CONTROL),
		# Translators: Input help mode message
		# for minimize volume of current focused application command.
		"minimizeFocusedAppVolume": (_("Minimize volume of current focused application"), SCRCAT_VOLUME_CONTROL),
		# Translators: Input help mode message for tools for add-on developpement dialog command.
		# Translators: Input help mode message
		# for increase volume of speakers command.
		"increaseSpeakersVolume": (_("Increase volume of speakers"), SCRCAT_VOLUME_CONTROL),
		# Translators: Input help mode message
		# for decrease volume of speakers command.
		"decreaseSpeakersVolume": (_("Decrease volume of speakers"), SCRCAT_VOLUME_CONTROL),
		# Translators: Input help mode message
		# for maximize volume of speakers command.
		"maximizeSpeakersVolume": (_("Maximize volume of speakers"), SCRCAT_VOLUME_CONTROL),
		# Translators: Input help mode message
		# for minimize volume of speakers command.
		"minimizeSpeakersVolume": (_("Minimize volume of speakers"), SCRCAT_VOLUME_CONTROL),
		# Translators: Input help mode message
		# for tools for add-on command.
		"toolsForAddon": (_("Display tools for add-on developpement dialog "), globalCommands.SCRCAT_TOOLS),
		# Translators: Input help mode message
		# for leftclick mouse button at navigator cursor position script command.
		"leftClickAtNavigatorObjectPosition": (_("Click the left mouse button at navigator object position. Twice: click twice this button at this position"), globalCommands.SCRCAT_MOUSE),
		# Translators: Input help mode message
		# for right click mouse button at navigator cursor position script command.
		"rightClickAtNavigatorObjectPosition": (_("Click the right mouse button at naviHgator object position. Twice: click twice this button at this position"), globalCommands.SCRCAT_MOUSE),
		# Translators: Input help mode message
		# for addon settings dialog script command.
		"addonSettingsDialog": (_("Display add-on settings dialog"), None),
		# Translators: Input help mode message
		# for toggle standard use of nunumeric keypad.
		"toggleNumpadStandardUse": (_("Enable or disable the standard use of numeric keypad"), None),
		}

	def __init__(self, *args, **kwargs):
		super(NVDAExtensionGlobalPlugin, self).__init__(*args, **kwargs)
		self.curAddon = _curAddon
		addonName = self.curAddon.manifest['name']
		addonVersion = self.curAddon.manifest["version"]
		self.maximizeWindowTimer = None
		log.info("Loaded %s version %s" % (addonName, addonVersion))
		self.installSettingsMenu()
		if isInstall(ID_CommandKeysSelectiveAnnouncement) or\
			isInstall(ID_KeyRemanence):
			wx.CallLater(800, commandKeysSelectiveAnnouncementAndRemanence.initialize)
		if isInstall(ID_ExtendedVirtualBuffer):
			from . import browseModeEx
			self.browseModeExChooseNVDAObjectOverlayClasses = browseModeEx.chooseNVDAObjectOverlayClasses  # noqa:E501
		from . import clipboardCommandAnnouncement
		self.clipboardCommandAnnouncementChooseNVDAObjectOverlayClasses = clipboardCommandAnnouncement.chooseNVDAObjectOverlayClasses  # noqa:E501
		if toggleNoDescriptionReportInRibbonOption(False):
			from . import extendedNetUIHWND
			self.extendedNetUIHWNDChooseNVDAObjectOverlayClasses = extendedNetUIHWND.chooseNVDAObjectOverlayClasses  # noqa:E501
		if isInstall(ID_SpeechHistory):
			wx.CallLater(800, speechHistory.initialize)
		if isInstall(ID_KeyboardKeyRenaming):
			settings._addonConfigManager.reDefineKeyboardKeyLabels()
		self.toggling = False
		self._bindGestures()
		self._setShellGestures()
		core.callLater(200, self.installShellScriptDocs)
		self.switchVoiceProfileMode = "off"
		if toggleSetOnMainAndNVDAVolumeAdvancedOption(False):
			volumeControl.setNVDAVolume(withMin=True)
			volumeControl.setSpeakerVolume(withMin=True)
		if toggleByPassNoDescriptionAdvancedOption(False):
			special.initialize()
		from .scripts import scriptHandlerEx
		scriptHandlerEx.initialize()
		# start update check if not in secur mode and option is set
		if not globalVars.appArgs.secure:
			from .settings import toggleAutoUpdateGeneralOptions
			if toggleAutoUpdateGeneralOptions(False):
				from .settings import toggleUpdateReleaseVersionsToDevVersionsGeneralOptions  # noqa:E501
				from . updateHandler import autoUpdateCheck
				autoUpdateCheck(
					toggleUpdateReleaseVersionsToDevVersionsGeneralOptions(False))

	def _bindGestures(self):
		for script in self._mainScriptToGestureAndfeatureOption:
			(gestures, featureID) = self._mainScriptToGestureAndfeatureOption[script]
			if gestures is None:
				continue
			if featureID:
				if not isInstall(featureID):
					continue
				elif isInstallWithoutGesture(featureID):
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

	def installShellScriptDocs(self):
		for script in self._scriptsToDocsAndCategory:
			(doc, category) = self._getScriptDocAndCategory(script)
			commandText = None
			if script in self._shellScriptToGestureAndFeatureOption:
				(gesture, featureID) = self._shellScriptToGestureAndFeatureOption[script]
				key = gesture.split(":")[-1]
				# Translators: message for indicate shell command in input help mode.
				commandText = _("(command: %s)") % key
			elif script in self._mainScriptToGestureAndfeatureOption:
				(gesture, featureID) = self._mainScriptToGestureAndfeatureOption[script]
			else:
				(gesture, featureID) = (None, None)
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
		(doc, category) = self._scriptsToDocsAndCategory[script]
		if category is None:
			category = SCRCAT_MODULE
		return (doc, category)

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
			_("Settings..."),
			"")
		gui.mainFrame.sysTrayIcon.Bind(
			wx.EVT_MENU, self.onSettingsSubMenu, settingsSubMenu)
		if isInstall(ID_KeyboardKeyRenaming):
			self.keyboardKeysRenamingMenu = menu.Append(
				wx.ID_ANY,
				# Translators: name of the option in the menu.
				_("Keyboard Keys renaming..."),
				"")
			gui.mainFrame.sysTrayIcon.Bind(
				wx.EVT_MENU,
				self.onKeyboardKeysRenamingMenu,
				self.keyboardKeysRenamingMenu)
		if isInstall(ID_CommandKeysSelectiveAnnouncement):
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
		if isInstall(ID_ExploreNVDA):
			self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
			menu = wx.Menu()
			self.exploreNVDAMenu = self.toolsMenu .AppendSubMenu(
				menu,
				# Translators: the name of addon submenu.
				_("Explore &NVDA"),
				# Translators: the tooltip text for addon submenu.
				_("Menu to explore NVDA program or configuration"))
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

	def script_moduleLayer(self, gesture):
		# A run-time binding will occur
		# from which we can perform various layered script commands
		# First, check if a second press of the script was done.
		if self.toggling:
			self.script_error(gesture)
			return
		self.bindGestures(self._shellGestures)
		self.toggling = True
		tones.beep(200, 40)

	def getScript(self, gesture):
		if not self.toggling:
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
		from .scripts import scriptHandlerEx
		scriptHandlerEx.terminate()
		commandKeysSelectiveAnnouncementAndRemanence.terminate()
		if self._repeatBeepOnAudio is not None:
			self._repeatBeepOnAudio .stop()
			self._repeatBeepOnAudio = None
		from .settings import _addonConfigManager
		_addonConfigManager.terminate()
		if hasattr(self, "_caretMovementScriptHelper "):
			CursorManager._caretMovementScriptHelper = self._caretMovementScriptHelper
		speechHistory.terminate()
		for item in ["NVDAExtensionGlobalPluginSettingsMenu", ]:
			if hasattr(self, item):
				self.prefsMenu.Remove(getattr(self, item))
		if hasattr(self, "exploreNVDAMenu"):
			self.toolsMenu .Remove(getattr(self, "exploreNVDAMenu"))
		special.terminate()
		super(NVDAExtensionGlobalPlugin, self).terminate()

	def onSettingsSubMenu(self, evt):
		wx.CallAfter(gui.mainFrame._popupSettingsDialog, AddonSettingsDialog)

	def script_addonSettingsDialog(self, gesture):
		wx.CallAfter(gui.mainFrame._popupSettingsDialog, AddonSettingsDialog)

	def onKeyboardKeysRenamingMenu(self, evt):
		from .keyboardKeyRenaming import KeyboardKeyRenamingDialog
		gui.mainFrame._popupSettingsDialog(KeyboardKeyRenamingDialog)

	def onResetConfiguration(self, evt):
		from .settings import _addonConfigManager
		wx.CallAfter(_addonConfigManager.resetConfiguration)

	def exploreFolder(self, path):
		import subprocess
		cmd = "explorer \"{path}\"" .format(path=path)
		subprocess.call(cmd, shell=True)

	def onExploreUserConfigFolderMenu(self, evt):
		path = globalVars.appArgs.configPath
		wx.CallAfter(self.exploreFolder, path)

	def script_exploreUserConfigFolder(self, gesture):
		self.onExploreUserConfigFolderMenu(None)

	def onExploreProgramFilesMenu(self, evt):
		path = os.getcwd()
		wx.CallAfter(self.exploreFolder, path)

	def script_exploreProgramFiles(self, gesture):
		self.onExploreProgramFilesMenu(None)

	def onCommandKeysSelectiveAnnouncementMenu(self, evt):
		gui.mainFrame._popupSettingsDialog(
			commandKeysSelectiveAnnouncementAndRemanence.CommandKeysSelectiveAnnouncementDialog)  # noqa:E501

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		self.clipboardCommandAnnouncementChooseNVDAObjectOverlayClasses(				obj, clsList)
		if hasattr(self, "extendedNetUIHWNDChooseNVDAObjectOverlayClasses"):
			self.extendedNetUIHWNDChooseNVDAObjectOverlayClasses(obj, clsList)
		if hasattr(self, "browseModeExChooseNVDAObjectOverlayClasses"):
			self.browseModeExChooseNVDAObjectOverlayClasses(obj, clsList)

	def maximizeForegroundWindow(self, windowHandle):
		self.maximizeWindowTimer = None
		oForeground = api.getForegroundObject()
		maximizeWindow(oForeground.windowHandle)

	def event_foreground(self, obj, nextHandler):
		if toggleAutomaticWindowMaximizationOption(False):
			if self.maximizeWindowTimer is not None:
				self.maximizeWindowTimer.Stop()
			self.maximizeWindowTimer = core.callLater(
				2000, self.maximizeForegroundWindow, obj.windowHandle)
		nextHandler()

	def event_gainFocus(self, obj, nextHandler):
		if self._trapNextGainFocus:
			self._trapNextGainFocus = False
			return
		nextHandler()

	def script_copyDateAndTimeToClip(self, gesture):
		dateText = winKernel.GetDateFormat(
			winKernel.LOCALE_USER_DEFAULT, winKernel.DATE_LONGDATE, None, None)
		if toggleReportTimeWithSecondsOption(False):
			timeText = winKernel.GetTimeFormat(
				winKernel.LOCALE_USER_DEFAULT, None, None, None)
		else:
			timeText = winKernel.GetTimeFormat(
				winKernel.LOCALE_USER_DEFAULT, winKernel.TIME_NOSECONDS, None, None)
		msg = "%s %s" % (dateText, timeText)
		api.copyToClip(msg)
		# Translators: message to report date and time copy to clipboard.
		ui.message(_("{0} copied to clipboard").format(msg))

	# modified nvda scripts
	def script_dateTimeEx(self, gesture):
		def callback(action="time"):
			speech.cancelSpeech()
			if action == "copyToClip":
				self.script_copyDateAndTimeToClip(gesture)
				return
			if action == "date":
				text = winKernel.GetDateFormat(
					winKernel.LOCALE_USER_DEFAULT, winKernel.DATE_LONGDATE, None, None)
				ui.message(text)
				return
			curLevel = config.conf["speech"]["symbolLevel"]
			config.conf["speech"]["symbolLevel"] = SYMLVL_SOME
			if toggleReportTimeWithSecondsOption(False):
				text = winKernel.GetTimeFormat(
					winKernel.LOCALE_USER_DEFAULT, None, None, None)
			else:
				text = winKernel.GetTimeFormat(
					winKernel.LOCALE_USER_DEFAULT, winKernel.TIME_NOSECONDS, None, None)
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
	if getInstallFeatureOption(ID_DateAndTime):
		script_dateTimeEx.removeCommandsScript = globalCommands.commands.script_dateTime  # noqa:E501

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
	script_reportAppModuleInfoEx.removeCommandsScript = globalCommands.commands.script_reportAppModuleInfo  # noqa:E501

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
		wx.CallAfter(ListeNotification.run)

	def script_report_WindowsList(self, gesture):
		wx.CallAfter(ActiveWindowsListDisplay.run)

	def script_report_SystrayIconsOrWindowsList(self, gesture):
		def callback():
			clearDelayScriptTask()
			wx.CallAfter(ListeNotification.run)

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

	def script_reportAppProductNameAndVersion(self, gesture):
		def callback(repeatCount):
			clearDelayScriptTask()
			obj = api.getFocusObject()
			appName = obj.appModule.productName
			appVersion = obj.appModule.productVersion
			# Translators: message to report app version.
			text = _("{0} version {1}") .format(appName, appVersion)
			if repeatCount == 0:
				ui.message(text)
			else:
				api.copyToClip(text)
				# Translators: message to report that product name and version
				# are copied to clipboard.
				ui.message(_("Product name and version has been copied to clipboard"))
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
				msg = _("addon: {name}, version: {version}").format(
					name=addon.manifest["name"], version=addon.manifest["version"])
				ui.message(msg)
				return
		# Translators: indicates that there is no active addon
				# for current focused application.
		msg = _("No addon")
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
		appName = "%s, %s" % (appProcessName, focus.appModule.productName)
		appVersion = focus.appModule.productVersion
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
		text = _("addd-on's path: %s") % path
		textList.append(text)
		if len(addons) > 1:
			# Translators: indicate that others add-ons are installed
			# and activated for this application.
			text = _("Warning: it seems that others add-ons are installed and activated for this application")   # noqa:E501
			textList.append(text)
		# Translators: Indicates the name of the appModule for the current program.
		msg = _("Loaded python module: %s") % modName
		textList.append(msg)
		# Translators: title of informationdialog box to show appModule informations.
		dialogTitle = _("Application context's informations's informations")
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
				path = logFile if py3 else logFile.decode("mbcs")
				if api.copyToClip(path):
					ui.message(_("Current log file path copied to clipboard"))
				else:
					ui.message(_("Current log file path cannot be copied to clipboard"))
				return
			elif action == "openOld":
				logFile = os.path.join(
					os.path.dirname(_getDefaultLogFilePath()), "nvda-old.log")
				errorMsg = _("Previous log file can not be opened")
			elif action == "openCurrent":
				logFile = os.path.join(
					os.path.dirname(_getDefaultLogFilePath()), "nvda.log")
				errorMsg = _("Current log file can not be opened")
			try:
				os.startfile(logFile)
			except:  # noqa:E722
				wx.CallAfter(
					gui.messageBox,
					errorMsg,
					# Translators: dialog title.
					_("Open Error"),
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
			speechHistory.getSpeechRecorder().reportSpeechHistory("previous")

	def script_reportNextSpeechHistoryRecord(self, gesture):
		stopDelayScriptTask()
		if speechHistory.isActive():
			speechHistory.getSpeechRecorder().reportSpeechHistory("next")

	def script_reportCurrentSpeechHistoryRecord(self, gesture):
		def callback():
			clearDelayScriptTask()
			if speechHistory.isActive():
				speechHistory.getSpeechRecorder().reportSpeechHistory("current")
		stopDelayScriptTask()
		count = scriptHandler.getLastScriptRepeatCount()
		if count == 0:
			delayScriptTask(callback)
		else:
			speechHistory.getSpeechRecorder().displaySpeechHistory()

	def script_displaySpeechHistoryRecords(self, gesture):
		speechHistory.getSpeechRecorder().displaySpeechHistory()

	def script_displayFormatting(self, gesture):
		reportFormattingOptions = (
			"reportFontName",
			"reportFontSize",
			"reportFontAttributes",
			"reportSuperscriptsAndSubscripts",
			"reportColor",
			"reportStyle",
			"reportAlignment",
			"reportSpellingErrors",
			"reportLineIndentation",
			"reportParagraphIndentation",
			"reportLineSpacing",
			"reportBorderStyle",
			"reportBorderColor",
		)
	
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
			textList.append(speech.getIndentationSpeech(indentation, formatConfig))
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
		wx.CallAfter(gui.mainFrame._popupSettingsDialog, KeyboardKeyRenamingDialog)

	def script_commandKeySelectiveAnnouncement(self, gesture):
		from .commandKeysSelectiveAnnouncementAndRemanence import CommandKeysSelectiveAnnouncementDialog  # noqa:E501
		wx.CallAfter(
			gui.mainFrame._popupSettingsDialog, CommandKeysSelectiveAnnouncementDialog)

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
	script_speakForegroundEx.removeCommandsScript = globalCommands.commands.script_speakForeground  # noqa:E501

	def script_displayModuleUserGuide(self, gesture):
		path = self.curAddon.getDocFilePath()
		speech.speakMessage(_("Please wait"))
		os.startfile(path)

	def script_shutdownComputerDialog(self, gesture):
		from .computerTools import shutdown_gui as shutdown_gui
		shutdown_gui.ComputerShutdownDialog.run()

	def script_shutdownComputer(self, gesture):
		from .computerTools.shutdown_util import shutdown as shutdown
		forceClose = True
		timeout = 0
		shutdown(timeout, forceClose)

	def script_rebootComputer(self, gesture):
		from .computerTools.shutdown_util import reboot as reboot
		forceClose = True
		timeout = 0
		reboot(timeout, forceClose)

	def script_hibernateComputer(self, gesture):
		from .computerTools.shutdown_util import suspend as suspend
		suspend(hibernate=True)

	def script_toggleCurrentAppVolumeMute(self, gesture):
		focus = api.getFocusObject()
		appName = appModuleHandler.getAppNameFromProcessID(focus.processID, True)
		if appName == "nvda.exe":
			speech.speakMessage(_("Unavailable for NVDA"))
			return
		try:
			volumeControl.toggleProcessVolume(appName)
		except:  # noqa:E722
			speech.speakMessage(_("Not available on this operating's system"))

	def script_setMainAndNVDAVolume(self, gesture):
		if volumeControl.setSpeakerVolume() and volumeControl.setNVDAVolume():
			speech.speakMessage(
				# Translators: message to user  nvda and main volume  are established .
				_("The main volume and that of NVDA are established and their level sets to the one in the configuration"))  # noqa:E501
		else:
			speech.speakMessage(_("Not available on this operating's system"))

	def script_increaseFocusedAppVolume(self, gesture):
		wx.CallAfter(volumeControl.changeFocusedAppVolume, action="increase")
	script_increaseFocusedAppVolume .noFinish = True

	def script_decreaseFocusedAppVolume(self, gesture):
		wx.CallAfter(volumeControl.changeFocusedAppVolume, action="decrease")
	script_decreaseFocusedAppVolume .noFinish = True

	def script_maximizeFocusedAppVolume(self, gesture):
		wx.CallAfter(volumeControl.changeFocusedAppVolume, action="max")
	script_maximizeFocusedAppVolume .noFinish = True

	def script_minimizeFocusedAppVolume(self, gesture):
		wx.CallAfter(volumeControl.changeFocusedAppVolume, action="min")
	script_minimizeFocusedAppVolume .noFinish = True

	def script_increaseSpeakersVolume(self, gesture):
		wx.CallAfter(volumeControl.changeSpeakersVolume, action="increase")
	script_increaseSpeakersVolume .noFinish = True

	def script_decreaseSpeakersVolume(self, gesture):
		wx.CallAfter(volumeControl.changeSpeakersVolume, action="decrease")
	script_decreaseSpeakersVolume .noFinish = True

	def script_maximizeSpeakersVolume(self, gesture):
		wx.CallAfter(volumeControl.changeSpeakersVolume, action="max")
	script_maximizeSpeakersVolume .noFinish = True

	def script_minimizeSpeakersVolume(self, gesture):
		wx.CallAfter(volumeControl.changeSpeakersVolume, action="min")
	script_minimizeSpeakersVolume .noFinish = True

	def script_manageVoiceProfileSelectors(self, gesture):
		from . import switchVoiceProfile
		wx.CallAfter(switchVoiceProfile.SelectorsManagementDialog .run, self)

	def script_nextVoiceProfile(self, gesture):
		from . import switchVoiceProfile
		switchVoiceProfile.SwitchVoiceProfilesManager().nextVoiceProfile(
			forward=True)

	def script_previousVoiceProfile(self, gesture):
		from . import switchVoiceProfile
		switchVoiceProfile.SwitchVoiceProfilesManager().nextVoiceProfile(
			forward=False)

	def script_toggleSwitchVoiceProfileMode(self, gesture):
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

		def toggleSwitchVoiceProfileMode(mmode=""):
			if mode != "":
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
		mode = ""
		if gesture.displayName == "escape":
			mode = "off"
		wx.CallAfter(toggleSwitchVoiceProfileMode, mode)

	def setVoiceProfileSelector(self, selector):
		from . import switchVoiceProfile
		switchManager = switchVoiceProfile.SwitchVoiceProfilesManager()
		switchManager.setLastSelector(selector)
		if switchManager.isSet(selector):
			wx.CallAfter(switchManager.switchToVoiceProfile, selector)
			return
		# Translators: message to  user that the selector is not set.
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
			speech.speakMessage(
				# Translators: message to user no configuration change made.
				_("There has been no change of gesture made by the user"))
			return
		wx.CallAfter(gui.mainFrame._popupSettingsDialog, UserInputGesturesDialog)

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
				except:  # noqa:E722
					# Translators: Reported when the object has no location
					# for the mouse to move to it.
					ui.message(_("Object has no location"))
					return
				x = int(left + (width / 2))
				y = int(top + (height / 2))
			oldSpeechMode = speech.speechMode
			speech.speechMode = speech.speechMode_off
			winUser.setCursorPos(x, y)
			mouseHandler.executeMouseMoveEvent(x, y)
			time.sleep(0.2)
			speech.speechMode = oldSpeechMode
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
				except:  # noqa:E722
					# Translators: Reported when the object has no location
					# for the mouse to move to it.
					ui.message(_("Object has no location"))
					return
				x = int(left + (width / 2))
				y = int(top + (height / 2))
			oldSpeechMode = speech.speechMode
			speech.speechMode = speech.speechMode_off
			winUser.setCursorPos(x, y)
			mouseHandler.executeMouseMoveEvent(x, y)
			time.sleep(0.2)
			speech.speechMode = oldSpeechMode
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

	def script_toggleNumpadStandardUse(self, gesture):
		if not isInstall(ID_CommandKeysSelectiveAnnouncement) and\
			not isInstall(ID_KeyRemanence):
			speech.speakMessage(
				# Translators: message to user the fonctionnality is not available.
				_("""This functionnality is only available if "command key selective announcement" or "keys's remanence functionnality" is installed"""))  # noqa:E501
			return
		from .settings import toggleEnableNumpadNavigationModeToggleAdvancedOption
		if not toggleEnableNumpadNavigationModeToggleAdvancedOption(False):

			speech.speakMessage(
				# Translators: message to user the fonctionnality is not available.
				_("""This functionnality is only available if "command key selective announcement" or "keys's remanence functionnality" is installed"""))  # noqa:E501
			return
		from .commandKeysSelectiveAnnouncementAndRemanence import _myInputManager
		_myInputManager .toggleNavigationNumpadMode()

	def script_toggleNumpadStandardUseWithNumlockKey(self, gesture):

		def callback(gesture):
			clearDelayScriptTask()
			if isInstall(ID_CommandKeysSelectiveAnnouncement) or\
				isInstall(ID_KeyRemanence):
				gesture.reportExtra()
		stopDelayScriptTask()
		if not toggleEnableNumpadNavigationModeToggleAdvancedOption(False) or\
			not toggleActivateNumpadStandardUseWithNumLockAdvancedOption(False):
			gesture.send()
			callback(gesture)
			return
		count = scriptHandler.getLastScriptRepeatCount()
		gesture.send()
		if count == 0:
			delayScriptTask(callback, gesture)
		else:
			if not isInstall(ID_CommandKeysSelectiveAnnouncement) and\
				not isInstall(ID_KeyRemanence):
				speech.speakMessage(
					# Translators: message to user the fonctionnality is not available.
					_("""This functionnality is only available if "command key selective announcement" or "keys's remanence functionnality" is installed"""))  # noqa:E501
				return
			self.script_toggleNumpadStandardUse(gesture)

	def checkUpdateWithLocalMyAddonsFile(self, auto=False):
		path = "F:\\nvdaprojet\\paulber007Repositories\\AllMyNVDAAddons\\myAddons.latest"  # noqa:E501
		from .settings import toggleUpdateReleaseVersionsToDevVersionsGeneralOptions
		from .updateHandler.update_check import CheckForAddonUpdate
		wx.CallAfter(
			CheckForAddonUpdate,
			addonName=None,
			updateInfosFile=path,
			auto=auto,
			releaseToDev=toggleUpdateReleaseVersionsToDevVersionsGeneralOptions(False))

	def script_test(self, gesture):
		print("test")
		ui.message("NVDAExtensionGlobalPlugin test")
		self.checkUpdateWithLocalMyAddonsFile()


class HelperDialog(wx.Dialog):
	_instance = None
	title = None

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
		self.scriptToKey = {}
		for script in self.globalPlugin._scriptsToDocsAndCategory:
			if script not in self.globalPlugin._shellScriptToGestureAndFeatureOption:
				continue
			gest = self.globalPlugin._shellScriptToGestureAndFeatureOption[script][0]
			if gest in self.globalPlugin._shellGestures:
				(doc, category) = self.globalPlugin._scriptsToDocsAndCategory[script]
				key = ":".join(gest.split(":")[1:])
				self.scriptToKey[script] = key
				self.docToScript[doc] = script

	def doGui(self):
		self.initList()
		self.docList = sorted([doc for doc in self.docToScript])
		choice = []
		for doc in self.docList:
			script = self.docToScript[doc]
			key = self.scriptToKey[script]
			choice.append("%s: %s" % (doc, key))

		from gui import guiHelper
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# the list box
		# Translators: This is the label of the list appearing
		# on Active Windows List Display dialog.
		labelText = _("Description: command")
		self.scriptsListBox = sHelper.addLabeledControl(
			labelText,
			wx.ListBox,
			id=wx.ID_ANY,
			choices=choice,
			style=wx.LB_SINGLE,
			size=(700, 280))
		if self.scriptsListBox.GetCount():
			self.scriptsListBox.SetSelection(0)
		# Buttons
		bHelper = guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: This is a label of a button appearing
		# on active windows list display dialog.
		runScriptButton = bHelper.addButton(
			self, id=wx.ID_ANY, label=_("&Run script"))
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
		self.Bind(wx.EVT_ACTIVATE, self.onActivate)
		self.SetEscapeId(wx.ID_CLOSE)

	def Destroy(self):
		HelperDialog._instance = None
		super(HelperDialog, self).Destroy()

	def onActivate(self, evt):
		evt.Skip()

	def onRunScriptButton(self, evt):
		index = self.scriptsListBox.GetSelection()
		doc = self.docList[index]
		script = self.docToScript[doc]
		key = self.scriptToKey[script]
		from keyboardHandler import KeyboardInputGesture
		gesture = KeyboardInputGesture.fromName(key)
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
