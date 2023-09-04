# globalPlugins\NVDAExtensionGlobalPlugin\settings\addonConfig.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from configobj import ConfigObj
from configobj.validate import Validator, ValidateError
from io import StringIO
import config

addonHandler.initTranslation()

# addon config section
SCT_General = "General"
SCT_InstallFeatureOptions = "InstallFeatureOptions"
SCT_RedefinedKeyLabels = "RedefinedKeyLabels"
SCT_RedefinedKeyNames = "RedefinedKeyNames"
SCT_CategoriesAndSymbols = "Categories&Symbols"
SCT_MinuteTimer = "MinuteTimer"
SCT_Options = "Options"
SCT_AdvancedOptions = "Advanced options"
SCT_ShutdownComputer = "ShutdownComputer"
SCT_AudioDevicesForCycle = "AudioDevicesForCycle"

# general section items
ID_ConfigVersion = "ConfigVersion"
ID_AutoUpdate = "AutoUpdate"
ID_UpdateReleaseVersionsToDevVersions = "UpdateReleaseVersionsToDevVersions"
ID_LastChecked = "lastChecked"
ID_RemindUpdate = "RemindUpdate"

# InstallFeatureOption section  items
# functionality ids
FCT_SystrayIconsAndActiveWindowsList = "SystrayIconsAndActiveWindowsList"
FCT_ComplexSymbols = "ComplexSymbols"
FCT_FocusedApplicationInformations = "focusedApplicationInformations"
FCT_ExtendedVirtualBuffer = "ExtendedVirtualBuffer"
FCT_ClipboardCommandAnnouncement = "FakeClipboardAnnouncement"
FCT_CurrentFolderReport = "CurrentFolderReport"
FCT_OpenCurrentOrOldNVDALogFile = "OpenCurrentOrOldNVDALogFile"
FCT_SpeechHistory = "SpeechHistory"
FCT_KeyboardKeyRenaming = "KeyboardKeyRenaming"
FCT_CommandKeysSelectiveAnnouncement = "CommandKeysSelectiveAnnouncement"
FCT_MinuteTimer = "MinuteTimer"
FCT_RestartInDebugMode = "RestartInDebugMode"
FCT_ForegroundWindowObjectsList = "ForegroundWindowObjectsList"
FCT_VoiceProfileSwitching = "VoiceProfileSwitching"
FCT_KeyRemanence = "KeyRemanence"
FCT_VolumeControl = "VolumeControl"
FCT_SplitAudio = "SplitAudio"
FCT_Tools = "Tools"
FCT_DateAndTime = "DateAndTime"
FCT_TextAnalysis = "TextAnalysis"
FCT_TemporaryAudioDevice = "TemporaryAudioDevice"
FCT_ManageUserConfigurations = "manageUserConfigurations"
FCT_ExploreNVDA = "ExploreNVDA"
FCT_VariousOutSecureMode = "VariousOutSecureMode"
FCT_Various = "Various"
# option ids
ID_ReportNextWordOnDeletion = "ReportNextWordOnDeletion"
ID_NoDescriptionReportInRibbon = "NoDescriptionReportInRibbon"
ID_ReportFormatting = "ReportFormatting"  # to be deleted later
ID_AutomaticWindowMaximization = "AutomaticWindowMaximization"
ID_ReportTimeWithSeconds = "ReportTimeWithSeconds"
ID_SayPunctuationsOnWordCaretMovement = "SayPunctuationsOnWordCaretMovement"
ID_OnlyNVDAKeyInRemanence = "OnlyNVDAKeyInRemanence"
ID_RemanenceAtNVDAStart = "RemanenceAtNVDAStart"
ID_RemanenceForGmail = "RemanenceForGmail"
ID_MaxClipboardReportedCharacters = "MaximumClipboardReportedCharacters"

# constants for InstallFeatureOption section  items
C_DoNotInstall = 0
C_Install = 1
C_InstallWithoutGesture = 2


# MinuteTimer section items
ID_RingCount = "RingCount"
ID_DelayBetweenRings = "DelayBetweenRings"
ID_LastDuration = "LastDuration"
ID_LastAnnounce = "LastAnnounce"
ID_LastDelayBeforeEndDuration = "LastDelayBeforeEndDuration"

# options section items
ID_SpeechRecordWithNumber = "SpeechRecordWithNumber"
ID_SpeechRecordInAscendingOrder = "SpeechRecordInAscendingOrder"
ID_LoopInNavigationMode = "LoopInNavigationMode"

# advanced options  section items
ID_PlaySoundOnErrors = "PlaySoundOnErrors"
ID_RemanenceDelay = "RemanenceDelay"
ID_BeepAtRemanenceStart = "BeepAtRemanenceStart"
ID_BeepAtRemanenceEnd = "BeepAtRemanenceEnd"
ID_SetOnMainAndNVDAVolume = "SetOnMainAndNVDAVolume"
ID_MinMasterVolumeLevel = "MinMasterVolumeLevel"
ID_MasterVolumeLevel = "MasterVolumeLevel"
ID_MinNVDAVolumeLevel = "MinNVDAVolumeLevel"
ID_NVDAVolumeLevel = "NVDAVolumeLevel"
ID_VolumeChangeStepLevel = "volumeChangeStepLevel"
ID_ReportVolumeChange = "ReportVolumeChange"
ID_AppVolumeLevelAnnouncementInPercent = "AppVolumeLevelAnnouncementInPercent"  # deprecated
ID_IncreaseSpeakersVolumeIfNecessary = "IncreaseSpeakersVolumeIfNessary"
ID_DialogTitleWithAddonSummary = "DialogTitleWithAddonSummary"
ID_ConfirmAudioDeviceChange = "ConfirmAudioDeviceChange"
ID_ConfirmAudioDeviceChangeTimeOut = "ConfirmAudioDeviceChangeTimeOut"
ID_ReducedPathItemsNumber = "ReducedPathItemsNumber"
ID_ReversedPathWithLevel = "ReversedPathWithLevel"
ID_LimitKeyRepeats = "LimitKeyRepeats"
ID_KeyRepeatDelay = "KeyRepeatDelay"
ID_RecordCurrentSettingsForCurrentSelector = "RecordCurrentSettingsForCurrentSelector"
# for old configuration, must be deleted in the future
ID_DelayBetweenSameGesture = "DelayBetweenSameGesture"
ID_MaximumDelayBetweenSameScript = "MaximumDelayBetweenSameScript"
ID_MaximumOfLastUsedSymbols = "MaximumOfLastUsedSymbols"
ID_ByPassNoDescription = "ByPassNoDescription"
ID_EnableNumpadNavigationModeToggle = "EnableNumpadNavigationModeToggle"
ID_ActivateNumpadNavigationModeAtStart = "ActivateNumpadNavigationModeAtStart"
ID_ActivateNumpadStandardUseWithNumLock = "ActivateNumpadStandardUseWithNumLock"
ID_ReportNumlockStateAtStart = "ReportNumlockStateAtStart"
ID_ReportCapslockStateAtStart = "ReportCapslockStateAtStart"
ID_TypedWordSpeakingEnhancement = "TypedWordSpeakingEnhancement"
ID_TonalitiesVolumeLevel = "TonalitiesVolumeLevel"
ID_AllowNVDATonesVolumeAdjustment = "AllowNVDATonesVolumeAdjustment"
ID_AllowNVDASoundGainModification = "AllowNVDASoundGainModification"
ID_PlayToneOnAudioDevice = "playToneOnAudioDevice"
PSOE_NoVersion = 0
PSOE_SnapshotVersions = 1
PSOE_UntilNVDARestart = 2
PSOE_AllVersions = 3
# constant for volume level
MIN_VOLUME_LEVEL = 0
MAX_VOLUME_LEVEL = 100

# IDs for ShutdownComputer section
ID_ForceClose = "ForceClose"
ID_ShutdownTimeout = "ShutdownTimeout"
# Translators: default message to user when of minute timer ends.
_ItIsTime = _("It's time").encode("utf-8")
# default values for volume control section
C_MinMasterVolumeLevel = 10
C_MasterVolumeLevel = 50
C_MinNVDAVolumeLevel = 10
C_NVDAVolumeLevel = 50
C_VolumeChangeStepLevel = 5

# default values for complex symbols editing helper feature
C_MaximumOfLastUsedSymbols = 20
# default value for ConfirmAudioDeviceSwitchingTimeOut
c_ConfirmAudioDeviceSwitchingTimeOut = 10

# for reporting spelling errors
SCT_ReportingSpellingErrors = "ReportingSpellingErrors"
ID_ReportingBy = "ReportingBy"
RSE_None = "none"
RSE_Beep = "beep"
RSE_Sound = "sound"
RSE_Message = "Message"

reportingSpellingErrorsChoiceLabels = {
	# Translators: choice label to report spelling errors with a beep.
	RSE_Beep: _("Beep"),
	# Translators: choice label to report  spelling errors with a sound.
	RSE_Sound: _("Sound"),
	# Translators: choice label to report spelling errors with speech message.
	RSE_Message: _("Message"),
	# Translators: choice label to no reporting spelling errors
	RSE_None: _("nothing"),
}

_curAddon = addonHandler.getCodeAddon()
addonName = _curAddon.manifest["name"]


class BaseAddonConfiguration(ConfigObj):
	_version = ""

	""" Add-on configuration file. It contains metadata about add-on . """
	_GeneralConfSpec = """[{section}]
	{idConfigVersion} = string(default = " ")
		""".format(section=SCT_General, idConfigVersion=ID_ConfigVersion)

	configspec = ConfigObj(StringIO("""# addon Configuration File
	{0}""".format(_GeneralConfSpec, )
	), list_values=False, encoding="UTF-8")

	def __init__(self, input):
		""" Constructs an L{AddonConfiguration} instance from manifest string data
		@param input: data to read the addon configuration information
		@type input: a fie-like object.
		"""
		super(BaseAddonConfiguration, self).__init__(
			input,
			configspec=self.configspec,
			encoding='utf-8',
			default_encoding='utf-8')
		self.newlines = "\r\n"
		self._errors = []
		val = Validator()
		result = self.validate(val, copy=True, preserve_errors=True)
		if type(result) == dict:
			self._errors = self.getValidateErrorsText(result)
		else:
			self._errors = None

	def getValidateErrorsText(self, result):
		textList = []
		for name, section in result.items():
			if section is True:
				continue
			textList.append("section [%s]" % name)
			for key, value in section.items():
				if isinstance(value, ValidateError):
					textList.append(
						'key "{}": {}'.format(
							key, value))
		return "\n".join(textList)

	@property
	def errors(self):
		return self._errors


