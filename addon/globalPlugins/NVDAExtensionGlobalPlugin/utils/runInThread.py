# NVDAExtensionGlobalPlugin/runInThread.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2017 - 2020 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from logHandler import log
import tones
import threading
from .. import settings
import nvwave
import speech
from .py3Compatibility import reLoad
addonHandler.initTranslation()


class RepeatTask(threading.Thread):
	_delay = None
	_armed = False

	def __init__(self, isRunning=None):
		if self._delay is None:
			log.error("Cannot create repeatTask thread because delay is none")
			return
		self.isRunning = isRunning
		super(RepeatTask, self).__init__()
		self._stopevent = threading.Event()

	def task(self):
		# must be overwritten
		return

		tones.beep(400, 200)

	def run(self):
		if self._delay is None:
			log.error("Cannot start repeatTask thread because not delay")
			return
		while not self._stopevent.isSet():
			self._stopevent.wait(self._delay)
			if self.isRunning is not None and not self.isRunning():
				# interrupted before stop
				# Translators: message to user to report an interuption before stop.
				speech.speakMessage(_("interrupted"))
				break
			self.task()

	def stop(self):
		self._stopevent.set()


class RepeatBeep(RepeatTask):
	def __init__(self, delay=2.0, beep=(200, 200), isRunning=None):
		self._delay = delay
		self.beep = beep
		super(RepeatBeep, self).__init__(isRunning)

	def task(self):
		if self._stopevent.isSet():
			return
		(frequence, length) = self.beep
		tones.beep(frequence, length)


class RepeatbeepOnAudioDevices(RepeatTask):
	def __init__(self):
		self._delay = float(
			60*settings._addonConfigManager.getRepeatBeepOnAudioDevicesDelay())
		super(RepeatbeepOnAudioDevices, self).__init__()

	def task(self):
		from . import mytones
		from .__init__ import setAudioOutputDevice
		devices = nvwave.getOutputDeviceNames()
		if len(devices) == 0:
			return
		try:
			for dev in devices[1:]:
				setAudioOutputDevice(dev)
				reLoad(mytones)
				mytones.beep(200, 40)
		except:  # noqa:E722
			pass
		setAudioOutputDevice = None
		reLoad(mytones)
