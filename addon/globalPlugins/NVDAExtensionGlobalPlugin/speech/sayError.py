# globalPlugins\NVDAExtensionGlobalPlugin\speech\sayError.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2024 paulber19
# This file is covered by the GNU General Public License.

import addonHandler
# from logHandler import log
import api
import os
import globalVars
import speech
import config
from .commands import BeepWithPauseCommand

addonHandler.initTranslation()


class SayErrorProfileTrigger(config.ProfileTrigger):
	spec = "sayError"


def getErrorSoundSpeechSequence(error=None):
	from speech.commands import WaveFileCommand
	fileName = os.path.join(globalVars.appDir, "waves", "textError.wav")
	seq = [
		speech.commands.EndUtteranceCommand(),
		WaveFileCommand(fileName),
		speech.commands.EndUtteranceCommand()
	]
	if error is not None:
		seq.extend([
			error,
			speech.commands.EndUtteranceCommand(),
		])
	return seq


def getErrorBeepSpeechSequence(error=None):
	seq = [
		speech.commands.EndUtteranceCommand(),
		BeepWithPauseCommand(150, 50),
		speech.commands.EndUtteranceCommand(),
		BeepWithPauseCommand(150, 50),
		speech.commands.EndUtteranceCommand(),
	]
	if error is not None and error != "" and not error.isspace():
		seq.extend([
			error,
			speech.commands.EndUtteranceCommand(),
		])
	return seq


def getErrorVoiceSpeechSequence(error=None):
	if error is None:
		return []
	t1 = SayErrorProfileTrigger()
	return [
		speech.commands.ConfigProfileTriggerCommand(t1, True),
		error,
		speech.commands.ConfigProfileTriggerCommand(t1, False),
	]


def getErrorSpeechSequence(error=None, reading=False):
	from ..settings import _addonConfigManager
	if _addonConfigManager.reportingSpellingErrorsByErrorReporting(reading=reading):
		return getErrorVoiceSpeechSequence(error)
	elif _addonConfigManager.reportingSpellingErrorsByBeep(reading=reading):
		return getErrorBeepSpeechSequence(error)
	elif _addonConfigManager.reportingSpellingErrorsBySound(reading=reading):
		return getErrorSoundSpeechSequence(error)
	elif error is not None:
		return [error]
	return None


def initialize():
	# Translators: name of say error profile
	name = _("Spelling errors' announcement")
	name = api.filterFileName(name)
	config.conf.triggersToProfiles["sayError"] = name
	fn = config.conf._getProfileFn(name)
	if os.path.isfile(fn):
		# the profile already exists
		return
	config.conf.createProfile(name)
