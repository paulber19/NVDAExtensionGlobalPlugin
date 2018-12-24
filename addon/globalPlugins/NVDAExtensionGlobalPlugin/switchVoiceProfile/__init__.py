#NVDAExtensionGlobalPlugin/switchVoiceProfile/__init__
#A part of  NvDAextensionGlobalPlugin add-on
#Copyright (C) 2018 paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

#originaly an idea of Tyler Spivey  with his switchSynth add-on .

import addonHandler
addonHandler.initTranslation()
import os
import config
import speech
import ui
import scriptHandler
import wx
import gui
import queueHandler
import NVDAObjects
from ..utils.informationDialog import InformationDialog, makeAddonWindowTitle
from ..utils.NVDAStrings import NVDAString

from ..__init__  import GB_taskTimer
import synthDriverHandler
import characterProcessing
import api
from ..settings import _addonConfigManager
import core

#constants
_VOICE_PROFILE_SWITCHING  = "VoiceProfileSwitching"
_LAST_SELECTOR = "LastSelector"
_MAX_SELECTORS= 8

class SwitchVoiceProfile(object):

	NVDASpeechSettings = ["autoLanguageSwitching", "autoDialectSwitching", "symbolLevel", "trustVoiceLanguage"]
	NVDASpeechManySettings = ["capPitchChange", "sayCapForCapitals", "beepForCapitals", "useSpellingFunctionality"]


	def __init__ (self):
		_addonConfigManager.updateVoiceProfileSwitchingConfig()
		self._initialize()
	
	def _initialize(self):
		self.switchVoiceProfileSection = _addonConfigManager.getVoiceProfileSwitching()
		self.curSynth = speech.getSynth()
		self.curConfigSpeech = config.conf["speech"].copy()
	
	def isSet(self, selector):
		return _addonConfigManager.isVoiceProfileSelectorSet(selector)
		
	
	def getLastSelector(self):
		return _addonConfigManager.getLastVoiceProfileSelector()

	
	def setLastSelector(self, selector):
		_addonConfigManager.setLastVoiceProfileSelector(selector)
	
	def switchToVoiceProfile(self, selector):
		voiceProfileSwitchingSect = _addonConfigManager.getVoiceProfileSwitching()
		#newProfile = voiceProfileSwitchingSect[selector].copy()
		newProfile = _addonConfigManager.getVoiceProfile(selector)
		voiceProfileName = newProfile["voiceProfileName"]
		synthName = None
		for s, val in speech.getSynthList():
			if s == newProfile["synthName"]:
				synthName = s
				break

		if synthName is None:
			if gui.messageBox(
				# Translators: the label of a message box dialog.
				_("Impossible, the synthetizer of voice profile {voiceProfileName} associated to selector {selector} is not available. Do you want to free this selector ?").format(selector= selector, voiceProfileName = voiceProfileName),
				# Translators: the title of a message box dialog.
				_("Synthetizer error"),
				wx.YES|wx.NO|wx.ICON_WARNING)==wx.YES:
				core.callLater(200, self.freeSelector, selector)
				return
		
		speechSynthConf = config.conf['speech'][synthName]
		for s,val in newProfile["config"].iteritems():
			config.conf['speech'][synthName][s] = val
		for s in self.NVDASpeechSettings:
			config.conf["speech"][s] = newProfile[s]
		config.conf["speech"]["__many__"] = newProfile["__many__"].copy()
		speech.setSynth(synthName)
		msg = _("Selector {selector}: {name}").format(selector = selector, name = voiceProfileName)
		ui.message(msg)
		self.setLastSelector(selector)
	def nextOrPreviousVoiceProfile(self, action = "next"):
		def nextSelector(currentSelector, action):
			if action == "next":
				selector = currentSelector+ 1 if currentSelector <_MAX_SELECTORS else 1
			else:
				selector = currentSelector- 1 if currentSelector >1 else _MAX_SELECTORS
			return selector
		
		lastSelector  = self.getLastSelector()
		iSelector = int(lastSelector)
		i= _MAX_SELECTORS-1
		while i:
			i=i-1
			iSelector = nextSelector(iSelector, action)
			sSelector = str(iSelector)
			if not self.isSet(sSelector):
				continue
			self.switchToVoiceProfile(sSelector)
			self.setLastSelector(sSelector)
			return
		if self.isSet(lastSelector):
			#Translators: this is a message to inform the user that there is no other voice profile.
			ui.message(_("no other selector set to voice profile"))
			newProfile = _addonConfigManager.getVoiceProfile(lastSelector) #.copy()
			voiceProfileName = newProfile["voiceProfileName"]
			msg = _("Selector {selector}: {name}").format(selector= lastSelector, name = voiceProfileName)
			ui.message(msg)
		else:
			#Translators: this is a message to inform the user that there is no voice profile set.
			ui.message(_("no selector set to voice profile"))

	
	def setVoiceProfileSelector(self, iSelector):
		selector = str(iSelector)
		self.setLastSelector(selector)
		#config.conf[_VOICE_PROFILE_SWITCHING ]._cache.clear()
		if self.isSet(selector):
			wx.CallAfter(self.switchToVoiceProfile, selector)
			return
		
		#Translators: this is  a message to inform the user  that the selector is not set.
		ui.message(_("Selector %s is free") %selector)
	
	def associateProfileToSelector(self, selector, voiceProfileName, defaultVoiceProfileName):
		c = {}
		c["voiceProfileName"] = voiceProfileName
		c["defaultVoiceProfileName"] = defaultVoiceProfileName
		synth = speech.getSynth()
		c["synthName"] = synth.name
		c["outputDevice"] = config.conf["speech"]["outputDevice"]
		c["config"] = config.conf['speech'][synth.name].copy()
		infos = {}
		for setting in synth.supportedSettings:
			name = setting.name
			if isinstance(setting,synthDriverHandler.NumericSynthSetting):
				infos[name] = c["config"][name]
			elif isinstance(setting, synthDriverHandler.BooleanSynthSetting):
				infos[name] = c["config"][name]
			else:
				if hasattr(synth,"available%ss"%setting.name.capitalize()):
					l=getattr(synth,"available%ss"%name.capitalize()).values()
					cur = c["config"][name]
					i=[x.ID for x in l].index(cur)
					v = l[i].name
					infos[name] = v

		c["synthDisplayInfos"] = infos.copy()
		c["__many__"] = config.conf["speech"]["__many__"].copy()
		for s in self.NVDASpeechSettings:
			c[s] = config.conf["speech"][s]
		_addonConfigManager.setVoiceProfile(selector, c)
		"""
		if _VOICE_PROFILE_SWITCHING  not in config.conf:
			config.conf[_VOICE_PROFILE_SWITCHING ] = {}
		if not self.isSet(selector):
			config.conf[_VOICE_PROFILE_SWITCHING ][selector] = {}
		config.conf[_VOICE_PROFILE_SWITCHING ][selector]= c.copy()
		"""
		#Translators: this is a message  to the user to report the association between selector and voice profile.
		msg = _("{name} voice profile set to selector {selector}").format(name = voiceProfileName, selector = selector)
		core.callLater(200, ui.message, msg)
		self.setLastSelector(selector)
		self._initialize()

	def freeAllSelectors(self):
		_addonConfigManager.freeAllVoiceProfileSelectors()
		#Translators: this a message to inform that all slots are not associated.
		msg = _("all selectors are freed from their vocal profile")
		ui.message( msg)
		self._initialize()
	
	def freeSelector(self, selector):
		_addonConfigManager.freeVoiceProfileSelector(selector)
		#Translators: this is  a message to inform the user that  the selector is not associated.
		ui.message(_("Selector %s is free") %selector)
		self._initialize()

