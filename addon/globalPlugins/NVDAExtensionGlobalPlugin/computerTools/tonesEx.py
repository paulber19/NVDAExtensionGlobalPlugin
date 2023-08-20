# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\tonesEx.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


from logHandler import log
import tones
from ctypes import create_string_buffer

_NVDABeep = None


def initialize():
	global _NVDABeep, _nvdaBeepCommand
	from ..settings import toggleAllowNVDATonesVolumeAdjustmentAdvancedOption
	if not toggleAllowNVDATonesVolumeAdjustmentAdvancedOption(False):
		return
	if tones.beep.__module__ != "tones":
		log.warning(
			"Incompatibility: beep function of tones module has been also patched probably by another add-on: %s. "
			"There is a risk of malfunction" % tones.beep.__module__)
	if _NVDABeep is None:
		_NVDABeep = tones.beep
		tones.beep = myBeep
		log.debug(
			"tones.beep function has been patched to allow NVDA tones volume adjustment by %s function of %s module"
			% (tones.beep .__name__, tones.beep .__module__))


def terminate():
	global _NVDABeep
	if _NVDABeep:
		tones.beep = _NVDABeep
		_NVDABeep = None


def myBeep(
	hz: float,
	length: int,
	left: int = None,
	right: int = None,
	isSpeechBeepCommand: bool = False
):
	"""Plays a tone at the given hz, length, and stereo balance.
	@param hz: pitch in hz of the tone
	@param length: length of the tone in ms
	@param left: volume of the left channel (0 to 100)
	@param right: volume of the right channel (0 to 100)
	@param isSpeechBeepCommand: whether this beep is created as part of a speech sequence
	"""
	from ..settings import _addonConfigManager
	tonalitiesVolumeLevel = _addonConfigManager.getTonalitiesVolumeLevel()
	if left is None:
		left = tonalitiesVolumeLevel
	if right is None:
		right = tonalitiesVolumeLevel
	log.io("Beep at pitch %s, for %s ms, left volume %s, right volume %s" % (hz, length, left, right))
	try:
		# for nvda >= 2023.1
		if not tones.decide_beep.decide(
			hz=hz,
			length=length,
			left=left,
			right=right,
			isSpeechBeepCommand=isSpeechBeepCommand
		):
			log.debug(
				"Beep canceled by handler registered to decide_beep extension point"
			)
			return
	except Exception:
		pass
	if not tones.player:
		return
	from NVDAHelper import generateBeep
	bufSize = generateBeep(None, hz, length, left, right)
	buf = create_string_buffer(bufSize)
	generateBeep(buf, hz, length, left, right)
	tones.player.stop()
	tones.player.feed(buf.raw)
