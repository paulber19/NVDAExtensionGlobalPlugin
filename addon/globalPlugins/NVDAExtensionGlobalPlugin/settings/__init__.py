#NVDAExtensionGlobalPlugin/settings/__init__.py
# a part of NVDAExtensionGlobalPlugin add-on
#Copyright (C) 2016-2017Paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.


#Manages configuration.
import addonHandler
addonHandler.initTranslation()
import os
import core
import sys
from cStringIO import StringIO
from configobj import ConfigObj
from validate import Validator
from logHandler import log
import globalVars
from addonConfig import *
import config
import gui
import wx
import buildVersion
import speech


def getInstallFeatureOption (featureID):
	conf = _addonConfigManager.addonConfig
	return conf[SCT_InstallFeatureOptions][featureID]

def setInstallFeatureOption (featureID, option):
	global _addonConfigManager
	conf = _addonConfigManager.addonConfig
	conf[SCT_InstallFeatureOptions][featureID]= option

def isInstall(featureID):
	conf = _addonConfigManager.addonConfig
	option = conf[SCT_InstallFeatureOptions][featureID]
	return False if option == C_DoNotInstall else True
	
def isInstallWithoutGesture(featureID):
	conf = _addonConfigManager.addonConfig
	option = conf[SCT_InstallFeatureOptions][featureID]
	return True if option == C_InstallWithoutGesture else False
def toggleOption (id, toggle = True):
	global _addonConfigManager
	conf = _addonConfigManager.addonConfig
	sct = SCT_Options
	if toggle:
		conf[sct][id] = not conf[sct][id]
		_addonConfigManager.saveSettings()
	return conf[sct][id]
	


def toggleReportNextWordOnDeletionOption (toggle = True):
	return toggleOption(ID_ReportNextWordOnDeletion   , toggle)
def toggleNoDescriptionReportInRibbonOption (toggle = True):
	return toggleOption(ID_NoDescriptionReportInRibbon, toggle)
def toggleAutomaticWindowMaximizationOption (toggle = True):
	return toggleOption(ID_AutomaticWindowMaximization,toggle)
def toggleReportTimeWithSecondsOption (toggle = True):
	return toggleOption(ID_ReportTimeWithSeconds, toggle)

def toggleSpeechRecordWithNumberOption (toggle = True):
	return toggleOption(ID_SpeechRecordWithNumber, toggle)
def toggleLoopInNavigationModeOption (toggle = True):
	return toggleOption(ID_LoopInNavigationMode, toggle)
def toggleAdvancedOption (id, toggle = True):
	global _addonConfigManager
	conf = _addonConfigManager.addonConfig
	sct = SCT_AdvancedOptions
	if toggle:
		conf[sct][id] = not conf[sct][id]
		_addonConfigManager.saveSettings()
	return conf[sct][id]
	


def toggleBeepAtRemanenceStartAdvancedOption (toggle = True):
	return toggleAdvancedOption(ID_BeepAtRemanenceStart,toggle)
def toggleBeepAtRemanenceEndAdvancedOption (toggle = True):
	return toggleAdvancedOption(ID_BeepAtRemanenceEnd,toggle)
def toggleSetOnMainAndNVDAVolumeAdvancedOption (toggle = True):
	return toggleAdvancedOption(ID_SetOnMainAndNVDAVolume,toggle)
def toggleDialogTitleWithAddonSummaryAdvancedOption (toggle = True):
	return toggleAdvancedOption(ID_DialogTitleWithAddonSummary,toggle)

def toggleByPassNoDescriptionAdvancedOption (toggle = True):
	return toggleAdvancedOption(ID_ByPassNoDescription,toggle)	