class SelectorsManagementDialog (wx.Dialog):
	shouldSuspendConfigProfileTriggers = True
	_instance = None
	title = None

	
		
	def __new__(cls, *args, **kwargs):
		if SelectorsManagementDialog ._instance is not None:
			return SelectorsManagementDialog ._instance
		return wx.Dialog.__new__(cls)
	
	def __init__(self, parent):
		if SelectorsManagementDialog ._instance is not None:
			return
		SelectorsManagementDialog ._instance = self
		self.switchVoiceProfile = SwitchVoiceProfile()
		self.selector = self.switchVoiceProfile.getLastSelector()
		profileName = config.conf.profiles[-1].name
		if profileName is  None:
			profileName = NVDAString("(normal configuration)")
		# Translators: This is the title  of  the Selectors Management dialog.
		dialogTitle = _("Voice profile selectors's Management  of configuration profile %s")
		title = SelectorsManagementDialog .title = makeAddonWindowTitle(dialogTitle%profileName)
		super(SelectorsManagementDialog , self).__init__(parent, -1, title)
		self.curSynth = self.switchVoiceProfile.curSynth
		self.selectorList = []
		for index in range(0,8):
			selector = str(index+1)
			if self.switchVoiceProfile.isSet(selector):
				newProfile = self.switchVoiceProfile.switchVoiceProfileSection [selector]
				voiceProfileName = newProfile["voiceProfileName"]
			else:
				voiceProfileName = _("free")
			self.selectorList.append("%s: %s"%(selector, voiceProfileName))
		self.doGui()
	
	def getCurrentSynthVoiceAndVariant(self):
		def getcurrentSettingName(setting):
			try:
				cur=getattr(synth,setting.name)
				l=getattr(synth,"available%ss"%setting.name.capitalize()).values()
				i=[x.ID for x in l].index(cur)
				return l[i].name
			except:
				return ""
		
		synth = speech.getSynth()
		voice = ""
		variant = ""
		for s in synth.supportedSettings:
			if s.name == "voice":
				voice = getcurrentSettingName(s)
			elif s.name == "variant":
				variant = getcurrentSettingName(s)
		
		return (voice, variant)
	
	def doGui(self):
		lastSelector =self.switchVoiceProfile.getLastSelector()
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label of  list box appearing in the Selectors Management dialog.
		selectorListLabelText=_("&Selectors:")
		self.selectorListBox =sHelper.addLabeledControl(selectorListLabelText, wx.ListBox,id = wx.ID_ANY, name= "Selectors" ,choices=self.selectorList) #, style = wx.LB_SINGLE |wx.LB_ALWAYS_SB|wx.WANTS_CHARS)
		self.selectorListBox.SetSelection(int(lastSelector)-1)
		bHelper= gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: This is a label of a button appearing on Selectors Management dialog.
		self.activateButton =  bHelper.addButton(self, label=_("&Activate voice profile"))
		# Translators: This is a label of a button appearing on Selectors Management dialog.
		self.associateButton =  bHelper.addButton(self, label=_("A&ssociate voice profile"))
		# Translators: This is a label of a button appearing on Selectors Management dialog.
		self.modifyButton =  bHelper.addButton(self, label=_("&Modify voice profile"))
		# Translators: This is a label of a button appearing on Selectors Management dialog.
		self.freeButton =  bHelper.addButton(self, label=_("&Free selector"))
		# Translators: This is a label of a button appearing on Selectors Management dialog.
		self.freeAllButton =  bHelper.addButton(self, label=_("&Free all selectors"))
		# Translators: This is a label of a button appearing on Selectors Management dialog.
		self.informationButton =  bHelper.addButton(self, label=_("Voice profile's &informations"))
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		closeButton= bHelper.addButton(self, id = wx.ID_CLOSE)
		mainSizer.Add(sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		#events
		self.selectorListBox.Bind(wx.EVT_LISTBOX, self.onSelectorSelection)
		self.selectorListBox.Bind(wx.EVT_SET_FOCUS, self.focusOnSelectorListBox)
		self.activateButton.Bind(wx.EVT_BUTTON,self.onActivateButton)
		self.associateButton.Bind(wx.EVT_BUTTON,self.onAssociateButton)
		self.modifyButton.Bind(wx.EVT_BUTTON,self.onModifyButton)
		self.freeButton.Bind(wx.EVT_BUTTON,self.onFreeButton)
		self.freeAllButton.Bind(wx.EVT_BUTTON,self.onFreeAllButton)
		self.informationButton.Bind(wx.EVT_BUTTON,self.onInformationButton)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)
		self.selectorListBox.SetFocus()
		self.updateButtons(lastSelector)
		isSet = False
		for index in range(1,_MAX_SELECTORS+1):
			selector = str(index)
			if self.switchVoiceProfile.isSet(selector):
				isSet = True
				break
		if isSet:
			self.freeAllButton.Enable()
		else:
			self.freeAllButton.Disable()
	
	def Destroy(self):
		SelectorsManagementDialog ._instance = None
		super(SelectorsManagementDialog , self).Destroy()
	
	def onInformationButton(self, evt):
		def boolToText(val):
			return _("yes") if val else _("no")
		def punctuationLevelToText(level):
			return characterProcessing.SPEECH_SYMBOL_LEVEL_LABELS[int(level)]
		NVDASpeechSettingsInfos = [
			(_("Automatic language switching (when supported)"), boolToText), 
			(_("Automatic dialect switching (when supported)"), boolToText),
			(_("Punctuation/symbol level"), punctuationLevelToText),
			(_("Trust voice's language when processing characters and symbols"), boolToText),
			]
		NVDASpeechManySettingsInfos = [
			(_("Capital pitch change percentage"), None),
			(_("Say cap before capitals"), boolToText),
			(_("Beep for capitals"), boolToText),
			(_("Use &spelling functionality if supported"), boolToText),
			]
		index = self.selectorListBox.GetSelection()
		selector = str(index+1)
		if not self.switchVoiceProfile.isSet(selector):
			return
		s = self.switchVoiceProfile.switchVoiceProfileSection [selector].copy()
		text = []
		text.append(_("selector: %s") %selector)
		text.append(_("Voice profile name: %s") %s["voiceProfileName"])
		synthName = s["synthName"]

		text.append(_("Synthetizer: %s") %synthName)
		text.append(_("Output device: %s")%s["outputDevice"])
		if "synthDisplayInfos" not in s :
			# Translators: message to user .
			ui.message(_("Voice profile Informations  cannot be displayed. You must  before, re-associate  the selector"))
			return

		synthClass = synthDriverHandler._getSynthDriver(synthName)
		supportedSettings = synthClass.supportedSettings
		for setting in supportedSettings:
			val = s["synthDisplayInfos"][setting.name]
			if isinstance(setting, synthDriverHandler.BooleanSynthSetting):
				val = boolToText(val)
			text.append("%s: %s" %(setting.displayName, val))

		for setting in SwitchVoiceProfile.NVDASpeechSettings:
			val = s[setting] 
			index = SwitchVoiceProfile.NVDASpeechSettings.index(setting)
			(name, f) = NVDASpeechSettingsInfos[index]
			if f is not None:
				val = f(val)
			text.append("%s: %s"%(name, val))
		for setting in SwitchVoiceProfile.NVDASpeechManySettings:
			val = s["config"][setting] 
			index = SwitchVoiceProfile.NVDASpeechManySettings.index(setting)
			(name, f) = NVDASpeechManySettingsInfos[index]
			if f is not None:
				val = f(val)
			text.append("%s: %s"%(name, val))			
		
		# Translators: this is the title of informationdialog box  to show voice profile informations.
		dialogTitle = _("Voice profile 's informations")
		InformationDialog.run (None, dialogTitle, "", "\r\n".join(text))
	
	def onActivateButton(self, evt):
		index = self.selectorListBox.GetSelection()
		core.callLater(200, self.switchVoiceProfile.setVoiceProfileSelector,index+1)
		self.Close()
		
	
	def onAssociateButton(self, evt):
		index = self.selectorListBox.GetSelection()
		selector = str(index+1)
		if self.switchVoiceProfile.isSet(selector):
			voiceProfileName = self.switchVoiceProfile.switchVoiceProfileSection [selector]["voiceProfileName"]
			if gui.messageBox(
				# Translators: the label of a message box dialog.
				_("Selector {selector} is already set to {voiceProfileName} voice profile. Do you want to replace this voice profile?") .format(selector= selector, voiceProfileName = voiceProfileName),
				# Translators: the title of a message box dialog.
				_("Confirmation"),
				wx.YES|wx.NO|wx.ICON_WARNING)==wx.NO:
					return
		with AssociateVoiceProfileDialog(self, selector) as associateVoiceProfileDialog:
			if associateVoiceProfileDialog.ShowModal() != wx.ID_OK:
				return
		
		core.callLater( 200,self.switchVoiceProfile.associateProfileToSelector,  selector, associateVoiceProfileDialog.voiceProfileName, associateVoiceProfileDialog.defaultVoiceProfileName)
		self.Close()
	
	def onModifyButton(self, evt):
		index = self.selectorListBox.GetSelection()
		selector = str(index+1)
		voiceProfile = self.switchVoiceProfile.switchVoiceProfileSection [selector]
		with ModifyVoiceProfileDialog(self, voiceProfile) as modifyVoiceProfileDialog:
			if modifyVoiceProfileDialog.ShowModal() != wx.ID_OK:
				return
			
			voiceProfileName = modifyVoiceProfileDialog.voiceProfileName
			self.selectorListBox.SetString(index, "%s: %s"%(str(index+1), voiceProfileName))
			voiceProfile["voiceProfileName"]=voiceProfileName 

	
	def onFreeButton(self, evt):
		index = self.selectorListBox.GetSelection() 
		selector = str(index+1)
		if not self.switchVoiceProfile.isSet(selector):
			return
		voiceProfileName = self.switchVoiceProfile.switchVoiceProfileSection [selector]["voiceProfileName"]
		if gui.messageBox(
			# Translators: the label of a message box dialog.
			_("Do you want realy free selector {selector} associated to voice profile {voiceProfileName}").format(selector= selector, voiceProfileName =voiceProfileName),
			# Translators: the title of a message box dialog.
			_("Confirmation"),
			wx.YES|wx.NO|wx.ICON_WARNING)==wx.NO:
			return
		
		self.switchVoiceProfile.freeSelector(selector)
		self.selectorListBox.SetString(index, "%s: %s"%(selector, _("free")))
		self.updateButtons(str(selector))
		self.selectorListBox.SetFocus()


		
		
		
	def onFreeAllButton(self, evt):
		
		if gui.messageBox(
			# Translators: the label of a message box dialog.
			_("Do you want realy free all selectors set to this configuration profile ?"),
			# Translators: the title of a message box dialog.
			_("Confirmation"),
			wx.YES|wx.NO|wx.ICON_WARNING)==wx.NO:
			return

		self.switchVoiceProfile.freeAllSelectors()
		for index in xrange(self.selectorListBox.Count):
			selector = str(index+1)
			self.selectorListBox.SetString(index, "%s: %s"%(selector, _("free")))
		selector = self.selectorListBox.GetSelection()+1
		self.updateButtons(str(selector))
		self.selectorListBox.SetFocus()


	def updateButtons(self, selector):
		if self.switchVoiceProfile.isSet(selector):
			self.activateButton.Enable()
			self.activateButton.SetDefault()
			self.modifyButton.Enable()
			self.freeButton.Enable()
			self.informationButton.Enable()
		else:
			self.associateButton.SetDefault()
			self.activateButton.Disable()
			self.modifyButton.Disable()
			self.freeButton.Disable()
			self.informationButton.Disable()
		enable = False
		for index in xrange(self.selectorListBox.Count):
			selector = str(index+1)
			if self.switchVoiceProfile.isSet(selector):
				enable = True
				break
		if enable:
			self.freeAllButton.Enable()
		else:
			self.freeAllButton.Disable()
	
	def focusOnSelectorListBox(self, evt):
		selector = self.selectorListBox.GetSelection()+1
		self.updateButtons(str(selector))

	def onSelectorSelection(self, evt):
		selector = self.selectorListBox.GetSelection()+1
		self.updateButtons(str(selector))
	
	@classmethod
	def run(cls, obj):
		if cls._instance is not None:
			msg = _("%s dialog is allready open") %cls.title
			queueHandler.queueFunction(queueHandler.eventQueue, speech.speakMessage, msg)
			return

		gui.mainFrame.prePopup()
		d =   cls(gui.mainFrame)
		d.CentreOnScreen()
		d.ShowModal()
		gui.mainFrame.postPopup()


