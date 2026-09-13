import os
import codecs
import gettext
from pathlib import Path

import markdown
from . import txt2tagsEx as txt2tags
from .typings import AddonInfo


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


def getStylesCss(baseDir, stylesCss):
	stylesCssFile = os.path.join(baseDir, stylesCss)
	if not os.path.exists(stylesCssFile):
		dirList = baseDir.split("\\")
		d = "\\".join(dirList[:-1])
		cssFile = os.path.join(d, stylesCss)
		stylesCssFile = os.path.join(baseDir, ".." , stylesCss)
	return stylesCssFile


def getStyles(baseDir, stylesCss):
	stylesCss = getStylesCss(baseDir, stylesCss)
	styles = ""
	if os.path.exists(stylesCss):
		with codecs.open(stylesCss, "r", "utf-8") as f:
			styles = """<style media="screen">"""
			styles = styles + "\n" +f.read()
			styles = styles + "\n" + "</style>"
	return styles


def writeHTMLFile(dest, htmlText, lang, title, cssFileName):
	cssFile =cssFileName if cssFileName is not None else "style.css"
	styles = getStyles(os.path.dirname(dest), cssFile)
	header =  HTML_HEADERS.format(
		lang=lang,
		dir="rtl" if lang in RTL_LANG_CODES else "ltr",
		title=title,
		styles=styles,
	)
	docText = header +"\n" + htmlText + "\n</html>\n"
	with codecs.open(dest, "w", "utf-8") as f:
		f.write(docText)
		#f.write(header)
		#f.write("\n" + htmlText)
		#f.write("\n</html>\n")


def getHTMLBody(dest):
	src = codecs.open( dest, "r","utf_8",errors="replace")
	startTag=  "</head>"
	endTag= "<!-- html code generated"
	appendLine = False
	text =[]
	for sLine in src:
		line = sLine.lower()
		startTagFound = line.find(startTag)
		endTagFound = line.find(endTag)
		if startTagFound >= 0:
			appendLine = True
			sLine = sLine[startTagFound+len(startTag):]
			text.append(sLine)
			continue
		elif endTagFound >=0:
			sLine = sLine[: endTagFound]
			text.append(sLine)
			break
		if appendLine:
			text.append(sLine)
	text.append("</body>")
	return "".join(text)

def getTitle(addon_info, moFile):
	if isinstance(moFile, str):
		moFile = Path(moFile)
	try:
		with moFile.open("rb") as f:
			_ = gettext.GNUTranslations(f).gettext
	except Exception:
		summary = addon_info["addon_summary"]
	else:
		summary = _(addon_info["addon_summary"])
	version = addon_info["addon_version"]
	title = f"{summary} {version}"
	return title
	



def t2t2html( #source, dest):
	source: str | Path,
	dest: str | Path,
	*,
	moFile: str | Path | None,
	addon_info: AddonInfo,
):

	txt2tags.exec_command_line([source,])
	htmlText = getHTMLBody(dest)
	if isinstance(source, str):
		source = Path(source)
	lang = source.parent.name.replace("_", "-")
	title = getTitle(addon_info, moFile)
	writeHTMLFile(dest, htmlText, lang, title, cssFileName = "style_t2t.css")

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








def md2html(
	source: str | Path,
	dest: str | Path,
	*,
	moFile: str | Path | None,
	mdExtensions: list[str],
	addon_info: AddonInfo,
):
	if isinstance(source, str):
		source = Path(source)
	if isinstance(dest, str):
		dest = Path(dest)
		title = getTitle(addon_info, moFile)
	lang = source.parent.name.replace("_", "-")
	headerDic = {
		'[[!meta title="': "# ",
		'"]]': " #",
	}
	if not mdExtensions:
		mdExtensions = markdown_extensions.copy()
	with source.open("r", encoding="utf-8") as f:
		mdText = f.read()
	for k, v in headerDic.items():
		mdText = mdText.replace(k, v, 1)
	htmlText = "<body>\n" +markdown.markdown(mdText, extensions=mdExtensions) +"\n</body>"
	writeHTMLFile(dest, htmlText, lang, title, cssFileName = "style.css")
