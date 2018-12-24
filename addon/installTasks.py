# -*- coding: UTF-8 -*-
# installTasks.py
# a part of NVDAExtensionGlobalPLugin add-on
#Copyright (C) 2016-2017 Paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.


import os, sys, globalVars
from logHandler import log

_addonConfigFileName = "NVDAExtensionGlobalPluginAddon.ini"
def deleteAddonProfilesConfig():
	import config
	conf = config.conf
	addonName = "NVDAExtensionGlobalPlugin"
	if addonName in conf.profiles[0].keys():
		del conf.profiles[0][addonName]
		
	profileNames = []
	profileNames.extend(config.conf.listProfiles())
	for name in profileNames:
		profile = config.conf._getProfile(name)
		if profile.get("NVDAExtensionGlobalPlugin"):
			del profile["NVDAExtensionGlobalPlugin"]
			config.conf._dirtyProfiles.add(name)
	log.info("Addon profile configuration  cleared")

	
def onInstall():
	log.debug("OnInstall")
	import addonHandler
	addonHandler.initTranslation()
	import gui, wx,shutil
	#include the module directory to the path
	sys.path.append(os.path.dirname(__file__))
	from onInstall import checkWindowListAddonInstalled ,installNewSymbols
	checkWindowListAddonInstalled ()
	installNewSymbols()
	# save old configuration
	userConfigPath = globalVars.appArgs.configPath
	addonConfigFile = os.path.join(userConfigPath , _addonConfigFileName)
	if os.path.exists(addonConfigFile ):
		# existing previous addon config 
		if gui.messageBox(
			# Translators: the label of a message box dialog.
			_("Do you want to keep previous add-on configuration settings ?"),
			# Translators: the title of a message box dialog.
			_("NVDAExtensionGlobalPlugin add-on installation"),
			wx.YES|wx.NO|wx.ICON_WARNING)==wx.YES:
			dest = os.path.join(os.path.dirname(__file__).decode("mbcs"), _addonConfigFileName)
			try:
				shutil.copy(addonConfigFile, dest)
			except:
				log.error("Addon configuration cannot be saved: %s"%addonConfigFile)
				deleteAddonProfilesConfig()
		
		else:
			# user don't want to save configuration
			deleteAddonProfilesConfig()
		

		# in all cases, addon config file must deleted
		os.remove(addonConfigFile )
		if os.path.exists(addonConfigFile):
			log.error("Error on deletion of NVDAExtensionGlobalPlugin addon settings file: %s"%addonConfigFile)
	else:
		# no previous addon config, but try to clear nvda.ini file and profiles
		deleteAddonProfilesConfig()
	
	del sys.path[-1]
	


def onUninstall():
	log.debug("OnUnInstall")
		# delete current configuration file
	userConfigPath = globalVars.appArgs.configPath
	addonConfigFile = os.path.join(userConfigPath , _addonConfigFileName)
	if os.path.exists(addonConfigFile ):
		os.remove(addonConfigFile  )
		if os.path.exists(addonConfigFile ):
			log.error("Error on deletion of NVDAExtensionGlobalPlugin addon settings file: %s"%addonConfigFile)
		else:
			log.info("Addon configuration deleted: %s"%addonConfigFile )
	
