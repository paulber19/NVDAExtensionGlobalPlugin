# globalPlugins\NVDAExtensionGlobalPlugin\reportFormating\__init__
# A part of NvDAextensionGlobalPlugin
# Copyright (C) 2016 - 2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import colors
from versionInfo import version_year, version_major
from ..utils.NVDAStrings import NVDAString
from ..utils.informationDialog import InformationDialog

addonHandler.initTranslation()


def getReportFormattingOptions():
	NVDAVersion = [version_year, version_major]
	if NVDAVersion >= [2023, 1]:
		return(
			"reportFontName",
			"reportFontSize",
			"reportFontAttributes",
			"reportSuperscriptsAndSubscripts",
			"reportColor",
			"reportStyle",
			"reportAlignment",
			"reportSpellingErrors",
			"reportLineIndentation",
			"reportParagraphIndentation",
			"reportLineSpacing",
			"reportCellBorders",
		)

	else:
		return(
			"reportFontName",
			"reportFontSize",
			"reportFontAttributes",
			"reportSuperscriptsAndSubscripts",
			"reportColor",
			"reportStyle",
			"reportAlignment",
			"reportSpellingErrors",
			"reportLineIndentation",
			"reportParagraphIndentation",
			"reportLineSpacing",
			"reportBorderStyle",
			"reportBorderColor",
		)


def getFontText(attrs):
	font = None
	# Translators: this is a element in report formatting dialog box.
	fontTitle = _("Font:")
	fontFamily = attrs.get("font-family")
	if fontFamily:
		# Translators: this is a element in report formatting dialog box.
		text = _("Family: %s") % fontFamily
		font = "%s\r\n	%s" % (fontTitle, text)
	fontName = attrs.get("font-name")
	if fontName:
		# Translators: this is a element in report formatting dialog box.
		text = _("Name: %s") % fontName
		font = "%s\r\n	%s" % (font, text)\
			if font else "%s\r\n	%s" % (fontTitle, text)
	fontSize = attrs.get("font-size")
	if fontSize:
		# Translators: this is a element in report formatting dialog box.
		text = _("Size: %s") % fontSize
		font = "%s\r\n	%s" % (font, text)\
			if font else "%s\r\n	%s" % (fontTitle, text)
		# attributes
	attrText = getAttributesText(attrs)
	if attrText:
		font = "%s\r\n	%s" % (font, attrText)\
			if font else "%s\r\n	%s" % (fontTitle, attrText)
	# color
	colorText = getColorText(attrs)
	if colorText:
		font = "%s\r\n	%s" % (font, colorText)\
			if font else "%s\r\n	%s" % (fontTitle, colorText)
	# emphasis
	emphasisText = getEmphasisText(attrs)
	if emphasisText:
		font = "%s\r\n	%s" % (font, emphasisText)\
			if font else "%s\r\n	%s" % (fontTitle, emphasisText)
	return font


def getStyleText(attrs):
	style = attrs.get("style")
	if not style:
		# Translators: this is a element in report formatting dialog box.
		style = NVDAString("default style")
	return style


def getTextAlignmentText(attrs):
	text = None
	textAlign = attrs.get("text-align")
	if textAlign:
		textAlign = textAlign.lower() if textAlign else textAlign
		if textAlign == "left":
			text = NVDAString("align left")
		elif textAlign == "center":
			text = NVDAString("align center")
		elif textAlign == "right":
			text = NVDAString("align right")
		elif textAlign == "justify":
			text = NVDAString("align justify")
		elif textAlign == "distribute":
			text = NVDAString("align distributed")
		else:
			text = NVDAString("align default")
	if text:
		# Translators: this is a element in report formatting dialog box.
		text = _("Text's alignment: %s") % text
	return text