class AddonConfiguration25(BaseAddonConfiguration):
	_version = "2.5"
	_GeneralConfSpec = """[{section}]
	{idConfigVersion} = string(default = {version})
	{autoUpdate} = boolean(default=True)
	{updateReleaseToDev} = boolean(default=False)
	{lastChecked} = integer(default=0)
	{remindUpdate} = boolean(default=False)
	""".format(
		section=SCT_General,
		idConfigVersion=ID_ConfigVersion,
		version=_version,
		autoUpdate=ID_AutoUpdate,
		updateReleaseToDev=ID_UpdateReleaseVersionsToDevVersions,
		lastChecked=ID_LastChecked,
		remindUpdate=ID_RemindUpdate)

	_FeatureAuthorizationsConfSpec = """[{section}]
	{SystrayIconsAndActiveWindowsList} = integer(default={install})
	{complexSymbols} = integer(default= {installWithoutGesture})
	{clipboardCommandAnnouncement} = integer(default={install})
	{currentFolderReport} = integer(default={installWithoutGesture})
	{virtualBuffer} = integer(default={install})
	{focusedApplicationInformations}= integer(default={installWithoutGesture})
	{openNVDALog}  = integer(default={installWithoutGesture})
	{speechHistory}  = integer(default={installWithoutGesture})
	{keyboardKeyRenaming}  = integer(default={install})
	{commandKeysSelectiveAnnouncement}  = integer(default={install})
	{minuteTimer}  = integer(default={installWithoutGesture})
	{foregroundWindowObjectsList}  = integer(default={install}),
	{voiceProfileSwitching}  = integer(default={installWithoutGesture}),
	{keyRemanence}  = integer(default={DoNotInstall}),
	{restartInDebugMode}  = integer(default={DoNotInstall}),
	{volumeControl}  = integer(default={installWithoutGesture}),
	{tools}  = integer(default={DoNotInstall}),
	{dateAndTime}  = integer(default={installWithoutGesture}),
	""".format(
		section=SCT_InstallFeatureOptions,
		SystrayIconsAndActiveWindowsList=FCT_SystrayIconsAndActiveWindowsList,
		currentFolderReport=FCT_CurrentFolderReport,
		virtualBuffer=FCT_ExtendedVirtualBuffer,
		complexSymbols=FCT_ComplexSymbols,
		clipboardCommandAnnouncement=FCT_ClipboardCommandAnnouncement,
		focusedApplicationInformations=FCT_FocusedApplicationInformations,
		openNVDALog=FCT_OpenCurrentOrOldNVDALogFile,
		speechHistory=FCT_SpeechHistory,
		keyboardKeyRenaming=FCT_KeyboardKeyRenaming,
		commandKeysSelectiveAnnouncement=FCT_CommandKeysSelectiveAnnouncement,
		minuteTimer=FCT_MinuteTimer,
		foregroundWindowObjectsList=FCT_ForegroundWindowObjectsList,
		voiceProfileSwitching=FCT_VoiceProfileSwitching,
		keyRemanence=FCT_KeyRemanence,
		restartInDebugMode=FCT_RestartInDebugMode,
		install=C_Install,
		DoNotInstall=C_DoNotInstall,
		installWithoutGesture=C_InstallWithoutGesture,
		volumeControl=FCT_VolumeControl,
		tools=FCT_Tools,
		dateAndTime=FCT_DateAndTime)

	_OptionsConfSpec = """[{section}]
	{reportNextWordOnDeletion}  = boolean(default=True)
	{NoDescriptionReportInRibbon}  = boolean(default=True)
	{automaticWindowMaximization}  = boolean(default=True)
	{reportTimeWithSeconds}  = boolean(default=False),
	{speechRecordWithNumber}  = boolean(default=True),
	{speechRecordInascendingOrder}  = boolean(default=False),
	{loopInNavigationMode}  = boolean(default=False),
	""".format(
		section=SCT_Options,
		reportNextWordOnDeletion=ID_ReportNextWordOnDeletion,
		NoDescriptionReportInRibbon=ID_NoDescriptionReportInRibbon,
		automaticWindowMaximization=ID_AutomaticWindowMaximization,
		reportTimeWithSeconds=ID_ReportTimeWithSeconds,
		speechRecordWithNumber=ID_SpeechRecordWithNumber,
		speechRecordInascendingOrder=ID_SpeechRecordInAscendingOrder,
		loopInNavigationMode=ID_LoopInNavigationMode)

	_MinuteTimerConfSpec = """[{section}]
	{ringCount} = integer(default = 3)
	{delayBetweenRings} = integer(default = 1500)
	{lastDuration} = integer(default = 30)
	{lastAnnounce} = string(default = "{ItIsTime}")
	{lastDelayBeforeEndDuration} = integer(default = 5)
	""".format(
		section=SCT_MinuteTimer,
		ringCount=ID_RingCount,
		delayBetweenRings=ID_DelayBetweenRings,
		lastDuration=ID_LastDuration,
		lastAnnounce=ID_LastAnnounce,
		lastDelayBeforeEndDuration=ID_LastDelayBeforeEndDuration,
		ItIsTime=_ItIsTime)

	_AdvancedOptionsConfSpec = """[{section}]
	{playSoundOnErrors} = integer(default=1)
	{onlyNVDAKeyInRemanence}= boolean(default=False)
	{remanenceAtNVDAStart} = boolean(default=False)
	{remanenceDelay} = integer(default=2000)
	{beepAtRemanenceStart}  = boolean(default=True)
	{beepAtRemanenceEnd}  = boolean(default=True)
	{remanenceForGmail} = boolean(default=False)
	{setOnMainAndNVDAVolume}= boolean(default=True)
	{minMasterVolumeLevel} = integer(default={c_MinMasterVolumeLevel})
	{masterVolumeLevel} = integer(default={c_MasterVolumeLevel})
	{minNVDAVolumeLevel} = integer(default={c_MinNVDAVolumeLevel})
	{NVDAVolumeLevel} = integer(default={c_NVDAVolumeLevel})
	{volumeChangeStepLevel} = integer(default={defaultVolumeChangeStepLevel})
	{reportVolumeChange}= boolean(default=True)
	{dialogTitleWithAddonSummary}  = boolean(default=True)
	{maximumDelayBetweenSameScript} = integer(default=500)
	{maximumOfLastUsedSymbols} = integer(default={c_MaximumOfLastUsedSymbols} )
	{byPassNoDescription}  = boolean(default=True)
	{enableNumpadNavigationModeToggle}  = boolean(default=False)
	{activateNumpadNavigationModeAtStart}  = boolean(default=False)
	{activateNumpadStandardUseWithNumLock}  = boolean(default=False)
	""".format(
		section=SCT_AdvancedOptions,
		playSoundOnErrors=ID_PlaySoundOnErrors,
		onlyNVDAKeyInRemanence=ID_OnlyNVDAKeyInRemanence,
		remanenceAtNVDAStart=ID_RemanenceAtNVDAStart,
		remanenceDelay=ID_RemanenceDelay,
		beepAtRemanenceStart=ID_BeepAtRemanenceStart,
		beepAtRemanenceEnd=ID_BeepAtRemanenceEnd,
		remanenceForGmail=ID_RemanenceForGmail,
		setOnMainAndNVDAVolume=ID_SetOnMainAndNVDAVolume,
		minMasterVolumeLevel=ID_MinMasterVolumeLevel,
		masterVolumeLevel=ID_MasterVolumeLevel,
		minNVDAVolumeLevel=ID_MinNVDAVolumeLevel,
		NVDAVolumeLevel=ID_NVDAVolumeLevel,
		volumeChangeStepLevel=ID_VolumeChangeStepLevel,
		reportVolumeChange=ID_ReportVolumeChange,
		defaultVolumeChangeStepLevel=C_VolumeChangeStepLevel,
		dialogTitleWithAddonSummary=ID_DialogTitleWithAddonSummary,
		maximumDelayBetweenSameScript=ID_MaximumDelayBetweenSameScript,
		maximumOfLastUsedSymbols=ID_MaximumOfLastUsedSymbols,
		byPassNoDescription=ID_ByPassNoDescription,
		c_MinMasterVolumeLevel=C_MinMasterVolumeLevel,
		c_MasterVolumeLevel=C_MasterVolumeLevel,
		c_MinNVDAVolumeLevel=C_MinNVDAVolumeLevel,
		c_NVDAVolumeLevel=C_NVDAVolumeLevel,
		c_MaximumOfLastUsedSymbols=C_MaximumOfLastUsedSymbols,
		enableNumpadNavigationModeToggle=ID_EnableNumpadNavigationModeToggle,
		activateNumpadNavigationModeAtStart=ID_ActivateNumpadNavigationModeAtStart,
		activateNumpadStandardUseWithNumLock=ID_ActivateNumpadStandardUseWithNumLock)

	_ShutdownComputerConfSpec = """[{section}]
	{forceClose}  = boolean(default=True),
	{timeout} = integer(default = 1)
	""".format(
		section=SCT_ShutdownComputer,
		forceClose=ID_ForceClose,
		timeout=ID_ShutdownTimeout)

	#: The configuration specification
	configspec = ConfigObj(StringIO(
		"""# addon Configuration File
{general}\r\n{features}\r\n{options}\r\n{minuteTimer}\r\n{advancedOptions}\r\n{shutdown}
""".format(
			general=_GeneralConfSpec,
			features=_FeatureAuthorizationsConfSpec,
			options=_OptionsConfSpec,
			minuteTimer=_MinuteTimerConfSpec,
			advancedOptions=_AdvancedOptionsConfSpec,
			shutdown=_ShutdownComputerConfSpec)
	), list_values=False, encoding="UTF-8")


