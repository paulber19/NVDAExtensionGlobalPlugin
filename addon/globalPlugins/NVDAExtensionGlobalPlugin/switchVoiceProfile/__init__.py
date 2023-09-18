# globalPlugins\NVDAExtensionGlobalPlugin\switchVoiceProfile\__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2018 - 2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

# originaly an idea of Tyler Spivey with his switchSynth add-on .

import addonHandler
from logHandler import log
import config
import ui
import wx
import gui
import queueHandler
import core
import characterProcessing
from synthDriverHandler import getSynth, setSynth, getSynthList
from ..utils.informationDialog import InformationDialog
from ..utils.NVDAStrings import NVDAString
from ..utils import isOpened, makeAddonWindowTitle, getHelpObj
from ..utils import contextHelpEx

addonHandler.initTranslation()

# constants

# keys and sections of "voiceProfileSwitching" section
SCT_VoiceProfileSwitching = "voiceProfileSwitching"
OLD_SCT_VoiceProfileSwitching = "SwitchingVoiceProfile"
KEY_ConfigVersion = "configVersion"
KEY_UseNormalConfigurationSelectors = "useNormalConfigurationSelectors"
KEY_LastSelector = "lastSelector"
# keys and sections of selector configuration
KEY_Activate = "activate"
KEY_VoiceProfileName = "voiceProfileName"
KEY_DefaultVoiceProfileName = "defaultVoiceProfileName"
KEY_SynthName = "synthName"
KEY_SynthDisplayInfos = "synthDisplayInfos"

# NVDA sections and keys confSpec definition
SCT_Speech = "speech"
SCT_Many = "__many__"
KEY_OutputDevice = "outputDevice"
# switching profile configuration version

_MAX_SELECTORS = 8


# timer for switchTo method
GB_SwitchToTimer = None


