# globalPlugins\NVDAExtensionGlobalPlugin\clipboardCommandAnnouncement\settingsDialogs.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2025 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


from gui.settingsDialogs import KeyboardSettingsPanel, NVDASettingsDialog
from gui import  mainFrame


class MyKeyboardSettingsPanel(KeyboardSettingsPanel):
	def makeSettings(self, settingsSizer):
		super().makeSettings(settingsSizer)
		self.alertForSpellingErrorsCheckBox.Enable()

try:
	NVDASettingsDialog.categoryClasses [NVDASettingsDialog.categoryClasses .index(KeyboardSettingsPanel)] = MyKeyboardSettingsPanel
except ValueError:
	# when the modules are reloaded, MyKeyboardSettingsPanel has already replaced KeyboardSettingsPanel.
	# But we still have to put it back in place.
	cat = NVDASettingsDialog.categoryClasses[:]
	for c in cat:
		if c.__module__ == MyKeyboardSettingsPanel.__module__:
			NVDASettingsDialog.categoryClasses[NVDASettingsDialog.categoryClasses .index(c)] = MyKeyboardSettingsPanel
			break


def myOnKeyboardSettingsCommand(*args, **kwargs):
	mainFrame.popupSettingsDialog(NVDASettingsDialog, MyKeyboardSettingsPanel)

mainFrame.onKeyboardSettingsCommand = myOnKeyboardSettingsCommand
