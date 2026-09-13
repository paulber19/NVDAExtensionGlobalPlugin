# -*- coding: UTF-8 -*-
# installTasks.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2026 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

from logHandler import log
import os
import sys
import globalVars
import config
import api
import addonHandler

addonHandler.initTranslation()

PREVIOUSCONFIGURATIONFILE_SUFFIX = ".prev"
DELETECONFIGURATIONFILE_SUFFIX = ".delete"


def getAddonName():
	curModuleFilePath = os.path.dirname(__file__)
	manifestPath = os.path.join(curModuleFilePath, addonHandler.MANIFEST_FILENAME)
	if not os.path.exists(manifestPath):
		log.warning("There is not manifest.ini for this module")
		return None
	with open(manifestPath) as f:
		manifest = addonHandler.AddonManifest(f)
		addonName = manifest.get("name")
	return addonName


def renameFile(file, dest):
	log.debug("renaming file:  %s to %s" % (file, dest))
	try:
		if os.path.exists(dest):
			os.remove(dest)
		os.rename(file, dest)
		log.debug("current configuration file: %s renamed to : %s" % (file, dest))
	except Exception:
		log.error("current configuration file: %s  cannot be renamed to: %s" % (file, dest))


def saveCurAddonConfigurationProfiles(addonName):
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
		try:
			profile = config.conf._getProfile(name)
		except Exception:
			continue
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
	conf = config.conf
	save = False
	if addonName in conf.profiles[0]:
		log.warning("%s section deleted from profile: normal configuration " % addonName)  # noqa:E501
		del conf.profiles[0][addonName]
		save = True
	profileNames = []
	profileNames.extend(config.conf.listProfiles())
	for name in profileNames:
		try:
			profile = config.conf._getProfile(name)
		except Exception:
			continue
		if profile.get(addonName):
			log.warning("%s section deleted from profile: %s" % (addonName, name))
			del profile[addonName]
			save = True
			config.conf._dirtyProfiles.add(name)
	# We save the configuration, in case the user would not have checked
	# the "Save configuration on exit" checkbox in General settings.
	if save:
		config.conf.save()
	# delete "spelling error announcement" profil if exist
	name = _("Spelling errors' announcement")
	name = api.filterFileName(name)
	fn = config.conf._getProfileFn(name)
	if os.path.isfile(fn):
		os.remove(fn)


def keepPreviousSettingsConfirmation(addonSummary):
	curPath = os.path.dirname(__file__)
	sharedPath = os.path.join(curPath, "shared")
	sys.path.append(curPath)
	sys.path.append(sharedPath)
	from negp_messages import confirm_YesNo, ReturnCode
	del sys.path[-1]
	del sys.path[-1]

	if confirm_YesNo(
		# Translators: the label of a message box dialog.
		_("Do you want to keep current add-on configuration settings ?"),
		# Translators: the title of a message box dialog.
		_("%s - installation") % addonSummary,
	) == ReturnCode.YES or confirm_YesNo(
		# Translators: the label of a message box dialog.
		_("Are you sure you don't want to keep the current add-on configuration settings?"),
		# Translators: the title of a message box dialog.
		_("%s - installation") % addonSummary,
	) != ReturnCode.YES:
		return True
	return False


def onInstall():
	curPath = os.path.dirname(__file__)
	sys.path.append(curPath)
	from onInstall import checkWindowListAddonInstalled
	del sys.path[-1]
	addon = addonHandler._availableAddons[curPath]
	addonName = addon.manifest["name"]
	addonSummary = addon.manifest["summary"]
	checkWindowListAddonInstalled()
	# save old configuration if user wants it
	userConfigPath = globalVars.appArgs.configPath
	curConfigFileName = "%sAddon.ini" % addonName
	addonConfigFile = os.path.join(userConfigPath, curConfigFileName)
	if os.path.exists(addonConfigFile):
		# existing current addon config
		extraAppArgs = globalVars.appArgsExtra if hasattr(globalVars, "appArgsExtra") else globalVars.unknownAppArgs
		# this configuration is automatically preserved during an automatic update
		keep = True if "addon-auto-update" in extraAppArgs else False
		if keep or keepPreviousSettingsConfirmation(addonSummary):
			dest = addonConfigFile + PREVIOUSCONFIGURATIONFILE_SUFFIX
			renameFile(addonConfigFile, dest)
			saveCurAddonConfigurationProfiles(addonName)
		else:
			log.debug("user don't want to keep configuration")
			# add-on configuration should not be kept
			dest = addonConfigFile + DELETECONFIGURATIONFILE_SUFFIX
			renameFile(addonConfigFile, dest)
	# in all cases, clean up all add-on configuration
	deleteAddonProfilesConfig(addonName)


def onUninstall():
	addonName = getAddonName()
	if not addonName:
		log.debug("no addon name in the manifest")
		return
	deleteAddonProfilesConfig(addonName)
	# delete current configuration file
	userConfigPath = globalVars.appArgs.configPath
	curConfigFileName = "%sAddon.ini" % addonName
	addonConfigFile = os.path.join(userConfigPath, curConfigFileName)
	if os.path.exists(addonConfigFile):
		os.remove(addonConfigFile)
		if os.path.exists(addonConfigFile):
			log.error("Error on deletion of  addon settings file: %s" % addonConfigFile)  # noqa:E501
		else:
			log.info("Addon configuration deleted: %s" % addonConfigFile)
