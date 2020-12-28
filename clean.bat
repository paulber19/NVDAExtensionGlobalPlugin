echo off
call scons -c -s
del /s /q  *.pyc
del /s /q .sconsign.dblite
del *.pot
rd /s  /q __pycache__
rd /s /q  .\site_scons\site_tools\gettexttool\__pycache__