class AddonConfiguration26(BaseAddonConfiguration):
	_version = "2.6"
	_GeneralConfSpec = """[{section}]
	{idConfigVersion} = string(default = {version})
	{autoUpdate} = boolean(default=True)
	{updateReleaseToDev} = boolean(default=False)
	{lastChecked} = integer(default=0)
	{remindUpdate} = boolean(default=False)
	""".format(
		section=SCT_General,
		idConfigVersion=ID_ConfigVersion,
		version=_version,
		autoUpdate=ID_AutoUpdate,
		updateReleaseToDev=ID_UpdateReleaseVersionsToDevVersions,
		lastChecked=ID_LastChecked,
		remindUpdate=ID_RemindUpdate)

	_FeatureAuthorizationsConfSpec = """[{section}]
	{SystrayIconsAndActiveWindowsList} = integer(default={install})
	{complexSymbols} = integer(default= {installWithoutGesture})
	{clipboardCommandAnnouncement} = integer(default={install})
	{currentFolderReport} = integer(default={installWithoutGesture})
	{virtualBuffer} = integer(default={install})
	{focusedApplicationInformations}= integer(default={installWithoutGesture})
	{openNVDALog}  = integer(default={installWithoutGesture})
	{speechHistory}  = integer(default={installWithoutGesture})
	{keyboardKeyRenaming}  = integer(default={install})
	{commandKeysSelectiveAnnouncement}  = integer(default={install})
	{minuteTimer}  = integer(default={installWithoutGesture})
	{foregroundWindowObjectsList}  = integer(default={install}),
	{voiceProfileSwitching}  = integer(default={installWithoutGesture}),
	{keyRemanence}  = integer(default={DoNotInstall}),
	{restartInDebugMode}  = integer(default={DoNotInstall}),
	{volumeControl}  = integer(default={installWithoutGesture}),
	{tools}  = integer(default={DoNotInstall}),
	{dateAndTime}  = integer(default={installWithoutGesture}),
	""".format(
		section=SCT_InstallFeatureOptions,
		SystrayIconsAndActiveWindowsList=FCT_SystrayIconsAndActiveWindowsList,
		currentFolderReport=FCT_CurrentFolderReport,
		virtualBuffer=FCT_ExtendedVirtualBuffer,
		complexSymbols=FCT_ComplexSymbols,
		clipboardCommandAnnouncement=FCT_ClipboardCommandAnnouncement,
		focusedApplicationInformations=FCT_FocusedApplicationInformations,
		openNVDALog=FCT_OpenCurrentOrOldNVDALogFile,
		speechHistory=FCT_SpeechHistory,
		keyboardKeyRenaming=FCT_KeyboardKeyRenaming,
		commandKeysSelectiveAnnouncement=FCT_CommandKeysSelectiveAnnouncement,
		minuteTimer=FCT_MinuteTimer,
		foregroundWindowObjectsList=FCT_ForegroundWindowObjectsList,
		voiceProfileSwitching=FCT_VoiceProfileSwitching,
		keyRemanence=FCT_KeyRemanence,
		restartInDebugMode=FCT_RestartInDebugMode,
		install=C_Install,
		DoNotInstall=C_DoNotInstall,
		installWithoutGesture=C_InstallWithoutGesture,
		volumeControl=FCT_VolumeControl,
		tools=FCT_Tools,
		dateAndTime=FCT_DateAndTime)

	_OptionsConfSpec = """[{section}]
	{reportNextWordOnDeletion}  = boolean(default=True)
	{NoDescriptionReportInRibbon}  = boolean(default=True)
	{automaticWindowMaximization}  = boolean(default=True)
	{reportTimeWithSeconds}  = boolean(default=False),
	{speechRecordWithNumber}  = boolean(default=True),
	{speechRecordInascendingOrder}  = boolean(default=False),
	{loopInNavigationMode}  = boolean(default=False),
	""".format(
		section=SCT_Options,
		reportNextWordOnDeletion=ID_ReportNextWordOnDeletion,
		NoDescriptionReportInRibbon=ID_NoDescriptionReportInRibbon,
		automaticWindowMaximization=ID_AutomaticWindowMaximization,
		reportTimeWithSeconds=ID_ReportTimeWithSeconds,
		speechRecordWithNumber=ID_SpeechRecordWithNumber,
		speechRecordInascendingOrder=ID_SpeechRecordInAscendingOrder,
		loopInNavigationMode=ID_LoopInNavigationMode)

	_MinuteTimerConfSpec = """[{section}]
	{ringCount} = integer(default = 3)
	{delayBetweenRings} = integer(default = 1500)
	{lastDuration} = integer(default = 30)
	{lastAnnounce} = string(default = "{ItIsTime}")
	{lastDelayBeforeEndDuration} = integer(default = 5)
	""".format(
		section=SCT_MinuteTimer,
		ringCount=ID_RingCount,
		delayBetweenRings=ID_DelayBetweenRings,
		lastDuration=ID_LastDuration,
		lastAnnounce=ID_LastAnnounce,
		lastDelayBeforeEndDuration=ID_LastDelayBeforeEndDuration,
		ItIsTime=_ItIsTime)

	_AdvancedOptionsConfSpec = """[{section}]
	{playSoundOnErrors} = integer(default=1)
	{onlyNVDAKeyInRemanence}= boolean(default=False)
	{remanenceAtNVDAStart} = boolean(default=False)
	{remanenceDelay} = integer(default=2000)
	{beepAtRemanenceStart}  = boolean(default=True)
	{beepAtRemanenceEnd}  = boolean(default=True)
	{remanenceForGmail} = boolean(default=False)
	{setOnMainAndNVDAVolume}= boolean(default=True)
	{minMasterVolumeLevel} = integer(default={c_MinMasterVolumeLevel})
	{masterVolumeLevel} = integer(default={c_MasterVolumeLevel})
	{minNVDAVolumeLevel} = integer(default={c_MinNVDAVolumeLevel})
	{NVDAVolumeLevel} = integer(default={c_NVDAVolumeLevel})
	{volumeChangeStepLevel} = integer(default={defaultVolumeChangeStepLevel})
	{reportVolumeChange}= boolean(default=True)
	{appVolumeLevelAnnouncementInPercent}= boolean(default=True)
	{dialogTitleWithAddonSummary}  = boolean(default=True)
	{maximumDelayBetweenSameScript} = integer(default=500)
	{maximumOfLastUsedSymbols} = integer(default={c_MaximumOfLastUsedSymbols} )
	{byPassNoDescription}  = boolean(default=True)
	{enableNumpadNavigationModeToggle}  = boolean(default=False)
	{activateNumpadNavigationModeAtStart}  = boolean(default=False)
	{activateNumpadStandardUseWithNumLock}  = boolean(default=False)
	""".format(
		section=SCT_AdvancedOptions,
		playSoundOnErrors=ID_PlaySoundOnErrors,
		onlyNVDAKeyInRemanence=ID_OnlyNVDAKeyInRemanence,
		remanenceAtNVDAStart=ID_RemanenceAtNVDAStart,
		remanenceDelay=ID_RemanenceDelay,
		beepAtRemanenceStart=ID_BeepAtRemanenceStart,
		beepAtRemanenceEnd=ID_BeepAtRemanenceEnd,
		remanenceForGmail=ID_RemanenceForGmail,
		setOnMainAndNVDAVolume=ID_SetOnMainAndNVDAVolume,
		minMasterVolumeLevel=ID_MinMasterVolumeLevel,
		masterVolumeLevel=ID_MasterVolumeLevel,
		minNVDAVolumeLevel=ID_MinNVDAVolumeLevel,
		NVDAVolumeLevel=ID_NVDAVolumeLevel,
		volumeChangeStepLevel=ID_VolumeChangeStepLevel,
		reportVolumeChange=ID_ReportVolumeChange,
		defaultVolumeChangeStepLevel=C_VolumeChangeStepLevel,
		appVolumeLevelAnnouncementInPercent=ID_AppVolumeLevelAnnouncementInPercent,
		dialogTitleWithAddonSummary=ID_DialogTitleWithAddonSummary,
		maximumDelayBetweenSameScript=ID_MaximumDelayBetweenSameScript,
		maximumOfLastUsedSymbols=ID_MaximumOfLastUsedSymbols,
		byPassNoDescription=ID_ByPassNoDescription,
		c_MinMasterVolumeLevel=C_MinMasterVolumeLevel,
		c_MasterVolumeLevel=C_MasterVolumeLevel,
		c_MinNVDAVolumeLevel=C_MinNVDAVolumeLevel,
		c_NVDAVolumeLevel=C_NVDAVolumeLevel,
		c_MaximumOfLastUsedSymbols=C_MaximumOfLastUsedSymbols,
		enableNumpadNavigationModeToggle=ID_EnableNumpadNavigationModeToggle,
		activateNumpadNavigationModeAtStart=ID_ActivateNumpadNavigationModeAtStart,
		activateNumpadStandardUseWithNumLock=ID_ActivateNumpadStandardUseWithNumLock)

	_ShutdownComputerConfSpec = """[{section}]
	{forceClose}  = boolean(default=True),
	{timeout} = integer(default = 1)
""".format(
		section=SCT_ShutdownComputer,
		forceClose=ID_ForceClose,
		timeout=ID_ShutdownTimeout)

	#: The configuration specification
	configspec = ConfigObj(StringIO(
		"""# addon Configuration File
{general}\r\n{features}\r\n{options}\r\n{minuteTimer}\r\n{advancedOptions}\r\n{shutdown}
""".format(
			general=_GeneralConfSpec,
			features=_FeatureAuthorizationsConfSpec,
			options=_OptionsConfSpec,
			minuteTimer=_MinuteTimerConfSpec,
			advancedOptions=_AdvancedOptionsConfSpec,
			shutdown=_ShutdownComputerConfSpec)
	), list_values=False, encoding="UTF-8")


