# globalPlugins\NVDAExtensionGlobalPlugin\volumeControl\audioManagerDialog.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2021-2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


import addonHandler
# from logHandler import log
import ui
import braille
import speech
import queueHandler
import api
import wx
from gui.guiHelper import BoxSizerHelper
from gui import guiHelper, mainFrame
from ..utils import isOpened, makeAddonWindowTitle, getHelpObj
from ..utils import contextHelpEx




from .volumeControl import (
	getChannels, getAppVolumeObj, getNVDAVolumeObj,
	getNVDAChannelsVolume, getAbsoluteLevel,
	splitChannels, toggleChannels,
	validateVolumeLevel, setAppVolume,
	updateNVDAAndApplicationsChannelsLevels, changeSpeakersVolume,
	getApplicationVolumeInfo, isInitialized,
	nvdaAppName, isNVDA
)

addonHandler.initTranslation()


class NVDAAndAudioApplicationsManagerDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	_instance = None
	# help in the user manual.
	helpObj = getHelpObj("hdr34")
	selectDelay = None

	def __new__(cls, *args, **kwargs):
		if NVDAAndAudioApplicationsManagerDialog._instance is None:
			return wx.Dialog.__new__(cls)
		return NVDAAndAudioApplicationsManagerDialog._instance

	def __init__(self, parent):
		if NVDAAndAudioApplicationsManagerDialog._instance is not None:
			return
		NVDAAndAudioApplicationsManagerDialog._instance = self
		focus = api.getFocusObject()
		from appModuleHandler import getAppNameFromProcessID
		self.focusedAppName = getAppNameFromProcessID(focus.processID, True).split(".")[0]
		# Translators: this is the title of NVDA and Applications audio Channels manager dialog
		dialogTitle = _("NVDA and running Applications audio manager")
		title = NVDAAndAudioApplicationsManagerDialog.title = makeAddonWindowTitle(dialogTitle)
		super(NVDAAndAudioApplicationsManagerDialog, self).__init__(parent, wx.ID_ANY, title)
		self.doGui()
		self.backToForeground = False

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label for a listbox
		# in NVDA and audio Applications manager dialog
		labelText = _("Applications:")
		self.initApplicationsList()
		choices = [app.split(".")[0] for app in self.applications]
		self.applicationsListBox = sHelper.addLabeledControl(
			labelText,
			wx.ListBox,
			choices=choices
		)
		if self.focusedAppName in choices:
			self.applicationsListBox.SetStringSelection(self.focusedAppName)
		else:
			self.applicationsListBox.SetSelection(0)
		# Translators: This is the label for a group
		# in NVDA and audio Applications manager dialog
		groupText = _("Volume")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is a label for a choice box
		# in NVDA and audio Applications manager dialog.
		labelText = _("&Volume:")
		levels = [str(x) for x in reversed(range(0, 101))]
		self.volumeBox = group.addLabeledControl(
			labelText,
			wx.Choice,
			choices=levels
		)
		# Translators: This is the label for a checkbox
		# in NVDA and audio Applications manager dialog
		labelText = _("&Muted")
		self.volumeMuteCheckBox = group.addItem(wx.CheckBox(groupBox, label=labelText))
		self.volumeMuteCheckBox.SetValue(False)
		# Translators: This is the label for a group
		# in NVDA and audio Applications manager dialog
		groupText = _("Balance")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is a label for a choice box
		# in NVDA and audio Applications manager dialog.
		labelText = _("&Left:")
		levels = [str(x) for x in reversed(range(0, 101))]
		self.leftChannelBox = group.addLabeledControl(
			labelText,
			wx.Choice,
			choices=levels
		)
		self.leftChannelBox.SetSelection(0)
		# Translators: This is a label for a choice box
		# in NVDA and audio Applications manager dialog
		labelText = _("&Right:")
		self.rightChannelBox = group.addLabeledControl(
			labelText,
			wx.Choice,
			choices=levels
		)
		self.rightChannelBox.SetSelection(0)
		# the buttons
		bHelper = sHelper.addDialogDismissButtons(
			guiHelper.ButtonHelper(wx.HORIZONTAL))
		closeButton = bHelper.addButton(self, wx.ID_CLOSE)
		closeButton.SetDefault()
		mainSizer.Add(sHelper.sizer, border=10, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# the events
		self.Bind(wx.EVT_ACTIVATE, self.onActivate)
		self.applicationsListBox.Bind(wx.EVT_LISTBOX, self.onSelectApplication)
		self.applicationsListBox.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
		self.volumeBox.Bind(wx.EVT_CHOICE, self.onVolumeChoice)
		self.volumeMuteCheckBox.Bind(wx.EVT_CHECKBOX, self.onVolumeMute)
		self.leftChannelBox.Bind(wx.EVT_CHOICE, self.onLeftChannelChoice)
		self.rightChannelBox.Bind(wx.EVT_CHOICE, self.onRightChannelChoice)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)
		self.applicationsListBox.SetFocus()
		self.updateChannels(self.applications[0])
		self.updateVolume(self.applications[0])
		self.applicationsListBox.Bind(wx.EVT_SET_FOCUS, self.onFocusApplicationsList)
		info = self.formatApplicationInfo(self.applications[0], name=False, mute=True)
		wx.CallLater(100, ui.message, info)
		info = self.formatApplicationInfo(self.applications[0], name=True, mute=True)
		wx.CallLater(
			40,
			braille.handler.message,
			info)

	def Destroy(self):
		self.Unbind(wx.EVT_ACTIVATE)
		NVDAAndAudioApplicationsManagerDialog._instance = None
		super(NVDAAndAudioApplicationsManagerDialog, self).Destroy()

	def onActivate(self, evt):
		isActive = evt.GetActive()
		self.isActive = isActive
		if isActive:
			if not hasattr(self, "delay"):
				self.backToForeground = True
			else:
				self.backToForeground = False
		else:
			del self.backToForeground
		evt.Skip()

	def initApplicationsList(self):
		self.applicationsChannelsVolumes = getChannels()
		self.applicationsChannelsVolumes[nvdaAppName] = getNVDAChannelsVolume()
		self.applications = sorted(list(self.applicationsChannelsVolumes.keys()))

	def updateApplicationsList(self):
		curApplications = self.applications
		curApp = self.applicationsListBox.GetStringSelection()
		self.initApplicationsList()
		if curApplications == self.applications:
			return
		choices = [app.split(".")[0] for app in self.applications]
		self.applicationsListBox.Clear()
		self.applicationsListBox.Append(choices)
		if curApp in choices:
			self.applicationsListBox.SetStringSelection(curApp)
		else:
			self.applicationsListBox.SetSelection(0)

	def focusApplicationsList(self, speakEnd=False):
		if not self.isActive or not self.applicationsListBox.HasFocus():
			return
		self.updateApplicationsList()
		index = self.applicationsListBox.GetSelection()
		application = self.applications[index]
		if speakEnd:
			info = self.formatApplicationInfo(application, name=True, mute=True)
			wx.CallLater(40, ui.message, info)
			wx.CallLater(
				20, queueHandler.queueFunction,
				queueHandler.eventQueue,
				ui.message, _("refresh terminated"))
			return
		self.reportState(application)

	def onFocusApplicationsList(self, evt):
		if hasattr(self, "backToForeground") and self.backToForeground:
			delay = 5000
			wx.CallLater(50, ui.message, _("Please wait, refreshing list"))
			speakEnd = True
			self.backToForeground = False
		else:
			delay = 50
			speakEnd = False
		wx.CallLater(delay, self.focusApplicationsList, speakEnd)

	def onRefreshButton(self, evt):
		if self.applicationsListBox.HasFocus():
			self.focusApplicationsList()
			return
		self.applicationsListBox.SetFocus()

	def updateVolume(self, application):
		volumeObj = getAppVolumeObj(application)
		if volumeObj is None:
			# for some unknown reason , nvda volume object cannot be found.
			# so, volume change  is  not available.
			self.volumeBox.Disable()
			return
		self.volumeBox.Enable()
		mute = volumeObj.GetMute()
		self.volumeMuteCheckBox.SetValue(mute)
		volume = volumeObj.GetMasterVolume()
		level = getAbsoluteLevel(volume)
		self.volumeBox.SetStringSelection(str(level))

	def updateChannels(self, application):
		if isNVDA(application) and not isInitialized():
			# nvda channels  ae manager by other add-on
			# so disable channels box
			self.leftChannelBox.Disable()
			self.rightChannelBox.Disable()
			return
		self.applicationsChannelsVolumes = getChannels()
		self.applicationsChannelsVolumes[nvdaAppName] = getNVDAChannelsVolume()
		channelsVolume = self.applicationsChannelsVolumes[application]
		leftVolume = int(channelsVolume[0] * 100)
		rightVolume = int(channelsVolume[1] * 100)
		self.leftChannelBox.SetStringSelection(str(leftVolume))
		self.rightChannelBox.SetStringSelection(str(rightVolume))
		self.leftChannelBox.Enable()
		self.rightChannelBox.Enable()

	def formatApplicationInfo(self, application, name=False, position=True, volume=False, mute=True):
		textList = []
		if name:
			textList.append(application.split(".")[0])
		if position:
			positionMsg = getApplicationVolumeInfo(application)
			textList.append(positionMsg)
		if volume:
			from .volumeControl import volumeMsg
			vol = self.volumeBox.GetStringSelection()
			textList.append("%s %s" % (volumeMsg, vol))
		if mute:
			if self.volumeMuteCheckBox.Enabled:
				if self.volumeMuteCheckBox.GetValue():
					# Translators: volume is mute
					muteMsg = _("mute")
					textList.append(muteMsg)

		return ", ".join(textList)

	def reportState(self, application):
		info = self.formatApplicationInfo(application, mute=True)
		wx.CallLater(40, speech.speakMessage, info)
		info = self.formatApplicationInfo(application, name=True, mute=True)
		wx.CallLater(
			40,
			braille.handler.message,
			info)

	def onSelectApplication(self, evt):
		index = self.applicationsListBox.GetSelection()
		application = self.applications[index]
		self.updateChannels(application)
		self.updateVolume(application)
		if isNVDA(application):
			self.volumeMuteCheckBox.Disable()
		else:
			self.volumeMuteCheckBox.Enable()
		self.reportState(application)
		if evt:
			evt.Skip()

	def onKeyDown(self, evt):
		def _changeSpeakersVolume(offset):
			from .volumeControl import getSpeakerVolume
			level = round(100 * getSpeakerVolume()) + offset
			if level > 100:
				level = 100
			else:
				minimumLevel = _addonConfigManager .getMinMasterVolumeLevel()
				if level < minimumLevel:
					level = minimumLevel
			changeSpeakersVolume(action="set", value=level)
			self.updateVolume(application)

		def changeApplicationVolume(application, offset):
			if isNVDA(application) and getNVDAVolumeObj() is None:
				# for some unknown reason, nvda volume object cannot be retrieved.
				# so volume changes are not available
				# Translators: volume cannot be changed for NVDA
				wx.CallLater(40, ui.message, _("Volume changes are  not available for NVDA"))
				return

			level = int(self.volumeBox.GetStringSelection()) + offset
			level = max(0, level)
			level = min(100, level)
			(relativeLevel, absoluteLevel) = validateVolumeLevel(level, application)
			self.volumeBox.SetStringSelection(str(absoluteLevel))
			setAppVolume(application, relativeLevel, True, absoluteLevel)
			self.updateVolume(application)

		index = self.applicationsListBox.GetSelection()
		application = self.applications[index]
		mod = evt.GetModifiers()
		keyCode = evt.GetKeyCode()
		if mod == wx.MOD_CONTROL | wx.MOD_SHIFT:
			# for speakers volume modification
			from ..settings import _addonConfigManager
			offset = _addonConfigManager.getVolumeChangeStepLevel()
			if keyCode == wx.WXK_UP:
				wx.CallLater(40, _changeSpeakersVolume, offset)
			elif keyCode == wx.WXK_DOWN:
				wx.CallLater(40, _changeSpeakersVolume, -offset)
			elif keyCode == wx.WXK_PAGEUP:
				wx.CallLater(40, _changeSpeakersVolume, 2 * offset)
			elif keyCode == wx.WXK_PAGEDOWN:
				wx.CallLater(40, _changeSpeakersVolume, -2 * offset)
			elif keyCode == wx.WXK_HOME:
				wx.CallLater(40, changeSpeakersVolume, action="max")
			elif keyCode == wx.WXK_END:
				wx.CallLater(40, changeSpeakersVolume, action="min")
			# no more with control and shift
			return
		if mod == wx.MOD_CONTROL:
			# for application volume modification
			from ..settings import _addonConfigManager
			offset = _addonConfigManager.getVolumeChangeStepLevel()
			if keyCode == wx.WXK_UP:
				changeApplicationVolume(application, offset)
				return
			elif keyCode == wx.WXK_DOWN:
				changeApplicationVolume(application, -offset)
				return
			elif keyCode == wx.WXK_PAGEDOWN:
				offset = 2 * _addonConfigManager.getVolumeChangeStepLevel()
				changeApplicationVolume(application, -offset)
				return
			elif keyCode == wx.WXK_PAGEUP:
				offset = 2 * _addonConfigManager.getVolumeChangeStepLevel()
				changeApplicationVolume(application, offset)
				return
			elif keyCode == wx.WXK_HOME:
				changeApplicationVolume(application, offset=100)
				return
			elif keyCode == wx.WXK_END:
				changeApplicationVolume(application, offset=-100)
				return
			elif keyCode == ord("M"):
				if self.volumeMuteCheckBox.Enabled:
					mute = not self.volumeMuteCheckBox.GetValue()
					self._mute(mute)
					self.volumeMuteCheckBox.SetValue(mute)
					if mute:
						# Translators: volume is mute
						muteMsg = _("mute")
					else:
						# Translators: volume is unmute
						muteMsg = _("unmute")
					appMsg = ".".join(application.split(".")[:-1])
					wx.CallLater(40, ui.message, "%s %s" % (appMsg, muteMsg))
				return
		# for audio split
		if keyCode == wx.WXK_LEFT:
			if mod == wx.MOD_SHIFT:
				if isNVDA(application):
					toggleChannels(application=application, balance="left")
				else:
					splitChannels(application=application, NVDAChannel="left")
				self.updateChannels(application)
				return
			if mod == wx.MOD_CONTROL:
				splitChannels(application=None, NVDAChannel="left")
				self.updateChannels(application)
				return
			if mod == wx.MOD_NONE:
				toggleChannels(application=application, balance="left")
				self.updateChannels(application)
				return
		elif keyCode == wx.WXK_RIGHT:
			if mod == wx.MOD_SHIFT:
				if isNVDA(application):
					toggleChannels(application=application, balance="right")
				else:
					splitChannels(application=application, NVDAChannel="right")
				self.updateChannels(application)
				return
			if mod == wx.MOD_CONTROL:
				splitChannels(application=None, NVDAChannel="right")
				self.updateChannels(application)
				return
			if mod == wx.MOD_NONE:
				toggleChannels(application=application, balance="right")
				self.updateChannels(application)
				return
		elif keyCode == wx.WXK_SPACE:
			if mod == wx.MOD_SHIFT:
				splitChannels(application=application, NVDAChannel=None)
				self.updateChannels(application)
				return
			if mod == wx.MOD_CONTROL:
				splitChannels(application=None, NVDAChannel=None)
				self.updateChannels(application)
				return
			if mod == wx.MOD_NONE:
				toggleChannels(application=application, balance="center")
				self.updateChannels(application)
				return

		evt.Skip()

	def onVolumeChoice(self, evt):
		appIndex = self.applicationsListBox.GetSelection()
		application = self.applications[appIndex]
		level = int(self.volumeBox.GetStringSelection())
		(relativeLevel, absoluteLevel) = validateVolumeLevel(level, application)
		setAppVolume(application, relativeLevel, False)
		self.updateVolume(application)

	def channelChange(self):
		leftVolume = int(self.leftChannelBox.GetStringSelection()) / 100
		rightVolume = int(self.rightChannelBox.GetStringSelection()) / 100
		index = self.applicationsListBox.GetSelection()
		application = self.applications[index]
		if isNVDA(application) and (not leftVolume and not rightVolume):
			# Translators: message to user to inform
			# hat the NVDA channel levels cannot be set to zero simultaneously
			wx.CallLater(40, ui.message, _("The volume of NVDA channels cannot be zero both simultaneously"))
			self.updateChannels(application)
			return
		self.applicationsChannelsVolumes[application] = (leftVolume, rightVolume)
		updateNVDAAndApplicationsChannelsLevels(self.applicationsChannelsVolumes)

	def onLeftChannelChoice(self, evt):
		self.channelChange()
		evt.Skip()

	def onRightChannelChoice(self, evt):
		self.channelChange()
		evt.Skip()

	def _mute(self, mute):
		appIndex = self.applicationsListBox.GetSelection()
		application = self.applications[appIndex]
		volumeObj = getAppVolumeObj(application)
		if volumeObj is None:
			return
		volumeObj.SetMute(mute, None)

	def onVolumeMute(self, evt):
		self._mute(self.volumeMuteCheckBox.GetValue())
		evt.Skip()

	@classmethod
	def run(cls):
		from .volumeControl import isInitialized
		if not isInitialized:
			# cannot split sound
			# Translators: message to user to report incompatibility with another add-on.
			wx.CallLater(40, ui.message, _("Not available cause of conflict with another add-on. See NVDA log"))
			return
		if isOpened(cls):
			return
		mainFrame.prePopup()
		d = cls(mainFrame)
		d.CentreOnScreen()
		d.Show()
		mainFrame.postPopup()
