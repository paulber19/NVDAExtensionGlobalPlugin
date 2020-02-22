# updateCheck.py
# common Part of all of my add-on
# Copyright 2019 Paulber19
#some parts of code comes from others add-ons:
# add-on Updater (author Joseph Lee)
# brailleExtender (author Andre-Abush )

import addonHandler
addonHandler.initTranslation()
from logHandler import log
import os
import time
import sys
import gui
import wx
from .NVDAStrings  import  NVDAString
import globalVars
import core
import config
import ui
try:
	from urllib import urlopen
except:
	from urllib.request import urlopen

from updateCheck import UpdateDownloader
import tempfile
import threading
py3 = sys.version.startswith("3")
try:
	from addonAPIVersion import getAPIVersionTupleFromString
except:
	# for compatibility with nvda 2018.4.1
	import re
	
	
	ADDON_API_VERSION_REGEX = re.compile(r"^(0|\d{4})\.(\d)(?:\.(\d))?$")
	def getAPIVersionTupleFromString(version):
		"""Converts a string containing an NVDA version to a tuple of the form (versionYear, versionMajor, versionMinor)"""
		match = ADDON_API_VERSION_REGEX.match(version)
		if not match:
			raise ValueError(version)
		return tuple(int(i) if i is not None else 0 for i in match.groups())



_curAddon = addonHandler.getCodeAddon()
_curAddonName = _curAddon.manifest["name"]
def checkCompatibility(addonName,minimumNVDAVersion = None, lastTestedVersion = None, minimumWindowsVersion =None, auto = True):
	def checkWindowsCompatibility(minimumWindowsVersion, auto):
			# Some add-ons require a specific Windows release or later.
			import winVersion
			if minimumWindowsVersion is None:
				minimumWindowsVersion = winVersion.winVersion[:3]
			else:
				minimumWindowsVersion = [int(data) for data in minimumWindowsVersion.split(".")]
			minimumWinMajor, minimumWinMinor, minimumWinBuild = minimumWindowsVersion
			winMajor, winMinor, winBuild = winVersion.winVersion[:3]
			if (winMajor, winMinor, winBuild) < (minimumWinMajor, minimumWinMinor, minimumWinBuild):
				if not auto:
					# Translators: The message displayed when the add-on requires a newer version of Windows.
					#gui.messageBox(_("{name} add-on is not compatible with this version of Windows.").format(name = addonName),
					gui.messageBox(_("The update is not compatible with this version of Windows."),

						makAddonWindow(NVDAString("Error")),
						wx.OK | wx.ICON_ERROR)
				return False
			return True
	def checkNVDACompatibility(minimumNVDAVersion, lastTestedNVDAVersion, auto):
		# Check compatibility with NVDA 
		import versionInfo
		if minimumNVDAVersion is None:
			minimumNVDAVersion = [versionInfo.version_year, versionInfo.version_major]
		if lastTestedNVDAVersion is None:
			lastTestedNVDAVersion = [versionInfo.version_year, versionInfo.version_major]
		# For NVDA version, only version_year.version_major will be checked.
		minimumYear, minimumMajor = minimumNVDAVersion[:2]
		lastTestedYear, lastTestedMajor = lastTestedNVDAVersion[:2]
		if not ((minimumYear, minimumMajor) <= (versionInfo.version_year, versionInfo.version_major) <= (lastTestedYear, lastTestedMajor)):
			if not auto:
				# Translators: The message displayed when trying to update an add-on that is not going to be compatible with the current version of NVDA.
				gui.messageBox(_("The update is not compatible with this version of NVDA. Minimum NVDA version: {minYear}{minMajor}, last tested: {testedYear}.{testedMajor}.").format(minYear = minimumYear, minMajor = minimumMajor, testedYear=lastTestedYear, testedMajor=lastTestedMajor),
				makeAddonWindowTitle(NVDAString("Error")),
				wx.OK | wx.ICON_ERROR)
			return False
		return True
	res = checkNVDACompatibility(minimumNVDAVersion, lastTestedVersion, auto)
	if res:
		return checkWindowsCompatibility( minimumWindowsVersion, auto)
	return False

def makeAddonWindowTitle(dialogTitle):
	curAddon = addonHandler.getCodeAddon()
	addonSummary = curAddon.manifest['summary']
	return "%s - %s"%(addonSummary, dialogTitle)




