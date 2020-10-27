# -*- coding: UTF-8 -*-

# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

# Full getext (please don't change)
def _(arg):
	return arg

# Add-on information variables
{addonInfoStart}
	# for previously unpublished addons,
	#	please follow the community guidelines at:
	# https://bitbucket.org/nvdaaddonteam/todo/raw/master/guideLines.txt
	# add-on Name, internal for nvda
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