class SwitchVoiceProfilesManager(object):
	_configVersion = 2
	# minimum configuration version for compatibility
	_minConfigVersion = 2
	NVDASpeechSettings = [
		"autoLanguageSwitching",
		"autoDialectSwitching",
		"symbolLevel",
		"trustVoiceLanguage",
		"includeCLDR",
		"delayedCharacterDescriptions"]
	NVDASpeechManySettings = [
		"capPitchChange",
		"sayCapForCapitals",
		"beepForCapitals",
		"useSpellingFunctionality"]

	def __init__(self):
		curAddon = addonHandler.getCodeAddon()
		self.addonName = curAddon.manifest["name"]
		self.curSynth = getSynth()
		self._initialize()

	def _initialize(self):
		self.deletePreviousVoiceProfileSelectorsConfiguration()
		if not config.conf.get(self.addonName):
			config.conf[self.addonName] = {}
		if not config.conf[self.addonName].get(SCT_VoiceProfileSwitching):
			config.conf[self.addonName][SCT_VoiceProfileSwitching] = {}
		if not config.conf.profiles[0].get(self.addonName):
			config.conf.profiles[0][self.addonName] = {}
			config.conf.profiles[0][self.addonName][SCT_VoiceProfileSwitching] = {}
			config.conf.profiles[0][self.addonName][SCT_VoiceProfileSwitching][KEY_ConfigVersion] = str(
				self._configVersion)
		elif not config.conf.profiles[0][self.addonName].get(
			SCT_VoiceProfileSwitching):
			config.conf.profiles[0][self.addonName][SCT_VoiceProfileSwitching] = {}
			config.conf.profiles[0][self.addonName][SCT_VoiceProfileSwitching][KEY_ConfigVersion] = str(
				self._configVersion)

	def deletePreviousVoiceProfileSelectorsConfiguration(self):
		# check if this add-on version is not compatible with previous voice profile selectors configuration
		# If so we must delete all previous associations
		if self.deleteAllProfiles():
			gui.messageBox(
				# Translators: the label of a message box dialog.
				_(
					"""The current configuration of the "Voice profile switching"feature is not compatible """
					"""with this add-on's version, All selectors have been released and the voice profiles deleted. """
					"""Sorry for the inconvenience."""),
				# Translators: the title of a message box dialog.
				makeAddonWindowTitle(_("Warning")),
				wx.OK | wx.ICON_WARNING)

	def deleteAllProfiles(self):
		conf = config.conf
		save = False
		deleteAll = False
		if self.addonName in conf.profiles[0]:
			if OLD_SCT_VoiceProfileSwitching in conf.profiles[0][self.addonName]:
				log.warning("%s section deleted from profile: %s" % (
					OLD_SCT_VoiceProfileSwitching, "normal configuration"))
				del conf.profiles[0][self.addonName][OLD_SCT_VoiceProfileSwitching]
				save = True
			elif SCT_VoiceProfileSwitching in conf.profiles[0][self.addonName]:
				configVersion = conf.profiles[0][self.addonName][SCT_VoiceProfileSwitching].get(KEY_ConfigVersion)
				if configVersion is None\
					or int(configVersion) < int(self._minConfigVersion)\
					or int(configVersion) > int(self._configVersion):
					log.warning("%s section deleted from profile: %s" % (
						SCT_VoiceProfileSwitching, "normal configuration"))
					del conf.profiles[0][self.addonName][SCT_VoiceProfileSwitching]
					deleteAll = True
					save = True
		else:
			deleteAll = True
		profileNames = []
		profileNames.extend(config.conf.listProfiles())
		for name in profileNames:
			profile = config.conf._getProfile(name)
			if profile.get(self.addonName):
				if OLD_SCT_VoiceProfileSwitching in profile[self.addonName]:
					log.warning("%s section deleted from profile: %s" % (
						OLD_SCT_VoiceProfileSwitching, profile.name))
					del profile[self.addonName][OLD_SCT_VoiceProfileSwitching]
					config.conf._dirtyProfiles.add(name)
					save = True
				elif SCT_VoiceProfileSwitching in profile[self.addonName] and deleteAll:
					log.warning("%s section deleted from profile: %s" % (
						SCT_VoiceProfileSwitching, profile.name))
					del profile[self.addonName][SCT_VoiceProfileSwitching]
					config.conf._dirtyProfiles.add(name)
					save = True
		if save:
			config.conf.save()
			return True
		return False

	def getConfig(self):
		cfg = config.conf[self.addonName][SCT_VoiceProfileSwitching]
		return cfg.dict()

	def getSelectorConfig(self, selector):
		cfg = config.conf[self.addonName][SCT_VoiceProfileSwitching]
		speechSpec = config.conf["speech"].spec
		selectorCfg = cfg.get(selector)
		if selectorCfg is None:
			return {}
		selectorCfg._cache.clear()
		selectorCfg.spec["speech"] = speechSpec
		selectorConfig = selectorCfg.dict()
		tempDic = selectorCfg.dict()
		for key in tempDic["speech"].keys():
			if type(tempDic["speech"][key]) == dict and key not in ["__many__", tempDic["synthName"]]:
				del selectorConfig["speech"][key]
		return selectorConfig

	def getVoiceProfile(self, selector):
		if not self.isSet(selector):
			return {}
		return self.getSelectorConfig(selector)

	def isSet(self, selector, inUpdate=False):
		if inUpdate:
			updateConf = self.getUpdatedConfig()
			if updateConf.get(selector)\
				and updateConf[selector] != {}:
				if updateConf.get(KEY_VoiceProfileName)\
					or self.getConfig()[selector].get(KEY_VoiceProfileName):
					return True
		else:
			conf = self.getConfig()
			if conf.get(selector)\
				and conf[selector] != {}\
				and conf[selector].get(KEY_VoiceProfileName):
				return True
		return False

	def getLastSelector(self):
		conf = self.getConfig()
		if conf.get(KEY_LastSelector):
			return conf[KEY_LastSelector]
		return "1"

	def setLastSelector(self, selector):
		conf = config.conf[self.addonName][SCT_VoiceProfileSwitching]
		conf[KEY_LastSelector] = selector

	def switchToVoiceProfile(self, selector, silent=False):
		def finish(synthName, synthspeechConfig, msg):
			# stop previous synth because oneCore voice switch don't work without it
			config.conf[SCT_Speech] = synthSpeechConfig.copy()
			setSynth(synthName)
			config.conf[SCT_Speech][synthName] = synthSpeechConfig[synthName].copy()
			getSynth().loadSettings()
			# Reinitialize the tones module to update the audio device
			import tones
			tones.terminate()
			tones.initialize()
			if msg:
				ui.message(msg)

		newProfile = self.getVoiceProfile(selector)
		synthName = None
		for s, val in getSynthList():
			if s == newProfile[KEY_SynthName]:
				synthName = s
				break
		voiceProfileName = newProfile[KEY_VoiceProfileName]
		if synthName is None:
			if gui.messageBox(
				# Translators: the label of a message box dialog.
				_(
					"Impossible, the synthesizer of voice profile {voiceProfileName} associated to selector {selector} "
					"is not available. Do you want to free this selector?").format(
						selector=selector, voiceProfileName=voiceProfileName),
				# Translators: the title of a message box dialog.
				_("Synthesizer error"),
				wx.YES | wx.NO | wx.ICON_WARNING) == wx.YES:
				core.callLater(200, self.freeSelector, selector)
			return
		synthSpeechConfig = config.conf[SCT_Speech].dict()
		synthSpeechConfig.update(newProfile[SCT_Speech].copy())
		self.setLastSelector(selector)
		msg = None if silent else _("Selector {selector}: {name}").format(
			selector=selector, name=voiceProfileName)
		queueHandler.queueFunction(
			queueHandler.eventQueue, finish, synthName, synthSpeechConfig, msg)

	def nextVoiceProfile(self, forward=True):
		def moveSelector(currentSelector, forward):
			if forward:
				selector = currentSelector + 1 if currentSelector < _MAX_SELECTORS else 1
			else:
				selector = currentSelector - 1 if currentSelector > 1 else _MAX_SELECTORS
			return selector
		lastSelector = self.getLastSelector()
		iSelector = int(lastSelector)
		i = _MAX_SELECTORS - 1
		while i:
			i = i - 1
			iSelector = moveSelector(iSelector, forward)
			sSelector = str(iSelector)
			if not self.isSet(sSelector, not self.getUseNormalConfigurationSelectorsFlag()):
				continue

			# NVDA crash if synth switch too rapidly
			def switchTo(selector):
				global GB_SwitchToTimer
				GB_SwitchToTimer = None
				self.switchToVoiceProfile(sSelector)

			global GB_SwitchToTimer
			if GB_SwitchToTimer is not None:
				GB_SwitchToTimer.Stop()
			self.setLastSelector(sSelector)
			GB_SwitchToTimer = wx.CallLater(300, switchTo, sSelector)
			return
		if self.isSet(lastSelector):
			# Translators: message to user to report there is no other voice profile.
			ui.message(_("no other selector set to voice profile"))
			newProfile = self.getVoiceProfile(lastSelector)
			voiceProfileName = newProfile[KEY_VoiceProfileName]
			msg = _("Selector {selector}: {name}").format(
				selector=lastSelector, name=voiceProfileName)
			ui.message(msg)
		else:
			# Translators: message to user to report  there is no voice profile set.
			ui.message(_("no selector set to voice profile"))

	def setVoiceProfile(self, selector, silent=False):
		self.setLastSelector(selector)
		if not self.isSet(selector):
			# Translators: message to user to report  the selector is not set.
			ui.message(_("Selector %s is free") % selector)
			return
		wx.CallAfter(self.switchToVoiceProfile, selector, silent)

	def getSynthDisplayInfos(self, synth, synthConf):
		conf = synthConf
		id = "id"
		import autoSettingsUtils.driverSetting
		numericSynthSetting = [autoSettingsUtils.driverSetting.NumericDriverSetting, ]
		booleanSynthSetting = [autoSettingsUtils.driverSetting.BooleanDriverSetting, ]

		infos = []
		for setting in synth.supportedSettings:
			settingID = getattr(setting, id)
			if type(setting) in numericSynthSetting:
				info = str(conf[settingID])
				infos.append((setting.displayName, info))
			elif type(setting) in booleanSynthSetting:
				info = _("yes") if conf[settingID] else _("no")
				infos.append((setting.displayName, info))
			else:
				if hasattr(synth, "available%ss" % settingID.capitalize()):
					tempList = list(getattr(
						synth, "available%ss" % settingID.capitalize()).values())
					cur = conf[settingID]
					# for nvda =>2019.3
					i = [x.id for x in tempList].index(cur)
					v = tempList[i].displayName
					info = v
					infos.append((setting.displayName, info))
		d = {}
		for i in range(0, len(infos)):
			item = infos[i]
			d[str(i + 1)] = [item[0], item[1]]
		return d

	def getCurrentSynthDatas(self):
		synth = self.curSynth
		synthDatas = {}
		synthDatas[KEY_SynthName] = synth.name
		d = config.conf[SCT_Speech].dict()
		for key in config.conf[SCT_Speech]:
			val = config.conf[SCT_Speech][key]
			if type(val) == config.AggregatedSection\
				and key not in [SCT_Many, synth.name]:
				del d[key]
		synthDatas[SCT_Speech] = d
		synthDatas[KEY_SynthDisplayInfos] = self.getSynthDisplayInfos(synth, d[synth.name])
		return synthDatas

	def updateCurrentVoiceProfilSettings(self):
		from ..settings import toggleRecordCurrentSettingsForCurrentSelectorAdvancedOption
		if not toggleRecordCurrentSettingsForCurrentSelectorAdvancedOption(False):
			return
		currentSelector = self.getLastSelector()
		if not self.isSet(currentSelector):
			return
		conf = config.conf[self.addonName][SCT_VoiceProfileSwitching][currentSelector]
		voiceProfileName = conf[KEY_VoiceProfileName]
		defaultVoiceProfileName = conf[KEY_DefaultVoiceProfileName]
		self.setVoiceProfileSettingsToSelector(currentSelector, voiceProfileName, defaultVoiceProfileName)

	def setVoiceProfileSettingsToSelector(
		self, selector, voiceProfileName, defaultVoiceProfileName):
		if not config.conf.get(self.addonName):
			config.conf[self.addonName] = {}
		if not config.conf[self.addonName].get(SCT_VoiceProfileSwitching):
			config.conf[self.addonName][SCT_VoiceProfileSwitching] = {}
			config.conf[self.addonName][SCT_VoiceProfileSwitching][KEY_ConfigVersion] =\
				str(self._configVersion)
		config.conf[self.addonName][SCT_VoiceProfileSwitching][selector] = {}
		conf = config.conf[self.addonName][SCT_VoiceProfileSwitching][selector]
		conf[KEY_Activate] = True
		conf[KEY_VoiceProfileName] = voiceProfileName
		conf[KEY_DefaultVoiceProfileName] = defaultVoiceProfileName
		synthDatas = self.getCurrentSynthDatas()
		for key in synthDatas.keys():
			conf[key] = synthDatas[key]
		conf._cache.clear()

	def associateProfileToSelector(
		self, selector, voiceProfileName, defaultVoiceProfileName):
		self.setVoiceProfileSettingsToSelector(selector, voiceProfileName, defaultVoiceProfileName)
		self.setLastSelector(selector)
		# Translators: message to user to report the association
		# between selector and voice profile.
		msg = _("{name} voice profile set to selector {selector}").format(
			name=voiceProfileName, selector=selector)
		ui.message(msg)

	def freeSelector(self, selector):
		if self.isSet(selector):
			config.conf[self.addonName][SCT_VoiceProfileSwitching][selector] = {}
			config.conf[self.addonName][SCT_VoiceProfileSwitching]._cache.clear()
		# Translators: this is a message to inform the user
			# that the selector is not associated.
		ui.message(_("Selector %s is free") % selector)

	def freeAllSelectors(self):
		for index in range(1, 8):
			selector = str(index)
			if self.isSet(selector):
				config.conf[self.addonName][SCT_VoiceProfileSwitching][selector] = {}
		config.conf[self.addonName][SCT_VoiceProfileSwitching]._cache.clear()
		# Translators: this a message to inform that all slots are not associated.
		msg = _("all selectors are freed from their vocal profile")
		ui.message(msg)

	def getUpdatedConfig(self):
		conf = config.conf
		if conf.get(self.addonName)\
			and conf[self.addonName].get(SCT_VoiceProfileSwitching):
			return conf[self.addonName][SCT_VoiceProfileSwitching]._getUpdateSection()

	def getUseNormalConfigurationSelectorsFlag(self):
		conf = config.conf[self.addonName][SCT_VoiceProfileSwitching].dict()
		if KEY_UseNormalConfigurationSelectors in conf:
			return conf[KEY_UseNormalConfigurationSelectors] in [True, str(True)]
		# by default
		return True

	def setUseNormalConfigurationSelectorsFlag(self, val):
		sct = config.conf[self.addonName][SCT_VoiceProfileSwitching]
		sct[KEY_UseNormalConfigurationSelectors] = val
		sct._cache.clear()

	def getVoiceProfileName(self, selector):
		conf = config.conf[self.addonName][SCT_VoiceProfileSwitching].dict()
		return conf[selector][KEY_VoiceProfileName]

	def getSynthInformations(self, selector=None):
		def boolToText(value):

			if type(value) == str and value == "True":
				return _("yes")
			if type(value) == str and value == "False":
				return _("no")
			if type(value) == bool:
				text = _("yes") if value else _("no")
				return text
			log.error("boolToText: value is out of type range:  bool, str")
			return ""

		def punctuationLevelToText(level):
			return characterProcessing.SPEECH_SYMBOL_LEVEL_LABELS[int(level)]
		NVDASpeechSettingsInfos = [
			(_("Automatic language switching (when supported)"), boolToText),
			(_("Automatic dialect switching (when supported)"), boolToText),
			(_("Punctuation/symbol level"), punctuationLevelToText),
			(_("Trust voice's language when processing characters and symbols"), boolToText),
			(_(
				"Include Unicode Consortium data (including emoji) when processing characters and symbols"),
				boolToText),
			(_("Delayed descriptions for characters on cursor movement"), boolToText),
		]

		NVDASpeechManySettingsInfos = [
			(_("Capital pitch change percentage"), None),
			(_("Say cap before capitals"), boolToText),
			(_("Beep for capitals"), boolToText),
			(_("Use spelling functionality if supported"), boolToText),
		]
		textList = []
		if selector is None:
			# get infos for current synth
			selectorConfig = self.getCurrentSynthDatas()
		else:
			selectorConfig = self.getSelectorConfig(selector)
			textList.append(_("selector: %s") % selector)
			textList.append(
				# Translators: text to report voice profile name.
				_("Voice profile name: %s") % selectorConfig[KEY_VoiceProfileName])
			updatedConf = self.getUpdatedConfig()
			if selector not in updatedConf:
				textList.append(
					# Translators:text to report that it is normal configuration.
					_("Associated under %s configuration profile") % NVDAString("(normal configuration)"))
		synthName = selectorConfig[KEY_SynthName]
		textList.append(
			# Translators: text to report synthesizer name.
			_("Synthesizer: %s") % synthName)
		synthSettings = selectorConfig[SCT_Speech][synthName].copy()
		textList.append(
			# Translators:  label to report synthesizer output device .
			_("Output device: %s") % selectorConfig[SCT_Speech][KEY_OutputDevice])
		synthDisplayInfos = selectorConfig[KEY_SynthDisplayInfos]
		for i in synthDisplayInfos:
			item = synthDisplayInfos[i]
			textList.append("%s: %s" % (item[0], item[1]))
		for setting in SwitchVoiceProfilesManager.NVDASpeechSettings:
			val = selectorConfig[SCT_Speech][setting]
			index = SwitchVoiceProfilesManager.NVDASpeechSettings.index(setting)
			(name, f) = NVDASpeechSettingsInfos[index]
			if f is not None:
				res = f(val)
			textList.append("%s: %s" % (name, res))
		for setting in SwitchVoiceProfilesManager.NVDASpeechManySettings:
			val = selectorConfig[SCT_Speech][SCT_Many][setting]
			if setting in synthSettings:
				val = synthSettings[setting]
			else:
				val = selectorConfig[SCT_Speech][SCT_Many][setting]
			index = SwitchVoiceProfilesManager.NVDASpeechManySettings.index(setting)
			(name, f) = NVDASpeechManySettingsInfos[index]
			if f is not None:
				val = f(val)
			textList.append("%s: %s" % (name, val))
		return textList


