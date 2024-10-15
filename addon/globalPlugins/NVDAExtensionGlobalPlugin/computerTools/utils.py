# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\utils.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2024 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


def isWasapiUsed():
	# wasapi can be used since nvda 2023.2
	# by checking the advanced option: use wasapi for audio output
	try:
		from nvwave import WasapiWavePlayer, WavePlayer
		if WavePlayer == WasapiWavePlayer:
			return True
	except Exception:
		pass
	return False
