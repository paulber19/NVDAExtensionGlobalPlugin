# globalPlugins\utilities\pycawEx\myPycawUtils.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2024 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

# patch of AudioUtilities pycaw class to get audio sources of a specific device

from logHandler import log
import comtypes
from versionInfo import version_year, version_major
NVDAVersion = [version_year, version_major]
if NVDAVersion >= [2024, 2]:
	# for nvda version >= 2024.2
	from pycaw.api.audiopolicy import IAudioSessionControl2, IAudioSessionManager2
	from pycaw.api.mmdeviceapi import IMMDeviceEnumerator
	from pycaw.constants import (
		DEVICE_STATE,
		CLSID_MMDeviceEnumerator,
		EDataFlow,
		ERole,
	)
	from pycaw.utils import AudioUtilities, AudioSession
else:
	# for nvda version <2024.2
	import sys
	import os
	sysPath = list(sys.path)
	if "pycaw" in sys.modules:
		log.warning("Potential incompatibility: pycaw module is also used and loaded probably by other add-on")
		del sys.modules["pycaw"]
	sys.path = [sys.path[0]]
	from ..utils.py3Compatibility import getCommonUtilitiesPath
	commonUtilitiesPath = getCommonUtilitiesPath()
	pycawPath = os.path.join(commonUtilitiesPath, "pycawEx")
	psutilPath = os.path.join(commonUtilitiesPath, "psutilEx")
	sys.path.append(commonUtilitiesPath)
	sys.path.append(psutilPath)
	sys.path.append(pycawPath)
	from pycawEx.pycaw.api.audiopolicy import IAudioSessionControl2, IAudioSessionManager2
	from pycawEx.pycaw.api.mmdeviceapi import IMMDeviceEnumerator
	from pycawEx.pycaw.constants import (
		DEVICE_STATE,
		CLSID_MMDeviceEnumerator,
		EDataFlow,
		ERole,
	)
	from pycawEx.pycaw.utils import AudioUtilities, AudioSession
	sys.path = sysPath


class MyAudioUtilities(AudioUtilities):

	@staticmethod
	def GetSpeakers(audioDeviceID=None):
		"""
		get the speakers (1st render + multimedia) device
		"""
		deviceEnumerator = comtypes.CoCreateInstance(
			CLSID_MMDeviceEnumerator,
			IMMDeviceEnumerator,
			comtypes.CLSCTX_INPROC_SERVER)
		if audioDeviceID is None:
			speakers = deviceEnumerator.GetDefaultAudioEndpoint(
				EDataFlow.eRender.value, ERole.eMultimedia.value)
		else:
			speakers = deviceEnumerator.GetDevice(audioDeviceID)
		return speakers

	@staticmethod
	def GetAudioSessionManager(audioDeviceID=None):
		speakers = MyAudioUtilities.GetSpeakers(audioDeviceID)
		if speakers is None:
			return None
		# win7+ only
		o = speakers.Activate(IAudioSessionManager2._iid_, comtypes.CLSCTX_ALL, None)
		mgr = o.QueryInterface(IAudioSessionManager2)
		return mgr

	@staticmethod
	def GetAllSessions(audioDeviceID=None):
		audio_sessions = []
		mgr = MyAudioUtilities.GetAudioSessionManager(audioDeviceID)
		if mgr is None:
			return audio_sessions
		sessionEnumerator = mgr.GetSessionEnumerator()
		count = sessionEnumerator.GetCount()
		for i in range(count):
			ctl = sessionEnumerator.GetSession(i)
			if ctl is None:
				continue
			ctl2 = ctl.QueryInterface(IAudioSessionControl2)
			if ctl2 is not None:
				audio_session = AudioSession(ctl2)
				audio_sessions.append(audio_session)
		return audio_sessions

	@staticmethod
	def GetAllDevices(flow=EDataFlow.eAll, state=DEVICE_STATE.MASK_ALL):
		devices = []
		deviceEnumerator = comtypes.CoCreateInstance(
			CLSID_MMDeviceEnumerator, IMMDeviceEnumerator, comtypes.CLSCTX_INPROC_SERVER
		)
		if deviceEnumerator is None:
			return devices

		collection = deviceEnumerator.EnumAudioEndpoints(
			flow.value, state.value
		)
		if collection is None:
			return devices

		count = collection.GetCount()
		for i in range(count):
			dev = collection.Item(i)
			if dev is not None:
				devices.append(MyAudioUtilities.CreateDevice(dev))
		return devices
