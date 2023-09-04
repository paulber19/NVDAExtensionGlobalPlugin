# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\audioManagerDialog.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2021-2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


import addonHandler
from logHandler import log
import os
import globalVars
import gui
import ui
import config
import time
import braille
import speech
import queueHandler
import api
import wx
from gui.guiHelper import BoxSizerHelper
from gui import guiHelper, mainFrame
from . import waves
from .audioCore import isWasapiUsed
from ..utils import isOpened, makeAddonWindowTitle, getHelpObj
from ..utils import contextHelpEx
from ..utils.NVDAStrings import NVDAString
from .audioCore import isNVDA
addonHandler.initTranslation()

from . import audioCore


class NVDAAndAudioApplicationsManagerDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	_instance = None
	# help in the user manual.
	helpObj = getHelpObj("hdr34")
	selectDelay = None
	refreshApplicationsListTimer = None

	def __new__(cls, *args, **kwargs):
		if NVDAAndAudioApplicationsManagerDialog._instance is None:
			return wx.Dialog.__new__(cls)
		return NVDAAndAudioApplicationsManagerDialog._instance

	def __init__(self, parent):
		if NVDAAndAudioApplicationsManagerDialog._instance is not None:
			return
		NVDAAndAudioApplicationsManagerDialog._instance = self

		# Translators: this is the title of NVDA and Applications audio Channels manager dialog
		dialogTitle = _("Audio sources's manager")
		title = NVDAAndAudioApplicationsManagerDialog.title = makeAddonWindowTitle(dialogTitle)
		super(NVDAAndAudioApplicationsManagerDialog, self).__init__(parent, wx.ID_ANY, title)
		from .audioCore import audioOutputDevicesManager
		self.devices = audioOutputDevicesManager.getDevices()
		self._currentDevice = audioOutputDevicesManager.getDefaultDevice()
		self.audioSources = audioCore.AudioSources(self._currentDevice)
		self.doGui()
		self.backToForeground = False

	def doGui(self):
		focus = api.getFocusObject()
		from appModuleHandler import getAppNameFromProcessID
		focusedAppName = getAppNameFromProcessID(focus.processID, True)
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = BoxSizerHelper(self, orientation=wx.VERTICAL)
		from .audioCore import audioOutputDevicesManager
		self.deviceNames = audioOutputDevicesManager.getDeviceNames()
		# Translators: This is the label for a listbox
		# in NVDA and audio Applications manager dialog
		labelText = NVDAString("Audio output  &device:")
		# Translators: label to indicate that the device is the default system peripheral
		defaultDeviceText = _("Default Output")
		choices = []
		for device in self.devices:
			name = device.name
			if device._default:
				name = "%s (%s)" % (name, defaultDeviceText)
			choices.append(name)
		self.devicesListBox = sHelper.addLabeledControl(
			labelText,
			wx.ListBox,
			choices=choices
		)
		self.devicesListBox .SetSelection(self.devices.index(self._currentDevice))
		# Translators: This is the label for a listbox
		# in NVDA and audio Applications manager dialog
		labelText = _("Audio &sources:")
		self.initApplicationsList()
		choices = [app.split(".")[0] for app in self.applications]
		self.applicationsListBox = sHelper.addLabeledControl(
			labelText,
			wx.ListBox,
			choices=choices
		)
		if focusedAppName in self.applications:
			self.applicationsListBox.SetSelection(self.applications.index(focusedAppName))
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
		# Translators: This is the label for a group
		# in NVDA and audio Applications manager dialog
		groupText = _("Sounds")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = self.NVDASoundsGroup = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is a label for a choice
		# in NVDA and audio Applications manager dialog.
		labelText = _("&Tonalities's volume:")
		self.tonalitiesLevelBox = group.addLabeledControl(
			labelText,
			wx.Choice,
			choices=levels,
		)
		# Translators: This is a label of a button appearing
		# in NVDA and audio Applications manager dialog
		labelText = _("&change sound files's gain")
		self.modifyGainButton = group.addItem(wx.Button(groupBox, label=labelText))
		self.modifyGainButton.Bind(wx.EVT_BUTTON, self.onModifyGainButton)
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
		self.devicesListBox.Bind(wx.EVT_LISTBOX, self.onSelectDevice)
		self.devicesListBox.Bind(wx.EVT_KEY_DOWN, self.onDeviceKeyDown)
		self.devicesListBox.Bind(wx.EVT_KEY_DOWN, self.onDeviceKeyDown)
		self.applicationsListBox.Bind(wx.EVT_LISTBOX, self.onSelectApplication)
		self.applicationsListBox.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
		self.volumeBox.Bind(wx.EVT_CHOICE, self.onVolumeChoice)
		self.volumeMuteCheckBox.Bind(wx.EVT_CHECKBOX, self.onVolumeMute)
		self.leftChannelBox.Bind(wx.EVT_CHOICE, self.onLeftChannelChoice)
		self.rightChannelBox.Bind(wx.EVT_CHOICE, self.onRightChannelChoice)
		self.tonalitiesLevelBox.Bind(wx.EVT_CHOICE, self.onTonalitiesLevelChoice)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)
		self.applicationsListBox.SetFocus()
		self.updateGroups()
		self.applicationsListBox.Bind(wx.EVT_SET_FOCUS, self.onFocusApplicationsList)
		index = self.applicationsListBox.GetSelection()
		application = self.applications[index]
		info = self.formatApplicationInfo(application, name=False, mute=True)
		if info:
			wx.CallLater(100, ui.message, info)
		info = self.formatApplicationInfo(application, name=True, mute=True)
		if info:
			wx.CallLater(
				40,
				braille.handler.message,
				info)

	def Destroy(self):
		if self.refreshApplicationsListTimer is not None:
			self.refreshApplicationsListTimer.Stop()
		self.Unbind(wx.EVT_ACTIVATE)
		# for garbage collector
		del self.audioSources
		del self.devices
		del self._currentDevice
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
			self.applicationsListBox.SetFocus()
		else:
			del self.backToForeground
		evt.Skip()

	def initApplicationsList(self):
		self.applications = sorted(list(self.audioSources.sources.keys()))

	def updateApplicationsList(self):
		self.audioSources = audioCore.AudioSources(self._currentDevice)
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
		elif self.applications:
			self.applicationsListBox.SetSelection(0)

	def focusApplicationsList(self, speakEnd=False):
		self.refreshApplicationsListTimer.Stop()
		self.refreshApplicacionsListTimer = None
		if not self.isActive or not self.applicationsListBox.HasFocus():
			return
		self.updateApplicationsList()
		if len(self.applications) == 0:
			return
		index = self.applicationsListBox.GetSelection()
		application = self.applications[index]
		self.updateGroups(application)
		if speakEnd:
			info = self.formatApplicationInfo(application, name=True, mute=True)
			if not info:
				return
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
		self.refreshApplicationsListTimer = wx.CallLater(delay, self.focusApplicationsList, speakEnd)

	def updateGroups(self, application=None):
		self.updateVolumeGroup()
		self.updateChannelsGroup()
		self.updateNVDASoundsGroup()

	def updateNVDASoundsGroup(self, application=None):
		if self.applicationsListBox.Count == 0:
			self.tonalitiesLevelBox.Disable()
			self.modifyGainButton.Disable()
			for item in range(0, self.NVDASoundsGroup.sizer.GetItemCount()):
				self.NVDASoundsGroup.sizer.Hide(item)
			return
		from ..settings import toggleAllowNVDATonesVolumeAdjustmentAdvancedOption
		if application is None:
			index = self.applicationsListBox.GetSelection()
			application = self.applications[index]
		if isNVDA(application):
			from ..settings import toggleAllowNVDASoundGainModificationAdvancedOption
			if (
				not toggleAllowNVDASoundGainModificationAdvancedOption(False)
				and not toggleAllowNVDATonesVolumeAdjustmentAdvancedOption(False)
			):
				for item in range(0, self.NVDASoundsGroup.sizer.GetItemCount()):
					self.NVDASoundsGroup.sizer.Hide(item)
				return
			for item in range(0, self.NVDASoundsGroup.sizer.GetItemCount()):
				self.NVDASoundsGroup.sizer.Show(item)
			if not isWasapiUsed() and toggleAllowNVDATonesVolumeAdjustmentAdvancedOption(False):
				self.tonalitiesLevelBox.Enable()
				from ..settings import _addonConfigManager
				level = _addonConfigManager.getTonalitiesVolumeLevel()
				self.tonalitiesLevelBox.SetStringSelection(str(level))
			else:
				self.tonalitiesLevelBox.Disable()
			from ..settings import toggleAllowNVDASoundGainModificationAdvancedOption
			if toggleAllowNVDASoundGainModificationAdvancedOption(False):
				self.modifyGainButton.Enable()
			else:
				self.modifyGainButton.Disable()
		else:
			for item in range(0, self.NVDASoundsGroup.sizer.GetItemCount()):
				self.NVDASoundsGroup.sizer.Hide(item)

	def updateVolumeGroup(self, application=None):
		if self.applicationsListBox.Count == 0:
			# hide volume  choice box
			self.volumeBox.Disable()
			self.volumeMuteCheckBox.Disable()
			return
		self.volumeBox.Enable()
		self.volumeMuteCheckBox.Enable()
		if application is None:
			index = self.applicationsListBox.GetSelection()
			application = self.applications[index]
		audioSource = self.audioSources.getAudioSource(application)
		volume = audioSource.volume
		mute = audioSource.getMute()
		if isNVDA(application):
			self.volumeMuteCheckBox.Disable()
		else:
			self.volumeMuteCheckBox.Enable()
			self.volumeMuteCheckBox.SetValue(mute)
		level = self._currentDevice.getAbsoluteLevel(volume)
		self.volumeBox.SetStringSelection(str(level))
		log.debug("updateVolumeGroup: %s, volume: %s, device: %s, volume: %s" % (
			application, volume, self._currentDevice.name, self._currentDevice.getVolume()))

	def updateChannelsGroup(self, application=None):
		if self.applicationsListBox.Count == 0:
			self.leftChannelBox.Disable()
			self.rightChannelBox.Disable()
			return
		if application is None:
			index = self.applicationsListBox.GetSelection()
			application = self.applications[index]
		audioSource = self.audioSources.getAudioSource(application)
		if not audioSource.isStereo:
			self.leftChannelBox.Disable()
			self.rightChannelBox.Disable()
			return
		self.leftChannelBox.Enable()
		self.rightChannelBox.Enable()
		channelsVolume = audioSource.channelsVolume
		leftVolume = int(channelsVolume[0] * 100)
		rightVolume = int(channelsVolume[1] * 100)
		self.leftChannelBox.SetStringSelection(str(leftVolume))
		self.rightChannelBox.SetStringSelection(str(rightVolume))

	def formatApplicationInfo(self, application, name=False, position=True, volume=False, mute=True):
		log.debug("formatApplicationInfo application= %s, name= %s, position= %s, volume= %s, mute= %s" % (
			application, name, position, volume, mute))
		textList = []
		if name:
			textList.append(application.split(".")[0])
		if position:
			audioSource = self.audioSources.getAudioSource(application)
			positionMsg = audioSource.getApplicationVolumeInfo()
			if len(positionMsg):
				textList.append(positionMsg)
		if volume:
			from .audioCore import volumeMsg
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
		if info:

			wx.CallLater(40, speech.speakMessage, info)
		info = self.formatApplicationInfo(application, name=True, mute=True)
		if info:
			wx.CallLater(
				40,
				braille.handler.message,
				info)

	def playTonesOnDevice(self, deviceName):
		# to play a tone on the selected output device if option is true
		from ..settings import togglePlayToneOnAudioDeviceAdvancedOption
		if not togglePlayToneOnAudioDeviceAdvancedOption(False):
			return
		from synthDriverHandler import _audioOutputDevice
		curOutputDevice = _audioOutputDevice
		config.conf["speech"]["outputDevice"] = deviceName
		# Reinitialize the tones module to update the audio device
		import tones
		tones.terminate()
		tones.initialize()
		tones.beep(250, 100)
		time.sleep(0.3)
		tones.beep(350, 100)
		time.sleep(0.3)
		config.conf["speech"]["outputDevice"] = curOutputDevice
		# Reinitialize the tones module to update the audio device to the current output device
		import tones
		tones.terminate()
		tones.initialize()

	def onSelectDevice(self, evt):
		index = self.devicesListBox.GetSelection()
		device = self.devices[index]
		self._currentDevice = device
		# update audio sources
		self.audioSources = audioCore.AudioSources(self._currentDevice)
		self.updateApplicationsList()
		if self.applications:
			index = self.applicationsListBox.GetSelection()
			application = self.applications[index]
		else:
			application = None
		self.updateGroups(application)
		self.playTonesOnDevice(device.nvdaDeviceName)

	def onSelectApplication(self, evt):
		index = self.applicationsListBox.GetSelection()
		application = self.applications[index]
		self.updateGroups(application)
		self.reportState(application)
		if evt:
			evt.Skip()

	def _onDeviceKeyDown(self, evt):
		def _changeCurrentAudioDeviceVolume(offset):
			level = round(100 * self._currentDevice.getVolume()) + offset
			if level > 100:
				level = 100
			else:
				minimumLevel = _addonConfigManager .getMinMasterVolumeLevel()
				if level < minimumLevel:
					level = minimumLevel
			self._currentDevice.changeVolume(action="set", value=level)
			index = self.applicationsListBox.GetSelection()
			application = self.applications[index]
			self.updateVolumeGroup(application)
			self.updateNVDASoundsGroup(application)

		mod = evt.GetModifiers()
		keyCode = evt.GetKeyCode()
		if mod == wx.MOD_CONTROL | wx.MOD_SHIFT:
			# for audio device volume modification
			from ..settings import _addonConfigManager
			offset = _addonConfigManager.getVolumeChangeStepLevel()
			if keyCode == wx.WXK_UP:
				wx.CallLater(40, _changeCurrentAudioDeviceVolume, offset)
			elif keyCode == wx.WXK_DOWN:
				wx.CallLater(40, _changeCurrentAudioDeviceVolume, -offset)
			elif keyCode == wx.WXK_PAGEUP:
				wx.CallLater(40, _changeCurrentAudioDeviceVolume, 2 * offset)
			elif keyCode == wx.WXK_PAGEDOWN:
				wx.CallLater(40, _changeCurrentAudioDeviceVolume, -2 * offset)
			elif keyCode == wx.WXK_HOME:
				wx.CallLater(40, self._currentDevice.changeVolume, action="max")
			elif keyCode == wx.WXK_END:
				wx.CallLater(40, self._currentDevice.changeVolume, action="min")
			# no more with control and shift
			else:
				return False
			return True
		return False

	def onDeviceKeyDown(self, evt):
		if self._onDeviceKeyDown(evt):
			return
		evt.Skip()

	def onKeyDown(self, evt):
		if self.applicationsListBox.Count == 0:
			return

		def changeApplicationVolume(application, offset):
			level = int(self.volumeBox.GetStringSelection()) + offset
			level = max(0, level)
			level = min(100, level)
			audioSources = self.audioSources
			(relativeLevel, absoluteLevel) = audioSources.validateVolumeLevel(level, application)
			self.volumeBox.SetStringSelection(str(absoluteLevel))
			audioSources.setApplicationVolume(application, relativeLevel, True, absoluteLevel)
			self.updateVolumeGroup(application)

		if self._onDeviceKeyDown(evt):
			# key down for change device volume
			return
		index = self.applicationsListBox.GetSelection()
		application = self.applications[index]
		mod = evt.GetModifiers()
		keyCode = evt.GetKeyCode()
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
		audioSources = self.audioSources
		nvdaAudioSource = audioSources.getNVDAAudioSource()
		toggleChannels = audioSources.toggleChannels
		splitChannels = audioSources.splitChannels
		if keyCode == wx.WXK_LEFT:
			if mod == wx.MOD_SHIFT:
				if isNVDA(application):
					toggleChannels(application=application, balance="left")
					self.updateChannelsGroup(application)
				else:
					if nvdaAudioSource:
						splitChannels(application=application, NVDAChannel="left")
						self.updateChannelsGroup(application)
					else:
						wx.CallLater(40, ui.message, _("Not available, NVDA don't use this audio output device"))
				return
			if mod == wx.MOD_CONTROL:
				if nvdaAudioSource:
					splitChannels(application=None, NVDAChannel="left")
					self.updateChannelsGroup(application)
				else:
					# not available
					wx.CallLater(40, ui.message, _("Not available, NVDA don't use this audio output device"))
				return
			if mod == wx.MOD_NONE:
				toggleChannels(application=application, balance="left")
				self.updateChannelsGroup(application)
				return
		elif keyCode == wx.WXK_RIGHT:
			if mod == wx.MOD_SHIFT:
				if isNVDA(application):
					toggleChannels(application=application, balance="right")
				else:
					if nvdaAudioSource:
						splitChannels(application=application, NVDAChannel="right")
						self.updateChannelsGroup(application)
					else:
						wx.CallLater(40, ui.message, _("Not available, NVDA don't use this audio output device"))
				return
			if mod == wx.MOD_CONTROL:
				if nvdaAudioSource:
					splitChannels(application=None, NVDAChannel="right")
				else:
					# not available
					wx.CallLater(40, ui.message, _("Not available, NVDA don't use this audio output device"))
				self.updateChannelsGroup(application)
				return
			if mod == wx.MOD_NONE:
				toggleChannels(application=application, balance="right")
				self.updateChannelsGroup(application)
				return
		elif keyCode == wx.WXK_SPACE:
			if mod == wx.MOD_SHIFT:
				if nvdaAudioSource:
					splitChannels(application=application, NVDAChannel=None)
					self.updateChannelsGroup(application)
				else:
					# not available
					wx.CallLater(40, ui.message, _("Not available, NVDA don't use this audio output device"))
				return
			if mod == wx.MOD_CONTROL:
				splitChannels(application=None, NVDAChannel=None)
				self.updateChannelsGroup(application)
				return
			if mod == wx.MOD_NONE:
				toggleChannels(application=application, balance="center")
				self.updateChannelsGroup(application)
				return

		evt.Skip()

	def onVolumeChoice(self, evt):
		appIndex = self.applicationsListBox.GetSelection()
		application = self.applications[appIndex]
		level = int(self.volumeBox.GetStringSelection())
		audioSources = self.audioSources
		(relativeLevel, absoluteLevel) = audioSources.validateVolumeLevel(level, application)
		audioSources.setApplicationVolume(application, relativeLevel, False)
		self.updateVolumeGroup(application)

	def channelChange(self):
		leftVolume = int(self.leftChannelBox.GetStringSelection()) / 100
		rightVolume = int(self.rightChannelBox.GetStringSelection()) / 100
		index = self.applicationsListBox.GetSelection()
		application = self.applications[index]
		if isNVDA(application) and (not leftVolume and not rightVolume):
			# Translators: message to user to inform
			# hat the NVDA channel levels cannot be set to zero simultaneously
			wx.CallLater(40, ui.message, _("The volume of NVDA channels cannot be zero both simultaneously"))
			self.updateChannelsGroup(application)
			return
		audioSources = self.audioSources
		audioSource = audioSources.getAudioSource(application)
		if not audioSource:
			return
		audioSource.setChannels((leftVolume, rightVolume))

	def onLeftChannelChoice(self, evt):
		self.channelChange()
		evt.Skip()

	def onRightChannelChoice(self, evt):
		self.channelChange()
		evt.Skip()

	def onTonalitiesLevelChoice(self, evt):
		level = int(self.tonalitiesLevelBox.GetStringSelection())
		from ..settings import _addonConfigManager
		_addonConfigManager.setTonalitiesVolumeLevel(level)
		evt.Skip()

	def _mute(self, mute):
		index = self.applicationsListBox.GetSelection()
		application = self.applications[index]
		audioSource = self.audioSources.getAudioSource(application)
		audioSource.setMute(mute)

	def onVolumeMute(self, evt):
		self._mute(self.volumeMuteCheckBox.GetValue())
		evt.Skip()

	def onModifyGainButton(self, evt):
		dlg = GainModificationDialog(self)
		dlg.ShowModal()
		dlg.Destroy()
		evt.Skip()

	@classmethod
	def run(cls):
		if isOpened(cls):
			return
		# scan devices
		from .audioCore import audioOutputDevicesManager
		audioOutputDevicesManager.scanDone = False
		audioOutputDevicesManager.runNewDevicesScan()
		# Translators: message to user for waiting the end of audio output devices searching
		msg = _("Searching for audio output devices in progress")
		msg = "%s, %s" % (_("Please wait"), msg)
		ui.message(msg)
		# wait for 5 seconds
		i = 50
		from time import sleep
		sleep(2.0)
		while not audioOutputDevicesManager.scanDone and i:
			sleep(0.1)
			i -= 1
		if i == 0:
			log.debug(" end of scan too long")
			return
		audioOutputDevicesManager.shouldStopScan = False
		mainFrame.prePopup()
		d = cls(mainFrame)
		d.CentreOnScreen()
		d.Show()
		mainFrame.postPopup()


class GainModificationDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	title = None
	# help in the user manual.
	helpObj = getHelpObj("hdr34-1")

	NVDAWavesIdToDescription = {
		"NVDAWaves_browseMode.wav": _("Browse mode activated"),
		"NVDAWaves_focusMode.wav": _("Focus mode activated"),
		"NVDAWaves_error.wav": _("Error"),
		"NVDAWaves_exit.wav": _("NVDA exit"),
		"NVDAWaves_screenCurtainOff.wav": _("Screen curtain off"),
		"NVDAWaves_screenCurtainOn.wav": _("Screen curtain on"),
		"NVDAWaves_start.wav": _("NVDA start"),
		"NVDAWaves_suggestionsClosed.wav": _("Suggestions closed"),
		"NVDAWaves_suggestionsOpened.wav": _("Suggestions Opened"),
		"NVDAWaves_textError.wav": _("Text error"),
	}
	_addonSoundFileToDescription = {}

	sountIDToOriginalPath = {}

	def __init__(self, parent):
		# Translators: This is the title of the ModifyGainImport dialog.
		dialogTitle = _("NVDA sound files's Gain modification")
		GainModificationDialog.title = makeAddonWindowTitle(dialogTitle)
		super().__init__(
			parent,
			wx.ID_ANY,
			self.title,
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX
		)
		configPath = os.path.abspath(globalVars.appArgs.configPath)
		self.tempFile = os.path.join(configPath, "NVDAExtensionGlobalPlugin-temporary.wav")
		# modified waves directory
		self.modifiedWavesPath = waves.getModifiedWavesPath()
		self.initList()
		self.doGui()
		self.CentreOnScreen()

	def initList(self):
		NVDAWavesPath = os.path.join(os.getcwd(), "waves")
		addonSoundsPath = os.path.join(addonHandler.getCodeAddon().path, "sounds")
		addonTextAnalyzerSoundsPath = os.path.join(addonSoundsPath, "textAnalyzerAlerts")
		dirs = [NVDAWavesPath, addonSoundsPath, addonTextAnalyzerSoundsPath]
		self.soundFileNames = []
		self.soundIDToPath = {}
		self.soundIDToOriginalPath = {}
		for dirPath in dirs:
			files = os.listdir(dirPath)
			if dirPath == NVDAWavesPath:
				# start.wav is excluded because it is used before add-on loading
				files.remove("start.wav")

			for file in files:
				fullPath = os.path.join(dirPath, file)
				id = waves.getFileNameIdentification(fullPath)
				self.soundFileNames.append(id)
				self.soundIDToOriginalPath[id] = fullPath
				path = os.path.join(self.modifiedWavesPath, id)
				if os.path.exists(path):
					self.soundIDToPath[id] = path
				else:
					self.soundIDToPath[id] = fullPath

	def getDescription(self, id):
		desc = self.NVDAWavesIdToDescription.get(id)
		if desc is None:
			desc = id
		return desc

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label of list box appearing
		# on the ModifyGain dialog.
		labelText = _("&Sounds:")
		choice = []
		for id in self.soundFileNames:
			desc = self.getDescription(id)
			if self.soundIDToPath[id] != self.soundIDToOriginalPath[id]:
				desc = desc + " - " + _("modified")
			choice.append(desc)
		self.soundFilesListBox = sHelper.addLabeledControl(
			labelText,
			wx.ListBox,
			choices=choice
		)
		self.soundFilesListBox .Bind(wx.EVT_LISTBOX, self.onSelectSound)
		# translators: this is a label for a button in ModifyGain dialog.
		labelText = _("&Play")
		playButton = sHelper.addItem(wx.Button(self, label=labelText))
		playButton .Bind(wx.EVT_BUTTON, self.onPlayButton)
		# Translators: This is the label for a group
		# in ModifyGaindialog
		groupText = _("Gain")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# Translators: This is the label of choice box appearing
		# on the ModifyGain dialog.
		labelText = _("&Level:")
		choice = [str(x) for x in range(30, 0, -1)]
		choice.extend([str(-x) for x in range(0, 31)])
		self.gainChoiceBox = group.addLabeledControl(
			labelText,
			wx.Choice,
			choices=choice
		)
		self.gainChoiceBox.SetStringSelection("0")
		self.gainChoiceBox.Bind(wx.EVT_CHOICE, self.onSelectGain)
		# translators: this is a label for a button in ModifyGain dialog.
		labelText = _("&Check")
		self.checkButton = group.addItem(wx.Button(groupBox, label=labelText))
		self.checkButton .Bind(wx.EVT_BUTTON, self.onCheckButton)
		# translators: this is a label for a button in ModifyGain dialog.
		labelText = _("&Apply gain")
		self.applyButton = group.addItem(wx.Button(groupBox, label=labelText))
		self.applyButton .Bind(wx.EVT_BUTTON, self.onApplyButton)
		# translators: this is a label for a button in ModifyGain dialog.
		labelText = _("Apply gain &to all sounds")
		self.applyToAllButton = group.addItem(wx.Button(groupBox, label=labelText))
		self.applyToAllButton .Bind(wx.EVT_BUTTON, self.onApplyToAllButton)
		# Translators: This is the label for a group
		# in ModifyGaindialog
		groupText = _("Back to factory sounds")
		groupSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=groupText)
		groupBox = groupSizer.GetStaticBox()
		group = BoxSizerHelper(self, sizer=groupSizer)
		sHelper.addItem(group)
		# translators: this is a label for a button in ModifyGain dialog.
		labelText = _("R&eset selected sound")
		self.resetButton = group.addItem(wx.Button(groupBox, label=labelText))
		self.resetButton .Bind(wx.EVT_BUTTON, self.onResetButton)
		# translators: this is a label for a button in ModifyGain dialog.
		labelText = _("reset all s&ounds")
		self.resetAllButton = group.addItem(wx.Button(groupBox, label=labelText))
		self.resetAllButton .Bind(wx.EVT_BUTTON, self.onResetAllButton)
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		closeButton = bHelper.addButton(
			self, id=wx.ID_CLOSE, label=NVDAString("&Close"))
		closeButton.Bind(wx.EVT_BUTTON, self.onCloseButton)
		self.SetEscapeId(wx.ID_CLOSE)
		mainSizer.Add(
			sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		self.soundFilesListBox .SetSelection(0)
		self.soundFilesListBox .SetFocus()
		self.updateButtons()

	def updateButtons(self):
		if not os.path.exists(self.modifiedWavesPath) or len(os.listdir(self.modifiedWavesPath)) == 0:
			# hide reset all soundsbutton
			self.resetAllButton .Disable()
		else:
			self.resetAllButton .Enable()
		index = self.soundFilesListBox .GetSelection()
		soundID = self.soundFileNames[index]
		if self.soundIDToPath[soundID] == self.soundIDToOriginalPath[soundID]:
			# disable reset to factory button
			self.resetButton .Disable()
		else:
			self.resetButton .Enable()
		gain = int(self.gainChoiceBox.GetStringSelection())
		if gain:
			self.checkButton.Enable()
			self.applyButton.Enable()
			self.applyToAllButton.Enable()
		else:
			self.checkButton.Disable()
			self.applyButton.Disable()
			self.applyToAllButton.Disable()

	def onSelectSound(self, evt):
		self.updateButtons()
		evt.Skip()

	def onSelectGain(self, evt):
		self.updateButtons()
		evt.Skip()

	def onCheckButton(self, evt):
		gain = int(self.gainChoiceBox.GetStringSelection())
		index = self.soundFilesListBox .GetSelection()
		soundID = self.soundFileNames[index]
		path = self.soundIDToPath[soundID]
		result = waves.applyGain(gain, source=path, target=self.tempFile)
		if not result:
			return
		from nvwave import playWaveFile
		playWaveFile(self.tempFile)

	def _applyGain(self, gain, index):
		soundID = self.soundFileNames[index]
		path = self.soundIDToPath[soundID]
		if not os.path.exists(self.modifiedWavesPath):
			# create it
			try:
				os.makedirs(self.modifiedWavesPath)
			except OSError:
				if not os.path.exists(self.modifiedWavesPath):
					log.error("Impossible to create the folder: %s" % self.modifiedWavesPath)
					return False
		target = os.path.join(self.modifiedWavesPath, soundID)
		result = waves.applyGain(gain, source=path, target=target)
		if not result:
			log.warning("Gain cannot aplied to %s" % path)
			return False
		self.soundIDToPath[soundID] = target
		desc = self.getDescription(soundID) + " - " + _("modified")
		self.soundFilesListBox .SetString(index, desc)
		self.updateButtons()
		return True

	def onApplyButton(self, evt):
		gain = int(self.gainChoiceBox.GetStringSelection())
		index = self.soundFilesListBox .GetSelection()
		if self._applyGain(gain, index):
			# Translators: message to user to report gain apply
			desc = self.getDescription(self.soundFileNames[index])
			wx.CallLater(40, ui.message, _("The Gain has been applied to %s sound") % desc)
			return
		log.error("gain cannot be aply")

	def onApplyToAllButton(self, evt):
		gain = int(self.gainChoiceBox.GetStringSelection())
		soundsNotModified = []
		for index in range(0, self.soundFilesListBox .Count):
			if not self._applyGain(gain, index):
				soundsNotModified.append(self.soundFileNames[index])
		if len(soundsNotModified):
			log.warning("Gain could not be applied to: %s" % ", ".join(soundsNotModified))
			return
		# Translators: message to user to report gain modification
		wx.CallLater(40, ui.message, _("Gain has been applied to all sounds"))

	def onPlayButton(self, evt):
		index = self.soundFilesListBox .GetSelection()
		soundID = self.soundFileNames[index]
		path = self.soundIDToPath[soundID]
		from nvwave import playWaveFile
		playWaveFile(path)

	def _resetSound(self, index):
		soundID = self.soundFileNames[index]
		path = os.path.join(self.modifiedWavesPath, soundID)
		if os.path.exists(path):
			os.remove(path)
			if os.path.exists(path):
				log.error("Cannot remove %s file" % path)
		self.soundIDToPath[soundID] = self.soundIDToOriginalPath[soundID]
		self.soundFilesListBox .SetString(index, self.getDescription(soundID))

	def onResetButton(self, evt):
		index = self.soundFilesListBox .GetSelection()
		soundID = self.soundFileNames[index]
		self._resetSound(index)
		self.soundFilesListBox .SetFocus()
		self.updateButtons()
		# Translators: message to user to report reseting to factory
		wx.CallLater(40, ui.message, _("%s sound resets to factory sound") % self.getDescription(soundID))

	def onResetAllButton(self, evt):
		for index in range(0, self.soundFilesListBox .Count):
			self._resetSound(index)
		os.rmdir(self.modifiedWavesPath)
		self.updateButtons()
		self.soundFilesListBox .SetFocus()
		# Translators: message to user to report reseting of all sounds
		wx.CallLater(40, ui.message, _("All are have been reset to factory sounds"))

	def onCloseButton(self, evt):
		if os.path.exists(self.tempFile):
			os.remove(self.tempFile)
		if os.path.exists(self.modifiedWavesPath):
			files = os.listdir(self.modifiedWavesPath)
			if len(files) == 0:
				os.rmdir(self.modifiedWavesPath)
		self.Destroy()
