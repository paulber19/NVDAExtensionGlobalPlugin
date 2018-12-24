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
	"addon_description" : _("""This add-on adds to NVDA:
1- The following features (some of them can be enabled or disabled individually):
- Display of the list of icons in the notification area ,
- Display the window list of running applications,
- Assist in the composition of a symbol that is complex such as, for example, a a e related, a symbol power of 2 and option of adding their own categories and symbols,
- Extension of the functionality of the buffer virtual for the browsers Mozilla Firefox, Microsoft Internet Explorer, Microsoft Edge and Google Chrome:
	* new navigation commands to the buffer virtual (paragraph, division, anchor, main landmark),
	* new types of elements for the dialog box opened by "NVDA+F7" (title,reference, frame, button,etc.) with the announcement of the number of items found ,
	* scripts for the tables: announce of the cells in a row /column , go to first/last cell in the row/current column, move the column/row preceding or following with announcement possible of the cells in that row/column,
	* script to announce the URL of the document,
	* navigation in loop,
- Announcement of the function associated with editing commands like Copy, Paste, etc.,
- Announcement of the name of the folder pre-selected in the dialog boxes like "Open","Save", "Save as",etc,
- report or  display informations about focused application :
	* Announcement of the name and state of current voice profile ,
	* Announcement of the application's name and version number ,
	* announcement of name and version number of activated add-on,
- Opening of the old or current NVDA log and copy the path in the clipboard,
- speech history,
- presentation of the formatting of the text in a dialog box (disabled by default (NVDA command key NVDA+f),
- renaming  keyboard keys,
- selective announcement of  command keys,
- simple minute countdown timer,
- display visible items making up the foreground object,
- quick voice profils switching,
- modifier key remanence,
- shutdown , reboot or hibernate the computer,
- manage input gestures configured by user,
- main and NVDA volume control:
	* set on or off the volume for focused application,
	- establishe and set the level of main and NVDA volume at module start.
- conversion to html   of t2t or markdown add-on doc  files (for developer),
	2- The following options:
- remove the announcement of the object's description in the ribbons Windows,
- announce the focused word when deleting a word,
- automatically maximize the foreground window,
- say, systematically, the punctuations and symbols when you move by word (not enabled by default).
3- Advanced options:
- play sound on logged errors also for final or RC NVDA version,
- establishe and set automaticaly the level of main and NVDA volume at loading of module.
4- and various other items such as:
- sub-menus to explore the program folders or configuration,
- script to restart NVDA.
This Module has been developed with the participation of Daniel Poiraud. It is not compatible with versions of NVDA below the 2018.2.""" ),
	# version
	"addon_version" : "7.4.2",
	# Author(s)
	"addon_author" : u"PaulBer19",
	# URL for the add-on documentation support
	"addon_url" : "paulber19@laposte.net",
	# Documentation file name
	"addon_docFileName" : "addonUserManual.html",
	# Minimum NVDA version supported (e.g. "2018.3")
	"addon_minimumNVDAVersion" : "2018.2.1",
	# Last NVDA version supported/tested (e.g. "2018.4", ideally more recent than minimum version)
	"addon_lastTestedNVDAVersion" : 2019.1,
	# Add-on update channel (default is stable or None)
	"addon_updateChannel" : None,
	}


import os.path

# Define the python files that are the sources of your add-on.
# You can use glob expressions here, they will be expanded.
mainPath = os.path.join("addon", "globalPlugins", "NVDAExtensionGlobalPlugin")

pythonSources = [os.path.join("addon", "*.py"),
	os.path.join(mainPath, "*.py"),
]
dirs= os.listdir(mainPath)
for item in dirs:
	theFile = os.path.join(mainPath,item)
	if os.path.isdir(theFile):
		pythonSources .append(os.path.join(theFile, "*.py")
)
			
# Files that contain strings for translation. Usually your python sources
i18nSources = pythonSources
# for translation of manifest.ini
#i18nSources = pythonSources 



# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory, not to the root directory of your addon sources.
excludedFiles = []



