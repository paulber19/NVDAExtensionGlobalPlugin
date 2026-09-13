# globalPlugins\NVDAExtensionGlobalPlugin\tools\site_scons\site_tools\NVDATool\typings.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2026 Paulber19
# This file is covered by the GNU General Public License.

# This code comes from NVDA addon template source (copyright NVAccess)

from typing import TypedDict, Protocol


class AddonInfo(TypedDict):
	addon_name: str
	addon_summary: str
	addon_description: str
	addon_version: str
	addon_changelog: str
	addon_author: str
	addon_url: str | None
	addon_sourceURL: str | None
	addon_docFileName: str
	addon_minimumNVDAVersion: str | None
	addon_lastTestedNVDAVersion: str | None
	addon_updateChannel: str | None
	addon_license: str | None
	addon_licenseURL: str | None


class BrailleTableAttributes(TypedDict):
	displayName: str
	contracted: bool
	output: bool
	input: bool


class SymbolDictionaryAttributes(TypedDict):
	displayName: str
	mandatory: bool


class SpeechDictionaryAttributes(TypedDict):
	displayName: str
	mandatory: bool


BrailleTables = dict[str, BrailleTableAttributes]
SymbolDictionaries = dict[str, SymbolDictionaryAttributes]
SpeechDictionaries = dict[str, SpeechDictionaryAttributes]


class Strable(Protocol):
	def __str__(self) -> str: ...  # noqa:E704
