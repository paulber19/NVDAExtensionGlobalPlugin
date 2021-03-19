# globalPlugins\NVDAExtensionGlobalPlugin\settings\addonConfig.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2020 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from configobj import ConfigObj
# ConfigObj 5.1.0 and later integrates validate module.
try:
	from configobj.validate import Validator
except ImportError:
	from validate import Validator
from ..utils.py3Compatibility import importStringIO

StringIO = importStringIO()
addonHandler.initTranslation()
# NVDA config sections for addon
SCT_CommandKeysAnnouncement = "CommandKeysAnnouncement"
SCT_LastUsedSymbols = "LastUsedSymbols"

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

# general section items
ID_ConfigVersion = "ConfigVersion"
ID_AutoUpdate = "AutoUpdate"
ID_UpdateReleaseVersionsToDevVersions = "UpdateReleaseVersionsToDevVersions"
ID_LastChecked = "lastChecked"
ID_RemindUpdate = "RemindUpdate"
# InstallFeatureOption section  items
ID_ActiveWindowsListReport = "ActiveWindowsListReport"  # to be deleted later
ID_SystrayIconsList = "SystrayIconsList"  # to be deleted later
ID_SystrayIconsAndActiveWindowsList = "SystrayIconsAndActiveWindowsList"
ID_ComplexSymbols = "ComplexSymbols"
ID_CurrentFolderReport = "CurrentFolderReport"
ID_ExtendedVirtualBuffer = "ExtendedVirtualBuffer"
ID_ClipboardCommandAnnouncement = "FakeClipboardAnnouncement"
ID_FocusedApplicationInformations = "focusedApplicationInformations"
ID_CurrentVoiceProfilReport = "CurrentVoiceProfilReport"  # to be deleted later
ID_AppProductNameAndVersionReport = "AppProductNameAndVersionReport"  # to be deleted later  # noqa:E501
ID_OpenCurrentOrOldNVDALogFile = "OpenCurrentOrOldNVDALogFile"
ID_ReportNextWordOnDeletion = "ReportNextWordOnDeletion"
ID_NoDescriptionReportInRibbon = "NoDescriptionReportInRibbon"
ID_SpeechHistory = "SpeechHistory"
ID_ReportFormatting = "ReportFormatting"  # to be deleted later
ID_KeyboardKeyRenaming = "KeyboardKeyRenaming"
ID_CommandKeysSelectiveAnnouncement = "CommandKeysSelectiveAnnouncement"
ID_AutomaticWindowMaximization = "AutomaticWindowMaximization"
ID_ReportTimeWithSeconds = "ReportTimeWithSeconds"
ID_MinuteTimer = "MinuteTimer"
ID_ForegroundWindowObjectsList = "ForegroundWindowObjectsList"
ID_SayPunctuationsOnWordCaretMovement = "SayPunctuationsOnWordCaretMovement"
ID_VoiceProfileSwitching = "VoiceProfileSwitching"
ID_KeyRemanence = "KeyRemanence"
ID_OnlyNVDAKeyInRemanence = "OnlyNVDAKeyInRemanence"
ID_RemanenceAtNVDAStart = "RemanenceAtNVDAStart"
ID_RemanenceForGmail = "RemanenceForGmail"
ID_RestartInDebugMode = "RestartInDebugMode"
ID_VolumeControl = "VolumeControl"
ID_Tools = "Tools"
ID_DateAndTime = "DateAndTime"
ID_ExploreNVDA = "ExploreNVDA"
# constants for InstallFeatureOption section  items
C_DoNotInstall = 0
C_Install = 1
C_InstallWithoutGesture = 2

# for commandKeysAnnouncement section
ID_SpeakCommandKeysMode = "SpeakCommandKeysMode"
ID_DoNotSpeakCommandKeysMode = "DoNotSpeakCommandKeysMode"

# MinuteTimer section items
ID_RingCount = "RingCount"
ID_DelayBetweenRings = "DelayBetweenRings"
ID_LastDuration = "LastDuration"
ID_LastAnnounce = "LastAnnounce"
ID_LastDelayBeforeEndDuration = "LastDelayBeforeEndDuration"

