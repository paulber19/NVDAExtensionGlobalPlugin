# -*- coding: UTF-8 -*-

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
{addonInfoStart}
	# add-on Name/identifier, internal for NVDA
	"addon_name": "{name}",
	# Add-on summary, usually the user visible name of the addon.
	# Translators: Summary for this add-on to be shown
	# on installation and add-on information.
	"addon_summary": _("{summary}"),
	# Add-on description
	# Translators: Long description to be shown for this add-on
	# on add-on information from add-ons manager
	"addon_description": _("""{description}"""),
	# version
	"addon_version": "{version}",
	# Author(s)
	"addon_author": u"{author}",
	# URL for the add-on documentation support
	"addon_url": "{url}",
	# Documentation file name
	"addon_docFileName": "{docFileName}",
	# Minimum NVDA version supported (e.g. "2018.3")
	"addon_minimumNVDAVersion": "{minimumNVDAVersion}",
	# Last NVDA version supported/tested
	# (e.g. "2018.4", ideally more recent than minimum version)
	"addon_lastTestedNVDAVersion": "{lastTestedNVDAVersion}",
	# Add-on update channel (default is stable or None)
	"addon_updateChannel": "{updateChannel}",
{addonInfoEnd}

# Define the python files that are the sources of your add-on.
# You can use glob expressions here, they will be expanded.
pythonSources = []

# Files that contain strings for translation. Usually your python sources
i18nSources = pythonSources

# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory,
# not to the root directory of your addon sources.
excludedFiles = []

# If your add-on is written in a language other than english,
# modify this variable.
# For example:
# set baseLanguage to "es" if your add-on is primarily written in spanish.
baseLanguage = "en"