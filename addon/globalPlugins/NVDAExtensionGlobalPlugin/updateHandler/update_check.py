# updateCheck.py
# common Part of all of my add-on
# Copyright 2019-2025 Paulber19
# some parts of code comes from others add-ons:
# add-on Updater (author Joseph Lee)
# brailleExtender (author Andre-Abush )

import addonHandler
from logHandler import log
import os
import globalVars
import time
import api
import gui
import config
import wx
from .NVDAStrings import NVDAString
import core
import hashlib
try:
	from urllib import urlopen
except Exception:
	from urllib.request import urlopen
from updateCheck import UpdateDownloader
import tempfile
import threading
import addonAPIVersion
from versionInfo import version_year, version_major
import sys
_curAddon = addonHandler.getCodeAddon()
sharedPath = os.path.join(_curAddon.path, "shared")
sys.path.append(sharedPath)
from messages import confirm_YesNo, alert, warn, inform, ReturnCode
del sys.path[-1]
del sys.modules["messages"]

addonHandler.initTranslation()

_curAddon = addonHandler.getCodeAddon()
_checkForUpdate = False


def setCheckForUpdate(check):
	global _checkForUpdate
	_checkForUpdate = check


def shouldCheckForUpdate():
	return _checkForUpdate


def isCompatible(minimumNVDAVersion, lastTestedNVDAVersion):
	currentAPIVersion = addonAPIVersion.CURRENT
	hasAddonGotRequiredSupport = minimumNVDAVersion <= currentAPIVersion
	backwardsCompatToVersion = addonAPIVersion.BACK_COMPAT_TO
	return hasAddonGotRequiredSupport and (
		lastTestedNVDAVersion >= backwardsCompatToVersion)


def makeAddonWindowTitle(dialogTitle):
	addonSummary = _curAddon.manifest['summary']
	return "%s - %s" % (addonSummary, dialogTitle)


