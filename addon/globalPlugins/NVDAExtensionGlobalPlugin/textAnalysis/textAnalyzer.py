# globalPlugins/NVDAextensionGlobalPlugin\textAnalysis\textAnalyzer.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright 2021 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from logHandler import log
import os
import config
import ui
from ..utils.NVDAStrings import NVDAString
import tones
import textInfos
import nvwave
from ..settings.nvdaConfig import _NVDAConfigManager
from . import symbols

addonHandler.initTranslation()

_formattingFieldChangeMsg = {
	"color": _("color"),
	"background-color": _("background color"),
	"bold": _("bold"),
	"nonBold": _("non bold"),
	"italic": _(" italic"),
	"nonItalic": _(" non italic"),
	"underline": _("underline"),
	"nonUnderline": _("non underline"),
	"strikethrough": _("strikethrough"),
	"nonStrikethrough ": _("non strikethrough"),
	"hidden": _("hidden"),
	"nonHidden": _("non hidden"),
	"sub": _("subscript"),
	"super": _("superscript"),
	"baseLine": _("base line"),
	}

_negativeFields = {
	"bold": "nonBold",
	"italic": "nonItalic",
	"underline": "nonUnderline",
	"strikethrough": "nonStrikethrough ",
	"hidden": "nonHidden",
	"text-position": "baseLine",
	}


# keep previous analyzed text
_previousAnalyzedText = None


_textAnalyzerActivation = False

_defaultSymbolToSymetricDic = {
	# parenthese
	"(": ")",
	# "bracket"
	"[": "]",
	# "brace"
	"{": "}",
	# "quote"
	chr(0x201c): chr(0x201d),
	# chevron
	chr(0x2039): chr(0x203a),
	chr(0xab): chr(0xbb),
	}
_defaultPunctuations = {
	"All": "()[]{},:.;!?",
	"NeedSpaceBefore": "([{?!",
	"NeedSpaceAfter": ")]}?!:;",
	"NoSpaceBefore": ")]}.:;,",
	"NoSpaceAfter": "([{",
	}


# memorize all activated profiles
_profiles = []


def updateProfileConfiguration():
	global _profiles
	# call when profile is triggered.
	# activate text analyzer  for this profile , at first trigger and , if "start text analyzer at NVDA start" option is checked.
	currentProfile = config.conf.profiles[-1].name
	if currentProfile is None:
		currentProfile = NVDAString("normal configuration")
	if currentProfile in _profiles:
		return
	_profiles.append(currentProfile)
	# it's the first time after NVDA start, so set text analyzer activation if text analyzer must be started at NVDA start
	if _NVDAConfigManager.toggleTextAnalyzerActivationAtStartOption(False) and not _NVDAConfigManager.toggleTextAnalyzerActivationOption(False):
		_NVDAConfigManager.toggleTextAnalyzerActivationOption(True, silent=True)
		log.warning("Text analyzer activated at first time %s profile switched" % currentProfile)
	if not _NVDAConfigManager.toggleTextAnalyzerActivationAtStartOption(False) and _NVDAConfigManager.toggleTextAnalyzerActivationOption(False):
		_NVDAConfigManager.toggleTextAnalyzerActivationOption(True, silent=True)
		log.warning("Text analyzer desactivated at first time %s profile switched" % currentProfile)


