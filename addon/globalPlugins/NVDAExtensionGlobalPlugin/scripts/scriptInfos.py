# globalPlugins\NVDAExtensionGlobalPlugin\__init__.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2021 Paulber19
# This file is covered by the GNU General Public License.

import addonHandler
import globalCommands
import inputCore
from ..utils.NVDAStrings import NVDAString
addonHandler.initTranslation()

# Translators: The name of a category of NVDA commands.
SCRCAT_SWITCH_VOICE_PROFILE = _("Voice profile switching")
# Translators: Input help mode message
# for display active windows 's list dialog command.
activeWindowsDoc = _(
	"Display the running application windows's list with opportunity to put one of them on the foreground "
	"or destroy it")
# Translators: Input help mode message
# for display systray icons list dialog command.
systrayIconsDoc = _("Shows the list of buttons on the System Tray")
# Translators: The name of a category of NVDA commands.
SCRCAT_VOLUME_CONTROL = _("Volume control")
# Translators: Input help mode message
# for setting to x percent the volume of current focused application command.
_setFocusedAppVolumeToMsg = _(
	"Set the volume of current focused application to %s percent of speakers volume")
# Translators: Input help mode message
# for setting to x the main volume.
_setSpeakersVolumeToMsg = _("Set the main volume to %s")
# Translators: Input help mode message
# for setting to x percent the volume of NVDA command
_setNVDAVolumeToMsg = _("Set the NVDA volume to %s percent of speakers volume")

