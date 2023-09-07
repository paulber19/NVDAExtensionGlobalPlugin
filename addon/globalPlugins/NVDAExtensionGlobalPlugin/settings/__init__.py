# globalPlugins\NVDAExtensionGlobalPlugin\settings\__init__.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2022 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

# Manages configuration.
import addonHandler
from logHandler import log
import os
import core
import queueHandler
import globalVars
import config
import gui
import wx
import buildVersion
import ui
from configobj.validate import Validator, VdtTypeError
from languageHandler import getLanguage
from . import addonConfig
from ..utils.secure import inSecureMode

addonHandler.initTranslation()
# list of functionnalities which should not be installed in secure mode
_functionnalitiesNoInSecurMode = [
	addonConfig.FCT_SystrayIconsAndActiveWindowsList,
	addonConfig.FCT_FocusedApplicationInformations,
	addonConfig.FCT_ExtendedVirtualBuffer,
	addonConfig.FCT_ClipboardCommandAnnouncement,
	addonConfig.FCT_CurrentFolderReport,
	addonConfig.FCT_RestartInDebugMode,
	addonConfig.FCT_OpenCurrentOrOldNVDALogFile,
	addonConfig.FCT_SplitAudio,
	addonConfig.FCT_Tools,
	addonConfig.FCT_TextAnalysis,
	addonConfig.FCT_ManageUserConfigurations,
	addonConfig.FCT_ExploreNVDA,
	addonConfig.FCT_VariousOutSecureMode,
]


def getInstallFeatureOption(featureID):
	if inSecureMode():
		if featureID in _functionnalitiesNoInSecurMode:
			return addonConfig.C_DoNotInstall
	conf = _addonConfigManager.addonConfig
	state = conf[addonConfig.SCT_InstallFeatureOptions].get(featureID)
	if state is None:
		# by default, fonctionnality is installed
		state = addonConfig.C_Install
	return state


def setInstallFeatureOption(featureID, option):
	global _addonConfigManager
	conf = _addonConfigManager.addonConfig
	conf[addonConfig.SCT_InstallFeatureOptions][featureID] = option
	log.debug("setInstallFeatureOption: feature= %s, value= %s" % (
		featureID, conf[addonConfig.SCT_InstallFeatureOptions][featureID]))


def isInstall(featureID):
	option = getInstallFeatureOption(featureID)
	return False if option == addonConfig.C_DoNotInstall else True


def isInstallWithoutGesture(featureID):
	conf = _addonConfigManager.addonConfig
	option = conf[addonConfig.SCT_InstallFeatureOptions][featureID]
	return True if option == addonConfig.C_InstallWithoutGesture else False


def TOGGLE(sct, id, toggle):
	global _addonConfigManager
	conf = _addonConfigManager.addonConfig
	if toggle:
		conf[sct][id] = not conf[sct][id]
		log.debug("toggle:  sct= %s, id= %s, value= %s" % (
			sct, id, conf[sct][id]
		))
	return conf[sct][id]


def toggleGeneralOptions(id, toggle):
	sct = addonConfig.SCT_General
	return TOGGLE(sct, id, toggle)


def toggleAutoUpdateGeneralOptions(toggle=True):
	return toggleGeneralOptions(addonConfig.ID_AutoUpdate, toggle)


def toggleUpdateReleaseVersionsToDevVersionsGeneralOptions(toggle=True):
	return toggleGeneralOptions(addonConfig.ID_UpdateReleaseVersionsToDevVersions, toggle)


def toggleRemindUpdateGeneralOptions(toggle=True):
	return toggleGeneralOptions(addonConfig.ID_RemindUpdate, toggle)


def toggleOption(id, toggle):
	sct = addonConfig.SCT_Options
	return TOGGLE(sct, id, toggle)


def toggleNoDescriptionReportInRibbonOption(toggle=True):
	return toggleOption(addonConfig.ID_NoDescriptionReportInRibbon, toggle)


def toggleAutomaticWindowMaximizationOption(toggle=True):
	return toggleOption(addonConfig.ID_AutomaticWindowMaximization, toggle)


def toggleReportTimeWithSecondsOption(toggle=True):
	return toggleOption(addonConfig.ID_ReportTimeWithSeconds, toggle)


