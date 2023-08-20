# globalPlugins\NVDAExtensionGlobalPlugin\__init__.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2023 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
import os


def shouldLoadNVDAExtensionGlobalPlugin():
	import sys
	from .utils.py3Compatibility import getUtilitiesPath
	utilitiesPath = getUtilitiesPath()
	sysPath = sys.path
	sys.path.append(utilitiesPath)
	import psutil
	sys.path = sysPath
	process = psutil.Process(os.getpid())
	if process.name() == "nvda.exe":
		return True
	return False


if shouldLoadNVDAExtensionGlobalPlugin():
	from .theGlobalPlugin import NVDAExtensionGlobalPlugin
else:
	from globalPluginHandler import GlobalPlugin as NVDAExtensionGlobalPlugin


class GlobalPlugin (NVDAExtensionGlobalPlugin):
	# ??? this definition is necessary.
	# if not, the method of the NVDAExtensionGlobalPlugin class is never called.
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		super(GlobalPlugin, self).chooseNVDAObjectOverlayClasses(obj, clsList)