class AddonUpdateDownloader(UpdateDownloader):
	"""Same as downloader class for NVDA screen reader updates.
	No hash checking for now, and URL's and temp file paths are different.
	"""

	def __init__(self, url, addon, fileHash=None, autoUpdate=True):
		"""Constructor.
		@param url: URLs to try for the update file.
		@type url: str
		@param addon: the add-on being downloaded.
		@type addonName: str
		@param fileHash: The SHA-1 hash of the file as a hex string.
		@type fileHash: basestring
		"""
		self.urls = [url, ]
		self.addon = addon
		self.addonName = addon.manifest["name"]
		self.destPath = tempfile.mktemp(
			prefix="nvda_addonUpdate-", suffix=".nvda-addon")
		self.fileHash = fileHash
		self.autoUpdate = autoUpdate
		self.addonHasBeenUpdated = False
		log.warning("starting download: %s" % url)

	def start(self):
		"""Start the download.
		"""
		self._shouldCancel = False
		# Use a timer because timers aren't re-entrant.
		self._guiExecTimer = wx.PyTimer(self._guiExecNotify)
		gui.mainFrame.prePopup()
		# Translators: The title of the dialog
		# displayed while downloading add-on update.
		self._progressDialog = wx.ProgressDialog(
			makeAddonWindowTitle(_("Update")),
			# Translators: The progress message
			# indicating the name of the add-on being downloaded.
			_("Downloading {name}").format(name=self.addonName),
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
		alert(
			# Translators: A message indicating that an error occurred
			# while downloading an update to NVDA.
			_("Error downloading update for {name}.").format(name=self.addonName),
			makeAddonWindowTitle(NVDAString("Error")),
		)
		self.continueUpdatingAddons()

	def _download(self, url):
		try:
			remote = urlopen(url)
		except Exception:
			log.warning("Download: cannot open url: %s" % url)
			raise RuntimeError("URL Download failed: %s url cannot be opened" % url)
		if remote.code != 200:
			raise RuntimeError("Download failed with code %d" % remote.code)
		size = int(remote.headers["content-length"])
		with open(self.destPath, "wb") as local:
			if self.fileHash:
				hasher = hashlib.sha1()
			self._guiExec(self._downloadReport, 0, size)
			read = 0
			chunk = 8192
			while True:
				if self._shouldCancel:
					return
				if size - read < chunk:
					chunk = size - read
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
				bundle = addonHandler.AddonBundle(self.destPath.decode("mbcs"))
			except AttributeError:
				bundle = addonHandler.AddonBundle(self.destPath)
			except Exception:
				log.error(
					"Error opening addon bundle from %s" % self.destPath, exc_info=True)
				# Translators: The message displayed when an error occurs
				# when trying to update an add-on package due to package problems.
				alert(
					# Translators: message to user
					_("Cannot update {name} - missing file or invalid file format").format(
						name=self.addonName),
					makeAddonWindowTitle(NVDAString("Error")),
				)
				return None
			return bundle

		self._stopped()
		try:
			bundle = getBundle()
			if bundle is None:
				self.continueUpdatingAddons()
				return
			progressDialog = gui.IndeterminateProgressDialog(
				gui.mainFrame,
				# Translators: The title of the dialog
				# presented while an Addon is being updated.
				makeAddonWindowTitle(_("Updating")),
				# Translators: The message displayed while an addon is being updated.
				_("Please wait while the add-on is being updated."))
			try:
				if self.autoUpdate:
					# installTask must be inform that it's an autoUpdate
					# in this case, the current add-on configuration is automaticaly conserved
					extraAppArgs = globalVars.appArgsExtra if hasattr(
						globalVars, "appArgsExtra") else globalVars.unknownAppArgs
					extraAppArgs.append("addon-auto-update")
				from systemUtils import ExecAndPump
				ExecAndPump(addonHandler.installAddonBundle, bundle)
				if self.autoUpdate:
					extraAppArgs.remove("addon-auto-update")
			except Exception:
				if self.autoUpdate:
					extraAppArgs.remove("addon-auto-update")
				log.error(
					"Error installing addon bundle from %s" % self.destPath,
					exc_info=True)
				progressDialog.done()
				alert(
					# Translators: The message displayed when an error occurs
					# when installing an add-on package.
					_("Failed to update {name} add-on").format(name=self.addonName),
					makeAddonWindowTitle(NVDAString("Error")),
				)
				self.continueUpdatingAddons()
				return
			else:
				progressDialog.done()
				self.addonHasBeenUpdated = True
		finally:
			if not self.addon.isPendingRemove:
				self.addon.requestRemove()
			if self.addonHasBeenUpdated:
				if confirm_YesNo(
					NVDAString(
						"Changes were made to add-ons. "
						"You must restart NVDA for these changes to take effect. Would you like to restart now?"),
					NVDAString("Restart NVDA"),
				) == ReturnCode.YES:
					wx.CallAfter(core.restart)
		self.continueUpdatingAddons()

	def continueUpdatingAddons(self):
		# Do not leave add-on update installers in the temp directory.
		try:
			os.remove(self.destPath)
		except OSError:
			pass


class CheckForAddonUpdate(object):
	def __init__(
		self, updateInfosFile=None,
		auto=True, releaseToDev=False):
		log.debug("CheckForAddonUpdate")
		if auto and not shouldCheckForUpdate():
			return

		self.addon = addonHandler.getCodeAddon()
		log.warning("Check for %s add-on update" % self.addon.manifest["name"])
		self.addonSummary = self.addon.manifest["summary"]
		self.auto = auto
		self.releaseToDev = releaseToDev
		self.destPath = tempfile.mktemp(prefix="myAddons-", suffix=".latest")
		self.updateInfosFile = updateInfosFile
		self.title = _("{summary} - update").format(summary=self.addonSummary)
		# get latest addon update infos
		latestUpdateInfos = self.getLatestUpdateInfos(self.updateInfosFile)
		if latestUpdateInfos is None:
			return
		# check if service is in maintenance
		if latestUpdateInfos .get(
			"inMaintenance") and latestUpdateInfos["inMaintenance"] and not self.shouldByPassSiteInMaintenance():
			log.debug("service in maintenance")
			if auto:
				return
			warn(
				# Translators: message to user that the update service is temporarily in maintenance
				_("The service is temporarily under maintenance. Please, try again later."),
				self.title,
			)
			return
		addonUpdateInfos = latestUpdateInfos.get(self.addon.manifest["name"])
		if addonUpdateInfos is None:
			# no update for this add-on
			wx.CallAfter(self.upToDateDialog, self.auto)
			return
		newUpdate = self.checkForNewUpdate(addonUpdateInfos)
		if newUpdate is None:
			self.upToDateDialog(self.auto)
			return
		(version, url, minimumNVDAVersion, lastTestedNVDAVersion) = newUpdate
		import versionInfo
		if minimumNVDAVersion is None:
			minimumNVDAVersion = [versionInfo.version_year, versionInfo.version_major]
		if lastTestedNVDAVersion is None:
			lastTestedNVDAVersion = [versionInfo.version_year, versionInfo.version_major]
		# For NVDA version, only version_year.version_major will be checked.
		minimumYear, minimumMajor = minimumNVDAVersion[:2]
		lastTestedYear, lastTestedMajor = lastTestedNVDAVersion[:2]
		isVersionCompatible = isCompatible(minimumNVDAVersion, lastTestedNVDAVersion)
		if [version_year, version_major] <= [2023, 2] and not isVersionCompatible:
			if not auto:
				# Translators: The message displayed  when trying to update an add-on
				# that is not going to be compatible with the current version of NVDA.
				incompatibleAddonMsg = _(
					"The update is not compatible with this version of NVDA. "
					"Minimum NVDA version: {minYear}.{minMajor}, last tested: {testedYear}.{testedMajor}.").format(
						minYear=minimumYear, minMajor=minimumMajor, testedYear=lastTestedYear, testedMajor=lastTestedMajor)
				alert(
					incompatibleAddonMsg,
					makeAddonWindowTitle(NVDAString("Error")),
				)
			return
		url = "{baseURL}/{url}/{addonName}-{version}.nvda-addon".format(
			baseURL=latestUpdateInfos["baseURL"],
			addonName=self.addon.manifest["name"],
			url=url,
			version=version)
		compatibilityRange = ("%s.%s" % (minimumYear, minimumMajor), "%s.%s" % (lastTestedYear, lastTestedMajor))
		self.availableUpdateDialog(version, url, isVersionCompatible, compatibilityRange)

	def shouldByPassSiteInMaintenance(self):
		byPassMaintenanceFile = "paulber007AllMyAddons-maintenance.bypass"
		userConfigPath = globalVars.appArgs.configPath
		path = os.path.join(userConfigPath, byPassMaintenanceFile)
		if os.path.exists(path):
			log.debug("update service is in maintenance")

			return True
		return False

	def getreleaseNoteURL(self, stable=True):
		baseURL = "https://rawgit.com/paulber007/AllMyNVDAAddons/master"
		if stable:
			basereleaseNoteURL = "{baseURL}/{addonName}/{releaseNotes}".format(
				baseURL=baseURL,
				addonName=self.addon.manifest["name"],
				releaseNotes="releaseNotes")
			from languageHandler import getLanguage
			url = "{url}/{language}/changes.html".format(
				url=basereleaseNoteURL,
				language=getLanguage())
			try:
				urlopen(url)
			except IOError:
				lang = getLanguage().split("_")[0]
				url = "{url}/{language}/changes.html".format(
					url=basereleaseNoteURL,
					language=lang)
				try:
					urlopen(url)
				except IOError:
					url = "{url}/{language}/changes.html".format(
						url=basereleaseNoteURL,
						language="en")
		else:
			# dev url
			url = "{baseURL}/{addonName}/dev/changes.html".format(
				baseURL=baseURL,
				addonName=self.addon.manifest["name"])
		return url

	def availableUpdateDialog(self, version, url, versionCompatible=True, compatibilityRange=("1", "2")):
		if versionCompatible:
			# Translators: message to user to report a new version.
			msg = _("New version%s is available. Do you want to download it now?") % version
		else:
			# Translators: message to user to report a new incompatible version.
			msg = _(
				"""New version{0} is available.
But it is not compatible with this version of NVDA: minimum version requred = {1}, last version tested  = {2}.
Do you want to ignore this incompatibility and still download it now?""") .format(
					version, compatibilityRange[0], compatibilityRange[1])
		with UpdateCheckResultDialog(
			gui.mainFrame, self.title, msg, auto=self.auto, releaseNoteURL=self.releaseNoteURL) as d:
			res = d.ShowModal()
			if res == wx.ID_NO:
				return
			if res == wx.ID_YES:
				self.processUpdate(url)
				return
			# later
			from .state import setRemindUpdate
			setRemindUpdate(True)

	def upToDateDialog(self, auto):
		if auto:
			return
		inform(
			# Translators: message to user that add-on is up to date
			_("You are up-to-date. %s is the latest version.") % (
				self.addon.manifest["version"]),
			self.title,
		)

	def errorUpdateDialog(self):
		alert(
			_("Oops! There was a problem checking for updates. Please retry later"),
			self.title,
		)

	def getLatestUpdateInfos(self, updateInfosFile=None):
		def importCode(fileName, moduleName):
			import importlib.machinery
			import importlib.util
			loader = importlib.machinery.SourceFileLoader(moduleName, fileName)
			spec = importlib.util.spec_from_loader(loader.name, loader)
			mod = importlib.util.module_from_spec(spec)
			loader.exec_module(mod)
			return mod

		res = None
		if updateInfosFile is None:
			try:
				url = "https://rawgit.com/paulber007/AllMyNVDAAddons/master/myAddons.latest"
				res = urlopen(url)
			except IOError as e:
				log.warning("Fail to download update informations: error = %s" % e)
				if not self.auto:
					self.errorUpdateDialog()
				return None
			if res is None or res.code not in [200, 202]:
				log.warning("no update informations: code = %s" % res.code if res is not None else "None")
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
			log.warning("getUpdateInfos with test file: %s" % updateInfosFile)
			file = updateInfosFile
		try:
			res = open(file, "r")
		except Exception:
			log.warning("%s file cannot be opened " % file)
			if not self.auto:
				self.errorUpdateDialog()
			return None
		mod = importCode(res.name, "myAddonsLatest")
		res.close()
		if updateInfosFile is None:
			try:
				os.remove(file)
			except Exception:
				log.warning("error: cannot remove %s file" % file)
		if mod is None:
			self.errorUpdateDialog()
			return
		updateInfos = mod.lastAddonVersions.copy()
		del mod

		return updateInfos

	def isOldestVersion(self, curVersion, latestVersion):
		if latestVersion is None:
			return False
		(curReleaseID, curBuildID) = curVersion
		curReleaseID = curReleaseID.split(".")
		curReleaseID = tuple(int(i) for i in curReleaseID)
		(lastReleaseID, lastBuildID) = latestVersion
		lastReleaseID = lastReleaseID.split(".")
		lastReleaseID = tuple(int(i) for i in lastReleaseID)
		if curReleaseID < lastReleaseID:
			return True
		if curReleaseID > lastReleaseID:
			return False
		# same release ID
		if curBuildID == lastBuildID:
			return False
		if lastBuildID is None:
			return True
		if curBuildID is None:
			return False
		return int(curBuildID) < int(lastBuildID)

	def normalizeVersion(self, version):
		if version is None:
			return None
		v = version.split("-")
		releaseID = v[0]
		buildID = v[1] if len(v) > 1 else None
		if buildID is not None:
			if "dev" in buildID:
				buildID = buildID.replace("dev", "")
			elif "beta" in buildID:
				buildID = buildID.replace("beta", "1000")
			elif "rc" in buildID:
				buildID = buildID.replace("rc", "1000000")
		return (releaseID, buildID)

	def checkForNewUpdate(self, addonUpdateInfos):
		curVersion = self.normalizeVersion(self.addon.manifest["version"])
		(curReleaseID, curBuildID) = curVersion
		channel = "dev" if curBuildID is not None else "release"
		releaseVersion = addonUpdateInfos["release"].get("version")
		devVersion = addonUpdateInfos["dev"].get("version")
		isOldestThanReleaseVersion = self.isOldestVersion(
			curVersion, self.normalizeVersion(releaseVersion))
		isOldestThanDevVersion = self.isOldestVersion(
			curVersion, self.normalizeVersion(devVersion))
		if channel == "dev" and not self.releaseToDev:
			# update from dev version to stable version
			updateChannel = "release"
			latestVersion = releaseVersion
		elif isOldestThanReleaseVersion:
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
			self.releaseNoteURL = self.getreleaseNoteURL()
		else:
			url = "{url}/{channel}".format(
				channel=updateChannel, url=addonUpdateInfos["localURL"])
			self.releaseNoteURL = self.getreleaseNoteURL(False)
		minimumVersion = addonUpdateInfos[updateChannel].get(
			"minimumNVDAVersion", None)
		minimumNVDAVersion = addonAPIVersion .getAPIVersionTupleFromString(
			minimumVersion) if minimumVersion is not None else None
		lastTestedVersion = addonUpdateInfos[updateChannel].get(
			"lastTestedNVDAVersion", None)
		lastTestedNVDAVersion = addonAPIVersion .getAPIVersionTupleFromString(
			lastTestedVersion) if lastTestedVersion is not None else None
		return (latestVersion, url, minimumNVDAVersion, lastTestedNVDAVersion)

	def processUpdate(self, url):
		downloader = AddonUpdateDownloader(url, _curAddon, autoUpdate=self.auto)
		downloader.start()


class UpdateCheckResultDialog(wx.Dialog):
	def __init__(self, parent, title, message, auto, releaseNoteURL=None):
		super(UpdateCheckResultDialog, self).__init__(parent, -1, title=title)
		self.parent = parent
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: message to user to report a new version.
		text = sHelper.addItem(wx.StaticText(self))
		text.SetLabel(message)
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: This is a label of a button appearing
		# on UpdateCheckResult dialog.
		yesButton = bHelper.addButton(self, wx.ID_YES, label=_("&Yes"))
		yesButton.Bind(wx.EVT_BUTTON, self.onYesButton)
		yesButton.SetFocus()
		# Translators: This is a label of a button appearing
		# on UpdateCheckResult dialog.
		noButton = bHelper.addButton(self, wx.ID_NO, label=_("&No"))
		noButton.Bind(wx.EVT_BUTTON, self.onNoButton)
		if auto:
			# Translators: The label of a button to remind the user later
			# about performing some action.
			remindMeButton = bHelper.addButton(self, label=_("&Later"))
			remindMeButton.Bind(wx.EVT_BUTTON, self.onLaterButton)
		if releaseNoteURL is not None:
			self.releaseNoteURL = releaseNoteURL
			releaseNotesButton = bHelper.addButton(self, label=_("Wha&t's new"))
			releaseNotesButton .Bind(wx.EVT_BUTTON, self.onReleaseNotesButton)
		sHelper.addDialogDismissButtons(bHelper)
		mainSizer.Add(
			sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		self.CentreOnScreen()
		# the text in the window must be spoken.
		option = config.conf["presentation"]["reportObjectDescriptions"]
		config.conf["presentation"]["reportObjectDescriptions"] = True
		self.Show()
		api.processPendingEvents()
		config.conf["presentation"]["reportObjectDescriptions"] = option

	def onLaterButton(self, evt):
		self.EndModal(0)

	def onReleaseNotesButton(self, evt):
		import webbrowser
		webbrowser.open(self.releaseNoteURL)

	def onYesButton(self, evt):
		self.EndModal(wx.ID_YES)

	def onNoButton(self, evt):
		self.EndModal(wx.ID_NO)
