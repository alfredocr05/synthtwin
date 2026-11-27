@echo off
rem START-HERE: double-click this file to use synthtwin (plan P4-D483).
rem It runs scripts\check_folder.py with this folder's own Python, which
rem checks every file of the folder against SHA256SUMS and then opens
rem the window synthtwin runs in; every decision is made there, in
rem Python. On a problem its words stay on the screen until a key is
rem pressed. START-HERE /check checks the folder and opens nothing.
rem Double-clicked inside the zip, without Extract All, it stands alone
rem in a temporary folder with no Python beside it, and says so.
rem The check guards against a folder damaged or changed by accident.
rem This file, the folder's Python and the check itself run before any
rem hash is compared, so a folder changed on purpose is caught only by
rem the zip's own SHA-256, compared before unzipping (INSTALL-WINDOWS.txt,
rem FIRST, CHECK THE ZIP). Every command names its program by full path.
setlocal
if exist "%~dp0python\python.exe" goto check
echo Unzip synthtwin's zip first (right-click it, Extract All), then double-click START-HERE in the unzipped folder.
if /i not "%~1"=="/check" pause
exit /b 1
:check
"%~dp0python\python.exe" -I -B "%~dp0scripts\check_folder.py" --start "%~dp0." %1
set "STATUS=%ERRORLEVEL%"
if not "%STATUS%"=="0" if /i not "%~1"=="/check" pause
exit /b %STATUS%