def toggleSpeechRecordWithNumberOption(toggle=True):
	return toggleOption(addonConfig.ID_SpeechRecordWithNumber, toggle)


def toggleSpeechRecordInAscendingOrderOption(toggle=True):
	return toggleOption(addonConfig.ID_SpeechRecordInAscendingOrder, toggle)


def toggleLoopInNavigationModeOption(toggle=True):
	return toggleOption(addonConfig.ID_LoopInNavigationMode, toggle)


def toggleAdvancedOption(id, toggle):
	sct = addonConfig.SCT_AdvancedOptions
	return TOGGLE(sct, id, toggle)


def toggleBeepAtRemanenceStartAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_BeepAtRemanenceStart, toggle)


def toggleBeepAtRemanenceEndAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_BeepAtRemanenceEnd, toggle)


def toggleSetOnMainAndNVDAVolumeAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_SetOnMainAndNVDAVolume, toggle)


def toggleReportVolumeChangeAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_ReportVolumeChange, toggle)


def toggleIncreaseSpeakersVolumeIfNecessaryAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_IncreaseSpeakersVolumeIfNecessary, toggle)


def toggleDialogTitleWithAddonSummaryAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_DialogTitleWithAddonSummary, toggle)


def toggleByPassNoDescriptionAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_ByPassNoDescription, toggle)


def toggleOnlyNVDAKeyInRemanenceAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_OnlyNVDAKeyInRemanence, toggle)


def toggleRemanenceAtNVDAStartAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_RemanenceAtNVDAStart, toggle)


def toggleRemanenceForGmailAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_RemanenceForGmail, toggle)


def toggleEnableNumpadNavigationModeToggleAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_EnableNumpadNavigationModeToggle, toggle)


def toggleActivateNumpadNavigationModeAtStartAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_ActivateNumpadNavigationModeAtStart, toggle)


def toggleActivateNumpadStandardUseWithNumLockAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_ActivateNumpadStandardUseWithNumLock, toggle)


def toggleConfirmAudioDeviceChangeAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_ConfirmAudioDeviceChange, toggle)


def toggleReportNumlockStateAtStartAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_ReportNumlockStateAtStart, toggle)


def toggleReportCapslockStateAtStartAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_ReportCapslockStateAtStart, toggle)


def toggleReversedPathWithLevelAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_ReversedPathWithLevel, toggle)


def toggleLimitKeyRepeatsAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_LimitKeyRepeats, toggle)


def toggleRecordCurrentSettingsForCurrentSelectorAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_RecordCurrentSettingsForCurrentSelector, toggle)


def toggleTypedWordSpeakingEnhancementAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_TypedWordSpeakingEnhancement, toggle)


def toggleAllowNVDATonesVolumeAdjustmentAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_AllowNVDATonesVolumeAdjustment, toggle)


def toggleAllowNVDASoundGainModificationAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_AllowNVDASoundGainModification, toggle)


def togglePlayToneOnAudioDeviceAdvancedOption(toggle=True):
	return toggleAdvancedOption(addonConfig.ID_PlayToneOnAudioDevice, toggle)


