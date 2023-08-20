# globalPlugins\NVDAExtensionGlobalPlugin\WindowsExplorer\__init__.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2023 Paulber19
# This file is covered by the GNU General Public License.


import addonHandler
from baseObject import ScriptableObject
from scriptHandler import script, getLastScriptRepeatCount
from comtypes.client import CreateObject as COMCreate
import ui
import api
import os
from ..utils import delayScriptTask, stopDelayScriptTask, clearDelayScriptTask
try:
	# for nvda version >= 2021.2
	from controlTypes.role import Role
	ROLE_LISTITEM = Role.LISTITEM
except (ModuleNotFoundError, AttributeError):
	from controlTypes import ROLE_LISTITEM


addonHandler.initTranslation()

_curAddon = addonHandler.getCodeAddon()
_addonSummary = _curAddon.manifest['summary']


_shell = None


#  part of code coming from Nao (NVDA Advanced OCR)  add-on
# Auteurs : Alessandro Albano, Davide De Carne, Simone Dal Maso
def get_selected_files_explorer_ps():
	import subprocess
	si = subprocess.STARTUPINFO()
	si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
	cmd = "$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding; (New-Object -ComObject 'Shell.Application').Windows() | ForEach-Object { echo \\\"$($_.HWND):$($_.Document.FocusedItem.Path)\\\" }"  # noqa: E501
	cmd = "powershell.exe \"{}\"".format(cmd)
	try:
		p = subprocess.Popen(
			cmd, stdin=subprocess.DEVNULL,
			stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, startupinfo=si,
			encoding="utf-8", text=True)
		stdout, stderr = p.communicate()
		if p.returncode == 0 and stdout:
			ret = {}
			lines = stdout.splitlines()
			for line in lines:
				hwnd, name = line.split(':', 1)
				ret[str(hwnd)] = name
			return ret
	except Exception:
		pass
	return False


#  part of code coming from Nao (NVDA Advanced OCR)  add-on
# Auteurs : Alessandro Albano, Davide De Carne, Simone Dal Maso
def get_selected_file_explorer(obj=None):
	if obj is None:
		obj = api.getForegroundObject()
	file_path = None
	# We check if we are in the Windows Explorer.
	if True:
		desktop = False
		try:
			global _shell
			if not _shell:
				_shell = COMCreate("shell.application")
			# We go through the list of open Windows Explorers to find the one that has the focus.
			for window in _shell.Windows():
				if window.hwnd == obj.windowHandle:
					# Now that we have the current folder, we can explore the SelectedItems collection.
					file_path = str(window.Document.FocusedItem.path)
					break
			else:  # loop exhausted
				desktop = True
		except Exception:
			try:
				windows = get_selected_files_explorer_ps()
				if windows:
					if str(obj.windowHandle) in windows:
						file_path = windows[str(obj.windowHandle)]
					else:
						desktop = True
			except Exception:
				pass
		if desktop:
			desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
			file_path = desktop_path + '\\' + api.getDesktopObject().objectWithFocus().name
	return file_path


class ScriptsForWindowsExplorer(ScriptableObject):

	@script(
		# Translators: Message presented in input help mode.
		description=_(
			"Report the short path of focused folder or file  of Windows Explorer."
			" Twice: report the full path. Three time: copy the full path  to the clipboard"),
		category=_addonSummary
	)
	def script_reportFocusedExplorerItemPath(self, gesture):
		def callback(count):
			clearDelayScriptTask()
			path = get_selected_file_explorer()
			if not path:
				return
			if count == 0:
				# report short path
				pathList = path.split("\\")
				from ..settings import _addonConfigManager
				nbOfFolders = _addonConfigManager.getReducedPathItemsNumber()
				if len(pathList) <= nbOfFolders + 1:
					ui.message(path)
					return
				text = pathList[0] + "\\...\\" + "\\".join(pathList[- nbOfFolders:])

				ui.message(text)
			elif count == 1:
				# report full path
				ui.message(path)
			else:
				# copy path to clipboard
				api.copyToClip(path)
				# Translators: message to user to report path copy to clipboard
				ui.message(_("{0} copied to clipboard") .format(path))
		stopDelayScriptTask()
		count = getLastScriptRepeatCount()
		if count > 2:
			callback(count)
		else:
			delayScriptTask(callback, count)

	@script(
		# Translators: Message presented in input help mode.
		description=_(
			"Report the path of the file or folder under the cursor of Windows Explorer by going up the folders tree"),
		category=_addonSummary
	)
	def script_reportFocusedExplorerItemFolderPath(self, gesture):
		stopDelayScriptTask()
		path = get_selected_file_explorer()
		if not path:
			return
		pathList = path.split("\\")[:-1]
		nb = len(pathList)
		if nb == 1:
			ui.message(pathList[0])
			return
		from ..settings import toggleReversedPathWithLevelAdvancedOption
		withLevel = toggleReversedPathWithLevelAdvancedOption(False)
		text = ""
		for index in range(nb - 1, -1, -1):
			level = nb - index
			item = pathList[-level]
			if withLevel:
				levelText = "(n-%s)" % str(level - 1) if level - 1 else "(n)"
				text = text + "{name} {levelText}, " .format(name=item, levelText=levelText)
			else:
				text = text + " %s, " % item
		ui.message(text[:-2])


def updateChooseNVDAOverlayClass(obj, clsList):
	if (
		obj.appModule
		and obj.appModule.appName
		and obj.appModule.appName == "explorer"
		and obj.role == ROLE_LISTITEM
	):
		clsList.insert(0, ScriptsForWindowsExplorer)
