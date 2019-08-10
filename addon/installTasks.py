# -*- coding: UTF-8 -*-
# installTasks.py
# a part of NVDAExtensionGlobalPLugin add-on
#Copyright (C) 2016-2017 Paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

from logHandler import log

curConfigFileName = "NVDAExtensionGlobalPluginAddon.ini"

def saveAddonProfilesConfig(addonName):
	import config
	conf = config.conf
	save = False
	if addonName in conf.profiles[0]:
		log.warning("saveAddonProfilesConfig profile[0]")
		conf.profiles[0]["%s-temp"%addonName] = conf.profiles[0][addonName].copy()
		del conf.profiles[0][addonName]
		save = True
	profileNames = []
	profileNames.extend(config.conf.listProfiles())
	for name in profileNames:
		profile = config.conf._getProfile(name)
		if profile.get(addonName):
			log.warning("saveAddonProfilesConfig: profile %s"%name)
			profile["%s-temp"%addonName] = profile[addonName].copy()
			del profile[addonName]
			config.conf._dirtyProfiles.add(name)
			save = True
			
	# We save the configuration,if changes
	if save:
		config.conf.save()

def deleteAddonProfilesConfig(addonName):
	import config
	conf = config.conf
	save = False
	if addonName in conf.profiles[0]:
		log.warning("%s section deleted from profile: normal configuration "%addonName)
		del conf.profiles[0][addonName]
		save = True
	profileNames = []
	profileNames.extend(config.conf.listProfiles())
	for name in profileNames:
		profile = config.conf._getProfile(name)
		if profile.get(addonName):
			log.warning("%s  section deleted from profile:%s "%(addonName, name))
			del profile[addonName]
			save = True
			config.conf._dirtyProfiles.add(name)
	# We save the configuration, in case the user would not have checked the "Save configuration on exit" checkbox in General settings.
	if save and config.conf['general']['saveConfigurationOnExit']:
		config.conf.save()
	
def onInstall():
	log.warning("OnInstall")
	import addonHandler
	addonHandler.initTranslation()
	import gui, wx,shutil
	import os, globalVars, sys
	#include the module directory to the path
	curPath = os.path.dirname(__file__).decode("mbcs")
	sys.path.append(curPath)
	import buildVars
	addonName = buildVars.addon_info["addon_name"]
	addonSummary = _(buildVars.addon_info["addon_summary"])
	from onInstall import checkWindowListAddonInstalled ,installNewSymbols
	del sys.path[-1]
	checkWindowListAddonInstalled ()
	installNewSymbols()
	# save old configuration if user wants it
	userConfigPath = globalVars.appArgs.configPath
	addonConfigFile = os.path.join(userConfigPath , curConfigFileName)
	if os.path.exists(addonConfigFile ):
		# existing previous addon config 
		if gui.messageBox(
			# Translators: the label of a message box dialog.
			_("Do you want to keep previous add-on configuration settings ?"),
			# Translators: the title of a message box dialog.
			_("%s - installation")%addonSummary,
			wx.YES|wx.NO|wx.ICON_WARNING)==wx.YES:
			dest = os.path.join(curPath, curConfigFileName)
			try:
				shutil.copy(addonConfigFile, dest)
				saveAddonProfilesConfig(addonName)
			except:
				log.error("Addon configuration cannot be saved: %s"%addonConfigFile)
				# clean up all add-on configuration
				deleteAddonProfilesConfig(addonName)
		else:
			# user don't want to save configuration
			# clean up all add-on configuration
			deleteAddonProfilesConfig(addonName)
		# in all cases, addon config file must deleted
		os.remove(addonConfigFile )
		if os.path.exists(addonConfigFile):
			log.error("Error on deletion of NVDAExtensionGlobalPlugin addon settings file: %s"%addonConfigFile)
	else:
		# no previous addon config, but try to clear nvda.ini file and profiles
		deleteAddonProfilesConfig(addonName)
	

def onUninstall():
	import os, globalVars, sys
	log.warning("OnUnInstall")
	#include the module directory to the path
	curPath = os.path.dirname(__file__).decode("mbcs")
	sys.path.append(curPath)
	import buildVars
	addonName = buildVars.addon_info["addon_name"]
	del sys.path[-1]
	deleteAddonProfilesConfig(addonName)
	# delete current configuration file
	userConfigPath = globalVars.appArgs.configPath
	addonConfigFile = os.path.join(userConfigPath , curConfigFileName)
	if os.path.exists(addonConfigFile ):
		os.remove(addonConfigFile  )
		if os.path.exists(addonConfigFile ):
			log.error("Error on deletion of NVDAExtensionGlobalPlugin addon settings file: %s"%addonConfigFile)
		else:
			log.info("Addon configuration deleted: %s"%addonConfigFile )
	
