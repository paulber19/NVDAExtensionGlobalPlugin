# -*- coding: UTF-8 -*-

import os.path

# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.


# Since some strings in "addon_info" are translatable,
# we need to include them in the .po files.
# Gettext recognizes only strings given as parameters to the "_" function.
# To avoid initializing translations in this module we simply roll our own "fake" "_" function
# which returns whatever is given to it as an argument.
def _(arg):
	return arg


# Add-on information variables
addon_info = {
	# add-on Name, internal for nvda
	"addon_name": "NVDAExtensionGlobalPlugin",
	# Add-on summary, usually the user visible name of the addon.
	# Translators: Summary for this add-on to be shown on installation
	# and add-on information.
	"addon_summary": _("NVDA global commands extension"),
	# Add-on description
	# Translators: Long description to be shown for this add-on on
	# add-on information from add-ons manager
	"addon_description": _("""This global add-on provides a multitude of features described in detail in its user manual (see the add-on's help for this)."""),


	# version
	"addon_version": "13.1.3",
	# Author(s)
	"addon_author": "PaulBer19 (paulber19@laposte.net",
	# URL for the add-on documentation support
	"addon_url": "https://github.com/paulber19/NVDAExtensionGlobalPlugin.git",
	# URL for the add-on repository where the source code can be found
	"addon_sourceURL": "https://github.com/paulber19/NVDAExtensionGlobalPlugin.git",
	# Documentation file name
	"addon_docFileName": "addonUserManual.html",
	# Minimum NVDA version supported (e.g. "2018.3")
	"addon_minimumNVDAVersion": "2022.1",
	# Last NVDA version supported/tested
	# (e.g. "2018.4", ideally more recent than minimum version)
	"addon_lastTestedNVDAVersion": "2023.2",
	# Add-on update channel (default is stable or None)
	"addon_updateChannel": None,
	# Add-on license such as GPL 2
	"addon_license": "GPL v2",
	# URL for the license document the ad-on is licensed under
	"addon_licenseURL": "https://www.gnu.org/licenses/gpl-2.0.html",
}

# Define the python files that are the sources of your add-on.
# You can use glob expressions here, they will be expanded.
mainPath = os.path.join("addon", "globalPlugins", "NVDAExtensionGlobalPlugin")
pythonSources = [
	os.path.join("addon", "*.py"),
	os.path.join(mainPath, "*.py"),
	os.path.join(mainPath, "activeWindowsListReport", "*.py"),
	os.path.join(mainPath, "browseModeEx", "*.py"),
	os.path.join(mainPath, "clipboardCommandAnnouncement", "*.py"),
	os.path.join(
		mainPath, "commandKeysSelectiveAnnouncementAndRemanence", "*.py"),
	os.path.join(mainPath, "ComplexSymbols", "*.py"),
	os.path.join(mainPath, "currentFolder", "*.py"),
	os.path.join(mainPath, "computerTools", "*.py"),
	os.path.join(mainPath, "extendedNetUIHWND", "*.py"),
	os.path.join(mainPath, "keyboardKeyRenaming", "*.py"),
	os.path.join(mainPath, "minuteTimer", "*.py"),
	os.path.join(mainPath, "NVDALogs", "*.py"),
	os.path.join(mainPath, "reportFormatting", "*.py"),
	os.path.join(mainPath, "scripts", "*.py"),
	os.path.join(mainPath, "settings", "*.py"),
	os.path.join(mainPath, "speechHistory", "*.py"),
	os.path.join(mainPath, "switchVoiceProfile", "*.py"),
	os.path.join(mainPath, "systemTrayIconsList", "*.py"),
	os.path.join(mainPath, "textAnalysis", "*.py"),
	os.path.join(mainPath, "tools", "*.py"),
	os.path.join(mainPath, "updateHandler", "*.py"),
	os.path.join(mainPath, "userInputGestures", "*.py"),
	os.path.join(mainPath, "utils", "*.py"),
	os.path.join(mainPath, "WindowsExplorer", "*.py"),
	os.path.join(mainPath, "winExplorer", "*.py"),
]


# Files that contain strings for translation. Usually your python sources
i18nSources = pythonSources

# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory,
# not to the root directory of your addon sources.
excludedFiles = []

# Base language for the NVDA add-on
# If your add-on is written in a language other than english,
# modify this variable.
# For example:
# set baseLanguage to "es" if your add-on is primarily written in spanish.
baseLanguage = "en"

# Markdown extensions for add-on documentation
# Most add-ons do not require additional Markdown extensions.
# If you need to add support for markup such as tables, fill out the below list.
# Extensions string must be of the form "markdown.extensions.extensionName"
# e.g. "markdown.extensions.tables" to add tables.
markdownExtensions = []
