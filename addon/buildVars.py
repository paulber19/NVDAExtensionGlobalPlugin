# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

from site_scons.site_tools.NVDATool.typings import AddonInfo, BrailleTables, SymbolDictionaries, SpeechDictionaries

# Since some strings in "addon_info" are translatable,
# we need to include them in the .po files.
# Gettext recognizes only strings given as parameters to the "_" function.
# To avoid initializing translations in this module we simply roll our own "fake" "_" function
# which returns whatever is given to it as an argument.
from site_scons.site_tools.NVDATool.utils import _


# Add-on information variables
addon_info = AddonInfo(
	# add-on Name/identifier, internal for NVDA
	addon_name="NVDAExtensionGlobalPlugin",
	# Add-on summary, usually the user visible name of the addon.
	# Translators: Summary/title for this add-on
	# to be shown on installation and add-on information found in add-on store
	addon_summary=_("NVDA global commands extension"),
	# Add-on description
	# Translators: Long description to be shown for this add-on on add-on information from add-on store
	addon_description=_("""This add-on brings to NVDA a multitude of features which can be activated or deactivated individually depending on the need.
Here are a few:
* Display of the list of icons in the notification area or windows of applications launched,
* Help in the composition of a symbol that is complex such as, for example, a a e related, a symbol power of 2 and possibility to add its own categories and symbols,
* Extension of the functionality of the virtual buffer for browser:
 * new commands for navigation mode (paragraph, division, anchor, main landmark),
 * new types of elements for the dialog box opened by "NVDA+F7" (radio button, paragraph, frame, checkBox, etc) with the announcement of the number of items found,
 * option to browse in a loop in search of a next or previous item,
 * new scripts for table: cell/line/column announcement, move to the next or previous column / row with announcement of the cells composing it,
* intelligent announcement of the function of editing commands like Copy, cut or Paste and improvement of the NVDA base script which announces the text in the clipboard("NVDA+c" ),
* voice speechs's history,
* renaming keyboard keys,
* selective announcement of command keys,
* display of visible elements making up the object in the foreground and possibility to move to or click on the elements,
* quick voice profile switching,
* persistence of NVDA and modification keys and specific persistence for the gmail.com site,
* shutdown, restart or Hibernate the computer,
* management of input gestures configured by user,
* sound control: system/ NVDA/application's quick volume changes, audio split, temporary audio output device switching,
* user configurations management and NVDA restarting  with precise configuration,
* text analyser,
* quick add-ons activation / desactivation,
* Announcement or display of information about the application under focus, such as its version, the active configuration profile, loaded add-on,
* possible use of numeric keypad as standard numeric keypad,
* possibility of executing scripts from the "Input gestures" dialog,
* and more.

For the full list of the add-on's features and their description, see the user manual.
"""),
	# version
	addon_version="15.1",
	# Brief changelog for this version
	# It can span multiple lines
	# Translators: what's new content for the add-on version to be shown in the add-on store
		addon_changelog=_("""See add-on history."""),
	# Author(s)
	addon_author="PaulBer19 (paulber19@laposte.net",
	# URL for the add-on documentation support
	addon_url="https://github.com/paulber19/NVDAExtensionGlobalPlugin.git",
	# URL for the add-on repository where the source code can be found
	addon_sourceURL=None,
	# Documentation file name
	addon_docFileName="addonUserManual.html",
	# Minimum NVDA version supported (e.g. "2018.3")
	addon_minimumNVDAVersion="2025.1.0",
	# Last NVDA version supported/tested (e.g. "2018.4", ideally more recent than minimum version)
	addon_lastTestedNVDAVersion="2026.2.0",
	# Add-on update channel (default is None, denoting stable releases,
	# and for development releases, use "dev".)
	# Do not change unless you know what you are doing!
	addon_updateChannel=None,
	# Add-on license such as GPL 2
	addon_license=None,
	# URL for the license document the ad-on is licensed under
	addon_licenseURL=None,
)


