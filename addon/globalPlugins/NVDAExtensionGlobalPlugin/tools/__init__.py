# globalPlugins\NVDAExtensionGlobalPlugin\tools\__init__.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 -2022 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from logHandler import log
import ui
import codecs
import os
# from ctypes import *
import zipfile
import gui
import wx
import sys
import languageHandler
from ..utils import isOpened, makeAddonWindowTitle, getHelpObj
from ..utils import runInThread
from .generate import generateManifest, generateTranslatedManifest
from .gettextTools import generatePotFile, compilePoFiles
import shutil
from ..utils import contextHelpEx

addonHandler.initTranslation()


_curModuleFilePath = os.path.dirname(__file__)


# Translators: strings used to generate readme.md file
_buildVarsStrings = {
	"addonInfoStart": "addon_info = {",
	"addonInfoEnd": "}",
}


def get_all_file_paths(directory):
	file_paths = []
	for root, directories, files in os.walk(directory):
		if root[len(directory) + 1:] == "debugTools":
			continue
		for filename in files:
			if os.path.isdir(filename):
				if filename in ["__pycache", ]:
					continue
			else:
				if os.path.splitext(filename)[1]\
					in [".pyo", ".pyc", ".nvda-addon", ".pickle"]:
					continue
			filepath = os.path.join(root, filename)
			file_paths.append(filepath)
	return file_paths


def createAddonBundleFromPath(addon):
	file_paths = get_all_file_paths(addon.path)
	sys.path.append(addon.path)
	try:
		import buildVars
		from importlib import reload
		reload(buildVars)
		del sys.path[-1]
	except ImportError:
		del sys.path[-1]
		gui.messageBox(
			# Translators: message to user.
			_("Error: buildVars.py file is not found"),
			# Translators: dialog title on errorr.
			_("error"),
			wx.OK)
		return None
	addonFileName = "%s-%s.nvda-addon" % (
		buildVars.addon_info["addon_name"], buildVars.addon_info["addon_version"])
	dest = os.path.join(addon.path, addonFileName)
	if os.path.exists(dest):
		# delete previous bundle
		os.remove(dest)
	with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as zip:
		for file in file_paths:
			relativePath = os.path.relpath(file, addon.path)
			zip.write(file, relativePath)
	return addonFileName


def getLocaleLanguages(addon):
	langs = []
	if "locale" in os.listdir(addon.path):
		localeFolder = os.path.join(addon.path, "locale")
		dirs = os.listdir(localeFolder)
		for item in dirs:
			f = os.path.join(localeFolder, item)
			if os.path.isdir(f):
				langs.append(item)
	return langs


def getDocLanguages(addon):
	localeLanguages = getLocaleLanguages(addon)
	langs = []
	if "doc" in os.listdir(addon.path):
		docFolder = os.path.join(addon.path, "doc")
		dirs = os.listdir(docFolder)
		for item in dirs:
			f = os.path.join(docFolder, item)
			if not os.path.isdir(f):
				continue
			if item in localeLanguages:
				langs.append(item)
			elif "_" in item and item.split("_")[0] in localeLanguages:
				langs.append(item)
			else:
				pass
	return langs


def getMmanifestInfos(addon, lang):
	path = addon.path
	manifest_path = os.path.join(path, addonHandler.MANIFEST_FILENAME)
	with open(manifest_path) as f:
		translatedInput = None
		translatedPath = os.path.join("locale", lang)
		p = os.path.join(path, translatedPath, addonHandler.MANIFEST_FILENAME)
		if os.path.exists(p):
			log.debug("Using manifest translation from %s", p)
			translatedInput = open(p, 'rb')
			try:
				return addonHandler.AddonManifest(f, translatedInput)
			except Exception:
				# Translators: dialog title on errorr.
				dialogTitle = _("error")
				gui.messageBox(
					# Translators: message to the user on getting addon manifest.
					_("Cannot get add-on translated manifest of %s language") % lang,
					dialogTitle, wx.OK | wx.ICON_ERROR)
	return addonHandler.AddonManifest(manifest_path)


