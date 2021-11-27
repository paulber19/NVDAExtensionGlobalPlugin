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
from ..settings import ID_VolumeControl

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
		"setMainAndNVDAVolume": (("kb:nvda+escape",), ID_VolumeControl),
		"toggleCurrentAppVolumeMute": (("kb:nvda+pause",), ID_VolumeControl),
		"increaseFocusedAppVolume": (None, ID_VolumeControl),
		"decreaseFocusedAppVolume": (None, ID_VolumeControl),
		"maximizeFocusedAppVolume": (None, ID_VolumeControl),
		"minimizeFocusedAppVolume": (None, ID_VolumeControl),
		"increaseSpeakersVolume": (None, ID_VolumeControl),
		"decreaseSpeakersVolume": (None, ID_VolumeControl),
		"maximizeSpeakersVolume": (None, ID_VolumeControl),
		"minimizeSpeakersVolume": (None, ID_VolumeControl),
		"setFocusedAppVolumeTo10Percent": (None, ID_VolumeControl),
		"setFocusedAppVolumeTo20Percent": (None, ID_VolumeControl),
		"setFocusedAppVolumeTo30Percent": (None, ID_VolumeControl),
		"setFocusedAppVolumeTo40Percent": (None, ID_VolumeControl),
		"setFocusedAppVolumeTo50Percent": (None, ID_VolumeControl),
		"setFocusedAppVolumeTo60Percent": (None, ID_VolumeControl),
		"setFocusedAppVolumeTo70Percent": (None, ID_VolumeControl),
		"setFocusedAppVolumeTo80Percent": (None, ID_VolumeControl),
		"setFocusedAppVolumeTo90Percent": (None, ID_VolumeControl),
		"setFocusedAppVolumeToPreviousLevel": (None, ID_VolumeControl),
		"setSpeakersVolumeLevelTo10": (None, ID_VolumeControl),
		"setSpeakersVolumeLevelTo20": (None, ID_VolumeControl),
		"setSpeakersVolumeLevelTo30": (None, ID_VolumeControl),
		"setSpeakersVolumeLevelTo40": (None, ID_VolumeControl),
		"setSpeakersVolumeLevelTo50": (None, ID_VolumeControl),
		"setSpeakersVolumeLevelTo60": (None, ID_VolumeControl),
		"setSpeakersVolumeLevelTo70": (None, ID_VolumeControl),
		"setSpeakersVolumeLevelTo80": (None, ID_VolumeControl),
		"setSpeakersVolumeLevelTo90": (None, ID_VolumeControl),
		"setSpeakersVolumeLevelToPreviousLevel": (None, ID_VolumeControl),
	}

	_volumeControlShellScriptToGestureAndFeatureOption = {
		"setMainAndNVDAVolume": ("kb:control+s", ID_VolumeControl),
		"increaseFocusedAppVolume": ("kb:upArrow", ID_VolumeControl),
		"decreaseFocusedAppVolume": ("kb:downArrow", ID_VolumeControl),
		"maximizeFocusedAppVolume": ("kb:pageUp", ID_VolumeControl),
		"minimizeFocusedAppVolume": ("kb:pageDown", ID_VolumeControl),
		"increaseSpeakersVolume": ("kb:control+upArrow", ID_VolumeControl),
		"decreaseSpeakersVolume": ("kb:control+downArrow", ID_VolumeControl),
		"maximizeSpeakersVolume": ("kb:control+pageUp", ID_VolumeControl),
		"minimizeSpeakersVolume": ("kb:control+pageDown", ID_VolumeControl),
		"setFocusedAppVolumeTo10Percent": ("kb:1", ID_VolumeControl),
		"setFocusedAppVolumeTo20Percent": ("kb:2", ID_VolumeControl),
		"setFocusedAppVolumeTo30Percent": ("kb:3", ID_VolumeControl),
		"setFocusedAppVolumeTo40Percent": ("kb:4", ID_VolumeControl),
		"setFocusedAppVolumeTo50Percent": ("kb:5", ID_VolumeControl),
		"setFocusedAppVolumeTo60Percent": ("kb:6", ID_VolumeControl),
		"setFocusedAppVolumeTo70Percent": ("kb:7", ID_VolumeControl),
		"setFocusedAppVolumeTo80Percent": ("kb:8", ID_VolumeControl),
		"setFocusedAppVolumeTo90Percent": ("kb:9", ID_VolumeControl),
		"setFocusedAppVolumeToPreviousLevel": ("kb:backspace", ID_VolumeControl),
		# for speakers volume
		"setSpeakersVolumeLevelTo10": ("kb:Control+1", ID_VolumeControl),
		"setSpeakersVolumeLevelTo20": ("kb:control+2", ID_VolumeControl),
		"setSpeakersVolumeLevelTo30": ("kb:control+3", ID_VolumeControl),
		"setSpeakersVolumeLevelTo40": ("kb:control+4", ID_VolumeControl),
		"setSpeakersVolumeLevelTo50": ("kb:control+5", ID_VolumeControl),
		"setSpeakersVolumeLevelTo60": ("kb:control+6", ID_VolumeControl),
		"setSpeakersVolumeLevelTo70": ("kb:control+7", ID_VolumeControl),
		"setSpeakersVolumeLevelTo80": ("kb:control+8", ID_VolumeControl),
		"setSpeakersVolumeLevelTo90": ("kb:control+9", ID_VolumeControl),
		"setSpeakersVolumeLevelToPreviousLevel": ("kb:control+backspace", ID_VolumeControl),
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
		if volumeControl.setSpeakerVolume() and volumeControl.setNVDAVolume():
			ui.message(
				# Translators: message to user nvda and main volume are established .
				_("The main volume and that of NVDA are established and their level sets to the one in the configuration"))  # noqa:E501
		else:
			ui.message(_("Not available on this operating's system"))

	def script_increaseFocusedAppVolume(self, gesture):
		wx.CallAfter(volumeControl.changeFocusedAppVolume, action="increase")
	script_increaseFocusedAppVolume .noFinish = True

	def script_decreaseFocusedAppVolume(self, gesture):
		wx.CallAfter(volumeControl.changeFocusedAppVolume, action="decrease")
	script_decreaseFocusedAppVolume .noFinish = True

	def script_maximizeFocusedAppVolume(self, gesture):
		wx.CallAfter(volumeControl.changeFocusedAppVolume, action="max")
	script_maximizeFocusedAppVolume .noFinish = True

	def script_minimizeFocusedAppVolume(self, gesture):
		wx.CallAfter(volumeControl.changeFocusedAppVolume, action="min")
	script_minimizeFocusedAppVolume .noFinish = True

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

	def script_setFocusedAppVolumeTo10Percent(self, gesture):
		wx.CallAfter(volumeControl.changeFocusedAppVolume, action="set", value=10)
	script_setFocusedAppVolumeTo10Percent.noFinish = True

	def script_setFocusedAppVolumeTo20Percent(self, gesture):
		wx.CallAfter(volumeControl.changeFocusedAppVolume, action="set", value=20)
	script_setFocusedAppVolumeTo20Percent.noFinish = True

	def script_setFocusedAppVolumeTo30Percent(self, gesture):
		wx.CallAfter(volumeControl.changeFocusedAppVolume, action="set", value=30)
	script_setFocusedAppVolumeTo30Percent.noFinish = True

	def script_setFocusedAppVolumeTo40Percent(self, gesture):
		wx.CallAfter(volumeControl.changeFocusedAppVolume, action="set", value=40)
	script_setFocusedAppVolumeTo40Percent.noFinish = True

	def script_setFocusedAppVolumeTo50Percent(self, gesture):
		wx.CallAfter(volumeControl.changeFocusedAppVolume, action="set", value=50)
	script_setFocusedAppVolumeTo50Percent.noFinish = True

	def script_setFocusedAppVolumeTo60Percent(self, gesture):
		wx.CallAfter(volumeControl.changeFocusedAppVolume, action="set", value=60)
	script_setFocusedAppVolumeTo60Percent.noFinish = True

	def script_setFocusedAppVolumeTo70Percent(self, gesture):
		wx.CallAfter(volumeControl.changeFocusedAppVolume, action="set", value=70)
	script_setFocusedAppVolumeTo70Percent.noFinish = True

	def script_setFocusedAppVolumeTo80Percent(self, gesture):
		wx.CallAfter(volumeControl.changeFocusedAppVolume, action="set", value=80)
	script_setFocusedAppVolumeTo80Percent.noFinish = True

	def script_setFocusedAppVolumeTo90Percent(self, gesture):
		wx.CallAfter(volumeControl.changeFocusedAppVolume, action="set", value=90)
	script_setFocusedAppVolumeTo90Percent.noFinish = True

	def script_setFocusedAppVolumeToPreviousLevel(self, gesture):
		wx.CallAfter(volumeControl.setFocusedAppVolumeToPreviousLevel)

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