class AddonConfiguration27(BaseAddonConfiguration):
	_version = "2.7"
	_GeneralConfSpec = """[{section}]
	{idConfigVersion} = string(default = {version})
	{autoUpdate} = boolean(default=True)
	{updateReleaseToDev} = boolean(default=False)
	{lastChecked} = integer(default=0)
	{remindUpdate} = boolean(default=False)
	""".format(
		section=SCT_General,
		idConfigVersion=ID_ConfigVersion,
		version=_version,
		autoUpdate=ID_AutoUpdate,
		updateReleaseToDev=ID_UpdateReleaseVersionsToDevVersions,
		lastChecked=ID_LastChecked,
		remindUpdate=ID_RemindUpdate)

	_FeatureAuthorizationsConfSpec = """[{section}]
		{SystrayIconsAndActiveWindowsList} = integer(default={install})
		{complexSymbols} = integer(default= {installWithoutGesture})
		{clipboardCommandAnnouncement} = integer(default={install})
		{currentFolderReport} = integer(default={installWithoutGesture})
		{virtualBuffer} = integer(default={install})
		{focusedApplicationInformations}= integer(default={installWithoutGesture})
		{openNVDALog}  = integer(default={installWithoutGesture})
		{speechHistory}  = integer(default={installWithoutGesture})
		{keyboardKeyRenaming}  = integer(default={install})
		{commandKeysSelectiveAnnouncement}  = integer(default={install})
		{minuteTimer}  = integer(default={installWithoutGesture})
		{foregroundWindowObjectsList} = integer(default={install}),
		{voiceProfileSwitching} = integer(default={installWithoutGesture}),
		{keyRemanence} = integer(default={DoNotInstall}),
		{restartInDebugMode} = integer(default={DoNotInstall}),
		{volumeControl} = integer(default={installWithoutGesture}),
		{splitAudio} = integer(default={installWithoutGesture}),
		{tools} = integer(default={DoNotInstall}),
		{dateAndTime} = integer(default={installWithoutGesture}),
		{textAnalysis} = integer(default={installWithoutGesture}),
		{temporaryAudioDevice} = integer(default={install}),
	""".format(
		section=SCT_InstallFeatureOptions,
		SystrayIconsAndActiveWindowsList=FCT_SystrayIconsAndActiveWindowsList,
		currentFolderReport=FCT_CurrentFolderReport,
		virtualBuffer=FCT_ExtendedVirtualBuffer,
		complexSymbols=FCT_ComplexSymbols,
		clipboardCommandAnnouncement=FCT_ClipboardCommandAnnouncement,
		focusedApplicationInformations=FCT_FocusedApplicationInformations,
		openNVDALog=FCT_OpenCurrentOrOldNVDALogFile,
		speechHistory=FCT_SpeechHistory,
		keyboardKeyRenaming=FCT_KeyboardKeyRenaming,
		commandKeysSelectiveAnnouncement=FCT_CommandKeysSelectiveAnnouncement,
		minuteTimer=FCT_MinuteTimer,
		foregroundWindowObjectsList=FCT_ForegroundWindowObjectsList,
		voiceProfileSwitching=FCT_VoiceProfileSwitching,
		keyRemanence=FCT_KeyRemanence,
		restartInDebugMode=FCT_RestartInDebugMode,
		install=C_Install,
		DoNotInstall=C_DoNotInstall,
		installWithoutGesture=C_InstallWithoutGesture,
		volumeControl=FCT_VolumeControl,
		splitAudio=FCT_SplitAudio,
		tools=FCT_Tools,
		dateAndTime=FCT_DateAndTime,
		textAnalysis=FCT_TextAnalysis,
		temporaryAudioDevice=FCT_TemporaryAudioDevice,
	)

	_OptionsConfSpec = """[{section}]
		{reportNextWordOnDeletion}  = boolean(default=True)
		{NoDescriptionReportInRibbon}  = boolean(default=True)
		{automaticWindowMaximization}  = boolean(default=True)
		{reportTimeWithSeconds}  = boolean(default=False),
		{speechRecordWithNumber}  = boolean(default=True),
		{speechRecordInascendingOrder}  = boolean(default=False),
		{loopInNavigationMode}  = boolean(default=False),
	""".format(
		section=SCT_Options,
		reportNextWordOnDeletion=ID_ReportNextWordOnDeletion,
		NoDescriptionReportInRibbon=ID_NoDescriptionReportInRibbon,
		automaticWindowMaximization=ID_AutomaticWindowMaximization,
		reportTimeWithSeconds=ID_ReportTimeWithSeconds,
		speechRecordWithNumber=ID_SpeechRecordWithNumber,
		speechRecordInascendingOrder=ID_SpeechRecordInAscendingOrder,
		loopInNavigationMode=ID_LoopInNavigationMode)

	_MinuteTimerConfSpec = """[{section}]
		{ringCount} = integer(default = 3)
		{delayBetweenRings} = integer(default = 1500)
		{lastDuration} = integer(default = 30)
		{lastAnnounce} = string(default = "{ItIsTime}")
		{lastDelayBeforeEndDuration} = integer(default = 5)
	""".format(
		section=SCT_MinuteTimer,
		ringCount=ID_RingCount,
		delayBetweenRings=ID_DelayBetweenRings,
		lastDuration=ID_LastDuration,
		lastAnnounce=ID_LastAnnounce,
		lastDelayBeforeEndDuration=ID_LastDelayBeforeEndDuration,
		ItIsTime=_ItIsTime)

	_AdvancedOptionsConfSpec = """[{section}]
	{playSoundOnErrors} = integer(default=1)
	{onlyNVDAKeyInRemanence}= boolean(default=False)
	{remanenceAtNVDAStart} = boolean(default=False)
	{remanenceDelay} = integer(default=2000)
	{beepAtRemanenceStart}  = boolean(default=True)
	{beepAtRemanenceEnd}  = boolean(default=True)
	{remanenceForGmail} = boolean(default=False)
	{setOnMainAndNVDAVolume}= boolean(default=True)
	{minMasterVolumeLevel} = integer(default={c_MinMasterVolumeLevel})
	{masterVolumeLevel} = integer(default={c_MasterVolumeLevel})
	{minNVDAVolumeLevel} = integer(default={c_MinNVDAVolumeLevel})
	{NVDAVolumeLevel} = integer(default={c_NVDAVolumeLevel})
	{volumeChangeStepLevel} = integer(default={defaultVolumeChangeStepLevel})
	{reportVolumeChange}= boolean(default=True)
	{appVolumeLevelAnnouncementInPercent}= boolean(default=True)
	{dialogTitleWithAddonSummary}  = boolean(default=True)
	{maximumDelayBetweenSameScript} = integer(default=500)
	{maximumOfLastUsedSymbols} = integer(default={c_MaximumOfLastUsedSymbols} )
	{byPassNoDescription}  = boolean(default=True)
	{enableNumpadNavigationModeToggle}  = boolean(default=False)
	{activateNumpadNavigationModeAtStart}  = boolean(default=False)
	{activateNumpadStandardUseWithNumLock}  = boolean(default=False)
	{confirmAudioDeviceChange}  = boolean(default=True)
	{confirmAudioDeviceChangeTimeOut} = integer(default=10)
	""".format(
		section=SCT_AdvancedOptions,
		playSoundOnErrors=ID_PlaySoundOnErrors,
		onlyNVDAKeyInRemanence=ID_OnlyNVDAKeyInRemanence,
		remanenceAtNVDAStart=ID_RemanenceAtNVDAStart,
		remanenceDelay=ID_RemanenceDelay,
		beepAtRemanenceStart=ID_BeepAtRemanenceStart,
		beepAtRemanenceEnd=ID_BeepAtRemanenceEnd,
		remanenceForGmail=ID_RemanenceForGmail,
		setOnMainAndNVDAVolume=ID_SetOnMainAndNVDAVolume,
		minMasterVolumeLevel=ID_MinMasterVolumeLevel,
		masterVolumeLevel=ID_MasterVolumeLevel,
		minNVDAVolumeLevel=ID_MinNVDAVolumeLevel,
		NVDAVolumeLevel=ID_NVDAVolumeLevel,
		volumeChangeStepLevel=ID_VolumeChangeStepLevel,
		reportVolumeChange=ID_ReportVolumeChange,
		defaultVolumeChangeStepLevel=C_VolumeChangeStepLevel,
		appVolumeLevelAnnouncementInPercent=ID_AppVolumeLevelAnnouncementInPercent,
		dialogTitleWithAddonSummary=ID_DialogTitleWithAddonSummary,
		maximumDelayBetweenSameScript=ID_MaximumDelayBetweenSameScript,
		maximumOfLastUsedSymbols=ID_MaximumOfLastUsedSymbols,
		byPassNoDescription=ID_ByPassNoDescription,
		c_MinMasterVolumeLevel=C_MinMasterVolumeLevel,
		c_MasterVolumeLevel=C_MasterVolumeLevel,
		c_MinNVDAVolumeLevel=C_MinNVDAVolumeLevel,
		c_NVDAVolumeLevel=C_NVDAVolumeLevel,
		c_MaximumOfLastUsedSymbols=C_MaximumOfLastUsedSymbols,
		enableNumpadNavigationModeToggle=ID_EnableNumpadNavigationModeToggle,
		activateNumpadNavigationModeAtStart=ID_ActivateNumpadNavigationModeAtStart,
		activateNumpadStandardUseWithNumLock=ID_ActivateNumpadStandardUseWithNumLock,
		confirmAudioDeviceChange=ID_ConfirmAudioDeviceChange,
		confirmAudioDeviceChangeTimeOut=ID_ConfirmAudioDeviceChangeTimeOut
	)

	_ShutdownComputerConfSpec = """[{section}]
	{forceClose}  = boolean(default=True),
	{timeout} = integer(default = 1)
""".format(
		section=SCT_ShutdownComputer,
		forceClose=ID_ForceClose,
		timeout=ID_ShutdownTimeout)

	#: The configuration specification
	configspec = ConfigObj(StringIO(
		"""# addon Configuration File
{general}\r\n{features}\r\n{options}\r\n{minuteTimer}\r\n{advancedOptions}\r\n{shutdown}
""".format(
			general=_GeneralConfSpec,
			features=_FeatureAuthorizationsConfSpec,
			options=_OptionsConfSpec,
			minuteTimer=_MinuteTimerConfSpec,
			advancedOptions=_AdvancedOptionsConfSpec,
			shutdown=_ShutdownComputerConfSpec)
	), list_values=False, encoding="UTF-8")


_reportNumlockStateAtStartDefault = True if config.conf['keyboard']['keyboardLayout'] == "desktop" else False