class ModifyVoiceProfileDialog(wx.Dialog):
	# Translators: This is the title  of  the modify voice profile dialog.
	title = _("Modify voice profile ")
	
	def __init__(self, parent, voiceProfile):
		super(ModifyVoiceProfileDialog,self).__init__(parent, title=self.title )
		self.voiceProfile = voiceProfile
		voiceProfileName = voiceProfile["voiceProfileName"]
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label of the edit field appearing in the Modify voice profile dialog.
		voiceProfileNameEditLabelText = _("voice profile name:")
		self.voiceProfileNameEdit = sHelper.addLabeledControl(voiceProfileNameEditLabelText, wx.TextCtrl)
		self.voiceProfileNameEdit .AppendText(voiceProfileName)
		bHelper= gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: This is a label of a button appearing on modify voice profile Dialog.
		defaultButton =  bHelper.addButton(self, label=_("&Default"))
		sHelper.addItem(bHelper)
		sHelper.addDialogDismissButtons(self.CreateButtonSizer(wx.OK|wx.CANCEL))
		mainSizer.Add(sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		defaultButton.Bind(wx.EVT_BUTTON,self.onDefaultButton)
		self.Bind(wx.EVT_BUTTON,self.onOk,id=wx.ID_OK)
		self.voiceProfileNameEdit.SetFocus()
		self.CentreOnScreen()
	
	def onDefaultButton(self, evt):
		self.voiceProfileNameEdit .Clear()
		self.voiceProfileNameEdit .AppendText(self.voiceProfile["defaultVoiceProfileName"])
		self.voiceProfileNameEdit .SetFocus()
		evt.Skip()
	def onOk(self, evt):
		voiceProfileName = self.voiceProfileNameEdit.GetValue()
		if len(voiceProfileName) == 0:
			core.callLater(200,ui.message, _("You must set the name of voice profile"))
			return

		self.voiceProfileName = voiceProfileName
		evt.Skip()


class AssociateVoiceProfileDialog(wx.Dialog):
	# Translators: This is the title  of  the Associate voice profile dialog.
	title = _("Voice profile association")
	
	def __init__(self, parent, selector):
		super(AssociateVoiceProfileDialog,self).__init__(parent, title=self.title )
		self.parent = parent
		self.selector = selector
		synthName = self.parent.switchVoiceProfile.curSynth.name
		(voice,variant) = self.getCurrentSynthVoiceAndVariant()
		self.defaultVoiceProfileName = "%s %s %s"%(synthName , voice , variant)
		self.voice = voice
		self.variant = variant

		mainSizer=wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label of the edit field appearing in the associate voice profile dialog.
		voiceProfileNameEditLabelText = _("voice profile name:")
		self.voiceProfileNameEdit = sHelper.addLabeledControl(voiceProfileNameEditLabelText, wx.TextCtrl)
		self.voiceProfileNameEdit .AppendText(self.defaultVoiceProfileName)
		bHelper= gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: This is a label of a button appearing on associate voice profile dialog.
		defaultButton =  bHelper.addButton(self, label=_("&Default"))
		sHelper.addItem(bHelper)
		sHelper.addDialogDismissButtons(self.CreateButtonSizer(wx.OK|wx.CANCEL))
		mainSizer.Add(sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		defaultButton.Bind(wx.EVT_BUTTON,self.onDefaultButton)
		self.Bind(wx.EVT_BUTTON,self.onOk,id=wx.ID_OK)
		self.voiceProfileNameEdit.SetFocus()
		self.CentreOnScreen()
		
	def getCurrentSynthVoiceAndVariant(self):
		def getcurrentSettingName(setting):
			try:
				cur=getattr(synth,setting.name)
				l=getattr(synth,"available%ss"%setting.name.capitalize()).values()
				i=[x.ID for x in l].index(cur)
				return l[i].name
			except:
				return ""
		
		synth = self.parent.switchVoiceProfile.curSynth
		voice = ""
		variant = ""
		for s in synth.supportedSettings:
			if s.name == "voice":
				voice = getcurrentSettingName(s)
			elif s.name == "variant":
				variant = getcurrentSettingName(s)
		
		return (voice, variant)

	
	def onDefaultButton(self, evt):
		self.voiceProfileNameEdit .Clear()
		self.voiceProfileNameEdit .AppendText(self.defaultVoiceProfileName)
		self.voiceProfileNameEdit .SetFocus()
		evt.Skip()
	
	def onOk(self, evt):
		voiceProfileName = self.voiceProfileNameEdit.GetValue()
		if len(voiceProfileName) == 0:
			core.callLater(200,ui.message, _("You must set the name of voice profile"))
			return
		
		self.voiceProfileName = voiceProfileName
		evt.Skip()

