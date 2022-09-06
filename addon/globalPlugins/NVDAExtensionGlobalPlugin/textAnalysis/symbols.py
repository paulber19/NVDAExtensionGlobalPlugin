# globalPlugins\NVDAExtensionGlobalPlugin\textAnalysis\symbols.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2021 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from logHandler import log
import os.path
from configobj import ConfigObj
from configobj.validate import Validator
from io import StringIO

# sections
SCT_SymbolToSymetric = "SymbolToSymetric"
SCT_Punctuations = "Punctuations"
# symbols for numbers
NUM_DecimalSymbol = "decimalSymbol"
NUM_DigitGroupingSymbol = "digitGroupingSymbol"
# items of Punctuations section
SMBL_All = "All"
SMBL_NeedSpaceBefore = "NeedSpaceBefore"
SMBL_NeedSpaceAfter = "NeedSpaceAfter"
SMBL_NoSpaceBefore = "NoSpaceBefore"
SMBL_NoSpaceAfter = "NoSpaceAfter"

_configSpec = """
{decimalSymbol}= string(default=".")
{digitGroupingSymbol}= string(default=",")
[{symbolToSymetric}]
[{punctuations}]
	{all}= string(default="")
	{needSpaceBefore}= string(default="")
	{needSpaceAfter}= string(default="")
	{noSpaceBefore}= string(default="")
	{noSpaceAfter}= string(default="")
""".format(
	decimalSymbol=NUM_DecimalSymbol,
	digitGroupingSymbol=NUM_DigitGroupingSymbol,
	symbolToSymetric=SCT_SymbolToSymetric,
	punctuations=SCT_Punctuations,
	all=SMBL_All,
	needSpaceBefore=SMBL_NeedSpaceBefore,
	needSpaceAfter=SMBL_NeedSpaceAfter,
	noSpaceBefore=SMBL_NoSpaceBefore,
	noSpaceAfter=SMBL_NoSpaceAfter)


def getTextAnalysisIniFilePath():
	from languageHandler import getLanguage
	lang = getLanguage()
	langs = [lang, ]
	addonFolderPath = addonHandler.getCodeAddon().path
	if '_' in lang:
		langs.append(lang.split("_")[0])
	langs.append("en")
	for lang in langs:
		langDir = os.path.join(addonFolderPath, "locale", lang)
		if os.path.exists(langDir):
			file = os.path.join(langDir, "textAnalysis.ini")
			if os.path.isfile(file):
				log.debugWarning("textAnalyzis.ini file loaded from locale\\%s folder" % lang)
				return file
	log.error("textAnalysis.ini file not found")
	return ""


def getSymbolChoiceLabels():
	symbolChoiceLabels = {}
	symbolToSymetricDic = getSymbolToSymetricDic()
	for symbol, symetric in symbolToSymetricDic.items():
		label = "{symbol} {symetric}".format(
			symbol=symbol,
			symetric=symetric)
		symbolChoiceLabels[symbol] = label
	return symbolChoiceLabels


def getSymbols_all():
	dic = getPunctuationsDic()
	return dic[SMBL_All]


def getPunctuationsDic():
	if _conf:
		sct = _conf.get(SCT_Punctuations)
		if sct is None:
			log.error("textAnalysis punctuations section not found")
		return sct
	log.error("textAnalysis configuration cannot be loaded")
	return None


def getSymbolToSymetricDic():
	if _conf:
		sct = _conf.get(SCT_SymbolToSymetric)
		if sct is None:
			log.error("textAnalysis symbols section not found")
		return sct
	log.error("textAnalysis configuration cannot be loaded")
	return None


def getDecimalSymbol():
	if _conf is None:
		return ""
	return _conf.get(NUM_DecimalSymbol, "")


def getDigitGroupingSymbol():
	if _conf is None:
		return ""
	return _conf.get(NUM_DigitGroupingSymbol, "")


def getTextAnalysisConfig():
	path = getTextAnalysisIniFilePath()
	conf = ConfigObj(
		path,
		configspec=StringIO(""),
		encoding="utf-8",
		list_values=False)
	conf.newlines = "\r\n"
	val = Validator()
	ret = conf.validate(val, preserve_errors=True, copy=True)
	if not ret:
		log.warning("KeyboardKeys configuration file  is invalid: %s", ret)
	return conf


# singleton
_conf = getTextAnalysisConfig()