scriptsToDocInformations = {
	# Translators: Input help mode message
	# for display shutdown , reboot or hibernate computer dialog command.
	"shutdownComputerDialog": (
		_("Display the dialog to shutdown, reboot or hibernate the computer"), None, "hdr19"),
	# Translators: Input help mode message
	# for shutdown computer command.
	"shutdownComputer": (_("Shutdown the computer"), None, "hdr19"),
	# Translators: Input help mode message
	# for reboot computer command.
	"rebootComputer": (_("Reboot the computer"), None, "hdr19"),
	# Translators: Input help mode message
	# for hibernate computer command.
	"hibernateComputer": (_("Hibernate the computer"), None, "hdr19"),
	# Translators: Input help mode message
	# for display complex symbols help dialog command.
	"ComplexSymbolHelp": (_("Allow you to copy or type complex symbol"), None, "hdr3-1"),
	# Translators: Input help mode message
	# for lastUsedComplexSymbolsList.
	"lastUsedComplexSymbolsList": (_("Display the list of last used complex symbols"), None, "hdr3-2"),
	# Translators: Input help mode message
	# for list foreground object command (usually the foreground window).
	"foregroundWindowObjectsList": (
		_("Display the list's visible items making up current foreground object"),
		globalCommands.SCRCAT_FOCUS, "hdr16"),
	# Translators: Input help mode message
	# for read or list foreground object command (usually the foreground window).
	"speakForegroundEx": ("%s. %s" % (
		globalCommands.commands.script_speakForeground.__func__.__doc__,
		_("If pressed twice: display the list's visible items making up it")),
		globalCommands.SCRCAT_FOCUS, ""),
	"report_WindowsList": (activeWindowsDoc, None, "hdr1-2"),
	"report_SystrayIcons": (systrayIconsDoc, None, "hdr1-1"),
	# Translators: Input help mode message
	# for display systray icons list or active windows list dialog command.
	"report_SystrayIconsOrWindowsList": (
		_("{systrayIconsDoc}. Twice, {activeWindowsDoc}").format(
			systrayIconsDoc=systrayIconsDoc, activeWindowsDoc=activeWindowsDoc),
		None, "hdr1-3"),
	# Translators: Input help mode message
	# for report current application name and version command.
	"reportAppProductNameAndVersion": (
		_("Report the application 's name and version. Twice: copy these informations to clipboard"),
		globalCommands.SCRCAT_TOOLS, None),
	# Translators: Input help mode message
	# for report current program name and app module name or current configuration profile name command.
	"reportAppModuleInfoEx": (
		_(
			"Speaks the filename of the active application along "
			"with the name of the currently loaded appModule python file. "
			"Pressing this key twice,speak the name and state of the current configuration profile"),
		globalCommands.SCRCAT_TOOLS, None),
	# Translators: Input help mode message
	# for report current addon's name and version command.
	"reportCurrentAddonNameAndVersion": (
		_("Report the name and version number of add-on activated for focused application"),
		globalCommands.SCRCAT_TOOLS, None),
	# Translators: Input help mode message
	# for displayt current program informations dialog command.
	"DisplayAppModuleInfo": (
		_("Display informations about the focused application"), globalCommands.SCRCAT_TOOLS, "hdr4-2"),
	# Translators: Input help mode message
	# for display minute timer dialog command.
	"minuteTimer": (
		_(
			"Display dialog to start the minute timer. "
			"If minute timer already started, display dialog to report duration"), None, "hdr14"),
	# Translators: Input help mode message
	# for display addon user guide command.
	"displayModuleUserGuide": (_("Display add-on user's guide"), None, ""),
	# Translators: Input help mode message
	# for display shell command help dialog command.
	"displayHelp": (_("Display the list of commands of the commands interpreter"), None, "hdr0-1-3"),
	# Translators: Input help mode message
	# for display log management dialog command.
	"NVDALogsManagement": (_("Open a dialog to manage NVDA logs"), globalCommands.SCRCAT_TOOLS, "hdr9-1"),
	# Translators: Input help mode message
	# for open current or old log command.
	"openCurrentOrOldNVDALogFile": (
		_(
			"Open current NVDA log file. Pressing this key twice, open the old NVDA log file. "
			"Pressing third, copy current log path to the clipboard"), globalCommands.SCRCAT_TOOLS, "hdr9-2"),
	# Translators: Input help mode message
	# for report current folder command in open or save dialog box.
	"reportCurrentFolder": (
		_("report the name of current selected folder in the open or Save dialog box. Twice: report full path"),
		None, None),
	# Translators: Input help mode message
	# for report current folder name command in open or save dialog box.
	"reportCurrentFolderName": (
		_("report the name of current selected folder in the open or Save dialog box"), None, "hdr8"),
	# Translators: Input help mode message
	# for report current folder path command in open or save dialog box.
	"reportCurrentFolderFullPath": (
		_("report the full path of current selected folder in the open or Save dialog box"), None, "hdr8"),
	# Translators: Input help mode message
	# for open user config folder command.
	"exploreUserConfigFolder": (_("Explore my user configuration's folder"), None, "hdr202"),
	# Translators: Input help mode message
	# for open NVDA program files folder command.
	"exploreProgramFiles": (_("Explore NVDA program's folder"), None, "hdr202"),
	# Translators: Input help mode message
	# for display speech history records list dialog command.
	"displaySpeechHistoryRecords": (
		_("Display speech history records"), globalCommands.SCRCAT_SPEECH, "hdr10-1"),
	# Translators: Input help mode message
	# for report previous speech history record command.
	"reportPreviousSpeechHistoryRecord": (
		_("Report previous record of the speech history"),
		globalCommands.SCRCAT_SPEECH, "hdr10"),
	# Translators: Input help mode message
	# for report current speech history record command.
	"reportCurrentSpeechHistoryRecord": (
		_(
			"Report current record of the speech history.Pressing Twice: copy it to clipboard. "
			"Pressing three: display speech history"), globalCommands.SCRCAT_SPEECH, "hdr10"),
	# Translators: Input help mode message
	# for report next speech history record command.
	"reportNextSpeechHistoryRecord": (
		_("Report next record of the speech history"),
		globalCommands.SCRCAT_SPEECH, "hdr10"),
	# Translators: Input help mode message
	# for restart NVDA in default or debug log level command.
	"restartEx": (_("Restart NVDA. Twice: restart with log level set to debug"), inputCore.SCRCAT_MISC, "hdr15"),
	# Translators: Input help mode message
	# for toggle switch voice profile mode command.
	"toggleSwitchVoiceProfileMode": (
		_("Toggle voice profile switch mode"), SCRCAT_SWITCH_VOICE_PROFILE, "hdr17-2"),
	# Translators: Input help mode message
	# for display voice profile management dialog command.
	"manageVoiceProfileSelectors": (
		_("Display dialog to manage voice profile selectors"), SCRCAT_SWITCH_VOICE_PROFILE, "hdr17-1"),
	# Translators: Input help mode message
	# for go to previous voice profile selector command.
	"previousVoiceProfile": (
		_(
			"Go backward to the first selector associated to a voice profile "
			"and set this voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE, "hdr17"),
	# Translators: Input help mode message
	# for go to next voice profile selector command.
	"nextVoiceProfile": (
		_(
			"Go to forward to the first selector associated to a voice profile "
			"and set this voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE, "hdr17"),
	# Translators: Input help mode message
	# for display keyboard keys renaming dialog command.
	"keyboardKeyRenaming": (_("Display keyboard keys renaming dialog"), None, "hdr12"),
	# Translators: Input help mode message
	# for command key selective announcement dialog command.
	"commandKeySelectiveAnnouncement": (_("Display command key selective announcement dialog"), None, "hdr13"),
	# Translators: Input help mode message
	# for report or copy to clipboard date and time command.
	"dateTimeEx": (
		_(
			"Report the current time. "
			"Twice: report the current date. Third: copy date and time to the clipboard"),
		globalCommands.SCRCAT_SYSTEM, "hdr24-2"),
	# Translators: Input help mode message
	# for copy date and time to clipboard command.
	"copyDateAndTimeToClip": (_("Copy date and time to the clipboard"), globalCommands.SCRCAT_SYSTEM, "hdr24-1"),
	# Translators: Input help mode message
	# for display formatting dialog command.
	"displayFormatting": (
		_(
			"Display, in dialog box, formatting informations "
			"for the current review cursor position within a document"),
		None, "hdr203"),
	# Translators: Input help mode message
	# for launch module layer command.
	"moduleLayer": (_("Launch commands's interpreter of add-on"), None, "hdr0-1-3"),
	# Translators: Input help mode message
	# for set VoiceProfile Selector 1 command.
	"setVoiceProfileSelector1": (
		_(
			"Set selector 1 as current selector and set, if possible, "
			"its associated voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE, "hdr17"),
	# Translators: Input help mode message
	# for set VoiceProfile Selector 2 command.
	"setVoiceProfileSelector2": (
		_(
			"Set selector 2 as current selector and set, if possible, "
			"its associated voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE, "hdr17"),
	# Translators: Input help mode message
	# for set VoiceProfile Selector 3 command.
	"setVoiceProfileSelector3": (
		_(
			"Set selector 3 as current selector and set, if possible, "
			"its associated voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE, "hdr17"),
	# Translators: Input help mode message
	# for set VoiceProfile Selector 4 command.
	"setVoiceProfileSelector4": (
		_(
			"Set selector 4 as current selector and set, if possible, "
			"its associated voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE, "hdr17"),
	# Translators: Input help mode message
	# for set VoiceProfile Selector 5 command.
	"setVoiceProfileSelector5": (
		_(
			"Set selector 5 as current selector and set, if possible, "
			"its associated voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE, "hdr17"),
	# Translators: Input help mode message
	# for set VoiceProfile Selector 6 command.
	"setVoiceProfileSelector6": (
		_(
			"Set selector 6 as current selector and set, if possible, "
			"its associated voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE, "hdr17"),
	# Translators: Input help mode message
	# for set VoiceProfile Selector 7 command.
	"setVoiceProfileSelector7": (
		_(
			"Set selector 7 as current selector and set, if possible, "
			"its associated voice profile as current voice profile"), SCRCAT_SWITCH_VOICE_PROFILE, "hdr17"),
	# Translators: Input help mode message
	# for set VoiceProfile Selector 8 command.
	"setVoiceProfileSelector8": (
		_(
			"Set selector 8 as current selector and set, if possible, "
			"its associated voice profile as current voice profile"),
		SCRCAT_SWITCH_VOICE_PROFILE, "hdr17"),
	# Translators: Input help mode message
	# for activate user input gesture dialog command.
	"activateUserInputGesturesDialog": (
		_("Displays the dialog to manage the input gestures configured by user"), None, "hdr20"),
	# Translators: Input help mode message
	# for tools for add-on command.
	"toolsForAddon": (_("Display tools for add-on development dialog "), globalCommands.SCRCAT_TOOLS, "hdr22"),
	# Translators: Input help mode message
	# for leftclick mouse button at navigator cursor position script command.
	"leftClickAtNavigatorObjectPosition": (
		_(
			"Click the left mouse button at navigator object position. "
			"Twice: click twice this button at this position"),
		globalCommands.SCRCAT_MOUSE, "hdr23"),
	# Translators: Input help mode message
	# for right click mouse button at navigator cursor position script command.
	"rightClickAtNavigatorObjectPosition": (
		_(
			"Click the right mouse button at navigator object position. "
			"Twice: click twice this button at this position"), globalCommands.SCRCAT_MOUSE, "hdr23"),
	# Translators: Input help mode message
	# for global settings dialog script command.
	"globalSettingsDialog": (_("Display add-on settings dialog"), None, "hdr-configurationMenu"),
	# Translators: Input help mode message
	# for profile settings dialog script command.
	"profileSettingsDialog": (
		_("Display settings dialog for current configuration profile"), None, "hdr-configurationMenu"),
	# Translators: Input help mode message
	# for toggle standard use of nunumeric keypad script.
	"toggleNumpadStandardUse": (_("Enable or disable the standard use of numeric keypad"), None, "hdr304"),
	# Translators: Input help mode message
	# for CloseAllWindows script command.
	"closeAllWindows": (_("Close all opened windows"), None, "hdr26"),
	# Translators: Input help mode message
	# for displayRunningAddonsList script command.
	"displayRunningAddonsList": (_("Display running add-ons list"), None, "hdr27"),
	# Translators: Input help mode message
	# for reportOrDisplayCurrentSpeechSettings script commands.
	"reportOrDisplayCurrentSpeechSettings": (
		_("Report current speech settings. Twice: display them"), globalCommands.SCRCAT_SPEECH, "hdr17-6"),
	# Translators: Input help mode message
	# for reportCurrentSpeechSettings script commands.
	"reportCurrentSpeechSettings": (
		_("Report current speech settings"), globalCommands.SCRCAT_SPEECH, "hdr17-6"),
	# Translators: Input help mode message
	# for displayCurrentSpeechSettings script commands.
	"displayCurrentSpeechSettings": (
		_("Display current speech settings"), globalCommands.SCRCAT_SPEECH, "hdr17-6"),
	# Translators: Input help mode message
	# for toggleTextAnalyzer script commands.
	"toggleTextAnalyzer": (_("activate or desactivate text analyzer"), None, "hdr31-1"),
	# Translators: Input help mode message
	# for analyzeCurrentWord script commands.
	"analyzeCurrentWord": (_("Analyze the word under system cursor"), None, "hdr31-3"),
	# Translators: Input help mode message
	# for analyzeCurrentLine script commands.
	"analyzeCurrentLine": (_("Analyze the line under system cursor"), None, "hdr31-3"),
	# Translators: Input help mode message
	# for analyzeCurrentSentence script commands.
	"analyzeCurrentSentence": (_("Analyze the sentence under system cursor"), None, "hdr31-3"),
	# Translators: Input help mode message
	# for analyzeCurrentParagraph script commands.
	"analyzeCurrentParagraph": (_("Analyze the paragraph under system cursor"), None, "hdr31-3"),
	# Translators: Input help mode message
	# for find and move to next line with textanalyzer irregularity
	"findNextTextAnalyzerAlert": (
		_("Move to next irregularity detected by text analyzer"),
		None, "hdr31-3"),
	# Translators: Input help mode message
	# for find and move to previous line with textanalyzer irregularitiy
	"findPreviousTextAnalyzerAlert": (
		_("Move to previous irregularity detected by text analyzer"),
		None, "hdr31-3"),
	# Translators: Input help mode message
	# for manageUserConfigurations script commands.
	"manageUserConfigurations": (_("Display the dialog to manage user configurations"), None, "hdr30"),
	# Translators: Input help mode message
	# for toggleReportCurrentCaretPosition script commands.
	"toggleReportCurrentCaretPosition": (
		_("Toggle reporting of current caret position in edit box"), None, "hdr32"),
	# Translators: Input help mode message
	# for reportClipboardTextEx script commands.
	"reportClipboardTextEx": (
		NVDAString("Reports the text on the Windows clipboard"),
		globalCommands.SCRCAT_SYSTEM,
		"hdr7-2"),
	# Translators: Input help mode message
	# for addToClip script commands.
	"addToClip": (_("Add, to clipboard, the selected text "), None, "hdr7-1"),
	# Translators: Input help mode message
	# for clearClipboard script commands.
	"emptyClipboard": (_("Empty the clipboard"), globalCommands.SCRCAT_SYSTEM, "hdr7-3"),
	# Translators: Input help mode message
	# for temporary audio device manager script commands.
	"temporaryAudioOutputDeviceManager": (
		_("Display the temporary audio device manager"), globalCommands.SCRCAT_SPEECH, "hdr33-1"),
	# Translators: Input help mode message
	# for cancel temporary audio device script commands.
	"cancelTemporaryAudioOutputDevice": (
		_("Leave up the temporary audio device"), globalCommands.SCRCAT_SPEECH, "hdr33-3"),
	# Translators: Input help mode message
	# for set temporary audio device script commands.
	"setTemporaryAudioOutputDevice": (
		_(
			"Set, as temporary audio device, the next device "
			"in the list of checked devices of the temporary audio device manager"),
		globalCommands.SCRCAT_SPEECH, "hdr33-2"),
	# Translators: Input help mode message
	# for set or cancel temporary audio device script commands.
	"setOrCancelTemporaryAudioOutputDevice": (
		_(
			"Set, as temporary audio output device , the next device in the list of devices selected "
			"in the temporary audio output device manager. "
			"Twice: leave up the temporary audio output device"), globalCommands.SCRCAT_SPEECH, "hdr33-4"),
	# Translators: Input help mode message
	# for activate addons activation dialog script commands.
	"activateQuickAddonsActivationDialog": (
		_("Activate quick Addons Activation Dialog"), globalCommands.SCRCAT_SPEECH, "hdr35"),

	# volumeControlScripts To DocInformations
	# Translators: Input help mode message
	# for set on main and NVDA volume command.
	"setMainAndNVDAVolume": (_("Set on main and NVDA volume"), SCRCAT_VOLUME_CONTROL, "hdr21-4"),
	# Translators: Input help mode message
	# for toggle current focused application's volume command.
	"toggleCurrentAppVolumeMute": (
		_("Toggle current focused application volume mute"), SCRCAT_VOLUME_CONTROL, "hdr21-2"),
	# for focused application volume
	# Translators: Input help mode message
	# for increase volume of current focused application command.
	"increaseFocusedAppVolume": (
		_("Increase volume of current focused application"), SCRCAT_VOLUME_CONTROL, "hdr21-3"),
	# Translators: Input help mode message
	# for decrease volume of current focused application command.
	"decreaseFocusedAppVolume": (
		_("Decrease volume of current focused application"), SCRCAT_VOLUME_CONTROL, "hdr21-3"),
	# Translators: Input help mode message
	# for maximize volume of current focused application command.
	"maximizeFocusedAppVolume": (
		_("Maximize volume of current focused application"), SCRCAT_VOLUME_CONTROL, "hdr21-3"),
	# Translators: Input help mode message
	# for minimize volume of current focused application command.
	"minimizeFocusedAppVolume": (
		_("Minimize volume of current focused application"), SCRCAT_VOLUME_CONTROL, "hdr21-3"),
	# Translators: Input help mode message
	# for set app volume to x percent commands
	"setFocusedAppVolumeTo10Percent": (_setFocusedAppVolumeToMsg % 10, SCRCAT_VOLUME_CONTROL, "hdr21-3"),
	"setFocusedAppVolumeTo20Percent": (_setFocusedAppVolumeToMsg % 20, SCRCAT_VOLUME_CONTROL, "hdr21-3"),
	"setFocusedAppVolumeTo30Percent": (_setFocusedAppVolumeToMsg % 30, SCRCAT_VOLUME_CONTROL, "hdr21-3"),
	"setFocusedAppVolumeTo40Percent": (_setFocusedAppVolumeToMsg % 40, SCRCAT_VOLUME_CONTROL, "hdr21-3"),
	"setFocusedAppVolumeTo50Percent": (_setFocusedAppVolumeToMsg % 50, SCRCAT_VOLUME_CONTROL, "hdr21-3"),
	"setFocusedAppVolumeTo60Percent": (_setFocusedAppVolumeToMsg % 60, SCRCAT_VOLUME_CONTROL, "hdr21-3"),
	"setFocusedAppVolumeTo70Percent": (_setFocusedAppVolumeToMsg % 70, SCRCAT_VOLUME_CONTROL, "hdr21-3"),
	"setFocusedAppVolumeTo80Percent": (_setFocusedAppVolumeToMsg % 80, SCRCAT_VOLUME_CONTROL, "hdr21-3"),
	"setFocusedAppVolumeTo90Percent": (_setFocusedAppVolumeToMsg % 90, SCRCAT_VOLUME_CONTROL, "hdr21-3"),
	# Translators: Input help mode message
	# for setting back to previous level the volume of current focused application command.
	"setFocusedAppVolumeToPreviousLevel": (
		_("Set the volume of current focused application to previous level"), SCRCAT_VOLUME_CONTROL, "hdr21-5"),

	# scripts for nvda volume
	# Translators: Input help mode message
	# for increase NVDA volume command.
	"increaseNVDAVolume": (_("Increase NVDA volume"), SCRCAT_VOLUME_CONTROL, "hdr21-3"),
	# Translators: Input help mode message
	# for decrease NVDA volume command.
	"decreaseNVDAVolume": (_("Decrease NVDA volume"), SCRCAT_VOLUME_CONTROL, "hdr21-3"),
	# Translators: Input help mode message
	# for maximize NVDA volume command.
	"maximizeNVDAVolume": (_("Maximize NVDA volume"), SCRCAT_VOLUME_CONTROL, "hdr21-3"),
	# Translators: Input help mode message
	# for minimize NVDA volume command.
	"minimizeNVDAVolume": (_("Minimize NVDA volume "), SCRCAT_VOLUME_CONTROL, "hdr21-3"),
	# Translators: Input help mode message
	# for set NVDA volume to x percent commands
	"setNVDAVolumeTo10Percent": (_setNVDAVolumeToMsg % 10, SCRCAT_VOLUME_CONTROL, "hdr21-8"),
	"setNVDAVolumeTo20Percent": (_setNVDAVolumeToMsg % 20, SCRCAT_VOLUME_CONTROL, "hdr21-8"),
	"setNVDAVolumeTo30Percent": (_setNVDAVolumeToMsg % 30, SCRCAT_VOLUME_CONTROL, "hdr21-8"),
	"setNVDAVolumeTo40Percent": (_setNVDAVolumeToMsg % 40, SCRCAT_VOLUME_CONTROL, "hdr21-8"),
	"setNVDAVolumeTo50Percent": (_setNVDAVolumeToMsg % 50, SCRCAT_VOLUME_CONTROL, "hdr21-8"),
	"setNVDAVolumeTo60Percent": (_setNVDAVolumeToMsg % 60, SCRCAT_VOLUME_CONTROL, "hdr21-8"),
	"setNVDAVolumeTo70Percent": (_setNVDAVolumeToMsg % 70, SCRCAT_VOLUME_CONTROL, "hdr21-8"),
	"setNVDAVolumeTo80Percent": (_setNVDAVolumeToMsg % 80, SCRCAT_VOLUME_CONTROL, "hdr21-8"),
	"setNVDAVolumeTo90Percent": (_setNVDAVolumeToMsg % 90, SCRCAT_VOLUME_CONTROL, "hdr21-8"),
	# Translators: Input help mode message
	# for setting back to previous level the NVDA volume command.
	"setNVDAVolumeToPreviousLevel": (
		_("Set the NVDA volume to previous level"), SCRCAT_VOLUME_CONTROL, "hdr21-5"),

	# scripts for speakers volume
	# Translators: Input help mode message
	# for increase volume of speakers command.
	"increaseSpeakersVolume": (_("Increase volume of speakers"), SCRCAT_VOLUME_CONTROL, "hdr21-4"),
	# Translators: Input help mode message
	# for decrease volume of speakers command.
	"decreaseSpeakersVolume": (_("Decrease volume of speakers"), SCRCAT_VOLUME_CONTROL, "hdr21-4"),
	# Translators: Input help mode message
	# for maximize volume of speakers command.
	"maximizeSpeakersVolume": (_("Maximize volume of speakers"), SCRCAT_VOLUME_CONTROL, "hdr21-4"),
	# Translators: Input help mode message
	# for minimize volume of speakers command.
	"minimizeSpeakersVolume": (_("Minimize volume of speakers"), SCRCAT_VOLUME_CONTROL, "hdr21-4"),
	# Translators: Input help mode message
	# for set speaker volume to x percent commandsminimize volume of speakers command.
	"setSpeakersVolumeLevelTo10": (_setSpeakersVolumeToMsg % 10, SCRCAT_VOLUME_CONTROL, "hdr21-4"),
	"setSpeakersVolumeLevelTo20": (_setSpeakersVolumeToMsg % 20, SCRCAT_VOLUME_CONTROL, "hdr21-4"),
	"setSpeakersVolumeLevelTo30": (_setSpeakersVolumeToMsg % 30, SCRCAT_VOLUME_CONTROL, "hdr21-4"),
	"setSpeakersVolumeLevelTo40": (_setSpeakersVolumeToMsg % 40, SCRCAT_VOLUME_CONTROL, "hdr21-4"),
	"setSpeakersVolumeLevelTo50": (_setSpeakersVolumeToMsg % 50, SCRCAT_VOLUME_CONTROL, "hdr21-4"),
	"setSpeakersVolumeLevelTo60": (_setSpeakersVolumeToMsg % 60, SCRCAT_VOLUME_CONTROL, "hdr21-4"),
	"setSpeakersVolumeLevelTo70": (_setSpeakersVolumeToMsg % 70, SCRCAT_VOLUME_CONTROL, "hdr21-4"),
	"setSpeakersVolumeLevelTo80": (_setSpeakersVolumeToMsg % 80, SCRCAT_VOLUME_CONTROL, "hdr21-4"),
	"setSpeakersVolumeLevelTo90": (_setSpeakersVolumeToMsg % 90, SCRCAT_VOLUME_CONTROL, "hdr21-4"),
	# Translators: Input help mode message
	# for setting back to previous level the volume of speakers command.
	"setSpeakersVolumeLevelToPreviousLevel": (
		_("Set the main volume to previous level"), SCRCAT_VOLUME_CONTROL, "hdr21-8"),
	# scripts for sound split

	# Translators: Input help mode message
	# for setNVDAToRightAndFocusedApplicationToLeft script command
	"setNVDAToRightAndFocusedApplicationToLeft": (
		_("Hear NVDA to right and focused application to left"), SCRCAT_VOLUME_CONTROL, "hdr34"),
	# Translators: Input help mode message
	# for setNVDAToLeftAndFocusedApplicationToRight script command
	"setNVDAToLeftAndFocusedApplicationToRight": (
		_("Hear NVDA to left and focused application to right"), SCRCAT_VOLUME_CONTROL, "hdr34"),
	# Translators: Input help mode message
	# for centerNVDAAndFocusedApplication script command.
	"centerNVDAAndFocusedApplication": (
		_("Hear NVDA and focused application on center"), SCRCAT_VOLUME_CONTROL, "hdr34"),
	# Translators: Input help mode message
	# for setNVDAToRightAndAllApplicationsToLeft script command
	"setNVDAToRightAndAllApplicationsToLeft": (
		_("Hear NVDA to right and all audio applications to left"), SCRCAT_VOLUME_CONTROL, "hdr34"),
	# Translators: Input help mode message
	# for setNVDAToLeftAndAllApplicationsToRight script command
	"setNVDAToLeftAndAllApplicationsToRight": (
		_("Hear NVDA to left and all audio applications to right"), SCRCAT_VOLUME_CONTROL, "hdr34"),
	# Translators: Input help mode message
	# for centerNVDAAndAllApplications script command.
	"centerNVDAAndAllApplications": (
		_("Hear NVDA and all audio applications on center"), SCRCAT_VOLUME_CONTROL, "hdr34"),
	# Translators: Input help mode message
	# for centerFocusedApplication script command.
	"centerFocusedApplication": (
		_("Hear focused application on center"), SCRCAT_VOLUME_CONTROL, "hdr34"),
	# Translators: Input help mode message
	# for displayNVDAAndApplicationsAudioChannelsManagerDialog script command
	"displayNVDAAndApplicationsAudioManager": (
		_("Display NVDA 's audio sources manager"), SCRCAT_VOLUME_CONTROL, "hdr34"),
}
