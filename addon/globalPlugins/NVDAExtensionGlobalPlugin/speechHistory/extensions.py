# globalPlugins\NVDAExtensionGlobalPlugin\speechHistory\extensions.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2024 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""
Extension points for prevent new speech
"""

from extensionPoints import Action
from versionInfo import version_year, version_major
NVDAVersion = [version_year, version_major]
if NVDAVersion >= [2024, 2]:
	# we use NVDA pre_speech speech extensionPoint
	from speech.extensions import pre_speech
	my_pre_speech = pre_speech
else:
	my_pre_speech = Action()
	"""
	Notifies when code attempts to speak text.
	@param speechSequence: the sequence of text and L{SpeechCommand} objects to speak
	@type speechSequence: speech.SpeechSequence
	"""