def writeHTMLFile(dest, htmlText, title, cssFileName):
	cssFile = cssFileName if cssFileName is not None else "style.css"
	lang = os.path.basename(os.path.dirname(dest)).replace('_', '-')
	with codecs.open(dest, "w", "utf-8") as f:
		f.write(
			"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
			+ "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\"\n"
			+ "    \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">\n"
			+ "<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"%s\" lang=\"%s\">\n" % (lang, lang)
			+ "<head>\n"
			+ "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\"/>\n"
			+ "<link rel=\"stylesheet\" type=\"text/css\" href=\"../%s\" media=\"screen\"/>\n" % cssFile
			+ "<title>%s</title>\n" % title
			+ "</head>\n"
		)
		f.write(htmlText)
		f.write("\n</html>\n")
	f.close()


def md2html(source):
	from ..utils.py3Compatibility import getCommonUtilitiesPath
	commonUtilitiesPath = getCommonUtilitiesPath()
	markdownPath = os.path.join(commonUtilitiesPath, "markdown")
	sys.path.append(markdownPath)
	from markdown2 import markdown
	del sys.path[-1]
	headerDic = {
		"[[!meta title=\"": "# ",
		"\"]]": " #",
	}
	with codecs.open(source, "r", "utf-8") as f:
		mdText = f.read()
		for k, v in headerDic.items():
			mdText = mdText.replace(k, v, 1)
		htmlText = markdown(mdText)
	htmlText = "<body>\n" + htmlText + "\n</body>"
	return htmlText


def getHTMLBody(dest):
	src = codecs.open(dest, "r", "utf_8", errors="replace")
	startTag = "</head>"
	endTag = "<!-- html code generated"
	appendLine = False
	text = []
	for sLine in src:
		line = sLine.lower()
		startTagFound = line.find(startTag)
		endTagFound = line.find(endTag)
		if startTagFound >= 0:
			appendLine = True
			sLine = sLine[startTagFound + len(startTag):]
			text.append(sLine)
			continue
		elif endTagFound >= 0:
			sLine = sLine[: endTagFound]
			text.append(sLine)
			break
		if appendLine:
			text.append(sLine)
	text.append("</body>")
	return "".join(text)


def t2t2html(source, dest):
	from ..utils.py3Compatibility import getUtilitiesPath
	sys.path.append(getUtilitiesPath())
	import txt2tags
	del sys.path[-1]
	txt2tags.exec_command_line(["%s" % (source), ])
	# we don't want the footer
	htmlText = getHTMLBody(dest)
	os.remove(dest)
	return htmlText


def generateHTMLFiles(addon, docDirs):
	mdCount = 0
	t2tCount = 0
	for d in docDirs:
		lang = d.split("\\")[-1]
		fileList = os.listdir(d)
		for file in fileList:
			theFile = os.path.join(d, file)
			if not os.path.isfile(theFile):
				continue
			f = file.split(".")
			ext = f[-1].lower()
			if ext not in ["md", "t2t"]:
				continue
			base = addon.path.join(f[:-1])
			dest = os.path.join(d, base + ".html")
			manifest = getMmanifestInfos(addon, lang)
			title = "%s %s" % (manifest["summary"], manifest["version"])
			if ext == "t2t":
				htmlText = t2t2html(theFile, dest)
				cssFileName = "style_t2t.css"
				t2tCount += 1
			elif ext == "md":
				htmlText = md2html(theFile)
				cssFileName = "style.css"
				mdCount += 1
			writeHTMLFile(dest, htmlText, title, cssFileName)
	return (mdCount, t2tCount)


def clean(addon):
	if os.path.exists(os.path.join(addon.path, "buildVars.pyo")):
		os.remove(os.path.join(addon.path, "buildVars.pyo"))
	if os.path.exists(os.path.join(addon.path, "buildVars.pyc")):
		os.remove(os.path.join(addon.path, "buildVars.pyc"))


