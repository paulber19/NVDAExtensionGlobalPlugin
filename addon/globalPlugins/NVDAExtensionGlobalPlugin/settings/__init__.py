# globalPlugins\NVDAExtensionGlobalPlugin\settings\__init__.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2021 Paulber19
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
# ConfigObj 5.1.0 and later integrates validate module.
try:
	from configobj.validate import Validator, VdtTypeError
except ImportError:
	from validate import Validator, VdtTypeError
from languageHandler import getLanguage
from .addonConfig import *  # noqa:F403

addonHandler.initTranslation()


def getInstallFeatureOption(featureID):
	if globalVars.appArgs.secure:
		noInstallList = [
			ID_SystrayIconsAndActiveWindowsList,
			ID_OpenCurrentOrOldNVDALogFile,
			ID_Tools,
			ID_ExploreNVDA,
		]
		if featureID in noInstallList:
			return C_DoNotInstall
	conf = _addonConfigManager.addonConfig
	state = conf[SCT_InstallFeatureOptions].get(featureID)
	if state is None:
		# by default, fonctionnality is installed
		state = C_Install
	return state


def setInstallFeatureOption(featureID, option):
	global _addonConfigManager
	conf = _addonConfigManager.addonConfig
	conf[SCT_InstallFeatureOptions][featureID] = option


def isInstall(featureID):
	option = getInstallFeatureOption(featureID)
	return False if option == C_DoNotInstall else True


def isInstallWithoutGesture(featureID):
	conf = _addonConfigManager.addonConfig
	option = conf[SCT_InstallFeatureOptions][featureID]
	return True if option == C_InstallWithoutGesture else False


def TOGGLE(sct, id, toggle):
	global _addonConfigManager
	conf = _addonConfigManager.addonConfig
	if toggle:
		conf[sct][id] = not conf[sct][id]
	return conf[sct][id]


def toggleGeneralOptions(id, toggle):
	sct = SCT_General
	return TOGGLE(sct, id, toggle)


def toggleAutoUpdateGeneralOptions(toggle=True):
	return toggleGeneralOptions(ID_AutoUpdate, toggle)


def toggleUpdateReleaseVersionsToDevVersionsGeneralOptions(toggle=True):
	return toggleGeneralOptions(ID_UpdateReleaseVersionsToDevVersions, toggle)


def toggleRemindUpdateGeneralOptions(toggle=True):
	return toggleGeneralOptions(ID_RemindUpdate, toggle)


def toggleOption(id, toggle):
	sct = SCT_Options
	return TOGGLE(sct, id, toggle)


def toggleReportNextWordOnDeletionOption(toggle=True):
	# bug fix in nvda 2020.3
	# so return always False if nvda version is equal or higher to this version
	import versionInfo
	NVDAVersion = [versionInfo.version_year, versionInfo.version_major]
	if NVDAVersion >= [2020, 3]:
		return False
	return toggleOption(ID_ReportNextWordOnDeletion, toggle)


def toggleNoDescriptionReportInRibbonOption(toggle=True):
	return toggleOption(ID_NoDescriptionReportInRibbon, toggle)


def toggleAutomaticWindowMaximizationOption(toggle=True):
	return toggleOption(ID_AutomaticWindowMaximization, toggle)


def toggleReportTimeWithSecondsOption(toggle=True):
	return toggleOption(ID_ReportTimeWithSeconds, toggle)


def toggleSpeechRecordWithNumberOption(toggle=True):
	return toggleOption(ID_SpeechRecordWithNumber, toggle)


def toggleSpeechRecordInAscendingOrderOption(toggle=True):
	return toggleOption(ID_SpeechRecordInAscendingOrder, toggle)


def toggleLoopInNavigationModeOption(toggle=True):
	return toggleOption(ID_LoopInNavigationMode, toggle)


def toggleAdvancedOption(id, toggle):
	sct = SCT_AdvancedOptions
	return TOGGLE(sct, id, toggle)


def toggleBeepAtRemanenceStartAdvancedOption(toggle=True):
	return toggleAdvancedOption(ID_BeepAtRemanenceStart, toggle)


def toggleBeepAtRemanenceEndAdvancedOption(toggle=True):
	return toggleAdvancedOption(ID_BeepAtRemanenceEnd, toggle)


