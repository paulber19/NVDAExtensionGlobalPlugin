# globalPlugins\NVDAExtensionGlobalPlugin\settings\nvdaConfig.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2021-2022 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from logHandler import log
import config
import ui
from ..textAnalysis.symbols import (
	SMBL_NeedSpaceBefore,
	SMBL_NeedSpaceAfter,
	SMBL_NoSpaceBefore,
	SMBL_NoSpaceAfter,
)
addonHandler.initTranslation()
# sections in nvda and profiles ini files
# last user config section
SCT_LastUsedSymbols = "LastUsedSymbols"

# command selective announcement section
SCT_CommandKeysAnnouncement = "CommandKeysAnnouncement"
# items for commandKeysAnnouncement section
ID_SpeakCommandKeysMode = "SpeakCommandKeysMode"
ID_DoNotSpeakCommandKeysMode = "DoNotSpeakCommandKeysMode"
# options section
SCT_Options = "Options"
# options section items
ID_SymbolLevelOnWordCaretMovement = "SymbolLevelOnWordMovement"
ID_ReportCurrentCaretPosition = "ReportCurrentCaretPosition"
ID_AddToClipSeparator = "AddToClipSeparator"
ID_AddTextBefore = "AddTextBefore"
ID_ConfirmToAddToClip = "ConfirmToAddToClip"
ID_ActivateNumlock = "ActivateNumlOck"
ID_SpeakAlphaNumChars = "SpeakAlphaNumChars"
ID_BlockInsertKey = "BlockinsertKey"
ID_BlockCapslockKey = "BlockCapslockKey"

# activateNumlock values
ANL_NoChange = 0
ANL_Off = 1
ANL_On = 2

# text analyzer section
SCT_TextAnalyzer = "textAnalyzer"
# items for text analyzer section
ID_ActivationAtStart = "ActivationAtStart"
ID_TextAnalyzerActivated = "TextAnalyzerActivated"
ID_ActivationAtStart = "ActivationAtStart"
ID_ReportBy = "ReportBy"
ID_ReportSymbolMismatchAnalysis = "ReportSymbolMismatchAnalysis"
ID_ReportAnomalies = "ReportAnomalies"
ID_ReportFormattingChanges = "ReportFormattingChanges"
# sections in TextAnalyzer section
SCT_Symbols = "Symbols"
SCT_Anomalies = "Anomalies"
SCT_Formatting = "Formatting"
SCT_Alert = "Alert"

# items in Anomalies section
ANO_MultipleContigousSpaces = "MultipleContigousSpaces"
ANO_SpaceOrTabAtEnd = "SpaceOrTabAtEnd"
ANO_IsolatedOrNonSpacedPunctuations = "IsolatedOrNonSpacedPunctuations"
ANO_UppercaseMissing = "UppercaseMissing"
ANO_NeedSpaceBefore = "NeedSpaceBefore"
ANO_NeedSpaceAfter = "NeedSpaceAfter"
ANO_NoSpaceBefore = "NoSpaceBefore"
ANO_NoSpaceAfter = "NoSpaceAfter"
SCT_SymbolsAndSpace = "SymbolsAndSpace"
# items in SymbolsAndSpace section
SAS_PreviousLanguage = "PreviousLanguage"
SAS_NeedSpaceBefore = SMBL_NeedSpaceBefore
SAS_NeedSpaceAfter = SMBL_NeedSpaceAfter
SAS_NoSpaceBefore = SMBL_NoSpaceBefore
SAS_NoSpaceAfter = SMBL_NoSpaceAfter


# item in formatting section
ID_Style = "Style"
ID_FontName = "FontName"
ID_FontSize = "FontSize"
ID_FontAttributes = "Attributes"
ID_Color = "Color"
# values for ID_ReportBy
SIG_Beep = "beep"
SIG_Sound = "sound"
SIG_AlertMessage = "alertMessage"
SIG_Number = "number"
SIG_Description = "description"

# items in Alert section
ID_BeepFrequencyAndLength = "BeepFrequencyAndLength"
ID_SoundFile = "SoundFile"
ID_AlertMessage = "Alertmessage"

_symbolsAndSpaceConfspec = {
	SAS_PreviousLanguage: """string(default="")""",
	SAS_NeedSpaceBefore: """string(default="")""",
	SAS_NeedSpaceAfter: """string(default="")""",
	SAS_NoSpaceBefore: """string(default="")""",
	SAS_NoSpaceAfter: """string(default="")""",
}

