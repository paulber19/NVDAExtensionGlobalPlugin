# globalPlugins\NVDAExtensionGlobalPlugin\ComplexSymbols\newSymbolsHandler.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from logHandler import log
import os
import globalVars
import characterProcessing
import synthDriverHandler


addonHandler.initTranslation()

addonPath = os.path.abspath(os.path.dirname(__file__))
addonName = addonPath.split("\\")[-1]
addonName = addonName.split(".")[0]
userPath = os.path.abspath(os.path.join(globalVars.appArgs.configPath, ""))
addonNewSymbolsPath = os.path.join(addonPath, "newSymbols")


def getNewSymbolsFileForVoiceLanguage(curLang):
	addonPath = addonHandler.getCodeAddon().path
	folder = os.path.join(addonPath, "newSymbols")
	if "_" in curLang:
		curLang = curLang.split("_")[0]
	langs = [curLang, "en"]
	newSymbolsFileList = os.listdir(folder)
	for lang in langs:
		newSymbolsFileName = "symbols-" + lang + ".dic"
		if newSymbolsFileName in newSymbolsFileList:
			log.debug("found New symbols from %s" % newSymbolsFileName)
			return os.path.join(folder, newSymbolsFileName)
	return None


def getNewSymbolsForCurrentLanguage():
	from speech.speech import getCurrentLanguage
	curLang = getCurrentLanguage()
	log.debug("Get new symbols for current language: %s" % curLang)
	try:
		symbolProcessor = characterProcessing._localeSpeechSymbolProcessors.fetchLocaleData(curLang)
		lang = curLang
	except LookupError:
		symbolProcessor = characterProcessing._localeSpeechSymbolProcessors.fetchLocaleData("en")
		lang = "en"
		log.debug("No locale datas for current language, getting datas for: %s" % lang)
	symbolsFile = getNewSymbolsFileForVoiceLanguage(lang)
	newSymbols = characterProcessing.SpeechSymbols()
	newSymbols.load(
		symbolsFile,
		allowComplexSymbols=False)
	log.debug("newSymbols: %s" % newSymbols.__dict__)
	change = False
	log.debug("userSymbols: %s" % symbolProcessor.userSymbols.symbols)
	alreadyInComputedSymbols = []
	alreadyInUserSymbols = []
	for symbol in newSymbols.symbols.values():
		identifier = symbol.identifier
		if symbolProcessor.userSymbols.symbols.get(identifier, None) is not None:
			alreadyInUserSymbols.append(identifier if symbol.replacement is None else symbol.replacement)
			continue
		if symbolProcessor.computedSymbols.get(identifier, None) is not None:
			log.debug("new symbol already in computed symbols: %s" % identifier)
			alreadyInComputedSymbols.append(identifier if symbol.replacement is None else symbol.replacement)
			continue
		if symbolProcessor.updateSymbol(symbol):
			change = True
	if len(alreadyInUserSymbols):
		log.debug("New symbols for %s language already in user symbols: %s" % (
			lang, ",".join(alreadyInUserSymbols)))
	if len(alreadyInComputedSymbols):
		log.debug("New symbols for %s language already in computed symbols: %s" % (
			lang, ",".join(alreadyInComputedSymbols)))
	if not change:
		return
	log.debug("user symbols file has been updated for language: %s" % symbolProcessor.locale)
	characterProcessing._localeSpeechSymbolProcessors.invalidateLocaleData(symbolProcessor.locale)
	return


# to save original nvda changeVoice method
_NVDAChangeVoice = None


def myChangeVoice(synth, voice):
	_NVDAChangeVoice(synth, voice)
	log.debug("myChangeVoice: synthtName= %s, voice= %s" % (synth.name, voice))
	getNewSymbolsForCurrentLanguage()


def initialize():
	global _NVDAChangeVoice
	_NVDAChangeVoice = synthDriverHandler.changeVoice
	synthDriverHandler.changeVoice = myChangeVoice
	log.debug(
		"synthDriverHandler.changeVoice  patched by: %s of %s module "
		% (myChangeVoice.__name__, myChangeVoice.__module__))

	getNewSymbolsForCurrentLanguage()
	log.debug("newSymbolsHandler iinitialized")


def terminate():
	global _NVDAChangeVoice
	synthDriverHandler.changeVoice = _NVDAChangeVoice
	_NVDAChangeVoice = None