def _makeHTML(addon, lang):
	# Translators: title of dialog
	dialogTitle = _("Creation of HTML documentation files")
	if "doc" not in os.listdir(addon.path):
		gui.messageBox(
			# Translators: message to user no doc folder
			_("No documentation file to convert"),
			dialogTitle, wx.OK | wx.ICON_ERROR)
		return
	docFolder = os.path.join(addon.path, "doc")
	dirList = getDocLanguages(addon)
	docDirs = []
	if lang == "all":
		for item in dirList:
			theDir = os.path.join(docFolder, item)
			docDirs.append(theDir)
	else:
		for item in dirList:
			if (item == lang or "_" in item and item.split("_")[0] == lang):
				theDir = os.path.join(docFolder, item)
				docDirs.append(theDir)
	(mdCount, t2tCount) = generateHTMLFiles(addon, docDirs)
	n = mdCount + t2tCount
	if n == 0:
		gui.messageBox(
			# Translators: message to user no converted document
			_("No file converted"),
			dialogTitle, wx.OK)
	else:
		# copy css style file
		curAddon = addonHandler.getCodeAddon()
		if mdCount:
			source = os.path.join(curAddon.path, "doc", "style_md.css")
			dest = os.path.join(docFolder, "style_md.css")
			try:
				shutil.copy(source, dest)
			except Exception:
				pass
		elif t2tCount:
			source = os.path.join(curAddon.path, "doc", "style_t2t.css")
			dest = os.path.join(docFolder, "style_t2t.css")
			try:
				shutil.copy(source, dest)
			except Exception:
				pass
		gui.messageBox(
			# Translators: message to user to report number of converted documents
			_("%s files converted") % n,
			dialogTitle, wx.OK)
	# clean up
		clean(addon)


def _makeMainManifestIni(addon):
	# Translators: title of dialog
	dialogTitle = _("Creation of manifest.ini file")
	sys.path.append(addon.path)
	try:
		import buildVars
		from importlib import reload
		reload(buildVars)
		del sys.path[-1]
	except ImportError:
		del sys.path[-1]
		gui.messageBox(
			# Translators: message to user.
			_("Error: buildVars.py file is not found"),
			dialogTitle, wx.OK)
		return
	dest = os.path.join(addon.path, "manifest.ini")
	if os.path.exists(dest):
		if gui.messageBox(
			# Translators: message to user to confirm the update of manifest.ini.
			_("The manifest.ini file already exists. Do you really want to update it?"),
			dialogTitle, wx.YES | wx.NO) == wx.NO:
			return
	templateFile = os.path.join(_curModuleFilePath, "manifest.ini.tpl")
	with codecs.open(templateFile, "r", "utf-8") as f:
		manifest_template = f.read()
	from .generate import generateManifest
	addonInfo = buildVars.addon_info.copy()
	generateManifest(dest, addonInfo, manifest_template)
	# Translators: message to user to report end of manifest.ini creation
	msg = _("manifest.ini file has been updated")
	gui.messageBox(msg, dialogTitle, wx.OK)
	# clean up
	clean(addon)


def _makeLocaleManifestIni(addon, lang):
	# Translators: title of dialog
	dialogTitle = _("Creation of localization manifest.ini file")
	sys.path.append(addon.path)
	try:
		import buildVars
		from importlib import reload
		reload(buildVars)
		del sys.path[-1]
	except ImportError:
		del sys.path[-1]
		gui.messageBox(
			# Translators: message to user.
			_("Error: buildVars.py file is not found"),
			dialogTitle, wx.OK)
		return
	templateFile = os.path.join(
		_curModuleFilePath, "manifest-translated.ini.tpl")
	with codecs.open(templateFile, "r", "utf-8") as f:
		manifest_template = f.read()
	from .generate import generateTranslatedManifest
	localeDir = os.path.join(addon.path, "locale")
	if not os.path.exists(localeDir):
		gui.messageBox(
			# Translators: message to user
			_("No language for this add-on"),
			dialogTitle, wx.OK)
		return
	if lang == "all":
		langs = os.listdir(localeDir)
	else:
		langs = [lang, ]
	manifest = getManifest(addon)
	if manifest is None:
		gui.messageBox(
			# Translators: message to user.
			_("Error: %s file is not found") % addonHandler.MANIFEST_FILENAME,
			dialogTitle, wx.OK)
		return
	count = 0
	noTranslation = []
	for lang in langs:
		moFile = os.path.join(localeDir, lang, "LC_MESSAGES", "nvda.po")
		if not os.path.exists(moFile):
			continue
		if not generateTranslatedManifest(addon, manifest, lang, manifest_template):
			noTranslation.append(lang)
		count = count + 1
	if len(noTranslation):
		# Translators: title of dialog
		dialogTitle = _("Creation of localization manifest.ini file")
		# Translators: message to user.
		missingTranslationMsg = _("Some translation strings are missing for \"%s\" language") % lang
		gui.messageBox(missingTranslationMsg, dialogTitle, wx.OK)
	if count:
		# Translators: message to user
		# to report number of translated manifest.ini files.
		msg = _("%s localization manifest.ini files created") % count
	else:
		# Translators: message to user to report no translated manifest.ini file .
		msg = _("No localization manifest.ini file created")
	gui.messageBox(msg, dialogTitle, wx.OK)
	# clean up
	clean(addon)


