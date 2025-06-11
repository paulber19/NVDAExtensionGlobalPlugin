# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\audioUtils.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2025 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import config
from ..utils.NVDAStrings import NVDAString
from versionInfo import version_year, version_major
NVDAVersion = [version_year, version_major]


def isWasapiUsed():
	# nvda 2025.1 and above use Wasapi
	if NVDAVersion >= [2025, 1]:
		return True

	# wasapi can be used since nvda 2023.2
	# by checking the advanced option: use wasapi for audio output
	try:
		from nvwave import WasapiWavePlayer, WavePlayer
		if WavePlayer == WasapiWavePlayer:
			return True
	except Exception:
		pass
	return False


def getOutputDevice():
	try:
		# for nvda version >=  2025.1
		return config.conf["audio"]["outputDevice"]
	except KeyError:
		# for nvda version < 2025.1
		return config.conf["speech"]["outputDevice"]


def setOutputDevice(device):
	if "outputDevice" in config.conf["audio"]:
		# for nvda version >= 2025.1
		config.conf["audio"]["outputDevice"] = device
	else:
		# for nvda version  < 2025.1
		config.conf["speech"]["outputDevice"] = device


def get_outputDevices():
	if NVDAVersion < [2025, 1]:
		from nvwave import _getOutputDevices
		devices = [(ID, name) for ID, name in _getOutputDevices()]
		deviceIds = [ID for ID, name in devices]
		deviceNames = [name for id, name in devices]
		# #11349: On Windows 10 20H1 and 20H2, Microsoft Sound Mapper returns an empty string.
		if deviceNames[0] in ("", "Microsoft Sound Mapper"):
			# Translators: name for default (Microsoft Sound Mapper) audio output device.
			deviceNames[0] = NVDAString("Microsoft Sound Mapper")
	else:
		from utils import mmdevice
		deviceIds, deviceNames = zip(*mmdevice.getOutputDevices(includeDefault=True))
	return deviceIds, deviceNames
