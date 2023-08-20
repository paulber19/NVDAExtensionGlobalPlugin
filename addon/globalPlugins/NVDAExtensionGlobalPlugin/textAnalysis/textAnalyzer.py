# globalPlugins/NVDAextensionGlobalPlugin\textAnalysis\textAnalyzer.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright 2021-2022 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from logHandler import log
import os
import wx
import api
import gui
import config
import ui
import speech
from ..utils.NVDAStrings import NVDAString
import tones
import textInfos
import nvwave
from ..settings.nvdaConfig import _NVDAConfigManager
from . import symbols
from ..utils.textInfo import getStartOffset, getEndOffset

addonHandler.initTranslation()

_formattingFieldChangeMsg = {
	"color": _("color"),
	"background-color": _("background color"),
	"bold": NVDAString("bold"),
	"nonBold": NVDAString("no bold"),
	"italic": NVDAString(" italic"),
	"nonItalic": NVDAString("no italic"),
	"underline": NVDAString("underline"),
	"nonUnderline": NVDAString("not underlined"),
	"strikethrough": NVDAString("strikethrough"),
	"nonStrikethrough ": NVDAString("no strikethrough"),
	"hidden": NVDAString("hidden"),
	"nonHidden": NVDAString("not hidden"),
	"sub": NVDAString("subscript"),
	"super": NVDAString("superscript"),
	"baseLine": NVDAString("base line"),
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
	# activate text analyzer  for this profile ,
	# at first trigger and , if "start text analyzer at NVDA start" option is checked.
	currentProfile = config.conf.profiles[-1].name
	if currentProfile is None:
		currentProfile = NVDAString("normal configuration")
	if currentProfile in _profiles:
		return
	_profiles.append(currentProfile)
	# it's the first time after NVDA start
	#  so set text analyzer activation if text analyzer must be started at NVDA start
	if _NVDAConfigManager.toggleTextAnalyzerActivationAtStartOption(False) and (
		not _NVDAConfigManager.toggleTextAnalyzerActivationOption(False)):
		_NVDAConfigManager.toggleTextAnalyzerActivationOption(True, silent=True)
		log.warning("Text analyzer activated at first time %s profile switched" % currentProfile)
	if not _NVDAConfigManager.toggleTextAnalyzerActivationAtStartOption(False) and (
		_NVDAConfigManager.toggleTextAnalyzerActivationOption(False)):
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
	symbolsToPositions = {}
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
		if c not in symbolsToPositions:
			symbolsToPositions[c] = []
		symbolsToPositions[c].append(position)
	for symbol, symetric in symbolToSymetricDic .items():
		if symbol not in charactersToSymbol:
			continue
		done = False
		i = 100
		characters = charactersToSymbol[symbol]
		symbolPositions = symbolsToPositions[symbol]
		while i and not done:
			i -= 1
			pos = characters.find("%s%s" % (symbol, symetric))
			if pos < 0:
				break
			del symbolPositions[pos]
			del symbolPositions[pos]
			characters = characters[:pos] + characters[pos + 2:]
		for index in range(0, len(characters)):
			ch = characters[index]
			position = symbolPositions[index]
			if position not in errorPositions:
				errorPositions[position] = []
			errorPositions[position].append(("unexpectedSymbol", ch))


decimalSymbol = symbols.getDecimalSymbol()
digitGroupingSymbol = symbols.getDigitGroupingSymbol()


def checkExtraWhiteSpace(info, unit, errorPositions):
	text = info.text
	log.debug("checkExtraWhiteSpace: %s" % text)
	curEndPos = getEndOffset(info)
	tempInfo = info.copy()
	tempInfo.collapse()
	tempInfo.expand(textInfos.UNIT_STORY)
	storyEndPos = getEndOffset(tempInfo)
	if unit == textInfos.UNIT_WORD:
		text = text.strip()
	else:
		text = text.replace("\r", "")
		text = text.replace("\n", "")
	if len(text) == 0:
		return
	eol = False
	if unit == textInfos.UNIT_LINE:
		eol = True
	elif len(text) != len(info.text) or curEndPos == storyEndPos:
		# there is end of line.
		eol = True
	# replacing non-breaking space by simple space
	text = text.replace(chr(0xA0), " ")
	if _NVDAConfigManager.spaceOrTabAtEndAnomalyOption():
		log.debug("eol: %s, text: %s" % (eol, text))
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
		if (index > 0 and index < len(text) - 1) and ch in [decimalSymbol, digitGroupingSymbol]:
			if text[index - 1].isdigit() and text[index + 1].isdigit():
				continue
		position = index + 1
		if ch not in symbols.getSymbols_all():
			if _NVDAConfigManager.uppercaseMissingAnomalyOption():
				if index > 1 and ch.islower() and text[index - 2] == "." and text[index - 1] == " ":
					# missing uppercase
					if position not in errorPositions:
						errorPositions[position] = []
					errorPositions[position].append(("missingUppercase", ch))
				elif ch.isupper() and (index > 1) and (text[index - 1].islower()) and (text[index - 2].isspace()):
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
			if ch in symbolsAndSpaceDic["NeedSpaceBefore"] and index and not text[index - 1].isspace():
				if position not in errorPositions:
					errorPositions[position] = []
				errorPositions[position].append(("neededSpace", None))
			if ch in symbolsAndSpaceDic["NeedSpaceAfter"] and (
				index != len(text) - 1) and not text[index + 1].isspace():
				if text[index + 1] not in [".", ","]:
					if position + 1not in errorPositions:
						errorPositions[position + 1] = []
					errorPositions[position + 1].append(("neededSpace", None))
			if ch in symbolsAndSpaceDic["NoSpaceBefore"] and index and text[index - 1].isspace():
				if position - 1 not in errorPositions:
					errorPositions[position - 1] = []
				errorPositions[position - 1].append(("unexpectedSpace", None))
			if ch in symbolsAndSpaceDic["NoSpaceAfter"] and (index < len(text) - 1) and text[index + 1].isspace():
				if position + 1not in errorPositions:
					errorPositions[position + 1] = []
				errorPositions[position + 1].append(("unexpectedSpace", None))


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
		file = os.path.join(path, "sounds", "textAnalyzerAlerts", fileName)
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


def getAnalyze(textInfo, unit, reportFormatted=True):
	log.debug("getAnalyse: %s, %s" % (unit, textInfo.text))
	errorPositions = {}
	if _NVDAConfigManager.toggleReportSymbolMismatchAnalysisOption(False):
		checkSymbolsDiscrepancies(textInfo, errorPositions)
	if _NVDAConfigManager.toggleReportAnomaliesOption(False):
		checkAnomalies(textInfo, unit, errorPositions)
	if _NVDAConfigManager.toggleReportFormattingChangesOption(False):
		checkFormatingChanges(textInfo, unit, errorPositions)
	alertCount = getAlertCount(errorPositions)
	if not reportFormatted:
		return (alertCount, errorPositions)
	textList = getReportText(errorPositions)
	return (alertCount, textList)


def analyzeText(info, unit):
	global _previousAnalyzedText
	if not _NVDAConfigManager.toggleTextAnalyzerActivationOption(False):
		return
	if unit in [None, textInfos.UNIT_CHARACTER]:
		return
	textInfo = info.copy()
	textInfo.expand(unit)
	log.debug("analyzeText: %s, %s" % (unit, info.text))
	if textInfo.text == _previousAnalyzedText:
		return
	alertCount, textList = getAnalyze(textInfo, unit)
	if alertCount:
		reportAnalysis(alertCount, textList)
	_previousAnalyzedText = info.text


_formatFieldList = [
	"color", "font-name", "font-family",
	"font-size", "bold", "italic", "strikethrough",
	"underline", "hidden"
]


# parts of code originaly written by Tony Malik for  browserNav add-on.
def compareFormatFields(f1, f2):
	for key in _formatFieldList:
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
		info.move(textInfos.UNIT_CHARACTER, len(info.text) - 1)
		info.expand(textInfos.UNIT_CHARACTER)
		formatField = getFormatField(info, formatConfig)
		return formatField
	return None


# parts of code originaly written by Tony Malik for  browserNav add-on.
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
				newAdjustment, fcp, lastFieldCommandField = findInWord(
					textInfo, previousFieldCommandField, formatConfig, offset)
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


_maxNumberOfLinesToScan = 100


def askToContinueSearching(textInfo, next):
	textInfo.updateCaret()
	if gui.messageBox(
		# Translators: message to indicate the no alert found by scanning 1000 lines
		_(
			"No irregularities were found on %s lines scanned."
			" Do you want to continue the analysis?") % _maxNumberOfLinesToScan,
		# Translators: dialog title.
		_("Text analysis"),
		wx.YES | wx.NO | wx.CANCEL | wx.ICON_WARNING) != wx.YES:
		return

	def callback(textInfo, next):
		speech.cancelSpeech()
		wx.CallLater(50, moveToAlert, next)
	wx.CallLater(500, callback, textInfo, next)


_newLine = False


def getLineText(textInfo):
	tempInfo = textInfo.copy()
	tempInfo.expand(textInfos.UNIT_LINE)
	lineText = tempInfo.text
	lineText = lineText.replace("\n", "")
	lineText = lineText.replace("\r", "")
	del tempInfo
	return lineText


def moveToAlert(next=True):
	log.debug("moveToLineWithAlert: next= %s" % next)
	focus = api.getFocusObject()
	info = focus.makeTextInfo(textInfos.POSITION_CARET)
	try:
		info = focus.makeTextInfo(textInfos.POSITION_CARET)
	except Exception:
		return
	from ..utils import runInThread
	textInfo = info.copy()
	direction = 1 if next else -1
	i = _maxNumberOfLinesToScan
	th = runInThread.RepeatBeep(delay=1.5, beep=(200, 200))
	th.start()
	global _newLine
	_newLine = False
	while i:
		i -= 1
		# check if no character on the line
		lineText = getLineText(textInfo)
		if len(lineText) == 0:
			log.debug("Line is empty")
			res = None
		else:
			res = findAlertOnTheLine(textInfo, next)
		if res is not None:
			# an alert is found
			th.stop()
			del th
			offset, positionMsg = res
			textInfo.collapse()
			# offset can be 0 when an alert is found on first character and cursor is on this character
			if offset:
				result = textInfo.move(textInfos.UNIT_CHARACTER, offset)
				if result == 0:
					log.debug("Cannot move to alert: offset: %s" % offset)
					return
			textInfo.collapse()
			log.debug("Moved to alert: position= %s" % (getStartOffset(textInfo)))
			textInfo.updateCaret()
			from ..utils.textInfo import getLineInfoMessage
			lineNumberMsg = getLineInfoMessage(textInfo)
			textInfo.collapse()
			textInfo.expand(textInfos.UNIT_WORD)
			ui.message("%s%s %s" % (lineNumberMsg, positionMsg, textInfo.text))
			return
		# not alert found, so  go to next or prior line
		textInfo.collapse()
		textInfo.expand(textInfos.UNIT_LINE)
		oldStart = getStartOffset(textInfo)
		textInfo.collapse()
		result = textInfo.move(textInfos.UNIT_LINE, direction)
		textInfo.expand(textInfos.UNIT_LINE)
		newStart = getStartOffset(textInfo)
		log.debug("after move to line:result= %s, direction= %s,  newStart= %s, oldStart= %s" % (
			result, direction, newStart, oldStart))
		# with word, move don't return 0. So checks start of textinfo.
		if result == 0 or oldStart == newStart:
			# on first or last line of document, so stop search
			break
		#  we are on new line
		textInfo.collapse()
		curPos = getStartOffset(textInfo)
		textInfo.expand(textInfos.UNIT_LINE)
		lineStart = getStartOffset(textInfo)
		lineEnd = getEndOffset(textInfo)
		log.debug("On new line: curPos: %s, start: %s, end: %s" % (curPos, lineStart, lineEnd))
		lineText = textInfo.text.replace("\n", "")
		lineText = lineText.replace("\r", "")
		if len(lineText) != 0 and not next:
			# move to last character of line
			offset = len(lineText) - 1
			log.debug("lineText: %s, %s" % (len(lineText), lineText))
			textInfo.collapse()
			result = textInfo.move(textInfos.UNIT_CHARACTER, offset)
			log.debug("after going to last charatter of the line:  result= %s, position= %s" % (
				result, getStartOffset(textInfo)))
		_newLine = True
		# continue the loop

	th.stop()
	del th
	if i == 0:
		wx.CallAfter(askToContinueSearching, textInfo, next)
		return
	ui.message(_("No more irregularity"))


def findAlertOnTheLine(info, next=True):
	textInfo = info.copy()
	from ..utils.textInfo import getRealPosition
	curPosition = getRealPosition(info)
	lineText = getLineText(textInfo)
	log.debug("findAlertOnTheLine: next= %s, curPosition= %s" % (next, curPosition))
	global _newLine
	textInfo.expand(textInfos.UNIT_LINE)
	lineStart = getStartOffset(textInfo)
	lineEnd = getEndOffset(textInfo)
	log.debug("line: Start: %s, end: %s" % (lineStart, lineEnd))
	# find alerts
	(alertCount, alerts) = getAnalyze(textInfo, textInfos.UNIT_LINE, reportFormatted=False)
	log.debug("allerts: %s" % alerts)
	if alertCount == 0:
		# no alerts
		log.debug("no alert")
		return None
	# prepare alert messages
	alertPositions = sorted(list(alerts))
	textList = getReportText(alerts)
	alertMessages = {}
	for alert in alertPositions:
		alertMessages[alert] = textList[alertPositions.index(alert)]
	if not next:
		alertPositions.reverse()
	# now search for next alert on the line from current position
	log.debug("alertPositions: %s" % alertPositions)
	lastPosition = len(lineText) - 1
	for position in alertPositions:
		newPosition = position - 1
		if _newLine and newPosition == 0 and curPosition == 0:
			offset = 0
			log.debug("alert found: curPosition= %s, newPosition= %s, offset= %s" % (curPosition, newPosition, offset))
			_newLine = False
			return (offset, alertMessages[position])
		if _newLine and curPosition == lastPosition:
			# cursor is on an alert at the end of line.
			offset = 0
			log.debug("alert found: curPosition= %s, newPosition= %s, offset= %s" % (curPosition, newPosition, offset))
			_newLine = False
			return (offset, alertMessages[position])
		if next and newPosition > curPosition:
			offset = newPosition - curPosition if curPosition >= 0 else 0
			log.debug("alert found: curPosition= %s, newPosition= %s, offset= %s" % (curPosition, newPosition, offset))
			_newLine = False
			return (offset, alertMessages[position])
		elif not next and curPosition > newPosition:
			offset = newPosition - curPosition
			log.debug("alert found: curPosition= %s, newPosition= %s, offset= %s" % (curPosition, newPosition, offset))
			return (offset, alertMessages[position])
	log.debug("no alert")
	return None
