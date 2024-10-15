# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2024 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


def initialize():
	# for tonalities volume changes
	from ..settings import toggleAllowNVDATonesVolumeAdjustmentAdvancedOption
	if toggleAllowNVDATonesVolumeAdjustmentAdvancedOption(False):
		from . import tonesPatches
		tonesPatches.initialize()
	from . import temporaryOutputDevicePatches
	temporaryOutputDevicePatches.patche()
	from . import audioCore
	audioCore.initialize()


def terminate():
	from . import audioCore
	audioCore.terminate()
	from . import tonesPatches
	tonesPatches.terminate()
	from . import temporaryOutputDevicePatches
	temporaryOutputDevicePatches.patche(install=False)