def getColorText(attrs):
	textList = []
	color = attrs.get("color")
	backgroundColor = attrs.get("background-color")
	backgroundColor2 = attrs.get("background-color2")
	bgColorText = backgroundColor.name\
		if isinstance(backgroundColor, colors.RGB) else backgroundColor
	if backgroundColor2:
		bg2Name = backgroundColor2.name if isinstance(backgroundColor2, colors.RGB) else backgroundColor2
		# Translators: Reported when there are two background colors.
		# This occurs when, for example,
		# a gradient pattern is applied to a spreadsheet cell.
		# {color1} will be replaced with the first background color.
		# {color2} will be replaced with the second background color.
		bgColorText = NVDAString("{color1} to {color2}").format(
			color1=bgColorText, color2=bg2Name)
	if color and backgroundColor:
		# Translators: Reported when both the text and background colors change.
		# {color} will be replaced with the text color.
		# {backgroundColor} will be replaced with the background color.
		textList.append(NVDAString("{color} on {backgroundColor}").format(
			color=color.name if isinstance(color, colors.RGB) else color,
			backgroundColor=bgColorText))
	elif color:
		# Translators: Reported when the text color changes
		# (but not the background color).
		# {color} will be replaced with the text color.
		textList.append(NVDAString("{color}").format(
			color=color.name if isinstance(color, colors.RGB) else color))
	elif backgroundColor:
		# Translators: Reported when the background color changes
		# (but not the text color).
		# {backgroundColor} will be replaced with the background color.
		textList.append(
			NVDAString("{backgroundColor} background").format(backgroundColor=bgColorText))
	backgroundPattern = attrs.get("background-pattern")
	if backgroundPattern:
		textList.append(NVDAString("background pattern {pattern}").format(
			pattern=backgroundPattern))
	if textList:
		return ", ".join(textList)
	return None


def getAttributesText(attrs):
	attrib = None
	bold = attrs.get("bold")
	if bold:
		text = NVDAString("bold")
		# Translators: this is a element in report formatting dialog box.
		attrib = _("Attributes: %s") % text
	italic = attrs.get("italic")
	if italic:
		text = NVDAString("italic")
		# Translators: this is a element in report formatting dialog box.
		attrib = "%s, %s" % (attrib, text) if attrib else _("Attributes: %s") % text
	strikethrough = attrs.get("strikethrough")
	if strikethrough:
		text = NVDAString("strikethrough")
		# Translators: this is a element in report formatting dialog box.
		attrib = "%s, %s" % (attrib, text) if attrib else _("Attributes: %s") % text
	underline = attrs.get("underline")
	if underline:
		text = NVDAString("underlined")
		# Translators: this is a element in report formatting dialog box.
		attrib = "%s, %s" % (attrib, text) if attrib else _("Attributes: %s") % text
	hidden = attrs.get("hidden")
	if hidden:
		# Translators: Reported when text is hidden.
		text = NVDAString("hidden")
		attrib = "%s, %s" % (attrib, text) if attrib else _("Attributes: %s") % text

	return attrib


def getVerticalAlignmentText(attrs):
	text = None
	verticalAlign = attrs.get("vertical-align")
	if verticalAlign:
		verticalAlign = verticalAlign.lower() if verticalAlign else verticalAlign
		if verticalAlign == "top":
			text = NVDAString("vertical align top")
		elif verticalAlign in ("center", "middle"):
			text = NVDAString("vertical align middle")
		elif verticalAlign == "bottom":
			text = NVDAString("vertical align bottom")
		elif verticalAlign == "baseline":
			text = NVDAString("vertical align baseline")
		elif verticalAlign == "justify":
			text = NVDAString("vertical align justified")
		elif verticalAlign == "distributed":
			text = NVDAString("vertical align distributed")
		else:
			text = NVDAString("vertical align default")
	if text:
		# Translators: this is a element in report formatting dialog box.
		text = _("Vertical alignment: %s") % text
	return text


def getPositionText(attrs):
	text = None
	textPosition = attrs.get("text-position")
	if textPosition:
		textPosition = textPosition.lower() if textPosition else textPosition
		if textPosition == "super":
			text = NVDAString("superscript")
		elif textPosition == "sub":
			text = NVDAString("subscript")
		else:
			text = NVDAString("baseline")
	if text:
		# Translators: this is a element in report formatting dialog box.
		text = _("Position: %s") % text
	return text