class AddonConfigurationManager():
	_currentConfigVersion = "3.1"
	_configFileName = "NVDAExtensionGlobalPluginAddon.ini"
	_versionToConfiguration = {

		"2.5": addonConfig.AddonConfiguration25,
		"2.6": addonConfig.AddonConfiguration26,
		"2.7": addonConfig.AddonConfiguration27,
		"2.8": addonConfig.AddonConfiguration28,
		"2.9": addonConfig.AddonConfiguration29,
		"3.0": addonConfig.AddonConfiguration30,
		"3.1": addonConfig.AddonConfiguration31,
	}

	def __init__(self):
		global _addonConfigManager
		self.curAddon = addonHandler.getCodeAddon()
		self.addonName = self.curAddon.manifest["name"]
		from keyLabels import localizedKeyLabels
		self.basicLocalizedKeyLabels = localizedKeyLabels.copy()
		self.restoreAddonProfilesConfig(self.addonName)
		self.loadSettings()
		log.debug("%s configuration: %s" % (self.addonName, self.addonConfig))
		self.setIsTestVersionFlag()
		config.post_configSave.register(self.handlePostConfigSave)

	def restoreAddonProfilesConfig(self, addonName):
		conf = config.conf
		save = False
		if "%s-temp" % addonName in conf.profiles[0]:
			log.warning("restoreAddonProfilesConfig profile[0]")
			conf.profiles[0][addonName] = conf.profiles[0]["%s-temp" % addonName].copy()
			del conf.profiles[0]["%s-temp" % addonName]
			save = True
		profileNames = []
		profileNames.extend(config.conf.listProfiles())
		for name in profileNames:
			profile = config.conf._getProfile(name)
			if profile.get("%s-temp" % addonName):
				log.warning("restoreAddonProfilesConfig: profile %s" % name)
				profile[addonName] = profile["%s-temp" % addonName].copy()
				del profile["%s-temp" % addonName]
				config.conf._dirtyProfiles.add(name)
				save = True
		# We save the configuration,
				# in case the user would not have checked
				# the "Save configuration on exit" checkbox in General settings.
		if save:
			config.conf.save()

	def warnConfigurationReset(self):
		wx.CallLater(
			100,
			gui.messageBox,
			# Translators: A message warning configuration reset.
			_(
				"The configuration file of the add-on contains errors. "
				"The part of the configuration concerning the global parameters has been  reset to factory defaults"),
			# Translators: title of message box
			"{addon} - {title}" .format(addon=self.curAddon.manifest["summary"], title=_("Warning")),
			wx.OK | wx.ICON_WARNING
		)

	def loadSettings(self):
		from .addonConfig import BaseAddonConfiguration, SCT_General, ID_ConfigVersion
		addonConfigFile = os.path.join(
			globalVars.appArgs.configPath, self._configFileName)
		doMerge = True
		if os.path.exists(addonConfigFile):
			# there is allready a config file
			try:
				baseConfig = BaseAddonConfiguration(addonConfigFile)
				if baseConfig.errors:
					e = Exception("Error parsing configuration file:\n%s" % baseConfig.errors)
					raise e
				if baseConfig[SCT_General][ID_ConfigVersion] != self._currentConfigVersion:
					# it's an old config, but old config file must not exist here.
					# Must be deleted
					os.remove(addonConfigFile)
					log.warning("NVDAExtensionGlobalPlugin: old config file removed: %s" % addonConfigFile)
				else:
					# it's the same version of config, so no merge
					doMerge = False
			except Exception as e:
				log.warning(e)
				# error on reading config file, so delete it
				os.remove(addonConfigFile)
				self.warnConfigurationReset()
		self.shouldSetRecoveryDefaultVolumes = False
		if os.path.exists(addonConfigFile):
			self.addonConfig =\
				self._versionToConfiguration[self._currentConfigVersion](addonConfigFile)
			if self.addonConfig.errors:
				log.warning(self.addonConfig.errors)
				log.warning(
					"Addon configuration file error: configuration reset to factory defaults")
				os.remove(addonConfigFile)
				self.warnConfigurationReset()
				# reset configuration to factory defaults
				self.addonConfig =\
					self._versionToConfiguration[self._currentConfigVersion](None)
				self.addonConfig.filename = addonConfigFile
				doMerge = False
		else:
			# no add-on configuration file found
			self.addonConfig =\
				self._versionToConfiguration[self._currentConfigVersion](None)
			self.addonConfig.filename = addonConfigFile
			# probably, it's an add-on installation, set recovery default volumes
			self.shouldSetRecoveryDefaultVolumes = True
		# merge step
		oldConfigFile = os.path.join(self.curAddon.path, self._configFileName)
		if os.path.exists(oldConfigFile):
			if doMerge:
				self.mergeSettings(oldConfigFile)
			os.remove(oldConfigFile)
		if not os.path.exists(addonConfigFile):
			self.saveSettings(True)

	def mergeSettings(self, oldConfigFile):
		log.warning("Merge settings with old configuration")
		from .addonConfig import BaseAddonConfiguration, SCT_General, ID_ConfigVersion
		baseConfig = BaseAddonConfiguration(oldConfigFile)
		version = baseConfig[SCT_General][ID_ConfigVersion]
		if version not in self._versionToConfiguration:
			log.warning("Configuration merge error: unknown configuration version")
			return
		oldConfig = self._versionToConfiguration[version](oldConfigFile)
		if oldConfig .errors:
			log.warning("Merge settings with old configuration errors: \n%s" % oldConfig .errors)
			log.warning("Merge settings with old configuration : merge aborted")
			wx.CallLater(
				100,
				gui.messageBox,
				# Translators: message to inform the user
				# than it's not possible to merge with old configuration because of error.
				_(
					"""The old configuration file of "%s" add-on contains errors. """
					"""It's not possible to keep previous configuration""") % self.curAddon.manifest["summary"],
				# Translators: title of message box
				"{addon} - {title}" .format(addon=self.curAddon.manifest["summary"], title=_("Warning")),
				wx.OK | wx.ICON_WARNING
			)
			core.callLater(
				1000,
				ui.message,
				# Translators: message to inform the user
				# than it's not possible to merge with old configuration because of error.
				_(
					"""The old configuration file of "%s" add-on contains errors. """
					"""It's not possible to keep previous configuration""") % (
						self.curAddon.manifest["summary"]))
			return
		for sect in self.addonConfig.sections:
			for k in self.addonConfig[sect]:
				if sect == addonConfig.SCT_General and k == addonConfig.ID_ConfigVersion:
					continue
				if sect in oldConfig.sections and k in oldConfig[sect]:
					if sect == addonConfig.SCT_InstallFeatureOptions:
						# option type is not more booleen but integer
						self.addonConfig[sect][k] = int(oldConfig[sect][k])
					else:
						self.addonConfig[sect][k] = oldConfig[sect][k]
		# others section
		from .addonConfig import SCT_RedefinedKeyLabels
		for sect in [SCT_RedefinedKeyLabels, ]:
			if sect in oldConfig.sections:
				self.addonConfig[sect] = oldConfig[sect]

	def handlePostConfigSave(self):
		self.saveSettings(True)

	def saveSettings(self, force=False):
		# We never want to save config if runing securely
		if inSecureMode():
			return
		# We save the configuration,
			# in case the user would not have checked the "Save configuration on exit"
			# checkbox in General settings or force is is True
		if not force\
			and not config.conf['general']['saveConfigurationOnExit']:
			return
		if self.addonConfig is None:
			return
		val = Validator()
		try:
			self.addonConfig.validate(val, copy=True)
		except VdtTypeError:
			# error in configuration file
			log.warning("saveSettings: validator error: %s" % self.addonConfig.errors)
			return
		try:
			self.addonConfig.write()
			log.warning("add-on configuration saved")
		except Exception:
			log.warning("Could not save add-on configuration - probably read only file system")

	def resetConfiguration(self):
		from ..utils import makeAddonWindowTitle
		if gui.messageBox(
			# Translators: A message asking the user to confirm reset of configuration.
			_(
				"The add-on configuration will be reset to factory values and NVDA will be restarted. "
				"Would you like to continue?"),
			makeAddonWindowTitle(_("Configuration reset")),
			wx.YES | wx.NO | wx.ICON_WARNING) == wx.NO:
			return
		addonConfigFile = os.path.join(
			globalVars.appArgs.configPath, self._configFileName)
		os.remove(addonConfigFile)
		self.addonConfig = self._versionToConfiguration[self._currentConfigVersion](None)
		self.saveSettings(True)
		from .nvdaConfig import _NVDAConfigManager

		_NVDAConfigManager.deleteConfiguration()
		queueHandler.queueFunction(queueHandler.eventQueue, core.restart)

	def terminate(self):
		log.warning("addonConfigManager terminate")
		self.saveSettings()
		config.post_configSave.unregister(self.handlePostConfigSave)

	def saveRedefinedKeyLabels(self, keyLabels):
		from .addonConfig import SCT_RedefinedKeyNames, SCT_RedefinedKeyLabels
		lang = getLanguage().split("-")[0]
		conf = self.addonConfig
		if SCT_RedefinedKeyNames not in conf:
			conf[SCT_RedefinedKeyLabels] = {}
		elif lang in conf[SCT_RedefinedKeyLabels]:
			del conf[SCT_RedefinedKeyLabels][lang]
		conf[SCT_RedefinedKeyLabels][lang] = {}
		for keyName in keyLabels:
			conf[SCT_RedefinedKeyLabels][lang][keyName] = keyLabels[keyName]

	def getRedefinedKeyLabels(self):
		from .addonConfig import SCT_RedefinedKeyLabels
		lang = getLanguage().split("-")[0]
		conf = self.addonConfig
		if SCT_RedefinedKeyLabels in conf and lang in conf[SCT_RedefinedKeyLabels]:
			labels = conf[SCT_RedefinedKeyLabels][lang].copy()
			if len(labels):
				return labels
		return {}

	def reDefineKeyboardKeyLabels(self):
		from keyLabels import localizedKeyLabels
		localizedKeyLabels.clear()
		for key in self.basicLocalizedKeyLabels:
			localizedKeyLabels[key] = self.basicLocalizedKeyLabels[key]

		labels = self.getRedefinedKeyLabels()
		for key in labels:
			if key in localizedKeyLabels:
				localizedKeyLabels[key] = labels[key]
			else:
				# error, it's not a good key
				log.error("error in RedefinedKeyLabels section: bad key %s" % key)

	def getBasicLocalizedKeyLabels(self):
		return self.basicLocalizedKeyLabels

	# complex symbols editing feature
	def getUserComplexSymbols(self):
		from .addonConfig import SCT_CategoriesAndSymbols
		lang = getLanguage().split("-")[0]
		conf = self.addonConfig
		if SCT_CategoriesAndSymbols in conf\
			and lang in conf[SCT_CategoriesAndSymbols]:
			return conf[SCT_CategoriesAndSymbols][lang].copy()
		return {}

	def saveUserComplexSymbols(self, userComplexSymbols):
		from .addonConfig import SCT_CategoriesAndSymbols
		lang = getLanguage().split("-")[0]
		conf = self.addonConfig
		if SCT_CategoriesAndSymbols not in conf:
			conf[SCT_CategoriesAndSymbols] = {}
		conf[SCT_CategoriesAndSymbols][lang] = {}
		for sect in userComplexSymbols:
			if sect not in conf[SCT_CategoriesAndSymbols][lang]:
				conf[SCT_CategoriesAndSymbols][lang][sect] = {}
			for symbol in userComplexSymbols[sect]:
				conf[SCT_CategoriesAndSymbols	][lang][sect][symbol] =\
					userComplexSymbols[sect][symbol]

	def deleceAllUserComplexSymbols(self):
		from .addonConfig import SCT_CategoriesAndSymbols
		conf = self.addonConfig
		if SCT_CategoriesAndSymbols in conf:
			del conf[SCT_CategoriesAndSymbols]
			# delece All User Complex Symbols in configuration profiles
		from .nvdaConfig import _NVDAConfigManager
		_NVDAConfigManager.deleceAllLastUserComplexSymbols()

	def getMaximumOfLastUsedSymbols(self):
		from .addonConfig import SCT_AdvancedOptions, ID_MaximumOfLastUsedSymbols
		conf = self.addonConfig
		return int(conf[SCT_AdvancedOptions][ID_MaximumOfLastUsedSymbols])

	def setMaximumOfLastUsedSymbols(self, max):
		from .addonConfig import SCT_AdvancedOptions, ID_MaximumOfLastUsedSymbols
		conf = self.addonConfig
		conf[SCT_AdvancedOptions][ID_MaximumOfLastUsedSymbols] = str(max)

	def getMaximumClipboardReportedCharacters(self):
		from .addonConfig import SCT_AdvancedOptions, ID_MaxClipboardReportedCharacters
		conf = self.addonConfig
		return int(conf[SCT_AdvancedOptions][ID_MaxClipboardReportedCharacters])

	def setMaximumClipboardReportedCharacters(self, max):
		from .addonConfig import SCT_AdvancedOptions, ID_MaxClipboardReportedCharacters
		conf = self.addonConfig
		conf[SCT_AdvancedOptions][ID_MaxClipboardReportedCharacters] = str(max)

	# minute timer feature
	def getMinuteTimerOptions(self):
		from .addonConfig import (
			SCT_MinuteTimer, ID_RingCount, ID_DelayBetweenRings)
		conf = self.addonConfig
		return (
			conf[SCT_MinuteTimer][ID_RingCount],
			conf[SCT_MinuteTimer][ID_DelayBetweenRings])

	def saveMinuteTimerOptions(self, options):
		from .addonConfig import (
			SCT_MinuteTimer, ID_RingCount, ID_DelayBetweenRings)
		(ringCount, delayBetweenRings) = options
		conf = self.addonConfig
		conf[SCT_MinuteTimer][ID_RingCount] = ringCount
		conf[SCT_MinuteTimer][ID_DelayBetweenRings] = delayBetweenRings

	def getLastMinuteTimerDatas(self):
		from .addonConfig import (
			SCT_MinuteTimer, ID_LastDuration, ID_LastAnnounce, ID_LastDelayBeforeEndDuration)
		conf = self.addonConfig[SCT_MinuteTimer]
		return (
			conf[ID_LastDuration],
			conf[ID_LastAnnounce],
			conf[ID_LastDelayBeforeEndDuration])

	def saveLastMinuteTimerDatas(self, lastDatas):
		from .addonConfig import SCT_MinuteTimer, ID_LastDuration, ID_LastDelayBeforeEndDuration, ID_LastAnnounce
		(lastDuration, lastAnnounce, lastDelayBeforeEndDuration) = lastDatas
		conf = self.addonConfig
		conf[SCT_MinuteTimer][ID_LastDuration] = lastDuration
		conf[SCT_MinuteTimer][ID_LastAnnounce] = lastAnnounce
		conf[SCT_MinuteTimer][ID_LastDelayBeforeEndDuration] = lastDelayBeforeEndDuration

	def getPlaySoundOnErrorsOption(self):
		from .addonConfig import SCT_AdvancedOptions, ID_PlaySoundOnErrors
		conf = self.addonConfig
		return conf[SCT_AdvancedOptions][ID_PlaySoundOnErrors]

	def setPlaySoundOnErrorsOption(self, option):
		from .addonConfig import (
			SCT_AdvancedOptions, ID_PlaySoundOnErrors,
			PSOE_SnapshotVersions, PSOE_NoVersion, PSOE_AllVersions)
		conf = self.addonConfig
		if option in [PSOE_NoVersion, PSOE_AllVersions]:
			conf[SCT_AdvancedOptions][ID_PlaySoundOnErrors] = option
		else:
			conf[SCT_AdvancedOptions][ID_PlaySoundOnErrors] = PSOE_SnapshotVersions
		self.setIsTestVersionFlag(option)

	def getIsTestVersionFlag(self):
		return buildVersion.isTestVersion

	def setIsTestVersionFlag(self, option=None):
		from .addonConfig import PSOE_SnapshotVersions
		playSoundOnErrorsOption = self.getPlaySoundOnErrorsOption()if not option else option
		if playSoundOnErrorsOption == PSOE_SnapshotVersions:
			version = buildVersion.version
			buildVersion.isTestVersion = not version[0].isdigit()\
				or "alpha" in version or "beta" in version or "dev" in version
		else:
			buildVersion.isTestVersion = playSoundOnErrorsOption

	def getForceCloseOption(self):
		from .addonConfig import SCT_ShutdownComputer, ID_ForceClose
		conf = self.addonConfig
		return conf[SCT_ShutdownComputer][ID_ForceClose]

	def setForceCloseOption(self, forceClose):
		from .addonConfig import SCT_ShutdownComputer, ID_ForceClose
		conf = self.addonConfig
		conf[SCT_ShutdownComputer][ID_ForceClose] = forceClose

	def getdelayBeforeShutdownOrRestart(self):
		from .addonConfig import SCT_ShutdownComputer, ID_ShutdownTimeout
		conf = self.addonConfig
		return conf[SCT_ShutdownComputer][ID_ShutdownTimeout]

	def setDelayBeforeShutdownOrRestart(self, delay):
		from .addonConfig import SCT_ShutdownComputer, ID_ShutdownTimeout
		conf = self.addonConfig
		conf[SCT_ShutdownComputer][ID_ShutdownTimeout] = delay

	def getRemanenceAtNVDAStart(self):
		from .addonConfig import SCT_AdvancedOptions, ID_RemanenceAtNVDAStart
		conf = self.addonConfig
		return conf[SCT_AdvancedOptions][ID_RemanenceAtNVDAStart]

	def getRemanenceDelay(self):
		from .addonConfig import SCT_AdvancedOptions, ID_RemanenceDelay
		conf = self.addonConfig
		return conf[SCT_AdvancedOptions][ID_RemanenceDelay]

	def setRemanenceDelay(self, delay):
		from .addonConfig import SCT_AdvancedOptions, ID_RemanenceDelay
		conf = self.addonConfig
		conf[SCT_AdvancedOptions][ID_RemanenceDelay] = delay

	def getMinMasterVolumeLevel(self):
		from .addonConfig import SCT_AdvancedOptions, ID_MinMasterVolumeLevel
		return self.addonConfig[SCT_AdvancedOptions][ID_MinMasterVolumeLevel]

	def setMinMasterVolumeLevel(self, level):
		from .addonConfig import SCT_AdvancedOptions, ID_MinMasterVolumeLevel
		self.addonConfig[SCT_AdvancedOptions][ID_MinMasterVolumeLevel] = level

	def getMasterVolumeLevel(self):
		from .addonConfig import SCT_AdvancedOptions, ID_MasterVolumeLevel
		return self.addonConfig[SCT_AdvancedOptions][ID_MasterVolumeLevel]

	def setMasterVolumeLevel(self, level):
		from .addonConfig import SCT_AdvancedOptions, ID_MasterVolumeLevel
		self.addonConfig[SCT_AdvancedOptions][ID_MasterVolumeLevel] = level

	def getMinNVDAVolumeLevel(self):
		from .addonConfig import SCT_AdvancedOptions, ID_MinNVDAVolumeLevel
		return self.addonConfig[SCT_AdvancedOptions][ID_MinNVDAVolumeLevel]

	def setMinNVDAVolumeLevel(self, level):
		from .addonConfig import SCT_AdvancedOptions, ID_MinNVDAVolumeLevel
		self.addonConfig[SCT_AdvancedOptions][ID_MinNVDAVolumeLevel] = level

	def getNVDAVolumeLevel(self):
		from .addonConfig import SCT_AdvancedOptions, ID_NVDAVolumeLevel
		return self.addonConfig[SCT_AdvancedOptions][ID_NVDAVolumeLevel]

	def setNVDAVolumeLevel(self, level):
		from .addonConfig import SCT_AdvancedOptions, ID_NVDAVolumeLevel
		self.addonConfig[SCT_AdvancedOptions][ID_NVDAVolumeLevel] = level

	def getVolumeChangeStepLevel(self):
		from .addonConfig import SCT_AdvancedOptions, ID_VolumeChangeStepLevel
		return self.addonConfig[SCT_AdvancedOptions][ID_VolumeChangeStepLevel]

	def setVolumeChangeStepLevel(self, level):
		from .addonConfig import SCT_AdvancedOptions, ID_VolumeChangeStepLevel
		self.addonConfig[SCT_AdvancedOptions][ID_VolumeChangeStepLevel] = level

	def getMaximumDelayBetweenSameScript(self):
		from .addonConfig import SCT_AdvancedOptions, ID_MaximumDelayBetweenSameScript
		conf = self.addonConfig
		return int(conf[SCT_AdvancedOptions][ID_MaximumDelayBetweenSameScript])

	def setMaximumDelayBetweenSameScript(self, delay):
		from .addonConfig import SCT_AdvancedOptions, ID_MaximumDelayBetweenSameScript
		conf = self.addonConfig
		conf[SCT_AdvancedOptions][ID_MaximumDelayBetweenSameScript] = str(delay)

	def getReducedPathItemsNumber(self):
		from .addonConfig import SCT_AdvancedOptions, ID_ReducedPathItemsNumber
		conf = self.addonConfig
		return int(conf[SCT_AdvancedOptions][ID_ReducedPathItemsNumber])

	def setReducedPathItemsNumber(self, nb):
		from .addonConfig import SCT_AdvancedOptions, ID_ReducedPathItemsNumber
		conf = self.addonConfig
		conf[SCT_AdvancedOptions][ID_ReducedPathItemsNumber] = str(nb)

	def getConfirmAudioDeviceChangeTimeOut(self):
		from .addonConfig import SCT_AdvancedOptions, ID_ConfirmAudioDeviceChangeTimeOut
		conf = self.addonConfig
		return conf[SCT_AdvancedOptions][ID_ConfirmAudioDeviceChangeTimeOut]

	def setConfirmAudioDeviceChangeTimeOut(self, delay):
		from .addonConfig import SCT_AdvancedOptions, ID_ConfirmAudioDeviceChangeTimeOut
		conf = self.addonConfig
		conf[SCT_AdvancedOptions][ID_ConfirmAudioDeviceChangeTimeOut] = delay

	def getLastChecked(self):
		from .addonConfig import SCT_General, ID_LastChecked
		conf = self.addonConfig
		return conf[SCT_General][ID_LastChecked]

	def setLastChecked(self, lastTime):
		from .addonConfig import SCT_General, ID_LastChecked
		conf = self.addonConfig
		conf[SCT_General][ID_LastChecked] = int(lastTime)

	def getAudioDevicesForCycle(self):
		from .addonConfig import SCT_AudioDevicesForCycle
		conf = self.addonConfig
		if SCT_AudioDevicesForCycle not in conf:
			return []
		devices = list(conf[SCT_AudioDevicesForCycle].values())
		return devices

	def saveAudioDevicesForCycle(self, devicesForCycle):
		from .addonConfig import SCT_AudioDevicesForCycle
		conf = self.addonConfig
		d = {}
		if SCT_AudioDevicesForCycle in conf:
			d = conf[SCT_AudioDevicesForCycle]
		devices = list(d.values())
		for device, isChecked in devicesForCycle.items():
			if device in devices:
				if not isChecked:
					del devices[devices.index(device)]
				continue
			if isChecked:
				devices.append(device)
		conf[SCT_AudioDevicesForCycle] = {}
		for device in devices:
			index = devices.index(device) + 1
			conf[SCT_AudioDevicesForCycle][str(index)] = device

	def getReportingSpellingErrorsByOption(self):
		from .addonConfig import SCT_ReportingSpellingErrors, ID_ReportingBy
		conf = self.addonConfig[SCT_ReportingSpellingErrors]
		option = conf[ID_ReportingBy]
		return option

	def setReportingSpellingErrorsByOption(self, option):
		from .addonConfig import SCT_ReportingSpellingErrors, ID_ReportingBy
		conf = self.addonConfig[SCT_ReportingSpellingErrors]
		conf[ID_ReportingBy] = option

	def reportingSpellingErrorsByBeep(self, option=None):
		if option is None:
			option = self.getReportingSpellingErrorsByOption()
		return option == addonConfig.RSE_Beep

	def reportingSpellingErrorsBySound(self, option=None):
		if option is None:
			option = self.getReportingSpellingErrorsByOption()
		return option == addonConfig.RSE_Sound

	def reportingSpellingErrorsByMessage(self, option=None):
		if option is None:
			option = self.getReportingSpellingErrorsByOption()
		return option == addonConfig.RSE_Message

	def getKeyRepeatDelay(self):
		from .addonConfig import SCT_AdvancedOptions, ID_KeyRepeatDelay
		conf = self.addonConfig
		return int(conf[SCT_AdvancedOptions][ID_KeyRepeatDelay])

	def setKeyRepeatDelay(self, delay):
		from .addonConfig import SCT_AdvancedOptions, ID_KeyRepeatDelay
		conf = self.addonConfig
		conf[SCT_AdvancedOptions][ID_KeyRepeatDelay] = str(delay)

	def getTonalitiesVolumeLevel(self):
		from .addonConfig import SCT_AdvancedOptions, ID_TonalitiesVolumeLevel
		conf = self.addonConfig
		return conf[SCT_AdvancedOptions][ID_TonalitiesVolumeLevel]

	def setTonalitiesVolumeLevel(self, level):
		from .addonConfig import SCT_AdvancedOptions, ID_TonalitiesVolumeLevel
		conf = self.addonConfig
		conf[SCT_AdvancedOptions][ID_TonalitiesVolumeLevel] = int(level)


# singleton for add-on configuration manager
_addonConfigManager = AddonConfigurationManager()
