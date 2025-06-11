# globalPlugins\NVDAExtensionGlobalPlugin\speech\commands.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2024 paulber19
# This file is covered by the GNU General Public License.

import addonHandler
# from logHandler import log
import time
import speech.commands

addonHandler.initTranslation()


class BeepWithPauseCommand(speech.commands.BaseCallbackCommand):
	"""Produce a beep followed by a pause."""

	def __init__(self, hz, length, left=50, right=50):
		self.hz = hz
		self.length = length
		self.left = left
		self.right = right

	def run(self):
		import tones

		tones.beep(
			self.hz,
			self.length,
			left=self.left,
			right=self.right,
			isSpeechBeepCommand=True,
		)
		time.sleep(2 * self.length / 1000)

	def __repr__(self):
		return "BeepCommand({hz}, {length}, left={left}, right={right})".format(
			hz=self.hz,
			length=self.length,
			left=self.left,
			right=self.right,
		)
