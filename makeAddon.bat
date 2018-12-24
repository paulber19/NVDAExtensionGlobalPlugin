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