def checkSymbolsDiscrepancies(info, errorPositions):
	text = info.text
	if len(text) == 0:
		return
	symbolToSymetricDic = symbols.getSymbolToSymetricDic()
	symetricToSymbolDic = {}
	for symbol, symetric in symbolToSymetricDic .items():
		symetricToSymbolDic[symetric] = symbol
	allSymbols = symbolToSymetricDic .keys()
	allSymbols.extend(symbolToSymetricDic .values())
	charactersToSymbol = {}
	characterPositionsToSymbol = {}
	for index in range(0, len(text)):
		ch = text[index]
		if ch not in allSymbols:
			continue
		position = index + 1
		if ch in symbolToSymetricDic:
			c = ch
		elif ch in symetricToSymbolDic:
			c = symetricToSymbolDic[ch]
		if c not in charactersToSymbol:
			charactersToSymbol[c] = ""
		charactersToSymbol[c] += ch
		if c not in characterPositionsToSymbol:
			characterPositionsToSymbol[c] = []
		characterPositionsToSymbol[c].append(position)
	for symbol, symetric in symbolToSymetricDic .items():
		if symbol not in charactersToSymbol:
			continue
		done = False
		i = 100
		characters = charactersToSymbol[symbol]
		characterPositions = characterPositionsToSymbol[symbol]
		while i and not done:
			i -= 1
			pos = characters.find("%s%s" % (symbol, symetric))
			if pos < 0:
				break
			del characterPositions[pos]
			del characterPositions[pos]
			characters = characters[:pos] + characters[pos+2:]
		for index in range(0, len(characters)):
			ch = characters[index]
			position = characterPositions[index]
			if position not in errorPositions:
				errorPositions[position] = []
			errorPositions[position].append(("unexpectedSymbol", ch))


def checkExtraWhiteSpace(info, unit, errorPositions):
	text = info.text
	log.info("checkExtraWhiteSpace: %s" % text)
	if hasattr(info.bookmark, "_end"):
		curEndPos = info.bookmark._end._endOffset
	else:
		curEndPos = info.bookmark.endOffset
	tempInfo = info.copy()
	tempInfo.collapse()
	tempInfo.expand(textInfos.UNIT_STORY)
	if hasattr(tempInfo.bookmark, "_end"):
		storyEndPos = tempInfo.bookmark._end._endOffset
	else:
		storyEndPos = tempInfo.bookmark.endOffset
	eol = False
	if unit == textInfos.UNIT_WORD:
		text = text.strip()
	else:
		text = text.replace("\r", "")
		text = text.replace("\n", "")
	if len(text) == 0:
		return
		if len(text) != len(info.text) or curEndPos == storyEndPos:
			# there is end of line.
			eol = True
	# replacing non-breaking space by simple space
	text = text.replace(chr(0xA0), " ")
	if _NVDAConfigManager.spaceOrTabAtEndAnomalyOption():
		if text[-1] == "\t" and eol:
			if len(text) not in errorPositions:
				errorPositions[len(text)] = []
			errorPositions[len(text)].append(("tabAtEnd", None))
		elif text[-1].isspace() and eol:
			if len(text) not in errorPositions:
				errorPositions[len(text)] = []
			errorPositions[len(text)].append(("spaceAtEnd", None))
	if _NVDAConfigManager.multipleContigousSpacesAnomalyOption():
		end = False
		temp = text
		dec = 0
		while not end:
			index = temp.find("  ")
			if index < 0:
				break
			pos = index + dec + 1
			if pos not in errorPositions:
				errorPositions[pos] = []
			errorPositions[pos].append(("multipleSpaces", None))
			temp = temp[index:].lstrip()
			if len(temp) == 0:
				break
			dec = text.find(temp)


