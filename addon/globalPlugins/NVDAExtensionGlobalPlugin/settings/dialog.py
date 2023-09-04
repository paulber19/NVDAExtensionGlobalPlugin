# globalPlugins\NVDAExtensionGlobalPlugin\settings\dialog.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2022 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import wx
import os
import config
import nvwave
from gui.settingsDialogs import MultiCategorySettingsDialog, SettingsPanel
import gui
from gui import nvdaControls
import core
import characterProcessing
import queueHandler
from languageHandler import getLanguage
from gui.guiHelper import BoxSizerHelper
from versionInfo import version_year, version_major
from ..settings import _addonConfigManager
from ..utils.NVDAStrings import NVDAString
from ..utils import makeAddonWindowTitle, getHelpObj
from ..utils.secure import inSecureMode
from ..utils import contextHelpEx


addonHandler.initTranslation()

_helpMsg = _("Press F1 for help")


def askForNVDARestart():
	if gui.messageBox(
		# Translators: A message asking the user if they wish to restart NVDA
		# as NVDAExtensionGlobalPlugin addon settings changes have been made.
		_(
			"Some changes have been made. "
			"You must save the configuration and restart NVDA for these changes to take effect. "
			"Would you like to do it now?"),
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
		from .addonConfig import (
			C_Install, C_DoNotInstall, C_InstallWithoutGesture,
			FCT_ExtendedVirtualBuffer, FCT_SystrayIconsAndActiveWindowsList,
			FCT_ComplexSymbols, FCT_ClipboardCommandAnnouncement,
			FCT_CurrentFolderReport, FCT_FocusedApplicationInformations,
			FCT_OpenCurrentOrOldNVDALogFile, FCT_SpeechHistory,
			FCT_KeyboardKeyRenaming, FCT_CommandKeysSelectiveAnnouncement,
			FCT_MinuteTimer, FCT_ForegroundWindowObjectsList,
			FCT_VoiceProfileSwitching, FCT_KeyRemanence,
			FCT_RestartInDebugMode, FCT_VolumeControl,
			FCT_SplitAudio, FCT_Tools, FCT_DateAndTime,
			FCT_TextAnalysis, FCT_TemporaryAudioDevice,
		)
		from ..settings import getInstallFeatureOption

		installChoiceLabels = {
			C_DoNotInstall: _("Do not install"),
			C_Install: _("Install"),
			C_InstallWithoutGesture: _("Install without gesture"),
		}
		installChoice = [installChoiceLabels[x] for x in [C_DoNotInstall, C_Install, C_InstallWithoutGesture]]
		sHelper = BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("Display &systray icons and running application windows list:")
		self.installSystrayIconsListFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice)
		self.installSystrayIconsListFeatureOptionBox .SetSelection(
			getInstallFeatureOption(FCT_SystrayIconsAndActiveWindowsList))
		self.bindHelpEvent(getHelpObj("hdr1"), self.installSystrayIconsListFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("&Complex symbols edition help:")
		self.installComplexSymbolsFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice)
		self.installComplexSymbolsFeatureOptionBox .SetSelection(getInstallFeatureOption(FCT_ComplexSymbols))
		self.bindHelpEvent(getHelpObj("hdr3"), self.installComplexSymbolsFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("&Focused application's informations:")
		self.installFocusedApplicationInformationsFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice)
		self.installFocusedApplicationInformationsFeatureOptionBox.SetSelection(
			getInstallFeatureOption(FCT_FocusedApplicationInformations))
		self.bindHelpEvent(getHelpObj("hdr4"), self.installFocusedApplicationInformationsFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("&Extended Virtual Buffer:")
		self.installExtendedVirtualBufferFeaturesOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice[:-1])
		self.installExtendedVirtualBufferFeaturesOptionBox .SetSelection(
			getInstallFeatureOption(FCT_ExtendedVirtualBuffer))
		self.bindHelpEvent(getHelpObj("hdr5"), self.installExtendedVirtualBufferFeaturesOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("C&lipboard command announcement:")
		self.installClipboardCommandAnnouncementFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice[:-1])
		self.installClipboardCommandAnnouncementFeatureOptionBox .SetSelection(
			getInstallFeatureOption(FCT_ClipboardCommandAnnouncement))
		self.bindHelpEvent(getHelpObj("hdr7"), self.installClipboardCommandAnnouncementFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("""Anno&uncement of the preselected folder in "Open", "Save", "Save as" dialog boxes:""")
		self.installCurrentFolderReportFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice)
		self.bindHelpEvent(getHelpObj("hdr8"), self.installCurrentFolderReportFeatureOptionBox)
		self.installCurrentFolderReportFeatureOptionBox.SetSelection(
			getInstallFeatureOption(FCT_CurrentFolderReport))
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("&NVDA's log Files:")
		self.installOpenCurrentOrOldNVDALogFileFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice)
		self.installOpenCurrentOrOldNVDALogFileFeatureOptionBox.SetSelection(
			getInstallFeatureOption(FCT_OpenCurrentOrOldNVDALogFile))
		self.bindHelpEvent(getHelpObj("hdr9"), self.installOpenCurrentOrOldNVDALogFileFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("Speech &history:")
		self.installSpeechHistoryFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice)
		self.installSpeechHistoryFeatureOptionBox.SetSelection(getInstallFeatureOption(FCT_SpeechHistory))
		self.bindHelpEvent(getHelpObj("hdr10"), self.installSpeechHistoryFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("&Keyboard keys renaming:")
		self.installKeyboardKeyRenamingFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice[:-1])
		self.installKeyboardKeyRenamingFeatureOptionBox.SetSelection(
			getInstallFeatureOption(FCT_KeyboardKeyRenaming))
		self.bindHelpEvent(getHelpObj("hdr12"), self.installKeyboardKeyRenamingFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("C&ommand keys selective announcement:")
		self.installCommandKeysSelectiveAnnouncementFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice[:-1])
		self.installCommandKeysSelectiveAnnouncementFeatureOptionBox.SetSelection(
			getInstallFeatureOption(FCT_CommandKeysSelectiveAnnouncement))
		self.bindHelpEvent(getHelpObj("hdr13"), self.installCommandKeysSelectiveAnnouncementFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("Minute &timer:")
		self.installMinuteTimerFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice)
		self.installMinuteTimerFeatureOptionBox.SetSelection(getInstallFeatureOption(FCT_MinuteTimer))
		self.bindHelpEvent(getHelpObj("hdr14"), self.installMinuteTimerFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("NVDA's &restart:")
		self.installRestartInDebugModeFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice)
		self.installRestartInDebugModeFeatureOptionBox.SetSelection(getInstallFeatureOption(FCT_RestartInDebugMode))
		self.bindHelpEvent(getHelpObj("hdr15"), self.installRestartInDebugModeFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("Display visible items making up the foreground &object:")
		self.installForegroundWindowObjectsListFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice)
		self.installForegroundWindowObjectsListFeatureOptionBox.SetSelection(
			getInstallFeatureOption(FCT_ForegroundWindowObjectsList))
		self.bindHelpEvent(getHelpObj("hdr16"), self.installForegroundWindowObjectsListFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("&Voice profile switching:")
		self.installVoiceProfileSwitchingFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice)
		self.installVoiceProfileSwitchingFeatureOptionBox.SetSelection(
			getInstallFeatureOption(FCT_VoiceProfileSwitching))
		self.bindHelpEvent(getHelpObj("hdr17"), self.installVoiceProfileSwitchingFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("Ke&ys's remanence:")
		self.installKeyRemanenceFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice[:-1])
		self.installKeyRemanenceFeatureOptionBox.SetSelection(getInstallFeatureOption(FCT_KeyRemanence))
		self.bindHelpEvent(getHelpObj("hdr18"), self.installKeyRemanenceFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("Volu&me's control:")
		self.installVolumeControlFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice)
		self.installVolumeControlFeatureOptionBox.SetSelection(getInstallFeatureOption(FCT_VolumeControl))
		self.bindHelpEvent(getHelpObj("hdr21"), self.installVolumeControlFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("&audio split:")
		self.installSplitAudioFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice)
		self.installSplitAudioFeatureOptionBox.SetSelection(getInstallFeatureOption(FCT_SplitAudio))
		self.bindHelpEvent(getHelpObj("hdr34"), self.installSplitAudioFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("&Development's tools:")
		self.installDevToolsFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice[:-1])
		self.installDevToolsFeatureOptionBox.SetSelection(getInstallFeatureOption(FCT_Tools))
		self.bindHelpEvent(getHelpObj("hdr22"), self.installDevToolsFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("&Date and time - supplements:")
		self.installDateAndTimeFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice[:])
		self.installDateAndTimeFeatureOptionBox.SetSelection(getInstallFeatureOption(FCT_DateAndTime))
		self.bindHelpEvent(getHelpObj("hdr24"), self.installDateAndTimeFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("Text anal&ysis:")
		self.installTextAnalysisFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice[:])
		self.installTextAnalysisFeatureOptionBox.SetSelection(getInstallFeatureOption(FCT_TextAnalysis))
		self.bindHelpEvent(getHelpObj("hdr31"), self.installTextAnalysisFeatureOptionBox)
		# Translators: This is the label for a listbox in the FeaturesInstallation settings panel.
		labelText = _("Temporar&y audio device:")
		self.installTemporaryAudioDeviceFeatureOptionBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=installChoice[:-1])
		self.installTemporaryAudioDeviceFeatureOptionBox.SetSelection(
			getInstallFeatureOption(FCT_TemporaryAudioDevice))
		self.bindHelpEvent(getHelpObj("hdr33"), self.installTemporaryAudioDeviceFeatureOptionBox)

	def saveSettingChanges(self):
		from .addonConfig import (
			C_Install, C_DoNotInstall,
			C_NVDAVolumeLevel, C_MinNVDAVolumeLevel,
			C_MasterVolumeLevel, C_MinMasterVolumeLevel, C_MaximumOfLastUsedSymbols,
			FCT_ExtendedVirtualBuffer, FCT_SystrayIconsAndActiveWindowsList,
			FCT_ComplexSymbols, FCT_ClipboardCommandAnnouncement,
			FCT_CurrentFolderReport, FCT_FocusedApplicationInformations,
			FCT_OpenCurrentOrOldNVDALogFile, FCT_SpeechHistory,
			FCT_KeyboardKeyRenaming, FCT_CommandKeysSelectiveAnnouncement,
			FCT_MinuteTimer, FCT_ForegroundWindowObjectsList,
			FCT_VoiceProfileSwitching, FCT_KeyRemanence,
			FCT_RestartInDebugMode, FCT_VolumeControl,
			FCT_SplitAudio, FCT_Tools, FCT_DateAndTime,
			FCT_TextAnalysis, FCT_TemporaryAudioDevice,
		)
		from ..settings import (
			getInstallFeatureOption, setInstallFeatureOption,
			toggleLoopInNavigationModeOption,
			toggleSpeechRecordWithNumberOption, toggleSpeechRecordInAscendingOrderOption,
			toggleSetOnMainAndNVDAVolumeAdvancedOption, toggleReportTimeWithSecondsOption,
		)
		self.restartNVDA = False
		option = getInstallFeatureOption(FCT_ExtendedVirtualBuffer)
		if self.installExtendedVirtualBufferFeaturesOptionBox.GetSelection() != option:
			setInstallFeatureOption(
				FCT_ExtendedVirtualBuffer, self.installExtendedVirtualBufferFeaturesOptionBox.GetSelection())
			self.restartNVDA = True
			if getInstallFeatureOption(FCT_ExtendedVirtualBuffer) == C_Install:
				# set LoopInNavigationModeOption to default state (False)
				if toggleLoopInNavigationModeOption(False):
					toggleLoopInNavigationModeOption(True)
		option = getInstallFeatureOption(FCT_SystrayIconsAndActiveWindowsList)
		if self.installSystrayIconsListFeatureOptionBox.GetSelection() != option:
			setInstallFeatureOption(
				FCT_SystrayIconsAndActiveWindowsList, self.installSystrayIconsListFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		if self.installComplexSymbolsFeatureOptionBox.GetSelection() != getInstallFeatureOption(FCT_ComplexSymbols):
			setInstallFeatureOption(FCT_ComplexSymbols, self.installComplexSymbolsFeatureOptionBox.GetSelection())
			self.restartNVDA = True
			if getInstallFeatureOption(FCT_ComplexSymbols) == C_DoNotInstall:
				# set parameters to default values
				_addonConfigManager.setMaximumOfLastUsedSymbols(C_MaximumOfLastUsedSymbols)
				_addonConfigManager.deleceAllUserComplexSymbols()
		option = getInstallFeatureOption(FCT_ClipboardCommandAnnouncement)
		if self.installClipboardCommandAnnouncementFeatureOptionBox.GetSelection() != option:
			setInstallFeatureOption(
				FCT_ClipboardCommandAnnouncement, self.installClipboardCommandAnnouncementFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		option = getInstallFeatureOption(FCT_CurrentFolderReport)
		if self.installCurrentFolderReportFeatureOptionBox.GetSelection() != option:
			setInstallFeatureOption(
				FCT_CurrentFolderReport, self.installCurrentFolderReportFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		option = getInstallFeatureOption(FCT_FocusedApplicationInformations)
		if self.installFocusedApplicationInformationsFeatureOptionBox.GetSelection() != option:
			setInstallFeatureOption(
				FCT_FocusedApplicationInformations,
				self.installFocusedApplicationInformationsFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		option = getInstallFeatureOption(FCT_OpenCurrentOrOldNVDALogFile)
		if self.installOpenCurrentOrOldNVDALogFileFeatureOptionBox.GetSelection() != option:
			setInstallFeatureOption(
				FCT_OpenCurrentOrOldNVDALogFile, self.installOpenCurrentOrOldNVDALogFileFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		if self.installSpeechHistoryFeatureOptionBox.GetSelection() != getInstallFeatureOption(FCT_SpeechHistory):
			setInstallFeatureOption(FCT_SpeechHistory, self.installSpeechHistoryFeatureOptionBox.GetSelection())
			self.restartNVDA = True
			if getInstallFeatureOption(FCT_SpeechHistory) == C_DoNotInstall:
				# set parameters to Default values
				if not toggleSpeechRecordWithNumberOption(False):
					toggleSpeechRecordWithNumberOption(True)
				if toggleSpeechRecordInAscendingOrderOption(False):
					toggleSpeechRecordInAscendingOrderOption(True)
		option = getInstallFeatureOption(FCT_KeyboardKeyRenaming)
		if self.installKeyboardKeyRenamingFeatureOptionBox.GetSelection() != option:
			setInstallFeatureOption(
				FCT_KeyboardKeyRenaming, self.installKeyboardKeyRenamingFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		option = getInstallFeatureOption(FCT_CommandKeysSelectiveAnnouncement)
		if self.installCommandKeysSelectiveAnnouncementFeatureOptionBox.GetSelection() != option:
			setInstallFeatureOption(
				FCT_CommandKeysSelectiveAnnouncement,
				self.installCommandKeysSelectiveAnnouncementFeatureOptionBox.GetSelection())
			self.restartNVDA = True
			if getInstallFeatureOption(FCT_CommandKeysSelectiveAnnouncement) == C_DoNotInstall:
				# delete all command selective announcement feature configuration
				from .nvdaConfig import _NVDAConfigManager
				_NVDAConfigManager.deleceCommandKeyAnnouncementConfiguration()
		if self.installMinuteTimerFeatureOptionBox.GetSelection() != getInstallFeatureOption(FCT_MinuteTimer):
			setInstallFeatureOption(FCT_MinuteTimer, self.installMinuteTimerFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		option = getInstallFeatureOption(FCT_ForegroundWindowObjectsList)
		if self.installForegroundWindowObjectsListFeatureOptionBox.GetSelection() != option:
			setInstallFeatureOption(
				FCT_ForegroundWindowObjectsList, self.installForegroundWindowObjectsListFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		option = getInstallFeatureOption(FCT_VoiceProfileSwitching)
		if self.installVoiceProfileSwitchingFeatureOptionBox.GetSelection() != option:
			setInstallFeatureOption(
				FCT_VoiceProfileSwitching, self.installVoiceProfileSwitchingFeatureOptionBox.GetSelection())
			self.restartNVDA = True
			if getInstallFeatureOption(FCT_VoiceProfileSwitching) == C_DoNotInstall:
				from ..switchVoiceProfile import SwitchVoiceProfilesManager
				SwitchVoiceProfilesManager().deleteAllProfiles()

		if self.installKeyRemanenceFeatureOptionBox.GetSelection() != getInstallFeatureOption(FCT_KeyRemanence):
			setInstallFeatureOption(FCT_KeyRemanence, self.installKeyRemanenceFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		option = getInstallFeatureOption(FCT_RestartInDebugMode)
		if self.installRestartInDebugModeFeatureOptionBox.GetSelection() != option:
			setInstallFeatureOption(
				FCT_RestartInDebugMode, self.installRestartInDebugModeFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		if self.installVolumeControlFeatureOptionBox.GetSelection() != getInstallFeatureOption(FCT_VolumeControl):
			setInstallFeatureOption(FCT_VolumeControl, self.installVolumeControlFeatureOptionBox.GetSelection())
			self.restartNVDA = True
			if getInstallFeatureOption(FCT_VolumeControl) != C_DoNotInstall:
				# set parameters to default values
				if not toggleSetOnMainAndNVDAVolumeAdvancedOption(False):
					toggleSetOnMainAndNVDAVolumeAdvancedOption(True)
				_addonConfigManager.setMinMasterVolumeLevel(int(C_MinMasterVolumeLevel))
				_addonConfigManager.setMasterVolumeLevel(C_MasterVolumeLevel)
				_addonConfigManager.setMinNVDAVolumeLevel(int(C_MinNVDAVolumeLevel))
				_addonConfigManager.setNVDAVolumeLevel(int(C_NVDAVolumeLevel))
		if self.installSplitAudioFeatureOptionBox.GetSelection() != getInstallFeatureOption(FCT_SplitAudio):
			setInstallFeatureOption(FCT_SplitAudio, self.installSplitAudioFeatureOptionBox.GetSelection())
			self.restartNVDA = True

		if self.installDevToolsFeatureOptionBox.GetSelection() != getInstallFeatureOption(FCT_Tools):
			setInstallFeatureOption(FCT_Tools, self.installDevToolsFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		if self.installDateAndTimeFeatureOptionBox.GetSelection() != getInstallFeatureOption(FCT_DateAndTime):
			setInstallFeatureOption(FCT_DateAndTime, self.installDateAndTimeFeatureOptionBox.GetSelection())
			if not getInstallFeatureOption(FCT_DateAndTime) == C_Install:
				# set report time with second to default value
				if toggleReportTimeWithSecondsOption(False):
					toggleReportTimeWithSecondsOption(True)
			self.restartNVDA = True
		if self.installTextAnalysisFeatureOptionBox.GetSelection() != getInstallFeatureOption(FCT_TextAnalysis):
			setInstallFeatureOption(FCT_TextAnalysis, self.installTextAnalysisFeatureOptionBox.GetSelection())
			self.restartNVDA = True
		option = getInstallFeatureOption(FCT_TemporaryAudioDevice)
		if self.installTemporaryAudioDeviceFeatureOptionBox.GetSelection() != option:
			setInstallFeatureOption(
				FCT_TemporaryAudioDevice, self.installTemporaryAudioDeviceFeatureOptionBox.GetSelection())
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
		from .addonConfig import (
			FCT_ExtendedVirtualBuffer,
			FCT_ComplexSymbols, FCT_SpeechHistory,
			C_DoNotInstall
		)
		from ..settings import (
			getInstallFeatureOption,
			toggleSpeechRecordWithNumberOption,
			toggleSpeechRecordInAscendingOrderOption,
			toggleLoopInNavigationModeOption
		)
		sHelper = BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a group of editing options in the
		# NVDAEnhancement settings panel
		groupText = _("Editing")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a comboBox in the NVDAEnhancement settings panel.
		labelText = _("maximum number of last &used symbols recorded:")
		choices = [x * 10 for x in range(1, 11)]
		choices = list(reversed(choices))
		self.maximumOfLastUsedSymbolsBox = group.addLabeledControl(
			labelText, wx.Choice, choices=[str(x) for x in choices])
		self.maximumOfLastUsedSymbolsBox.SetSelection(
			choices.index(_addonConfigManager.getMaximumOfLastUsedSymbols()))
		self.bindHelpEvent(getHelpObj("hdr3-1"), self.maximumOfLastUsedSymbolsBox)
		if getInstallFeatureOption(FCT_ComplexSymbols) == C_DoNotInstall:
			self.maximumOfLastUsedSymbolsBox.Disable()
		# Translators: This is the label for a group in NVDAEnhancement settings panel
		groupText = _("Speech history")
		groupSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the NVDAEnhancement settings panel.
		labelText = _("&Number the records ")
		self.speechRecordWithNumberOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.speechRecordWithNumberOptionBox.SetValue(toggleSpeechRecordWithNumberOption(False))
		self.bindHelpEvent(getHelpObj("hdr10-1"), self.speechRecordWithNumberOptionBox)
		# Translators: This is the label for a checkbox in the NVDAEnhancement settings panel.
		labelText = _("&Display records in ascending order")
		self.speechRecordInAscendingOrderOptionBox = group.addItem(
			wx.CheckBox(groupBox, wx.ID_ANY, label=labelText))
		self.speechRecordInAscendingOrderOptionBox.SetValue(toggleSpeechRecordInAscendingOrderOption(False))
		self.bindHelpEvent(getHelpObj("hdr10-1"), self.speechRecordInAscendingOrderOptionBox)
		if getInstallFeatureOption(FCT_SpeechHistory) == C_DoNotInstall:
			for item in range(0, group.sizer.GetItemCount()):
				group.sizer.Hide(item)
		# Translators: This is the label for a group NVDAEnhancement settings panel
		groupText = _("Browser")
		groupSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the NVDAEnhancement settings panel.
		labelText = _("&Browse in loop")
		self.loopInNavigationModeOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.loopInNavigationModeOptionBox.SetValue(toggleLoopInNavigationModeOption(False))
		self.bindHelpEvent(getHelpObj("hdr5-5"), self.loopInNavigationModeOptionBox)
		if getInstallFeatureOption(FCT_ExtendedVirtualBuffer) == C_DoNotInstall:
			group.sizer.Hide(0)
		# Translators: This is the label for a group of editing options in the NVDAEnhancement settings panel.
		groupText = _("reporting spelling errors")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a choice box in the TextAnalyzer settings panel.
		labelText = _("Report &by:")
		from .addonConfig import reportingSpellingErrorsChoiceLabels
		self.reportingSpellingErrorsByChoiceBox = group.addLabeledControl(
			labelText,
			wx.Choice,
			choices=[label for option, label in reportingSpellingErrorsChoiceLabels .items()]
		)
		option = _addonConfigManager.getReportingSpellingErrorsByOption()
		self.reportingSpellingErrorsByChoiceBox.SetSelection(
			list(reportingSpellingErrorsChoiceLabels .keys()).index(option))
		self.bindHelpEvent(getHelpObj("hdr104"), self.reportingSpellingErrorsByChoiceBox)
		# Translators: This is the label for a group of editing options in the
		# NVDAEnhancement settings panel
		groupText = _("Clipboard")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a comboBox in the NVDAEnhancement settings panel.
		labelText = _("maximum number of reported characters:")
		choices = [x * 1024 for x in range(1, 1000)]
		choices = list(reversed(choices))
		choiceLabels = [str(x) for x in choices]
		choices = [0, ] + choices
		# Translators: choice for no limit
		choiceLabels.insert(0, _("No limit"))
		self.maximumOfReportedCharactersBox = group.addLabeledControl(
			labelText, wx.Choice, choices=choiceLabels)
		self.maximumOfReportedCharactersBox.SetSelection(
			choices.index(_addonConfigManager.getMaximumClipboardReportedCharacters()))
		self.bindHelpEvent(getHelpObj("hdr7-2"), self.maximumOfReportedCharactersBox)

	def saveSettingChanges(self):
		from ..settings import (
			toggleSpeechRecordWithNumberOption,
			toggleSpeechRecordInAscendingOrderOption,
			toggleLoopInNavigationModeOption
		)
		from . import _addonConfigManager
		self.restartNVDA = False
		if self.speechRecordWithNumberOptionBox.IsChecked() != toggleSpeechRecordWithNumberOption(False):
			toggleSpeechRecordWithNumberOption()
		option = toggleSpeechRecordInAscendingOrderOption(False)
		if self.speechRecordInAscendingOrderOptionBox.IsChecked() != option:
			toggleSpeechRecordInAscendingOrderOption()
		if self.loopInNavigationModeOptionBox.IsChecked() != toggleLoopInNavigationModeOption(False):
			toggleLoopInNavigationModeOption()
		maximumOfLastUsedSymbols = int(self.maximumOfLastUsedSymbolsBox.GetString(
			self.maximumOfLastUsedSymbolsBox.GetSelection()))
		_addonConfigManager.setMaximumOfLastUsedSymbols(maximumOfLastUsedSymbols)
		from .addonConfig import reportingSpellingErrorsChoiceLabels
		index = self.reportingSpellingErrorsByChoiceBox.GetSelection()
		option = [x for x in reportingSpellingErrorsChoiceLabels .keys()][index]
		_addonConfigManager.setReportingSpellingErrorsByOption(option)
		index = self.maximumOfReportedCharactersBox.GetSelection()
		max = 0
		if index:
			max = int(self.maximumOfReportedCharactersBox.GetStringSelection())
		_addonConfigManager.setMaximumClipboardReportedCharacters(max)

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
		from ..settings import (
			getInstallFeatureOption,
			toggleNoDescriptionReportInRibbonOption,
			toggleAutomaticWindowMaximizationOption,
			toggleReportTimeWithSecondsOption,
			toggleSetOnMainAndNVDAVolumeAdvancedOption,
			toggleReportVolumeChangeAdvancedOption,
			toggleIncreaseSpeakersVolumeIfNecessaryAdvancedOption,
			toggleConfirmAudioDeviceChangeAdvancedOption,
			toggleReversedPathWithLevelAdvancedOption
		)
		sHelper = BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a group of editing options in the computer settings panel.
		groupText = _("Windows")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the Computer settings panel.
		labelText = _("&No object description in Windows ribbons")
		self.noDescriptionReportInRibbonOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.noDescriptionReportInRibbonOptionBox.SetValue(toggleNoDescriptionReportInRibbonOption(False))
		self.bindHelpEvent(getHelpObj("hdr100"), self.noDescriptionReportInRibbonOptionBox)
		if inSecureMode():
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
		from .addonConfig import FCT_DateAndTime, C_DoNotInstall
		if getInstallFeatureOption(FCT_DateAndTime) == C_DoNotInstall:
			self.reportTimeWithSecondsOptionBox.Disable()

		# Translators: This is the label for a group of editing options in the computer settings panel.
		groupText = _("Windows explorer")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is a label for a choice box in computer settings panel.
		labelText = _("Number of items to &keep for reduced path:")
		choice = [x for x in reversed(list(range(1, 11)))]
		self.reducedPathItemsNumberBox = group.addLabeledControl(
			labelText, wx.Choice, choices=[str(x) for x in choice])
		self.reducedPathItemsNumberBox .SetSelection(choice.index(_addonConfigManager.getReducedPathItemsNumber()))
		self.bindHelpEvent(getHelpObj("hdr208"), self.reducedPathItemsNumberBox)
		# Translators: This is the label for a checkbox in the Computer settings panel.
		labelText = _("Report folder name of Reversed path with levels")
		self.reversedPathWithLevelOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.reversedPathWithLevelOptionBox .SetValue(toggleReversedPathWithLevelAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr208"), self.reversedPathWithLevelOptionBox)
		# Translators: This is the label for a group in computer settings panel.
		groupText = _("Volume control")
		volumeGroup = BoxSizerHelper(
			self, sizer=wx.StaticBoxSizer(wx.StaticBox(self, label=groupText), wx.VERTICAL))
		sHelper.addItem(volumeGroup)
		# Translators: This is the label for a group in computer settings panel.
		groupText = _("Main and NVDA volume")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
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
		group = BoxSizerHelper(self, sizer=groupSizer)
		volumeGroup.addItem(group)
		# Translators: This is a label for a choice box in computer settings panel.
		labelText = _("&Threshold of recovery of the volume:")
		choice = [10 * x for x in reversed(list(range(0, 11)))]
		self.minMasterVolumeLevelBox = group.addLabeledControl(
			labelText, wx.Choice, choices=[str(x) for x in choice[5:]])
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
		group = BoxSizerHelper(self, sizer=groupSizer)
		volumeGroup.addItem(group)
		# Translators: This is a label for a choice box in computer settings panel.
		labelText = _("T&hreshold of recovery of the volume:")
		self.minNVDAVolumeLevelBox = group.addLabeledControl(
			labelText, wx.Choice, choices=[str(x) + "%" for x in choice])
		self.minNVDAVolumeLevelBox.SetSelection(choice.index(_addonConfigManager.getMinNVDAVolumeLevel()))
		self.bindHelpEvent(getHelpObj("hdr21-7"), self.minNVDAVolumeLevelBox)
		# Translators: This is a label for a choice box in computer settings panel.
		labelText = _("&Recovery level:")
		self.NVDAVolumeLevelBox = group.addLabeledControl(
			labelText, wx.Choice, choices=[str(x) + "%" for x in choice])
		self.NVDAVolumeLevelBox.SetSelection(choice.index(_addonConfigManager.getNVDAVolumeLevel()))
		self.bindHelpEvent(getHelpObj("hdr21-7"), self.NVDAVolumeLevelBox)
		# Translators: This is the label for a group in computer settings panel.
		groupText = _("Volume change")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		volumeGroup.addItem(group)
		# Translators: This is a label for a choice box in computer settings panel.
		labelText = _("Ste&ps's size:")
		choice = [str(x) for x in range(1, 21)]
		self.volumeChangeStepLevelBox = group.addLabeledControl(
			labelText, wx.Choice, choices=list(reversed(choice)))
		self.volumeChangeStepLevelBox.SetStringSelection(str(_addonConfigManager.getVolumeChangeStepLevel())	)
		self.bindHelpEvent(getHelpObj("hdr21-3"), self.volumeChangeStepLevelBox)
		# Translators: This is the label for a checkbox in the computer settings panel.
		labelText = _("R&eport volume changes")
		self.reportVolumeChangeOptionCheckBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.reportVolumeChangeOptionCheckBox.SetValue(toggleReportVolumeChangeAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr21-6"), self.reportVolumeChangeOptionCheckBox)
		# Translators: This is the label for a checkbox in the computer settings panel.
		labelText = _("&Increase speakers volume if necessary")
		self.increaseSpeakersVolumeIfNecessaryOptionCheckBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.increaseSpeakersVolumeIfNecessaryOptionCheckBox .SetValue(
			toggleIncreaseSpeakersVolumeIfNecessaryAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr21-8"), self.increaseSpeakersVolumeIfNecessaryOptionCheckBox)
		from .addonConfig import FCT_VolumeControl
		if not getInstallFeatureOption(FCT_VolumeControl):
			for item in range(0, volumeGroup.sizer.GetItemCount()):
				volumeGroup.sizer.Hide(item)
		groupText = _("Temporary audio device")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the Computer settings panel.
		labelText = _("Ask for confirmation")
		self.confirmAudioDeviceChangeCheckBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.confirmAudioDeviceChangeCheckBox.SetValue(toggleConfirmAudioDeviceChangeAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr33"), self.confirmAudioDeviceChangeCheckBox)
		# Translators: This is a label for a choice box in computer settings panel.
		labelText = _("ma&ximum waiting time for confirmation (in seconds):")
		choice = [str(x) for x in range(1, 31)]
		self.confirmAudioDeviceChangeTimeOutChoiceBox = group.addLabeledControl(
			labelText, wx.Choice, choices=list(reversed(choice)))
		self.confirmAudioDeviceChangeTimeOutChoiceBox.SetStringSelection(
			str(_addonConfigManager.getConfirmAudioDeviceChangeTimeOut())	)
		self.bindHelpEvent(getHelpObj("hdr33"), self.confirmAudioDeviceChangeTimeOutChoiceBox)

	def saveSettingChanges(self):
		from ..settings import (
			getInstallFeatureOption,
			toggleNoDescriptionReportInRibbonOption,
			toggleAutomaticWindowMaximizationOption,
			toggleReportTimeWithSecondsOption,
			toggleSetOnMainAndNVDAVolumeAdvancedOption,
			toggleReportVolumeChangeAdvancedOption,
			toggleIncreaseSpeakersVolumeIfNecessaryAdvancedOption,
			toggleConfirmAudioDeviceChangeAdvancedOption,
			toggleReversedPathWithLevelAdvancedOption
		)
		self.restartNVDA = False
		if self.noDescriptionReportInRibbonOptionBox.IsChecked() != toggleNoDescriptionReportInRibbonOption(False):
			toggleNoDescriptionReportInRibbonOption()
			self.restartNVDA = True
		if self.AutomaticWindowMaximizationOptionBox.IsChecked() != toggleAutomaticWindowMaximizationOption(False):
			toggleAutomaticWindowMaximizationOption()
		from .addonConfig import FCT_DateAndTime, C_DoNotInstall
		if getInstallFeatureOption(FCT_DateAndTime) != C_DoNotInstall:
			if self.reportTimeWithSecondsOptionBox.IsChecked() != toggleReportTimeWithSecondsOption(False):
				toggleReportTimeWithSecondsOption()
		option = toggleSetOnMainAndNVDAVolumeAdvancedOption(False)
		if self.setOnMainAndNVDAVolumeOptionCheckBox.IsChecked() != option:
			toggleSetOnMainAndNVDAVolumeAdvancedOption()
		itemsNumber = self.reducedPathItemsNumberBox .GetStringSelection()
		_addonConfigManager.setReducedPathItemsNumber(int(itemsNumber))
		option = toggleReversedPathWithLevelAdvancedOption(False)
		if self.reversedPathWithLevelOptionBox.IsChecked() != option:
			toggleReversedPathWithLevelAdvancedOption()
		levelString = self.minMasterVolumeLevelBox.GetStringSelection()
		_addonConfigManager.setMinMasterVolumeLevel(int(levelString))
		levelString = self.masterVolumeLevelBox.GetStringSelection()
		_addonConfigManager.setMasterVolumeLevel(int(levelString))
		levelString = self.minNVDAVolumeLevelBox .GetStringSelection()[:-1]
		_addonConfigManager.setMinNVDAVolumeLevel(int(levelString))
		levelString = self.NVDAVolumeLevelBox.GetStringSelection()[:-1]
		_addonConfigManager.setNVDAVolumeLevel(int(levelString))
		levelString = self.volumeChangeStepLevelBox.GetStringSelection()
		_addonConfigManager.setVolumeChangeStepLevel(int(levelString))
		if self.reportVolumeChangeOptionCheckBox.IsChecked() != toggleReportVolumeChangeAdvancedOption(False):
			toggleReportVolumeChangeAdvancedOption()
		option = toggleIncreaseSpeakersVolumeIfNecessaryAdvancedOption(False)
		if self.increaseSpeakersVolumeIfNecessaryOptionCheckBox.IsChecked() != option:
			toggleIncreaseSpeakersVolumeIfNecessaryAdvancedOption()
		option = toggleConfirmAudioDeviceChangeAdvancedOption(False)
		if self.confirmAudioDeviceChangeCheckBox.IsChecked() != option:
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
		from ..settings import (
			toggleDialogTitleWithAddonSummaryAdvancedOption,
			toggleByPassNoDescriptionAdvancedOption,
			toggleLimitKeyRepeatsAdvancedOption, toggleRecordCurrentSettingsForCurrentSelectorAdvancedOption,
			toggleTypedWordSpeakingEnhancementAdvancedOption, toggleAllowNVDATonesVolumeAdjustmentAdvancedOption,
			toggleAllowNVDASoundGainModificationAdvancedOption, togglePlayToneOnAudioDeviceAdvancedOption
		)
		sHelper = BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a choice box in the advanced settings panel.
		labelText = _("&Play sound on logged errors:")
		self.playSoundOnErrorsOptionChoiceBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=self._playSoundOnErrorsOptionLabels)
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
		self.MaximumDelayBetweenSameScriptBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=[str(x) for x in choice])
		self.MaximumDelayBetweenSameScriptBox.SetSelection(
			choice.index(_addonConfigManager.getMaximumDelayBetweenSameScript()))
		self.bindHelpEvent(getHelpObj("hdr303"), self.MaximumDelayBetweenSameScriptBox)
		# Translators: This is the label for a checkbox in the Advanced settings panel.
		labelText = _(
			"""&Do not take account of the option called "Report object descriptions" """
			"""during the display of the dialog box same as confirmation""")
		self.byPassNoDescriptionOptionBox = sHelper.addItem(wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.byPassNoDescriptionOptionBox.SetValue(toggleByPassNoDescriptionAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr204"), self.byPassNoDescriptionOptionBox)
		if inSecureMode():
			self.MaximumDelayBetweenSameScriptBox .Hide()
			self.byPassNoDescriptionOptionBox.Hide()
		# Translators: This is the label for a checkbox in the Advanced settings panel.
		labelText = _("&Enhance speak typed words")
		self.typedWordSpeakingEnhancementOptionBox = sHelper.addItem(wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.typedWordSpeakingEnhancementOptionBox .SetValue(
			toggleTypedWordSpeakingEnhancementAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr209"), self.typedWordSpeakingEnhancementOptionBox)
		# Translators: This is the label for a group of editing options in the computer settings panel.
		groupText = _("Key Repeat")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the Advanced settings panel.
		labelText = _("&Limit key repeats")
		self.limitKeyRepeatsOptionBox = group.addItem(wx.CheckBox(groupBox, wx.ID_ANY, label=labelText))
		self.limitKeyRepeatsOptionBox.SetValue(toggleLimitKeyRepeatsAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr307"), self.limitKeyRepeatsOptionBox)
		# Translators: This is the label for a choice box in the advanced settings panel.
		labelText = _("Delay between &repeat (in ms):")
		choices = [x for x in range(10, 510, 10)]
		choices = list(reversed(choices))
		self.keyRepeatDelayOptionChoiceBox = group.addLabeledControl(
			labelText, wx.Choice, choices=[str(x) for x in choices])
		self.keyRepeatDelayOptionChoiceBox.SetSelection(choices.index(_addonConfigManager.getKeyRepeatDelay()))
		self.bindHelpEvent(getHelpObj("hdr307"), self.keyRepeatDelayOptionChoiceBox)
		# Translators: This is the label for a group of editing options in the computer settings panel.
		groupText = _("Voice profile switching")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the Advanced settings panel.
		labelText = _("&Automatically save current voice settings for current selector before switching")
		self.recordCurrentSettingsForCurrentSelectorOptionBox = group.addItem(
			wx.CheckBox(groupBox, wx.ID_ANY, label=labelText))
		self.recordCurrentSettingsForCurrentSelectorOptionBox.SetValue(
			toggleRecordCurrentSettingsForCurrentSelectorAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr17-7"), self.recordCurrentSettingsForCurrentSelectorOptionBox)
		# Translators: This is the label for a group of editing options in the computer settings panel.
		groupText = _("Audio sources's manager")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the Advanced settings panel.
		labelText = _("Allow &NVDA tonalities's volume adjustment")
		self.allowNVDASoundsVolumeAdjustmentOptionBox = group.addItem(
			wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.allowNVDASoundsVolumeAdjustmentOptionBox.SetValue(
			toggleAllowNVDATonesVolumeAdjustmentAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr34-1"), self.allowNVDASoundsVolumeAdjustmentOptionBox)
		# Translators: This is the label for a checkbox in the Advanced settings panel.
		labelText = _("allow nvda sounds files's &gain modification")
		self.allowNVDASoundGainModificationBox = group.addItem(
			wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.allowNVDASoundGainModificationBox.SetValue(
			toggleAllowNVDASoundGainModificationAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr34-2"), self.allowNVDASoundGainModificationBox)
		from ..computerTools.audioCore import isWasapiUsed
		if isWasapiUsed():
			self.allowNVDASoundsVolumeAdjustmentOptionBox.Disable()
		# Translators: This is the label for a checkbox in the Advanced settings panel.
		labelText = _("Play tone on audio &output device")
		self.playToneOnAudioDeviceBox = group.addItem(
			wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.playToneOnAudioDeviceBox.SetValue(
			togglePlayToneOnAudioDeviceAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr34?1"), self.playToneOnAudioDeviceBox)

	def saveSettingChanges(self):
		from ..settings import (
			toggleDialogTitleWithAddonSummaryAdvancedOption,
			toggleByPassNoDescriptionAdvancedOption,
			toggleLimitKeyRepeatsAdvancedOption, toggleRecordCurrentSettingsForCurrentSelectorAdvancedOption,
			toggleTypedWordSpeakingEnhancementAdvancedOption, toggleAllowNVDATonesVolumeAdjustmentAdvancedOption,
			toggleAllowNVDASoundGainModificationAdvancedOption,
			togglePlayToneOnAudioDeviceAdvancedOption,
		)
		self.restartNVDA = False
		playSoundOnErrorsOption = self.playSoundOnErrorsOptionChoiceBox.GetSelection()
		_addonConfigManager.setPlaySoundOnErrorsOption(playSoundOnErrorsOption)
		option = toggleDialogTitleWithAddonSummaryAdvancedOption(False)
		if self.dialogTitleWithAddonSummaryOptionBox.IsChecked() != option:
			toggleDialogTitleWithAddonSummaryAdvancedOption()
		maximumDelayBetweenSameScript = int(
			self.MaximumDelayBetweenSameScriptBox.GetString(self.MaximumDelayBetweenSameScriptBox.GetSelection()))
		if maximumDelayBetweenSameScript != _addonConfigManager.getMaximumDelayBetweenSameScript():
			_addonConfigManager.setMaximumDelayBetweenSameScript(maximumDelayBetweenSameScript)
			self.restartNVDA = True
		if self.byPassNoDescriptionOptionBox.IsChecked() != toggleByPassNoDescriptionAdvancedOption(False):
			toggleByPassNoDescriptionAdvancedOption()
			self.restartNVDA = True
		option = toggleLimitKeyRepeatsAdvancedOption(False)
		if self.limitKeyRepeatsOptionBox.IsChecked() != option:
			toggleLimitKeyRepeatsAdvancedOption()
		keyRepeatDelay = int(
			self.keyRepeatDelayOptionChoiceBox.GetString(self.keyRepeatDelayOptionChoiceBox.GetSelection()))
		if keyRepeatDelay != _addonConfigManager.getKeyRepeatDelay():
			_addonConfigManager.setKeyRepeatDelay(keyRepeatDelay)
		option = toggleRecordCurrentSettingsForCurrentSelectorAdvancedOption(False)
		if self.recordCurrentSettingsForCurrentSelectorOptionBox.IsChecked() != option:
			toggleRecordCurrentSettingsForCurrentSelectorAdvancedOption()
		option = toggleTypedWordSpeakingEnhancementAdvancedOption(False)
		if self.typedWordSpeakingEnhancementOptionBox.IsChecked() != option:
			toggleTypedWordSpeakingEnhancementAdvancedOption()
		option = toggleAllowNVDATonesVolumeAdjustmentAdvancedOption(False)
		if self.allowNVDASoundsVolumeAdjustmentOptionBox.IsChecked() != option:
			toggleAllowNVDATonesVolumeAdjustmentAdvancedOption()
			self.restartNVDA = True
		option = toggleAllowNVDASoundGainModificationAdvancedOption(False)
		if self.allowNVDASoundGainModificationBox.IsChecked() != option:
			toggleAllowNVDASoundGainModificationAdvancedOption()
			self.restartNVDA = True
		option = togglePlayToneOnAudioDeviceAdvancedOption(False)
		if self.playToneOnAudioDeviceBox.IsChecked() != option:
			togglePlayToneOnAudioDeviceAdvancedOption()

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
		from ..settings import (
			getInstallFeatureOption,
			toggleOnlyNVDAKeyInRemanenceAdvancedOption,
			toggleRemanenceAtNVDAStartAdvancedOption,
			toggleBeepAtRemanenceStartAdvancedOption,
			toggleBeepAtRemanenceEndAdvancedOption,
			toggleRemanenceForGmailAdvancedOption,
			toggleEnableNumpadNavigationModeToggleAdvancedOption,
			toggleActivateNumpadStandardUseWithNumLockAdvancedOption,
			toggleActivateNumpadNavigationModeAtStartAdvancedOption,
			toggleReportNumlockStateAtStartAdvancedOption,
			toggleReportCapslockStateAtStartAdvancedOption,
		)
		sHelper = BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a group of editing options in the Keyboard settings panel.
		groupText = _("Keys's remanence")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
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
		self.remanenceDelayBox = group.addLabeledControl(
			labelText, wx.Choice, choices=[str(x) for x in self.remanenceDelayChoice])
		self.remanenceDelayBox.SetSelection(
			self.remanenceDelayChoice.index(_addonConfigManager.getRemanenceDelay()))
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
		from .addonConfig import FCT_KeyRemanence
		if not getInstallFeatureOption(FCT_KeyRemanence):
			for item in range(0, group.sizer.GetItemCount()):
				group.sizer.Hide(item)
		# Translators: This is the label for a group of editing options in the Keyboard settings panel.
		groupText = _("Numeric keypad")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the keyboard settings panel.
		labelText = _("&Allow the standard use of the numeric keypad")
		self.enableNumpadNavigationModeToggleOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.enableNumpadNavigationModeToggleOptionBox.SetValue(
			toggleEnableNumpadNavigationModeToggleAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr304"), self.enableNumpadNavigationModeToggleOptionBox)
		# Translators: This is the label for a checkbox in the keyboard settings panel.
		labelText = _("&Enable the standard use of the numeric keypad at NVDA's start")
		self.activateNumpadNavigationModeAtStartOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.activateNumpadNavigationModeAtStartOptionBox.SetValue(
			toggleActivateNumpadNavigationModeAtStartAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr304"), self.activateNumpadNavigationModeAtStartOptionBox)
		# Translators: This is the label for a checkbox in the keyboard settings panel.
		labelText = _("&Enable / disable numeric keypad's standard use with num lock key")
		self.activateNumpadStandardUseWithNumLockOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.activateNumpadStandardUseWithNumLockOptionBox.SetValue(
			toggleActivateNumpadStandardUseWithNumLockAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr304"), self.activateNumpadStandardUseWithNumLockOptionBox)
		# Translators: This is the label for a group of editing options in the Keyboard settings panel.
		groupText = _("Numeric lock")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the keyboard settings panel.
		labelText = _("&Report ?he activated state at NVDA starting")
		self.reportNumlockStateAtStartOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.reportNumlockStateAtStartOptionBox .SetValue(
			toggleReportNumlockStateAtStartAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr305"), self.reportNumlockStateAtStartOptionBox)
		# Translators: This is the label for a group of editing options in the Keyboard settings panel.
		groupText = _("Capital lock")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the keyboard settings panel.
		labelText = _("&Report the activated state at NVDA starting")
		self.reportCapslockStateAtStartOptionBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.reportCapslockStateAtStartOptionBox .SetValue(
			toggleReportCapslockStateAtStartAdvancedOption(False))
		self.bindHelpEvent(getHelpObj("hdr306"), self.reportCapslockStateAtStartOptionBox)

	def saveSettingChanges(self):
		from ..settings import (
			getInstallFeatureOption,
			toggleOnlyNVDAKeyInRemanenceAdvancedOption,
			toggleRemanenceAtNVDAStartAdvancedOption,
			toggleBeepAtRemanenceStartAdvancedOption,
			toggleBeepAtRemanenceEndAdvancedOption,
			toggleRemanenceForGmailAdvancedOption,
			toggleEnableNumpadNavigationModeToggleAdvancedOption,
			toggleActivateNumpadStandardUseWithNumLockAdvancedOption,
			toggleActivateNumpadNavigationModeAtStartAdvancedOption,
			toggleReportNumlockStateAtStartAdvancedOption,
			toggleReportCapslockStateAtStartAdvancedOption,
		)
		self.restartNVDA = False
		from .addonConfig import FCT_KeyRemanence
		if getInstallFeatureOption(FCT_KeyRemanence):
			option = toggleOnlyNVDAKeyInRemanenceAdvancedOption(False)
			if self.onlyNVDAKeyInRemanenceAdvancedOptionBox.IsChecked() != option:
				toggleOnlyNVDAKeyInRemanenceAdvancedOption()
			option = toggleRemanenceAtNVDAStartAdvancedOption(False)
			if self.remanenceAtNVDAStartAdvancedOptionBox.IsChecked() != option:
				toggleRemanenceAtNVDAStartAdvancedOption()
			remanenceDelay = self.remanenceDelayBox.GetSelection()
			_addonConfigManager.setRemanenceDelay(self.remanenceDelayChoice[remanenceDelay])
			option = toggleBeepAtRemanenceStartAdvancedOption(False)
			if self.beepAtRemanenceStartOptionCheckBox.IsChecked() != option:
				toggleBeepAtRemanenceStartAdvancedOption()
			option = toggleBeepAtRemanenceEndAdvancedOption(False)
			if self.beepAtRemanenceEndOptionCheckBox.IsChecked() != option:
				toggleBeepAtRemanenceEndAdvancedOption()
			option = toggleRemanenceForGmailAdvancedOption(False)
			if self.remanenceForGmailOptionCheckBox.IsChecked() != option:
				toggleRemanenceForGmailAdvancedOption()
		option = toggleEnableNumpadNavigationModeToggleAdvancedOption(False)
		if self.enableNumpadNavigationModeToggleOptionBox.IsChecked() != option:
			toggleEnableNumpadNavigationModeToggleAdvancedOption()
			# in all cases, disable numpad navigation mode
			from ..commandKeysSelectiveAnnouncementAndRemanence import _myInputManager
			if _myInputManager is not None:
				_myInputManager .setNumpadNavigationMode(False)
		option = toggleActivateNumpadNavigationModeAtStartAdvancedOption(False)
		if self.activateNumpadNavigationModeAtStartOptionBox.IsChecked() != option:
			toggleActivateNumpadNavigationModeAtStartAdvancedOption()
		option = toggleActivateNumpadStandardUseWithNumLockAdvancedOption(False)
		if self.activateNumpadStandardUseWithNumLockOptionBox.IsChecked() != option:
			toggleActivateNumpadStandardUseWithNumLockAdvancedOption()
		option = toggleReportNumlockStateAtStartAdvancedOption(False)
		if self.reportNumlockStateAtStartOptionBox.IsChecked() != option:
			toggleReportNumlockStateAtStartAdvancedOption()
		option = toggleReportCapslockStateAtStartAdvancedOption(False)
		if self.reportCapslockStateAtStartOptionBox.IsChecked() != option:
			toggleReportCapslockStateAtStartAdvancedOption()

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
		from ..settings import (
			toggleUpdateReleaseVersionsToDevVersionsGeneralOptions,
			toggleAutoUpdateGeneralOptions
		)
		sHelper = BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a checkbox in the Update settings panel.
		labelText = _("Automatically check for &updates")
		self.autoCheckForUpdatesCheckBox = sHelper.addItem(wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.autoCheckForUpdatesCheckBox.SetValue(toggleAutoUpdateGeneralOptions(False))
		self.bindHelpEvent(getHelpObj("hdr-update"), self.autoCheckForUpdatesCheckBox)
		# Translators: This is the label for a checkbox in the Update settings panel.
		labelText = _("Update also release versions to &development versions")
		self.updateReleaseVersionsToDevVersionsCheckBox = sHelper.addItem(
			wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.updateReleaseVersionsToDevVersionsCheckBox.SetValue(
			toggleUpdateReleaseVersionsToDevVersionsGeneralOptions(False))
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
		lang = getLanguage()
		theFile = os.path.join(addon.path, "doc", lang, "changes.html")
		if not os.path.exists(theFile):
			lang = lang.split("_")[0]
			theFile = os.path.join(addon.path, "doc", lang, "changes.html")
			if not os.path.exists(theFile):
				lang = "en"
				theFile = os.path.join(addon.path, "doc", lang, "changes.html")
		os.startfile(theFile)

	def saveSettingChanges(self):
		from ..settings import (
			toggleUpdateReleaseVersionsToDevVersionsGeneralOptions,
			toggleAutoUpdateGeneralOptions
		)
		self.restartNVDA = False
		if self.autoCheckForUpdatesCheckBox.IsChecked() != toggleAutoUpdateGeneralOptions(False):
			toggleAutoUpdateGeneralOptions()
		option = toggleUpdateReleaseVersionsToDevVersionsGeneralOptions(False)
		if self.updateReleaseVersionsToDevVersionsCheckBox.IsChecked() != option:
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
	# if in secur mode, some panels must be disabled
	inSecureModeCategoryClasses = [
		NVDAEnhancementSettingsPanel,
		ComputerSettingsPanel,
		KeyboardSettingsPanel,
		AdvancedSettingsPanel,
	]

	def __init__(self, parent, initialCategory=None):
		curAddon = addonHandler.getCodeAddon()
		# Translators: title of add-on settings dialog.
		dialogTitle = _("Settings")
		self.title = "%s - %s" % (curAddon.manifest["summary"], dialogTitle)
		if inSecureMode():
			self.categoryClasses = self.inSecureModeCategoryClasses[:]
		else:
			self.categoryClasses = self.baseCategoryClasses[:]
		super(GlobalSettingsDialog, self).__init__(parent, initialCategory)
		from speech.speech import speakMessage
		wx.CallLater(1000, speakMessage, _helpMsg)


class NVDAEnhancementProfileSettingsPanel(SettingsPanel):
	# Translators: This is the label for the settings dialog.
	title = _("NVDA enhancements")

	def __init__(self, parent):
		self.title = makeAddonWindowTitle(self.title)
		super(NVDAEnhancementProfileSettingsPanel, self).__init__(parent)

	def makeSettings(self, settingsSizer):
		sHelper = BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a group of cursor's movement options in the
		# NVDAEnhancement profile settings panel
		groupText = _("Cursor's moving")
		groupSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=groupText)
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a combobox in the NVDAEnhancement settings panel.
		labelText = _("&Punctuation/symbol level on word movement:")
		symbolLevelLabels = characterProcessing.SPEECH_SYMBOL_LEVEL_LABELS
		symbolLevelChoices = [
			symbolLevelLabels[level] for level in characterProcessing.CONFIGURABLE_SPEECH_SYMBOL_LEVELS]
		# Translators: This is the label for an item in combobox in the
		# NVDAEnhancement settings panel.
		symbolLevelChoices = [_("Current configuration profile's level"), ] + symbolLevelChoices[:]
		self.symbolLevelList = group.addLabeledControl(labelText, wx.Choice, choices=symbolLevelChoices)
		from .nvdaConfig import _NVDAConfigManager
		symbolLevelOnWordCaretMovement = _NVDAConfigManager .getSymbolLevelOnWordCaretMovement()
		if symbolLevelOnWordCaretMovement is None:
			self.symbolLevelList.SetSelection(0)
		else:
			self.symbolLevelList.SetSelection(
				1 + characterProcessing.CONFIGURABLE_SPEECH_SYMBOL_LEVELS.index((symbolLevelOnWordCaretMovement)))

	def saveSettingChanges(self):
		from .nvdaConfig import _NVDAConfigManager
		self.restartNVDA = False
		if self.symbolLevelList.GetSelection() == 0:
			_NVDAConfigManager .saveSymbolLevelOnWordCaretMovement(None)
		else:
			index = self.symbolLevelList.GetSelection()
			level = characterProcessing.CONFIGURABLE_SPEECH_SYMBOL_LEVELS[index - 1]

			if version_year >= 2022 or (version_year == 2021 and version_major >= 2):
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
		sHelper = BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a group of editing options in the Keyboard profile settings panel.
		groupText = _("Clipboard")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
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
		# Translators: This is the label for a checkBox in the Keyboard profile settings panel.
		labelText = _("Ask &confirmation before adding")
		self.confirmToAddToClipCheckBox = group.addItem(wx.CheckBox(self, label=labelText))
		self.confirmToAddToClipCheckBox .SetValue(_NVDAConfigManager.toggleAddTextBeforeOption(False))
		self.bindHelpEvent(getHelpObj("hdr7-1"), self.confirmToAddToClipCheckBox)
		labelText = _("&Remanence's delay (in milliseconds):")
		# Translators: This is the label for a group of editing options in the Keyboard profile settings panel.
		groupText = _("Numeric lock")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a combobox in the Keyboard profile settings panel.
		labelText = _("&On profile activation:")
		# numlock activation choices for
		# must be  in the same order that the ANL constants
		activateNumlockChoices = (
			# Translators: label Choice in Activate NumLock combo box
			# ANL_NoChange constant
			_("Do nothing"),
			# Translators: Choice in Activate NumLock combo box
			# ANL_Off constant
			_("Desactivate"),
			# Translators: Choice in Activate NumLock combo box
			# ANL_On
			_("Activate"),
		)
		self.activateNumlockBox = group.addLabeledControl(
			labelText, wx.Choice, choices=activateNumlockChoices)
		self.activateNumlockBox .SetStringSelection(
			activateNumlockChoices[_NVDAConfigManager.getActivateNumlockOption()])
		self.bindHelpEvent(getHelpObj("hdr305"), self.activateNumlockBox)
		# Translators: This is the label for a group of editing options in the Keyboard profile settings panel.
		groupText = _("Key blocking")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkBox in the Keyboard profile settings panel.
		labelText = _("Block insert key")
		self.blockInsertKeyCheckBox = group.addItem(wx.CheckBox(self, label=labelText))
		self.blockInsertKeyCheckBox .SetValue(_NVDAConfigManager.toggleBlockInsertKeyOption(False))
		self.bindHelpEvent(getHelpObj("hdr105"), self.blockInsertKeyCheckBox)
		# Translators: This is the label for a checkBox in the Keyboard profile settings panel.
		labelText = _("Block capslock key")
		self.blockCapslockKeyCheckBox = group.addItem(wx.CheckBox(self, label=labelText))
		self.blockCapslockKeyCheckBox .SetValue(_NVDAConfigManager.toggleBlockCapslockKeyOption(False))
		self.bindHelpEvent(getHelpObj("hdr105"), self.blockCapslockKeyCheckBox)
		from ..settings import getInstallFeatureOption
		from .addonConfig import FCT_KeyRemanence, FCT_CommandKeysSelectiveAnnouncement
		if not getInstallFeatureOption(
			FCT_KeyRemanence) and not getInstallFeatureOption(FCT_CommandKeysSelectiveAnnouncement):
			for item in range(0, group.sizer.GetItemCount()):
				group.sizer.Hide(item)
		# Translators: This is the label for a group of editing options in the Keyboard profile settings panel.
		groupText = _("Characters echo")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkBox in the Keyboard profile settings panel.
		labelText = _("Still speak &non-alphanumeric characters when keyboard echo by characters is disabled")
		self.alphaNumCharsCheckBox = group.addItem(wx.CheckBox(self, label=labelText))
		self.alphaNumCharsCheckBox .SetValue(_NVDAConfigManager.toggleSpeakAlphaNumCharsOption(False))
		self.bindHelpEvent(getHelpObj("hdr106"), self.alphaNumCharsCheckBox)

	def saveSettingChanges(self):
		from .nvdaConfig import _NVDAConfigManager
		self.restartNVDA = False
		_NVDAConfigManager.setAddToClipSeparator(self.setSeparatorEdit .GetValue())
		if self.addTextBeforeCheckBox.IsChecked() != _NVDAConfigManager.toggleAddTextBeforeOption(False):
			_NVDAConfigManager.toggleAddTextBeforeOption(True)
		if self.confirmToAddToClipCheckBox.IsChecked() != _NVDAConfigManager.toggleConfirmToAddToClipOption(False):
			_NVDAConfigManager.toggleConfirmToAddToClipOption(True)
		option = self.activateNumlockBox .GetSelection()
		_NVDAConfigManager.setActivateNumlockOption(option)
		if self.blockInsertKeyCheckBox .IsChecked() != _NVDAConfigManager.toggleBlockInsertKeyOption(False):
			_NVDAConfigManager.toggleBlockInsertKeyOption(True)
		if self.blockCapslockKeyCheckBox .IsChecked() != _NVDAConfigManager.toggleBlockCapslockKeyOption(False):
			_NVDAConfigManager.toggleBlockCapslockKeyOption(True)
		if self.alphaNumCharsCheckBox .IsChecked() != _NVDAConfigManager.toggleSpeakAlphaNumCharsOption(False):
			_NVDAConfigManager.toggleSpeakAlphaNumCharsOption(True)

	def onSave(self):
		self.saveSettingChanges()
		from ..utils import numlock
		wx.CallLater(400, numlock.manageNumlockActivation)


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
		soundsDir = os.path.join(path, "sounds", "textAnalyzerAlerts")
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
		sHelper = BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a checkbox in the TextAnalyzer settings panel.
		labelText = _("&Activate text analyzer")
		self.textAnalyzerActivationCheckBox = sHelper.addItem(wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.textAnalyzerActivationCheckBox.SetValue(_NVDAConfigManager.toggleTextAnalyzerActivationOption(False))
		self.bindHelpEvent(getHelpObj("hdr31-1"), self.textAnalyzerActivationCheckBox)
		# Translators: This is the label for a checkbox in the TextAnalyzer settings panel.
		labelText = _("Activate text analyzer at add-on's &start")
		self.textAnalyzerActivationAtStartCheckBox = sHelper.addItem(wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.textAnalyzerActivationAtStartCheckBox.SetValue(
			_NVDAConfigManager.toggleTextAnalyzerActivationAtStartOption(False))
		self.bindHelpEvent(getHelpObj("hdr31-1"), self.textAnalyzerActivationAtStartCheckBox)
		# Translators: This is the label for a group of editing options in the TextAnalyzer settings panel.
		groupText = _("Symbols match")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the TextAnalyzer settings panel.
		labelText = _("Report &discrepancies")
		self.reportSymbolsDiscrepanciesCheckBox = group.addItem(wx.CheckBox(groupBox, wx.ID_ANY, label=labelText))
		self.reportSymbolsDiscrepanciesCheckBox .SetValue(
			_NVDAConfigManager.toggleReportSymbolMismatchAnalysisOption(False))
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
		group = BoxSizerHelper(self, sizer=groupSizer)
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
		group = BoxSizerHelper(self, sizer=groupSizer)
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
		group = BoxSizerHelper(self, sizer=groupSizer)
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
		file = os.path.join(path, "sounds", "textAnalyzerAlerts", fileName)
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
		option = _NVDAConfigManager.toggleTextAnalyzerActivationOption(False)
		if self.textAnalyzerActivationCheckBox.IsChecked() != option:
			_NVDAConfigManager.toggleTextAnalyzerActivationOption(True)
		option = _NVDAConfigManager.toggleTextAnalyzerActivationAtStartOption(False)
		if self.textAnalyzerActivationAtStartCheckBox.IsChecked() != option:
			_NVDAConfigManager.toggleTextAnalyzerActivationAtStartOption(True)
		option = _NVDAConfigManager.toggleReportSymbolMismatchAnalysisOption(False)
		if self.reportSymbolsDiscrepanciesCheckBox .IsChecked() != option:
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
		option = _NVDAConfigManager.toggleReportFormattingChangesOption(False)
		if self.reportFormattingChangesCheckBox .IsChecked() != option:
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
	# if in secur mode, some panels must be disabled
	inSecureModeCategoryClasses = [
		NVDAEnhancementProfileSettingsPanel,
	]

	def __init__(self, parent, initialCategory=None):
		curAddon = addonHandler.getCodeAddon()
		currentProfile = config.conf.profiles[-1].name
		if currentProfile is None:
			currentProfile = NVDAString("normal configuration")
		# Translators: title of add-on settings dialog.
		dialogTitle = _("Profile settings's %s") % currentProfile
		self.title = "%s - %s" % (curAddon.manifest["summary"], dialogTitle)
		if inSecureMode():
			self.categoryClasses = self.inSecureModeCategoryClasses[:]
		else:
			self.categoryClasses = self.baseCategoryClasses[:]
		super(ProfileSettingsDialog, self).__init__(parent, initialCategory)
		from speech.speech import speakMessage
		wx.CallLater(1000, speakMessage, _helpMsg)
