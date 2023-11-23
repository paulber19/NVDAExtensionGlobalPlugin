# globalPlugins\NVDAExtensionGlobalPlugin\utils\py3Compatibility.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright 2019 - 2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import os
import sys


def getCommonUtilitiesPath():
	curAddonPath = getAddonPath()
	return os.path.join(curAddonPath, "utilities")


def getUtilitiesPath():
	curAddonPath = getAddonPath()
	if sys.version .startswith("3.11"):
		utilities = "utilitiesPy311"
	else:
		utilities = "utilitiesPy37"
	return os.path.join(curAddonPath, utilities)


def getAddonPath(addon=None):
	if addon is None:
		addon = addonHandler.getCodeAddon()
	return addon.path