def checkUppercaseMissingAndStrayOrUnSpacedPunctuation(info, unit, errorPositions):
	text = info.text

	text = text.replace("\r", "")
	text = text.replace("\n", "")
	text = text.replace(chr(0xA0), " ")
	if len(text) == 0:
		return
	symbolsAndSpaceDic = _NVDAConfigManager.getSymbolsAndSpaceDic()
	for index in range(0, len(text)):
		ch = text[index]
		position = index+1
		if ch not in symbols.getSymbols_all():
			if _NVDAConfigManager.uppercaseMissingAnomalyOption():
				if index > 1 and ch.islower() and text[index-2] == "." and text[index-1] == " ":
					# missing uppercase
					if position not in errorPositions:
						errorPositions[position] = []
					errorPositions[position].append(("missingUppercase", ch))
				elif ch.isupper() and (index > 1) and (text[index-1].islower()) and (text[index-2].isspace()):
					# inversed uppercase
					if position not in errorPositions:
						errorPositions[position] = []
					errorPositions[position].append(("inversedUppercase", ch))
			continue
		if len(text) == 1:
			if unit != textInfos.UNIT_WORD:
				if position not in errorPositions:
					errorPositions[position] = []
				errorPositions[position].append(("unexpectedPunctuation", ch))
			continue
		if _NVDAConfigManager.isolatedOrNonSpacedPunctuationsAnomalyOption():
			if ch in symbolsAndSpaceDic["NeedSpaceBefore"] and index and not text[index-1].isspace():
				if position not in errorPositions:
					errorPositions[position] = []
				errorPositions[position].append(("neededSpace", None))
			if ch in symbolsAndSpaceDic["NeedSpaceAfter"] and (index != len(text)-1) and not text[index+1].isspace():
				if text[index+1] not in [".", ","]:
					if position + 1not in errorPositions:
						errorPositions[position+1] = []
					errorPositions[position+1].append(("neededSpace", None))
			if ch in symbolsAndSpaceDic["NoSpaceBefore"] and index and text[index-1].isspace():
				if position-1 not in errorPositions:
					errorPositions[position-1] = []
				errorPositions[position-1].append(("unexpectedSpace", None))
			if ch in symbolsAndSpaceDic["NoSpaceAfter"] and (index < len(text) - 1) and text[index+1].isspace():
				if position + 1not in errorPositions:
					errorPositions[position+1] = []
				errorPositions[position+1].append(("unexpectedSpace", None))


def checkAnomalies(info, unit, errorPositions):
	checkExtraWhiteSpace(info, unit, errorPositions)
	checkUppercaseMissingAndStrayOrUnSpacedPunctuation(info, unit, errorPositions)


def getReportText(errorPositions):
	textList = []
	for pos in sorted(errorPositions):
		errors = errorPositions[pos]
		tempList = set()
		for (errorType, errorValue) in errors:
			if errorType == "unexpectedSpace":
				tempList.add(_("unexpected space"))
			elif errorType == "neededSpace":
				tempList.add(_("missing space"))
			elif errorType == "missingUppercase":
				tempList.add(_("missing uppercase"))
			elif errorType == "inversedUppercase":
				tempList.add(_("inversed uppercase"))
			elif errorType == "unexpectedSymbol":
				tempList.add(_("unexpected %s") % errorValue)
			elif errorType == "multipleSpaces":
				tempList.add(_("multiple contigous spaces"))
			elif errorType == "tabAtEnd":
				tempList.add(_("tab at end"))
			elif errorType == "spaceAtEnd":
				tempList.add(_("space at end"))
			elif errorType == "formatChange":
				tempList.add(_("change in %s") % ", ".join(errorValue))
		text = ", ".join(tempList)
		if pos == 0:
			textList.append(text)
		else:
			textList.append(_("At {pos}: {anomaly}").format(pos=pos, anomaly=text))
	return textList


def reportAnalysis(count, textList, description=False):
	if len(textList) == 0:
		return
	if description:
		ui.message(", ".join(textList))
	elif _NVDAConfigManager.reportByBeep():
		(freq, length) = _NVDAConfigManager.getBeepFrequencyAndLength()
		tones.beep(freq, length)
	elif _NVDAConfigManager.reportBySound():
		fileName = _NVDAConfigManager.getSoundFileName()
		path = addonHandler.getCodeAddon().path
		file = os.path.join(path, "sounds", "text analyzer alerts", fileName)
		nvwave.playWaveFile(file)
	elif _NVDAConfigManager.reportByAlertMessage():
		msg = _NVDAConfigManager.getAlertMessage()
		if msg == "":
			# Translators: default alert message when text analyzer detect something.
			msg = _("Alert")
		ui.message(msg)
	elif _NVDAConfigManager.reportByNumber():
		ui.message(_("%s analyzis's detections") % count)
	else:
		ui.message(", ".join(textList))


