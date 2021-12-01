# globalPlugins\NVDAExtensionGlobalPlugin\settings\dialog.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2021 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import globalVars
import wx
import nvwave
from gui.settingsDialogs import MultiCategorySettingsDialog, SettingsPanel
import gui
from gui import nvdaControls
import core
import characterProcessing
import queueHandler
from languageHandler import getLanguage
from ..settings import _addonConfigManager
from ..settings import *  # noqa:F403
from ..utils.NVDAStrings import NVDAString
from ..utils import makeAddonWindowTitle, getHelpObj
from ..utils import contextHelpEx

addonHandler.initTranslation()


def askForNVDARestart():
	if gui.messageBox(
		# Translators: A message asking the user if they wish to restart NVDA as NVDAExtensionGlobalPlugin addon settings changes have been made.
		_("Some changes have been made. You must save the configuration and restart NVDA for these changes to take effect. Would you like to do it now?"),
		makeAddonWindowTitle(NVDAString("Restart NVDA")),
		wx.YES | wx.NO | wx.ICON_WARNING) == wx.YES:
		_addonConfigManager.saveSettings(True)
		queueHandler.queueFunction(queueHandler.eventQueue, core.restart)
		return
	gui.messageBox(
		# Translators: A message to user
		_("Don't forget to save the configuration for the changes to take effect !"),
		makeAddonWindowTitle(NVDAString("Warning")),
		wx.OK | wx.ICON_WARNING)


