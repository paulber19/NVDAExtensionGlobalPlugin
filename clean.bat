echo off
call scons -c -s
del /s /q  *.pyc
del /s /q .sconsign.dblite
del *.pot