def toggleSetOnMainAndNVDAVolumeAdvancedOption(toggle=True):
	return toggleAdvancedOption(ID_SetOnMainAndNVDAVolume, toggle)


def toggleReportVolumeChangeAdvancedOption(toggle=True):
	return toggleAdvancedOption(ID_ReportVolumeChange, toggle)


def toggleAppVolumeLevelAnnouncementInPercentAdvancedOption(toggle=True):
	return toggleAdvancedOption(ID_AppVolumeLevelAnnouncementInPercent, toggle)


def toggleDialogTitleWithAddonSummaryAdvancedOption(toggle=True):
	return toggleAdvancedOption(ID_DialogTitleWithAddonSummary, toggle)


def toggleByPassNoDescriptionAdvancedOption(toggle=True):
	return toggleAdvancedOption(ID_ByPassNoDescription, toggle)


def toggleOnlyNVDAKeyInRemanenceAdvancedOption(toggle=True):
	return toggleAdvancedOption(ID_OnlyNVDAKeyInRemanence, toggle)


def toggleRemanenceAtNVDAStartAdvancedOption(toggle=True):
	return toggleAdvancedOption(ID_RemanenceAtNVDAStart, toggle)


def toggleRemanenceForGmailAdvancedOption(toggle=True):
	return toggleAdvancedOption(ID_RemanenceForGmail, toggle)


def toggleEnableNumpadNavigationModeToggleAdvancedOption(toggle=True):
	return toggleAdvancedOption(ID_EnableNumpadNavigationModeToggle, toggle)


def toggleActivateNumpadNavigationModeAtStartAdvancedOption(toggle=True):
	return toggleAdvancedOption(ID_ActivateNumpadNavigationModeAtStart, toggle)


def toggleActivateNumpadStandardUseWithNumLockAdvancedOption(toggle=True):
	return toggleAdvancedOption(ID_ActivateNumpadStandardUseWithNumLock, toggle)


def toggleConfirmAudioDeviceChangeAdvancedOption(toggle=True):
	return toggleAdvancedOption(ID_ConfirmAudioDeviceChange, toggle)