class FeaturesInstallationSettingsPanel(
	contextHelpEx.ContextHelpMixinEx,
	SettingsPanel):
	# Translators: This is the label for the Installed features dialog.
	title = _("Features's installation")

	def __init__(self, parent):
		self.title = makeAddonWindowTitle(self.title)
		super(FeaturesInstallationSettingsPanel, self).__init__(parent)

	def makeSettings(self, settingsSizer):
		installChoiceLabels = {
			C_DoNotInstall: _("Do not install"),
			C_Install: _("Install"),
			C_InstallWithoutGesture: _("Install without gesture"),
			}
		installChoice = [installChoiceLabels[x] for x in [C_DoNotInstall, C_Install, C_InstallWithoutGesture]]
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("Display &systray icons and running application windows list:")
		self.installSystrayIconsListFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice)
		self.installSystrayIconsListFeatureOptionBox .SetSelection(getInstallFeatureOption(ID_SystrayIconsAndActiveWindowsList))
		self.bindHelpEvent(getHelpObj("hdr1"), self.installSystrayIconsListFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("&Complex symbols edition help:")
		self.installComplexSymbolsFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice)
		self.installComplexSymbolsFeatureOptionBox .SetSelection(getInstallFeatureOption(ID_ComplexSymbols))
		self.bindHelpEvent(getHelpObj("hdr3"), self.installComplexSymbolsFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("&Focused application's informations:")
		self.installFocusedApplicationInformationsFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice)
		self.installFocusedApplicationInformationsFeatureOptionBox.SetSelection(getInstallFeatureOption(ID_FocusedApplicationInformations))
		self.bindHelpEvent(getHelpObj("hdr4"), self.installFocusedApplicationInformationsFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("&Extended Virtual Buffer:")
		self.installExtendedVirtualBufferFeaturesOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice[:-1])
		self.installExtendedVirtualBufferFeaturesOptionBox .SetSelection(getInstallFeatureOption(ID_ExtendedVirtualBuffer))
		self.bindHelpEvent(getHelpObj("hdr5"), self.installExtendedVirtualBufferFeaturesOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("C&lipboard command announcement:")
		self.installClipboardCommandAnnouncementFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice[:-1])
		self.installClipboardCommandAnnouncementFeatureOptionBox .SetSelection(getInstallFeatureOption(ID_ClipboardCommandAnnouncement))
		self.bindHelpEvent(getHelpObj("hdr7"), self.installClipboardCommandAnnouncementFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("""Anno&uncement of the preselected folder in "Open", "Save", "Save as" dialog boxes:""")
		self.installCurrentFolderReportFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice)
		self.bindHelpEvent(getHelpObj("hdr8"), self.installCurrentFolderReportFeatureOptionBox)
		self.installCurrentFolderReportFeatureOptionBox .SetSelection(getInstallFeatureOption(ID_CurrentFolderReport))
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("&NVDA's log Files:")
		self.installOpenCurrentOrOldNVDALogFileFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice)
		self.installOpenCurrentOrOldNVDALogFileFeatureOptionBox.SetSelection(getInstallFeatureOption(ID_OpenCurrentOrOldNVDALogFile))
		self.bindHelpEvent(getHelpObj("hdr9"), self.installOpenCurrentOrOldNVDALogFileFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("Speech &history:")
		self.installSpeechHistoryFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice)
		self.installSpeechHistoryFeatureOptionBox.SetSelection(getInstallFeatureOption(ID_SpeechHistory))
		self.bindHelpEvent(getHelpObj("hdr10"), self.installSpeechHistoryFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("&Keyboard keys renaming:")
		self.installKeyboardKeyRenamingFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice[:-1])
		self.installKeyboardKeyRenamingFeatureOptionBox.SetSelection(getInstallFeatureOption(ID_KeyboardKeyRenaming))
		self.bindHelpEvent(getHelpObj("hdr12"), self.installKeyboardKeyRenamingFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("C&ommand keys selective announcement:")
		self.installCommandKeysSelectiveAnnouncementFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice[:-1])
		self.installCommandKeysSelectiveAnnouncementFeatureOptionBox.SetSelection(getInstallFeatureOption(ID_CommandKeysSelectiveAnnouncement))
		self.bindHelpEvent(getHelpObj("hdr13"), self.installCommandKeysSelectiveAnnouncementFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("Minute &timer:")
		self.installMinuteTimerFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice)
		self.installMinuteTimerFeatureOptionBox.SetSelection(getInstallFeatureOption(ID_MinuteTimer))
		self.bindHelpEvent(getHelpObj("hdr14"), self.installMinuteTimerFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("NVDA's &restart:")
		self.installRestartInDebugModeFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice)
		self.installRestartInDebugModeFeatureOptionBox.SetSelection(getInstallFeatureOption(ID_RestartInDebugMode))
		self.bindHelpEvent(getHelpObj("hdr15"), self.installRestartInDebugModeFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("Display visible items making up the foreground &object:")
		self.installForegroundWindowObjectsListFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice)
		self.installForegroundWindowObjectsListFeatureOptionBox.SetSelection(getInstallFeatureOption(ID_ForegroundWindowObjectsList))
		self.bindHelpEvent(getHelpObj("hdr16"), self.installForegroundWindowObjectsListFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("&Voice profile switching:")
		self.installVoiceProfileSwitchingFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice)
		self.installVoiceProfileSwitchingFeatureOptionBox.SetSelection(getInstallFeatureOption(ID_VoiceProfileSwitching))
		self.bindHelpEvent(getHelpObj("hdr17"), self.installVoiceProfileSwitchingFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("Ke&ys's remanence:")
		self.installKeyRemanenceFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice[:-1])
		self.installKeyRemanenceFeatureOptionBox.SetSelection(getInstallFeatureOption(ID_KeyRemanence))
		self.bindHelpEvent(getHelpObj("hdr18"), self.installKeyRemanenceFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("Volu&me's control:")
		self.installVolumeControlFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice)
		self.installVolumeControlFeatureOptionBox.SetSelection(getInstallFeatureOption(ID_VolumeControl))
		self.bindHelpEvent(getHelpObj("hdr21"), self.installVolumeControlFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("&Development's tools:")
		self.installDevToolsFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice[:-1])
		self.installDevToolsFeatureOptionBox.SetSelection(getInstallFeatureOption(ID_Tools))
		self.bindHelpEvent(getHelpObj("hdr22"), self.installDevToolsFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("&Date and time - supplements:")
		self.installDateAndTimeFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice[:])
		self.installDateAndTimeFeatureOptionBox.SetSelection(getInstallFeatureOption(ID_DateAndTime))
		self.bindHelpEvent(getHelpObj("hdr24"), self.installDateAndTimeFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("Text anal&ysis:")
		self.installTextAnalysisFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice[:])
		self.installTextAnalysisFeatureOptionBox.SetSelection(getInstallFeatureOption(FCT_TextAnalysis))
		self.bindHelpEvent(getHelpObj("hdr31"), self.installTextAnalysisFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("Temporar&y audio device:")
		self.installTemporaryAudioDeviceFeatureOptionBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=installChoice[:-1])
		self.installTemporaryAudioDeviceFeatureOptionBox.SetSelection(getInstallFeatureOption(FCT_TemporaryAudioDevice))
		self.bindHelpEvent(getHelpObj("hdr33"), self.installTemporaryAudioDeviceFeatureOptionBox)

	def saveSettingChanges(self):
		self.restartNVDA = False
		if self.installExtendedVirtualBufferFeaturesOptionBox.GetSelection() != getInstallFeatureOption(ID_ExtendedVirtualBuffer):
			setInstallFeatureOption(ID_ExtendedVirtualBuffer, self.installExtendedVirtualBufferFeaturesOptionBox.GetSelection())
			self.restartNVDA = True
			if getInstallFeatureOption(ID_ExtendedVirtualBuffer) == C_Install:
				# set LoopInNavigationModeOption to default state (False)
				if toggleLoopInNavigationModeOption(False):
					toggleLoopInNavigationModeOption(True)
		if self.installSystrayIconsListFeatureOptionBox.GetSelection() != getInstallFeatureOption(ID_SystrayIconsAndActiveWindowsList):
			setInstallFeatureOption(ID_SystrayIconsAndActiveWindowsList, self.installSystrayIconsListFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		if self.installComplexSymbolsFeatureOptionBox.GetSelection() != getInstallFeatureOption(ID_ComplexSymbols):
			setInstallFeatureOption(ID_ComplexSymbols, self.installComplexSymbolsFeatureOptionBox.GetSelection())
			self.restartNVDA = True
			if getInstallFeatureOption(ID_ComplexSymbols) == C_DoNotInstall:
				# set parameters to default values
				_addonConfigManager.setMaximumOfLastUsedSymbols(C_MaximumOfLastUsedSymbols)
				_addonConfigManager.deleceAllUserComplexSymbols()
		if self.installClipboardCommandAnnouncementFeatureOptionBox.GetSelection() != getInstallFeatureOption(ID_ClipboardCommandAnnouncement):
			setInstallFeatureOption(ID_ClipboardCommandAnnouncement, self.installClipboardCommandAnnouncementFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		if self.installCurrentFolderReportFeatureOptionBox.GetSelection() != getInstallFeatureOption(ID_CurrentFolderReport):
			setInstallFeatureOption(ID_CurrentFolderReport, self.installCurrentFolderReportFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		if self.installFocusedApplicationInformationsFeatureOptionBox.GetSelection() != getInstallFeatureOption(ID_FocusedApplicationInformations):
			setInstallFeatureOption(ID_FocusedApplicationInformations, self.installFocusedApplicationInformationsFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		if self.installOpenCurrentOrOldNVDALogFileFeatureOptionBox.GetSelection() != getInstallFeatureOption(ID_OpenCurrentOrOldNVDALogFile):
			setInstallFeatureOption(ID_OpenCurrentOrOldNVDALogFile, self.installOpenCurrentOrOldNVDALogFileFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		if self.installSpeechHistoryFeatureOptionBox.GetSelection() != getInstallFeatureOption(ID_SpeechHistory):
			setInstallFeatureOption(ID_SpeechHistory, self.installSpeechHistoryFeatureOptionBox.GetSelection())
			self.restartNVDA = True
			if getInstallFeatureOption(ID_SpeechHistory) == C_DoNotInstall:
				# set parameters to Default values
				if not toggleSpeechRecordWithNumberOption(False):
					toggleSpeechRecordWithNumberOption(True)
				if toggleSpeechRecordInAscendingOrderOption(False):
					toggleSpeechRecordInAscendingOrderOption(True)
		if self.installKeyboardKeyRenamingFeatureOptionBox.GetSelection() != getInstallFeatureOption(ID_KeyboardKeyRenaming):
			setInstallFeatureOption(ID_KeyboardKeyRenaming, self.installKeyboardKeyRenamingFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		if self.installCommandKeysSelectiveAnnouncementFeatureOptionBox.GetSelection() != getInstallFeatureOption(ID_CommandKeysSelectiveAnnouncement):
			setInstallFeatureOption(ID_CommandKeysSelectiveAnnouncement, self.installCommandKeysSelectiveAnnouncementFeatureOptionBox.GetSelection())
			self.restartNVDA = True
			if getInstallFeatureOption(ID_CommandKeysSelectiveAnnouncement) == C_DoNotInstall:
				# delete all command selective announcement feature configuration
				from .nvdaConfig import _NVDAConfigManager
				_NVDAConfigManager.deleceCommandKeyAnnouncementConfiguration()
		if self.installMinuteTimerFeatureOptionBox.GetSelection() != getInstallFeatureOption(ID_MinuteTimer):
			setInstallFeatureOption(ID_MinuteTimer, self.installMinuteTimerFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		if self.installForegroundWindowObjectsListFeatureOptionBox.GetSelection() != getInstallFeatureOption(ID_ForegroundWindowObjectsList):
			setInstallFeatureOption(ID_ForegroundWindowObjectsList, self.installForegroundWindowObjectsListFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		if self.installVoiceProfileSwitchingFeatureOptionBox.GetSelection() != getInstallFeatureOption(ID_VoiceProfileSwitching):
			setInstallFeatureOption(ID_VoiceProfileSwitching, self.installVoiceProfileSwitchingFeatureOptionBox.GetSelection())
			self.restartNVDA = True
			if getInstallFeatureOption(ID_VoiceProfileSwitching) == C_DoNotInstall:
				from ..switchVoiceProfile import SwitchVoiceProfilesManager
				SwitchVoiceProfilesManager().deleteAllProfiles()

		if self.installKeyRemanenceFeatureOptionBox.GetSelection() != getInstallFeatureOption(ID_KeyRemanence):
			setInstallFeatureOption(ID_KeyRemanence, self.installKeyRemanenceFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		if self.installRestartInDebugModeFeatureOptionBox.GetSelection() != getInstallFeatureOption(ID_RestartInDebugMode):
			setInstallFeatureOption(ID_RestartInDebugMode, self.installRestartInDebugModeFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		if self.installVolumeControlFeatureOptionBox.GetSelection() != getInstallFeatureOption(ID_VolumeControl):
			setInstallFeatureOption(ID_VolumeControl, self.installVolumeControlFeatureOptionBox.GetSelection())
			self.restartNVDA = True
			if getInstallFeatureOption(ID_VolumeControl) != C_DoNotInstall:
				# set parameters to default values
				if not toggleSetOnMainAndNVDAVolumeAdvancedOption(False):
					toggleSetOnMainAndNVDAVolumeAdvancedOption(True)
				_addonConfigManager.setMinMasterVolumeLevel(int(C_MinMasterVolumeLevel))
				_addonConfigManager.setMasterVolumeLevel(C_MasterVolumeLevel)
				_addonConfigManager.setMinNVDAVolumeLevel(int(C_MinNVDAVolumeLevel))
				_addonConfigManager.setNVDAVolumeLevel(int(C_NVDAVolumeLevel))
		if self.installDevToolsFeatureOptionBox.GetSelection() != getInstallFeatureOption(ID_Tools):
			setInstallFeatureOption(ID_Tools, self.installDevToolsFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		if self.installDateAndTimeFeatureOptionBox.GetSelection() != getInstallFeatureOption(ID_DateAndTime):
			setInstallFeatureOption(ID_DateAndTime, self.installDateAndTimeFeatureOptionBox.GetSelection())
			if not getInstallFeatureOption(ID_DateAndTime) == C_Install:
				# set report time with second to default value
				if toggleReportTimeWithSecondsOption(False):
					toggleReportTimeWithSecondsOption(True)
			self.restartNVDA = True
		if self.installTextAnalysisFeatureOptionBox.GetSelection() != getInstallFeatureOption(FCT_TextAnalysis):
			setInstallFeatureOption(FCT_TextAnalysis, self.installTextAnalysisFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		if self.installTemporaryAudioDeviceFeatureOptionBox.GetSelection() != getInstallFeatureOption(FCT_TemporaryAudioDevice):
			setInstallFeatureOption(FCT_TemporaryAudioDevice, self.installTemporaryAudioDeviceFeatureOptionBox.GetSelection())
			self.restartNVDA = True

	def onSave(self):
		self.saveSettingChanges()


class NVDAEnhancementSettingsPanel(
	contextHelpEx.ContextHelpMixinEx,
	SettingsPanel):
	# Translators: This is the label for the settings dialog.
	title = _("NVDA enhancements")

	def __init__(self, parent):
		self.title = makeAddonWindowTitle(self.title)
		super(NVDAEnhancementSettingsPanel, self).__init__(parent)

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a group of editing options in the
		# NVDAEnhancement settings panel
		groupText = _("Editing")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = gui.guiHelper.BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# bug fix in nvda 2020.3
		# so hide it for nvda version higher or equal to this version
		# Translators: This is the label for a checkbox in the NVDAEnhancement settings panel.
		labelText = _("&Report next word on deletion")
		self.ReportNextWordOnDeletionOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.ReportNextWordOnDeletionOptionBox.SetValue(toggleReportNextWordOnDeletionOption(False))
		self.bindHelpEvent(getHelpObj("hdr101"), self.ReportNextWordOnDeletionOptionBox)
		import versionInfo
		NVDAVersion = [versionInfo.version_year, versionInfo.version_major]
		if globalVars.appArgs.secure\
			or NVDAVersion >= [2020, 3]:
			self.ReportNextWordOnDeletionOptionBox .Hide()
		# Translators: This is the label for a comboBox in the NVDAEnhancement settings panel.
		labelText = _("maximum number of last &used symbols recorded:")
		choice = [x*10 for x in range(1, 11)]
		choice = list(reversed(choice))
		self.maximumOfLastUsedSymbolsBox = group.addLabeledControl(labelText, wx.Choice, choices=[str(x) for x in choice])
		self.maximumOfLastUsedSymbolsBox.SetSelection(choice.index(_addonConfigManager.getMaximumOfLastUsedSymbols()))
		self.bindHelpEvent(getHelpObj("hdr3-1"), self.maximumOfLastUsedSymbolsBox)
		if getInstallFeatureOption(ID_ComplexSymbols) == C_DoNotInstall:
			self.maximumOfLastUsedSymbolsBox.Disable()
		# Translators: This is the label for a group in NVDAEnhancement settings panel
		groupText = _("Speech history")
		groupSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = gui.guiHelper.BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the NVDAEnhancement settings panel.
		labelText = _("&Number the records ")
		self.speechRecordWithNumberOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.speechRecordWithNumberOptionBox.SetValue(toggleSpeechRecordWithNumberOption(False))
		self.bindHelpEvent(getHelpObj("hdr10-1"), self.speechRecordWithNumberOptionBox)
		# Translators: This is the label for a checkbox in the NVDAEnhancement settings panel.
		labelText = _("&Display records in ascending order")
		self.speechRecordInAscendingOrderOptionBox = group.addItem(wx.CheckBox(groupBox, wx.ID_ANY, label=labelText))
		self.speechRecordInAscendingOrderOptionBox.SetValue(toggleSpeechRecordInAscendingOrderOption(False))
		self.bindHelpEvent(getHelpObj("hdr10-1"), self.speechRecordInAscendingOrderOptionBox)
		if getInstallFeatureOption(ID_SpeechHistory) == C_DoNotInstall:
			for item in range(0, group.sizer.GetItemCount()):
				group.sizer.Hide(item)
		# Translators: This is the label for a group NVDAEnhancement settings panel
		groupText = _("Browser")
		groupSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = gui.guiHelper.BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the NVDAEnhancement settings panel.
		labelText = _("&Browse in loop")
		self.loopInNavigationModeOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.loopInNavigationModeOptionBox.SetValue(toggleLoopInNavigationModeOption(False))
		self.bindHelpEvent(getHelpObj("hdr5-5"), self.loopInNavigationModeOptionBox)
		if getInstallFeatureOption(ID_ExtendedVirtualBuffer) == C_DoNotInstall:
			group.sizer.Hide(0)

	def saveSettingChanges(self):
		from . import _addonConfigManager
		self.restartNVDA = False
		if self.ReportNextWordOnDeletionOptionBox.IsChecked() != toggleReportNextWordOnDeletionOption(False):
			toggleReportNextWordOnDeletionOption()
			self.restartNVDA = True
		if self.speechRecordWithNumberOptionBox.IsChecked() != toggleSpeechRecordWithNumberOption(False):
			toggleSpeechRecordWithNumberOption()
		if self.speechRecordInAscendingOrderOptionBox.IsChecked() != toggleSpeechRecordInAscendingOrderOption(False):
			toggleSpeechRecordInAscendingOrderOption()
		if self.loopInNavigationModeOptionBox.IsChecked() != toggleLoopInNavigationModeOption(False):
			toggleLoopInNavigationModeOption()
		maximumOfLastUsedSymbols = int(self.maximumOfLastUsedSymbolsBox.GetString(self.maximumOfLastUsedSymbolsBox.GetSelection()))
		_addonConfigManager.setMaximumOfLastUsedSymbols(maximumOfLastUsedSymbols)

	def onSave(self):
		self.saveSettingChanges()


class ComputerSettingsPanel(
	contextHelpEx.ContextHelpMixinEx,
	SettingsPanel):
	# Translators: This is the label for the options settings dialog.
	title = _("Computer")

	def __init__(self, parent):
		self.title = makeAddonWindowTitle(self.title)
		super(ComputerSettingsPanel, self).__init__(parent)

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a group of editing options in the computer settings panel.
		groupText = _("Windows")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = gui.guiHelper.BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the Computer settings panel.
		labelText = _("&No object description in Windows ribbons")
		self.noDescriptionReportInRibbonOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.noDescriptionReportInRibbonOptionBox.SetValue(toggleNoDescriptionReportInRibbonOption(False))
		self.bindHelpEvent(getHelpObj("hdr100"), self.noDescriptionReportInRibbonOptionBox)
		if globalVars.appArgs.secure:
			self.noDescriptionReportInRibbonOptionBox .Hide()
		# Translators: This is the label for a checkbox in the Computer settings panel.
		labelText = _("Automatically &maximize windows")
		self.AutomaticWindowMaximizationOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.AutomaticWindowMaximizationOptionBox.SetValue(toggleAutomaticWindowMaximizationOption(False))
		self.bindHelpEvent(getHelpObj("hdr102"), self.AutomaticWindowMaximizationOptionBox)

		# Translators: This is the label for a checkbox in the Computer settings panel.
		labelText = _("Report &windows clock's time with seconds")
		self.reportTimeWithSecondsOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.reportTimeWithSecondsOptionBox.SetValue(toggleReportTimeWithSecondsOption(False))
		self.bindHelpEvent(getHelpObj("hdr24-2"), self.reportTimeWithSecondsOptionBox)
		if getInstallFeatureOption(ID_DateAndTime) == C_DoNotInstall:
			self.reportTimeWithSecondsOptionBox.Disable()

		# Translators: This is the label for a group in computer settings panel.
		groupText = _("Volume control")
		volumeGroup = gui.guiHelper.BoxSizerHelper(self, sizer=wx.StaticBoxSizer(wx.StaticBox(self, label=groupText), wx.VERTICAL))
		sHelper.addItem(volumeGroup)
		# Translators: This is the label for a group in computer settings panel.
		groupText = _("Main and NVDA volume")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = gui.guiHelper.BoxSizerHelper(self, sizer=groupSizer)
		volumeGroup.addItem(group)
		# Translators: This is the label for a checkbox in the computer settings panel.
		labelText = _("Set on &volume at the loading of the add-on")
		self.setOnMainAndNVDAVolumeOptionCheckBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.setOnMainAndNVDAVolumeOptionCheckBox.SetValue(toggleSetOnMainAndNVDAVolumeAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr21-7"), self.setOnMainAndNVDAVolumeOptionCheckBox)
		# Translators: This is the label for a group of main volume options in the computer settings panel.
		groupText = _("Main volume")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = gui.guiHelper.BoxSizerHelper(self, sizer=groupSizer)
		volumeGroup.addItem(group)
		# Translators: This is a label for a choice box in computer settings panel.
		labelText = _("&Threshold of recovery of the volume:")
		choice = [10 * x for x in reversed(list(range(0, 11)))]
		self.minMasterVolumeLevelBox = group.addLabeledControl(labelText, wx.Choice, choices=[str(x) for x in choice[5:]])
		self.minMasterVolumeLevelBox.SetSelection(choice[5:].index(_addonConfigManager.getMinMasterVolumeLevel()))
		self.bindHelpEvent(getHelpObj("hdr21-7"), self.minMasterVolumeLevelBox)
		# Translators: This is a label for a choice box in computer settings panel.
		labelText = _("Recovery &level:")
		self.masterVolumeLevelBox = group.addLabeledControl(labelText, wx.Choice, choices=[str(x) for x in choice])
		self.masterVolumeLevelBox.SetSelection(choice.index(_addonConfigManager.getMasterVolumeLevel()))
		self.bindHelpEvent(getHelpObj("hdr21-7"), self.masterVolumeLevelBox)
		# Translators: This is the label for a group of NVDA volume options in the computer settings panel.
		groupText = _("NVDA volume")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = gui.guiHelper.BoxSizerHelper(self, sizer=groupSizer)
		volumeGroup.addItem(group)
		# Translators: This is a label for a choice box in computer settings panel.
		labelText = _("T&hreshold of recovery of the volume:")
		self.minNVDAVolumeLevelBox = group.addLabeledControl(labelText, wx.Choice, choices=[str(x) for x in choice[5:]])
		self.minNVDAVolumeLevelBox.SetSelection(choice[5:].index(_addonConfigManager.getMinNVDAVolumeLevel()))
		self.bindHelpEvent(getHelpObj("hdr21-7"), self.minNVDAVolumeLevelBox)
		# Translators: This is a label for a choice box in computer settings panel.
		labelText = _("&Recovery level:")
		self.NVDAVolumeLevelBox = group.addLabeledControl(labelText, wx.Choice, choices=[str(x) for x in choice[5:]])
		self.NVDAVolumeLevelBox.SetSelection(choice[5:].index(_addonConfigManager.getNVDAVolumeLevel()))
		self.bindHelpEvent(getHelpObj("hdr21-7"), self.NVDAVolumeLevelBox)
		# Translators: This is the label for a group in computer settings panel.
		groupText = _("Volume change")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = gui.guiHelper.BoxSizerHelper(self, sizer=groupSizer)
		volumeGroup.addItem(group)
		# Translators: This is a label for a choice box in computer settings panel.
		labelText = _("Ste&ps's size:")
		choice = [str(x) for x in range(1, 21)]
		self.volumeChangeStepLevelBox = group.addLabeledControl(labelText, wx.Choice, choices=list(reversed(choice)))
		self.volumeChangeStepLevelBox.SetStringSelection(str(_addonConfigManager.getVolumeChangeStepLevel())	)
		self.bindHelpEvent(getHelpObj("hdr21-3"), self.volumeChangeStepLevelBox)
		# Translators: This is the label for a checkbox in the computer settings panel.
		labelText = _("R&eport volume changes")
		self.reportVolumeChangeOptionCheckBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.reportVolumeChangeOptionCheckBox.SetValue(toggleReportVolumeChangeAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr21-6"), self.reportVolumeChangeOptionCheckBox)
		# Translators: This is the label for a checkbox in the computer settings panel.
		labelText = _("&Announce application volume level in percent")
		self.appVolumeLevelAnnouncementInPercentOptionCheckBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.appVolumeLevelAnnouncementInPercentOptionCheckBox .SetValue(toggleAppVolumeLevelAnnouncementInPercentAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr21-6"), self.appVolumeLevelAnnouncementInPercentOptionCheckBox)
		if not getInstallFeatureOption(ID_VolumeControl):
			for item in range(0, volumeGroup.sizer.GetItemCount()):
				volumeGroup.sizer.Hide(item)
		groupText = _("Temporary audio device")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = gui.guiHelper.BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the Computer settings panel.
		labelText = _("Ask for confirmation")
		self.confirmAudioDeviceChangeCheckBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.confirmAudioDeviceChangeCheckBox.SetValue(toggleConfirmAudioDeviceChangeAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr33"), self.confirmAudioDeviceChangeCheckBox)
		# Translators: This is a label for a choice box in computer settings panel.
		labelText = _("ma&ximum waiting time for confirmation (in seconds):")
		choice = [str(x) for x in range(1, 31)]
		self.confirmAudioDeviceChangeTimeOutChoiceBox = group.addLabeledControl(labelText, wx.Choice, choices=list(reversed(choice)))
		self.confirmAudioDeviceChangeTimeOutChoiceBox.SetStringSelection(str(_addonConfigManager.getConfirmAudioDeviceChangeTimeOut())	)
		self.bindHelpEvent(getHelpObj("?dr33"), self.confirmAudioDeviceChangeTimeOutChoiceBox)

	def saveSettingChanges(self):
		self.restartNVDA = False
		if self.noDescriptionReportInRibbonOptionBox.IsChecked() != toggleNoDescriptionReportInRibbonOption(False):
			toggleNoDescriptionReportInRibbonOption()
			self.restartNVDA = True
		if self.AutomaticWindowMaximizationOptionBox.IsChecked() != toggleAutomaticWindowMaximizationOption(False):
			toggleAutomaticWindowMaximizationOption()
		if getInstallFeatureOption(ID_DateAndTime) != C_DoNotInstall:
			if self.reportTimeWithSecondsOptionBox.IsChecked() != toggleReportTimeWithSecondsOption(False):
				toggleReportTimeWithSecondsOption()
		if self.setOnMainAndNVDAVolumeOptionCheckBox.IsChecked() != toggleSetOnMainAndNVDAVolumeAdvancedOption(False):
			toggleSetOnMainAndNVDAVolumeAdvancedOption()
		levelString = self.minMasterVolumeLevelBox.GetStringSelection()
		_addonConfigManager.setMinMasterVolumeLevel(int(levelString))
		levelString = self.masterVolumeLevelBox.GetStringSelection()
		_addonConfigManager.setMasterVolumeLevel(int(levelString))
		levelString = self.minNVDAVolumeLevelBox.GetStringSelection()
		_addonConfigManager.setMinNVDAVolumeLevel(int(levelString))
		levelString = self.NVDAVolumeLevelBox.GetStringSelection()
		_addonConfigManager.setNVDAVolumeLevel(int(levelString))
		levelString = self.volumeChangeStepLevelBox.GetStringSelection()
		_addonConfigManager.setVolumeChangeStepLevel(int(levelString))
		if self.reportVolumeChangeOptionCheckBox.IsChecked() != toggleReportVolumeChangeAdvancedOption(False):
			toggleReportVolumeChangeAdvancedOption()
		if self.appVolumeLevelAnnouncementInPercentOptionCheckBox.IsChecked() != toggleAppVolumeLevelAnnouncementInPercentAdvancedOption(False):
			toggleAppVolumeLevelAnnouncementInPercentAdvancedOption(True)
		if self.confirmAudioDeviceChangeCheckBox.IsChecked() != toggleConfirmAudioDeviceChangeAdvancedOption(False):
			toggleConfirmAudioDeviceChangeAdvancedOption(True)
		timeOut = self.confirmAudioDeviceChangeTimeOutChoiceBox.GetStringSelection()
		_addonConfigManager.setConfirmAudioDeviceChangeTimeOut(timeOut)

	def onSave(self):
		self.saveSettingChanges()


class AdvancedSettingsPanel(
	contextHelpEx.ContextHelpMixinEx,
	SettingsPanel):
	# Translators: This is the label for the Advanced settings panel.
	title = _("advanced")
	_playSoundOnErrorsOptionLabels = [  # becarefull: order is important
		# Translators: This is a label for a choice item in Advanced options settings dialog.
		_("For No NVDA's version"),  # PSOE_NoVersion
		# Translators: This is a label for a choice item in Advanced options settings dialog.
		_("For Only the NVDA's snapshot versions"),  # PSOE_SnapshotVersions
		# Translators: This is a label for a choice item in Advanced options settings dialog.
		_("Only until the next NVDA restart"),  # PSOE_UntilNVDARestart
		# Translators: This is a label for a choice item in Advanced options settings dialog.
		_("For all NVDA's versions"),  # PSOE_AllVersions
		]

	def __init__(self, parent):
		self.title = makeAddonWindowTitle(self.title)
		super(AdvancedSettingsPanel, self).__init__(parent)

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a choice box in the advanced settings panel.
		labelText = _("&Play sound on logged errors:")
		self.playSoundOnErrorsOptionChoiceBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=self._playSoundOnErrorsOptionLabels)
		self.playSoundOnErrorsOptionChoiceBox.SetSelection(_addonConfigManager.getPlaySoundOnErrorsOption())
		self.bindHelpEvent(getHelpObj("hdr300"), self.playSoundOnErrorsOptionChoiceBox)
		# Translators: This is the label for a checkbox in the Advanced settings panel.
		labelText = _("&Title dialog with add-on name")
		self.dialogTitleWithAddonSummaryOptionBox = sHelper.addItem(wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.dialogTitleWithAddonSummaryOptionBox.SetValue(toggleDialogTitleWithAddonSummaryAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr302"), self.dialogTitleWithAddonSummaryOptionBox)
		# Translators: This is the label for a comboBox in the advanced settings panel.
		labelText = _("&Delay between repeat of same gesture:")
		choice = [x for x in range(100, 3050, 50)]
		choice = list(reversed(choice))
		self.MaximumDelayBetweenSameScriptBox = sHelper.addLabeledControl(labelText, wx.Choice, choices=[str(x) for x in choice])
		self.MaximumDelayBetweenSameScriptBox.SetSelection(choice.index(_addonConfigManager.getMaximumDelayBetweenSameScript()))
		self.bindHelpEvent(getHelpObj("hdr303"), self.MaximumDelayBetweenSameScriptBox)
		# Translators: This is the label for a checkbox in the Advanced settings panel.
		labelText = _("""&Do not take account of the option called "Report object descriptions" during the display of the dialog box same as confirmation""")
		self.byPassNoDescriptionOptionBox = sHelper.addItem(wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.byPassNoDescriptionOptionBox.SetValue(toggleByPassNoDescriptionAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr204"), self.byPassNoDescriptionOptionBox)
		if globalVars.appArgs.secure:
			self.MaximumDelayBetweenSameScriptBox .Hide()
			self.byPassNoDescriptionOptionBox.Hide()

	def saveSettingChanges(self):
		self.restartNVDA = False
		playSoundOnErrorsOption = self.playSoundOnErrorsOptionChoiceBox.GetSelection()
		_addonConfigManager.setPlaySoundOnErrorsOption(playSoundOnErrorsOption)
		if self.dialogTitleWithAddonSummaryOptionBox.IsChecked() != toggleDialogTitleWithAddonSummaryAdvancedOption(False):
			toggleDialogTitleWithAddonSummaryAdvancedOption()
		maximumDelayBetweenSameScript = int(self.MaximumDelayBetweenSameScriptBox.GetString(self.MaximumDelayBetweenSameScriptBox.GetSelection()))
		if maximumDelayBetweenSameScript != _addonConfigManager.getMaximumDelayBetweenSameScript():
			_addonConfigManager.setMaximumDelayBetweenSameScript(maximumDelayBetweenSameScript)
			self.restartNVDA = True
		if self.byPassNoDescriptionOptionBox.IsChecked() != toggleByPassNoDescriptionAdvancedOption(False):
			toggleByPassNoDescriptionAdvancedOption()
			self.restartNVDA = True

	def onSave(self):
		self.saveSettingChanges()


class KeyboardSettingsPanel(
	contextHelpEx.ContextHelpMixinEx,
	SettingsPanel):
	# Translators: This is the label for the Keyboard settings panel.
	title = _("Keyboard")

	def __init__(self, parent):
		self.title = makeAddonWindowTitle(self.title)
		super(KeyboardSettingsPanel, self).__init__(parent)

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a group of editing options in the Keyboard settings panel.
		groupText = _("Keys's remanence")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = gui.guiHelper.BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the Keyboard settings panel.
		labelText = _("&Only NVDA key in remanence")
		self.onlyNVDAKeyInRemanenceAdvancedOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.onlyNVDAKeyInRemanenceAdvancedOptionBox.SetValue(toggleOnlyNVDAKeyInRemanenceAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr18"), self.onlyNVDAKeyInRemanenceAdvancedOptionBox)
		# Translators: This is the label for a checkbox in the Keyboard settings panel.
		labelText = _("Activate &remanence at NVDA's start")
		self.remanenceAtNVDAStartAdvancedOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.remanenceAtNVDAStartAdvancedOptionBox.SetValue(toggleRemanenceAtNVDAStartAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr18"), self.remanenceAtNVDAStartAdvancedOptionBox)
		# Translators: This is the label for a combobox in the Keyboard settings panel.
		labelText = _("&Remanence's delay (in milliseconds):")
		remanenceDelayChoice = [x for x in range(1000, 10500, 500)]
		self.remanenceDelayChoice = list(reversed(remanenceDelayChoice))
		self.remanenceDelayBox = group.addLabeledControl(labelText, wx.Choice, choices=[str(x) for x in self.remanenceDelayChoice])
		self.remanenceDelayBox.SetSelection(self.remanenceDelayChoice.index(_addonConfigManager.getRemanenceDelay()))
		self.bindHelpEvent(getHelpObj("hdr18"), self.remanenceDelayBox)
		# Translators: This is the label for a check box in the Keyboard settings panel.
		labelText = _("Play &sound at the start of remanence")
		self.beepAtRemanenceStartOptionCheckBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.beepAtRemanenceStartOptionCheckBox .SetValue(toggleBeepAtRemanenceStartAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr18"), self.beepAtRemanenceStartOptionCheckBox)
		# Translators: This is the label for a check box in the Keyboard settings panel.
		labelText = _("Play sound at the &end of remanence")
		self.beepAtRemanenceEndOptionCheckBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.beepAtRemanenceEndOptionCheckBox .SetValue(toggleBeepAtRemanenceEndAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr18"), self.beepAtRemanenceEndOptionCheckBox)
		# Translators: This is the label for a check box in the Keyboard settings panel.
		labelText = _("Special remanence for &Gmail.com")
		self.remanenceForGmailOptionCheckBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.remanenceForGmailOptionCheckBox .SetValue(toggleRemanenceForGmailAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr18-1"), self.remanenceForGmailOptionCheckBox)
		if not getInstallFeatureOption(ID_KeyRemanence):
			for item in range(0, group.sizer.GetItemCount()):
				group.sizer.Hide(item)
		# Translators: This is the label for a group of editing options in the Keyboard settings panel.
		groupText = _("Numeric keypad")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = gui.guiHelper.BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the keyboard settings panel.
		labelText = _("&Allow the standard use of the numeric keypad")
		self.enableNumpadNavigationModeToggleOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.enableNumpadNavigationModeToggleOptionBox.SetValue(toggleEnableNumpadNavigationModeToggleAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr304"), self.enableNumpadNavigationModeToggleOptionBox)
		# Translators: This is the label for a checkbox in the keyboard settings panel.
		labelText = _("&Enable the standard use of the numeric keypad at NVDA's start")
		self.activateNumpadNavigationModeAtStartOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.activateNumpadNavigationModeAtStartOptionBox.SetValue(toggleActivateNumpadNavigationModeAtStartAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr304"), self.activateNumpadNavigationModeAtStartOptionBox)
		# Translators: This is the label for a checkbox in the keyboard settings panel.
		labelText = _("&Enable / disable numeric keypad's standard use with num lock key")
		self.activateNumpadStandardUseWithNumLockOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.activateNumpadStandardUseWithNumLockOptionBox.SetValue(toggleActivateNumpadStandardUseWithNumLockAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr304"), self.activateNumpadStandardUseWithNumLockOptionBox)

	def saveSettingChanges(self):
		self.restartNVDA = False
		if getInstallFeatureOption(ID_KeyRemanence):
			if self.onlyNVDAKeyInRemanenceAdvancedOptionBox.IsChecked() != toggleOnlyNVDAKeyInRemanenceAdvancedOption(False):
				toggleOnlyNVDAKeyInRemanenceAdvancedOption()
			if self.remanenceAtNVDAStartAdvancedOptionBox.IsChecked() != toggleRemanenceAtNVDAStartAdvancedOption(False):
				toggleRemanenceAtNVDAStartAdvancedOption()
			remanenceDelay = self.remanenceDelayBox.GetSelection()
			_addonConfigManager.setRemanenceDelay(self.remanenceDelayChoice[remanenceDelay])
			if self.beepAtRemanenceStartOptionCheckBox.IsChecked() != toggleBeepAtRemanenceStartAdvancedOption(False):
				toggleBeepAtRemanenceStartAdvancedOption()
			if self.beepAtRemanenceEndOptionCheckBox.IsChecked() != toggleBeepAtRemanenceEndAdvancedOption(False):
				toggleBeepAtRemanenceEndAdvancedOption()
			if self.remanenceForGmailOptionCheckBox.IsChecked() != toggleRemanenceForGmailAdvancedOption(False):
				toggleRemanenceForGmailAdvancedOption()
		if self.enableNumpadNavigationModeToggleOptionBox.IsChecked() != toggleEnableNumpadNavigationModeToggleAdvancedOption(False):
			toggleEnableNumpadNavigationModeToggleAdvancedOption()
			# in all cases, disable numpad navigation mode
			from ..commandKeysSelectiveAnnouncementAndRemanence import _myInputManager
			if _myInputManager is not None:
				_myInputManager .setNumpadNavigationMode(False)
		if self.activateNumpadNavigationModeAtStartOptionBox.IsChecked() != toggleActivateNumpadNavigationModeAtStartAdvancedOption(False):
			toggleActivateNumpadNavigationModeAtStartAdvancedOption()
		if self.activateNumpadStandardUseWithNumLockOptionBox.IsChecked() != toggleActivateNumpadStandardUseWithNumLockAdvancedOption(False):
			toggleActivateNumpadStandardUseWithNumLockAdvancedOption()

	def onSave(self):
		self.saveSettingChanges()


class UpdateSettingsPanel(
	contextHelpEx.ContextHelpMixinEx,
	SettingsPanel):
	# Translators: This is the label for the Advanced settings panel.
	title = _("Update")

	def __init__(self, parent):
		self.title = makeAddonWindowTitle(self.title)
		super(UpdateSettingsPanel, self).__init__(parent)

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a checkbox in the Update settings panel.
		labelText = _("Automatically check for &updates")
		self.autoCheckForUpdatesCheckBox = sHelper.addItem(wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.autoCheckForUpdatesCheckBox.SetValue(toggleAutoUpdateGeneralOptions(False))
		self.bindHelpEvent(getHelpObj("hdr-update"), self.autoCheckForUpdatesCheckBox)
		# Translators: This is the label for a checkbox in the Update settings panel.
		labelText = _("Update also release versions to &development versions")
		self.updateReleaseVersionsToDevVersionsCheckBox = sHelper.addItem(wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.updateReleaseVersionsToDevVersionsCheckBox.SetValue(toggleUpdateReleaseVersionsToDevVersionsGeneralOptions(False))
		self.bindHelpEvent(getHelpObj("hdr-update"), self.updateReleaseVersionsToDevVersionsCheckBox)
		# translators: this is a label for a button in update settings panel.
		labelText = _("&Check for update")
		checkForUpdateButton = wx.Button(self, label=labelText)
		sHelper.addItem(checkForUpdateButton)
		self.bindHelpEvent(getHelpObj("hdr-update"), checkForUpdateButton)
		checkForUpdateButton.Bind(wx.EVT_BUTTON, self.onCheckForUpdate)
		# translators: this is a label for a button in update settings panel.
		labelText = _("View &history")
		seeHistoryButton = wx.Button(self, label=labelText)
		sHelper.addItem(seeHistoryButton)
		self.bindHelpEvent(getHelpObj("hdr-update"), seeHistoryButton)
		seeHistoryButton.Bind(wx.EVT_BUTTON, self.onSeeHistory)

	def onCheckForUpdate(self, evt):
		from ..updateHandler import addonUpdateCheck
		releaseToDevVersion = self.updateReleaseVersionsToDevVersionsCheckBox.IsChecked()
		wx.CallAfter(addonUpdateCheck, auto=False, releaseToDev=releaseToDevVersion)

		self.Close()

	def onSeeHistory(self, evt):
		addon = addonHandler.getCodeAddon()

		theFile = os.path.join(addon.path, "doc", getLanguage(), "changes.html")
		if not os.path.exists(theFile):
			lang = getLanguage()
			theFile = os.path.join(addon.path, "doc", lang, "changes.html")
			if not os.path.exists(theFile):
				lang = "en"
				theFile = os.path.join(addon.path, "doc", lang, "changes.html")
		os.startfile(theFile)

	def saveSettingChanges(self):
		self.restartNVDA = False
		if self.autoCheckForUpdatesCheckBox.IsChecked() != toggleAutoUpdateGeneralOptions(False):
			toggleAutoUpdateGeneralOptions()
		if self.updateReleaseVersionsToDevVersionsCheckBox.IsChecked() != toggleUpdateReleaseVersionsToDevVersionsGeneralOptions(False):
			toggleUpdateReleaseVersionsToDevVersionsGeneralOptions()

	def onSave(self):
		self.saveSettingChanges()


class MultiCategorySettingsDialogEx(
	contextHelpEx.ContextHelpMixinEx,
	MultiCategorySettingsDialog):
	helpObj = getHelpObj("hdr-configurationMenu")

	def _doSave(self):
		askForRestart = False
		super(MultiCategorySettingsDialogEx, self)._doSave()
		for panel in self.catIdToInstanceMap.values():
			askForRestart = askForRestart or panel.restartNVDA
		if askForRestart:
			askForNVDARestart()


class GlobalSettingsDialog(MultiCategorySettingsDialogEx):
	INITIAL_SIZE = (1000, 480)
	# Min height required to show the OK, Cancel, Apply buttons
	MIN_SIZE = (470, 240)
	baseCategoryClasses = [
		FeaturesInstallationSettingsPanel,
		NVDAEnhancementSettingsPanel,
		ComputerSettingsPanel,
		KeyboardSettingsPanel,
		AdvancedSettingsPanel,
		UpdateSettingsPanel,
		]

	def __init__(self, parent, initialCategory=None):
		curAddon = addonHandler.getCodeAddon()
		# Translators: title of add-on settings dialog.
		dialogTitle = _("Settings")
		self.title = "%s - %s" % (curAddon.manifest["summary"], dialogTitle)
		self.categoryClasses = self.baseCategoryClasses[:]
		# if in secur mode, some panels must be disabled
		if globalVars.appArgs.secure:
			self.categoryClasses.remove(FeaturesInstallationSettingsPanel)
			self.categoryClasses .remove(UpdateSettingsPanel)
		super(GlobalSettingsDialog, self).__init__(parent, initialCategory)


class NVDAEnhancementProfileSettingsPanel(SettingsPanel):
	# Translators: This is the label for the settings dialog.
	title = _("NVDA enhancements")

	def __init__(self, parent):
		self.title = makeAddonWindowTitle(self.title)
		super(NVDAEnhancementProfileSettingsPanel, self).__init__(parent)

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a group of cursor's movement options in the
		# NVDAEnhancement profile settings panel
		groupText = _("Cursor's moving")
		groupSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=groupText)
		group = gui.guiHelper.BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a combobox in the NVDAEnhancement settings panel.
		labelText = _("&Punctuation/symbol level on word movement:")
		symbolLevelLabels = characterProcessing.SPEECH_SYMBOL_LEVEL_LABELS
		symbolLevelChoices = [symbolLevelLabels[level] for level in characterProcessing.CONFIGURABLE_SPEECH_SYMBOL_LEVELS]
		# Translators: This is the label for an item in combobox in the
		# NVDAEnhancement settings panel.
		symbolLevelChoices = [_("Current configuration profile's level"), ] + symbolLevelChoices[:]
		self.symbolLevelList = group.addLabeledControl(labelText, wx.Choice, choices=symbolLevelChoices)
		from .nvdaConfig import _NVDAConfigManager
		symbolLevelOnWordCaretMovement = _NVDAConfigManager .getSymbolLevelOnWordCaretMovement()
		if symbolLevelOnWordCaretMovement is None:
			self.symbolLevelList.SetSelection(0)
		else:
			self.symbolLevelList.SetSelection(1+characterProcessing.CONFIGURABLE_SPEECH_SYMBOL_LEVELS.index((symbolLevelOnWordCaretMovement)))

	def saveSettingChanges(self):
		from .nvdaConfig import _NVDAConfigManager
		self.restartNVDA = False
		if self.symbolLevelList.GetSelection() == 0:
			_NVDAConfigManager .saveSymbolLevelOnWordCaretMovement(None)
		else:
			index = self.symbolLevelList.GetSelection()
			level = characterProcessing.CONFIGURABLE_SPEECH_SYMBOL_LEVELS[index-1]
			print ("level: %s"%level)
			from versionInfo import version_year, version_major
			if version_year >= 2022  or (version_year == 2021 and version_major >= 2):
				level = level.value
			_NVDAConfigManager .saveSymbolLevelOnWordCaretMovement(level)

	def onSave(self):
		self.saveSettingChanges()


class KeyboardProfileSettingsPanel(
	contextHelpEx.ContextHelpMixinEx,
	SettingsPanel):
	# Translators: This is the label for the Keyboard settings panel.
	title = _("Keyboard")

	def __init__(self, parent):
		self.title = makeAddonWindowTitle(self.title)
		super(KeyboardProfileSettingsPanel, self).__init__(parent)

	def makeSettings(self, settingsSizer):
		from .nvdaConfig import _NVDAConfigManager
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a group of editing options in the Keyboard profile settings panel.
		groupText = _("Clipboard")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = gui.guiHelper.BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the Keyboard profile settings panel.
		labelText = _("Text used as a &separator between contents added to the clipboard.")
		self.setSeparatorEdit = group.addLabeledControl(labelText, wx.TextCtrl)
		self.setSeparatorEdit.SetValue(_NVDAConfigManager.getAddToClipSeparator())
		self.bindHelpEvent(getHelpObj("hdr7-1"), self.setSeparatorEdit)
		# Translators: This is the label for a checkbox in the Keyboard settings panel.
		labelText = _("&Add text before clipboard datas")
		self.addTextBeforeCheckBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.addTextBeforeCheckBox.SetValue(_NVDAConfigManager.toggleAddTextBeforeOption(False))
		self.bindHelpEvent(getHelpObj("hdr7-1"), self.addTextBeforeCheckBox)
		# Translators: This is the label for a combobox in the Keyboard profile settings panel.
		labelText = _("Ask &confirmation before adding")
		self.confirmToAddToClipCheckBox = group.addItem(wx.CheckBox(self, label=labelText))
		self.confirmToAddToClipCheckBox .SetValue(_NVDAConfigManager.toggleAddTextBeforeOption(False))
		self.bindHelpEvent(getHelpObj("hdr7-1"), self.confirmToAddToClipCheckBox)
		labelText = _("&Remanence's delay (in milliseconds):")

	def saveSettingChanges(self):
		from .nvdaConfig import _NVDAConfigManager
		self.restartNVDA = False
		_NVDAConfigManager.setAddToClipSeparator(self.setSeparatorEdit .GetValue())
		if self.addTextBeforeCheckBox.IsChecked() != _NVDAConfigManager.toggleAddTextBeforeOption(False):
			_NVDAConfigManager.toggleAddTextBeforeOption(True)
		if self.confirmToAddToClipCheckBox.IsChecked() != _NVDAConfigManager.toggleConfirmToAddToClipOption(False):
			_NVDAConfigManager.toggleConfirmToAddToClipOption(True)

	def onSave(self):
		self.saveSettingChanges()


class TextAnalyzerProfileSettingsPanel(
	contextHelpEx.ContextHelpMixinEx,
	SettingsPanel):
	# Translators: This is the label for the text analyzer profile settings panel.
	title = _("Text analysis")
	helpObj = getHelpObj("hdr31")

	def __init__(self, parent):
		self.title = makeAddonWindowTitle(self.title)
		super(TextAnalyzerProfileSettingsPanel, self).__init__(parent)

	def getSounds(self):
		path = addonHandler.getCodeAddon().path
		soundsDir = os.path.join(path, "sounds", "text analyzer alerts")
		itemList = os.listdir(soundsDir)
		filesList = []
		for item in itemList:
			theFile = os.path.join(soundsDir, item)
			if not(os.path.isdir(theFile))\
				and (os.path.splitext(theFile)[1] == ".wav"):
				filesList.append(item)
		return filesList

	def makeSettings(self, settingsSizer):
		from .nvdaConfig import _NVDAConfigManager
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a checkbox in the TextAnalyzer settings panel.
		labelText = _("&Activate text analyzer")
		self.textAnalyzerActivationCheckBox = sHelper.addItem(wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.textAnalyzerActivationCheckBox.SetValue(_NVDAConfigManager.toggleTextAnalyzerActivationOption(False))
		self.bindHelpEvent(getHelpObj("hdr31-1"), self.textAnalyzerActivationCheckBox)
		# Translators: This is the label for a checkbox in the TextAnalyzer settings panel.
		labelText = _("Activate text analyzer at add-on's &start")
		self.textAnalyzerActivationAtStartCheckBox = sHelper.addItem(wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.textAnalyzerActivationAtStartCheckBox.SetValue(_NVDAConfigManager.toggleTextAnalyzerActivationAtStartOption(False))
		self.bindHelpEvent(getHelpObj("hdr31-1"), self.textAnalyzerActivationAtStartCheckBox)
		# Translators: This is the label for a group of editing options in the TextAnalyzer settings panel.
		groupText = _("Symbols match")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = gui.guiHelper.BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the TextAnalyzer settings panel.
		labelText = _("Report &discrepancies")
		self.reportSymbolsDiscrepanciesCheckBox = group.addItem(wx.CheckBox(groupBox, wx.ID_ANY, label=labelText))
		self.reportSymbolsDiscrepanciesCheckBox .SetValue(_NVDAConfigManager.toggleReportSymbolMismatchAnalysisOption(False))
		self.bindHelpEvent(getHelpObj("hdr31-2-1"), self.reportSymbolsDiscrepanciesCheckBox)
		# Translators: This is the label for a checkListBox in the TextAnalyzer settings panel.
		labelText = _("S&ymbols:")
		from ..textAnalysis.symbols import getSymbolChoiceLabels
		self.symbolLabels = getSymbolChoiceLabels()
		self.symbolOptions = _NVDAConfigManager.getSymbolOptionsForDiscrepanciesAnalysis()
		self.symbolsCheckListBox = group.addLabeledControl(
			labelText,
			nvdaControls.CustomCheckListBox,
			choices=[self.symbolLabels[x] for x in list(self.symbolOptions.keys())],
			)
		if self.symbolsCheckListBox.GetCount():
			self.symbolsCheckListBox.SetSelection(0)
		self.bindHelpEvent(getHelpObj("hdr31-2-1"), self.symbolsCheckListBox)
		strings = []
		for symbol in self.symbolOptions:
			if self.symbolOptions[symbol]:
				strings.append(self.symbolLabels[symbol])
		self.symbolsCheckListBox.SetCheckedStrings(strings)
		# anomalies group
		# Translators: This is the label for a group of editing options in the TextAnalyzer settings panel.
		groupText = _("Anomalies")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = gui.guiHelper.BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the TextAnalyzer settings panel.
		labelText = _("Report a&nomalies")
		self.reportAnomaliesCheckBox = group.addItem(wx.CheckBox(groupBox, wx.ID_ANY, label=labelText))
		self.reportAnomaliesCheckBox .SetValue(_NVDAConfigManager.toggleReportAnomaliesOption(False))
		self.bindHelpEvent(getHelpObj("hdr31-2-2"), self.reportAnomaliesCheckBox)
		# Translators: This is the label for a checkListbox in the TextAnalyzer settings panel.
		labelText = _("&Verify:")
		from .nvdaConfig import anomalyLabels
		self.anomaliesCheckListBox = group.addLabeledControl(
			labelText,
			nvdaControls.CustomCheckListBox,
			choices=[label for anomaly, label in anomalyLabels.items()]
			)
		self.anomaliesCheckListBox.SetSelection(0)
		self.bindHelpEvent(getHelpObj("hdr31-2-2"), self.anomaliesCheckListBox)
		self.anomaliesOptions = _NVDAConfigManager.getAnomaliesOptions()
		for anomaly in anomalyLabels:
			index = list(anomalyLabels.keys()).index(anomaly)
			if self.anomaliesOptions[anomaly]:
				self.anomaliesCheckListBox.Check(index)
		self.anomaliesCheckListBox.Bind(
			wx.EVT_LISTBOX, self.onSelectAnomaly)
		# Translators: label for a checkListbox in TextAnalysis settings panel.
		labelText = _("&For symbols:")
		from ..textAnalysis.symbols import getSymbols_all
		self.symbolsAndSpaceCheckListBox = group.addLabeledControl(
			labelText,
			nvdaControls.CustomCheckListBox,
			choices=[x for x in getSymbols_all()]
			)
		self.symbolsAndSpaceCheckListBox .Bind(
			wx.EVT_CHECKLISTBOX, self.onCheckPunctuation)
		self.bindHelpEvent(getHelpObj("hdr31-2-2"), self.symbolsAndSpaceCheckListBox)
		# formatting changes groupe
		# Translators: This is the label for a group of editing options in the TextAnalyzer settings panel.
		groupText = _("Formatting")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = gui.guiHelper.BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the TextAnalyzer settings panel.
		labelText = _("Report &changes")
		self.reportFormattingChangesCheckBox = group.addItem(wx.CheckBox(groupBox, wx.ID_ANY, label=labelText))
		self.reportFormattingChangesCheckBox.SetValue(_NVDAConfigManager.toggleReportFormattingChangesOption(False))
		self.bindHelpEvent(getHelpObj("hdr31-2-3"), self.reportFormattingChangesCheckBox)
		# Translators: This is the label for a checkListbox in the TextAnalyzer settings panel.
		labelText = _("Ty&pe:")
		from .nvdaConfig import formattingChangeLabels
		self.formattingChangesCheckListBox = group.addLabeledControl(
			labelText,
			nvdaControls.CustomCheckListBox,
			choices=[label for formattingChange, label in formattingChangeLabels.items()]
			)
		self.formattingChangesCheckListBox.SetSelection(0)
		self.bindHelpEvent(getHelpObj("hdr31-2-3"), self.formattingChangesCheckListBox)
		self.formattingChangesOptions = _NVDAConfigManager.getFormattingChangesOptions()
		for formattingChange in formattingChangeLabels:
			index = list(formattingChangeLabels.keys()).index(formattingChange)
			if self.formattingChangesOptions[formattingChange]:
				self.formattingChangesCheckListBox.Check(index)
		# Translators: This is the label for a group of editing options in the TextAnalyzer settings panel.
		groupText = _("Alert")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = gui.guiHelper.BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a choice box in the TextAnalyzer settings panel.
		labelText = _("Report &by:")
		from .nvdaConfig import reportByChoiceLabels
		self.reportByChoiceBox = group.addLabeledControl(
			labelText,
			wx.Choice,
			choices=[label for option, label in reportByChoiceLabels.items()]
			)
		option = _NVDAConfigManager.getReportByOption()
		self.reportByChoiceBox.SetSelection(list(reportByChoiceLabels.keys()).index(option))
		self.reportByChoiceBox .Bind(
			wx.EVT_CHOICE, self.onSelectReportBy)
		self.bindHelpEvent(getHelpObj("hdr31-1"), self.reportByChoiceBox)
		# Translators: This is the label for a choice box in the textAnalyzer settings panel.
		labelText = _("Sounds:")
		soundFiles = self.getSounds()
		soundChoices = [os.path.splitext(file)[0] for file in soundFiles]
		self.soundsChoiceBox = group.addLabeledControl(labelText, wx.Choice, choices=soundChoices)
		file = _NVDAConfigManager.getSoundFileName()
		self.soundsChoiceBox.SetStringSelection(os.path.splitext(file)[0])
		self.soundsChoiceBox.Bind(
			wx.EVT_CHOICE, self.onSelectSound)
		self.bindHelpEvent(getHelpObj("hdr31-1"), self.soundsChoiceBox)
		# for reportByBeep option
		(frequency, length) = _NVDAConfigManager.getBeepFrequencyAndLength()
		choices = [str(x) for x in range(1010, 5, -5)]
		# Translators: This is the label for a choice box in the textAnalyzer settings panel.
		labelText = _("Frequency:")
		self.beepFrequencyChoiceBox = group.addLabeledControl(labelText, wx.Choice, choices=choices)
		self.beepFrequencyChoiceBox .SetStringSelection(str(frequency))
		self.bindHelpEvent(getHelpObj("hdr31-1"), self.beepFrequencyChoiceBox)
		# Translators: This is the label for a choice box in the textAnalyzer settings panel.
		labelText = _("Length:")
		self.beepLengthChoiceBox = group.addLabeledControl(labelText, wx.Choice, choices=choices)
		self.beepLengthChoiceBox .SetStringSelection(str(length))
		self.bindHelpEvent(getHelpObj("hdr31-1"), self.beepLengthChoiceBox)
		# Translators: This is the label for a edit box in the textAnalyzer settings panel.
		labelText = _("Message:")
		self.alertMessageEditBox = sHelper.addLabeledControl(
			labelText, wx.TextCtrl)
		self.bindHelpEvent(getHelpObj("hdr31-1"), self.alertMessageEditBox)
		self.alertMessageEditBox.Value = _NVDAConfigManager.getAlertMessage()
		self.onSelectAnomaly(None)
		self.onSelectReportBy(None)

	def onCheckPunctuation(self, evt):
		from .nvdaConfig import _NVDAConfigManager
		anomalyLabel = self.anomaliesCheckListBox.GetStringSelection()
		anomalyId = _NVDAConfigManager.getAnomalyWithPunctuationsOptionId(anomalyLabel)
		if anomalyId is None:
			# not possible
			evt.Skip()
			return
		# update all checked punctuations
		punctuations = self.symbolsAndSpaceCheckListBox .GetCheckedStrings()
		self.symbolsAndSpaceDic[anomalyId] = "".join(punctuations)
		evt.Skip()

	def onSelectAnomaly(self, evt):
		from .nvdaConfig import _NVDAConfigManager
		anomalyLabel = self.anomaliesCheckListBox.GetStringSelection()
		anomalyId = _NVDAConfigManager.getAnomalyWithPunctuationsOptionId(anomalyLabel)
		if anomalyId is None:
			# anomaly option without punctuations list
			self.symbolsAndSpaceCheckListBox .Disable()
			if evt is not None:
				evt.Skip()
			return
		from ..textAnalysis import symbols
		allPunctuations = symbols.getSymbols_all()
		self.symbolsAndSpaceCheckListBox .Clear()
		self.symbolsAndSpaceCheckListBox .AppendItems(list(allPunctuations))
		if not hasattr(self, "symbolsAndSpaceDic"):
			self.symbolsAndSpaceDic = _NVDAConfigManager.getSymbolsAndSpaceDic()
		selectedPunctuations = self.symbolsAndSpaceDic[anomalyId]
		self.symbolsAndSpaceCheckListBox .SetCheckedStrings(list(selectedPunctuations))
		self.symbolsAndSpaceCheckListBox .Enable()
		if evt is None:
			return
		evt.Skip()

	def onSelectSound(self, evt):
		fileName = self.soundsChoiceBox.GetStringSelection() + ".wav"
		path = addonHandler.getCodeAddon().path
		file = os.path.join(path, "sounds", "text analyzer alerts", fileName)
		nvwave.playWaveFile(file)
		evt.Skip()

	def onSelectReportBy(self, evt):
		from .nvdaConfig import _NVDAConfigManager
		reportByChoice = self.reportByChoiceBox .GetStringSelection()
		if _NVDAConfigManager.isReportBySoundOption(reportByChoice):
			self.soundsChoiceBox.Enable()
			self.beepFrequencyChoiceBox .Disable()
			self.beepLengthChoiceBox .Disable()
			self.alertMessageEditBox.Disable()
		elif _NVDAConfigManager.isReportByBeepOption(reportByChoice):
			self.beepFrequencyChoiceBox .Enable()
			self.beepLengthChoiceBox .Enable()
			self.soundsChoiceBox.Disable()
			self.alertMessageEditBox.Disable()
		elif _NVDAConfigManager.isReportByAlertMessageOption(reportByChoice):
			self.alertMessageEditBox.Enable()
			self.soundsChoiceBox.Disable()
			self.beepFrequencyChoiceBox .Disable()
			self.beepLengthChoiceBox .Disable()
		else:
			self.soundsChoiceBox.Disable()
			self.beepFrequencyChoiceBox .Disable()
			self.beepLengthChoiceBox .Disable()
			self.alertMessageEditBox.Disable()
		if evt:
			evt.Skip()

	def saveSettingChanges(self):
		from .nvdaConfig import _NVDAConfigManager
		self.restartNVDA = False
		if self.textAnalyzerActivationCheckBox.IsChecked() != _NVDAConfigManager.toggleTextAnalyzerActivationOption(False):
			_NVDAConfigManager.toggleTextAnalyzerActivationOption(True)
		if self.textAnalyzerActivationAtStartCheckBox.IsChecked() != _NVDAConfigManager.toggleTextAnalyzerActivationAtStartOption(False):
			_NVDAConfigManager.toggleTextAnalyzerActivationAtStartOption(True)
		if self.reportSymbolsDiscrepanciesCheckBox .IsChecked() != _NVDAConfigManager.toggleReportSymbolMismatchAnalysisOption(False):
			_NVDAConfigManager.toggleReportSymbolMismatchAnalysisOption(True)
		checkedStrings = self.symbolsCheckListBox.GetCheckedStrings()
		for symbol in self.symbolOptions:
			label = self.symbolLabels[symbol]
			isChecked = True if label in checkedStrings else False
			self.symbolOptions[symbol] = isChecked
		_NVDAConfigManager.setSymbolOptionsForDiscrepanciesAnalysis(self.symbolOptions)
		# anomalies group
		if self.reportAnomaliesCheckBox .IsChecked() != _NVDAConfigManager.toggleReportAnomaliesOption(False):
			_NVDAConfigManager.toggleReportAnomaliesOption(True)
		for index in range(0, self.anomaliesCheckListBox.Count):
			isChecked = self.anomaliesCheckListBox.IsChecked(index)
			from .nvdaConfig import anomalyLabels
			anomaly = list(anomalyLabels.keys())[index]
			self.anomaliesOptions[anomaly] = isChecked
		_NVDAConfigManager.setAnomaliesOptions(self.anomaliesOptions)
		if hasattr(self, "symbolsAndSpaceDic"):
			_NVDAConfigManager.setSymbolsAndSpaceDic(self.symbolsAndSpaceDic)
		# formatting changes group
		if self.reportFormattingChangesCheckBox .IsChecked() != _NVDAConfigManager.toggleReportFormattingChangesOption(False):
			_NVDAConfigManager.toggleReportFormattingChangesOption(True)
		for index in range(0, self.formattingChangesCheckListBox.Count):
			isChecked = self.formattingChangesCheckListBox.IsChecked(index)
			from .nvdaConfig import formattingChangeLabels
			formattingChange = list(formattingChangeLabels.keys())[index]
			self.formattingChangesOptions[formattingChange] = isChecked
		_NVDAConfigManager.setFormattingChangesOptions(self.formattingChangesOptions)
		from .nvdaConfig import reportByChoiceLabels
		index = self.reportByChoiceBox.GetSelection()
		option = [x for x in reportByChoiceLabels.keys()][index]
		_NVDAConfigManager.setReportByOption(option)
		fileName = self.soundsChoiceBox.GetStringSelection() + ".wav"
		_NVDAConfigManager.setSoundFileName(fileName)
		frequency = self.beepFrequencyChoiceBox.GetStringSelection()
		length = self.beepLengthChoiceBox.GetStringSelection()
		_NVDAConfigManager.setBeepFrequencyAndLength(frequency, length)
		_NVDAConfigManager.setAlertMessage(self.alertMessageEditBox.GetValue())

	def onSave(self):
		self.saveSettingChanges()


class ProfileSettingsDialog(MultiCategorySettingsDialogEx):
	INITIAL_SIZE = (1000, 480)
	# Min height required to show the OK, Cancel, Apply buttons
	MIN_SIZE = (470, 240)
	baseCategoryClasses = [
		NVDAEnhancementProfileSettingsPanel,
		KeyboardProfileSettingsPanel,
		TextAnalyzerProfileSettingsPanel,
		]

	def __init__(self, parent, initialCategory=None):
		curAddon = addonHandler.getCodeAddon()
		currentProfile = config.conf.profiles[-1].name
		if currentProfile is None:
			currentProfile = NVDAString("normal configuration")
		# Translators: title of add-on settings dialog.
		dialogTitle = _("Profile settings's %s") % currentProfile
		self.title = "%s - %s" % (curAddon.manifest["summary"], dialogTitle)
		self.categoryClasses = self.baseCategoryClasses[:]

		super(ProfileSettingsDialog, self).__init__(parent, initialCategory)