def getAlertCount(errorPositions):
	count = 0
	for pos in errorPositions:
		count += len(errorPositions[pos])
	return count


def getAnalyze(textInfo, unit):
	log.info("getAnalyse: %s, %s" % (unit, textInfo.text))
	errorPositions = {}
	if _NVDAConfigManager.toggleReportSymbolMismatchAnalysisOption(False):
		checkSymbolsDiscrepancies(textInfo, errorPositions)
	if _NVDAConfigManager.toggleReportAnomaliesOption(False):
		checkAnomalies(textInfo, unit, errorPositions)
	if _NVDAConfigManager.toggleReportFormattingChangesOption(False):
		checkFormatingChanges(textInfo, unit, errorPositions)
	alertCount = getAlertCount(errorPositions)
	textList = getReportText(errorPositions)
	return (alertCount, textList)


def analyzeText(info, unit):
	global _previousAnalyzedText
	if not _NVDAConfigManager.toggleTextAnalyzerActivationOption(False):
		return
	if unit in [None,  textInfos.UNIT_CHARACTER]:
		return
	textInfo = info.copy()
	textInfo.expand(unit)
	log.info("analyzeText: %s, %s" % (unit, info.text))
	if textInfo.text == _previousAnalyzedText:
		return
	alertCount, textList = getAnalyze(textInfo, unit)
	if alertCount:
		reportAnalysis(alertCount, textList)
	_previousAnalyzedText = info.text


# code from Javi Dominguez
blacklistKeys = {"_startOfNode", "_endOfNode"}
whitelistKeys = "color,font-name, font-family,font-size,bold,italic,strikethrough,underline".split(",")


def compareFormatFields(f1, f2):
	for key in whitelistKeys:
		if key not in f1 and key not in f2:
			continue
		try:
			if f1[key] != f2[key]:
				return False
		except KeyError:
			return False
	return True


def getOriginalFormat(caretInfo):
	formatConfig = config.conf['documentFormatting']
	formatInfo = caretInfo.copy()
	formatInfo.move(textInfos.UNIT_CHARACTER, 1, endPoint="end")
	textWithFields = formatInfo.getTextWithFields(formatConfig)
	fields = [
		field for field in textWithFields if (
			isinstance(field, textInfos.FieldCommand)
			and field.command == 'formatChange'
		)
	]
	if len(fields) == 0:
		raise Exception("No formatting information available at the cursor!")
	return fields[0]


def getFormatField(textInfo, formatConfig):
	formatField = textInfos.FormatField()
	for field in textInfo.getTextWithFields(formatConfig):
		if isinstance(field, textInfos.FieldCommand) and\
			isinstance(field.field, textInfos.FormatField):
			formatField.update(field.field)
	return formatField


def findInWord(caretInfo, originalFormatField, formatConfig, offset):
	textInfo = caretInfo.copy()
	textInfo.expand(textInfos.UNIT_WORD)
	text = textInfo.text
	endOfText = len(text)
	index = 1
	previousFormatField = originalFormatField
	formattingChangePositions = {}
	textInfo.collapse()
	while index <= endOfText:
		position = index + offset
		textInfo.expand(textInfos.UNIT_CHARACTER)
		formatField = getFormatField(textInfo, formatConfig)
		if previousFormatField and formatField != previousFormatField:
			for field, fieldValue in formatField.items():
				if fieldValue == previousFormatField.get(field):
					continue
				if field in _negativeFields and (fieldValue in ["0", "1"] or isinstance(fieldValue, bool)):
					if not int(fieldValue):
						field = _negativeFields[field]
					value = _formattingFieldChangeMsg[field]
				else:
					value = fieldValue
					if field in ["color", "background-color"]:
						from colors import RGB
						if isinstance(value, RGB):
							value = value.name
							value = "%s %s" % (_formattingFieldChangeMsg[field], value)
						elif field == "background-color":
							value = "%s %s" % (_formattingFieldChangeMsg[field], value)

				if position not in formattingChangePositions:
					formattingChangePositions[position] = []
				formattingChangePositions[position].append(value)
			# now manage field in previous formatField but not in the new
			for field in previousFormatField:
				if field not in formatField:
					# there is a change
					if field in _negativeFields:
						value = _formattingFieldChangeMsg[_negativeFields[field]]
						if position not in formattingChangePositions:
							formattingChangePositions[position] = []
						formattingChangePositions[position].append(value)
		previousFormatField = formatField
		index += 1
		textInfo.collapse()
		if textInfo.move(textInfos.UNIT_CHARACTER, 1) == 0:
			break
	return endOfText, formattingChangePositions, formatField