# options section items
ID_SymbolLevelOnWordCaretMovement = "SymbolLevelOnWordMovement"
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
ID_AppVolumeLevelAnnouncementInPercent = "AppVolumeLevelAnnouncementInPercent"
ID_DialogTitleWithAddonSummary = "DialogTitleWithAddonSummary"
# for old configuration, , must be deleted in the future
ID_DelayBetweenSameGesture = "DelayBetweenSameGesture"
ID_MaximumDelayBetweenSameScript = "MaximumDelayBetweenSameScript"
ID_MaximumOfLastUsedSymbols = "MaximumOfLastUsedSymbols"
ID_ByPassNoDescription = "ByPassNoDescription"
ID_EnableNumpadNavigationModeToggle = "EnableNumpadNavigationModeToggle"
ID_ActivateNumpadNavigationModeAtStart = "ActivateNumpadNavigationModeAtStart"
ID_ActivateNumpadStandardUseWithNumLock = "ActivateNumpadStandardUseWithNumLock"  # noqa:E501

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
		if not result:
			self._errors = result

	@property
	def errors(self):
		return self._errors


class AddonConfiguration20(BaseAddonConfiguration):
	_version = "2.0"

	_GeneralConfSpec = """[{section}]
	{idConfigVersion} = string(default = {version})
	""".format(
		section=SCT_General,
		idConfigVersion=ID_ConfigVersion,
		version=_version)

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
	""".format(
		section=SCT_InstallFeatureOptions,
		SystrayIconsAndActiveWindowsList=ID_SystrayIconsAndActiveWindowsList,
		currentFolderReport=ID_CurrentFolderReport,
		virtualBuffer=ID_ExtendedVirtualBuffer,
		complexSymbols=ID_ComplexSymbols,
		clipboardCommandAnnouncement=ID_ClipboardCommandAnnouncement,
		focusedApplicationInformations=ID_FocusedApplicationInformations,
		openNVDALog=ID_OpenCurrentOrOldNVDALogFile,
		speechHistory=ID_SpeechHistory,
		keyboardKeyRenaming=ID_KeyboardKeyRenaming,
		commandKeysSelectiveAnnouncement=ID_CommandKeysSelectiveAnnouncement,
		minuteTimer=ID_MinuteTimer,
		foregroundWindowObjectsList=ID_ForegroundWindowObjectsList,
		voiceProfileSwitching=ID_VoiceProfileSwitching,
		keyRemanence=ID_KeyRemanence,
		restartInDebugMode=ID_RestartInDebugMode,
		install=C_Install,
		DoNotInstall=C_DoNotInstall,
		installWithoutGesture=C_InstallWithoutGesture,
		volumeControl=ID_VolumeControl)

	_OptionsConfSpec = """[{section}]
		{reportNextWordOnDeletion}  = boolean(default=True)
		{NoDescriptionReportInRibbon}  = boolean(default=True)
		{automaticWindowMaximization}  = boolean(default=True)
		{reportTimeWithSeconds}  = boolean(default=False),
	""".format(
		section=SCT_Options,
		reportNextWordOnDeletion=ID_ReportNextWordOnDeletion,
		NoDescriptionReportInRibbon=ID_NoDescriptionReportInRibbon,
		automaticWindowMaximization=ID_AutomaticWindowMaximization,
		reportTimeWithSeconds=ID_ReportTimeWithSeconds)

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
			ItIsTime=("It's time"))

	_AdvancedOptionsConfSpec = """[{section}]
	{playSoundOnErrors} = integer(default=1)
	{setOnMainAndNVDAVolume}= boolean(default=True)
	{remanenceDelay} = integer(default=2000)
	{beepAtRemanenceStart}  = boolean(default=True)
	{beepAtRemanenceEnd}  = boolean(default=True)
	{minMasterVolumeLevel} = integer(default=10)
	{masterVolumeLevel} = integer(default=50)
	{minNVDAVolumeLevel} = integer(default=10)
	{NVDAVolumeLevel} = integer(default=50)
	""".format(
		section=SCT_AdvancedOptions,
		playSoundOnErrors=ID_PlaySoundOnErrors,
		remanenceDelay=ID_RemanenceDelay,
		beepAtRemanenceStart=ID_BeepAtRemanenceStart,
		beepAtRemanenceEnd=ID_BeepAtRemanenceEnd,
		setOnMainAndNVDAVolume=ID_SetOnMainAndNVDAVolume,
		minMasterVolumeLevel=ID_MinMasterVolumeLevel,
		masterVolumeLevel=ID_MasterVolumeLevel,
		minNVDAVolumeLevel=ID_MinNVDAVolumeLevel,
		NVDAVolumeLevel=ID_NVDAVolumeLevel)

	_ShutdownComputerConfSpec = """[{section}]
		{forceClose}  = boolean(default=True),
		{timeout} = integer(default = 1)
	""".format(
		section=SCT_ShutdownComputer,
		forceClose=ID_ForceClose,
		timeout=ID_ShutdownTimeout)

	#: The configuration specification
	configspec = ConfigObj(StringIO("""# addon Configuration File
	{general}\r\n{features}\r\n{options}\r\n{minuteTimer}\r\n{advancedOptions}\r\n{shutdown}
	""".format(
		general=_GeneralConfSpec,
		features=_FeatureAuthorizationsConfSpec,
		options=_OptionsConfSpec,
		minuteTimer=_MinuteTimerConfSpec,
		advancedOptions=_AdvancedOptionsConfSpec,
		shutdown=_ShutdownComputerConfSpec)
	), list_values=False, encoding="UTF-8")


class AddonConfiguration21(BaseAddonConfiguration):
	_version = "2.1"

	_GeneralConfSpec = """[{section}]
	{idConfigVersion} = string(default = {version})
	""".format(
		section=SCT_General,
		idConfigVersion=ID_ConfigVersion,
		version=_version)

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
		""".format(
			section=SCT_InstallFeatureOptions,
			SystrayIconsAndActiveWindowsList=ID_SystrayIconsAndActiveWindowsList,
			currentFolderReport=ID_CurrentFolderReport,
			virtualBuffer=ID_ExtendedVirtualBuffer,
			complexSymbols=ID_ComplexSymbols,
			clipboardCommandAnnouncement=ID_ClipboardCommandAnnouncement,
			focusedApplicationInformations=ID_FocusedApplicationInformations,
			openNVDALog=ID_OpenCurrentOrOldNVDALogFile,
			speechHistory=ID_SpeechHistory,
			keyboardKeyRenaming=ID_KeyboardKeyRenaming,
			commandKeysSelectiveAnnouncement=ID_CommandKeysSelectiveAnnouncement,
			minuteTimer=ID_MinuteTimer,
			foregroundWindowObjectsList=ID_ForegroundWindowObjectsList,
			voiceProfileSwitching=ID_VoiceProfileSwitching,
			keyRemanence=ID_KeyRemanence,
			restartInDebugMode=ID_RestartInDebugMode,
			install=C_Install,
			DoNotInstall=C_DoNotInstall,
			installWithoutGesture=C_InstallWithoutGesture,
			volumeControl=ID_VolumeControl)

	_OptionsConfSpec = """[{section}]
		{reportNextWordOnDeletion}  = boolean(default=True)
		{NoDescriptionReportInRibbon}  = boolean(default=True)
		{automaticWindowMaximization}  = boolean(default=True)
		{reportTimeWithSeconds}  = boolean(default=False),
		{speechRecordWithNumber}  = boolean(default=True),
	""".format(
		section=SCT_Options,
		reportNextWordOnDeletion=ID_ReportNextWordOnDeletion,
		NoDescriptionReportInRibbon=ID_NoDescriptionReportInRibbon,
		automaticWindowMaximization=ID_AutomaticWindowMaximization,
		reportTimeWithSeconds=ID_ReportTimeWithSeconds,
		speechRecordWithNumber=ID_SpeechRecordWithNumber)

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
		{setOnMainAndNVDAVolume}= boolean(default=True)
		{remanenceDelay} = integer(default=2000)
		{beepAtRemanenceStart}  = boolean(default=True)
		{beepAtRemanenceEnd}  = boolean(default=True)
		{minMasterVolumeLevel} = integer(default=10)
		{masterVolumeLevel} = integer(default=50)
		{minNVDAVolumeLevel} = integer(default=10)
		{NVDAVolumeLevel} = integer(default=50)
		{dialogTitleWithAddonSummary}  = boolean(default=True)
		""".format(
			section=SCT_AdvancedOptions,
			playSoundOnErrors=ID_PlaySoundOnErrors,
			remanenceDelay=ID_RemanenceDelay,
			beepAtRemanenceStart=ID_BeepAtRemanenceStart,
			beepAtRemanenceEnd=ID_BeepAtRemanenceEnd,
			setOnMainAndNVDAVolume=ID_SetOnMainAndNVDAVolume,
			minMasterVolumeLevel=ID_MinMasterVolumeLevel,
			masterVolumeLevel=ID_MasterVolumeLevel,
			minNVDAVolumeLevel=ID_MinNVDAVolumeLevel,
			NVDAVolumeLevel=ID_NVDAVolumeLevel,
			dialogTitleWithAddonSummary=ID_DialogTitleWithAddonSummary)

	_ShutdownComputerConfSpec = """[{section}]
		{forceClose}  = boolean(default=True),
		{timeout} = integer(default = 1)