def getEmphasisText(attrs):
	textList = []
	# marked text
	marked = attrs.get("marked")
	if marked:
		# Translators: Reported when text is marked
		text = NVDAString("marked")
		textList.append(text)
	# strong text
	strong = attrs.get("strong")
	if strong:
		# Translators: Reported when text is marked as strong (e.g. bold)
		text = NVDAString("strong")
		textList.append(text)
	# emphasised text
	emphasised = attrs.get("emphasised")
	if emphasised:
		# Translators: Reported when text is marked as emphasised
		text = NVDAString("emphasised")
		textList.append(text)
	if textList:
		return ", ".join(textList)
	return None


def getParagraphIndentation(attrs):
	indentLabels = {
		'left-indent': (
			NVDAString("left indent"),
			NVDAString("no left indent"), ),
		'right-indent': (
			NVDAString("right indent"),
			NVDAString("no right indent"), ),
		'hanging-indent': (
			NVDAString("hanging indent"),
			NVDAString("no hanging indent"), ),
		'first-line-indent': (
			NVDAString("first line indent"),
			NVDAString("no first line indent"), ),
	}
	text = None
	for attr, (label, noVal) in indentLabels.items():
		newVal = attrs.get(attr)
		if newVal:
			text = str("%s\r\n	%s %s") % (
				text, label, newVal) if text else str("\r\n	%s %s") % (label, newVal)
		else:
			text = str("%s\r\n	%s") % (
				text, noVal) if text else "\r\n	%s" % (noVal)
	if text:
		# Translators: this is a element in report formatting dialog box.
		text = _("Paragraph's indentation: %s") % text
	return text


def getSpellingErrorText(attrs):
	invalidSpelling = attrs.get("invalid-spelling")
	if invalidSpelling:
		return NVDAString("spelling error")
	return None


def getGrammarErrorText(attrs):
	invalidGrammar = attrs.get("invalid-grammar")
	if invalidGrammar:
		return NVDAString("grammar error")
	return None


def getCellBorderText(attrs):
	borderStyle = attrs.get("border-style")
	if borderStyle:
		text = borderStyle
	else:
		# Translators: Indicates that cell does not have border lines.
		text = NVDAString("no border lines")
	return text


def getFormatFieldText(attrs):
	textList = []
	# style
	style = getStyleText(attrs)
	textList.append(_("style: %s") % style)
	# font
	font = getFontText(attrs)
	if font:
		textList.append(font)
# position
		position = getPositionText(attrs)
		if position:
			textList.append(position)
	# text's alignment
	textAlignment = getTextAlignmentText(attrs)
	if textAlignment:
		textList.append(textAlignment)

	# paraggraph indentation
	paragraphIndentation = getParagraphIndentation(attrs)
	if paragraphIndentation:
		textList.append(paragraphIndentation)
	VAlignment = getVerticalAlignmentText(attrs)
	if VAlignment:
		textList.append(VAlignment)
	# line spacing
	lineSpacing = attrs.get("line-spacing")
	if lineSpacing:
		# Translators: a type of line spacing (E.g. single line spacing).
		textList.append(_("Line spacing: %s") % lineSpacing)
	# spelling error
	spellingError = getSpellingErrorText(attrs)
	if spellingError:
		textList.append(spellingError)
	# grammar error
	grammarError = getGrammarErrorText(attrs)
	if grammarError:
		textList.append(grammarError)
	# cell bordertext
	cellBorder = getCellBorderText(attrs)
	if cellBorder:
		textList.append(cellBorder)
	return textList


def displayFormattingInformations(indentation, formatField):
	text = None
	if indentation:
		# Translators: this is a element in report formatting dialog box.
		text = _("Indentation: %s") % ", ".join(indentation)
	tempList = getFormatFieldText(formatField)
	for t in tempList:
		text = text + "\r\n" + t if text else t
	if text != "":
		# Translators: this is the title of information dialog
		# to show formatting informations.
		dialogTitle = _("Formatting's Informations")
		InformationDialog.run(None, dialogTitle, "", text)