def checkFormatingChanges(info, unit, errorPositions):
	findFormatingChanges(info, unit, errorPositions)


def getPreviousFormatField(caretInfo, formatConfig):
	info = caretInfo.copy()
	info.collapse()
	info.expand(textInfos.UNIT_LINE)
	info.setEndPoint(caretInfo, "startToStart")
	ret = info.move(textInfos.UNIT_WORD, -1)
	if ret:
		info.move(textInfos.UNIT_CHARACTER, len(info.text)-1)
		info.expand(textInfos.UNIT_CHARACTER)
		formatField = getFormatField(info, formatConfig)
		return formatField
	return None


def findFormatingChanges(info, unit, errorPositions):
	from ..settings.nvdaConfig import documentSettingsIDsToOptions
	caretInfo = info.copy()
	caretInfo.collapse()
	unitInfo = caretInfo.copy()
	unitInfo.expand(unit)
	textInfo = unitInfo.copy()
	formatConfig = dict()
	from config import conf
	for id in conf["documentFormatting"]:
		option = documentSettingsIDsToOptions.get(id)
		if option and _NVDAConfigManager.getFormattingChangesOptions().get(option):
			formatConfig[id] = True
			continue
		formatConfig[id] = False
	formattingChangePositions = {}
	offset = 0
	textWithFields = textInfo.getTextWithFields(formatConfig)
	fields = [
		field for field in textWithFields if (
			isinstance(field, textInfos.FieldCommand)
			and field.command == 'formatChange'
			)
		or isinstance(field, str)
	]
	if len(fields) == 0:
		return
	if not isinstance(fields[0], textInfos.FieldCommand):
		raise Exception("No formatting information found at cursor!")
	if not isinstance(fields[-1], str):
		raise Exception("Formatting information found in the end - unexpected!")
	textInfo.collapse()
	change = False
	adjustment = 0
	previousFieldCommandField = getPreviousFormatField(caretInfo, formatConfig)
	lastFieldCommandField = None
	for field in fields:
		if isinstance(field, textInfos.FieldCommand):
			if previousFieldCommandField and not compareFormatFields(field.field, previousFieldCommandField):
				# Bingo! But we still need to keep going to find the end of that piece with different formatting
				change = True
			lastFieldCommandField = field.field

		elif isinstance(field, str):
			if change:
				textInfo.move(textInfos.UNIT_CHARACTER, adjustment)
				textInfo.expand(textInfos.UNIT_WORD)
				textInfo.collapse()
				newAdjustment, fcp, lastFieldCommandField = findInWord(textInfo, previousFieldCommandField, formatConfig, offset)
				formattingChangePositions .update(fcp)
				for pos in sorted(fcp):
					changes = fcp[pos]
					if pos not in errorPositions:
						errorPositions[pos] = []
					errorPositions[pos].append(("formatChange", changes))
				change = False
				adjustment = 0
			adjustment += len(field)
			offset = offset + len(field)
			previousFieldCommandField = lastFieldCommandField
		else:
			raise Exception("Impossible!")
