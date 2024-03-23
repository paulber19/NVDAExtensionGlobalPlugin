# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\bluetoothAudio.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2023-2024 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


import nvwave
import os
import struct
import wave


# part of this code comes from  the BluetoothAudio addon for NVDA
# Copyright (C) 2018 Tony Malykh


def generateBeepBuf(whiteNoiseVolume):
	path = os.path.abspath(__file__)
	dirPath = os.path.dirname(path)
	fileName = os.path.join(dirPath, "waves", "white_noise_10s.wav")
	f = wave.open(fileName, "r")
	if f is None:
		raise RuntimeError()
	buf = f.readframes(f.getnframes())
	bufSize = len(buf)
	n = bufSize // 2
	unpacked = struct.unpack(f"<{n}h", buf)
	unpacked = list(unpacked)
	for i in range(n):
		unpacked[i] = int(unpacked[i] * whiteNoiseVolume / 1000)
	packed = struct.pack(f"<{n}h", *unpacked)
	return packed, f.getframerate()


def playWhiteNoise(deviceName):
	buf, framerate = generateBeepBuf(1)
	player = nvwave.WavePlayer(
		channels=2, samplesPerSec=framerate, bitsPerSample=16, outputDevice=deviceName, wantDucking=False)
	player.feed(buf)
