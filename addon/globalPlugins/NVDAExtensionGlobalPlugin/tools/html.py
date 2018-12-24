#NVDAExtensionGlobalPlugin/tools/html.py
# a part of NVDAExtensionGlobalPlugin add-on
#Copyright (C) 2016-2017 Paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import addonHandler
addonHandler.initTranslation()
from logHandler import log

import codecs
import os
from ctypes import *
import codecs
user32=windll.user32
import gui
import wx
from ..utils import isOpened, makeAddonWindowTitle
import addonHandler
import sys
import languageHandler

def getDocLanguages (addon):
	langs = []
	if "doc" in os.listdir(addon.path):
		docFolder = os.path.join(addon.path, "doc")
		dirs = os.listdir(docFolder)
		for item in dirs:
			f = os.path.join(docFolder, item)
			if os.path.isdir(f):
				langs.append(item)

	return langs

def getMmanifestInfos (addon, lang):
	path = addon.path
	manifest_path = os.path.join(path, addonHandler.MANIFEST_FILENAME)
	with open(manifest_path) as f:
		translatedInput = None
		translatedPath  = os.path.join("locale", lang)
		p = os.path.join(path, translatedPath, addonHandler.MANIFEST_FILENAME )
		if os.path.exists(p):
			log.debug("Using manifest translation from %s", p)
			translatedInput = open(p, 'r')
			try:
				return addonHandler.AddonManifest(f, translatedInput)
			except:
				# Translators: dialog title on errorr.
				dialogTitle = _("error")
				# Translators: message to the user on  getting addon manifest.
				gui.messageBox(_("Cannot get  add-on translated manifest of %s language")%lang, dialogTitle, wx.OK|wx.ICON_ERROR)
	return addonHandler.AddonManifest(manifest_path)






def writeHTMLFile(dest, htmlText, title, cssFile= "style.css"):
	lang = os.path.basename(os.path.dirname(dest)).replace('_', '-')
	with codecs.open(dest, "w", "utf-8") as f:
		f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" +
			"<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\"\n" +
			"    \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">\n" +
			"<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"%s\" lang=\"%s\">\n" % (lang, lang) +
			"<head>\n" +
			"<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\"/>\n" +
			"<link rel=\"stylesheet\" type=\"text/css\" href=\"../%s\" media=\"screen\"/>\n"%cssFile +
			"<title>%s</title>\n" % title +
			"</head>\n"
		)
		f.write(htmlText)
		f.write("\n</html>")



def md2html(source):
	curAddon = addonHandler.getCodeAddon()
	markdownPath= os.path.join(curAddon.path, "utilities")
	sys.path.append(markdownPath)
	import markdown
	del sys.path[-1]
	headerDic = {
		"[[!meta title=\"": "# ",
		"\"]]": " #",
	}
	with codecs.open(source, "r", "utf-8") as f:
		mdText = f.read()
		for k, v in headerDic.iteritems():
			mdText = mdText.replace(k, v, 1)
		htmlText = markdown.markdown(mdText)
	htmlText = "<body>\n" +htmlText + "\n</body>"
	return htmlText
	

def getHTMLBody(dest):
	src = codecs.open( dest, "r","utf_8",errors="replace")
	startTag=  "</head>"
	endTag= "<!-- html code generated"
	appendLine = False
	text =[]
	for sLine in src:
		if sLine[:len(startTag)].lower() ==  startTag:
			appendLine = True
			sLine= sLine[len(startTag):]
		elif sLine[:len(endTag)].lower() == endTag:
			break
		if appendLine and not sLine.isspace():
			text.append(sLine)
	text.append("</body>")
	return"".join(text[:])

def t2t2html(source, dest):
	curAddon = addonHandler.getCodeAddon()
	utilitiesPath= os.path.join(curAddon.path, "utilities")
	sys.path.append(utilitiesPath)
	import txt2tagsEx
	del sys.path[-1]
	txt2tagsEx.exec_command_line(["%s" %(source)])
	htmlText = getHTMLBody(dest)
	return htmlText
def makeHTML(addon, langs = None):
	cssFile = None
	if "doc" not in os.listdir(addon.path):
		gui.messageBox(_("doc folder is not present"), "Error",wx.OK|wx.ICON_ERROR)
		return
	docFolder = os.path.join(addon.path, "doc")
	dirList = os.listdir(docFolder)
	# search for .css file
	for f in dirList:
		if os.path.isdir(f):
			continue
		ext = f.split(".")[-1].lower()
		if ext == "css":
			cssFile = f
			break
	if cssFile is None:
		gui.messageBox(_("The cssstyle  file is not present in doc folder"), _("Warning"), wx.OK|wx.ICON_WARNING)		
	
	dirs = []
	if langs is None:
		for item in dirList:
			theDir = os.path.join(docFolder,item)
			if os.path.isdir(theDir):
				dirs.append(theDir)
	else:
		for item in langs:
			theDir = os.path.join(docFolder,item)
			dirs.append(theDir)
	
	n= 0
	for d in dirs:
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
			dest = os.path.join(d, base+".html")
			manifest = getMmanifestInfos (addon, lang)
			title="%s %s"%(manifest["summary"], manifest["version"])
			if ext == "t2t":
				htmlText = t2t2html(theFile, dest) 
				#writeHTMLFile(dest, htmlText, title, cssFile)
				n= n+1
			elif ext == "md":
				htmlText = md2html(theFile) 
				writeHTMLFile(dest, htmlText, title, cssFile)
				n= n+1
	if len(langs) == 1:
		# Translators: title of end of convertion dialog.
		dialogTitle = _("End's conversion  of doc files of %s folder")%lang
	else:
		# Translators: title of end of convertion dialog.
		dialogTitle = _("End's conversion  of all documentation  files")
	if n== 0:
		gui.messageBox(_("No html file converted"),dialogTitle, wx.OK)
	elif n== 1:
		gui.messageBox(_("one file converted"), dialogTitle, wx.OK)
	elif  n>1:
		gui.messageBox(_("%s files converted") %n, dialogTitle,wx.OK)