def _generatePOTFile(addon):
	addonSummary = addon.manifest["summary"]
	# Translators: title of dialog
	dialogTitle = _("Creation of POT file of %s add-on") % addonSummary
	sys.path.append(addon.path)
	try:
		import buildVars
		from importlib import reload
		reload(buildVars)
		del sys.path[-1]
	except ImportError:
		del sys.path[-1]

		gui.messageBox(
			# Translators: message to user.
			_("Error: buildVars.py file is not found"),
			dialogTitle, wx.OK)
		return
	potFileName = "%s-%s.pot" % (
		buildVars.addon_info["addon_name"], buildVars.addon_info["addon_version"])

	retval = generatePotFile(
		addon, potFileName, buildVars.addon_info, buildVars.i18nSources)
	if retval == 0:
		msg = _("%s file created") % potFileName
	else:
		if retval == -1:
			msg = _("Impossible to create POT file: no source file defined in buildVars.py")
		else:
			msg = _("Impossible to create POT file")
	gui.messageBox(msg, dialogTitle, wx.OK)
	# clean up
	clean(addon)


def getManifest(addon):
	manifest_path = os.path.join(addon.path, addonHandler.MANIFEST_FILENAME)
	if os.path.exists(manifest_path):
		with open(manifest_path) as f:
			manifest = addonHandler.AddonManifest(f)
			return manifest
	return None