class AddonUpdateDownloader(UpdateDownloader):
	"""Same as downloader class for NVDA screen reader updates.
	No hash checking for now, and URL's and temp file paths are different.
	"""

	def __init__(self, url, addonName, fileHash=None):
		"""Constructor.
		@param url: URLs to try for the update file.
		@type url: str
		@param addonName: Name of the add-on being downloaded.
		@type addonName: str
		@param fileHash: The SHA-1 hash of the file as a hex string.
		@type fileHash: basestring
		"""
		self.urls = [url, ]
		self.addonName = addonName
		self.destPath = tempfile.mktemp(prefix="nvda_addonUpdate-", suffix=".nvda-addon")
		self.fileHash = fileHash
		self.addonHasBeenUpdated = False
		log.warning("starting download: %s"%url)

	def start(self):
		"""Start the download.
		"""
		self._shouldCancel = False
		# Use a timer because timers aren't re-entrant.
		self._guiExecTimer = wx.PyTimer(self._guiExecNotify)
		gui.mainFrame.prePopup()
		# Translators: The title of the dialog displayed while downloading add-on update.
		self._progressDialog = wx.ProgressDialog(makeAddonWindowTitle(_("Update")),
			# Translators: The progress message indicating the name of the add-on being downloaded.
			_("Downloading {name}").format(name = self.addonName),
			# PD_AUTO_HIDE is required because ProgressDialog.Update blocks at 100%
			# and waits for the user to press the Close button.
			style=wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_AUTO_HIDE,
			parent=gui.mainFrame)
		self._progressDialog.Raise()
		t = threading.Thread(target=self._bg)
		t.daemon = True
		t.start()

	def _error(self):
		self._stopped()
		gui.messageBox(
			# Translators: A message indicating that an error occurred while downloading an update to NVDA.
			_("Error downloading update for {name}.").format(name = self.addonName),
			makeAddonWindowTitle(NVDAString("Error")),
			wx.OK | wx.ICON_ERROR)
		self.continueUpdatingAddons()
	
	def _download(self, url):
		try:
				remote = urlopen(url)
		except:
			log.warning("Download: cannot open url: %s"%url)
			raise RuntimeError("URL Download failed: %s url cannot be opened"%url )


		if remote.code != 200:
			raise RuntimeError("Download failed with code %d" % remote.code)
		# #2352: Some security scanners such as Eset NOD32 HTTP Scanner
		# cause huge read delays while downloading.
		# Therefore, set a higher timeout.
		if sys.version_info.major == 2: remote.fp._sock.settimeout(120)
		size = int(remote.headers["content-length"])
		with open(self.destPath, "wb") as local:
			if self.fileHash:
				hasher = hashlib.sha1()
			self._guiExec(self._downloadReport, 0, size)
			read = 0
			chunk=8192
			while True:
				if self._shouldCancel:
					return
				if size -read <chunk:
					chunk =size -read
				block = remote.read(chunk)
				if not block:
					break
				read += len(block)
				if self._shouldCancel:
					return
				local.write(block)
				if self.fileHash:
					hasher.update(block)
				self._guiExec(self._downloadReport, read, size)
			if read < size:
				raise RuntimeError("Content too short")
			if self.fileHash and hasher.hexdigest() != self.fileHash:
				raise RuntimeError("Content has incorrect file hash")
		self._guiExec(self._downloadReport, read, size)

	def _downloadSuccess(self):
		def getBundle():
			try:
				bundle=addonHandler.AddonBundle(self.destPath.decode("mbcs"))
			except AttributeError:
				bundle=addonHandler.AddonBundle(self.destPath)
			except:
				log.error("Error opening addon bundle from %s"%self.destPath,exc_info=True)
				# Translators: The message displayed when an error occurs when trying to update an add-on package due to package problems.
				gui.messageBox(_("Cannot update {name} - missing file or invalid file format").format(name = self.addonName),
					makeAddonWindowTitle(NVDAString("Error")),
					wx.OK | wx.ICON_ERROR)
				return None
			return bundle

		self._stopped()
		try:
			bundle = getBundle()
			if bundle is None:
				self.continueUpdatingAddons()
				return
			minimumNVDAVersion = bundle.manifest.get("minimumNVDAVersion", None)
			lastTestedNVDAVersion = bundle.manifest.get("lastTestedNVDAVersion", None)
			minimumWindowsVersion = bundle.manifest.get("minimumWindowsVersion", None)
			bundleName=bundle.manifest['name']
			if not checkCompatibility(bundleName, minimumNVDAVersion, lastTestedNVDAVersion, minimumWindowsVersion):
				self.continueUpdatingAddons()
				return
			isDisabled = False
			# Optimization (future): it is better to remove would-be add-ons all at once instead of doing it each time a bundle is opened.
			for addon in addonHandler.getAvailableAddons():
				# Check for disabled state first.
				if bundleName==addon.manifest['name']:
					if addon.isDisabled:
						isDisabled = True
					if not addon.isPendingRemove:
						addon.requestRemove()
					break
			progressDialog = gui.IndeterminateProgressDialog(gui.mainFrame,
			# Translators: The title of the dialog presented while an Addon is being updated.
			makeAddonWindowTitle(_("Updating")),
			# Translators: The message displayed while an addon is being updated.
			_("Please wait while the add-on is being updated."))
			try:
				gui.ExecAndPump(addonHandler.installAddonBundle,bundle)
			except:
				log.error("Error installing  addon bundle from %s"%self.destPath,exc_info=True)
				progressDialog.done()
				# Translators: The message displayed when an error occurs when installing an add-on package.
				gui.messageBox(_("Failed to update {name} add-on").format(name = self.addonName),
					makeAddonWindowTitle(NVDAString("Error")),
					wx.OK | wx.ICON_ERROR)
				self.continueUpdatingAddons()
				return
			else:
				progressDialog.done()
				self.addonHasBeenUpdated = True
				if isDisabled:
					for addon in addonHandler.getAvailableAddons():
						if bundleName==addon.manifest['name'] and addon.isPendingInstall:
							addon.enable(False)
							break
		finally:
			try:
				os.remove(self.destPath)
			except OSError:
				pass
			if self.addonHasBeenUpdated:
				if gui.messageBox(NVDAString("Changes were made to add-ons. You must restart NVDA for these changes to take effect. Would you like to restart now?"),
					NVDAString("Restart NVDA"),
					wx.YES|wx.NO|wx.ICON_WARNING)==wx.YES:
					wx.CallAfter(core.restart)
				return
		self.continueUpdatingAddons()

	def continueUpdatingAddons(self):
		# Do not leave add-on update installers in the temp directory.
		try:
			os.remove(self.destPath)
		except OSError:
			pass


		