""".format(
		section=SCT_ShutdownComputer,
		forceClose=ID_ForceClose,
		timeout=ID_ShutdownTimeout)

	#: The configuration specification
	configspec = ConfigObj(StringIO("""# addon Configuration File
	{general}\r\n{features}\r\n{options}\r\n{minuteTimer}\r\n{advancedOptions}\r\n{shutdown}
""".format(
		general=_GeneralConfSpec,
		features=_FeatureAuthorizationsConfSpec,
		options=_OptionsConfSpec,
		minuteTimer=_MinuteTimerConfSpec,
		advancedOptions=_AdvancedOptionsConfSpec,
		shutdown=_ShutdownComputerConfSpec)
		), list_values=False, encoding="UTF-8")


class AddonConfiguration22(BaseAddonConfiguration):
	_version = "2.2"
	_GeneralConfSpec = """[{section}]
	{idConfigVersion} = string(default = {version})
		""".format(
			section=SCT_General,
			idConfigVersion=ID_ConfigVersion,
			version=_version)

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
	""".format(
		section=SCT_InstallFeatureOptions,
		SystrayIconsAndActiveWindowsList=ID_SystrayIconsAndActiveWindowsList,
		currentFolderReport=ID_CurrentFolderReport,
		virtualBuffer=ID_ExtendedVirtualBuffer,
		complexSymbols=ID_ComplexSymbols,
		clipboardCommandAnnouncement=ID_ClipboardCommandAnnouncement,
		focusedApplicationInformations=ID_FocusedApplicationInformations,
		openNVDALog=ID_OpenCurrentOrOldNVDALogFile,
		speechHistory=ID_SpeechHistory,
		keyboardKeyRenaming=ID_KeyboardKeyRenaming,
		commandKeysSelectiveAnnouncement=ID_CommandKeysSelectiveAnnouncement,
		minuteTimer=ID_MinuteTimer,
		foregroundWindowObjectsList=ID_ForegroundWindowObjectsList,
		voiceProfileSwitching=ID_VoiceProfileSwitching,
		keyRemanence=ID_KeyRemanence,
		restartInDebugMode=ID_RestartInDebugMode,
		install=C_Install,
		DoNotInstall=C_DoNotInstall,
		installWithoutGesture=C_InstallWithoutGesture,
		volumeControl=ID_VolumeControl)

	_OptionsConfSpec = """[{section}]
		{reportNextWordOnDeletion}  = boolean(default=True)
		{NoDescriptionReportInRibbon}  = boolean(default=True)
		{automaticWindowMaximization}  = boolean(default=True)
		{reportTimeWithSeconds}  = boolean(default=False),
		{speechRecordWithNumber}  = boolean(default=True),
	""".format(
		section=SCT_Options,
		reportNextWordOnDeletion=ID_ReportNextWordOnDeletion,
		NoDescriptionReportInRibbon=ID_NoDescriptionReportInRibbon,
		automaticWindowMaximization=ID_AutomaticWindowMaximization,
		reportTimeWithSeconds=ID_ReportTimeWithSeconds,
		speechRecordWithNumber=ID_SpeechRecordWithNumber)

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
		{setOnMainAndNVDAVolume}= boolean(default=True)
		{remanenceDelay} = integer(default=2000)
		{beepAtRemanenceStart}  = boolean(default=True)
		{beepAtRemanenceEnd}  = boolean(default=True)
		{minMasterVolumeLevel} = integer(default=10)
		{masterVolumeLevel} = integer(default=50)
		{minNVDAVolumeLevel} = integer(default=10)
		{NVDAVolumeLevel} = integer(default=50)
		{dialogTitleWithAddonSummary}  = boolean(default=True)
		{maximumDelayBetweenSameScript} = integer(default=250)
		{maximumOfLastUsedSymbols} = integer(default=20)
		{byPassNoDescription}  = boolean(default=True)
		""".format(
			section=SCT_AdvancedOptions,
			playSoundOnErrors=ID_PlaySoundOnErrors,
			remanenceDelay=ID_RemanenceDelay,
			beepAtRemanenceStart=ID_BeepAtRemanenceStart,
			beepAtRemanenceEnd=ID_BeepAtRemanenceEnd,
			setOnMainAndNVDAVolume=ID_SetOnMainAndNVDAVolume,
			minMasterVolumeLevel=ID_MinMasterVolumeLevel,
			masterVolumeLevel=ID_MasterVolumeLevel,
			minNVDAVolumeLevel=ID_MinNVDAVolumeLevel,
			NVDAVolumeLevel=ID_NVDAVolumeLevel,
			dialogTitleWithAddonSummary=ID_DialogTitleWithAddonSummary,
			maximumDelayBetweenSameScript=ID_MaximumDelayBetweenSameScript,
			maximumOfLastUsedSymbols=ID_MaximumOfLastUsedSymbols,
			byPassNoDescription=ID_ByPassNoDescription)

	_ShutdownComputerConfSpec = """[{section}]
		{forceClose}  = boolean(default=True),
		{timeout} = integer(default = 1)