def _prepareAddon(addon):
	addonSummary = addon.manifest["summary"]
	# Translators: title of dialog
	dialogTitle = _("Prepare %s add-on") % addonSummary
	sys.path.append(addon.path)
	try:
		import buildVars
		from importlib import reload
		reload(buildVars)
		del sys.path[-1]
	except ImportError:
		del sys.path[-1]
		gui.messageBox(
			# Translators: message to user.
			_("Error: buildVars.py file is not found"),
			dialogTitle, wx.OK)
		return
	# start
	ui.message(_("Prepare add-on start"))
	th = runInThread.RepeatBeep(delay=2.0, beep=(200, 200), isRunning=None)
	th.start()
	# update of main manifest.ini file
	dest = os.path.join(addon.path, "manifest.ini")
	templateFile = os.path.join(_curModuleFilePath, "manifest.ini.tpl")
	with codecs.open(templateFile, "r", "utf-8") as f:
		manifest_template = f.read()
	addonInfo = buildVars.addon_info.copy()
	generateManifest(dest, addonInfo, manifest_template)
	textList = []
	# Translators: part of message to report update of manifest.ini file
	textList.append(_("Manifest.ini file updated"))
	# update or creation of all translated manifest.ini files
	templateFile = os.path.join(_curModuleFilePath, "manifest-translated.ini.tpl")
	with codecs.open(templateFile, "r", "utf-8") as f:
		manifest_template = f.read()
	localeDir = os.path.join(addon.path, "locale")
	manifest = getManifest(addon)
	if manifest is None:
		gui.messageBox(
			# Translators: message to user.
			_("Error: %s file is not found") % addonHandler.MANIFEST_FILENAME,
			dialogTitle, wx.OK)
	else:
		if os.path.exists(localeDir):
			langs = os.listdir(localeDir)
			count = 0
			noTranslations = []
			for lang in langs:
				moFile = os.path.join(localeDir, lang, "LC_MESSAGES", "nvda.po")
				if not os.path.exists(moFile):
					continue
				if not generateTranslatedManifest(
					addon, manifest, lang, manifest_template):
					noTranslations.append(lang)
				count += 1
			if count:
				# Translators: message to user to report number of created files.
				msg = _("%s localization manifest.ini files created or updated") % count
				textList.append(msg)
				if len(noTranslations):
					text = ", ".join(noTranslations)
					log .warning(
						"generateTranslatedManifest: no translation for language: %s" % text)
					# Translators: message to user to report missing translated strings.
					msg = _("But for these languages,  some strings are not translated: %s") % text
					textList.append(msg)
	# convert all doc files to html
	if "doc" in os.listdir(addon.path):
		docFolder = os.path.join(addon.path, "doc")
		dirList = os.listdir(docFolder)
		docDirs = []
		for item in dirList:
			theDir = os.path.join(docFolder, item)
			if os.path.isdir(theDir):
				docDirs.append(theDir)
		(mdCount, t2tCount) = generateHTMLFiles(addon, docDirs)
		cnt = mdCount + t2tCount
		if cnt == 0:
			# Translators: message to user to report no document converted
			msg = _("No file converted")
		elif cnt == 1:
			# Translators: message to user to report only one document converted to html
			msg = _("one file converted")
		else:
			# Translators: message to user to report number of
			# documents converted to html
			msg = _("%s files converted") % cnt
			msg = _("%s HTML files created") % cnt
		textList.append(msg)

	# create pot file
	from .gettextTools import generatePotFile
	potFileName = "%s-%s.pot" % (
		buildVars.addon_info["addon_name"], buildVars.addon_info["addon_version"])
	retval = generatePotFile(
		addon, potFileName, buildVars.addon_info, buildVars.i18nSources)
	if retval == 0:
		msg = _("%s file created") % potFileName
	else:
		msg = _("Impossible to create POT file")
	textList.append(msg)
	# compile all .po files
	(count, nbOfPoFiles) = compilePoFiles(addon)
	# Translators: message to report number of po files compiled.
	msg = _("{count} poFiles compiled on {nb}").format(
		count=count, nb=nbOfPoFiles)
	textList.append(msg)
	# """ Creates the bundle
	bundleName = createAddonBundleFromPath(addon)
	if bundleName is None:
		# Translators: message to report that add-on bundle is not created.
		msg = _("Add-on bundle could not be created")
	else:
		# Translators: message to report add-on bundle file.
		msg = _("The {name} file has been created and recorded in {dir} folder")\
			.format(name=bundleName, dir=addon.path)
	textList.append(msg)
	text = "\r\n".join(textList)
	# Translators: message to user
	msg = _("Completed") + "\r\n\r\n" + text
	th.stop()
	wx.CallAfter(gui.messageBox, msg, dialogTitle, wx.OK)
	# clean up
	clean(addon)