class CheckForAddonUpdate(object):
	def __init__(self, addonName = None, updateInfosFile = None, auto = True, releaseToDev = False):
		self.addon = None
		if addonName is None:
			# get current add-on
			self.addon = addonHandler.getCodeAddon()
		else:
			# find add-on in available add-ons
			for addon in addonHandler.getAvailableAddons():
				if addon.manifest["name"] == addonName:
					self.addon = addon
					break
		if self.addon is None:
			log.warning("CheckForAddonUpdate: no add-on")
			return
		log.warning("Check for %s add-on update"%self.addon.manifest["name"])
		self.addonSummary = self.addon.manifest["summary"]
		self.auto = auto
		self.releaseToDev = releaseToDev
		self.destPath = tempfile.mktemp(prefix="myAddons-", suffix=".latest")
		self.updateInfosFile = updateInfosFile
		self.title = _("{summary} - update").format(summary = self.addonSummary)
		# get latest addon update infos
		latestUpdateInfos = self.getLatestUpdateInfos(self.updateInfosFile)
		if latestUpdateInfos is None:
			return
		# check if service is in maintenance
		if latestUpdateInfos .get("inMaintenance") and latestUpdateInfos ["inMaintenance"]:
			if auto: return
			gui.messageBox(
				_("The service is temporarily under maintenance. Please, try again later."),
				self.title,
				wx.OK|wx.ICON_INFORMATION)
			return
		addonUpdateInfos = latestUpdateInfos.get(self.addon.manifest["name"])
		if addonUpdateInfos is None:
			# no update for this add-on
			wx.CallAfter(self.upToDateDialog, self.auto)
			return
		newUpdate = self.checkForNewUpdate(addonUpdateInfos) if addonUpdateInfos is not None else None
		if newUpdate is None:
			self.upToDateDialog(self.auto)
			return
		(version, url, minimumNVDAVersion, lastTestedNVDAVersion) = newUpdate
		if not checkCompatibility(self.addon.manifest["summary"], minimumNVDAVersion, lastTestedNVDAVersion, None, auto):
			return
		url = "{baseURL}/{url}/{addonName}-{version}.nvda-addon".format(baseURL = latestUpdateInfos["baseURL"], addonName = self.addon.manifest["name"], url= url, version = version)
		self.availableUpdateDialog (version, url) 

	def availableUpdateDialog(self, version, url):
		#Translators: message to user to report a new version.
		message = _("New version available, version %s. Do you want download it now?")%version
		with    UpdateCheckResultDialog(gui.mainFrame, self.title, message, auto = self.auto) as d:
			res = d.ShowModal() 
			if res == wx.ID_NO: return
			if res == wx.ID_YES:
				self.processUpdate(url)
				return
			# later
			from .state import setRemindUpdate
			setRemindUpdate(True)
	
	def upToDateDialog(self, auto):
		if auto: return
		gui.messageBox(
			_("You are up-to-date. %s is the latest version.") %self.addon.manifest["version"],
			self.title,
			wx.OK|wx.ICON_INFORMATION)

	def errorUpdateDialog(self):
		res = gui.messageBox(
			_("Oops! There was a problem checking for updates. Please retry later") ,
			self.title,
			wx.OK|wx.ICON_ERROR)

	def getLatestUpdateInfos(self, updateInfosFile = None):
		def importCodePy2(code, moduleName, add_to_sys_modules=0):
			""" code can be any object containing code -- string, file object, or
			compiled code object. Returns a new module object initialized
			by dynamically importing the given code and optionally adds it
			to sys.modules under the given name.
			"""
			import imp
			try:
				mod = imp.new_module(moduleName)
				if add_to_sys_modules:
					import sys
					sys.modules[moduleName] = mod
				exec (code) in mod.__dict__
			except:
				log.warning("Error importing myAddons.latest")
				mod =  None
			return mod


		def importCodePy3(fileName, moduleName):
			import importlib.machinery
			import importlib.util
			loader = importlib.machinery.SourceFileLoader(moduleName, fileName)
			spec = importlib.util.spec_from_loader(loader.name, loader)
			mod = importlib.util.module_from_spec(spec)
			try:
				loader.exec_module(mod)
			except:
				log.error("importCodePy3: cannot load myAddons.latest module")
				mod = None
			return mod

		res = None
		if updateInfosFile is None:
			try:
				url = "https://github.com/paulber007/AllMyNVDAAddons/raw/master/myAddons.latest"
				res = urlopen(url)
			except IOError as e:
				log.warning("Fail to download update informations: error = %s"%e)
				if not self.auto:
					self.errorUpdateDialog()
				return None
			if res is None or res.code not in [200, 202]:
				log.warning("no update informations: code = %s"%res.code if res is not None else none)
				if not self.auto:
					self.errorUpdateDialog()
				return None
			with open(self.destPath, "wb") as local:
				local.write(res.read())
			res.close()
			local.close()
			time.sleep(0.5)
			file = self.destPath
		else:
			log.warning("getUpdateInfos with test file: %s"%updateInfosFile)
			file = updateInfosFile
		try:
			res = open(file, "r")
		except:
			log.warning("%s file cannot be opened "%file)
			if not self.auto:
				self.errorUpdateDialog()
			return None
		if py3:
			mod = importCodePy3(res.name, "myAddonsLatest")
		else:
			code = res.read()
			mod = importCodePy2(code, "myAddonsLatest")
		res.close()
		if updateInfosFile is None:
			try:
				os.remove(file)
			except:
				log.warning("error: cannot remove %s file"%file)
		if mod is None :
			if not self.auto:
				self.errorUpdateDialog()
			return
		updateInfos = mod.lastAddonVersions.copy()
		del mod

		return updateInfos


	def isOldestVersion(self, curVersion, latestVersion):
		if latestVersion is None: return False
		(curReleaseID, curBuildID) = curVersion
		curReleaseID  = curReleaseID.split(".")
		curReleaseID = tuple(int(i) for i in curReleaseID)
		(lastReleaseID, lastBuildID) = latestVersion
		lastReleaseID= lastReleaseID.split(".")
		lastReleaseID= tuple(int(i) for i in lastReleaseID)
		if curReleaseID < lastReleaseID: return True
		if curReleaseID > lastReleaseID: return False
		# same release ID
		if curBuildID == lastBuildID: return False
		if lastBuildID is None: return True
		if curBuildID is None: return False
		return int(curBuildID) < int(lastBuildID)
	def normalizeVersion(self, version):
		if version is None: return None
		v = version.split("-")
		releaseID= v[0]
		buildID = v[1] if len(v) >1 else None
		if buildID is not None:
			if "dev" in buildID: buildID = buildID.replace("dev", "")
			elif "beta" in buildID: buildID = buildID.replace("beta", "1000")
			elif "rc" in buildID: buildID = buildID.replace("rc", "1000000")
		return (releaseID, buildID)
	def checkForNewUpdate(self, addonUpdateInfos):
		curVersion = self.normalizeVersion(self.addon.manifest["version"])
		(curReleaseID, curBuildID) = curVersion
		channel= "dev"  if curBuildID is not None else "release"
		#if channel == "dev" and channel not in addonUpdateInfos: channel = "release"
		#if channel not in addonUpdateInfos: return None
		releaseVersion = addonUpdateInfos["release"].get("version")
		devVersion = addonUpdateInfos["dev"].get("version")
		isOldestThanReleaseVersion =  self.isOldestVersion(curVersion, self.normalizeVersion(releaseVersion))
		isOldestThanDevVersion = self.isOldestVersion(curVersion, self.normalizeVersion(devVersion))
		if isOldestThanReleaseVersion:
			updateChannel = "release"
			latestVersion = releaseVersion
		elif isOldestThanDevVersion:
			if channel == "release" and not self.releaseToDev:
				return None
			updateChannel = "dev"
			latestVersion = devVersion
		else:
			return None
		if updateChannel == "release":
			url = addonUpdateInfos["localURL"]
		else:
			url = "{url}/{channel}".format(channel = updateChannel, url = addonUpdateInfos["localURL"])
		minimumVersion = addonUpdateInfos[updateChannel].get("minimumNVDAVersion", None)
		minimumNVDAVersion = getAPIVersionTupleFromString(minimumVersion) if minimumVersion is not None else None
		lastTestedVersion= addonUpdateInfos[updateChannel].get("lastTestedNVDAVersion", None)
		lastTestedNVDAVersion = getAPIVersionTupleFromString(lastTestedVersion) if lastTestedVersion is not None else None
		return (latestVersion, url, minimumNVDAVersion, lastTestedNVDAVersion)
	
	def processUpdate(self, url):
		downloader = AddonUpdateDownloader(url, _curAddonName)
		downloader.start()

