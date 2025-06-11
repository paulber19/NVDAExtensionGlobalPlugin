# globalPlugins\NVDAExtensionGlobalPlugin\__init__.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2024 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
import os
from logHandler import log


def shouldLoadNVDAExtensionGlobalPlugin():
	from versionInfo import version_year, version_major
	NVDAVersion = [version_year, version_major]
	if NVDAVersion < [2024, 3]:
		import sys
		from .utils.py3Compatibility import getCommonUtilitiesPath
		sysPath = list(sys.path)
		psutilModulePath = None
		if "psutil" in sys.modules:
			log.warning("Potential incompatibility: psutil module is also used and loaded probably by other add-on")
			psutilModulePath = sys.modules["psutil"]
			del sys.modules["psutil"]
		sys.path = [sys.path[0]]
		commonUtilitiesPath = getCommonUtilitiesPath()
		psutilPath = os.path.join(commonUtilitiesPath, "psutilEx")
		sys.path.append(commonUtilitiesPath)
		sys.path.append(psutilPath)
		import psutilEx as psutil
		sys.path = sysPath
		del sys.modules["psutilEx"]
		if psutilModulePath is not None:
			sys.modules["psutil"] = psutilModulePath
	else:
		import psutil

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
