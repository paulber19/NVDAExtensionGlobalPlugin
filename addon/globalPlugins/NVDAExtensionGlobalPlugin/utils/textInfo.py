# NVDAExtensionGlobalPlugin/utils/textInfo.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2023  paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from logHandler import log

import textInfos
import speech


def getStartOffset(textInfo):
	from NVDAObjects.UIA import UIATextInfo
	if issubclass(textInfo.obj.TextInfo, UIATextInfo):
		# UIA bookmark has no endOffset, so calculate it
		first = textInfo.copy()
		first.expand(textInfos.UNIT_STORY)
		startOffset = textInfo.compareEndPoints(first, "startToStart")
	else:
		if hasattr(textInfo.bookmark, "_start"):
			startOffset = textInfo.bookmark._start._startOffset
		else:
			startOffset = textInfo.bookmark.startOffset
	return startOffset


def getEndOffset(textInfo):
	from NVDAObjects.UIA import UIATextInfo
	if issubclass(textInfo.obj.TextInfo, UIATextInfo):
		# UIA bookmark has no endOffset, so calculate it
		first = textInfo.copy()
		first.expand(textInfos.UNIT_STORY)
		endOffset = textInfo.compareEndPoints(first, "endToStart")
	else:
		if hasattr(textInfo.bookmark, "_end"):
			endOffset = textInfo.bookmark._end._endOffset
		else:
			endOffset = textInfo.bookmark.endOffset
	return endOffset


def getTextInfoPositions(info):
	tempInfo = info.copy()
	start = getStartOffset(tempInfo)
	tempInfo.expand(textInfos.UNIT_LINE)
	start = getStartOffset(tempInfo)
	end = getEndOffset(tempInfo)
	tempInfo.collapse()
	textInfoPositions = []
	tempInfo.expand(textInfos.UNIT_CHARACTER)
	pos = getStartOffset(tempInfo)
	textInfoPositions.append(0)
	i = 0
	while i < (end - start):
		i += 1
		res = tempInfo.move(textInfos.UNIT_CHARACTER, 1)
		if res == 0:
			break
		tempInfo.expand(textInfos.UNIT_CHARACTER)
		pos = getStartOffset(tempInfo)
		textInfoPositions.append(pos - start)
	return textInfoPositions


def getRealPosition(info):
	tempInfo = info.copy()
	curPosition = getStartOffset(tempInfo)
	tempInfo.expand(textInfos.UNIT_LINE)
	lineStart = getStartOffset(tempInfo)
	tempInfo.collapse()
	positions = getTextInfoPositions(tempInfo)
	for pos in positions:
		if pos == curPosition - lineStart:
			return positions.index(pos)
	return None


_lastLineInfo = []


def getLineInfo(info):
	reportFormattingOptions = ("reportLineNumber", "reportPage")
	tempInfo = info.copy()
	formatConfig = dict()
	from config import conf
	for i in conf["documentFormatting"]:
		formatConfig[i] = i in reportFormattingOptions
	formatField = textInfos.FormatField()
	tempInfo.expand(textInfos.UNIT_LINE)
	for field in tempInfo.getTextWithFields(formatConfig):
		if isinstance(field, textInfos.FieldCommand) and\
			isinstance(field.field, textInfos.FormatField):
			formatField.update(field.field)
	lineInfoList = speech.getFormatFieldSpeech(
		formatField, formatConfig=formatConfig) if formatField else None
	if not lineInfoList:
		return ""
	log.debug("on: %s" % lineInfoList)
	return lineInfoList


def getLineInfoMessage(info):
	lineInfo = getLineInfo(info)
	global _lastLineInfo
	if _lastLineInfo != lineInfo:
		temp = []
		for item in lineInfo:
			if item in _lastLineInfo:
				continue
			temp.append(item)
		_lastLineInfo = lineInfo
		lineInfoMsg = ", ".join(temp)
	else:
		lineInfoMsg = ""
	return lineInfoMsg