class SelectorsManagementDialog (
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	shouldSuspendConfigProfileTriggers = True
	_instance = None
	# help in the user manual.
	helpObj = getHelpObj("hdr17-1")
	title = None

	def __new__(cls, *args, **kwargs):
		if SelectorsManagementDialog ._instance is not None:
			return SelectorsManagementDialog ._instance
		return wx.Dialog.__new__(cls)

	def __init__(self, parent):
		if SelectorsManagementDialog ._instance is not None:
			return
		SelectorsManagementDialog ._instance = self
		self.switchManager = SwitchVoiceProfilesManager()
		self.normalConfigurationProfile = False
		profileName = config.conf.profiles[-1].name
		if profileName is None:
			self.normalConfigurationProfile = True
			self.configurationProfileName = NVDAString("normal configuration")
		else:
			self.configurationProfileName = profileName

		# Translators: This is the title of the Selectors Management dialog.
		dialogTitle = _("Voice profile selectors's Management of profile %s")
		SelectorsManagementDialog .title = makeAddonWindowTitle(
			dialogTitle % self.configurationProfileName)
		super(SelectorsManagementDialog, self).__init__(parent, -1, self.title)
		self.curSynth = self.switchManager.curSynth
		self.doGui()

	def getSelectorsListLabel(self):
		# Translators: part of label of selectors list.
		text = _("&Selectors")
		if not self.normalConfigurationProfile\
			and self.switchManager.getUseNormalConfigurationSelectorsFlag():
			# current configuration profile Nam + normal configuration profile name
			return"%s (%s, %s):" % (
				text, self.configurationProfileName, NVDAString("normal configuration"))
		else:
			# only current configuration profile name
			return "%s (%s):" % (text, self.configurationProfileName)

	def getSelectorsList(self):
		selectorsList = []
		updatedConf = self.switchManager.getUpdatedConfig()
		conf = self.switchManager.getConfig()
		for index in range(0, 8):
			selector = str(index + 1)
			if self.switchManager.isSet(selector, not self.switchManager.getUseNormalConfigurationSelectorsFlag()):
				voiceProfileName = conf[selector][KEY_VoiceProfileName]
				if not self.normalConfigurationProfile and (
					selector not in updatedConf
					or not updatedConf[selector]):
					voiceProfileName = "%s %s" % (
						voiceProfileName, NVDAString("(normal configuration)"))
			else:
				voiceProfileName = _("free")
			selectorsList.append("%s: %s" % (selector, voiceProfileName))
		return selectorsList[:]

	def getCurrentSynthVoiceAndVariant(self):

		def getCurrentSettingName(setting):
			try:
				cur = getattr(synth, setting.name)
				tempList = list(getattr(
					synth, "available%ss" % setting.name.capitalize()).values())
				i = [x.id for x in tempList].index(cur)
				return tempList[i].displayName
			except Exception:
				return ""
		synth = getSynth()
		voice = ""
		variant = ""
		for s in synth.supportedSettings:
			if s.name == "voice":
				voice = getCurrentSettingName(s)
			elif s.name == "variant":
				variant = getCurrentSettingName(s)
		return (voice, variant)

	def doGui(self):
		lastSelector = self.switchManager.getLastSelector()
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label for a checkbox appearing
		# in the various settings panel.
		labelText = _("&Use selectors associated under normal cconfiguration's profile")
		self.useNormalConfigurationSelectorsCheckBox = sHelper.addItem(
			wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.useNormalConfigurationSelectorsCheckBox.SetValue(
			self.switchManager.getUseNormalConfigurationSelectorsFlag())
		if self.normalConfigurationProfile:
			self.useNormalConfigurationSelectorsCheckBox.Disable()
		# Translators: This is the label of list box appearing
			# on the Selectors Management dialog.
		labelText = self.getSelectorsListLabel()
		self.selectorListLabelText = wx.StaticText(self, wx.ID_ANY, label=labelText)
		self.selectorListBox = wx.ListBox(
			self, id=wx.ID_ANY, name="laSelectors", choices=self.getSelectorsList())
		sHelper.addItem(gui.guiHelper.associateElements(
			self.selectorListLabelText, self.selectorListBox))
		self.selectorListBox.SetSelection(int(lastSelector) - 1)
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: This is a label of a button appearing
		# on Selectors Management dialog.
		self.activateButton = bHelper.addButton(
			self, label=_("&Activate voice profile"))
		# Translators: This is a label of a button appearing
		# on Selectors Management dialog.
		self.associateButton = bHelper.addButton(
			self, label=_("A&ssociate voice profile"))
		# Translators: This is a label of a button appearing
		# on Selectors Management dialog.
		self.modifyButton = bHelper.addButton(self, label=_("&Modify voice profile"))
		# Translators: This is a label of a button appearing
		# on Selectors Management dialog.
		self.freeButton = bHelper.addButton(self, label=_("&Free selector"))
		# Translators: This is a label of a button appearing
		# on Selectors Management dialog.
		self.freeAllButton = bHelper.addButton(self, label=_("&Free all selectors"))
		# Translators: This is a label of a button appearing
		# on Selectors Management dialog.
		self.informationButton = bHelper.addButton(
			self, label=_("Voice profile's &informations"))
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		closeButton = bHelper.addButton(self, id=wx.ID_CLOSE)
		mainSizer.Add(
			sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# events
		self.useNormalConfigurationSelectorsCheckBox.Bind(
			wx.EVT_CHECKBOX, self.onCheckUseNormalConfigurationSelectors)
		self.selectorListBox.Bind(wx.EVT_LISTBOX, self.onSelectorSelection)
		self.selectorListBox.Bind(wx.EVT_SET_FOCUS, self.onFocusOnSelectorListBox)
		self.activateButton.Bind(wx.EVT_BUTTON, self.onActivateButton)
		self.associateButton.Bind(wx.EVT_BUTTON, self.onAssociateButton)
		self.modifyButton.Bind(wx.EVT_BUTTON, self.onModifyButton)
		self.freeButton.Bind(wx.EVT_BUTTON, self.onFreeButton)
		self.freeAllButton.Bind(wx.EVT_BUTTON, self.onFreeAllButton)
		self.informationButton.Bind(wx.EVT_BUTTON, self.onInformationButton)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)
		self.selectorListBox.SetFocus()
		self.updateButtons()

	def Destroy(self):
		SelectorsManagementDialog ._instance = None
		super(SelectorsManagementDialog, self).Destroy()

	def updateSelectorsList(self, currentSelector=None):
		self.selectorListBox.Clear()
		self.selectorListBox.AppendItems(self.getSelectorsList())
		if currentSelector is None:
			currentSelector = self.switchManager.getLastSelector()
		self.selectorListBox.SetSelection(int(currentSelector) - 1)

	def onCheckUseNormalConfigurationSelectors(self, evt):
		val = self.useNormalConfigurationSelectorsCheckBox.GetValue()
		self.switchManager.setUseNormalConfigurationSelectorsFlag(val)
		labelText = self.getSelectorsListLabel()
		self.selectorListLabelText.SetLabel(labelText)
		self.updateSelectorsList()

	def onInformationButton(self, evt):
		index = self.selectorListBox.GetSelection()
		selector = str(index + 1)
		textList = self.switchManager.getSynthInformations(selector)
		text = "\r\n".join(textList)
		# Translators: this is the title of informationdialog box
		# to show voice profile informations.
		dialogTitle = _("Voice profile 's informations")
		InformationDialog.run(None, dialogTitle, "", text)

	def onActivateButton(self, evt):
		# no action if focus is on check box
		if self.useNormalConfigurationSelectorsCheckBox.HasFocus():
			return
		index = self.selectorListBox.GetSelection()
		self.switchManager .updateCurrentVoiceProfilSettings()
		self.switchManager.setVoiceProfile(str(index + 1), silent=True)
		self.Close()

	def onAssociateButton(self, evt):
		# no action if focus is on the check box
		if self.useNormalConfigurationSelectorsCheckBox.HasFocus():
			return
		index = self.selectorListBox.GetSelection()
		selector = str(index + 1)
		if self.switchManager.isSet(selector, not self.switchManager.getUseNormalConfigurationSelectorsFlag()):
			conf = self.switchManager.getConfig()
			voiceProfileName = conf[selector][KEY_VoiceProfileName]
			if gui.messageBox(
				# Translators: the label of a message box dialog.
				_(
					"Selector {selector} is already set to {voiceProfileName} voice profile. "
					"Do you want to replace this voice profile?"
				) .format(selector=selector, voiceProfileName=voiceProfileName),
				# Translators: the title of a message box dialog.
				_("Confirmation"),
				wx.YES | wx.NO | wx.ICON_WARNING) == wx.NO:
				return
		with AssociateVoiceProfileDialog(
			self, selector) as associateVoiceProfileDialog:
			if associateVoiceProfileDialog.ShowModal() != wx.ID_OK:
				return
		core.callLater(
			200,
			self.switchManager.associateProfileToSelector,
			selector,
			associateVoiceProfileDialog.voiceProfileName,
			associateVoiceProfileDialog.defaultVoiceProfileName)
		self.Close()

	def onModifyButton(self, evt):
		index = self.selectorListBox.GetSelection()
		selector = str(index + 1)
		voiceProfile = self.switchManager.getConfig()[selector]
		with ModifyVoiceProfileDialog(self, voiceProfile) as modifyVoiceProfileDialog:
			if modifyVoiceProfileDialog.ShowModal() != wx.ID_OK:
				return
			voiceProfileName = modifyVoiceProfileDialog.voiceProfileName
			self.selectorListBox.SetString(
				index, "%s: %s" % (str(index + 1), voiceProfileName))
			voiceProfile[KEY_VoiceProfileName] = voiceProfileName

	def onFreeButton(self, evt):
		index = self.selectorListBox.GetSelection()
		selector = str(index + 1)
		if not self.switchManager.isSet(selector):
			return
		conf = self.switchManager.getConfig()
		voiceProfileName = conf[selector][KEY_VoiceProfileName]
		if gui.messageBox(
			# Translators: the label of a message box dialog.
			_(
				"""Do you really want to free selector {selector} """
				"""associated to the voice profile "{voiceProfileName}"?"""
			).format(selector=selector, voiceProfileName=voiceProfileName),
			# Translators: the title of a message box dialog.
			_("Confirmation"),
			wx.YES | wx.NO | wx.ICON_WARNING) == wx.NO:
			return
		self.switchManager.freeSelector(selector)
		self.updateSelectorsList(selector)
		self.updateButtons()
		self.selectorListBox.SetFocus()

	def onFreeAllButton(self, evt):
		if gui.messageBox(
			# Translators: the label of a message box dialog.
			_("Do you really want to free all selectors set to this configuration profile?"),
			# Translators: the title of a message box dialog.
			_("Confirmation"),
			wx.YES | wx.NO | wx.ICON_WARNING) == wx.NO:
			return

		self.switchManager.freeAllSelectors()
		index = self.selectorListBox.GetSelection()
		selector = str(index + 1)
		self.updateSelectorsList(selector)
		self.updateButtons()
		self.selectorListBox.SetFocus()

	def updateButtons(self):
		def isSet(selector):
			label = self.selectorListBox.GetString(int(selector) - 1)
			freeText = _("free")
			if label[-len(freeText):] == freeText:
				return False
			elif self.switchManager.isSet(selector):
				return True
			return False

		selector = str(self.selectorListBox.GetSelection() + 1)
		updatedConf = self.switchManager.getUpdatedConfig()
		if isSet(selector):
			self.activateButton.Enable()
			self.activateButton.SetDefault()
			self.informationButton.Enable()
			if selector in updatedConf\
				and not updatedConf[selector] == {}:
				self.modifyButton.Enable()
				self.freeButton.Enable()
			else:
				self.modifyButton.Disable()
				self.freeButton.Disable()
		else:
			self.associateButton.SetDefault()
			self.activateButton.Disable()
			self.modifyButton.Disable()
			self.freeButton.Disable()
			self.informationButton.Disable()
		enable = False
		for index in range(self.selectorListBox.Count):
			selector = str(index + 1)
			if (
				isSet(selector)
				and selector in updatedConf
				and updatedConf[selector] != {}):
				enable = True
				break
		if enable:
			self.freeAllButton.Enable()
		else:
			self.freeAllButton.Disable()

	def onFocusOnSelectorListBox(self, evt):
		self.updateButtons()

	def onSelectorSelection(self, evt):
		self.updateButtons()

	@classmethod
	def run(cls, obj):
		if isOpened(cls):
			return
		gui.mainFrame.prePopup()
		d = cls(gui.mainFrame)
		d.CentreOnScreen()
		d.ShowModal()
		gui.mainFrame.postPopup()


class ModifyVoiceProfileDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	# help in the user manual.
	helpObj = getHelpObj("hdr17-1")
	# Translators: This is the title of the modify voice profile dialog.
	title = _("Modify voice profile ")

	def __init__(self, parent, voiceProfile):
		super(ModifyVoiceProfileDialog, self).__init__(parent, title=self.title)
		self.voiceProfile = voiceProfile
		voiceProfileName = voiceProfile[KEY_VoiceProfileName]
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label of the edit field appearing
		# on the Modify voice profile dialog.
		voiceProfileNameEditLabelText = _("voice profile name:")
		self.voiceProfileNameEdit = sHelper.addLabeledControl(
			voiceProfileNameEditLabelText, wx.TextCtrl)
		self.voiceProfileNameEdit .AppendText(voiceProfileName)
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: This is a label of a button appearing
		# on modify voice profile Dialog.
		defaultButton = bHelper.addButton(self, label=_("&Default"))
		sHelper.addItem(bHelper)
		sHelper.addDialogDismissButtons(self.CreateButtonSizer(wx.OK | wx.CANCEL))
		mainSizer.Add(
			sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		defaultButton.Bind(wx.EVT_BUTTON, self.onDefaultButton)
		self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK)
		self.voiceProfileNameEdit.SetFocus()
		self.CentreOnScreen()

	def onDefaultButton(self, evt):
		self.voiceProfileNameEdit .Clear()
		self.voiceProfileNameEdit .AppendText(
			self.voiceProfile[KEY_DefaultVoiceProfileName])
		self.voiceProfileNameEdit .SetFocus()
		evt.Skip()

	def onOk(self, evt):
		voiceProfileName = self.voiceProfileNameEdit.GetValue()
		if len(voiceProfileName) == 0:
			core.callLater(
				200,
				ui.message,
				# Translators: message to user: profile's name must be set.
				_("You must set the name of voice profile"))
			return

		self.voiceProfileName = voiceProfileName
		evt.Skip()


class AssociateVoiceProfileDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	# Translators: This is the title of the Associate voice profile dialog.
	title = _("Voice profile association")
	# help in the user manual.
	helpObj = getHelpObj("hdr17-1")

	def __init__(self, parent, selector):
		super(AssociateVoiceProfileDialog, self).__init__(parent, title=self.title)
		self.parent = parent
		self.selector = selector
		synthName = self.parent.switchManager.curSynth.name
		(voice, variant) = self.getCurrentSynthVoiceAndVariant()
		self.defaultVoiceProfileName = "%s %s %s" % (synthName, voice, variant)
		self.voice = voice
		self.variant = variant

		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label of the edit field appearing
		# in the associate voice profile dialog.
		voiceProfileNameEditLabelText = _("voice profile name:")
		self.voiceProfileNameEdit = sHelper.addLabeledControl(
			voiceProfileNameEditLabelText, wx.TextCtrl)
		self.voiceProfileNameEdit .AppendText(self.defaultVoiceProfileName)
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: This is a label of a button appearing
		# on associate voice profile dialog.
		defaultButton = bHelper.addButton(self, label=_("&Default"))
		sHelper.addItem(bHelper)
		sHelper.addDialogDismissButtons(self.CreateButtonSizer(wx.OK | wx.CANCEL))
		mainSizer.Add(
			sHelper.sizer,
			border=gui.guiHelper.BORDER_FOR_DIALOGS,
			flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		defaultButton.Bind(wx.EVT_BUTTON, self.onDefaultButton)
		self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK)
		self.voiceProfileNameEdit.SetFocus()
		self.CentreOnScreen()

	def getCurrentSynthVoiceAndVariant(self):
		def getCurrentSettingName(synth, id):
			attr = "available%ss" % id.capitalize()
			try:
				tempList = list(getattr(synth, attr).values())
				i = [x.id for x in tempList].index(getattr(synth, id))
				return tempList[i].displayName
			except Exception:
				return ""
		synth = self.parent.switchManager.curSynth
		voice = ""
		variant = ""
		for s in synth.supportedSettings:
			id = s.id
			if id == "voice":
				voice = getCurrentSettingName(synth, id)
			elif id == "variant":
				variant = getCurrentSettingName(synth, id)
		return (voice, variant)

	def onDefaultButton(self, evt):
		self.voiceProfileNameEdit .Clear()
		self.voiceProfileNameEdit .AppendText(self.defaultVoiceProfileName)
		self.voiceProfileNameEdit .SetFocus()
		evt.Skip()

	def onOk(self, evt):
		voiceProfileName = self.voiceProfileNameEdit.GetValue()
		if len(voiceProfileName) == 0:
			core.callLater(
				200,
				ui.message,
				# Translators: message to user: profile's name must be set.
				_("You must set the name of voice profile"))
			return
		self.voiceProfileName = voiceProfileName
		evt.Skip()