class UpdateCheckResultDialog(wx.Dialog):
	def __init__(self, parent, title, message, auto):
		super(UpdateCheckResultDialog,self).__init__(parent, -1, title = title )
		self.parent = parent
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		#Translators: message to user to report a new version.
		text = sHelper.addItem(wx.StaticText(self))
		text.SetLabel(message)
		bHelper= gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: This is a label of a button appearing on UpdateCheckResult dialog.
		yesButton = bHelper.addButton(self, wx.ID_YES, label=_("&Yes"))
		yesButton.Bind(wx.EVT_BUTTON, self.onYesButton)
		yesButton.SetFocus()
		# Translators: This is a label of a button appearing on UpdateCheckResult dialog.
		noButton = bHelper.addButton(self, wx.ID_NO, label=_("&No"))
		noButton.Bind(wx.EVT_BUTTON, self.onNoButton)
		if auto:  # this prompt was triggered by auto update checker
			# Translators: The label of a button to remind the user later about performing some action.
			remindMeButton = bHelper.addButton(self, label=_("&Later"))
			remindMeButton.Bind(wx.EVT_BUTTON, self.onLaterButton)
		sHelper.addDialogDismissButtons(bHelper)
		mainSizer.Add(sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		self.CentreOnScreen()
		self.Show()
	
	def onLaterButton(self, evt):
		self.EndModal(0)
	
	def onYesButton(self, evt):
		self.EndModal(wx.ID_YES)

	def onNoButton(self, evt):
		self.EndModal(wx.ID_NO)

