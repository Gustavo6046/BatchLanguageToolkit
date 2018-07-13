@echo off
call webconfig.bat
bp websrc\brython_stdlib.js websrc\requirements.txt "%DEP_NLTK%" "%DEP_INFLECT%"
if exist brython_modules.js ren brython_modules.js %BUNDLENAME%.js