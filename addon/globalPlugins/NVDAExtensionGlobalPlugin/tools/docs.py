# globalPlugins\NVDAExtensionGlobalPlugin\tools\docs.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2026 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from logHandler import log
import os
import threading
import codecs
import sys
_curAddon = addonHandler.getCodeAddon()
sharedPath = os.path.join(_curAddon.path, "shared")
sys.path.append(sharedPath)
from negp_messages import alert
del sys.path[-1]
sysPath = list(sys.path)
from ..utils.py3Compatibility import getCommonUtilitiesPath
sys.path.append(getCommonUtilitiesPath())
import txt2tags
sys.path = list(sysPath)

import markdown
addonHandler.initTranslation()
_mdStyleCssName = "style.css"
_t2tStyleCssName = "style_t2t.css"


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
				alert(
					# Translators: message to the user on getting addon manifest.
					_("Cannot get add-on translated manifest of %s language") % lang,
					dialogTitle,
				)
	return addonHandler.AddonManifest(manifest_path)


HTML_HEADERS = """
<!DOCTYPE html>
<html lang="{lang}" dir="{dir}">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
{styles}
</head>
""".strip()

RTL_LANG_CODES = frozenset({"ar", "fa", "he"})


def writeHTMLFile(dest, htmlText, title, styles):
	lang = os.path.basename(os.path.dirname(dest)).replace('_', '-')
	header = HTML_HEADERS.format(
		lang=lang,
		dir="rtl" if lang in RTL_LANG_CODES else "ltr",
		title=title,
		styles=styles,
	)
	docText = header + "\n" + htmlText + "\n</html>\n"
	with codecs.open(dest, "w", "utf-8") as f:
		f.write(docText)


markdown_extensions = [
	"abbr",
	"admonition",
	"attr_list",
	"def_list",
	# "extra",
	"fenced_code",
	"footnotes",
	"legacy_attrs",
	"legacy_em",
	"md_in_html",
	"meta",
	"nl2br",
	"sane_lists",
	"smarty",
	"tables",
	"toc",
	"wikilinks",
]


def md2html(source, mdExtensions):
	headerDic = {
		"[[!meta title=\"": "# ",
		"\"]]": " #",
	}
	if not mdExtensions:
		mdExtensions = markdown_extensions
	with codecs.open(source, "r", "utf-8") as f:
		mdText = f.read()
		for k, v in headerDic.items():
			mdText = mdText.replace(k, v, 1)
		htmlText = markdown.markdown(mdText, extensions=mdExtensions)
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
	try:
		os.remove(dest)
	except Exception:
		pass
	log.debug("converting t2t file: %s" % source)
	cmd = [source,]
	th = threading.Thread(
		target=txt2tags.exec_command_line,
		args=(cmd,)
	)
	th.start()
	th.join()
	if os.path.exists(dest):
		# we don't want the footer
		htmlText = getHTMLBody(dest)
		os.remove(dest)
	else:
		log.warning("cannot convert t2t file: %s" % source)
		return None
	return htmlText


def getStylesCss(fileDir, fileType="t2t"):
	# the default styles css files are in doc folder
	# but translators can adapte these files for convenience
	# so the file modified must be placed in the language folder.
	if fileType == "t2t":
		stylesCss = os.path.join(fileDir, _t2tStyleCssName)
		if not os.path.exists(stylesCss):
			stylesCss = os.path.join(fileDir, "..", _t2tStyleCssName)
	elif fileType == "md":
		stylesCss = os.path.join(fileDir, _mdStyleCssName)
		if not os.path.exists(stylesCss):
			stylesCss = os.path.join(fileDir, "..", _mdStyleCssName)
	return stylesCss


def getStyles(fileDir, fileType="t2t"):
	stylesCss = getStylesCss(fileDir, fileType=fileType)
	styles = ""
	if os.path.exists(stylesCss):
		with codecs.open(stylesCss, "r", "utf-8") as f:
			styles = """<style media="screen">"""
			styles = styles + "\n" + f.read()
			styles = styles + "\n" + "</style>"
	return styles


def generateHTMLFiles(addon, docDirs, mdExtensions):
	mdCount = 0
	t2tCount = 0
	filesCount = 0
	for d in docDirs:
		lang = d.split("\\")[-1]
		fileList = os.listdir(d)
		filesCount = len(fileList)
		for file in fileList:
			theFile = os.path.join(d, file)
			if not os.path.isfile(theFile):
				continue
			(base, ext) = os.path.splitext(file)
			ext = ext[1:]
			if ext not in ["md", "t2t"]:
				continue
			dest = os.path.join(d, base + ".html")
			manifest = getMmanifestInfos(addon, lang)
			title = "%s %s" % (manifest["summary"], manifest["version"])
			styles = getStyles(d, fileType=ext)
			if ext == "t2t":
				htmlText = t2t2html(theFile, dest)
				if htmlText is None:
					continue
				t2tCount += 1
			elif ext == "md":
				htmlText = md2html(theFile, mdExtensions)
				mdCount += 1
			writeHTMLFile(dest, htmlText, title, styles)
	return (filesCount, mdCount, t2tCount)