class AddonConfigurationManager():
	_currentConfigVersion = "2.7"
	_configFileName = "NVDAExtensionGlobalPluginAddon.ini"
	_versionToConfiguration = {
		"2.0": AddonConfiguration20,
		"2.1": AddonConfiguration21,
		"2.2": AddonConfiguration22,
		"2.3": AddonConfiguration23,
		"2.4": AddonConfiguration24,
		"2.5": AddonConfiguration25,
		"2.6": AddonConfiguration26,
		"2.7": AddonConfiguration27,
		}

	def __init__(self):
		global _addonConfigManager
		self.curAddon = addonHandler.getCodeAddon()
		self.addonName = self.curAddon.manifest["name"]
		from keyLabels import localizedKeyLabels
		self.basicLocalizedKeyLabels = localizedKeyLabels.copy()
		self.restoreAddonProfilesConfig(self.addonName)
		self.loadSettings()
		self.setIsTestVersionFlag()
		config.post_configSave.register(self.handlePostConfigSave)

	def restoreAddonProfilesConfig(self, addonName):
		conf = config.conf
		save = False
		if "%s-temp" % addonName in conf.profiles[0]:
			log.warning("restoreAddonProfilesConfig profile[0]")
			conf.profiles[0][addonName] = conf.profiles[0]["%s-temp" % addonName].copy()  # noqa:E501
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

	def loadSettings(self):
		addonConfigFile = os.path.join(
			globalVars.appArgs.configPath, self._configFileName)
		doMerge = True
		if os.path.exists(addonConfigFile):
			# there is allready a config file
			baseConfig = BaseAddonConfiguration(addonConfigFile)
			if baseConfig[SCT_General][ID_ConfigVersion] != self._currentConfigVersion:
				# it's an old config, but old config file must not exist here.
				# Must be deleted
				os.remove(addonConfigFile)
				log.warning("NVDAExtensionGlobalPlugin: old config file removed: %s" % addonConfigFile)  # noqa:E501
			else:
				# it's the same version of config, so no merge
				doMerge = False
		if os.path.exists(addonConfigFile):
			self.addonConfig =\
				self._versionToConfiguration[self._currentConfigVersion](addonConfigFile)
			if self.addonConfig.errors != []:
				log.warning("Validator errors: %s" % self.addonConfig.errors)
				log.warning("Addon configuration file error: configuration reset to factory")  # noqa:E501
				os.remove(addonConfigFile)
				# Translators: A message informing the user that there are errors
				# in the configuration file.
				msg = _("""The configuration file of "%s" add-on contains errors. The add-on configuration has been reset to default configuration""") % self.curAddon.manifest["summary"]  # noqa:E501
				core.callLater(2000, ui.message, msg)
				# reset configuration to default
				self.addonConfig =\
					self._versionToConfiguration[self._currentConfigVersion](None)
				doMerge = False
		else:
			# no add-on configuration file found
			self.addonConfig =\
				self._versionToConfiguration[self._currentConfigVersion](None)
			# it's an add-on installation, set volume control parameters
			self.setDefaultVolumeControl()
		self.addonConfig.filename = addonConfigFile
		# merge step
		oldConfigFile = os.path.join(self.curAddon.path, self._configFileName)
		if os.path.exists(oldConfigFile):
			if doMerge:
				self.mergeSettings(oldConfigFile)
			os.remove(oldConfigFile)
		if not os.path.exists(addonConfigFile):
			self.saveSettings(True)

	def setDefaultVolumeControl(self):
		from ..computerTools.volumeControl import getSpeakerVolume, getNVDAVolume
		curVolume = getSpeakerVolume()
		if curVolume is None:
			return
		curVolume = int(curVolume * 100)
		if curVolume > 50:
			curVolume = 50
		curVolume = 10*int(curVolume/10)
		if curVolume == 0:
			curVolume = 10
		self.setMasterVolumeLevel(curVolume)
		if curVolume == 10:
			self.setMinMasterVolumeLevel(0)
		else:
			self.setMinMasterVolumeLevel(10)
		curNVDAVolume = getNVDAVolume()
		if curNVDAVolume is None:
			return
		r = [1.0, 0.975609779358, 0.853679358959, 0.609770953655, 0.365862578154, 0]
		newLevel = 50
		for x in r[:-1]:
			y = r[r.index(x)+1]
			if curNVDAVolume > y and curNVDAVolume <= x:
				break
			newLevel = newLevel - 10
		self.setNVDAVolumeLevel(newLevel)
		if newLevel == 10:
			self.setMinNVDAVolumeLevel(0)
		else:
			self.setMinNVDAVolumeLevel(10)

	def mergeSettings(self, oldConfigFile):
		log.warning("Merge settings with old configuration")
		baseConfig = BaseAddonConfiguration(oldConfigFile)
		version = baseConfig[SCT_General][ID_ConfigVersion]
		if version not in self._versionToConfiguration:
			log.warning("Configuration merge error: unknown configuration version")
			return
		oldConfig = self._versionToConfiguration[version](oldConfigFile)
		if oldConfig .errors != []:
			log.warning("Old Add-on configuration file error: merge aborted")
			core.callLater(
				1000,
				ui.message,
				# Translators: message to inform the user
				# than it's not possible to merge with old configuration because of error.
				_("""The old configuration file of "%s" add-on contains errors. It's not possible to keep previous configuration""") % self.curAddon.manifest["summary"])  # noqa:E501
			return
		for sect in self.addonConfig.sections:
			for k in self.addonConfig[sect]:
				if sect == SCT_General and k == ID_ConfigVersion:
					continue
				if sect in oldConfig.sections and k in oldConfig[sect]:
					if sect == SCT_InstallFeatureOptions:
						# option type is not more booleen but integer
						self.addonConfig[sect][k] = int(oldConfig[sect][k])
					else:
						self.addonConfig[sect][k] = oldConfig[sect][k]
		# others section
		for sect in [SCT_RedefinedKeyLabels, ]:
			if sect in oldConfig.sections:
				self.addonConfig[sect] = oldConfig[sect]

	def handlePostConfigSave(self):
		self.saveSettings(True)

	def saveSettings(self, force=False):
		# We never want to save config if runing securely
		if globalVars.appArgs.secure:
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
			log.warning("Could not save add-on configuration - probably read only file system")  # noqa:E501

	def resetConfiguration(self):
		from ..utils import makeAddonWindowTitle
		if gui.messageBox(
			# Translators: A message asking the user to confirm reset of configuration.
			_("The add-on configuration will be reset to factory values and NVDA will be restarted. Would you like to continue?"),  # noqa:E501
			makeAddonWindowTitle(_("Configuration reset")),
			wx.YES | wx.NO | wx.ICON_WARNING) == wx.NO:
			return
		addonConfigFile = os.path.join(
			globalVars.appArgs.configPath, self._configFileName)
		os.remove(addonConfigFile)
		self.addonConfig = self._versionToConfiguration[self._currentConfigVersion](None)  # noqa:E501
		self.saveSettings(True)
		from .nvdaConfig import _NVDAConfigManager

		_NVDAConfigManager.deleteConfiguration()
		queueHandler.queueFunction(queueHandler.eventQueue, core.restart)

	def terminate(self):
		log.warning("addonConfigManager terminate")
		self.saveSettings()
		config.post_configSave.unregister(self.handlePostConfigSave)

	def saveRedefinedKeyLabels(self, keyLabels):
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
		lang = getLanguage().split("-")[0]
		conf = self.addonConfig
		if SCT_CategoriesAndSymbols in conf\
			and lang in conf[SCT_CategoriesAndSymbols]:
			return conf[SCT_CategoriesAndSymbols][lang].copy()
		return {}

	def saveUserComplexSymbols(self, userComplexSymbols):
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
		conf = self.addonConfig
		if SCT_CategoriesAndSymbols in conf:
			del conf[SCT_CategoriesAndSymbols]
		from .nvdaConfig import _NVDAConfigManager
		_NVDAConfigManager.deleceAllLastUserComplexSymbols()

	def getMaximumOfLastUsedSymbols(self):
		conf = self.addonConfig
		return int(conf[SCT_AdvancedOptions][ID_MaximumOfLastUsedSymbols])

	def setMaximumOfLastUsedSymbols(self, max):
		conf = self.addonConfig
		conf[SCT_AdvancedOptions][ID_MaximumOfLastUsedSymbols] = str(max)

	# minute timer feature
	def getMinuteTimerOptions(self):
		conf = self.addonConfig
		return (
			conf[SCT_MinuteTimer][ID_RingCount],
			conf[SCT_MinuteTimer][ID_DelayBetweenRings])

	def saveMinuteTimerOptions(self, options):
		(ringCount, delayBetweenRings) = options
		conf = self.addonConfig
		conf[SCT_MinuteTimer][ID_RingCount] = ringCount
		conf[SCT_MinuteTimer][ID_DelayBetweenRings] = delayBetweenRings

	def getLastMinuteTimerDatas(self):
		conf = self.addonConfig[SCT_MinuteTimer]
		return (
			conf[ID_LastDuration],
			conf[ID_LastAnnounce],
			conf[ID_LastDelayBeforeEndDuration])

	def saveLastMinuteTimerDatas(self, lastDatas):
		(lastDuration, lastAnnounce, lastDelayBeforeEndDuration) = lastDatas
		conf = self.addonConfig
		conf[SCT_MinuteTimer][ID_LastDuration] = lastDuration
		conf[SCT_MinuteTimer][ID_LastAnnounce] = lastAnnounce
		conf[SCT_MinuteTimer][ID_LastDelayBeforeEndDuration] = lastDelayBeforeEndDuration  # noqa:E501

	def getPlaySoundOnErrorsOption(self):
		conf = self.addonConfig
		return conf[SCT_AdvancedOptions][ID_PlaySoundOnErrors]

	def setPlaySoundOnErrorsOption(self, option):
		conf = self.addonConfig
		if option in [PSOE_NoVersion, PSOE_AllVersions]:
			conf[SCT_AdvancedOptions][ID_PlaySoundOnErrors] = option
		else:
			conf[SCT_AdvancedOptions][ID_PlaySoundOnErrors] = PSOE_SnapshotVersions
		self.setIsTestVersionFlag(option)

	def getIsTestVersionFlag(self):
		return buildVersion.isTestVersion

	def setIsTestVersionFlag(self, option=None):
		playSoundOnErrorsOption = self.getPlaySoundOnErrorsOption()if not option else option  # noqa:E501
		if playSoundOnErrorsOption == PSOE_SnapshotVersions:
			version = buildVersion.version
			buildVersion.isTestVersion = not version[0].isdigit()\
				or "alpha" in version or "beta" in version or "dev" in version
		else:
			buildVersion.isTestVersion = playSoundOnErrorsOption

	def getForceCloseOption(self):
		conf = self.addonConfig
		return conf[SCT_ShutdownComputer][ID_ForceClose]

	def setForceCloseOption(self, forceClose):
		conf = self.addonConfig
		conf[SCT_ShutdownComputer][ID_ForceClose] = forceClose

	def getdelayBeforeShutdownOrRestart(self):
		conf = self.addonConfig
		return conf[SCT_ShutdownComputer][ID_ShutdownTimeout]

	def setDelayBeforeShutdownOrRestart(self, delay):
		conf = self.addonConfig
		conf[SCT_ShutdownComputer][ID_ShutdownTimeout] = delay

	def getRemanenceAtNVDAStart(self):
		conf = self.addonConfig
		return conf[SCT_AdvancedOptions][ID_RemanenceAtNVDAStart]

	def getRemanenceDelay(self):
		conf = self.addonConfig
		return conf[SCT_AdvancedOptions][ID_RemanenceDelay]

	def setRemanenceDelay(self, delay):
		conf = self.addonConfig
		conf[SCT_AdvancedOptions][ID_RemanenceDelay] = delay

	def getMinMasterVolumeLevel(self):
		return self.addonConfig[SCT_AdvancedOptions][ID_MinMasterVolumeLevel]

	def setMinMasterVolumeLevel(self, level):
		self.addonConfig[SCT_AdvancedOptions][ID_MinMasterVolumeLevel] = level

	def getMasterVolumeLevel(self):
		return self.addonConfig[SCT_AdvancedOptions][ID_MasterVolumeLevel]

	def setMasterVolumeLevel(self, level):
		self.addonConfig[SCT_AdvancedOptions][ID_MasterVolumeLevel] = level

	def getMinNVDAVolumeLevel(self):
		return self.addonConfig[SCT_AdvancedOptions][ID_MinNVDAVolumeLevel]

	def setMinNVDAVolumeLevel(self, level):
		self.addonConfig[SCT_AdvancedOptions][ID_MinNVDAVolumeLevel] = level

	def getNVDAVolumeLevel(self):
		return self.addonConfig[SCT_AdvancedOptions][ID_NVDAVolumeLevel]

	def setNVDAVolumeLevel(self, level):
		self.addonConfig[SCT_AdvancedOptions][ID_NVDAVolumeLevel] = level

	def getVolumeChangeStepLevel(self):
		return self.addonConfig[SCT_AdvancedOptions][ID_VolumeChangeStepLevel]

	def setVolumeChangeStepLevel(self, level):
		self.addonConfig[SCT_AdvancedOptions][ID_VolumeChangeStepLevel] = level

	def getMaximumDelayBetweenSameScript(self):
		conf = self.addonConfig
		return int(conf[SCT_AdvancedOptions][ID_MaximumDelayBetweenSameScript])

	def setMaximumDelayBetweenSameScript(self, delay):
		conf = self.addonConfig
		conf[SCT_AdvancedOptions][ID_MaximumDelayBetweenSameScript] = str(delay)

	def getConfirmAudioDeviceChangeTimeOut(self):
		conf = self.addonConfig
		return conf[SCT_AdvancedOptions][ID_ConfirmAudioDeviceChangeTimeOut]

	def setConfirmAudioDeviceChangeTimeOut(self, delay):
		conf = self.addonConfig
		conf[SCT_AdvancedOptions][ID_ConfirmAudioDeviceChangeTimeOut] = delay

	def getLastChecked(self):
		conf = self.addonConfig
		return conf[SCT_General][ID_LastChecked]

	def setLastChecked(self, lastTime):
		conf = self.addonConfig
		conf[SCT_General][ID_LastChecked] = int(lastTime)

	def getAudioDevicesForCycle(self):
		conf = self.addonConfig
		if SCT_AudioDevicesForCycle not in conf:
			return []
		devices = list(conf[SCT_AudioDevicesForCycle].values())
		return devices

	def saveAudioDevicesForCycle(self, devicesForCycle):
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
			index = devices.index(device)+1
			conf[SCT_AudioDevicesForCycle][str(index)] = device


# singleton for add-on configuration manager
_addonConfigManager = AddonConfigurationManager()
