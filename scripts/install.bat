@echo off
rem Install synthtwin on Windows from its offline bundle, then check this
rem computer (plans P4-D397 and P4-D416).
rem
rem The bundle is the only way synthtwin is installed (the owner's D3 of
rem 2026-10-20). Unzip it, then, in its folder, in a Command Prompt:
rem
rem   scripts\install.bat
rem
rem It takes no folder and needs no internet: it installs from the
rem bundle's own wheelhouse folder and nothing else.
rem
rem It is a .bat file and not a PowerShell script because many managed
rem Windows computers refuse to run PowerShell scripts.
rem
rem What it does, and nothing else: finds Python 3.11 or later (python,
rem then the py launcher), and says in plain words what to do when the
rem Python it finds is older; runs scripts\check_bundle.py with it, which
rem checks every file of the bundle against SHA256SUMS, every library
rem wheel against the hashes requirements-install.lock pins, that the
rem lock names no place to fetch from, and that the bundle was made for
rem this system and this Python, before anything is changed; makes a
rem fresh private environment, .venv, inside the bundle's folder,
rem clearing an earlier one there first (venv --clear), every time, since
rem pip skips a package whose version is already in place without
rem checking its bytes; installs the libraries from the bundle's
rem wheelhouse and nothing else (--no-index) with the hash of every file
rem checked (--require-hashes), then the synthtwin wheel found there with
rem --no-deps, both run with pip's --isolated and PIP_CONFIG_FILE set to
rem nul so no pip setting of this computer adds a place to fetch from;
rem and ends by running "synthtwin doctor", whose exit code it returns.
rem There is no other way in: when a file is missing, pip stops and so
rem does this script.
rem
rem Every message that names a path prints it through a FOR variable: a
rem FOR variable is put in after the line is read, so a folder whose name
rem holds an ampersand or a bracket is printed, never run (the Codex
rem review of lane TI, item 4).

setlocal
for %%I in ("%~dp0..") do set "HERE=%%~fI"
set "ENVDIR=%HERE%\.venv"
set "LOCK=%HERE%\requirements-install.lock"
set "WHEELS=%HERE%\wheelhouse"
set "PY="

if not "%~1"=="" goto :takes_no_folder

python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if not errorlevel 1 set "PY=python"
if defined PY goto :found_python
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if defined PY goto :found_python
python -c "import sys" >nul 2>&1
if not errorlevel 1 goto :too_old
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 goto :too_old
echo.
echo The installation stopped: no Python 3.11 or later was found on this
echo computer. Install the newest Python 3 from python.org (INSTALL.txt in
echo this folder says how), open a new Command Prompt window, and run this
echo script again.
exit /b 1

:found_python
%PY% -c "import sys; sys.exit(0 if sys.prefix == sys.base_prefix else 1)" >nul 2>&1
if errorlevel 1 goto :switched_on
if not exist "%LOCK%" goto :not_a_bundle
if not exist "%HERE%\scripts\check_bundle.py" goto :not_a_bundle

rem The bundle is checked before anything is changed, so a damaged or
rem wrong bundle leaves an earlier environment as it was.
%PY% -I "%HERE%\scripts\check_bundle.py" "%HERE%"
if errorlevel 1 goto :bundle_refused
set "WHEEL="
set "COUNT=0"
for %%W in ("%WHEELS%\synthtwin-*.whl") do call :count_wheel "%%~fW"
if not "%COUNT%"=="1" goto :wrong_wheels

for %%P in ("%ENVDIR%") do echo Installing synthtwin into %%~P
if exist "%ENVDIR%\pyvenv.cfg" for %%P in ("%ENVDIR%") do echo Replacing the earlier private environment in %%~P; a package you installed into it yourself must be installed again afterwards.
%PY% -m venv --clear "%ENVDIR%"
if errorlevel 1 goto :no_env
set "VPY=%ENVDIR%\Scripts\python.exe"

echo from the bundle's wheelhouse, with no internet
set "PIP_CONFIG_FILE=nul"
"%VPY%" -m pip install --isolated --disable-pip-version-check --no-index --find-links "%WHEELS%" --require-hashes -r "%LOCK%"
if errorlevel 1 goto :no_locked_wheels
"%VPY%" -m pip install --isolated --disable-pip-version-check --no-index --no-deps "%WHEEL%"
if errorlevel 1 goto :no_synthtwin_wheel

echo.
"%ENVDIR%\Scripts\synthtwin.exe" doctor
set "STATUS=%ERRORLEVEL%"
echo.
echo synthtwin is installed. Now, in this window, and in each new Command
echo Prompt window, switch its private environment on first, then type the
echo commands as INSTALL.txt writes them and as synthtwin prints them:
for %%P in ("%ENVDIR%\Scripts\activate.bat") do echo   "%%~P"
echo   synthtwin profile my-table.csv
exit /b %STATUS%

:count_wheel
set "WHEEL=%~1"
set /a COUNT+=1
goto :eof

:takes_no_folder
echo.
echo The installation stopped: this script takes no folder: it installs from
echo the wheelhouse folder of the bundle it sits in. Type scripts\install.bat
echo with nothing after it, in the bundle's folder, and run it again.
exit /b 1

:too_old
echo.
echo The installation stopped: the Python on this computer is older than
echo 3.11, and synthtwin needs Python 3.11 or later. Install the newest
echo Python 3 from python.org (INSTALL.txt in this folder says how), open a
echo new Command Prompt window, and run this script again.
exit /b 1

:switched_on
echo.
echo The installation stopped: the Python found belongs to a private
echo environment that is switched on in this Command Prompt window. Type
echo deactivate, press Enter, and run this script again.
exit /b 1

:not_a_bundle
echo.
echo The installation stopped: this folder is not a whole synthtwin bundle:
echo requirements-install.lock or scripts\check_bundle.py is missing. Download
echo the synthtwin bundle for this computer again, unzip it whole, and run
echo this script again from its folder.
exit /b 1

:bundle_refused
echo.
echo The installation stopped: the bundle's check above did not pass. Do
echo what it says, then run this script again.
exit /b 1

:no_env
echo.
echo The installation stopped: Python could not make the private environment
for %%P in ("%ENVDIR%") do echo in %%~P. Check that the bundle's folder is one you can save files in, then run this script again.
echo If a window still uses synthtwin, such as a Command Prompt with its
echo environment switched on or a notebook, close it first, then run this
echo script again.
exit /b 1

:wrong_wheels
echo.
for %%P in ("%WHEELS%") do echo The installation stopped: the folder %%~P must hold exactly one synthtwin wheel, synthtwin-VERSION-py3-none-any.whl, and it holds %COUNT%. Download the synthtwin bundle again, unzip it whole, and run this script again.
exit /b 1

:no_locked_wheels
echo.
echo The installation stopped: pip could not install the bundle's libraries
for %%P in ("%WHEELS%") do echo from %%~P with their hashes checked. Download the synthtwin bundle made
echo for this computer again, unzip it whole into a new folder, and run this
echo script again from there.
exit /b 1

:no_synthtwin_wheel
echo.
echo The installation stopped: pip could not install the synthtwin wheel in
for %%P in ("%WHEELS%") do echo %%~P. Download the synthtwin bundle again, unzip it whole into a new folder, and run this script again from there; if it stops here again, send the lines above to whoever looks after synthtwin.
exit /b 1
