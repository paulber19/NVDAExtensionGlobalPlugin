#NVDAExtensionGlobalPlugin/settings/dialog.py
# a part of NVDAExtensionGlobalPlugin add-on
#Copyright (C) 2016-2017  Paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import addonHandler
addonHandler.initTranslation()
import wx
from ..utils.NVDAStrings import NVDAString
from gui.settingsDialogs import SettingsDialog, MultiCategorySettingsDialog, SettingsPanel
from gui import nvdaControls
import gui
from ..settings import _addonConfigManager
from addonConfig import *
from . import *
import core
import characterProcessing
import queueHandler
from ..utils import makeAddonWindowTitle



def askForNVDARestart():

	if gui.messageBox(
		# Translators: A message asking the user if they wish to restart NVDA as NVDAExtensionGlobalPlugin addon settings changes have been made. 
		_("Some Changes have been made . You must restart NVDA for these changes to take effect. Would you like to restart now?"),
		makeAddonWindowTitle(NVDAString("Restart NVDA")),
		wx.YES|wx.NO|wx.ICON_WARNING)==wx.YES:
		queueHandler.queueFunction(queueHandler.eventQueue,core.restart)

class FeaturesInstallationSettingsPanel(SettingsPanel):
	# Translators: This is the label for the Installed features dialog.
	title = _("features's installation")
	def __init__(self, parent):
		self.title = makeAddonWindowTitle(self.title)
		super(FeaturesInstallationSettingsPanel, self).__init__(parent)	
	def makeSettings(self, settingsSizer):
		installChoiceLabels = {
		C_DoNotInstall: _("Do not install"),
		C_Install : _("Install"),
		C_InstallWithoutGesture: _("Install without gesture"),
		}
		installChoice =  [installChoiceLabels[x] for x in [C_DoNotInstall, C_Install, C_InstallWithoutGesture]]
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a listbox in the Installed features dialog.
		labelText = _("Display &systray icons and running application windows lists:")
		self.installSystrayIconsListFeatureOptionBox = sHelper.addLabeledControl(labelText , wx.Choice, choices= installChoice)
		self.installSystrayIconsListFeatureOptionBox .SetSelection(getInstallFeatureOption (ID_SystrayIconsAndActiveWindowsList))
		# Translators: This is the label for a listbox in the Installed features dialog.
		labelText = _("&complex symbols edition help:")
		self.installComplexSymbolsFeatureOptionBox = sHelper.addLabeledControl(labelText , wx.Choice, choices= installChoice)
		self.installComplexSymbolsFeatureOptionBox .SetSelection(getInstallFeatureOption (ID_ComplexSymbols ))
		# Translators: This is the label for a listbox in the Installed features dialog.
		labelText = _("&Focused Application's informations:")
		self.installFocusedApplicationInformationsFeatureOptionBox  = sHelper.addLabeledControl(labelText , wx.Choice, choices= installChoice)
		self.installFocusedApplicationInformationsFeatureOptionBox   .SetSelection(getInstallFeatureOption (ID_FocusedApplicationInformations))
		# Translators: This is the label for a listbox in the Installed features dialog.
		labelText = _("&Extended Virtual Buffer:")
		self.installExtendedVirtualBufferFeaturesOptionBox = sHelper.addLabeledControl(labelText , wx.Choice, choices= installChoice[:-1])
		self.installExtendedVirtualBufferFeaturesOptionBox .SetSelection(getInstallFeatureOption (ID_ExtendedVirtualBuffer))
		# Translators: This is the label for a listbox in the Installed features dialog.
		labelText = _("c&lipboard command announcement:")
		self.installClipboardCommandAnnouncementFeatureOptionBox  = sHelper.addLabeledControl(labelText , wx.Choice, choices= installChoice[:-1])
		self.installClipboardCommandAnnouncementFeatureOptionBox .SetSelection(getInstallFeatureOption (ID_ClipboardCommandAnnouncement  ))
		# Translators: This is the label for a listbox in the Installed features dialog.		
		labelText= _("C&urrent folder report:")
		self.installCurrentFolderReportFeatureOptionBox  = sHelper.addLabeledControl(labelText , wx.Choice, choices= installChoice)
		self.installCurrentFolderReportFeatureOptionBox .SetSelection(getInstallFeatureOption (ID_CurrentFolderReport   ))
		# Translators: This is the label for a listbox in the Installed features dialog.
		labelText = _("&NVDA's log Files:")
		self.installOpenCurrentOrOldNVDALogFileFeatureOptionBox  = sHelper.addLabeledControl(labelText , wx.Choice, choices= installChoice)
		self.installOpenCurrentOrOldNVDALogFileFeatureOptionBox   .SetSelection(getInstallFeatureOption (ID_OpenCurrentOrOldNVDALogFile))
		# Translators: This is the label for a listbox in the Installed features dialog.
		labelText = _("Speech &history:")
		self.installSpeechHistoryFeatureOptionBox  = sHelper.addLabeledControl(labelText , wx.Choice, choices= installChoice)
		self.installSpeechHistoryFeatureOptionBox   .SetSelection(getInstallFeatureOption (ID_SpeechHistory))
		# Translators: This is the label for a listbox in the Installed features dialog.
		labelText = _("&Keyboard Key renaming:")
		self.installKeyboardKeyRenamingFeatureOptionBox  = sHelper.addLabeledControl(labelText , wx.Choice, choices= installChoice[:-1])
		self.installKeyboardKeyRenamingFeatureOptionBox   .SetSelection(getInstallFeatureOption (ID_KeyboardKeyRenaming))
		# Translators: This is the label for a listbox in the Installed features dialog.
		labelText = _("C&ommand keys selective announcement:")
		self.installCommandKeysSelectiveAnnouncementFeatureOptionBox = sHelper.addLabeledControl(labelText , wx.Choice, choices= installChoice[:-1])
		self.installCommandKeysSelectiveAnnouncementFeatureOptionBox   .SetSelection(getInstallFeatureOption (ID_CommandKeysSelectiveAnnouncement ))
		# Translators: This is the label for a listbox in the Installed features dialog.
		labelText = _("Minute &timer:")
		self.installMinuteTimerFeatureOptionBox = sHelper.addLabeledControl(labelText , wx.Choice, choices= installChoice)
		self.installMinuteTimerFeatureOptionBox   .SetSelection(getInstallFeatureOption (ID_MinuteTimer ))
		# Translators: This is the label for a listbox in the Installed features dialog.
		labelText = _("NVDA's &restart:")
		self.installRestartInDebugModeFeatureOptionBox = sHelper.addLabeledControl(labelText , wx.Choice, choices= installChoice)
		self.installRestartInDebugModeFeatureOptionBox   .SetSelection(getInstallFeatureOption (ID_RestartInDebugMode ))
		# Translators: This is the label for a listbox in the Installed features dialog.
		labelText = _("Display visible items making up the foreground &object:")
		self.installForegroundWindowObjectsListFeatureOptionBox = sHelper.addLabeledControl(labelText , wx.Choice, choices= installChoice)
		self.installForegroundWindowObjectsListFeatureOptionBox   .SetSelection(getInstallFeatureOption (ID_ForegroundWindowObjectsList))
		# Translators: This is the label for a listbox in the Installed features dialog.
		labelText = _("&Voice profil switching:")
		self.installVoiceProfileSwitchingFeatureOptionBox = sHelper.addLabeledControl(labelText , wx.Choice, choices= installChoice)
		self.installVoiceProfileSwitchingFeatureOptionBox   .SetSelection(getInstallFeatureOption (ID_VoiceProfileSwitching ))
		# Translators: This is the label for a listbox in the Installed features dialog.
		labelText = _("Ke&ys's remanence:")
		self.installKeyRemanenceFeatureOptionBox = sHelper.addLabeledControl(labelText , wx.Choice, choices= installChoice[:-1])
		self.installKeyRemanenceFeatureOptionBox   .SetSelection(getInstallFeatureOption (ID_KeyRemanence ))
		# Translators: This is the label for a listbox in the Installed features dialog.
		labelText = _("Volu&me's control:")
		self.installVolumeControlFeatureOptionBox = sHelper.addLabeledControl(labelText , wx.Choice, choices= installChoice)
		self.installVolumeControlFeatureOptionBox   .SetSelection(getInstallFeatureOption (ID_VolumeControl))
		# Translators: This is the label for a listbox in the Installed features dialog.
		labelText = _("&Developpement's tools")
		self.installDevToolsFeatureOptionBox = sHelper.addLabeledControl(labelText , wx.Choice, choices= installChoice[:-1])
		self.installDevToolsFeatureOptionBox   .SetSelection(getInstallFeatureOption (ID_Tools))	
	#def postInit(self):
		#self.installSystrayIconsListFeatureOptionBox .SetFocus()
	def saveSettingChanges (self):
		self.restartNVDA = False
		if self.installExtendedVirtualBufferFeaturesOptionBox.GetSelection() != getInstallFeatureOption (ID_ExtendedVirtualBuffer):
			setInstallFeatureOption (ID_ExtendedVirtualBuffer,self.installExtendedVirtualBufferFeaturesOptionBox.GetSelection()  )
			if getInstallFeatureOption (ID_ExtendedVirtualBuffer) == C_Install:
				# set LoopInNavigationModeOption to default state (False)
				if toggleLoopInNavigationModeOption(False): toggleLoopInNavigationModeOption(True)
				
			self.restartNVDA = True
		if self.installSystrayIconsListFeatureOptionBox.GetSelection() != getInstallFeatureOption (ID_SystrayIconsAndActiveWindowsList):
			setInstallFeatureOption (ID_SystrayIconsAndActiveWindowsList, self.installSystrayIconsListFeatureOptionBox.GetSelection() )
			self.restartNVDA = True
		if self.installComplexSymbolsFeatureOptionBox.GetSelection() != getInstallFeatureOption (ID_ComplexSymbols):
			setInstallFeatureOption (ID_ComplexSymbols, self.installComplexSymbolsFeatureOptionBox.GetSelection() )
			self.restartNVDA = True
		if self.installClipboardCommandAnnouncementFeatureOptionBox.GetSelection() != getInstallFeatureOption (ID_ClipboardCommandAnnouncement  ):
			setInstallFeatureOption (ID_ClipboardCommandAnnouncement  , self.installClipboardCommandAnnouncementFeatureOptionBox.GetSelection() )
			self.restartNVDA = True
		if self.installCurrentFolderReportFeatureOptionBox.GetSelection() != getInstallFeatureOption (ID_CurrentFolderReport):
			setInstallFeatureOption (ID_CurrentFolderReport , self.installCurrentFolderReportFeatureOptionBox.GetSelection() )
			self.restartNVDA = True
		if self.installFocusedApplicationInformationsFeatureOptionBox.GetSelection() != getInstallFeatureOption (ID_FocusedApplicationInformations):
			setInstallFeatureOption (ID_FocusedApplicationInformations, self.installFocusedApplicationInformationsFeatureOptionBox.GetSelection() )
			self.restartNVDA = True
		if self.installOpenCurrentOrOldNVDALogFileFeatureOptionBox.GetSelection() != getInstallFeatureOption (ID_OpenCurrentOrOldNVDALogFile):
			setInstallFeatureOption (ID_OpenCurrentOrOldNVDALogFile, self.installOpenCurrentOrOldNVDALogFileFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		if self.installSpeechHistoryFeatureOptionBox.GetSelection() != getInstallFeatureOption (ID_SpeechHistory):
			setInstallFeatureOption (ID_SpeechHistory, self.installSpeechHistoryFeatureOptionBox.GetSelection() )
			self.restartNVDA = True
		if self.installKeyboardKeyRenamingFeatureOptionBox.GetSelection() != getInstallFeatureOption (ID_KeyboardKeyRenaming):
			setInstallFeatureOption (ID_KeyboardKeyRenaming, self.installKeyboardKeyRenamingFeatureOptionBox.GetSelection() )
			self.restartNVDA = True
		if self.installCommandKeysSelectiveAnnouncementFeatureOptionBox.GetSelection() != getInstallFeatureOption (ID_CommandKeysSelectiveAnnouncement):
			setInstallFeatureOption (ID_CommandKeysSelectiveAnnouncement, self.installCommandKeysSelectiveAnnouncementFeatureOptionBox.GetSelection() )
			self.restartNVDA = True
		if self.installMinuteTimerFeatureOptionBox.GetSelection() != getInstallFeatureOption (ID_MinuteTimer):
			setInstallFeatureOption (ID_MinuteTimer, self.installMinuteTimerFeatureOptionBox.GetSelection() )
			self.restartNVDA = True
		if self.installForegroundWindowObjectsListFeatureOptionBox.GetSelection() != getInstallFeatureOption (ID_ForegroundWindowObjectsList):
			setInstallFeatureOption (ID_ForegroundWindowObjectsList, self.installForegroundWindowObjectsListFeatureOptionBox.GetSelection() )
			self.restartNVDA = True
		if self.installVoiceProfileSwitchingFeatureOptionBox.GetSelection() != getInstallFeatureOption (ID_VoiceProfileSwitching):
			setInstallFeatureOption (ID_VoiceProfileSwitching, self.installVoiceProfileSwitchingFeatureOptionBox.GetSelection() )
			self.restartNVDA = True
		if self.installKeyRemanenceFeatureOptionBox.GetSelection() != getInstallFeatureOption (ID_KeyRemanence):
			setInstallFeatureOption (ID_KeyRemanence, self.installKeyRemanenceFeatureOptionBox.GetSelection() )
			self.restartNVDA = True
		if self.installRestartInDebugModeFeatureOptionBox.GetSelection() != getInstallFeatureOption (ID_RestartInDebugMode ):
			setInstallFeatureOption (ID_RestartInDebugMode , self.installRestartInDebugModeFeatureOptionBox.GetSelection() )
			self.restartNVDA = True
		if self.installVolumeControlFeatureOptionBox.GetSelection() != getInstallFeatureOption (ID_VolumeControl):
			setInstallFeatureOption (ID_VolumeControl, self.installVolumeControlFeatureOptionBox.GetSelection() )
			self.restartNVDA = True
		if self.installDevToolsFeatureOptionBox.GetSelection() != getInstallFeatureOption (ID_Tools):
			setInstallFeatureOption (ID_Tools, self.installDevToolsFeatureOptionBox.GetSelection() )
			self.restartNVDA = True
	
	def postSave(self):
		if self.restartNVDA:
			askForNVDARestart()

	def onSave(self):
		self.saveSettingChanges()


class OptionsSettingsPanel(SettingsPanel):
	# Translators: This is the label for the options settings  dialog.
	title = _("Options")
	def __init__(self, parent):
		self.title = makeAddonWindowTitle(self.title)
		super(OptionsSettingsPanel, self).__init__(parent)	
	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a checkbox in the Options dialog.
		labelText = _("&No object description inWindows ribbons")
		self.noDescriptionReportInRibbonOptionBox=sHelper.addItem (wx.CheckBox(self,wx.ID_ANY, label= labelText))
		self.noDescriptionReportInRibbonOptionBox.SetValue(toggleNoDescriptionReportInRibbonOption (False))
		# Translators: This is the label for a checkbox in the Options dialog.
		labelText = _("&Report next word on deletion")
		self.ReportNextWordOnDeletionOptionBox=sHelper.addItem (wx.CheckBox(self,wx.ID_ANY, label= labelText))
		self.ReportNextWordOnDeletionOptionBox.SetValue(toggleReportNextWordOnDeletionOption (False))
		# Translators: This is the label for a checkbox in the Options dialog.
		labelText = _("Automatically &maximize windows")
		self.AutomaticWindowMaximizationOptionBox=sHelper.addItem (wx.CheckBox(self,wx.ID_ANY, label= labelText))
		self.AutomaticWindowMaximizationOptionBox.SetValue(toggleAutomaticWindowMaximizationOption (False))
		# Translators: This is the label for a combobox in the
		# options dialog (possible choices are none, some, most and all).
		labelText = _("&Punctuation/symbol &level on word movement:")
		symbolLevelLabels=characterProcessing.SPEECH_SYMBOL_LEVEL_LABELS
		symbolLevelChoices= [symbolLevelLabels[level] for level in characterProcessing.CONFIGURABLE_SPEECH_SYMBOL_LEVELS]
		# Translators: This is the label for an item  in combobox in the
		# options dialog (possible choices are Current configuration Profil s level, none, some, most and all).
		symbolLevelChoices = [_("Current configuration profil's level"),] + symbolLevelChoices[:]
		self.symbolLevelList = sHelper.addLabeledControl(labelText, wx.Choice, choices=symbolLevelChoices)
		from ..settings import _addonConfigManager
		symbolLevelOnWordCaretMovement = _addonConfigManager .getSymbolLevelOnWordCaretMovement()
		if symbolLevelOnWordCaretMovement   is None:
			self.symbolLevelList.SetSelection(0)
		else:
			self.symbolLevelList.SetSelection(1+characterProcessing.CONFIGURABLE_SPEECH_SYMBOL_LEVELS.index((symbolLevelOnWordCaretMovement )))
		# Translators: This is the label for a checkbox in the Options dialog.
		labelText = _("Report &windows clock's time with seconds")
		self.reportTimeWithSecondsOptionBox=sHelper.addItem (wx.CheckBox(self,wx.ID_ANY, label= labelText))
		self.reportTimeWithSecondsOptionBox.SetValue(toggleReportTimeWithSecondsOption (False))
		# Translators: This is the label for a checkbox in the Options dialog.
		labelText = _("&Number the records of speech history")
		self.speechRecordWithNumberOptionBox=sHelper.addItem (wx.CheckBox(self,wx.ID_ANY, label= labelText))
		self.speechRecordWithNumberOptionBox.SetValue(toggleSpeechRecordWithNumberOption (False))	
		if getInstallFeatureOption (ID_ExtendedVirtualBuffer):
			# Translators: This is the label for a checkbox in the Options dialog.
			labelText = _("Na&vigate in loop")
			self.loopInNavigationModeOptionBox=sHelper.addItem (wx.CheckBox(self,wx.ID_ANY, label= labelText))
			self.loopInNavigationModeOptionBox.SetValue(toggleLoopInNavigationModeOption(False))
	def saveSettingChanges (self):
		self.restartNVDA = False
		if self.ReportNextWordOnDeletionOptionBox.IsChecked() != toggleReportNextWordOnDeletionOption(False):
			toggleReportNextWordOnDeletionOption()
		if self.noDescriptionReportInRibbonOptionBox.IsChecked() != toggleNoDescriptionReportInRibbonOption(False):
			toggleNoDescriptionReportInRibbonOption()
			self.restartNVDA = True
		if self.AutomaticWindowMaximizationOptionBox.IsChecked() != toggleAutomaticWindowMaximizationOption (False):
			toggleAutomaticWindowMaximizationOption ()
		if self.symbolLevelList.GetSelection() == 0  :
			from . import _addonConfigManager 
			_addonConfigManager .saveSymbolLevelOnWordCaretMovement(None)
		else:
			from . import _addonConfigManager 
			_addonConfigManager .saveSymbolLevelOnWordCaretMovement(characterProcessing.CONFIGURABLE_SPEECH_SYMBOL_LEVELS[self.symbolLevelList.GetSelection()-1])
		if self.reportTimeWithSecondsOptionBox.IsChecked() != toggleReportTimeWithSecondsOption (False):
			toggleReportTimeWithSecondsOption ()
		if self.speechRecordWithNumberOptionBox.IsChecked() != toggleSpeechRecordWithNumberOption (False):
			toggleSpeechRecordWithNumberOption ()
		if getInstallFeatureOption (ID_ExtendedVirtualBuffer) and (self.loopInNavigationModeOptionBox.IsChecked() != toggleLoopInNavigationModeOption(False)):
			toggleLoopInNavigationModeOption()
	
	def postSave(self):
		if self.restartNVDA:
			askForNVDARestart()
	
	def onSave(self):
		self.saveSettingChanges()
		#super(OptionsSettingsPanel, self).onSave(evt)

class AdvancedOptionsSettingsPanel(SettingsPanel):
	# Translators: This is the label for the Advanced options settings  dialog.
	title = _("advanced  options")
	
	_playSoundOnErrorsOptionLabels = [ # becarefull: order is important
		# Translators: This is a label for a choice item  in Advanced options settings  dialog.
		_("For No NVDA's version"), # PSOE_NoVersion
		# Translators: This is a label for a choice item  in Advanced options settings  dialog.
		_("For Only the NVDA's snapshot versions"),# PSOE_SnapshotVersions
		# Translators: This is a label for a choice item  in Advanced options settings  dialog.
		_("Only until the next NVDA restart"),# PSOE_UntilNVDARestart
		# Translators: This is a label for a choice item  in Advanced options settings  dialog.
		_("For all NVDA's versions"),# PSOE_AllVersions
		]
	_remanenceDelayLimits = (1000, 5000)
	_repeatBeepOnAudioDevicesDelayLimits = (1, 60)
	def __init__(self, parent ):
		self.globalPlugin = None
		self.title = makeAddonWindowTitle(self.title)
		super(AdvancedOptionsSettingsPanel, self).__init__(parent)
	
	def makeSettings(self, settingsSizer):
		from ..settings import _addonConfigManager, PSOE_NoVersion, PSOE_AllVersions
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a choice box in the advanced options dialog.
		labelText = _("&Play sound on logged errors:")
		self.playSoundOnErrorsOptionChoiceBox = sHelper.addLabeledControl(labelText , wx.Choice, choices=self._playSoundOnErrorsOptionLabels)
		# Translators: This is a label for a  edit box in Advanced Options dialog.
		labelText=_("&Remanence's delay (in milliseconds):")
		self.remanenceDelayChoice  = [100*(10+5*(x-1)) for x in range(1, 10)]
		self.remanenceDelayBox  = sHelper.addLabeledControl(labelText, wx.Choice, choices= [str(x) for x in self.remanenceDelayChoice  ])
		self.remanenceDelayBox  .SetSelection(self.remanenceDelayChoice.index(_addonConfigManager.getRemanenceDelay()))
		if not getInstallFeatureOption (ID_KeyRemanence):
			self.remanenceDelayBox .Disable()

		isTestVersion = _addonConfigManager.getPlaySoundOnErrorsOption ()
		self.playSoundOnErrorsOptionChoiceBox.SetSelection(isTestVersion)
				# Translators: This is the label for a check box in the advanced options dialog.
		labelText = _("Play &sound at the start of remanence")
		self.beepAtRemanenceStartOptionCheckBox =sHelper.addItem (wx.CheckBox(self,wx.ID_ANY, label= labelText ))
		self.beepAtRemanenceStartOptionCheckBox .SetValue(toggleBeepAtRemanenceStartAdvancedOption (False))
		if not getInstallFeatureOption (ID_KeyRemanence):
			self.beepAtRemanenceStartOptionCheckBox .Disable()
		# Translators: This is the label for a check box in the advanced options dialog.
		labelText = _("Play sound at the &end of remanence")
		self.beepAtRemanenceEndOptionCheckBox =sHelper.addItem (wx.CheckBox(self,wx.ID_ANY, label= labelText ))
		self.beepAtRemanenceEndOptionCheckBox .SetValue(toggleBeepAtRemanenceEndAdvancedOption (False))
		if not getInstallFeatureOption (ID_KeyRemanence):
			self.beepAtRemanenceEndOptionCheckBox .Disable()
		# Translators: This is the label for a checkbox in the advanced Options dialog.
		labelText = _("Set on &main and NVDA volume at the loading of the module")
		self.setOnMainAndNVDAVolumeOptionCheckBox=sHelper.addItem (wx.CheckBox(self,wx.ID_ANY, label= labelText))
		self.setOnMainAndNVDAVolumeOptionCheckBox.SetValue(toggleSetOnMainAndNVDAVolumeAdvancedOption(False))
		# Translators: This is a label for a  choice box in Advanced Options dialog.
		labelText=_("&Minimum main volume level:")
		choice = [10*x for x in reversed (range(0, 11))]
		self.minMasterVolumeLevelBox  = sHelper.addLabeledControl(labelText, wx.Choice, choices= [str(x) for x in choice[5:]])
		self.minMasterVolumeLevelBox  .SetSelection(choice[5:].index(_addonConfigManager.getMinMasterVolumeLevel()))
		# Translators: This is a label for a  choice box in Advanced Options dialog.
		labelText=_("Main volume &level:")
		self.masterVolumeLevelBox  = sHelper.addLabeledControl(labelText, wx.Choice, choices= [str(x) for x in choice  ])
		self.masterVolumeLevelBox  .SetSelection(choice.index(_addonConfigManager.getMasterVolumeLevel()))
		# Translators: This is a label for a  choice box in Advanced Options dialog.
		labelText=_("Minimum &NVDA volume level:")
		self.minNVDAVolumeLevelBox  = sHelper.addLabeledControl(labelText, wx.Choice, choices= [str(x) for x in choice[5:]  ])
		self.minNVDAVolumeLevelBox  .SetSelection(choice[5:].index(_addonConfigManager.getMinNVDAVolumeLevel()))
		# Translators: This is a label for a  choice box in Advanced Options dialog.
		labelText=_("NVDA &volume level:")
		self.NVDAVolumeLevelBox  = sHelper.addLabeledControl(labelText, wx.Choice, choices= [str(x) for x in choice[5:]  ])
		self.NVDAVolumeLevelBox  .SetSelection(choice[5:].index(_addonConfigManager.getNVDAVolumeLevel()))
		# Translators: This is the label for a checkbox in the Options dialog.
		labelText = _("&Title dialog with add-on name")
		self.dialogTitleWithAddonSummaryOptionBox=sHelper.addItem (wx.CheckBox(self,wx.ID_ANY, label= labelText))
		self.dialogTitleWithAddonSummaryOptionBox.SetValue(toggleDialogTitleWithAddonSummaryAdvancedOption (False))
		# Translators: This is the label for a choicebox in the advanced Options dialog.
		labelText = _("&Delay between repeat of same gesture:")
		choice = [100, 150, 200, 250, 300, 350, 400,450, 500]
		self.delayBetweenSameGestureBox  = sHelper.addLabeledControl(labelText, wx.Choice, choices= [str(x) for x in choice])
		self.delayBetweenSameGestureBox  .SetSelection(choice.index(_addonConfigManager.getDelayBetweenSameGesture()))
		# Translators: This is the label for a choicebox in the advanced Options dialog.
		labelText = _("maximum number of last &used symbols recorded:")
		choice = [x*10 for x in range(1, 11)]
		self.maximumOfLastUsedSymbolsBox= sHelper.addLabeledControl(labelText, wx.Choice, choices= [str(x) for x in choice])
		self.maximumOfLastUsedSymbolsBox.SetSelection(choice.index(_addonConfigManager.getMaximumOfLastUsedSymbols()))
		# Translators: This is the label for a checkbox in the Options dialog.
		labelText = _("&Does not take account of the option to Announce the description of the object during the display of the dialog box style confirmation")
		self.byPassNoDescriptionOptionBox=sHelper.addItem (wx.CheckBox(self,wx.ID_ANY, label= labelText))
		self.byPassNoDescriptionOptionBox.SetValue(toggleByPassNoDescriptionAdvancedOption (False))
	
	def saveSettingChanges (self):
		self.restartNVDA = False
		playSoundOnErrorsOption = self.playSoundOnErrorsOptionChoiceBox.GetSelection()
		_addonConfigManager.setPlaySoundOnErrorsOption(playSoundOnErrorsOption)
		remanenceDelay = self.remanenceDelayBox.GetSelection()
		_addonConfigManager.setRemanenceDelay(self.remanenceDelayChoice[remanenceDelay])
		if self.beepAtRemanenceStartOptionCheckBox.IsChecked() != toggleBeepAtRemanenceStartAdvancedOption (False):
			toggleBeepAtRemanenceStartAdvancedOption ()
		if self.setOnMainAndNVDAVolumeOptionCheckBox.IsChecked() != toggleSetOnMainAndNVDAVolumeAdvancedOption (False):
			toggleSetOnMainAndNVDAVolumeAdvancedOption ()
		if self.beepAtRemanenceEndOptionCheckBox.IsChecked() != toggleBeepAtRemanenceEndAdvancedOption (False):
			toggleBeepAtRemanenceEndAdvancedOption ()
		if self.dialogTitleWithAddonSummaryOptionBox.IsChecked() != toggleDialogTitleWithAddonSummaryAdvancedOption (False):
			toggleDialogTitleWithAddonSummaryAdvancedOption ()
		levelString = self.minMasterVolumeLevelBox.GetString(self.minMasterVolumeLevelBox.GetSelection())
		_addonConfigManager.setMinMasterVolumeLevel(int(levelString))
		levelString = self.masterVolumeLevelBox.GetString(self.masterVolumeLevelBox.GetSelection())
		_addonConfigManager.setMasterVolumeLevel(int(levelString))
		levelString = self.NVDAVolumeLevelBox.GetString(self.minNVDAVolumeLevelBox.GetSelection())
		_addonConfigManager.setMinNVDAVolumeLevel(int(levelString))
		levelString = self.NVDAVolumeLevelBox.GetString(self.NVDAVolumeLevelBox.GetSelection())
		_addonConfigManager.setNVDAVolumeLevel(int(levelString))
		delayBetweenSameGesture = int(self.delayBetweenSameGestureBox.GetString(self.delayBetweenSameGestureBox.GetSelection()))
		if delayBetweenSameGesture  != _addonConfigManager.getDelayBetweenSameGesture():
			_addonConfigManager.setDelayBetweenSameGesture(delayBetweenSameGesture)
			self.restartNVDA = True
		maximumOfLastUsedSymbols= int(self.maximumOfLastUsedSymbolsBox.GetString(self.maximumOfLastUsedSymbolsBox.GetSelection()))
		_addonConfigManager.setMaximumOfLastUsedSymbols(maximumOfLastUsedSymbols)
		if self.byPassNoDescriptionOptionBox.IsChecked() != toggleByPassNoDescriptionAdvancedOption (False):
			toggleByPassNoDescriptionAdvancedOption ()
			self.restartNVDA = True
	
	def postSave(self):
		if self.restartNVDA:
			askForNVDARestart()		
	def onSave(self):
		self.saveSettingChanges()

	#super(AdvancedOptionsSettingsPanel, self).onSave(evt)

class AddonSettingsDialog(MultiCategorySettingsDialog):
	categoryClasses=[
		FeaturesInstallationSettingsPanel,
		OptionsSettingsPanel,
		AdvancedOptionsSettingsPanel,
		]
	
	def __init__(self, parent, initialCategory=None):
		curAddon = addonHandler.getCodeAddon()
		# Translators: title of add-on parameters dialog.
		dialogTitle = _("Parameters")
		self.title = makeAddonWindowTitle(dialogTitle)
		super(AddonSettingsDialog,self).__init__(parent, initialCategory)
		