""".format(
		section=SCT_ShutdownComputer,
		forceClose=ID_ForceClose,
		timeout=ID_ShutdownTimeout)

	#: The configuration specification
	configspec = ConfigObj(StringIO("""# addon Configuration File
{general}\r\n{features}\r\n{options}\r\n{minuteTimer}\r\n{advancedOptions}\r\n{shutdown}
""".format(
		general=_GeneralConfSpec,
		features=_FeatureAuthorizationsConfSpec,
		options=_OptionsConfSpec,
		minuteTimer=_MinuteTimerConfSpec,
		advancedOptions=_AdvancedOptionsConfSpec,
		shutdown=_ShutdownComputerConfSpec)
	), list_values=False, encoding="UTF-8")


class AddonConfiguration23(BaseAddonConfiguration):
	_version = "2.3"

	_GeneralConfSpec = """[{section}]
	{idConfigVersion} = string(default = {version})
		""".format(
			section=SCT_General,
			idConfigVersion=ID_ConfigVersion,
			version=_version)

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
	""".format(
		section=SCT_InstallFeatureOptions,
		SystrayIconsAndActiveWindowsList=ID_SystrayIconsAndActiveWindowsList,
		currentFolderReport=ID_CurrentFolderReport,
		virtualBuffer=ID_ExtendedVirtualBuffer,
		complexSymbols=ID_ComplexSymbols,
		clipboardCommandAnnouncement=ID_ClipboardCommandAnnouncement,
		focusedApplicationInformations=ID_FocusedApplicationInformations,
		openNVDALog=ID_OpenCurrentOrOldNVDALogFile,
		speechHistory=ID_SpeechHistory,
		keyboardKeyRenaming=ID_KeyboardKeyRenaming,
		commandKeysSelectiveAnnouncement=ID_CommandKeysSelectiveAnnouncement,
		minuteTimer=ID_MinuteTimer,
		foregroundWindowObjectsList=ID_ForegroundWindowObjectsList,
		voiceProfileSwitching=ID_VoiceProfileSwitching,
		keyRemanence=ID_KeyRemanence,
		restartInDebugMode=ID_RestartInDebugMode,
		install=C_Install,
		DoNotInstall=C_DoNotInstall,
		installWithoutGesture=C_InstallWithoutGesture,
		volumeControl=ID_VolumeControl,
		tools=ID_Tools)

	_OptionsConfSpec = """[{section}]
		{reportNextWordOnDeletion}  = boolean(default=True)
		{NoDescriptionReportInRibbon}  = boolean(default=True)
		{automaticWindowMaximization}  = boolean(default=True)
		{reportTimeWithSeconds}  = boolean(default=False),
		{speechRecordWithNumber}  = boolean(default=True),
				{loopInNavigationMode}  = boolean(default=False),
	""".format(
		section=SCT_Options,
		reportNextWordOnDeletion=ID_ReportNextWordOnDeletion,
		NoDescriptionReportInRibbon=ID_NoDescriptionReportInRibbon,
		automaticWindowMaximization=ID_AutomaticWindowMaximization,
		reportTimeWithSeconds=ID_ReportTimeWithSeconds,
		speechRecordWithNumber=ID_SpeechRecordWithNumber,
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
		{setOnMainAndNVDAVolume}= boolean(default=True)
		{remanenceDelay} = integer(default=2000)
		{beepAtRemanenceStart}  = boolean(default=True)
		{beepAtRemanenceEnd}  = boolean(default=True)
		{minMasterVolumeLevel} = integer(default=10)
		{masterVolumeLevel} = integer(default=50)
		{minNVDAVolumeLevel} = integer(default=10)
		{NVDAVolumeLevel} = integer(default=50)
		{dialogTitleWithAddonSummary}  = boolean(default=True)
		{delayBetweenSameGesture} = integer(default=250)
		{maximumOfLastUsedSymbols} = integer(default=20)
		{byPassNoDescription}  = boolean(default=True)
		""".format(
			section=SCT_AdvancedOptions,
			playSoundOnErrors=ID_PlaySoundOnErrors,
			remanenceDelay=ID_RemanenceDelay,
			beepAtRemanenceStart=ID_BeepAtRemanenceStart,
			beepAtRemanenceEnd=ID_BeepAtRemanenceEnd,
			setOnMainAndNVDAVolume=ID_SetOnMainAndNVDAVolume,
			minMasterVolumeLevel=ID_MinMasterVolumeLevel,
			masterVolumeLevel=ID_MasterVolumeLevel,
			minNVDAVolumeLevel=ID_MinNVDAVolumeLevel,
			NVDAVolumeLevel=ID_NVDAVolumeLevel,
			dialogTitleWithAddonSummary=ID_DialogTitleWithAddonSummary,
			delayBetweenSameGesture=ID_DelayBetweenSameGesture,
			maximumOfLastUsedSymbols=ID_MaximumOfLastUsedSymbols,
			byPassNoDescription=ID_ByPassNoDescription)

	_ShutdownComputerConfSpec = """[{section}]
		{forceClose}  = boolean(default=True),
		{timeout} = integer(default = 1)
""".format(
		section=SCT_ShutdownComputer,
		forceClose=ID_ForceClose,
		timeout=ID_ShutdownTimeout)

	#: The configuration specification
	configspec = ConfigObj(StringIO("""# addon Configuration File
{general}\r\n{features}\r\n{options}\r\n{minuteTimer}\r\n{advancedOptions}\r\n{shutdown}
""".format(
		general=_GeneralConfSpec,
		features=_FeatureAuthorizationsConfSpec,
		options=_OptionsConfSpec,
		minuteTimer=_MinuteTimerConfSpec,
		advancedOptions=_AdvancedOptionsConfSpec,
		shutdown=_ShutdownComputerConfSpec)
	), list_values=False, encoding="UTF-8")


class AddonConfiguration24(BaseAddonConfiguration):
	_version = "2.4"
	_GeneralConfSpec = """[{section}]
	{idConfigVersion} = string(default = {version})
		""".format(
		section=SCT_General,
		idConfigVersion=ID_ConfigVersion,
		version=_version)

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
		SystrayIconsAndActiveWindowsList=ID_SystrayIconsAndActiveWindowsList,
		currentFolderReport=ID_CurrentFolderReport,
		virtualBuffer=ID_ExtendedVirtualBuffer,
		complexSymbols=ID_ComplexSymbols,
		clipboardCommandAnnouncement=ID_ClipboardCommandAnnouncement,
		focusedApplicationInformations=ID_FocusedApplicationInformations,
		openNVDALog=ID_OpenCurrentOrOldNVDALogFile,
		speechHistory=ID_SpeechHistory,
		keyboardKeyRenaming=ID_KeyboardKeyRenaming,
		commandKeysSelectiveAnnouncement=ID_CommandKeysSelectiveAnnouncement,
		minuteTimer=ID_MinuteTimer,
		foregroundWindowObjectsList=ID_ForegroundWindowObjectsList,
		voiceProfileSwitching=ID_VoiceProfileSwitching,
		keyRemanence=ID_KeyRemanence,
		restartInDebugMode=ID_RestartInDebugMode,
		install=C_Install,
		DoNotInstall=C_DoNotInstall,
		installWithoutGesture=C_InstallWithoutGesture,
		volumeControl=ID_VolumeControl,
		tools=ID_Tools,
		dateAndTime=ID_DateAndTime)

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
		{dialogTitleWithAddonSummary}  = boolean(default=True)
		{delayBetweenSameGesture} = integer(default=250)
		{maximumOfLastUsedSymbols} = integer(default={c_MaximumOfLastUsedSymbols} )
		{byPassNoDescription}  = boolean(default=True)
		""".format(
			section=SCT_AdvancedOptions,
			playSoundOnErrors=ID_PlaySoundOnErrors,
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
			dialogTitleWithAddonSummary=ID_DialogTitleWithAddonSummary,
			delayBetweenSameGesture=ID_DelayBetweenSameGesture,
			maximumOfLastUsedSymbols=ID_MaximumOfLastUsedSymbols,
			byPassNoDescription=ID_ByPassNoDescription,
			c_MinMasterVolumeLevel=C_MinMasterVolumeLevel,
			c_MasterVolumeLevel=C_MasterVolumeLevel,
			c_MinNVDAVolumeLevel=C_MinNVDAVolumeLevel,
			c_NVDAVolumeLevel=C_NVDAVolumeLevel,
			c_MaximumOfLastUsedSymbols=C_MaximumOfLastUsedSymbols)

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
		SystrayIconsAndActiveWindowsList=ID_SystrayIconsAndActiveWindowsList,
		currentFolderReport=ID_CurrentFolderReport,
		virtualBuffer=ID_ExtendedVirtualBuffer,
		complexSymbols=ID_ComplexSymbols,
		clipboardCommandAnnouncement=ID_ClipboardCommandAnnouncement,
		focusedApplicationInformations=ID_FocusedApplicationInformations,
		openNVDALog=ID_OpenCurrentOrOldNVDALogFile,
		speechHistory=ID_SpeechHistory,
		keyboardKeyRenaming=ID_KeyboardKeyRenaming,
		commandKeysSelectiveAnnouncement=ID_CommandKeysSelectiveAnnouncement,
		minuteTimer=ID_MinuteTimer,
		foregroundWindowObjectsList=ID_ForegroundWindowObjectsList,
		voiceProfileSwitching=ID_VoiceProfileSwitching,
		keyRemanence=ID_KeyRemanence,
		restartInDebugMode=ID_RestartInDebugMode,
		install=C_Install,
		DoNotInstall=C_DoNotInstall,
		installWithoutGesture=C_InstallWithoutGesture,
		volumeControl=ID_VolumeControl,
		tools=ID_Tools,
		dateAndTime=ID_DateAndTime)

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
			activateNumpadStandardUseWithNumLock=ID_ActivateNumpadStandardUseWithNumLock)  # noqa:E501

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
		SystrayIconsAndActiveWindowsList=ID_SystrayIconsAndActiveWindowsList,
		currentFolderReport=ID_CurrentFolderReport,
		virtualBuffer=ID_ExtendedVirtualBuffer,
		complexSymbols=ID_ComplexSymbols,
		clipboardCommandAnnouncement=ID_ClipboardCommandAnnouncement,
		focusedApplicationInformations=ID_FocusedApplicationInformations,
		openNVDALog=ID_OpenCurrentOrOldNVDALogFile,
		speechHistory=ID_SpeechHistory,
		keyboardKeyRenaming=ID_KeyboardKeyRenaming,
		commandKeysSelectiveAnnouncement=ID_CommandKeysSelectiveAnnouncement,
		minuteTimer=ID_MinuteTimer,
		foregroundWindowObjectsList=ID_ForegroundWindowObjectsList,
		voiceProfileSwitching=ID_VoiceProfileSwitching,
		keyRemanence=ID_KeyRemanence,
		restartInDebugMode=ID_RestartInDebugMode,
		install=C_Install,
		DoNotInstall=C_DoNotInstall,
		installWithoutGesture=C_InstallWithoutGesture,
		volumeControl=ID_VolumeControl,
		tools=ID_Tools,
		dateAndTime=ID_DateAndTime)

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
			appVolumeLevelAnnouncementInPercent= ID_AppVolumeLevelAnnouncementInPercent,
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
			activateNumpadStandardUseWithNumLock=ID_ActivateNumpadStandardUseWithNumLock)  # noqa:E501

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

