import addonHandler
addonHandler.initTranslation()
import sys
import subprocess
import os
import wx
import gui
import api
import glob

XGETTEXT_COMMON_ARGS = (
	"--msgid-bugs-address\"={gettext_package_bugs_address}\" "
	"--package-name=\"{gettext_package_name}\" "
	"--package-version=\"{gettext_package_version}\" "
	"-c -o \"{TARGET}\" -D \"{inputDirectory}\" {SOURCES}"
	)

def getI18nSources (addon, buildVarsI18nSources):
	i18nSources = []
	for path in buildVarsI18nSources :
		pathList = path.split("\\")
		if pathList[0] == "addon":
			pathList = pathList[1:]
		p =os.path.join(addon.path, "\\".join(pathList))
		if "*" in pathList[-1]:
			files = glob.glob(p)
			i18nSources .extend(files)
		else:
			i18nSources .append(p)
	return i18nSources 
def generatePotFile(addon, potFileName, buildVarsAddonInfo, buildVarsI18nSources):
	gettextVars={
		'gettext_package_bugs_address' : 'nvda-translations@freelists.org',
		'gettext_package_name' : buildVarsAddonInfo['addon_name'],
		'gettext_package_version' : buildVarsAddonInfo['addon_version']
	}
	addonPath = addon.path.encode("mbcs")
	potFileDir = os.path.join(addonPath, "locale", "en")
	files = glob.glob(os.path.join(potFileDir , "*.pot"))
	for f in files:
		os.remove(f)

	if not os.path.exists(potFileDir):
		os.mkdir(potFileDir)
	potFile = os.path.join(potFileDir,potFileName)
	i18nSources = getI18nSources(addon, buildVarsI18nSources)
	if len(i18nSources ) == 0:
		return -1
	gettextVars["TARGET"] = potFile
	gettextVars["inputDirectory"] = addonPath
	curAddon = addonHandler.getCodeAddon()
	xgettextPath = os.path.join(curAddon.path.encode("mbcs"), "utilities","xgettext.exe")
	sources = ""
	for item in i18nSources:
		f = item.replace(addon.path +"\\", "")
		sources = sources+ " " + "\"%s\""%f
	gettextVars["SOURCES"] = sources
	commandLine = xgettextPath + " " + XGETTEXT_COMMON_ARGS
	commandLine = commandLine.format(**gettextVars)
	p = subprocess.Popen(commandLine)
	retval = p.wait()
	return retval