class AddonConfiguration28(BaseAddonConfiguration):
	_version = "2.8"
	_GeneralConfSpec = """[{section}]
	{idConfigVersion} = string(default = {version})
	{autoUpdate} = boolean(default=True)
	{updateReleaseToDev} = boolean(default=False)
	{lastChecked} = integer(default=0)
	{remindUpdate} = boolean(default=False)
	""".format(
		section=SCT_General,
		idConfigVersion=ID_ConfigVersion,
		version=_version,
		autoUpdate=ID_AutoUpdate,
		updateReleaseToDev=ID_UpdateReleaseVersionsToDevVersions,
		lastChecked=ID_LastChecked,
		remindUpdate=ID_RemindUpdate)

	_FeatureAuthorizationsConfSpec = """[{section}]
		{SystrayIconsAndActiveWindowsList} = integer(default={install})
		{complexSymbols} = integer(default= {installWithoutGesture})
		{clipboardCommandAnnouncement} = integer(default={install})
		{currentFolderReport} = integer(default={installWithoutGesture})
		{virtualBuffer} = integer(default={install})
		{focusedApplicationInformations}= integer(default={installWithoutGesture})
		{openNVDALog}  = integer(default={installWithoutGesture})
		{speechHistory}  = integer(default={installWithoutGesture})
		{keyboardKeyRenaming}  = integer(default={install})
		{commandKeysSelectiveAnnouncement}  = integer(default={install})
		{minuteTimer}  = integer(default={installWithoutGesture})
		{foregroundWindowObjectsList} = integer(default={install}),
		{voiceProfileSwitching} = integer(default={installWithoutGesture}),
		{keyRemanence} = integer(default={DoNotInstall}),
		{restartInDebugMode} = integer(default={DoNotInstall}),
		{volumeControl} = integer(default={installWithoutGesture}),
		{splitAudio} = integer(default={installWithoutGesture}),
		{tools} = integer(default={DoNotInstall}),
		{dateAndTime} = integer(default={installWithoutGesture}),
		{textAnalysis} = integer(default={installWithoutGesture}),
		{temporaryAudioDevice} = integer(default={install}),
	""".format(
		section=SCT_InstallFeatureOptions,
		SystrayIconsAndActiveWindowsList=FCT_SystrayIconsAndActiveWindowsList,
		currentFolderReport=FCT_CurrentFolderReport,
		virtualBuffer=FCT_ExtendedVirtualBuffer,
		complexSymbols=FCT_ComplexSymbols,
		clipboardCommandAnnouncement=FCT_ClipboardCommandAnnouncement,
		focusedApplicationInformations=FCT_FocusedApplicationInformations,
		openNVDALog=FCT_OpenCurrentOrOldNVDALogFile,
		speechHistory=FCT_SpeechHistory,
		keyboardKeyRenaming=FCT_KeyboardKeyRenaming,
		commandKeysSelectiveAnnouncement=FCT_CommandKeysSelectiveAnnouncement,
		minuteTimer=FCT_MinuteTimer,
		foregroundWindowObjectsList=FCT_ForegroundWindowObjectsList,
		voiceProfileSwitching=FCT_VoiceProfileSwitching,
		keyRemanence=FCT_KeyRemanence,
		restartInDebugMode=FCT_RestartInDebugMode,
		install=C_Install,
		DoNotInstall=C_DoNotInstall,
		installWithoutGesture=C_InstallWithoutGesture,
		volumeControl=FCT_VolumeControl,
		splitAudio=FCT_SplitAudio,
		tools=FCT_Tools,
		dateAndTime=FCT_DateAndTime,
		textAnalysis=FCT_TextAnalysis,
		temporaryAudioDevice=FCT_TemporaryAudioDevice,
	)

	_OptionsConfSpec = """[{section}]
	{reportNextWordOnDeletion}  = boolean(default=True)
	{NoDescriptionReportInRibbon}  = boolean(default=True)
	{automaticWindowMaximization}  = boolean(default=True)
	{reportTimeWithSeconds}  = boolean(default=False),
	{speechRecordWithNumber}  = boolean(default=True),
	{speechRecordInascendingOrder}  = boolean(default=False),
	{loopInNavigationMode}  = boolean(default=False),
	""".format(
		section=SCT_Options,
		reportNextWordOnDeletion=ID_ReportNextWordOnDeletion,
		NoDescriptionReportInRibbon=ID_NoDescriptionReportInRibbon,
		automaticWindowMaximization=ID_AutomaticWindowMaximization,
		reportTimeWithSeconds=ID_ReportTimeWithSeconds,
		speechRecordWithNumber=ID_SpeechRecordWithNumber,
		speechRecordInascendingOrder=ID_SpeechRecordInAscendingOrder,
		loopInNavigationMode=ID_LoopInNavigationMode)

	_MinuteTimerConfSpec = """[{section}]
	{ringCount} = integer(default = 3)
	{delayBetweenRings} = integer(default = 1500)
	{lastDuration} = integer(default = 30)
	{lastAnnounce} = string(default = "{ItIsTime}")
	{lastDelayBeforeEndDuration} = integer(default = 5)
	""".format(
		section=SCT_MinuteTimer,
		ringCount=ID_RingCount,
		delayBetweenRings=ID_DelayBetweenRings,
		lastDuration=ID_LastDuration,
		lastAnnounce=ID_LastAnnounce,
		lastDelayBeforeEndDuration=ID_LastDelayBeforeEndDuration,
		ItIsTime=_ItIsTime)

	_AdvancedOptionsConfSpec = """[{section}]
	{playSoundOnErrors} = integer(default=1)
	{onlyNVDAKeyInRemanence}= boolean(default=False)
	{remanenceAtNVDAStart} = boolean(default=False)
	{remanenceDelay} = integer(default=2000)
	{beepAtRemanenceStart}  = boolean(default=True)
	{beepAtRemanenceEnd}  = boolean(default=True)
	{remanenceForGmail} = boolean(default=False)
	{setOnMainAndNVDAVolume}= boolean(default=True)
	{minMasterVolumeLevel} = integer(default={c_MinMasterVolumeLevel})
	{masterVolumeLevel} = integer(default={c_MasterVolumeLevel})
	{minNVDAVolumeLevel} = integer(default={c_MinNVDAVolumeLevel})
	{NVDAVolumeLevel} = integer(default={c_NVDAVolumeLevel})
	{volumeChangeStepLevel} = integer(default={defaultVolumeChangeStepLevel})
	{reportVolumeChange}= boolean(default=True)
	{increaseSpeakersVolumeIfNecessary}= boolean(default=False)
	{dialogTitleWithAddonSummary}  = boolean(default=True)
	{maximumDelayBetweenSameScript} = integer(default=500)
	{maximumOfLastUsedSymbols} = integer(default={c_MaximumOfLastUsedSymbols} )
	{byPassNoDescription}  = boolean(default=True)
	{enableNumpadNavigationModeToggle}  = boolean(default=False)
	{activateNumpadNavigationModeAtStart}  = boolean(default=False)
	{activateNumpadStandardUseWithNumLock}  = boolean(default=False)
	{confirmAudioDeviceChange}  = boolean(default=True)
	{confirmAudioDeviceChangeTimeOut} = integer(default=10)
	{reportNumlockStateAtStart} = boolean(default={reportNumlockStateAtStartDefault})
	{maxClipboardReportedCharacters} = integer(default=1024)


	""".format(
		section=SCT_AdvancedOptions,
		playSoundOnErrors=ID_PlaySoundOnErrors,
		onlyNVDAKeyInRemanence=ID_OnlyNVDAKeyInRemanence,
		remanenceAtNVDAStart=ID_RemanenceAtNVDAStart,
		remanenceDelay=ID_RemanenceDelay,
		beepAtRemanenceStart=ID_BeepAtRemanenceStart,
		beepAtRemanenceEnd=ID_BeepAtRemanenceEnd,
		remanenceForGmail=ID_RemanenceForGmail,
		setOnMainAndNVDAVolume=ID_SetOnMainAndNVDAVolume,
		minMasterVolumeLevel=ID_MinMasterVolumeLevel,
		masterVolumeLevel=ID_MasterVolumeLevel,
		minNVDAVolumeLevel=ID_MinNVDAVolumeLevel,
		NVDAVolumeLevel=ID_NVDAVolumeLevel,
		volumeChangeStepLevel=ID_VolumeChangeStepLevel,
		reportVolumeChange=ID_ReportVolumeChange,
		defaultVolumeChangeStepLevel=C_VolumeChangeStepLevel,
		increaseSpeakersVolumeIfNecessary=ID_IncreaseSpeakersVolumeIfNecessary,
		dialogTitleWithAddonSummary=ID_DialogTitleWithAddonSummary,
		maximumDelayBetweenSameScript=ID_MaximumDelayBetweenSameScript,
		maximumOfLastUsedSymbols=ID_MaximumOfLastUsedSymbols,
		byPassNoDescription=ID_ByPassNoDescription,
		c_MinMasterVolumeLevel=C_MinMasterVolumeLevel,
		c_MasterVolumeLevel=C_MasterVolumeLevel,
		c_MinNVDAVolumeLevel=C_MinNVDAVolumeLevel,
		c_NVDAVolumeLevel=C_NVDAVolumeLevel,
		c_MaximumOfLastUsedSymbols=C_MaximumOfLastUsedSymbols,
		enableNumpadNavigationModeToggle=ID_EnableNumpadNavigationModeToggle,
		activateNumpadNavigationModeAtStart=ID_ActivateNumpadNavigationModeAtStart,
		activateNumpadStandardUseWithNumLock=ID_ActivateNumpadStandardUseWithNumLock,
		confirmAudioDeviceChange=ID_ConfirmAudioDeviceChange,
		confirmAudioDeviceChangeTimeOut=ID_ConfirmAudioDeviceChangeTimeOut,
		reportNumlockStateAtStart=ID_ReportNumlockStateAtStart,
		reportNumlockStateAtStartDefault=_reportNumlockStateAtStartDefault,
		maxClipboardReportedCharacters=ID_MaxClipboardReportedCharacters,
	)

	_ShutdownComputerConfSpec = """[{section}]
	{forceClose}  = boolean(default=True),
	{timeout} = integer(default = 1)
""".format(
		section=SCT_ShutdownComputer,
		forceClose=ID_ForceClose,
		timeout=ID_ShutdownTimeout)

# reportingSpellingErrors configuration specification
	_reportingSpellingErrorsConfspec = """[{section}]
	{reportingBy} = string(default = "sound")
	""".format(
		section=SCT_ReportingSpellingErrors,
		reportingBy=ID_ReportingBy
	)

	#: The configuration specification
	configspec = ConfigObj(StringIO(
		"""# addon Configuration File
{general}\r\n{features}\r\n{options}\r\n{minuteTimer}\r\n{advancedOptions}\r\n{shutdown}\r\n{reportingSpellingErrors}
""".format(
			general=_GeneralConfSpec,
			features=_FeatureAuthorizationsConfSpec,
			options=_OptionsConfSpec,
			minuteTimer=_MinuteTimerConfSpec,
			advancedOptions=_AdvancedOptionsConfSpec,
			shutdown=_ShutdownComputerConfSpec,
			reportingSpellingErrors=_reportingSpellingErrorsConfspec,
		),
	), list_values=False, encoding="UTF-8")


