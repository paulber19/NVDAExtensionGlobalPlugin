# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2024 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

from logHandler import log


def initialize():
	log.debug("computerTools initialization")
	# for tonalities volume changes
	from ..settings import toggleAllowNVDATonesVolumeAdjustmentAdvancedOption
	if toggleAllowNVDATonesVolumeAdjustmentAdvancedOption(False):
		from . import tonesPatches
		tonesPatches.initialize()
	from . import temporaryOutputDevicePatches
	temporaryOutputDevicePatches.patche()
	from . import audioCore
	audioCore.initialize()
	"""
	try:
		# for nvda version > 2024.2
		splitAudioMode = config.conf["audio"]["soundSplitState"]
	except Exception:
		splitAudioMode = 0
	from ..settings import getInstallFeatureOption
	from ..settings.addonConfig import (
		C_DoNotInstall,
		FCT_SplitAudio
	)
	# if getInstallFeatureOption(FCT_SplitAudio) != C_DoNotInstall and  splitAudioMode:
		# from .messageDialogs import SplitAudioWarningDialog
		# from gui.message import  displayDialogAsModal
		# wx.CallAfter(displayDialogAsModal, SplitAudioWarningDialog(None))
	"""


def terminate():
	from . import audioCore
	audioCore.terminate()
	from . import tonesPatches
	tonesPatches.terminate()
	from . import temporaryOutputDevicePatches
	temporaryOutputDevicePatches.patche(install=False)