_anomaliesConfspec = {
	ANO_MultipleContigousSpaces: "boolean(default=True)",
	ANO_SpaceOrTabAtEnd: "boolean(default=True)",
	ANO_IsolatedOrNonSpacedPunctuations: "boolean(default=True)",
	ANO_UppercaseMissing: "boolean(default=True)",
	ANO_NeedSpaceBefore: "boolean(default=True)",
	ANO_NeedSpaceAfter: "boolean(default=True)",
	ANO_NoSpaceBefore: "boolean(default=True)",
	ANO_NoSpaceAfter: "boolean(default=True)",
}

# formatting configuration specification
_formattingConfspec = {
	ID_Style: "boolean(default=True)",
	ID_FontName: "boolean(default=True)",
	ID_FontSize: "boolean(default=True)",
	ID_FontAttributes: "boolean(default=True)",
	ID_Color: "boolean(default=True)",
}
# alert configuration specification
_alertConfspec = {
	ID_BeepFrequencyAndLength: """string(default="100,200")""",
	ID_SoundFile: """string(default="Windows Error.wav")""",
	# Translators: alert message for text analysis reporting.
	ID_AlertMessage: """string(default={message})""".format(message=_("Alert")),
}

# text analyzer configuration specification
_textAnalyzerConfspec = {
	ID_TextAnalyzerActivated: "boolean(default=False)",
	ID_ActivationAtStart: "boolean(default=False)",
	ID_ReportBy: "string(default='beep')",
	ID_ReportSymbolMismatchAnalysis: "boolean(default=True)",
	ID_ReportAnomalies: "boolean(default=True)",
	ID_ReportFormattingChanges: "boolean(default=False)",
	SCT_Anomalies: _anomaliesConfspec,
	SCT_SymbolsAndSpace: _symbolsAndSpaceConfspec,
	SCT_Formatting: _formattingConfspec,
	SCT_Alert: _alertConfspec,
}
numLockByLayoutDefault = ANL_Off if config.conf['keyboard']['keyboardLayout'] == "desktop" else ANL_NoChange

_optionsConfspec = {
	ID_SymbolLevelOnWordCaretMovement: """string(default="None")""",
	ID_ReportCurrentCaretPosition: "boolean(default=False)",
	ID_AddToClipSeparator: """string(default="")""",
	ID_AddTextBefore: "boolean(default=False)",
	ID_ConfirmToAddToClip: "boolean(default=False)",
	ID_ActivateNumlock: "integer(default=" + str(numLockByLayoutDefault) + ")",
	ID_SpeakAlphaNumChars: "boolean(default=False)",
	ID_BlockInsertKey: "boolean(default=False)",
	ID_BlockCapslockKey: "boolean(default=False)",
}

SCT_SynthSettingsRing = "SynthSettingsRing"
SCT_LastSelectedSettings = "lastSelectedSettings"

_curAddon = addonHandler.getCodeAddon()
_addonName = _curAddon.manifest["name"]
_addonConfspec = {
	SCT_Options: _optionsConfspec,
	SCT_TextAnalyzer: _textAnalyzerConfspec,
}
config.conf.spec[_addonName] = _addonConfspec

reportByChoiceLabels = {
	# Translators: choice label to report analysis detection with a beep.
	SIG_Beep: _("Beep"),
	# Translators: choice label to report  analysis detection with a sound.
	SIG_Sound: _("Sound"),
	# Translators: choice label to report analysis detection with speech message.
	SIG_AlertMessage: _("Alert message"),
	# Translators: choice label to report analysis detection by the number of detected elements .
	SIG_Number: _("Detections's number"),
	# Translators: choice label to report analysis detection with description of each detected elements.
	SIG_Description: _("detailed description")
}
anomalyLabels = {
	# Translators: choice item for reporting extra spaces.label
	ANO_MultipleContigousSpaces: _("The multiple contiguous spaces"),
	# Translators: choice item for reporting space or tab at end of text.
	ANO_SpaceOrTabAtEnd: _("The space or Tab at end"),
	# Translators: choice item for reporting strayed or non spaced punctuations.
	ANO_IsolatedOrNonSpacedPunctuations: _("The isolated or non spaced punctuations"),
	# Translators: choice item for reporting uppercase missing or inversed.
	ANO_UppercaseMissing: _("The uppercase missing or inversed"),
	# Translators: choice label for reporting symbols which need space before it.
	ANO_NeedSpaceBefore: _("The required space before the symbol"),
	# Translators: choice label for reporting symbols which need need space after it.
	ANO_NeedSpaceAfter: _("The required space after the symbol"),
	# Translators: choice label for reporting symbols which must not be preceded by a space.
	ANO_NoSpaceBefore: _("unexpected space before symbol"),
	# Translators: choice label for reporting symbols which must not be followed by a space")
	ANO_NoSpaceAfter: _("unexpected space after symbol"),
}
formattingChangeLabels = {
	# Translators: choice item for reporting font name change.
	ID_FontName: _("Font's name"),
	# Translators: choice item for reporting font size change.
	ID_FontSize: _("Font's size"),
	# Translators: choice item for reporting font attributes change.
	ID_FontAttributes: _("Font's attributes"),
	# Translators: choice item for reporting tyle change.
	ID_Style: _("Style"),
	# Translators: choice item for reporting color change.
	ID_Color: _("Color"),
}