class AddonConfiguration29(BaseAddonConfiguration):
	_version = "2.9"
	_GeneralConfSpec = """[{section}]
	{idConfigVersion} = string(default = {version})
	{autoUpdate} = boolean(default=True)
	{updateReleaseToDev} = boolean(default=False)
	{lastChecked} = integer(default=0)
	{remindUpdate} = boolean(default=False)
	""".format(
		section=SCT_General,
		idConfigVersion=ID_ConfigVersion,
		version=_version,
		autoUpdate=ID_AutoUpdate,
		updateReleaseToDev=ID_UpdateReleaseVersionsToDevVersions,
		lastChecked=ID_LastChecked,
		remindUpdate=ID_RemindUpdate)

	_FeatureAuthorizationsConfSpec = """[{section}]
		{SystrayIconsAndActiveWindowsList} = integer(default={install})
		{complexSymbols} = integer(default= {installWithoutGesture})
		{clipboardCommandAnnouncement} = integer(default={install})
		{currentFolderReport} = integer(default={installWithoutGesture})
		{virtualBuffer} = integer(default={install})
		{focusedApplicationInformations}= integer(default={installWithoutGesture})
		{openNVDALog}  = integer(default={installWithoutGesture})
		{speechHistory}  = integer(default={installWithoutGesture})
		{keyboardKeyRenaming}  = integer(default={install})
		{commandKeysSelectiveAnnouncement}  = integer(default={install})
		{minuteTimer}  = integer(default={installWithoutGesture})
		{foregroundWindowObjectsList} = integer(default={install}),
		{voiceProfileSwitching} = integer(default={installWithoutGesture}),
		{keyRemanence} = integer(default={DoNotInstall}),
		{restartInDebugMode} = integer(default={DoNotInstall}),
		{volumeControl} = integer(default={installWithoutGesture}),
		{splitAudio} = integer(default={installWithoutGesture}),
		{tools} = integer(default={DoNotInstall}),
		{dateAndTime} = integer(default={installWithoutGesture}),
		{textAnalysis} = integer(default={installWithoutGesture}),
		{temporaryAudioDevice} = integer(default={install}),
	""".format(
		section=SCT_InstallFeatureOptions,
		SystrayIconsAndActiveWindowsList=FCT_SystrayIconsAndActiveWindowsList,
		currentFolderReport=FCT_CurrentFolderReport,
		virtualBuffer=FCT_ExtendedVirtualBuffer,
		complexSymbols=FCT_ComplexSymbols,
		clipboardCommandAnnouncement=FCT_ClipboardCommandAnnouncement,
		focusedApplicationInformations=FCT_FocusedApplicationInformations,
		openNVDALog=FCT_OpenCurrentOrOldNVDALogFile,
		speechHistory=FCT_SpeechHistory,
		keyboardKeyRenaming=FCT_KeyboardKeyRenaming,
		commandKeysSelectiveAnnouncement=FCT_CommandKeysSelectiveAnnouncement,
		minuteTimer=FCT_MinuteTimer,
		foregroundWindowObjectsList=FCT_ForegroundWindowObjectsList,
		voiceProfileSwitching=FCT_VoiceProfileSwitching,
		keyRemanence=FCT_KeyRemanence,
		restartInDebugMode=FCT_RestartInDebugMode,
		install=C_Install,
		DoNotInstall=C_DoNotInstall,
		installWithoutGesture=C_InstallWithoutGesture,
		volumeControl=FCT_VolumeControl,
		splitAudio=FCT_SplitAudio,
		tools=FCT_Tools,
		dateAndTime=FCT_DateAndTime,
		textAnalysis=FCT_TextAnalysis,
		temporaryAudioDevice=FCT_TemporaryAudioDevice,
	)

	_OptionsConfSpec = """[{section}]
	{reportNextWordOnDeletion}  = boolean(default=True)
	{NoDescriptionReportInRibbon}  = boolean(default=True)
	{automaticWindowMaximization}  = boolean(default=True)
	{reportTimeWithSeconds}  = boolean(default=False),
	{speechRecordWithNumber}  = boolean(default=True),
	{speechRecordInascendingOrder}  = boolean(default=False),
	{loopInNavigationMode}  = boolean(default=False),
	""".format(
		section=SCT_Options,
		reportNextWordOnDeletion=ID_ReportNextWordOnDeletion,
		NoDescriptionReportInRibbon=ID_NoDescriptionReportInRibbon,
		automaticWindowMaximization=ID_AutomaticWindowMaximization,
		reportTimeWithSeconds=ID_ReportTimeWithSeconds,
		speechRecordWithNumber=ID_SpeechRecordWithNumber,
		speechRecordInascendingOrder=ID_SpeechRecordInAscendingOrder,
		loopInNavigationMode=ID_LoopInNavigationMode)

	_MinuteTimerConfSpec = """[{section}]
	{ringCount} = integer(default = 3)
	{delayBetweenRings} = integer(default = 1500)
	{lastDuration} = integer(default = 30)
	{lastAnnounce} = string(default = "{ItIsTime}")
	{lastDelayBeforeEndDuration} = integer(default = 5)
	""".format(
		section=SCT_MinuteTimer,
		ringCount=ID_RingCount,
		delayBetweenRings=ID_DelayBetweenRings,
		lastDuration=ID_LastDuration,
		lastAnnounce=ID_LastAnnounce,
		lastDelayBeforeEndDuration=ID_LastDelayBeforeEndDuration,
		ItIsTime=_ItIsTime)

	_AdvancedOptionsConfSpec = """[{section}]
	{playSoundOnErrors} = integer(default=1)
	{onlyNVDAKeyInRemanence}= boolean(default=False)
	{remanenceAtNVDAStart} = boolean(default=False)
	{remanenceDelay} = integer(default=2000)
	{beepAtRemanenceStart}  = boolean(default=True)
	{beepAtRemanenceEnd}  = boolean(default=True)
	{remanenceForGmail} = boolean(default=False)
	{setOnMainAndNVDAVolume}= boolean(default=True)
	{minMasterVolumeLevel} = integer(default={c_MinMasterVolumeLevel})
	{masterVolumeLevel} = integer(default={c_MasterVolumeLevel})
	{minNVDAVolumeLevel} = integer(default={c_MinNVDAVolumeLevel})
	{NVDAVolumeLevel} = integer(default={c_NVDAVolumeLevel})
	{volumeChangeStepLevel} = integer(default={defaultVolumeChangeStepLevel})
	{reportVolumeChange}= boolean(default=True)
	{increaseSpeakersVolumeIfNecessary}= boolean(default=False)
	{dialogTitleWithAddonSummary}  = boolean(default=True)
	{maximumDelayBetweenSameScript} = integer(default=500)
	{maximumOfLastUsedSymbols} = integer(default={c_MaximumOfLastUsedSymbols} )
	{byPassNoDescription}  = boolean(default=True)
	{enableNumpadNavigationModeToggle}  = boolean(default=False)
	{activateNumpadNavigationModeAtStart}  = boolean(default=False)
	{activateNumpadStandardUseWithNumLock}  = boolean(default=False)
	{confirmAudioDeviceChange}  = boolean(default=True)
	{confirmAudioDeviceChangeTimeOut} = integer(default=10)
	{reportNumlockStateAtStart} = boolean(default={reportNumlockStateAtStartDefault})
	{maxClipboardReportedCharacters} = integer(default=1024)
	{ReducedPathItemsNumber} =integer(default=4)
	{reversedPathWithLevel}  = boolean(default=True)
{limitKeyRepeats} = boolean(default=False)
{keyRepeatDelay} =integer(default=100)
	""".format(
		section=SCT_AdvancedOptions,
		playSoundOnErrors=ID_PlaySoundOnErrors,
		onlyNVDAKeyInRemanence=ID_OnlyNVDAKeyInRemanence,
		remanenceAtNVDAStart=ID_RemanenceAtNVDAStart,
		remanenceDelay=ID_RemanenceDelay,
		beepAtRemanenceStart=ID_BeepAtRemanenceStart,
		beepAtRemanenceEnd=ID_BeepAtRemanenceEnd,
		remanenceForGmail=ID_RemanenceForGmail,
		setOnMainAndNVDAVolume=ID_SetOnMainAndNVDAVolume,
		minMasterVolumeLevel=ID_MinMasterVolumeLevel,
		masterVolumeLevel=ID_MasterVolumeLevel,
		minNVDAVolumeLevel=ID_MinNVDAVolumeLevel,
		NVDAVolumeLevel=ID_NVDAVolumeLevel,
		volumeChangeStepLevel=ID_VolumeChangeStepLevel,
		reportVolumeChange=ID_ReportVolumeChange,
		defaultVolumeChangeStepLevel=C_VolumeChangeStepLevel,
		increaseSpeakersVolumeIfNecessary=ID_IncreaseSpeakersVolumeIfNecessary,
		dialogTitleWithAddonSummary=ID_DialogTitleWithAddonSummary,
		maximumDelayBetweenSameScript=ID_MaximumDelayBetweenSameScript,
		maximumOfLastUsedSymbols=ID_MaximumOfLastUsedSymbols,
		byPassNoDescription=ID_ByPassNoDescription,
		c_MinMasterVolumeLevel=C_MinMasterVolumeLevel,
		c_MasterVolumeLevel=C_MasterVolumeLevel,
		c_MinNVDAVolumeLevel=C_MinNVDAVolumeLevel,
		c_NVDAVolumeLevel=C_NVDAVolumeLevel,
		c_MaximumOfLastUsedSymbols=C_MaximumOfLastUsedSymbols,
		enableNumpadNavigationModeToggle=ID_EnableNumpadNavigationModeToggle,
		activateNumpadNavigationModeAtStart=ID_ActivateNumpadNavigationModeAtStart,
		activateNumpadStandardUseWithNumLock=ID_ActivateNumpadStandardUseWithNumLock,
		confirmAudioDeviceChange=ID_ConfirmAudioDeviceChange,
		confirmAudioDeviceChangeTimeOut=ID_ConfirmAudioDeviceChangeTimeOut,
		reportNumlockStateAtStart=ID_ReportNumlockStateAtStart,
		reportNumlockStateAtStartDefault=_reportNumlockStateAtStartDefault,
		maxClipboardReportedCharacters=ID_MaxClipboardReportedCharacters,
		ReducedPathItemsNumber=ID_ReducedPathItemsNumber,
		reversedPathWithLevel=ID_ReversedPathWithLevel,
		limitKeyRepeats=ID_LimitKeyRepeats,
		keyRepeatDelay=ID_KeyRepeatDelay,
	)

	_ShutdownComputerConfSpec = """[{section}]
	{forceClose}  = boolean(default=True),
	{timeout} = integer(default = 1)
""".format(
		section=SCT_ShutdownComputer,
		forceClose=ID_ForceClose,
		timeout=ID_ShutdownTimeout)

# reportingSpellingErrors configuration specification
	_reportingSpellingErrorsConfspec = """[{section}]
	{reportingBy} = string(default = "sound")
	""".format(
		section=SCT_ReportingSpellingErrors,
		reportingBy=ID_ReportingBy
	)

	#: The configuration specification
	configspec = ConfigObj(StringIO(
		"""# addon Configuration File
{general}\r\n{features}\r\n{options}\r\n{minuteTimer}\r\n{advancedOptions}\r\n{shutdown}\r\n{reportingSpellingErrors}
""".format(
			general=_GeneralConfSpec,
			features=_FeatureAuthorizationsConfSpec,
			options=_OptionsConfSpec,
			minuteTimer=_MinuteTimerConfSpec,
			advancedOptions=_AdvancedOptionsConfSpec,
			shutdown=_ShutdownComputerConfSpec,
			reportingSpellingErrors=_reportingSpellingErrorsConfspec,
		),
	), list_values=False, encoding="UTF-8")


