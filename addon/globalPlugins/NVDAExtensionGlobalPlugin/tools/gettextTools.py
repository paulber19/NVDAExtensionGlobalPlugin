# globalPlugins\NVDAExtensionGlobalPlugin\tools\gettextTools.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 -2020 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


import addonHandler
import subprocess
import os
import glob
from ..utils.py3Compatibility import getCommonUtilitiesPath

addonHandler.initTranslation()

XGETTEXT_COMMON_ARGS = (
	"--msgid-bugs-address\"={gettext_package_bugs_address}\" "
	"--package-name=\"{gettext_package_name}\" "
	"--package-version=\"{gettext_package_version}\" "
	"-c -o \"{TARGET}\" -D \"{inputDirectory}\" {SOURCES}"
)


def getI18nSources(addon, buildVarsI18nSources):
	i18nSources = []
	for path in buildVarsI18nSources:
		pathList = path.split("\\")
		if pathList[0] == "addon":
			pathList = pathList[1:]
		p = os.path.join(addon.path, "\\".join(pathList))
		if "*" in pathList[-1]:
			files = glob.glob(p)
			i18nSources .extend(files)
		else:
			i18nSources .append(p)
	return i18nSources


def generatePotFile(
	addon, potFileName, buildVarsAddonInfo, buildVarsI18nSources):
	gettextVars = {
		'gettext_package_bugs_address': 'nvda-translations@freelists.org',
		'gettext_package_name': buildVarsAddonInfo['addon_name'],
		'gettext_package_version': buildVarsAddonInfo['addon_version']
	}
	addonPath = addon.path
	potFileDir = os.path.join(addonPath, "locale", "en")
	files = glob.glob(os.path.join(potFileDir, "*.pot"))
	for f in files:
		os.remove(f)

	if not os.path.exists(potFileDir):
		os.mkdir(potFileDir)
	potFile = os.path.join(potFileDir, potFileName)
	i18nSources = getI18nSources(addon, buildVarsI18nSources)
	if len(i18nSources) == 0:
		return -1
	gettextVars["TARGET"] = potFile
	gettextVars["inputDirectory"] = addonPath
	utilitiesPath = getCommonUtilitiesPath()
	xgettextPath = os.path.join(utilitiesPath, "xgettext.exe")
	sources = ""
	for item in i18nSources:
		f = item.replace(addon.path + "\\", "")
		sources = sources + " " + "\"%s\"" % f
	gettextVars["SOURCES"] = sources
	commandLine = xgettextPath + " " + XGETTEXT_COMMON_ARGS
	commandLine = commandLine.format(**gettextVars)
	p = subprocess.Popen(commandLine)
	retval = p.wait()
	return retval


def compilePoFiles(addon):
	utilitiesPath = getCommonUtilitiesPath()
	msgfmtPath = os.path.join(utilitiesPath, "msgfmt.exe")
	prefixe = "nvda"
	localeDir = os.path.join(addon.path, "locale")
	poFiles = []
	for root, directories, files in os.walk(localeDir):
		for filename in files:
			if os.path.isdir(filename):
				continue
			if not filename.endswith(".po"):
				continue
			poFiles.append(os.path.join(root, filename))
	count = 0
	for poFile in poFiles:
		moPath = os.path.split(poFile)[0]
		moFile = os.path.join(moPath, "%s.mo" % prefixe)
		if os.path.exists(moFile):
			os.remove(moFile)
		commandLine = [
			"\"%s\"" % msgfmtPath,
			"-o",
			"\"%s\"" % moFile,
			"\"%s\"" % poFile]
		commandLine = " ".join(commandLine)
		p = subprocess.Popen(commandLine)
		retval = p.wait()
		if retval == 0:
			count += 1
	return (count, len(poFiles))