documentSettingsIDsToOptions = {
	"reportFontName": ID_FontName,
	"reportFontSize": ID_FontSize,
	"reportFontAttributes": ID_FontAttributes,
	"reportSuperscriptsAndSubscripts": ID_FontAttributes,
	"reportColor": ID_Color,
	"reportStyle": ID_Style,
}


class NVDAConfigurationManager(object):
	def __init__(self):
		self.addonName = _addonName

	def deleteConfiguration(self):
		conf = config.conf
		save = False
		if self.addonName in conf.profiles[0]:
			log.warning("%s section deleted from profile: %s" % (
				self.addonName, "normal configuration"))
			del conf.profiles[0][self.addonName]
			save = True
		profileNames = []
		profileNames.extend(config.conf.listProfiles())
		for name in profileNames:
			profile = config.conf._getProfile(name)
			if profile.get(self.addonName):
				log.warning("%s section deleted from profile: %s" % (
					self.addonName, profile.name))
				del profile[self.addonName]
				config.conf._dirtyProfiles.add(name)
				save = True
		if save:
			config.conf.save()
			return True
		return False

	def saveCommandKeysSelectiveAnnouncement(
		self, keysDic, speakCommandKeysOption):
		conf = config.conf
		addonName = self.addonName
		if addonName not in conf:
			conf[addonName] = {}
		sectName = ID_SpeakCommandKeysMode\
			if speakCommandKeysOption else ID_DoNotSpeakCommandKeysMode
		if SCT_CommandKeysAnnouncement not in conf[addonName]:
			conf[addonName][SCT_CommandKeysAnnouncement] = {}
		conf[addonName][SCT_CommandKeysAnnouncement][sectName] = keysDic.copy()

	def getCommandKeysSelectiveAnnouncement(self, speakCommandKeysOption):

		def getPositionOfLeftMostBit(n):
			i = 0
			while n:
				i += 1
				n = int(n / 2)
			return i - 1
		conf = config.conf
		if self.addonName not in conf:
			return {}
		addonName = self.addonName
		sectName = ID_SpeakCommandKeysMode\
			if speakCommandKeysOption else ID_DoNotSpeakCommandKeysMode
		if SCT_CommandKeysAnnouncement in conf[addonName]\
			and sectName in conf[addonName][SCT_CommandKeysAnnouncement]:
			d = conf[addonName][SCT_CommandKeysAnnouncement][sectName].copy()
			# we must delete "numlock" and "capslock" key because shouldReportAsCommand is false.
			keys = list(d.keys())
			change = False
			for key in keys:
				if key in ["numlock", "capslock"]:
					del d[key]
					change = True
					continue
				mask = abs(int(d[key]))
				if type(d[key]) == str:
					d[key] = mask
					change = True

					change = True
			if change:
				# update config
				self.saveCommandKeysSelectiveAnnouncement(
					d, speakCommandKeysOption)
			return d
		return {}

	def deleceCommandKeyAnnouncementConfiguration(self):
		# delete configuration for all profils
		conf = config.conf
		if self.addonName in conf.profiles[0]\
			and SCT_CommandKeysAnnouncement in conf.profiles[0][self.addonName]:
			del conf.profiles[0][self.addonName][SCT_CommandKeysAnnouncement]
		profileNames = []
		profileNames.extend(config.conf.listProfiles())
		for name in profileNames:
			profile = config.conf._getProfile(name)
			if profile.get(self.addonName)\
				and SCT_CommandKeysAnnouncement in profile[self.addonName]:
				del profile[self.addonName][SCT_CommandKeysAnnouncement]
				config.conf._dirtyProfiles.add(name)

	def getLastUsedSymbolsSection(self, profileName):
		if profileName is None:
			sct = SCT_LastUsedSymbols
		else:
			sct = "%s-pro" % SCT_LastUsedSymbols
		return sct

	def saveLastUsedSymbols(self, symbolsList):
		conf = config.conf
		addonName = self.addonName
		if addonName not in conf:
			conf[addonName] = {}
		profileName = config.conf.profiles[-1].name
		sct = self.getLastUsedSymbolsSection(profileName)
		if sct not in conf[addonName]:
			conf[addonName][sct] = {}
		d = {}
		i = 1
		for (desc, symb) in symbolsList:
			d[str(i)] = "%s %s" % (symb, desc)
			i = i + 1
		conf[addonName][sct] = d.copy()
		conf[addonName][sct]._cache.clear()

	def getLastUsedSymbols(self):
		conf = config.conf
		addonName = self.addonName
		profileName = config.conf.profiles[-1].name
		sct = self.getLastUsedSymbolsSection(profileName)
		if addonName not in conf or sct not in conf[addonName]:
			return []
		d = conf[addonName][sct].copy()
		if len(d) == 0:
			return []
		symbols = []
		skip = False
		for i in range(1, len(d) + 1):
			s = d[str(i)]
			sym = s[0]
			# cause of bug , we clean all symbol equal to space
			if sym == " ":
				skip = True
				continue
			desc = s[2:]
			symbols.append((desc, sym))
		from . import _addonConfigManager
		maximumOfLastUsedSymbols = _addonConfigManager.getMaximumOfLastUsedSymbols()
		# check if number of symbols recorded is not higher than maximum
		# because bug and of config change
		if skip or len(symbols) > maximumOfLastUsedSymbols:
			# adjust the list
			log.warning("getLastUsedSymbols: last user symbols list adjusted")
			symbols = symbols[len(symbols) - maximumOfLastUsedSymbols:]
			self.saveLastUsedSymbols(symbols)
		return symbols

	def updateLastSymbolsList(self, symbolDescription, symbol):
		symbols = self.getLastUsedSymbols()
		for (desc, symb) in symbols:
			if desc == symbolDescription:
				if symbol == symb:
					# already in list
					return
				else:
					# replace description and symbol
					index = symbols.index((desc, symb))
					symbols[index] = (symbolDescription, symbol)
					self.saveLastUsedSymbols(symbols)
					return
		from . import _addonConfigManager
		maximumOfLastUsedSymbols = _addonConfigManager.getMaximumOfLastUsedSymbols()
		if len(symbols) > maximumOfLastUsedSymbols:
			# pop the oldest
			symbols.pop(0)
		symbols.append((symbolDescription, symbol))
		self.saveLastUsedSymbols(symbols)

	def cleanLastUsedSymbolsList(self):
		self.saveLastUsedSymbols([])

	def deleceAllLastUserComplexSymbols(self):
		conf = config.conf
		if self.addonName in conf.profiles[0]\
			and SCT_LastUsedSymbols in conf.profiles[0][self.addonName]:
			del conf.profiles[0][self.addonName][SCT_LastUsedSymbols]
		profileNames = []
		profileNames.extend(config.conf.listProfiles())
		sct = "%s-pro" % SCT_LastUsedSymbols
		for name in profileNames:
			profile = config.conf._getProfile(name)
			if profile.get(self.addonName)\
				and sct in profile[self.addonName]:
				del profile[self.addonName][sct]
				config.conf._dirtyProfiles.add(name)

	def toggleOption(self, ID, toggle=True):
		conf = config.conf[self.addonName][SCT_Options]
		if toggle:
			conf[ID] = not conf[ID]
		return conf[ID]

	def toggleReportCurrentCaretPositionOption(self, toggle=True):
		return self.toggleOption(ID_ReportCurrentCaretPosition, toggle)
		conf = config.conf[self.addonName][SCT_Options]
		option = ID_ReportCurrentCaretPosition
		if toggle:
			conf[option] = not conf[option]
		return conf[option]

	def saveSymbolLevelOnWordCaretMovement(self, level):
		conf = config.conf
		if self.addonName not in conf:
			conf[self.addonName] = {}
		if SCT_Options not in conf[self.addonName]:
			conf[self.addonName][SCT_Options] = {}
		conf[self.addonName][SCT_Options][ID_SymbolLevelOnWordCaretMovement] =\
			str(level) if level is not None else "None"

	def getSymbolLevelOnWordCaretMovement(self):
		conf = config.conf
		if self.addonName in conf\
			and SCT_Options in conf[self.addonName]\
			and ID_SymbolLevelOnWordCaretMovement in conf[self.addonName][SCT_Options]:
			level = conf[self.addonName][SCT_Options][ID_SymbolLevelOnWordCaretMovement]
			if level != "None":
				try:
					return int(level)
				except Exception:
					# due to a bug , we must reset to default value
					conf[self.addonName][SCT_Options][ID_SymbolLevelOnWordCaretMovement] = None
		return None

	def toggleTextAnalyzerOption(self, option, toggle):
		conf = config.conf[self.addonName][SCT_TextAnalyzer]
		if toggle:
			conf[option] = not conf[option]
		return conf[option]

	def toggleTextAnalyzerActivationOption(self, toggle=True, silent=False):
		state = self.toggleTextAnalyzerOption(ID_TextAnalyzerActivated, toggle)
		if toggle and state:
			if not silent:
				# Translators: message to user to report tex analyzer activation.
				ui.message(_("Text analyzer activated"))
			log.warning("text analyzer on")
		elif toggle:
			if not silent:
				# Translators: message to user to report text analyzer desactivation.
				ui.message(_("Text analyzer desactivated"))
			log.warning("text analyzer off")
		return state

	def toggleTextAnalyzerActivationAtStartOption(self, toggle=True):
		return self.toggleTextAnalyzerOption(ID_ActivationAtStart, toggle)

	def toggleReportSymbolMismatchAnalysisOption(self, toggle=True):
		return self.toggleTextAnalyzerOption(ID_ReportSymbolMismatchAnalysis, toggle)

	def getSymbolOptionsForDiscrepanciesAnalysis(self):
		from ..textAnalysis.symbols import getSymbolChoiceLabels
		symbolLabels = getSymbolChoiceLabels()
		conf = config.conf[self.addonName][SCT_TextAnalyzer]
		if SCT_Symbols not in conf.spec:
			# no exist, so initialize it
			spec = {}
			for symbol in symbolLabels:
				spec[symbol] = "boolean(default=True)"
			conf.spec[SCT_Symbols] = spec
		sct = conf[SCT_Symbols].copy()
		if len(sct) != len(symbolLabels):
			for symbol in conf[SCT_Symbols].copy():
				if symbol not in symbolLabels:
					del sct[symbol]
		return sct

	def setSymbolOptionsForDiscrepanciesAnalysis(self, options):
		conf = config.conf[self.addonName][SCT_TextAnalyzer]
		conf[SCT_Symbols] = options

	def toggleReportAnomaliesOption(self, toggle=True):
		return self.toggleTextAnalyzerOption(ID_ReportAnomalies, toggle)

	def toggleReportFormattingChangesOption(self, toggle=True):
		return self.toggleTextAnalyzerOption(ID_ReportFormattingChanges, toggle)

	def getAnomaliesOptions(self):
		conf = config.conf[self.addonName][SCT_TextAnalyzer]
		return conf[SCT_Anomalies].copy()

	def setAnomaliesOptions(self, options):
		conf = config.conf[self.addonName][SCT_TextAnalyzer]
		conf[SCT_Anomalies] = options

	def getAnomalyOption(self, option):
		conf = config.conf[self.addonName][SCT_TextAnalyzer][SCT_Anomalies]
		return conf[option]

	def multipleContigousSpacesAnomalyOption(self):
		return self.getAnomalyOption(ANO_MultipleContigousSpaces)

	def spaceOrTabAtEndAnomalyOption(self):
		return self.getAnomalyOption(ANO_SpaceOrTabAtEnd)

	def isolatedOrNonSpacedPunctuationsAnomalyOption(self):
		return self.getAnomalyOption(ANO_IsolatedOrNonSpacedPunctuations)

	def uppercaseMissingAnomalyOption(self):
		return self.getAnomalyOption(ANO_UppercaseMissing)

	def isAnomalyOption(self, anomalyId, anomalyLabel):
		for (id, label) in anomalyLabels .items():
			if label == anomalyLabel and id == anomalyId:
				return True
		return False

	def isNeedSpaceBeforeAnomalyOption(self, anomalyLabel):
		return self.isAnomalyOption(ANO_NeedSpaceBefore, anomalyLabel)

	def isNeedSpaceAfterAnomalyOption(self, anomalyLabel):
		return self.isAnomalyOption(ANO_NeedSpaceAfter, anomalyLabel)

	def isNoSpaceBeforeAnomalyOption(self, anomalyLabel):
		return self.isAnomalyOption(ANO_NoSpaceBefore, anomalyLabel)

	def isNoSpaceAfterAnomalyOption(self, anomalyLabel):
		return self.isAnomalyOption(ANO_NoSpaceAfter, anomalyLabel)

	def needSpaceAfterAnomalyOption(self):
		return self.getAnomalyOption(ANO_NeedSpaceAfter)

	def noSpaceBeforeAnomalyOption(self):
		return self.getAnomalyOption(ANO_NoSpaceBefore)

	def noSpaceAfterAnomalyOption(self):
		return self.getAnomalyOption(ANO_NoSpaceAfter)

	def getAnomalyWithPunctuationsOptionId(self, anomalyLabel):
		for (id, label) in anomalyLabels .items():
			if label == anomalyLabel and (
				id in [SAS_NeedSpaceBefore, SAS_NeedSpaceAfter, SAS_NoSpaceBefore, SAS_NoSpaceAfter]):
				return id
		return None

	def getFormattingChangesOptions(self):
		conf = config.conf[self.addonName][SCT_TextAnalyzer]
		return conf[SCT_Formatting].copy()

	def setFormattingChangesOptions(self, options):
		conf = config.conf[self.addonName][SCT_TextAnalyzer]
		conf[SCT_Formatting] = options

	def getFormattingOption(self, option):
		conf = config.conf[self.addonName][SCT_TextAnalyzer][SCT_Formatting]
		return conf[option]

	def FontNameFormattingOption(self):
		return self.getFormattingOption(ID_FontName)

	def FontSizeFormattingOption(self):
		return self.getFormattingOption(ID_FontSize)

	def FontAttributesFormattingOption(self):
		return self.getFormattingOption(ID_FontAttributes)

	def colorFormattingOption(self):
		return self.getFormattingOption(ID_Color)

	def getReportByOption(self):
		conf = config.conf[self.addonName][SCT_TextAnalyzer]
		option = conf[ID_ReportBy]
		return option

	def setReportByOption(self, option):
		conf = config.conf[self.addonName][SCT_TextAnalyzer]
		conf[ID_ReportBy] = option

	def reportByBeep(self):
		return self.getReportByOption() == SIG_Beep

	def reportBySound(self):
		return self.getReportByOption() == SIG_Sound

	def reportByAlertMessage(self):
		return self.getReportByOption() == SIG_AlertMessage

	def reportByNumber(self):
		return self.getReportByOption() == SIG_Number

	def reportByDescription(self):
		return self.getReportByOption() == SIG_Description

	def isReportByOption(self, label, sigOption):
		for id, reportByChoiceLabel in reportByChoiceLabels.items():
			if label == reportByChoiceLabel and id == sigOption:
				return True
		return False

	def isReportBySoundOption(self, label):
		return self.isReportByOption(label, SIG_Sound)

	def isReportByBeepOption(self, label):
		return self.isReportByOption(label, SIG_Beep)

	def isReportByAlertMessageOption(self, label):
		return self.isReportByOption(label, SIG_AlertMessage)

	def getBeepFrequencyAndLength(self):
		conf = config.conf[self.addonName][SCT_TextAnalyzer][SCT_Alert]
		beepFrequencyAndLength = conf.get(ID_BeepFrequencyAndLength)
		(freq, length) = beepFrequencyAndLength.split(",")
		return (int(freq), int(length))

	def setBeepFrequencyAndLength(self, frequency, length):
		conf = config.conf[self.addonName][SCT_TextAnalyzer][SCT_Alert]
		beep = "%s,%s" % (frequency, length)
		conf[ID_BeepFrequencyAndLength] = beep

	def getSoundFileName(self):
		conf = config.conf[self.addonName][SCT_TextAnalyzer][SCT_Alert]
		return conf.get(ID_SoundFile)

	def setSoundFileName(self, fileName):
		conf = config.conf[self.addonName][SCT_TextAnalyzer][SCT_Alert]
		conf[ID_SoundFile] = fileName

	def getAlertMessage(self):
		conf = config.conf[self.addonName][SCT_TextAnalyzer][SCT_Alert]
		return conf[ID_AlertMessage]

	def setAlertMessage(self, message):
		conf = config.conf[self.addonName][SCT_TextAnalyzer][SCT_Alert]
		conf[ID_AlertMessage] = message

	def getSymbolsAndSpaceDic(self):
		conf = config.conf[self.addonName][SCT_TextAnalyzer][SCT_SymbolsAndSpace]
		from languageHandler import getLanguage
		lang = getLanguage().split("-")[0]
		if conf[SAS_PreviousLanguage] == "" or conf[SAS_PreviousLanguage] != lang:
			# initialize it
			conf[SAS_PreviousLanguage] = lang
			from ..textAnalysis import symbols
			d = symbols.getPunctuationsDic().copy()
			del d["All"]
			for key in d:
				conf[key] = d[key]
		return conf.copy()

	def setSymbolsAndSpaceDic(self, dic):
		conf = config.conf[self.addonName][SCT_TextAnalyzer][SCT_SymbolsAndSpace]
		for key in dic:
			conf[key] = dic[key]

	def getSymbols_NeedSpaceBefore(self):
		dic = self.getSymbolsAndSpaceDic()
		return dic[SAS_NeedSpaceBefore]

	def getSymbols_NeedSpaceAfter(self):
		dic = self.getSymbolsAndSpaceDic()
		return dic[SAS_NeedSpaceAfter]

	def getSymbols_NoSpaceBefore(self):
		dic = self.getSymbolsAndSpaceDic()
		return dic[SAS_NoSpaceBefore]

	def getSymbols_NoSpaceAfter(self):
		dic = self.getSymbolsAndSpaceDic()
		return dic[SAS_NoSpaceAfter]

	def toggleAddTextBeforeOption(self, toggle=True):
		return self.toggleOption(ID_AddTextBefore, toggle)

	def toggleConfirmToAddToClipOption(self, toggle=True):
		return self.toggleOption(ID_ConfirmToAddToClip, toggle)

	def getAddToClipSeparator(self):
		conf = config.conf[self.addonName][SCT_Options]
		return conf[ID_AddToClipSeparator]

	def setAddToClipSeparator(self, separator):
		conf = config.conf[self.addonName][SCT_Options]
		conf[ID_AddToClipSeparator] = separator

	def getLastSelectedSettingInSynthSettingsRing(self, synthName):
		conf = config.conf
		addonName = self.addonName
		try:
			return conf[addonName][SCT_SynthSettingsRing][SCT_LastSelectedSettings][synthName]
		except Exception:
			return None

	def saveLastSelectedSettingInSynthSettingsRing(self, synthName, settingId):
		conf = config.conf
		addonName = self.addonName
		if addonName not in conf:
			conf[addonName] = {}
		if SCT_SynthSettingsRing not in conf[addonName]:
			conf[addonName][SCT_SynthSettingsRing] = {}
		if SCT_LastSelectedSettings not in conf[addonName][SCT_SynthSettingsRing]:
			conf[addonName][SCT_SynthSettingsRing][SCT_LastSelectedSettings] = {}
		if conf[addonName][SCT_SynthSettingsRing][SCT_LastSelectedSettings].get(synthName, None) == settingId:
			return
		conf[addonName][SCT_SynthSettingsRing][SCT_LastSelectedSettings][synthName] = settingId
		profileName = config.conf.profiles[-1].name
		log.warning("Last selected setting in synth settings ring  is saved to  '%s' setting for '%s' profile " % (
			settingId, profileName))

	def setActivateNumlockOption(self, option):
		config.conf[self.addonName][SCT_Options][ID_ActivateNumlock] = option

	def getActivateNumlockOption(self):
		return config.conf[self.addonName][SCT_Options][ID_ActivateNumlock]

	def toggleSpeakAlphaNumCharsOption(self, toggle=True):
		return self.toggleOption(ID_SpeakAlphaNumChars, toggle)

	def toggleBlockInsertKeyOption(self, toggle=True):
		return self.toggleOption(ID_BlockInsertKey, toggle)

	def toggleBlockCapslockKeyOption(self, toggle=True):
		return self.toggleOption(ID_BlockCapslockKey, toggle)


# singleton for addon configuration manager
_NVDAConfigManager = NVDAConfigurationManager()
