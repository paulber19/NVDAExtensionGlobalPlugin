# globalPlugins\NVDAExtensionGlobalPlugin\clipboardCommandAnnouncement\speechEx.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C)  2023 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


from logHandler import log
import speech.speech
import api
import unicodedata
import config
import time
try:
	# for nvda version >= 2021.2
	from controlTypes.state import State
	STATE_READONLY = State.READONLY
except (ModuleNotFoundError, AttributeError):
	from controlTypes import STATE_READONLY


# this code comes from leonardder  work for issue #8110, see at:
# Speak typed words based on TextInfo if possible #8110


def speakTypedCharacters(ch: str):
	typingIsProtected = api.isTypingProtected()
	if typingIsProtected:
		realChar = speech.speech.PROTECTED_CHAR
	else:
		realChar = ch
	if unicodedata.category(ch)[0] in "LMN":
		speech.speech._curWordChars.append(realChar)
	elif ch == "\b":
		# Backspace, so remove the last character from our buffer.
		del speech.speech._curWordChars[-1:]
	elif ch == u'\u007f':
		# delete character produced in some apps with control+backspace
		return
	# elif len(speech.speech._curWordChars)>0:
	else:
		speakPreviousWord(realChar)
	from speech.speech import _speechState
	if _speechState._suppressSpeakTypedCharactersNumber > 0:
		# We primarily suppress based on character count and still have characters to suppress.
		# However, we time out after a short while just in case.
		suppress = time.time() - _speechState._suppressSpeakTypedCharactersTime <= 0.1
		if suppress:
			_speechState._suppressSpeakTypedCharactersNumber -= 1
		else:
			_speechState._suppressSpeakTypedCharactersNumber = 0
			_speechState._suppressSpeakTypedCharactersTime = None
	else:
		suppress = False
	if (
		not suppress
		and config.conf["keyboard"]["speakTypedCharacters"]
		and ch >= speech.speech.FIRST_NONCONTROL_CHAR
	):
		speech.speech.speakSpelling(realChar)


def speakPreviousWord(wordSeparator):
	# get word when not using textInfo
	word = "".join(speech.speech._curWordChars)
	log.debug("speakPreviousWord: %s" % word)
	typingIsProtected = api.isTypingProtected()
	if not (log.isEnabledFor(log.IO) or (
		config.conf["keyboard"]["speakTypedWords"] and not typingIsProtected)):
		speech.speech.clearTypedWordBuffer()
		return
	try:
		obj = api.getCaretObject()
	except Exception:
		# No caret object, nothing to report
		return
	# The caret object can be an NVDAObject or a TreeInterceptor.
	# Editable caret cases inherrit from EditableText.
	from editableText import EditableText
	if not isinstance(obj, EditableText) or STATE_READONLY in getattr(obj, "states", set()):
		speech.speech.clearTypedWordBuffer()
		return
	if not obj.useTextInfoToSpeakTypedWords and len(word) == 0:
		log.debug("no word and not useTextInfoToSpeakTypedWords ")
		return
	wordFound, wordInfo = obj.hasNewWordBeenTyped(wordSeparator)
	if wordFound is False:
		speech.speech._curWordChars.append(wordSeparator)
		log.debug("no word:  wordFound is false. Just append wordSeparator)")
		return
	speakUsingTextInfo = wordFound is True and not speech.speech.isBlank(wordInfo.text)
	if speakUsingTextInfo:
		word = wordInfo.text
	speech.speech.clearTypedWordBuffer()
	if log.isEnabledFor(log.IO):
		log.io(f"typed word: {word}")
	if len(word) and config.conf["keyboard"]["speakTypedWords"] and not typingIsProtected:
		speech.speech.speakText(word)
