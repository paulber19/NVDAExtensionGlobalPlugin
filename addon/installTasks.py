# -*- coding: UTF-8 -*-
# installTasks.py
# a part of NVDAExtensionGlobalPLugin add-on
# Copyright (C) 2016 - 2020 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

from logHandler import log


_addonName = "NVDAExtensionGlobalPlugin"
curConfigFileName = "%sAddon.ini" % _addonName


def saveCurAddonConfigurationProfiles(addonName):
	import config
	conf = config.conf
	save = False
	if addonName in conf.profiles[0]:
		log.warning("saveCurAddonConfigurationProfiles profile[0]")
		conf.profiles[0]["%s-temp" % addonName] = conf.profiles[0][addonName].copy()
		del conf.profiles[0][addonName]
		save = True
	profileNames = []
	profileNames.extend(config.conf.listProfiles())
	for name in profileNames:
		profile = config.conf._getProfile(name)
		if profile.get(addonName):
			log.warning("saveCurAddonConfigurationProfiles: profile %s" % name)
			profile["%s-temp" % addonName] = profile[addonName].copy()
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
		log.warning("%s section deleted from profile: normal configuration " % addonName)  # noqa:E501
		del conf.profiles[0][addonName]
		save = True
	profileNames = []
	profileNames.extend(config.conf.listProfiles())
	for name in profileNames:
		profile = config.conf._getProfile(name)
		if profile.get(addonName):
			log.warning("%s section deleted from profile: %s" % (addonName, name))
			del profile[addonName]
			save = True
			config.conf._dirtyProfiles.add(name)
	# We save the configuration, in case the user would not have checked
	# the "Save configuration on exit" checkbox in General settings.
	if save:
		config.conf.save()


def onInstall():
	import addonHandler
	addonHandler.initTranslation()
	import gui
	import wx
	import os
	import shutil
	import globalVars
	import sys
	curPath = os.path.dirname(__file__)
	sys.path.append(curPath)
	from onInstall import checkWindowListAddonInstalled, installNewSymbols
	del sys.path[-1]
	from addonHandler import _availableAddons
	addon = _availableAddons[curPath]
	addonName = addon.manifest["name"]
	addonSummary = addon.manifest["summary"]
	checkWindowListAddonInstalled()
	installNewSymbols()
	# save old configuration if user wants it
	userConfigPath = globalVars.appArgs.configPath
	addonConfigFile = os.path.join(userConfigPath, curConfigFileName)
	if os.path.exists(addonConfigFile):
		# existing previous addon config
		if gui.messageBox(
			# Translators: the label of a message box dialog.
			_("Do you want to keep previous add-on configuration settings?"),
			# Translators: the title of a message box dialog.
			_("%s - installation") % addonSummary,
			wx.YES | wx.NO | wx.ICON_WARNING) == wx.YES:
			dest = os.path.join(curPath, curConfigFileName)
			try:
				shutil.copy(addonConfigFile, dest)
				saveCurAddonConfigurationProfiles(addonName)
			except:  # noqa:E722
				log.error("Addon configuration cannot be saved: %s" % addonConfigFile)

		os.remove(addonConfigFile)
		if os.path.exists(addonConfigFile):
			log.error("Error on deletion of addon settings file: %s" % addonConfigFile)  # noqa:E501
	# in all cases, clean up all add-on configuration
	deleteAddonProfilesConfig(addonName)

def getUserConfigParentFolder():
	import os
	import globalVars
	userConfigPath = globalVars.appArgs.configPath 
	return os.path.split(userConfigPath)[0]


def onUninstall():
	import os
	import globalVars
	import sys
	# include the module directory to the path
	curPath = os.path.dirname(__file__)
	sys.path.append(curPath)
	import buildVars
	addonName = buildVars.addon_info["addon_name"]
	del sys.path[-1]
	deleteAddonProfilesConfig(addonName)
	# delete current configuration file
	userConfigPath = globalVars.appArgs.configPath
	addonConfigFile = os.path.join(userConfigPath, curConfigFileName)
	if os.path.exists(addonConfigFile):
		os.remove(addonConfigFile)
		if os.path.exists(addonConfigFile):
			log.error("Error on deletion of  addon settings file: %s" % addonConfigFile)  # noqa:E501
		else:
			log.info("Addon configuration deleted: %s" % addonConfigFile)
	path = os.path.join(getUserConfigParentFolder(), "%s-userConfigs.ini" % addonName)
	if os.path.exists(path):
		os.remove(path)
		if os.path.exists(path):
			log.error("%s Error: userConfigs file cannot be deleted: %s" % (_addonName,path))  # noqa:E501
		else:
			log.info("%s-userConfigs.ini  file has been deleted: %s" % (_addonName,path))