class ConvertToHTMLDialog(wx.Dialog):
	_instance = None
	title = None
	
	def __new__(cls, *args, **kwargs):
		if ConvertToHTMLDialog._instance is not None:
			return ConvertToHTMLDialog._instance
		return super(ConvertToHTMLDialog, cls).__new__(cls, *args, **kwargs)
	
	def __init__(self, parent, addonsList):
		if ConvertToHTMLDialog._instance is not None:
			return
		ConvertToHTMLDialog._instance = self
		# Translators: This is the title of Convert to HTML dialog.
		dialogTitle = _("Convert to HTML")
		title = ConvertToHTMLDialog.title = makeAddonWindowTitle(dialogTitle)
		super(ConvertToHTMLDialog, self).__init__(parent,-1,title, style = wx.CAPTION|wx.CLOSE_BOX|wx.TAB_TRAVERSAL)
		self.addonsList = addonsList
		languageNames = languageHandler.getAvailableLanguages()
		self.languages = {x[0]: x[1] for x in languageNames}
		self.doGui()
		
	
	@classmethod
	def getAddonsList(self):
		return [addon for addon in addonHandler.getAvailableAddons() ]

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# the addons list
		# Translators: This is a label appearing on Convert to HTML dialog.
		labelText=_("&Add-ons:")
		addonNamesList = [addon.manifest["summary"] for addon in self.addonsList]
		self.addonsListBox =sHelper.addLabeledControl(labelText, wx.ListBox, id = wx.ID_ANY, name= "addons",choices = addonNamesList)
		self.addonsListBox.SetSelection(0)
		# Translators: This is a label appearing on Convert to HTML dialog.
		labelText=_("&Languages:")
		langs = []
		self.languagesListBox =sHelper.addLabeledControl(labelText, wx.ListBox,id = wx.ID_ANY, name= "languages",choices = langs)
		self.updateLanguagesListBox()

		
		bHelper = sHelper.addDialogDismissButtons(gui.gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		# Translators:  this is a label appearing on Convert to HTML dialog.
		convertButton= bHelper.addButton(self, label  = _("Con&vert"))
		convertButton.SetDefault()
		# Translators:  this is a label appearing on Convert to HTML dialog.
		convertAllButton= bHelper.addButton(self, label  = _("Conver&t all"))
		cancelButton= bHelper.addButton(self, id = wx.ID_CANCEL)
		mainSizer.Add(sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# Events
		self.addonsListBox.Bind(wx.EVT_LISTBOX, self.onSelectAddon)
		cancelButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		convertButton.Bind(wx.EVT_BUTTON, self.onConvertButton)
		convertAllButton.Bind(wx.EVT_BUTTON, self.onConvertAllButton)
		self.SetEscapeId(wx.ID_CANCEL)
	
	def updateLanguagesListBox(self):
		index = self.addonsListBox.GetSelection()
		addon = self.addonsList[index]
		self.docLanguages = getDocLanguages(addon)
		choice = [self.languages[x] for x in self.docLanguages]
		self.languagesListBox.Clear()
		self.languagesListBox.AppendItems(choice)
		if len(choice):
			self.languagesListBox.SetSelection(0)
	
	def Destroy(self):
		ConvertToHTMLDialog._instance = None
		super(ConvertToHTMLDialog, self).Destroy()
	
	def onSelectAddon(self, event):
		self.updateLanguagesListBox()
		event.Skip()
	def onConvertButton(self, event):
		index = self.addonsListBox.GetSelection()
		addon = self.addonsList[index]
		index = self.languagesListBox.GetSelection()
		lang = self.docLanguages[index]
		makeHTML(addon,[lang,])
		if  self.languagesListBox.Count>1:
			self.languagesListBox.SetFocus()
		else:
			self.addonsListBox.SetFocus()
			
	def onConvertAllButton(self, event):
		index = self.addonsListBox.GetSelection()
		addon = self.addonsList[index]
		makeHTML(addon,self.docLanguages)
		self.addonsListBox.SetFocus()
	
	@classmethod
	def run(cls):
		if isOpened(cls):
			return

		gui.mainFrame.prePopup()		
		addonsList = cls.getAddonsList()
		if len(addonsList) == 0:
			speech.speakMessage (_("No add-on installed"))
			return
		d =   cls(gui.mainFrame, addonsList)
		d.Center(wx.BOTH | wx.CENTER_ON_SCREEN)
		d.Show()
		gui.mainFrame.postPopup()		

