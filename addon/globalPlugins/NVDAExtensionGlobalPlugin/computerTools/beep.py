# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\tonesEx.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2023-2024 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


from logHandler import log
import tones
import time
import nvwave
from ctypes import create_string_buffer

# temporary wave player
_player = None


def getPlayer(outputDevice):
	global _player
	if outputDevice is None:
		return tones.player
	try:
		_player = nvwave.WavePlayer(
			channels=2,
			samplesPerSec=int(tones.SAMPLE_RATE),
			bitsPerSample=16,
			outputDevice=outputDevice,
			wantDucking=False
		)
	except Exception:
		log.warning("Failed to initialize audio for tones", exc_info=True)
		_player = None
	return _player


def myBeep(
	hz: float,
	length: int,
	left: int = None,
	right: int = None,
	isSpeechBeepCommand: bool = False,
	device=None
):
	"""Plays a tone at the given hz, length, and stereo balance.
	@param hz: pitch in hz of the tone
	@param length: length of the tone in ms
	@param left: volume of the left channel (0 to 100)
	@param right: volume of the right channel (0 to 100)
	@param isSpeechBeepCommand: whether this beep is created as part of a speech sequence
	@device: audio output device
	"""
	from ..settings import _addonConfigManager
	tonalitiesVolumeLevel = _addonConfigManager.getTonalitiesVolumeLevel()
	if left is None:
		left = tonalitiesVolumeLevel
	if right is None:
		right = tonalitiesVolumeLevel
	log.io("Beep at pitch %s, for %s ms, left volume %s, right volume %s" % (hz, length, left, right))

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

	global _player
	_player = getPlayer(device)
	if not _player:
		return
	from NVDAHelper import generateBeep
	bufSize = generateBeep(None, hz, length, left, right)
	buf = create_string_buffer(bufSize)
	generateBeep(buf, hz, length, left, right)
	_player.stop()
	_player.feed(buf.raw)


from versionInfo import version_year, version_major
NVDAVersion = [version_year, version_major]


def playTonesOnDevice(outputDevice):
	outputDeviceName, outputDeviceId = outputDevice
	log.debug("playTonesOnDevice: %s" % outputDeviceName)
	device = outputDeviceName if NVDAVersion < [2025, 1] else outputDeviceId
	myBeep(hz=250, length=100, device=device)
	time.sleep(0.3)
	myBeep(hz=350, length=100, device=device)