class AddonConfigurationManager():
	_currentConfigVersion = "2.3"
	_configFileName = "NVDAExtensionGlobalPluginAddon.ini"
	_versionToConfiguration = {
		"1.9" : AddonConfiguration19,
		"2.0" : AddonConfiguration20,
		"2.1" : AddonConfiguration21,
		"2.2" : AddonConfiguration22,
		"2.3" : AddonConfiguration23,
		}
	def __init__(self, ) :
		global _addonConfigManager
		self.curAddon = addonHandler.getCodeAddon()
		self.addonName = self.curAddon.manifest["name"]
		from keyLabels import localizedKeyLabels
		self.basicLocalizedKeyLabels = localizedKeyLabels.copy()
		self.loadSettings()
		self.setIsTestVersionFlag()
	
	def loadSettings(self):
		addonConfigFile = os.path.join(globalVars.appArgs.configPath, self._configFileName)
		doMerge = True
		if os.path.exists(addonConfigFile):
			#  there is allready a config file
			baseConfig = BaseAddonConfiguration(addonConfigFile)
			if baseConfig[SCT_General][ID_ConfigVersion] != self._currentConfigVersion :
				# it's an old config, but  old config file must not exist here. Must be deleted
				os.remove(addonConfigFile)
				log.warning ("NVDAExtensionGlobalPlugin: old config file removed")
			else:
				# it's the same version of config, so no merge
				doMerge = False
		self.addonConfig = self._versionToConfiguration[self._currentConfigVersion](addonConfigFile)
		if self.addonConfig.errors != []:
			log.warning("Addon configuration file error: configuration reset to factory")
			core.callLater(2000, speech.speakMessage,
			# Translators: A message informing the user that there are errors in the configuration file.
			_("The configuration file of %s addon contains errors. The addon configuration has been reset to default configuration")%self.curAddon.manifest["summary"])
			os.remove(addonConfigFile)
			# reset configuration to default
			self.addonConfig = self._versionToConfiguration[self._currentConfigVersion](None)
			self.addonConfig.filename = addonConfigFile
			doMerge= False
		if not os.path.exists(addonConfigFile):
			# it's an addon installation, set volume control parameters
			self.setDefaultVolumeControl()
			
		# merge step
		oldConfigFile = os.path.join(self.curAddon.path, self._configFileName)
		if os.path.exists(oldConfigFile):
			if doMerge:
				self.mergeSettings(oldConfigFile)
			os.remove(oldConfigFile)
		
		#create or update config file
		self.saveSettings()
	
	def setDefaultVolumeControl(self):
		from ..volumeControl import getSpeakerVolume, getNVDAVolume
		curVolume = int(getSpeakerVolume()*100)
		if curVolume is None:
			return
		if curVolume >50: curVolume = 50
		curVolume = 10*int(curVolume/10)
		if curVolume == 0: curVolume = 10
		self.setMasterVolumeLevel(curVolume)
		if curVolume == 10:
			self.setMinMasterVolumeLevel(0)
		else:
			self.setMinMasterVolumeLevel(10)
		curNVDAVolume = getNVDAVolume()
		if curNVDAVolume is None:
			return
		r = [1.0, 0.975609779358,  0.853679358959, 0.609770953655, 0.365862578154, 0]
		newLevel = 50
		for x in r[:-1]:
			y = r[r.index(x)+1]
			if curNVDAVolume >y and curNVDAVolume <= x:
				break
			newLevel = newLevel -10
		self.setNVDAVolumeLevel(newLevel)
		if newLevel == 10:
			self.setMinNVDAVolumeLevel(0)
		else:
			self.setMinNVDAVolumeLevel(10)
			
	def mergeSettings(self, oldConfigFile):
		log.warning("Merge settings with old configuration")
		baseConfig = BaseAddonConfiguration(oldConfigFile)
		version = baseConfig[SCT_General][ID_ConfigVersion]
		if version not in self._versionToConfiguration.keys():
			log.warning("Configuration merge error: unknown configuration version") 
			return
			
		oldConfig = self._versionToConfiguration[version](oldConfigFile)
		if oldConfig .errors != []:
			log.warning("Old Addon configuration file error: merge aborted")
			core.callLater(1000, speech.speakMessage,
				# Translators:  message to inform the user  than it's not possible to merge with old configuration because of error.
				_("The old configuration file of %s addon contains errors. It's not possible to keep previous configuration")%self.curAddon.manifest["summary"])
			return
		
		for sect in self.addonConfig.sections:
			for k in self.addonConfig[sect].keys():
				if sect == SCT_General and k == ID_ConfigVersion:
					continue
				if sect in oldConfig.sections  and k in oldConfig[sect].keys():
					if  sect == SCT_InstallFeatureOptions :
						# option type is not more booleen but integer
						self.addonConfig[sect][k] = int(oldConfig[sect][k])
					else:
						self.addonConfig[sect][k] = oldConfig[sect][k]
		# others section
		for sect in[SCT_RedefinedKeyLabels, ]: 
			if sect in oldConfig.sections:
				self.addonConfig[sect] = oldConfig[sect]

		self.saveSettings()
	def saveSettings(self):
		#We never want to save config if runing securely
		if globalVars.appArgs.secure: return
		if self.addonConfig  is None: return
		try:
			val = Validator()
			self.addonConfig.validate(val, copy = True)
			self.addonConfig.write()
		
		except Exception, e:
			log.warning("Could not save configuration - probably read only file system")
			raise e
	
	def terminate(self):
		self.saveSettings()



	def saveRedefinedKeyLabels(self, keyLabels):
		from languageHandler import curLang
		lang = curLang.split("-")[0]
		conf = self.addonConfig
		if SCT_RedefinedKeyNames not in conf.keys():
			conf[SCT_RedefinedKeyLabels] = {}
		elif lang  in conf[SCT_RedefinedKeyLabels].keys():
			del conf[SCT_RedefinedKeyLabels][lang] 
		conf[SCT_RedefinedKeyLabels][lang]  = {}
		for keyName in keyLabels.keys():
			conf[SCT_RedefinedKeyLabels][lang] [keyName] = keyLabels[keyName]
		self.saveSettings()
			

		
	def getRedefinedKeyLabels(self):
		from languageHandler import curLang
		lang = curLang.split("-")[0]
		conf = self.addonConfig
		if SCT_RedefinedKeyLabels in conf.keys() and lang in conf[SCT_RedefinedKeyLabels]:
			labels = conf[SCT_RedefinedKeyLabels][lang].copy()
			if len(labels):
				return labels
		return {}
	def saveCommandKeysSelectiveAnnouncement(self, keysDic,speakCommandKeysOption):
		conf = config.conf
		addonName = self.addonName
		if addonName not in conf:
			conf[addonName] = {}
		sectName = ID_SpeakCommandKeysMode if  speakCommandKeysOption else ID_DoNotSpeakCommandKeysMode
		if SCT_CommandKeysAnnouncement not in conf[addonName]:
			conf[addonName][SCT_CommandKeysAnnouncement] = {}
		
		conf[addonName][SCT_CommandKeysAnnouncement][sectName] = keysDic.copy()
		self.saveSettings()
		
	def getCommandKeysSelectiveAnnouncement (self, speakCommandKeysOption):
		conf = config.conf
		if self.addonName not in conf:
			return {}
		addonName = self.addonName
		sectName =  ID_SpeakCommandKeysMode if speakCommandKeysOption else ID_DoNotSpeakCommandKeysMode
		if SCT_CommandKeysAnnouncement in conf[addonName] and sectName in conf[addonName][SCT_CommandKeysAnnouncement]:
			return conf[addonName][SCT_CommandKeysAnnouncement][sectName].copy()
		
		return {}
	
	def reDefineKeyboardKeyLabels(self):
		from keyLabels import localizedKeyLabels 
		localizedKeyLabels.clear()			
		for key in self.basicLocalizedKeyLabels.keys():
			localizedKeyLabels[key] = self.basicLocalizedKeyLabels[key]

		labels = self.getRedefinedKeyLabels()
		for  key in labels.keys():
			if key in localizedKeyLabels .keys():
				localizedKeyLabels [key] = labels[key]
			else:
				# error, it's not a good key
				log.error("error in RedefinedKeyLabels section: bad key %s" %key)

	def getBasicLocalizedKeyLabels(self):
		return self.basicLocalizedKeyLabels
		
	def getUserComplexSymbols(self):
		from languageHandler import curLang
		lang = curLang.split("-")[0]
		conf = self.addonConfig
		if SCT_CategoriesAndSymbols in conf.keys() and lang in conf[SCT_CategoriesAndSymbols]:
			return  conf[SCT_CategoriesAndSymbols][lang].copy()
		return {}
	def saveUserComplexSymbols(self, userComplexSymbols):
		from languageHandler import curLang
		lang = curLang.split("-")[0]
		conf = self.addonConfig
		if SCT_CategoriesAndSymbols not in conf.keys():
			conf[SCT_CategoriesAndSymbols] = {}
		conf[SCT_CategoriesAndSymbols][lang] = {}
		for sect in userComplexSymbols.keys():
			if sect not in conf[SCT_CategoriesAndSymbols][lang]:
				conf[SCT_CategoriesAndSymbols][lang][sect] = {}
			for symbol in userComplexSymbols[sect].keys():
				conf[SCT_CategoriesAndSymbols	][lang][sect][symbol] = userComplexSymbols[sect][symbol]
		
		conf.write()
	def getMinuteTimerOptions(self):
			conf = self.addonConfig
			return (conf[SCT_MinuteTimer][ID_RingCount], conf[SCT_MinuteTimer][ID_DelayBetweenRings])
	def saveMinuteTimerOptions(self, options):
		(ringCount, delayBetweenRings) = options
		conf = self.addonConfig
		conf[SCT_MinuteTimer][ID_RingCount] = ringCount
		conf[SCT_MinuteTimer][ID_DelayBetweenRings] = delayBetweenRings
		self.saveSettings()
	def getLastMinuteTimerDatas(self):
			conf = self.addonConfig
			return (conf[SCT_MinuteTimer][ID_LastDuration], conf[SCT_MinuteTimer][ID_LastAnnounce], conf[SCT_MinuteTimer][ID_LastDelayBeforeEndDuration])
	def saveLastMinuteTimerDatas(self, lastDatas):
		(lastDuration, lastAnnounce, lastDelayBeforeEndDuration) = lastDatas
		conf = self.addonConfig
		conf[SCT_MinuteTimer][ID_LastDuration] = lastDuration
		conf[SCT_MinuteTimer][ID_LastAnnounce] = lastAnnounce
		conf[SCT_MinuteTimer][ID_LastDelayBeforeEndDuration] = lastDelayBeforeEndDuration
		self.saveSettings()
	def saveSymbolLevelOnWordCaretMovement(self, level):
		conf = config.conf
		if self.addonName not in conf:
			conf[self.addonName] = {}
		
		if SCT_Options  not in conf[self.addonName]:
			conf[self.addonName][SCT_Options] = {}
		
		conf[self.addonName][SCT_Options][ID_SymbolLevelOnWordCaretMovement] = str(level) if level is not None else "None"
		self.saveSettings()
	
	def getSymbolLevelOnWordCaretMovement(self):
		conf = config.conf
		if (self.addonName  in conf
			and SCT_Options in conf[self.addonName  ]
			and ID_SymbolLevelOnWordCaretMovement in conf[self.addonName][SCT_Options]):
			level = conf[self.addonName][SCT_Options][ID_SymbolLevelOnWordCaretMovement]
			if level != "None":
				return int(level) 
		
		return None
	def getPlaySoundOnErrorsOption (self):
		conf = self.addonConfig
		return conf[SCT_AdvancedOptions][ID_PlaySoundOnErrors]
	def setPlaySoundOnErrorsOption (self, option):
		conf = self.addonConfig
		if option in [PSOE_NoVersion, PSOE_AllVersions]:
			conf[SCT_AdvancedOptions][ID_PlaySoundOnErrors] = option
		else:
			conf[SCT_AdvancedOptions][ID_PlaySoundOnErrors] = PSOE_SnapshotVersions
		self.saveSettings()
		self.setIsTestVersionFlag(option)
	
	def getIsTestVersionFlag(self):
		return buildVersion.isTestVersion
		
	def setIsTestVersionFlag(self, option = None):
		playSoundOnErrorsOption = self.getPlaySoundOnErrorsOption()if not option else option
		if playSoundOnErrorsOption == PSOE_SnapshotVersions:
			version = buildVersion.version
			buildVersion.isTestVersion = not version[0].isdigit() or "alpha" in version or "beta" in version or "dev" in version
		else:
			buildVersion.isTestVersion = playSoundOnErrorsOption
	
	def updateVoiceProfileSwitchingConfig(self):
		conf = config.conf
		update = True
		if self.addonName in conf and SCT_VoiceProfileSwitching in conf[self.addonName] :
			# no update
			update = False
		if self.addonName not in conf:
			conf[self.addonName] = {}
			conf[self.addonName][SCT_VoiceProfileSwitching] = {}
		
		if SCT_OldVoiceProfileSwitching in conf :
			c = conf[SCT_OldVoiceProfileSwitching]._getUpdateSection()
			if len(c.keys()):
				if update:
					for key,val in c.items():
						conf[self.addonName][SCT_VoiceProfileSwitching][key] = val
				# delete if possible
				conf[SCT_OldVoiceProfileSwitching] = {}
				conf[SCT_OldVoiceProfileSwitching] ._cache.clear()
				#del conf[SCT_OldVoiceProfileSwitching]# don't work


	
	def getVoiceProfileSwitching(self):
		conf = config.conf
		if self.addonName not in conf:
			conf[self.addonName] = {}
		if SCT_VoiceProfileSwitching not in conf[self.addonName]:
			conf[self.addonName][SCT_VoiceProfileSwitching] = {}
		return conf[self.addonName][SCT_VoiceProfileSwitching]._getUpdateSection()
	
		
	def isVoiceProfileSelectorSet(self, selector):
		conf = config.conf[self.addonName][SCT_VoiceProfileSwitching]
		if (selector not in conf
			or "voiceProfileName"  not in conf[selector]):
			return False
		return True

	def getLastVoiceProfileSelector(self):
		conf = config.conf[self.addonName][SCT_VoiceProfileSwitching]
		if conf.isSet(ID_LastSelector):
			return conf[ID_LastSelector]
		return "1"
	
	def setLastVoiceProfileSelector(self, selector):
		conf = config.conf[self.addonName][SCT_VoiceProfileSwitching]
		conf[ID_LastSelector] =selector
	
	def freeVoiceProfileSelector(self, selector):
		if self.isVoiceProfileSelectorSet(selector):
			config.conf[self.addonName][SCT_VoiceProfileSwitching][selector] = {}
			config.conf[self.addonName][SCT_VoiceProfileSwitching]._cache.clear()
	def freeAllVoiceProfileSelectors(self):
		config.conf[self.addonName][SCT_VoiceProfileSwitching] = {}
		config.conf[self.addonName][SCT_VoiceProfileSwitching]._cache.clear()
		
	def setVoiceProfile(self, selector, profile):
		conf = config.conf
		if self.addonName not in conf:
			conf[self.addonName] = {}
		if SCT_VoiceProfileSwitching not in conf[self.addonName]:
			conf[self.addonName][SCT_VoiceProfileSwitching] = {}
		if selector not in conf[self.addonName][SCT_VoiceProfileSwitching]:
			conf[self.addonName][SCT_VoiceProfileSwitching][selector] = {}
		for key, val in profile.items():
			conf[self.addonName][SCT_VoiceProfileSwitching][selector][key] = val
	
	def getVoiceProfile(self, selector):

		if self.isVoiceProfileSelectorSet(selector):
			return config.conf[self.addonName][SCT_VoiceProfileSwitching][selector].copy()
		return {}
	def getForceCloseOption(self):
		conf = self.addonConfig
		return conf[SCT_ShutdownComputer][ID_ForceClose]
	def setForceCloseOption(self, forceClose):
		conf = self.addonConfig
		conf[SCT_ShutdownComputer][ID_ForceClose] = forceClose
	def getdelayBeforeShutdownOrRestart(self):
		conf = self.addonConfig
		return conf[SCT_ShutdownComputer][ID_ShutdownTimeout ] 
	def setDelayBeforeShutdownOrRestart(self, delay):
		conf = self.addonConfig
		conf[SCT_ShutdownComputer][ID_ShutdownTimeout ] = delay
		

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
	def getLastUsedSymbolsSection(self, profileName):
		if profileName is None:
			sct= SCT_LastUsedSymbols 
		else:
			sct= "%s-pro" %SCT_LastUsedSymbols 
		return sct
			
	def saveLastUsedSymbols(self, symbolsList) :
		conf = config.conf
		addonName = self.addonName
		if addonName not in conf:
			conf[addonName] = {}
		profileName = config.conf.profiles[-1].name
		sct = self.getLastUsedSymbolsSection(profileName)
		if sct not in conf[addonName]:
			conf[addonName][sct] = {}
		d = {}
		i= 1
		for (desc, symb) in symbolsList:
			d[str(i)] = "%s %s"%(symb, desc)
			i = i+1
		conf[addonName][sct]= d.copy()
		conf[addonName][sct]._cache.clear()
		
	
	def getLastUsedSymbols(self):

		conf = config.conf
		addonName = self.addonName
		profileName = config.conf.profiles[-1].name
		sct = self.getLastUsedSymbolsSection(profileName)
		if addonName not in conf or sct not in conf[addonName]:
			return []
		d = conf[addonName][sct].copy()
		if len(d)== 0:
			return []
		symbols = []
		for i in range(1, len(d.keys())+1):
			s = d[str(i)]
			sym = s[0]
			desc = s[2:]
			symbols.append((desc, sym))
		maximumOfLastUsedSymbols = self.getMaximumOfLastUsedSymbols()
		# check if number of symbols recorded is not  higher than maximum because of config change
		if len(symbols) > maximumOfLastUsedSymbols:
			# adjust the list
			symbols = symbols[len(symbols) - maximumOfLastUsedSymbols:]
			self.saveLastUsedSymbols(symbols)
		return symbols
		
	def updateLastSymbolsList(self, symbolDescription, symbol):
		symbols = self.getLastUsedSymbols()
		for (desc, symb) in symbols:
			if desc == symbolDescription:
				if symbol ==symb:
					# already in list
					return
				else:
					# replace description and symbol
					index = symbols.index((desc, symb))
					symbols[index] = (symbolDescription, symbol)
					self.saveLastUsedSymbols(symbols)
					return
		maximumOfLastUsedSymbols = self.getMaximumOfLastUsedSymbols()
		if len(symbols) > maximumOfLastUsedSymbols:
			# pop the oldest
			symbols.pop(0)
		symbols.append((symbolDescription, symbol))
		self.saveLastUsedSymbols(symbols)
	def cleanLastUsedSymbolsList(self):
		profileName = config.conf.profiles[-1].name
		self.saveLastUsedSymbols([])
	
	def getDelayBetweenSameGesture(self):
		conf = self.addonConfig
		return int(conf[SCT_AdvancedOptions][ID_DelayBetweenSameGesture] )

	def setDelayBetweenSameGesture(self, delay):
		conf = self.addonConfig
		conf[SCT_AdvancedOptions][ID_DelayBetweenSameGesture]  = str(delay)
	def getMaximumOfLastUsedSymbols(self):
		conf = self.addonConfig
		return int(conf[SCT_AdvancedOptions][ID_MaximumOfLastUsedSymbols] )
	def setMaximumOfLastUsedSymbols(self, max):
		conf = self.addonConfig
		conf[SCT_AdvancedOptions][ID_MaximumOfLastUsedSymbols] = str(max)

# singleton for addon configuration manager
_addonConfigManager = AddonConfigurationManager()