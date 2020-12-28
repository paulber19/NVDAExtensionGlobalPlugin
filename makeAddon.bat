;@echo off
if exist .\addon\buildVars.py (
	copy .\addon\buildVars.py .
	)

call scons -s
ren *.nvda-addon *.nvda-addonTMP
call scons -c
ren *.nvda-addonTMP *.nvda-addon 
del /s /q *.pyc > NUL
del .sconsign.dblite> NUL
rd /s  /q __pycache__
rd /s /q  .\site_scons\site_tools\gettexttool\__pycache__