class AddonConfiguration30(BaseAddonConfiguration):
	_version = "3.0"
	_GeneralConfSpec = """[{section}]
	{idConfigVersion} = string(default = {version})
	{autoUpdate} = boolean(default=True)
	{updateReleaseToDev} = boolean(default=False)
	{lastChecked} = integer(default=0)
	{remindUpdate} = boolean(default=False)
	""".format(
		section=SCT_General,
		idConfigVersion=ID_ConfigVersion,
		version=_version,
		autoUpdate=ID_AutoUpdate,
		updateReleaseToDev=ID_UpdateReleaseVersionsToDevVersions,
		lastChecked=ID_LastChecked,
		remindUpdate=ID_RemindUpdate)

	_FeatureAuthorizationsConfSpec = """[{section}]
		{SystrayIconsAndActiveWindowsList} = integer(default={install})
		{complexSymbols} = integer(default= {installWithoutGesture})
		{clipboardCommandAnnouncement} = integer(default={install})
		{currentFolderReport} = integer(default={installWithoutGesture})
		{virtualBuffer} = integer(default={install})
		{focusedApplicationInformations}= integer(default={installWithoutGesture})
		{openNVDALog}  = integer(default={installWithoutGesture})
		{speechHistory}  = integer(default={installWithoutGesture})
		{keyboardKeyRenaming}  = integer(default={install})
		{commandKeysSelectiveAnnouncement}  = integer(default={install})
		{minuteTimer}  = integer(default={installWithoutGesture})
		{foregroundWindowObjectsList} = integer(default={install}),
		{voiceProfileSwitching} = integer(default={installWithoutGesture}),
		{keyRemanence} = integer(default={DoNotInstall}),
		{restartInDebugMode} = integer(default={DoNotInstall}),
		{volumeControl} = integer(default={installWithoutGesture}),
		{splitAudio} = integer(default={installWithoutGesture}),
		{tools} = integer(default={DoNotInstall}),
		{dateAndTime} = integer(default={installWithoutGesture}),
		{textAnalysis} = integer(default={installWithoutGesture}),
		{temporaryAudioDevice} = integer(default={install}),
	""".format(
		section=SCT_InstallFeatureOptions,
		SystrayIconsAndActiveWindowsList=FCT_SystrayIconsAndActiveWindowsList,
		currentFolderReport=FCT_CurrentFolderReport,
		virtualBuffer=FCT_ExtendedVirtualBuffer,
		complexSymbols=FCT_ComplexSymbols,
		clipboardCommandAnnouncement=FCT_ClipboardCommandAnnouncement,
		focusedApplicationInformations=FCT_FocusedApplicationInformations,
		openNVDALog=FCT_OpenCurrentOrOldNVDALogFile,
		speechHistory=FCT_SpeechHistory,
		keyboardKeyRenaming=FCT_KeyboardKeyRenaming,
		commandKeysSelectiveAnnouncement=FCT_CommandKeysSelectiveAnnouncement,
		minuteTimer=FCT_MinuteTimer,
		foregroundWindowObjectsList=FCT_ForegroundWindowObjectsList,
		voiceProfileSwitching=FCT_VoiceProfileSwitching,
		keyRemanence=FCT_KeyRemanence,
		restartInDebugMode=FCT_RestartInDebugMode,
		install=C_Install,
		DoNotInstall=C_DoNotInstall,
		installWithoutGesture=C_InstallWithoutGesture,
		volumeControl=FCT_VolumeControl,
		splitAudio=FCT_SplitAudio,
		tools=FCT_Tools,
		dateAndTime=FCT_DateAndTime,
		textAnalysis=FCT_TextAnalysis,
		temporaryAudioDevice=FCT_TemporaryAudioDevice,
	)

	_OptionsConfSpec = """[{section}]
	{reportNextWordOnDeletion}  = boolean(default=True)
	{NoDescriptionReportInRibbon}  = boolean(default=True)
	{automaticWindowMaximization}  = boolean(default=True)
	{reportTimeWithSeconds}  = boolean(default=False),
	{speechRecordWithNumber}  = boolean(default=True),
	{speechRecordInascendingOrder}  = boolean(default=False),
	{loopInNavigationMode}  = boolean(default=False),
	""".format(
		section=SCT_Options,
		reportNextWordOnDeletion=ID_ReportNextWordOnDeletion,
		NoDescriptionReportInRibbon=ID_NoDescriptionReportInRibbon,
		automaticWindowMaximization=ID_AutomaticWindowMaximization,
		reportTimeWithSeconds=ID_ReportTimeWithSeconds,
		speechRecordWithNumber=ID_SpeechRecordWithNumber,
		speechRecordInascendingOrder=ID_SpeechRecordInAscendingOrder,
		loopInNavigationMode=ID_LoopInNavigationMode)

	_MinuteTimerConfSpec = """[{section}]
	{ringCount} = integer(default = 3)
	{delayBetweenRings} = integer(default = 1500)
	{lastDuration} = integer(default = 30)
	{lastAnnounce} = string(default = "{ItIsTime}")
	{lastDelayBeforeEndDuration} = integer(default = 5)
	""".format(
		section=SCT_MinuteTimer,
		ringCount=ID_RingCount,
		delayBetweenRings=ID_DelayBetweenRings,
		lastDuration=ID_LastDuration,
		lastAnnounce=ID_LastAnnounce,
		lastDelayBeforeEndDuration=ID_LastDelayBeforeEndDuration,
		ItIsTime=_ItIsTime)

	_AdvancedOptionsConfSpec = """[{section}]
	{playSoundOnErrors} = integer(default=1)
	{onlyNVDAKeyInRemanence}= boolean(default=False)
	{remanenceAtNVDAStart} = boolean(default=False)
	{remanenceDelay} = integer(default=2000)
	{beepAtRemanenceStart}  = boolean(default=True)
	{beepAtRemanenceEnd}  = boolean(default=True)
	{remanenceForGmail} = boolean(default=False)
	{setOnMainAndNVDAVolume}= boolean(default=True)
	{minMasterVolumeLevel} = integer(default={c_MinMasterVolumeLevel})
	{masterVolumeLevel} = integer(default={c_MasterVolumeLevel})
	{minNVDAVolumeLevel} = integer(default={c_MinNVDAVolumeLevel})
	{NVDAVolumeLevel} = integer(default={c_NVDAVolumeLevel})
	{volumeChangeStepLevel} = integer(default={defaultVolumeChangeStepLevel})
	{reportVolumeChange}= boolean(default=True)
	{increaseSpeakersVolumeIfNecessary}= boolean(default=False)
	{dialogTitleWithAddonSummary}  = boolean(default=True)
	{maximumDelayBetweenSameScript} = integer(default=500)
	{maximumOfLastUsedSymbols} = integer(default={c_MaximumOfLastUsedSymbols} )
	{byPassNoDescription}  = boolean(default=True)
	{enableNumpadNavigationModeToggle}  = boolean(default=False)
	{activateNumpadNavigationModeAtStart}  = boolean(default=False)
	{activateNumpadStandardUseWithNumLock}  = boolean(default=False)
	{confirmAudioDeviceChange}  = boolean(default=True)
	{confirmAudioDeviceChangeTimeOut} = integer(default=10)
	{reportNumlockStateAtStart} = boolean(default={reportNumlockStateAtStartDefault})
	{reportCapslockStateAtStart} = boolean(default=True)
	{maxClipboardReportedCharacters} = integer(default=1024)
	{ReducedPathItemsNumber} =integer(default=4)
	{reversedPathWithLevel}  = boolean(default=True)
	{limitKeyRepeats} = boolean(default=False)
	{keyRepeatDelay} =integer(default=100)
	{recordCurrentSettingsForCurrentSelector} = boolean(default=False)
	{typedWordSpeakingEnhancement} = boolean(default=True)
	{tonalitiesVolumeLevel} = integer(default=50)
	{allowNVDATonesVolumeAdjustment} = boolean(default=True)
	{allowNVDASoundGainModification} = boolean(default=True)
	""".format(
		section=SCT_AdvancedOptions,
		playSoundOnErrors=ID_PlaySoundOnErrors,
		onlyNVDAKeyInRemanence=ID_OnlyNVDAKeyInRemanence,
		remanenceAtNVDAStart=ID_RemanenceAtNVDAStart,
		remanenceDelay=ID_RemanenceDelay,
		beepAtRemanenceStart=ID_BeepAtRemanenceStart,
		beepAtRemanenceEnd=ID_BeepAtRemanenceEnd,
		remanenceForGmail=ID_RemanenceForGmail,
		setOnMainAndNVDAVolume=ID_SetOnMainAndNVDAVolume,
		minMasterVolumeLevel=ID_MinMasterVolumeLevel,
		masterVolumeLevel=ID_MasterVolumeLevel,
		minNVDAVolumeLevel=ID_MinNVDAVolumeLevel,
		NVDAVolumeLevel=ID_NVDAVolumeLevel,
		volumeChangeStepLevel=ID_VolumeChangeStepLevel,
		reportVolumeChange=ID_ReportVolumeChange,
		defaultVolumeChangeStepLevel=C_VolumeChangeStepLevel,
		increaseSpeakersVolumeIfNecessary=ID_IncreaseSpeakersVolumeIfNecessary,
		dialogTitleWithAddonSummary=ID_DialogTitleWithAddonSummary,
		maximumDelayBetweenSameScript=ID_MaximumDelayBetweenSameScript,
		maximumOfLastUsedSymbols=ID_MaximumOfLastUsedSymbols,
		byPassNoDescription=ID_ByPassNoDescription,
		c_MinMasterVolumeLevel=C_MinMasterVolumeLevel,
		c_MasterVolumeLevel=C_MasterVolumeLevel,
		c_MinNVDAVolumeLevel=C_MinNVDAVolumeLevel,
		c_NVDAVolumeLevel=C_NVDAVolumeLevel,
		c_MaximumOfLastUsedSymbols=C_MaximumOfLastUsedSymbols,
		enableNumpadNavigationModeToggle=ID_EnableNumpadNavigationModeToggle,
		activateNumpadNavigationModeAtStart=ID_ActivateNumpadNavigationModeAtStart,
		activateNumpadStandardUseWithNumLock=ID_ActivateNumpadStandardUseWithNumLock,
		confirmAudioDeviceChange=ID_ConfirmAudioDeviceChange,
		confirmAudioDeviceChangeTimeOut=ID_ConfirmAudioDeviceChangeTimeOut,
		reportNumlockStateAtStart=ID_ReportNumlockStateAtStart,
		reportCapslockStateAtStart=ID_ReportCapslockStateAtStart,
		reportNumlockStateAtStartDefault=_reportNumlockStateAtStartDefault,
		maxClipboardReportedCharacters=ID_MaxClipboardReportedCharacters,
		ReducedPathItemsNumber=ID_ReducedPathItemsNumber,
		reversedPathWithLevel=ID_ReversedPathWithLevel,
		limitKeyRepeats=ID_LimitKeyRepeats,
		keyRepeatDelay=ID_KeyRepeatDelay,
		recordCurrentSettingsForCurrentSelector=ID_RecordCurrentSettingsForCurrentSelector,
		typedWordSpeakingEnhancement=ID_TypedWordSpeakingEnhancement,
		tonalitiesVolumeLevel=ID_TonalitiesVolumeLevel,
		allowNVDATonesVolumeAdjustment=ID_AllowNVDATonesVolumeAdjustment,
		allowNVDASoundGainModification=ID_AllowNVDASoundGainModification,
	)

	_ShutdownComputerConfSpec = """[{section}]
	{forceClose}  = boolean(default=True),
	{timeout} = integer(default = 1)
""".format(
		section=SCT_ShutdownComputer,
		forceClose=ID_ForceClose,
		timeout=ID_ShutdownTimeout)

# reportingSpellingErrors configuration specification
	_reportingSpellingErrorsConfspec = """[{section}]
	{reportingBy} = string(default = "sound")
	""".format(
		section=SCT_ReportingSpellingErrors,
		reportingBy=ID_ReportingBy
	)

	#: The configuration specification
	configspec = ConfigObj(StringIO(
		"""# addon Configuration File
{general}\r\n{features}\r\n{options}\r\n{minuteTimer}\r\n{advancedOptions}\r\n{shutdown}\r\n{reportingSpellingErrors}
""".format(
			general=_GeneralConfSpec,
			features=_FeatureAuthorizationsConfSpec,
			options=_OptionsConfSpec,
			minuteTimer=_MinuteTimerConfSpec,
			advancedOptions=_AdvancedOptionsConfSpec,
			shutdown=_ShutdownComputerConfSpec,
			reportingSpellingErrors=_reportingSpellingErrorsConfspec,
		),
	), list_values=False, encoding="UTF-8")


