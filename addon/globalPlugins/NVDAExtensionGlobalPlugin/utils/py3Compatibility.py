# globalPlugins\NVDAExtensionGlobalPlugin\utils\py3Compatibility.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright 2019 - 2025 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import os


def getCommonUtilitiesPath():
	curAddonPath = getAddonPath()
	return os.path.join(curAddonPath, "utilities")


def getAddonPath(addon=None):
	if addon is None:
		addon = addonHandler.getCodeAddon()
	return addon.path