# Define the python files that are the sources of your add-on.
# You can either list every file (using ""/") as a path separator,
# or use glob expressions.
# For example to include all files with a ".py" extension from the "globalPlugins" dir of your add-on
# the list can be written as follows:
# pythonSources = ["addon/globalPlugins/*.py"]
# For more information on SCons Glob expressions please take a look at:
# https://scons.org/doc/production/HTML/scons-user/apd.html
import os
mainPath = os.path.join("addon", "globalPlugins", "NVDAExtensionGlobalPlugin")
pythonSources: list[str] = [
	os.path.join("addon", "*.py"),
	os.path.join(mainPath, "*.py"),
	os.path.join(mainPath, "activeWindowsListReport", "*.py"),
	os.path.join(mainPath, "browseModeEx", "*.py"),
	os.path.join(mainPath, "clipboardCommandAnnouncement", "*.py"),
	os.path.join(
		mainPath, "commandKeysSelectiveAnnouncementAndRemanence", "*.py"),
	os.path.join(mainPath, "ComplexSymbols", "*.py"),
	os.path.join(mainPath, "currentFolder", "*.py"),
	os.path.join(mainPath, "computerTools", "*.py"),
	os.path.join(mainPath, "extendedNetUIHWND", "*.py"),
	os.path.join(mainPath, "keyboardKeyRenaming", "*.py"),
	os.path.join(mainPath, "minuteTimer", "*.py"),
	os.path.join(mainPath, "NVDALogs", "*.py"),
	os.path.join(mainPath, "reportFormatting", "*.py"),
	os.path.join(mainPath, "scripts", "*.py"),
	os.path.join(mainPath, "settings", "*.py"),
	os.path.join(mainPath, "speechHistory", "*.py"),
	os.path.join(mainPath, "switchVoiceProfile", "*.py"),
	os.path.join(mainPath, "systemTrayIconsList", "*.py"),
	os.path.join(mainPath, "textAnalysis", "*.py"),
	os.path.join(mainPath, "tools", "*.py"),
	os.path.join(mainPath, "updateHandler", "*.py"),
	os.path.join(mainPath, "userInputGestures", "*.py"),
	os.path.join(mainPath, "utils", "*.py"),
	os.path.join(mainPath, "WindowsExplorer", "*.py"),
	os.path.join(mainPath, "winExplorer", "*.py"),
]

# Files that contain strings for translation. Usually your python sources
i18nSources: list[str] = pythonSources + ["buildVars.py"]

# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory, not to the root directory of your addon sources.
# You can either list every file (using ""/") as a path separator,
# or use glob expressions.
excludedFiles: list[str] = []

# Base language for the NVDA add-on
# If your add-on is written in a language other than english, modify this variable.
# For example, set baseLanguage to "es" if your add-on is primarily written in spanish.
# You must also edit .gitignore file to specify base language files to be ignored.
baseLanguage: str = "en"

# Markdown extensions for add-on documentation
# Most add-ons do not require additional Markdown extensions.
# If you need to add support for markup such as tables, fill out the below list.
# Extensions string must be of the form "markdown.extensions.extensionName"
# e.g. "markdown.extensions.tables" to add tables.
markdownExtensions: list[str] = []

# Custom braille translation tables
# If your add-on includes custom braille tables (most will not), fill out this dictionary.
# Each key is a dictionary named according to braille table file name,
# with keys inside recording the following attributes:
# displayName (name of the table shown to users and translatable),
# contracted (contracted (True) or uncontracted (False) braille code),
# output (shown in output table list),
# input (shown in input table list).
brailleTables: BrailleTables = {}

# Custom speech symbol dictionaries
# Symbol dictionary files reside in the locale folder, e.g. `locale\en`, and are named `symbols-<name>.dic`.
# If your add-on includes custom speech symbol dictionaries (most will not), fill out this dictionary.
# Each key is the name of the dictionary,
# with keys inside recording the following attributes:
# displayName (name of the speech dictionary shown to users and translatable),
# mandatory (True when always enabled, False when not).
symbolDictionaries: SymbolDictionaries = {}

# Custom speech dictionaries (distinct from symbol dictionaries above)
# Speech dictionary files reside in the speechDicts folder and are named `name.dic`.
# If your add-on includes custom speech (pronunciation) dictionaries (most will not), fill out this dictionary.
# Each key is the name of the dictionary,
# with keys inside recording the following attributes:
# displayName (name of the speech dictionary shown to users and translatable),
# mandatory (True when always enabled, False when not).
speechDictionaries: SpeechDictionaries = {}
