# -*- coding: UTF-8 -*-

# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

# Full getext (please don't change)
_ = lambda x : x

# Add-on information variables
addon_info = {
	# for previously unpublished addons, please follow the community guidelines at:
	# https://bitbucket.org/nvdaaddonteam/todo/raw/master/guideLines.txt
	# add-on Name, internal for nvda
	"addon_name" : "NVDAExtensionGlobalPlugin",
	# Add-on summary, usually the user visible name of the addon.
	# Translators: Summary for this add-on to be shown on installation and add-on information.
	"addon_summary" : _("NVDA global commands extension"),
	# Add-on description
	# Translators: Long description to be shown for this add-on on add-on information from add-ons manager
	"addon_description" : _("""This Module has been developed with the participation of Daniel Poiraud.
It is not compatible with versions of NVDA below to 2018.3.2.
It adds to NVDA:
1- The features
some features can be enabled or disabled individually.
* Display of the list of icons in the notification area ,
* Display of the windows list of running applications,
* Assistance in the composition of a symbol that is complex such as, for example, a a e related, a symbol power of 2
	and possibility to add its own categories and symbols,
* Extension of the functionality of the virtual buffer
	for browsers Mozilla Firefox, Microsoft Internet Explorer, Microsoft Edge, and Google Chrome:

	* new commands for navigation mode (paragraph, division, anchor, main landmark,
	* new types of elements for the dialog box opened by "NVDA+F7" (radio button, paragraph, frame, checkBox, etc) with the announcement of the number of items found,
	* commands for the tables:
	announce the cells of a row /column , go to first/last cell in the row/current column, move the column/row preceding or following with announcement possible of the cells in that row/column,
	* announcement of the URL of the document,
	* navigation loop,
* Announcement of the function associated with editing commands
  style Copy, Paste, etc.,
* Announcement of the name of the folder pre-selected in the dialog boxes like "Open","Save", "Save as",etc.,
* display of information on the focused application:
	* the current profile configuration,
	* the name and version number of the application,
	* the add-on loaded for the application,
*	NVDA logs tools:
	* Opening the previous or current log,
	* copy of current Log path to the clipboard,

* history of voice speechs,
* renaming keyboard keys,
* selective announcement of  command keyboard keys ,
* simple countdown timer,
* display of visible elements making up the object in the foreground,
* fast switching of voice profile,
* remanence of the modifier keys,
* shutdown, restart or put on prolonged sleep the computer,
* control the master or NVDA volume:
	* mute or unmute volume  for the focused application,
	* establishment of the main Windows  or NVDA volume at the add-on loading,
* Tools for development of add-on
* supplements regarding the date and time: copy date and time to clipboard, report time with seconds


2- The options
* remove the ad from the description of the objects in the ribbons Windows,
* proclaim the word focused when deleting a word,
* automatically maximize the foreground window,
* announce punctuations and symbols when moving by word .

3-  The advanced options
* report, with a sound, the registration of an error in the NVDA log also for the final versions and release candidate of NVDA,
* Caption dialog title with the name of the module,
* Do not take account of the option to Announce the description of the object during the display of the dialog box style confirmation.


4- Various other elements
* presentation formatting of the text in a dialog box,
* sub-menus to explore the program folders or configuration,
* script to quickly restart NVDA.
"""),

	# version
	"addon_version" : "8.0",
	# Author(s)
	"addon_author" : "PaulBer19",
	# URL for the add-on documentation support
	"addon_url" : "paulber19@laposte.net",
	# Documentation file name
	"addon_docFileName" : "addonUserManual.html",
	# Minimum NVDA version supported (e.g. "2018.3")
	"addon_minimumNVDAVersion" : "2018.3.2",
	# Last NVDA version supported/tested (e.g. "2018.4", ideally more recent than minimum version)
	"addon_lastTestedNVDAVersion" : "2019.1.0",
	# Add-on update channel (default is stable or None)
	"addon_updateChannel" : None,
}


import os.path
# Define the python files that are the sources of your add-on.
# You can use glob expressions here, they will be expanded.
#pythonSources = []
mainPath = os.path.join("addon", "globalPlugins", "NVDAExtensionGlobalPlugin")
pythonSources = [
	os.path.join("addon", "*.py"),
	os.path.join(mainPath, "*.py"),
	os.path.join(mainPath, "activeWindowsListReport", "*.py"),
	os.path.join(mainPath, "browseModeEx", "*.py"),
	os.path.join(mainPath, "clipboardCommandAnnouncement", "*.py"),
	os.path.join(mainPath, "commandKeysSelectiveAnnouncement", "*.py"),
	os.path.join(mainPath, "ComplexSymbols", "*.py"),
	os.path.join(mainPath, "currentFolder", "*.py"),
	os.path.join(mainPath, "extendedNetUIHWND", "*.py"),
	os.path.join(mainPath, "keyboardKeyRenaming", "*.py"),
	os.path.join(mainPath, "minuteTimer", "*.py"),
	os.path.join(mainPath, "NVDALogs", "*.py"),
	os.path.join(mainPath, "reportFormatting", "*.py"),
	os.path.join(mainPath, "settings", "*.py"),
	os.path.join(mainPath, "shutdown", "*.py"),
	os.path.join(mainPath, "speechHistory", "*.py"),
	os.path.join(mainPath, "switchVoiceProfile", "*.py"),
	os.path.join(mainPath, "systemTrayIconsList", "*.py"),
	os.path.join(mainPath, "tools", "*.py"),
	os.path.join(mainPath, "userInputGestures", "*.py"),
	os.path.join(mainPath, "utils", "*.py"),
	os.path.join(mainPath, "volumeControl", "*.py"),
	os.path.join(mainPath, "winExplorer", "*.py"),
	]


# Files that contain strings for translation. Usually your python sources
i18nSources = pythonSources 

# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory, not to the root directory of your addon sources.
excludedFiles = []
