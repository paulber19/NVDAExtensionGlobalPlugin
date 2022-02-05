# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\volumeControlScripts.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2021 Paulber19
# This file is covered by the GNU General Public License.


import addonHandler
import baseObject
import ui
import wx
import api
import appModuleHandler
from . import volumeControl
from ..settings.addonConfig import FCT_VolumeControl, FCT_SplitAudio

addonHandler.initTranslation()

# Translators: The name of a category of NVDA commands.
SCRCAT_VOLUME_CONTROL = _("Volume control")
# Translators: Input help mode message
# for setting to 90% the volume of current focused application command.
_setFocusedAppVolumeToMsg = _("Set the volume of current focused application to %s percent")
# Translators: Input help mode message
# for setting to x the main volume.
_setSpeakersVolumeToMsg = _("Set the main volume to %s")


class ScriptsForVolume(baseObject.ScriptableObject):
	_volumeControlMainScriptToGestureAndfeatureOption = {
		"setMainAndNVDAVolume": (("kb:nvda+escape",), FCT_VolumeControl),
		"toggleCurrentAppVolumeMute": (("kb:nvda+pause",), FCT_VolumeControl),

		# for focused application
		"increaseFocusedAppVolume": (None, FCT_VolumeControl),
		"decreaseFocusedAppVolume": (None, FCT_VolumeControl),
		"maximizeFocusedAppVolume": (None, FCT_VolumeControl),
		"minimizeFocusedAppVolume": (None, FCT_VolumeControl),
		"setFocusedAppVolumeTo10Percent": (None, FCT_VolumeControl),
		"setFocusedAppVolumeTo20Percent": (None, FCT_VolumeControl),
		"setFocusedAppVolumeTo30Percent": (None, FCT_VolumeControl),
		"setFocusedAppVolumeTo40Percent": (None, FCT_VolumeControl),
		"setFocusedAppVolumeTo50Percent": (None, FCT_VolumeControl),
		"setFocusedAppVolumeTo60Percent": (None, FCT_VolumeControl),
		"setFocusedAppVolumeTo70Percent": (None, FCT_VolumeControl),
		"setFocusedAppVolumeTo80Percent": (None, FCT_VolumeControl),
		"setFocusedAppVolumeTo90Percent": (None, FCT_VolumeControl),
		"setFocusedAppVolumeToPreviousLevel": (None, FCT_VolumeControl),
		# for nvda
		"increaseNVDAVolume": (None, FCT_VolumeControl),
		"decreaseNVDAVolume": (None, FCT_VolumeControl),
		"maximizeNVDAVolume": (None, FCT_VolumeControl),
		"minimizeNVDAVolume": (None, FCT_VolumeControl),
		"setNVDAVolumeTo10Percent": (None, FCT_VolumeControl),
		"setNVDAVolumeTo20Percent": (None, FCT_VolumeControl),
		"setNVDAVolumeTo30Percent": (None, FCT_VolumeControl),
		"setNVDAVolumeTo40Percent": (None, FCT_VolumeControl),
		"setNVDAVolumeTo50Percent": (None, FCT_VolumeControl),
		"setNVDAVolumeTo60Percent": (None, FCT_VolumeControl),
		"setNVDAVolumeTo70Percent": (None, FCT_VolumeControl),
		"setNVDAVolumeTo80Percent": (None, FCT_VolumeControl),
		"setNVDATo90Percent": (None, FCT_VolumeControl),
		"setNVDAVolumeToPreviousLevel": (None, FCT_VolumeControl),
		# for speakers
		"increaseSpeakersVolume": (None, FCT_VolumeControl),
		"decreaseSpeakersVolume": (None, FCT_VolumeControl),
		"maximizeSpeakersVolume": (None, FCT_VolumeControl),
		"minimizeSpeakersVolume": (None, FCT_VolumeControl),
		"setSpeakersVolumeLevelTo10": (None, FCT_VolumeControl),
		"setSpeakersVolumeLevelTo20": (None, FCT_VolumeControl),
		"setSpeakersVolumeLevelTo30": (None, FCT_VolumeControl),
		"setSpeakersVolumeLevelTo40": (None, FCT_VolumeControl),
		"setSpeakersVolumeLevelTo50": (None, FCT_VolumeControl),
		"setSpeakersVolumeLevelTo60": (None, FCT_VolumeControl),
		"setSpeakersVolumeLevelTo70": (None, FCT_VolumeControl),
		"setSpeakersVolumeLevelTo80": (None, FCT_VolumeControl),
		"setSpeakersVolumeLevelTo90": (None, FCT_VolumeControl),
		"setSpeakersVolumeLevelToPreviousLevel": (None, FCT_VolumeControl),
		# for sound split
		"setNVDAToRightAndFocusedApplicationToLeft": (None, FCT_SplitAudio),
		"setNVDAToLeftAndFocusedApplicationToRight": (None, FCT_SplitAudio),
		"centerNVDAAndFocusedApplication": (None, FCT_SplitAudio),
		"setNVDAToRightAndAllApplicationsToLeft": (None, FCT_SplitAudio),
		"setNVDAToLeftAndAllApplicationsToRight": (None, FCT_SplitAudio),
		"centerNVDAAndAllApplications": (None, FCT_SplitAudio),
		"centerFocusedApplication": (None, None),
		"displayNVDAAndApplicationsAudioManager": (None, FCT_SplitAudio),
	}

	_volumeControlShellScriptToGestureAndFeatureOption = {
		"setMainAndNVDAVolume": ("kb:control+s", FCT_VolumeControl),
		# for focused application
		"increaseFocusedAppVolume": ("kb:upArrow", FCT_VolumeControl),
		"decreaseFocusedAppVolume": ("kb:downArrow", FCT_VolumeControl),
		"maximizeFocusedAppVolume": ("kb:pageUp", FCT_VolumeControl),
		"minimizeFocusedAppVolume": ("kb:pageDown", FCT_VolumeControl),
		"setFocusedAppVolumeTo10Percent": ("kb:1", FCT_VolumeControl),
		"setFocusedAppVolumeTo20Percent": ("kb:2", FCT_VolumeControl),
		"setFocusedAppVolumeTo30Percent": ("kb:3", FCT_VolumeControl),
		"setFocusedAppVolumeTo40Percent": ("kb:4", FCT_VolumeControl),
		"setFocusedAppVolumeTo50Percent": ("kb:5", FCT_VolumeControl),
		"setFocusedAppVolumeTo60Percent": ("kb:6", FCT_VolumeControl),
		"setFocusedAppVolumeTo70Percent": ("kb:7", FCT_VolumeControl),
		"setFocusedAppVolumeTo80Percent": ("kb:8", FCT_VolumeControl),
		"setFocusedAppVolumeTo90Percent": ("kb:9", FCT_VolumeControl),
		"setFocusedAppVolumeToPreviousLevel": ("kb:backspace", FCT_VolumeControl),
		# for nvda
		"increaseNVDAVolume": ("kb:shift+upArrow", FCT_VolumeControl),
		"decreaseNVDAVolume": ("kb:shift+downArrow", FCT_VolumeControl),
		"maximizeNVDAVolume": ("kb:shift+pageUp", FCT_VolumeControl),
		"minimizeNVDAVolume": ("kb:shift+pageDown", FCT_VolumeControl),
		"setNVDAVolumeTo10Percent": ("kb:shift+1", FCT_VolumeControl),
		"setNVDAVolumeTo20Percent": ("kb:shift+2", FCT_VolumeControl),
		"setNVDAVolumeTo30Percent": ("kb:shift+3", FCT_VolumeControl),
		"setNVDAVolumeTo40Percent": ("kb:shift+4", FCT_VolumeControl),
		"setNVDAVolumeTo50Percent": ("kb:shift+5", FCT_VolumeControl),
		"setNVDAVolumeTo60Percent": ("kb:shift+6", FCT_VolumeControl),
		"setNVDAVolumeTo70Percent": ("kb:shift+7", FCT_VolumeControl),
		"setNVDAVolumeTo80Percent": ("kb:shift+8", FCT_VolumeControl),
		"setNVDAVolumeTo90Percent": ("kb:shift+9", FCT_VolumeControl),
		"setNVDAVolumeToPreviousLevel": ("kb:shift+backspace", FCT_VolumeControl),
		"setNVDAVolumeToPreviousLevel": ("kb:shift+backspace", FCT_VolumeControl),
		# for speakers volume
		"increaseSpeakersVolume": ("kb:control+upArrow", FCT_VolumeControl),
		"decreaseSpeakersVolume": ("kb:control+downArrow", FCT_VolumeControl),
		"maximizeSpeakersVolume": ("kb:control+pageup", FCT_VolumeControl),
		"minimizeSpeakersVolume": ("kb:control+pagedown", FCT_VolumeControl),
		"setSpeakersVolumeLevelTo10": ("kb:control+1", FCT_VolumeControl),
		"setSpeakersVolumeLevelTo20": ("kb:control+2", FCT_VolumeControl),
		"setSpeakersVolumeLevelTo30": ("kb:control+3", FCT_VolumeControl),
		"setSpeakersVolumeLevelTo40": ("kb:control+4", FCT_VolumeControl),
		"setSpeakersVolumeLevelTo50": ("kb:control+5", FCT_VolumeControl),
		"setSpeakersVolumeLevelTo60": ("kb:control+6", FCT_VolumeControl),
		"setSpeakersVolumeLevelTo70": ("kb:control+7", FCT_VolumeControl),
		"setSpeakersVolumeLevelTo80": ("kb:control+8", FCT_VolumeControl),
		"setSpeakersVolumeLevelTo90": ("kb:control+9", FCT_VolumeControl),
		"setSpeakersVolumeLevelToPreviousLevel": ("kb:control+backspace", FCT_VolumeControl),
		# for sound split
		"setNVDAToRightAndFocusedApplicationToLeft": ("kb:rightArrow", FCT_SplitAudio),
		"setNVDAToLeftAndFocusedApplicationToRight": ("kb:leftArrow", FCT_SplitAudio),
		"centerNVDAAndFocusedApplication": ("kb:space", FCT_SplitAudio),
		"setNVDAToRightAndAllApplicationsToLeft": ("kb:control+rightArrow", FCT_SplitAudio),
		"setNVDAToLeftAndAllApplicationsToRight": ("kb:control+leftArrow", FCT_SplitAudio),
		"centerNVDAAndAllApplications": ("kb:control+space", FCT_SplitAudio),
		"centerFocusedApplication": ("kb:control+shift+space", None),
		"displayNVDAAndApplicationsAudioManager": ("kb:f6", FCT_SplitAudio),
	}

	def script_toggleCurrentAppVolumeMute(self, gesture):
		focus = api.getFocusObject()
		appName = appModuleHandler.getAppNameFromProcessID(focus.processID, True)
		if appName == "nvda.exe":
			ui.message(_("Unavailable for NVDA"))
			return
		try:
			volumeControl.toggleProcessVolume(appName)
		except Exception:
			ui.message(_("Not available on this operating's system"))

	def script_setMainAndNVDAVolume(self, gesture):
		if volumeControl.setSpeakerVolumeToRecoveryLevel() and volumeControl.setNVDAVolumeToRecoveryLevel():
			ui.message(
				# Translators: message to user nvda and main volume are established .
				_(
					"The main volume and that of NVDA are established and their level sets to the one in the configuration")
			)
		else:
			ui.message(_("Not available on this operating's system"))

	# for focused application
	def script_increaseFocusedAppVolume(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, action="increase")
	script_increaseFocusedAppVolume .noFinish = True

	def script_decreaseFocusedAppVolume(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, action="decrease")
	script_decreaseFocusedAppVolume .noFinish = True

	def script_maximizeFocusedAppVolume(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, action="max")
	script_maximizeFocusedAppVolume .noFinish = True

	def script_minimizeFocusedAppVolume(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, "nvda.exe", action="min")
	script_minimizeFocusedAppVolume .noFinish = True

	def script_setFocusedAppVolumeTo10Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, action="set", value=10)
	script_setFocusedAppVolumeTo10Percent.noFinish = True

	def script_setFocusedAppVolumeTo20Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, action="set", value=20)
	script_setFocusedAppVolumeTo20Percent.noFinish = True

	def script_setFocusedAppVolumeTo30Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, action="set", value=30)
	script_setFocusedAppVolumeTo30Percent.noFinish = True

	def script_setFocusedAppVolumeTo40Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, action="set", value=40)
	script_setFocusedAppVolumeTo40Percent.noFinish = True

	def script_setFocusedAppVolumeTo50Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, action="set", value=50)
	script_setFocusedAppVolumeTo50Percent.noFinish = True

	def script_setFocusedAppVolumeTo60Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, action="set", value=60)
	script_setFocusedAppVolumeTo60Percent.noFinish = True

	def script_setFocusedAppVolumeTo70Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, action="set", value=70)
	script_setFocusedAppVolumeTo70Percent.noFinish = True

	def script_setFocusedAppVolumeTo80Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, action="set", value=80)
	script_setFocusedAppVolumeTo80Percent.noFinish = True

	def script_setFocusedAppVolumeTo90Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, action="set", value=90)
	script_setFocusedAppVolumeTo90Percent.noFinish = True

	def script_setFocusedAppVolumeToPreviousLevel(self, gesture):
		wx.CallAfter(volumeControl.setFocusedAppVolumeToPreviousLevel)

	# for NVDA
	def script_increaseNVDAVolume(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, "nvda.exe", action="increase")
	script_increaseNVDAVolume .noFinish = True

	def script_decreaseNVDAVolume(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, "nvda.exe", action="decrease")
	script_decreaseNVDAVolume .noFinish = True

	def script_maximizeNVDAVolume(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, "nvda.exe", action="max")
	script_maximizeNVDAVolume .noFinish = True

	def script_minimizeNVDAVolume(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, "nvda.exe", action="min")
	script_minimizeNVDAVolume .noFinish = True

	def script_setNVDAVolumeTo10Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, "nvda.exe", action="set", value=10)
	script_setNVDAVolumeTo10Percent.noFinish = True

	def script_setNVDAVolumeTo20Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, "nvda.exe", action="set", value=20)
	script_setNVDAVolumeTo20Percent.noFinish = True

	def script_setNVDAVolumeTo30Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, "nvda.exe", action="set", value=30)
	script_setNVDAVolumeTo30Percent.noFinish = True

	def script_setNVDAVolumeTo40Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, "nvda.exe", action="set", value=40)
	script_setNVDAVolumeTo40Percent.noFinish = True

	def script_setNVDAVolumeTo50Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, "nvda.exe", action="set", value=50)
	script_setNVDAVolumeTo50Percent.noFinish = True

	def script_setNVDAVolumeTo60Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, "nvda.exe", action="set", value=60)
	script_setNVDAVolumeTo60Percent.noFinish = True

	def script_setNVDAVolumeTo70Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, "nvda.exe", action="set", value=70)
	script_setNVDAVolumeTo70Percent.noFinish = True

	def script_setNVDAVolumeTo80Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, "nvda.exe", action="set", value=80)
	script_setNVDAVolumeTo80Percent.noFinish = True

	def script_setNVDAVolumeTo90Percent(self, gesture):
		wx.CallAfter(volumeControl.changeAppVolume, "nvda.exe", action="set", value=90)
	script_setNVDAVolumeTo90Percent.noFinish = True

	def script_setNVDAVolumeToPreviousLevel(self, gesture):
		wx.CallAfter(volumeControl.setNVDAVolumeToPreviousLevel)

	# for speakers
	def script_increaseSpeakersVolume(self, gesture):
		wx.CallAfter(volumeControl.changeSpeakersVolume, action="increase")
	script_increaseSpeakersVolume .noFinish = True

	def script_decreaseSpeakersVolume(self, gesture):
		wx.CallAfter(volumeControl.changeSpeakersVolume, action="decrease")
	script_decreaseSpeakersVolume .noFinish = True

	def script_maximizeSpeakersVolume(self, gesture):
		wx.CallAfter(volumeControl.changeSpeakersVolume, action="max")
	script_maximizeSpeakersVolume .noFinish = True

	def script_minimizeSpeakersVolume(self, gesture):
		wx.CallAfter(volumeControl.changeSpeakersVolume, action="min")
	script_minimizeSpeakersVolume .noFinish = True

	def script_setSpeakersVolumeLevelTo10(self, gesture):
		wx.CallAfter(volumeControl.changeSpeakersVolume, action="set", value=10)
	script_setSpeakersVolumeLevelTo10.noFinish = True

	def script_setSpeakersVolumeLevelTo20(self, gesture):
		wx.CallAfter(volumeControl.changeSpeakersVolume, action="set", value=20)
	script_setSpeakersVolumeLevelTo20.noFinish = True

	def script_setSpeakersVolumeLevelTo30(self, gesture):
		wx.CallAfter(volumeControl.changeSpeakersVolume, action="set", value=30)
	script_setSpeakersVolumeLevelTo30.noFinish = True

	def script_setSpeakersVolumeLevelTo40(self, gesture):
		wx.CallAfter(volumeControl.changeSpeakersVolume, action="set", value=40)
	script_setSpeakersVolumeLevelTo40.noFinish = True

	def script_setSpeakersVolumeLevelTo50(self, gesture):
		wx.CallAfter(volumeControl.changeSpeakersVolume, action="set", value=50)
	script_setSpeakersVolumeLevelTo50.noFinish = True

	def script_setSpeakersVolumeLevelTo60(self, gesture):
		wx.CallAfter(volumeControl.changeSpeakersVolume, action="set", value=60)
	script_setSpeakersVolumeLevelTo60.noFinish = True

	def script_setSpeakersVolumeLevelTo70(self, gesture):
		wx.CallAfter(volumeControl.changeSpeakersVolume, action="set", value=70)
	script_setSpeakersVolumeLevelTo70.noFinish = True

	def script_setSpeakersVolumeLevelTo80(self, gesture):
		wx.CallAfter(volumeControl.changeSpeakersVolume, action="set", value=80)
	script_setSpeakersVolumeLevelTo80.noFinish = True

	def script_setSpeakersVolumeLevelTo90(self, gesture):
		wx.CallAfter(volumeControl.changeSpeakersVolume, action="set", value=90)
	script_setSpeakersVolumeLevelTo90.noFinish = True

	def script_setSpeakersVolumeLevelToPreviousLevel(self, gesture):
		wx.CallAfter(volumeControl.setSpeakersVolumeLevelToPreviousLevel)

	def script_setNVDAToRightAndFocusedApplicationToLeft(self, gesture):
		from ..computerTools.volumeControl import splitChannels
		focus = api.getFocusObject()
		appName = appModuleHandler.getAppNameFromProcessID(focus.processID, True)
		splitChannels(NVDAChannel="right", application=appName)

	def script_setNVDAToLeftAndFocusedApplicationToRight(self, gesture):
		from ..computerTools.volumeControl import splitChannels
		focus = api.getFocusObject()
		appName = appModuleHandler.getAppNameFromProcessID(focus.processID, True)
		splitChannels(NVDAChannel="left", application=appName)

	def script_centerNVDAAndFocusedApplication(self, gesture):
		from ..computerTools.volumeControl import splitChannels
		focus = api.getFocusObject()
		appName = appModuleHandler.getAppNameFromProcessID(focus.processID, True)
		splitChannels(NVDAChannel="None", application=appName)

	def script_setNVDAToRightAndAllApplicationsToLeft(self, gesture):
		from ..computerTools.volumeControl import splitChannels
		splitChannels(NVDAChannel="right", application=None)

	def script_setNVDAToLeftAndAllApplicationsToRight(self, gesture):
		from ..computerTools.volumeControl import splitChannels
		splitChannels(NVDAChannel="left", application=None)

	def script_centerNVDAAndAllApplications(self, gesture):
		from ..computerTools.volumeControl import splitChannels
		splitChannels(NVDAChannel="None", application=None)

	def script_centerFocusedApplication(self, gesture):
		from ..computerTools.volumeControl import centerFocusedApplication
		centerFocusedApplication()

	def script_displayNVDAAndApplicationsAudioManager(self, gesture):
		from .audioManagerDialog import NVDAAndAudioApplicationsManagerDialog
		wx.CallAfter(NVDAAndAudioApplicationsManagerDialog.run)
