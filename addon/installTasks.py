# -*- coding: UTF-8 -*-
# installTasks.py
# a part of NVDAExtensionGlobalPLugin add-on
#Copyright (C) 2016-2017 Paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

from logHandler import log

curConfigFileName = "NVDAExtensionGlobalPluginAddon.ini"

def deleteAddonProfilesConfig(addonName):
	import config
	conf = config.conf
	if addonName in conf.profiles[0]:
		del conf.profiles[0][addonName]
	profileNames = []
	profileNames.extend(config.conf.listProfiles())
	for name in profileNames:
		profile = config.conf._getProfile(name)
		if profile.get(addonName):
			del profile[addonName]
			config.conf._dirtyProfiles.add(name)
	log.info("%s: Addon profile configuration  cleared"%addonName)
	# We save the configuration, in case the user would not have checked the "Save configuration on exit" checkbox in General settings.
	if config.conf['general']['saveConfigurationOnExit']:
		config.conf.save()
	
def onInstall():
	log.debug("OnInstall")
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
	log.debug("OnUnInstall")
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
	