class AddonConfiguration31(BaseAddonConfiguration):
	_version = "3.1"
	_GeneralConfSpec = """[{section}]
	{idConfigVersion} = string(default = {version})
	{autoUpdate} = boolean(default=True)
	{updateReleaseToDev} = boolean(default=False)
	{lastChecked} = integer(default=0)
	{remindUpdate} = boolean(default=False)
	""".format(
		section=SCT_General,
		idConfigVersion=ID_ConfigVersion,
		version=_version,
		autoUpdate=ID_AutoUpdate,
		updateReleaseToDev=ID_UpdateReleaseVersionsToDevVersions,
		lastChecked=ID_LastChecked,
		remindUpdate=ID_RemindUpdate)

	_FeatureAuthorizationsConfSpec = """[{section}]
		{SystrayIconsAndActiveWindowsList} = integer(default={install})
		{complexSymbols} = integer(default= {installWithoutGesture})
		{clipboardCommandAnnouncement} = integer(default={install})
		{currentFolderReport} = integer(default={installWithoutGesture})
		{virtualBuffer} = integer(default={install})
		{focusedApplicationInformations}= integer(default={installWithoutGesture})
		{openNVDALog}  = integer(default={installWithoutGesture})
		{speechHistory}  = integer(default={installWithoutGesture})
		{keyboardKeyRenaming}  = integer(default={install})
		{commandKeysSelectiveAnnouncement}  = integer(default={install})
		{minuteTimer}  = integer(default={installWithoutGesture})
		{foregroundWindowObjectsList} = integer(default={install}),
		{voiceProfileSwitching} = integer(default={installWithoutGesture}),
		{keyRemanence} = integer(default={DoNotInstall}),
		{restartInDebugMode} = integer(default={DoNotInstall}),
		{volumeControl} = integer(default={installWithoutGesture}),
		{splitAudio} = integer(default={installWithoutGesture}),
		{tools} = integer(default={DoNotInstall}),
		{dateAndTime} = integer(default={installWithoutGesture}),
		{textAnalysis} = integer(default={installWithoutGesture}),
		{temporaryAudioDevice} = integer(default={install}),
	""".format(
		section=SCT_InstallFeatureOptions,
		SystrayIconsAndActiveWindowsList=FCT_SystrayIconsAndActiveWindowsList,
		currentFolderReport=FCT_CurrentFolderReport,
		virtualBuffer=FCT_ExtendedVirtualBuffer,
		complexSymbols=FCT_ComplexSymbols,
		clipboardCommandAnnouncement=FCT_ClipboardCommandAnnouncement,
		focusedApplicationInformations=FCT_FocusedApplicationInformations,
		openNVDALog=FCT_OpenCurrentOrOldNVDALogFile,
		speechHistory=FCT_SpeechHistory,
		keyboardKeyRenaming=FCT_KeyboardKeyRenaming,
		commandKeysSelectiveAnnouncement=FCT_CommandKeysSelectiveAnnouncement,
		minuteTimer=FCT_MinuteTimer,
		foregroundWindowObjectsList=FCT_ForegroundWindowObjectsList,
		voiceProfileSwitching=FCT_VoiceProfileSwitching,
		keyRemanence=FCT_KeyRemanence,
		restartInDebugMode=FCT_RestartInDebugMode,
		install=C_Install,
		DoNotInstall=C_DoNotInstall,
		installWithoutGesture=C_InstallWithoutGesture,
		volumeControl=FCT_VolumeControl,
		splitAudio=FCT_SplitAudio,
		tools=FCT_Tools,
		dateAndTime=FCT_DateAndTime,
		textAnalysis=FCT_TextAnalysis,
		temporaryAudioDevice=FCT_TemporaryAudioDevice,
	)

	_OptionsConfSpec = """[{section}]
	{reportNextWordOnDeletion}  = boolean(default=True)
	{NoDescriptionReportInRibbon}  = boolean(default=True)
	{automaticWindowMaximization}  = boolean(default=True)
	{reportTimeWithSeconds}  = boolean(default=False),
	{speechRecordWithNumber}  = boolean(default=True),
	{speechRecordInascendingOrder}  = boolean(default=False),
	{loopInNavigationMode}  = boolean(default=False),
	""".format(
		section=SCT_Options,
		reportNextWordOnDeletion=ID_ReportNextWordOnDeletion,
		NoDescriptionReportInRibbon=ID_NoDescriptionReportInRibbon,
		automaticWindowMaximization=ID_AutomaticWindowMaximization,
		reportTimeWithSeconds=ID_ReportTimeWithSeconds,
		speechRecordWithNumber=ID_SpeechRecordWithNumber,
		speechRecordInascendingOrder=ID_SpeechRecordInAscendingOrder,
		loopInNavigationMode=ID_LoopInNavigationMode)

	_MinuteTimerConfSpec = """[{section}]
	{ringCount} = integer(default = 3)
	{delayBetweenRings} = integer(default = 1500)
	{lastDuration} = integer(default = 30)
	{lastAnnounce} = string(default = "{ItIsTime}")
	{lastDelayBeforeEndDuration} = integer(default = 5)
	""".format(
		section=SCT_MinuteTimer,
		ringCount=ID_RingCount,
		delayBetweenRings=ID_DelayBetweenRings,
		lastDuration=ID_LastDuration,
		lastAnnounce=ID_LastAnnounce,
		lastDelayBeforeEndDuration=ID_LastDelayBeforeEndDuration,
		ItIsTime=_ItIsTime)

	_AdvancedOptionsConfSpec = """[{section}]
	{playSoundOnErrors} = integer(default=1)
	{onlyNVDAKeyInRemanence}= boolean(default=False)
	{remanenceAtNVDAStart} = boolean(default=False)
	{remanenceDelay} = integer(default=2000)
	{beepAtRemanenceStart}  = boolean(default=True)
	{beepAtRemanenceEnd}  = boolean(default=True)
	{remanenceForGmail} = boolean(default=False)
	{setOnMainAndNVDAVolume}= boolean(default=True)
	{minMasterVolumeLevel} = integer(default={c_MinMasterVolumeLevel})
	{masterVolumeLevel} = integer(default={c_MasterVolumeLevel})
	{minNVDAVolumeLevel} = integer(default={c_MinNVDAVolumeLevel})
	{NVDAVolumeLevel} = integer(default={c_NVDAVolumeLevel})
	{volumeChangeStepLevel} = integer(default={defaultVolumeChangeStepLevel})
	{reportVolumeChange}= boolean(default=True)
	{increaseSpeakersVolumeIfNecessary}= boolean(default=False)
	{dialogTitleWithAddonSummary}  = boolean(default=True)
	{maximumDelayBetweenSameScript} = integer(default=500)
	{maximumOfLastUsedSymbols} = integer(default={c_MaximumOfLastUsedSymbols} )
	{byPassNoDescription}  = boolean(default=True)
	{enableNumpadNavigationModeToggle}  = boolean(default=False)
	{activateNumpadNavigationModeAtStart}  = boolean(default=False)
	{activateNumpadStandardUseWithNumLock}  = boolean(default=False)
	{confirmAudioDeviceChange}  = boolean(default=True)
	{confirmAudioDeviceChangeTimeOut} = integer(default=10)
	{reportNumlockStateAtStart} = boolean(default={reportNumlockStateAtStartDefault})
	{reportCapslockStateAtStart} = boolean(default=True)
	{maxClipboardReportedCharacters} = integer(default=1024)
	{ReducedPathItemsNumber} =integer(default=4)
	{reversedPathWithLevel}  = boolean(default=True)
	{limitKeyRepeats} = boolean(default=False)
	{keyRepeatDelay} =integer(default=100)
	{recordCurrentSettingsForCurrentSelector} = boolean(default=False)
	{typedWordSpeakingEnhancement} = boolean(default=True)
	{tonalitiesVolumeLevel} = integer(default=50)
	{allowNVDATonesVolumeAdjustment} = boolean(default=True)
	{allowNVDASoundGainModification} = boolean(default=True)
	{playToneOnAudioDevice} = boolean(default=True)
	""".format(
		section=SCT_AdvancedOptions,
		playSoundOnErrors=ID_PlaySoundOnErrors,
		onlyNVDAKeyInRemanence=ID_OnlyNVDAKeyInRemanence,
		remanenceAtNVDAStart=ID_RemanenceAtNVDAStart,
		remanenceDelay=ID_RemanenceDelay,
		beepAtRemanenceStart=ID_BeepAtRemanenceStart,
		beepAtRemanenceEnd=ID_BeepAtRemanenceEnd,
		remanenceForGmail=ID_RemanenceForGmail,
		setOnMainAndNVDAVolume=ID_SetOnMainAndNVDAVolume,
		minMasterVolumeLevel=ID_MinMasterVolumeLevel,
		masterVolumeLevel=ID_MasterVolumeLevel,
		minNVDAVolumeLevel=ID_MinNVDAVolumeLevel,
		NVDAVolumeLevel=ID_NVDAVolumeLevel,
		volumeChangeStepLevel=ID_VolumeChangeStepLevel,
		reportVolumeChange=ID_ReportVolumeChange,
		defaultVolumeChangeStepLevel=C_VolumeChangeStepLevel,
		increaseSpeakersVolumeIfNecessary=ID_IncreaseSpeakersVolumeIfNecessary,
		dialogTitleWithAddonSummary=ID_DialogTitleWithAddonSummary,
		maximumDelayBetweenSameScript=ID_MaximumDelayBetweenSameScript,
		maximumOfLastUsedSymbols=ID_MaximumOfLastUsedSymbols,
		byPassNoDescription=ID_ByPassNoDescription,
		c_MinMasterVolumeLevel=C_MinMasterVolumeLevel,
		c_MasterVolumeLevel=C_MasterVolumeLevel,
		c_MinNVDAVolumeLevel=C_MinNVDAVolumeLevel,
		c_NVDAVolumeLevel=C_NVDAVolumeLevel,
		c_MaximumOfLastUsedSymbols=C_MaximumOfLastUsedSymbols,
		enableNumpadNavigationModeToggle=ID_EnableNumpadNavigationModeToggle,
		activateNumpadNavigationModeAtStart=ID_ActivateNumpadNavigationModeAtStart,
		activateNumpadStandardUseWithNumLock=ID_ActivateNumpadStandardUseWithNumLock,
		confirmAudioDeviceChange=ID_ConfirmAudioDeviceChange,
		confirmAudioDeviceChangeTimeOut=ID_ConfirmAudioDeviceChangeTimeOut,
		reportNumlockStateAtStart=ID_ReportNumlockStateAtStart,
		reportCapslockStateAtStart=ID_ReportCapslockStateAtStart,
		reportNumlockStateAtStartDefault=_reportNumlockStateAtStartDefault,
		maxClipboardReportedCharacters=ID_MaxClipboardReportedCharacters,
		ReducedPathItemsNumber=ID_ReducedPathItemsNumber,
		reversedPathWithLevel=ID_ReversedPathWithLevel,
		limitKeyRepeats=ID_LimitKeyRepeats,
		keyRepeatDelay=ID_KeyRepeatDelay,
		recordCurrentSettingsForCurrentSelector=ID_RecordCurrentSettingsForCurrentSelector,
		typedWordSpeakingEnhancement=ID_TypedWordSpeakingEnhancement,
		tonalitiesVolumeLevel=ID_TonalitiesVolumeLevel,
		allowNVDATonesVolumeAdjustment=ID_AllowNVDATonesVolumeAdjustment,
		allowNVDASoundGainModification=ID_AllowNVDASoundGainModification,
		playToneOnAudioDevice=ID_PlayToneOnAudioDevice,
	)

	_ShutdownComputerConfSpec = """[{section}]
	{forceClose}  = boolean(default=True),
	{timeout} = integer(default = 1)
""".format(
		section=SCT_ShutdownComputer,
		forceClose=ID_ForceClose,
		timeout=ID_ShutdownTimeout)

# reportingSpellingErrors configuration specification
	_reportingSpellingErrorsConfspec = """[{section}]
	{reportingBy} = string(default = "sound")
	""".format(
		section=SCT_ReportingSpellingErrors,
		reportingBy=ID_ReportingBy
	)

	#: The configuration specification
	configspec = ConfigObj(StringIO(
		"""# addon Configuration File
{general}\r\n{features}\r\n{options}\r\n{minuteTimer}\r\n{advancedOptions}\r\n{shutdown}\r\n{reportingSpellingErrors}
""".format(
			general=_GeneralConfSpec,
			features=_FeatureAuthorizationsConfSpec,
			options=_OptionsConfSpec,
			minuteTimer=_MinuteTimerConfSpec,
			advancedOptions=_AdvancedOptionsConfSpec,
			shutdown=_ShutdownComputerConfSpec,
			reportingSpellingErrors=_reportingSpellingErrorsConfspec,
		),
	), list_values=False, encoding="UTF-8")