def _createBuildVarsFile(addon):
	# Translators: title of dialog
	dialogTitle = _("Creation of buildVars.py file")
	templateFile = os.path.join(_curModuleFilePath, "buildVars.py.tpl")
	with codecs.open(templateFile, "r", "utf-8") as f:
		buildVars_template = f.read()
	manifest_path = os.path.join(addon.path, addonHandler.MANIFEST_FILENAME)
	if not os.path.exists(manifest_path):

		gui.messageBox(
			# Translators: message to user.
			_("Error: %s file is not found") % addonHandler.MANIFEST_FILENAME,
			dialogTitle, wx.OK)
		return
	with open(manifest_path) as f:
		manifest = addonHandler.AddonManifest(f)
	dest = os.path.join(addon.path, "buildVars.py")
	if os.path.exists(dest):
		# Translators: message to user.
		msg = _("Warning: buildVars.py already exists. Do you want to replace it?")
		if gui.messageBox(msg, dialogTitle, wx.YES | wx.NO) == wx.NO:
			return

	default_vars = {
		"name": "addonTemplate",
		"summary": "Add-on user visible name",
		"description": """Description for the add-on. It can span multiple lines.""",
		"version": "x.y",
		"author": str("name <name@domain.com>"),
		"url": None,
		"docFileName": "readme.html",
		"minimumNVDAVersion": None,
		"lastTestedNVDAVersion": None,
		"updateChannel": None
	}
	vars = {}
	vars.update(_buildVarsStrings)
	vars.update(default_vars)
	for var in manifest:
		if manifest[var] is None:
			continue
		if type(manifest[var]) == tuple:
			tempList = [str(x) for x in manifest[var]]
			vars[var] = ".".join(tempList)
			continue
		vars[var] = manifest[var]
	buildVars = buildVars_template.format(**vars)
	buildVars = buildVars.replace("\"None\"", "None")
	buildVars = buildVars.replace("_(\"\"\"None\"\"\")", "None")
	with codecs.open(dest, "w", "utf-8") as f:
		f.write(buildVars)
	# Translators message to user to report buildVars.py has been created
		msg = _("buildVars.py file created")
	gui.messageBox(msg, dialogTitle, wx.OK)
	# clean up
	clean(addon)


class ToolsForAddonDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	_instance = None
	title = None
	# help in the user manual.
	helpObj = getHelpObj("hdr22")

	def __new__(cls, *args, **kwargs):
		if ToolsForAddonDialog._instance is not None:
			return ToolsForAddonDialog._instance
		return super(ToolsForAddonDialog, cls).__new__(cls, *args, **kwargs)

	def __init__(self, parent, addonsList):
		if ToolsForAddonDialog._instance is not None:
			return
		ToolsForAddonDialog._instance = self
		# Translators: This is the title of the dialog
		dialogTitle = _("Tools for add-on development")
		title = ToolsForAddonDialog.title = makeAddonWindowTitle(dialogTitle)
		super(ToolsForAddonDialog, self).__init__(
			parent, -1, title, style=wx.CAPTION | wx.CLOSE_BOX | wx.TAB_TRAVERSAL)
		self.addonsList = addonsList
		languageNames = languageHandler.getAvailableLanguages()
		self.languages = {x[0]: x[1] for x in languageNames}
		self.doGui()

	@classmethod
	def getAddonsList(self):
		from locale import strxfrm
		return sorted(addonHandler.getAvailableAddons(), key=lambda a: strxfrm(a.manifest['summary']))

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# the addons list
		# Translators: This is a label appearing on Convert to HTML dialog.
		labelText = _("&Add-ons:")
		addonNamesList = [
			"%s %s" % (addon.manifest["summary"], addon.manifest["version"]) for addon in self.addonsList]
		self.addonsListBox = sHelper.addLabeledControl(
			labelText, wx.ListBox, id=wx.ID_ANY, name="addons", choices=addonNamesList)
		self.addonsListBox.SetSelection(0)
		self.bindHelpEvent(getHelpObj("hdr22"), self.addonsListBox)
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: this is a label appearing on tools for add-on dialog
		updateVersionButton = bHelper.addButton(
			# Translators: this is a label appearing on tools for add-on dialog
			self, label=_("Update add-on &version"))
		self.bindHelpEvent(getHelpObj("hdr22-2"), updateVersionButton)
		updateManifestIniButton = bHelper.addButton(
			self,
			# Translators: this is a label appearing on tools for add-on dialog
			label=_("&Update manifest.ini file"))
		self.bindHelpEvent(getHelpObj("hdr22-3"), updateManifestIniButton)
		createPOTFileButton = bHelper.addButton(
			self,
			# Translators: this is a label appearing on tools for add-on dialog
			label=_("Create P&OT file"))
		self.bindHelpEvent(getHelpObj("hdr22-6"), createPOTFileButton)
		prepareAddonButton = bHelper.addButton(
			self,
			# Translators: this is a label appearing on tools for add-on dialog
			label=_("&Prepare addon"))
		self.bindHelpEvent(getHelpObj("hdr22-7"), prepareAddonButton)
		sHelper.addItem(bHelper)
		# Translators: This is a label appearing on Convert to HTML dialog.
		labelText = _("&Languages:")
		langs = []
		self.languagesListBox = sHelper.addLabeledControl(
			labelText, wx.ListBox, id=wx.ID_ANY, name="languages", choices=langs)
		self.updateLanguagesListBox()
		self.bindHelpEvent(getHelpObj("hdr22-4"), self.languagesListBox)
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)

		createLocaleManifestIniButton = bHelper.addButton(
			# Translators: this is a label appearing on tools for add-on dialog
			self, label=_("Create &localization manifest.ini file"))
		self.bindHelpEvent(getHelpObj("hdr22-4"), createLocaleManifestIniButton)
		createHTMLDocumentationButton = bHelper.addButton(
			# Translators: this is a label appearing on tools for add-on dialog
			self, label=_("Create &HTML documentation files"))
		self.bindHelpEvent(getHelpObj("hdr22-5"), createHTMLDocumentationButton)
		createBuildVarsFileButton = bHelper.addButton(
			# Translators: this is a label appearing on tools for add-on dialog
			self, label=_("Create &buildVars file"))
		self.bindHelpEvent(getHelpObj("hdr22-1"), createBuildVarsFileButton)
		exploreAddonFolderButton = bHelper.addButton(
			# Translators: this is a label appearing on tools for add-on dialog
			self, label=_("&Explore add-on folder"))
		self.bindHelpEvent(getHelpObj("hdr22-8"), exploreAddonFolderButton)
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		cancelButton = bHelper.addButton(self, id=wx.ID_CANCEL)
		mainSizer.Add(
			sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# Events
		self.addonsListBox.Bind(wx.EVT_LISTBOX, self.onSelectAddon)
		cancelButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		createBuildVarsFileButton.Bind(
			wx.EVT_BUTTON, self.onCreateBuildVarsFileButton)
		updateManifestIniButton.Bind(wx.EVT_BUTTON, self.onUpdateManifestIniButton)
		createLocaleManifestIniButton.Bind(
			wx.EVT_BUTTON, self.onCreateLocaleManifestIniButton)
		createHTMLDocumentationButton.Bind(
			wx.EVT_BUTTON, self.oncreateHTMLDocumentationButton)
		createPOTFileButton.Bind(wx.EVT_BUTTON, self.oncreatePOTFileButton)
		prepareAddonButton.Bind(wx.EVT_BUTTON, self.onPrepareAddonButton)
		exploreAddonFolderButton.Bind(wx.EVT_BUTTON, self.onExploreAddonFolderButton)
		updateVersionButton.Bind(wx.EVT_BUTTON, self.onUpdateVersionButton)
		self.SetEscapeId(wx.ID_CANCEL)

	def updateLanguagesListBox(self):
		index = self.addonsListBox.GetSelection()
		addon = self.addonsList[index]
		localeLanguages = getLocaleLanguages(addon)
		# choice = [self.languages[x] for x in self.localeLanguages]
		choice = []
		self.localeLanguages = []
		for lang in localeLanguages:
			langName = self.languages[lang] if lang in self.languages else lang
			choice.append(langName)
			self.localeLanguages.append(lang)
		self.localeLanguages .append("all")
		choice.append(_("All"))
		self.languagesListBox.Clear()
		self.languagesListBox.AppendItems(choice)
		if len(choice):
			self.languagesListBox.SetSelection(0)

	def Destroy(self):
		ToolsForAddonDialog._instance = None
		super(ToolsForAddonDialog, self).Destroy()

	def onSelectAddon(self, event):
		self.updateLanguagesListBox()
		event.Skip()

	def onCreateBuildVarsFileButton(self, event):
		index = self.addonsListBox.GetSelection()
		addon = self.addonsList[index]
		_createBuildVarsFile(addon)

	def onUpdateManifestIniButton(self, event):
		index = self.addonsListBox.GetSelection()
		addon = self.addonsList[index]
		_makeMainManifestIni(addon)

	def onCreateLocaleManifestIniButton(self, event):
		index = self.addonsListBox.GetSelection()
		addon = self.addonsList[index]
		index = self.languagesListBox.GetSelection()
		lang = self.localeLanguages[index]
		_makeLocaleManifestIni(addon, lang)

	def oncreateHTMLDocumentationButton(self, event):
		index = self.addonsListBox.GetSelection()
		addon = self.addonsList[index]
		index = self.languagesListBox.GetSelection()
		lang = self.localeLanguages[index]
		_makeHTML(addon, lang)
		if self.languagesListBox.Count > 1:
			self.languagesListBox.SetFocus()
		else:
			self.addonsListBox.SetFocus()

	def oncreatePOTFileButton(self, event):
		index = self.addonsListBox.GetSelection()
		addon = self.addonsList[index]
		_generatePOTFile(addon)

	def onPrepareAddonButton(self, event):
		index = self.addonsListBox.GetSelection()
		addon = self.addonsList[index]
		_prepareAddon(addon)

	def onExploreAddonFolderButton(self, event):
		index = self.addonsListBox.GetSelection()
		addon = self.addonsList[index]
		import subprocess
		path = addon.path
		cmd = "explorer \"{path}\"" .format(path=path)
		wx.CallLater(300, subprocess.call, cmd, shell=True)
		self.Close()

	def updateAddonVersion(self, addon, oldVersion, newVersion):
		# Translators: title of dialog
		dialogTitle = _("Update add-on version")
		buildVarsFile = os.path.join(addon.path, "buildVars.py")
		if not os.path.exists(buildVarsFile):
			gui.messageBox(
				# Translators: no comment
				_("Error: buildVars.py file is not found"),
				dialogTitle, wx.OK)
			return
		buildVarsList = []
		buildVars = codecs.open(buildVarsFile, "r", "utf_8", errors="replace")
		for line in buildVars:
			buildVarsList.append(line)
		buildVars.close()
		match = "\"addon_version\""
		found = False
		for line in buildVarsList:
			if match in line:
				found = True
				break
		if not found:
			gui.messageBox(
				# Translators: message to user add-on version line not found
				_("Error: buildVars.py file has no add-on version line"),
				dialogTitle, wx.OK)
			return
		index = buildVarsList.index(line)
		buildVarsList[index] = line.replace(oldVersion, newVersion)
		dest = codecs.open(buildVarsFile, "w", "utf_8", errors="replace")
		for line in buildVarsList:
			dest.write(line)
		dest.close()
		# Translators: message to user add-on version has been updated.
		gui.messageBox(
			# Translators: message to user  updating add-on's version
			# of buildVars.py file.
			_("Version of buildVars.py file has been updated"),
			dialogTitle,
			wx.OK)

	def onUpdateVersionButton(self, evt):
		index = self.addonsListBox.GetSelection()
		addon = self.addonsList[index]
		# Translators: title of dialog
		dialogTitle = _("Update add-on version")
		sys.path.append(addon.path)
		try:
			import buildVars
			from importlib import reload
			reload(buildVars)
			del sys.path[-1]
		except ImportError:
			del sys.path[-1]
			# Translators: message to user.
			gui.messageBox(
				# Translators: message to user buildVars.py file is not found.
				_("Error: buildVars.py file is not found"),
				dialogTitle,
				wx.OK)
			return
		version = buildVars.addon_info["addon_version"]
		with wx.TextEntryDialog(
			self,
			# Translators: Message to show on the dialog.
			_("Entry add-on version:"),
			# Translators: This is a title of text control
			# in dialog box in Manage Symbols Dialog.
			_("Update add-on version"),
			"") as entryDialog:
			entryDialog.SetValue(version)
			if entryDialog.ShowModal() != wx.ID_OK:
				return
			newVersion = entryDialog.Value
			self.updateAddonVersion(addon, version, newVersion)

	@classmethod
	def run(cls):
		if isOpened(cls):
			return
		addonsList = cls.getAddonsList()
		if len(addonsList) == 0:
			ui.message(_("No add-on installed"))
			return
		gui.mainFrame.prePopup()
		d = cls(gui.mainFrame, addonsList)
		d.CentreOnScreen()
		d.Show()
		gui.mainFrame.postPopup()
