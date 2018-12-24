@echo off
del readme.md
call scons readme
del /s /q *.pyc
del .sconsign.dblite
