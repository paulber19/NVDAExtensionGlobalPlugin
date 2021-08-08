# globalPlugins\NVDAExtensionGlobalPlugin\tools\generate.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2021 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import codecs
import os

import gettext
addonHandler.initTranslation()


def generateManifest(dest, addonInfo, template):
	_ = ""
	manifest = template.format(**addonInfo)
	with codecs.open(dest, "w", "utf-8") as f:
		f.write(manifest)


def getTranslationsInstance(addon, language, domain='nvda'):
	localedir = os.path.join(addon.path, "locale")
	return gettext.translation(
		domain, localedir=localedir, languages=[language], fallback=True)


def getVariablesBetweenBrass(stringToFormat):
	vars = []
	for s in stringToFormat.split("{"):
		if "}" not in s:
			continue
		vars.append(s.split("}")[0])
	return vars


def generateTranslatedManifest(addon, addonInfos, language, template):
	_ = getTranslationsInstance(addon, language).gettext
	vars = {}
	translatedVars = {}
	allTranslated = True
	for var in getVariablesBetweenBrass(template):
		vars[var] = addonInfos[var]
		translatedVars[var] = _(addonInfos[var])
		if translatedVars[var] == vars[var]:
			allTranslated = False
	result = template.format(**translatedVars)
	dest = os.path.join(addon.path, "locale", language, "manifest.ini")
	with codecs.open(dest, "w", "utf-8") as f:
		f.write(result)
	return allTranslated
