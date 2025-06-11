# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\tonesPatches.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2024-2025 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


from logHandler import log
import tones
from .beep import myBeep

# global variable to save nvda patched method
_NVDATonesBeep = None


def initialize():
	from .audioUtils import isWasapiUsed
	if isWasapiUsed():
		return
	# patche tones.beep
	global _NVDATonesBeep
	if _NVDATonesBeep is not None:
		return
	_NVDATonesBeep = tones.beep
	if tones.beep.__module__ != "tones":
		log.warning(
			"Incompatibility: tones.beep method has also been patched probably by another add-on: %s. "
			"There is a risk of malfunction" % tones.beep.__module__)
	tones.beep = myBeep
	log.debug(
		"To allow NVDA tones volume adjustment, tones.beep function has been patched by %s function of %s module"
		% (tones.beep .__name__, tones.beep .__module__))


def terminate():
	global _NVDATonesBeep
	if _NVDATonesBeep is not None:
		tones.beep = _NVDATonesBeep
		_NVDATonesBeep = None
