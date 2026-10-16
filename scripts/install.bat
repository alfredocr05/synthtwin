@echo off
rem Install synthtwin on Windows, then check this computer (plan P4-D397).
rem
rem Run it from a Command Prompt; it works on the synthtwin folder it sits in:
rem
rem   scripts\install.bat                  from this folder, over the internet
rem   scripts\install.bat WHEEL_FOLDER     with no internet, from a folder of
rem                                        wheels (see "Installing" in README.md)
rem
rem It is a .bat file and not a PowerShell script because many managed
rem Windows computers refuse to run PowerShell scripts.
rem
rem What it does, and nothing else: finds Python 3.10 or later (python,
rem then the py launcher); makes a fresh private environment, .venv, inside
rem the synthtwin folder, clearing an earlier one there first (venv
rem --clear), every time, since pip skips a package whose version is
rem already in place without checking its bytes; installs numpy and pandas
rem from requirements-install.lock with the hash of every file checked
rem (--require-hashes) -- given a wheel folder, from that folder and
rem nothing else (--no-index), then the synthtwin wheel found there with
rem --no-deps, the same two pip commands README.md gives by hand, run with
rem pip's --isolated and PIP_CONFIG_FILE set to nul so no pip setting of
rem this computer adds a place to fetch from; without one, the same locked,
rem hash-checked files over the internet and this folder itself, which
rem also runs the build backend pip fetches for it (not pinned by the
rem lock; plan P4-D397 states it) -- and ends by running "synthtwin
rem doctor", whose exit code it returns.
rem
rem Every message that names a path prints it through a FOR variable: a
rem FOR variable is put in after the line is read, so a folder whose name
rem holds an ampersand or a bracket is printed, never run (the Codex
rem review of lane TI, item 4).

setlocal
for %%I in ("%~dp0..") do set "HERE=%%~fI"
set "ENVDIR=%HERE%\.venv"
set "LOCK=%HERE%\requirements-install.lock"
set "WHEELS=%~1"
set "PY="

python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if not errorlevel 1 set "PY=python"
if defined PY goto :found_python
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if defined PY goto :found_python
echo.
echo The installation stopped: no Python 3.10 or later was found on this
echo computer. Install one (see "Before you start" in README.md), open a new
echo Command Prompt window, and run this script again.
exit /b 1

:found_python
%PY% -c "import sys; sys.exit(0 if sys.prefix == sys.base_prefix else 1)" >nul 2>&1
if errorlevel 1 goto :switched_on
if exist "%LOCK%" goto :found_lock
echo.
echo The installation stopped: requirements-install.lock is missing from
for %%P in ("%HERE%") do echo %%~P. Download the synthtwin folder again; the lock file is part of it.
exit /b 1

:found_lock
rem The wheel folder is checked before anything is changed, so a mistyped
rem folder leaves an earlier environment as it was.
set "WHEEL="
set "COUNT=0"
if "%WHEELS%"=="" goto :make_env
for %%I in ("%WHEELS%") do set "WHEELS=%%~fI"
if "%WHEELS:~-1%"=="\" set "WHEELS=%WHEELS:~0,-1%"
if not exist "%WHEELS%\" goto :no_wheel_folder
for %%W in ("%WHEELS%\synthtwin-*.whl") do call :count_wheel "%%~fW"
if not "%COUNT%"=="1" goto :wrong_wheels

:make_env
for %%P in ("%ENVDIR%") do echo Installing synthtwin into %%~P
if exist "%ENVDIR%\pyvenv.cfg" for %%P in ("%ENVDIR%") do echo Replacing the earlier private environment in %%~P; a package you installed into it yourself must be installed again afterwards.
%PY% -m venv --clear "%ENVDIR%"
if errorlevel 1 goto :no_env
set "VPY=%ENVDIR%\Scripts\python.exe"
if "%WHEELS%"=="" goto :from_folder

for %%P in ("%WHEELS%") do echo from the wheel folder %%~P, with no internet
set "PIP_CONFIG_FILE=nul"
"%VPY%" -m pip install --isolated --disable-pip-version-check --no-index --find-links "%WHEELS%" --require-hashes -r "%LOCK%"
if errorlevel 1 goto :no_locked_wheels
"%VPY%" -m pip install --isolated --disable-pip-version-check --no-index --no-deps "%WHEEL%"
if errorlevel 1 goto :no_synthtwin_wheel
goto :doctor

:from_folder
echo from this folder, fetching the locked, hash-checked numpy and pandas
"%VPY%" -m pip install --disable-pip-version-check --require-hashes -r "%LOCK%"
if errorlevel 1 goto :no_internet
"%VPY%" -m pip install --disable-pip-version-check --no-deps -e "%HERE%"
if errorlevel 1 goto :no_synthtwin

:doctor
echo.
"%ENVDIR%\Scripts\synthtwin.exe" doctor
set "STATUS=%ERRORLEVEL%"
echo.
echo synthtwin is installed. Now, in this window, and in each new Command
echo Prompt window, switch its private environment on first, then type the
echo commands as README.md writes them and as synthtwin prints them:
for %%P in ("%ENVDIR%\Scripts\activate.bat") do echo   "%%~P"
echo   synthtwin profile my-table.csv
exit /b %STATUS%

:count_wheel
set "WHEEL=%~1"
set /a COUNT+=1
goto :eof

:switched_on
echo.
echo The installation stopped: the Python found belongs to a private
echo environment that is switched on in this Command Prompt window. Type
echo deactivate, press Enter, and run this script again.
exit /b 1

:no_env
echo.
echo The installation stopped: Python could not make the private environment
for %%P in ("%ENVDIR%") do echo in %%~P. Check that the synthtwin folder is one you can save files in, then run this script again.
echo If a window still uses synthtwin, such as a Command Prompt with its
echo environment switched on or a notebook, close it first, then run this
echo script again.
exit /b 1

:no_wheel_folder
echo.
for %%P in ("%WHEELS%") do echo The installation stopped: there is no folder at %%~P. Run this script again naming the folder that holds the wheels you copied across.
exit /b 1

:wrong_wheels
echo.
for %%P in ("%WHEELS%") do echo The installation stopped: the folder %%~P must hold exactly one synthtwin wheel, synthtwin-VERSION-py3-none-any.whl, and it holds %COUNT%. Leave exactly one there and run this script again.
exit /b 1

:no_locked_wheels
echo.
echo The installation stopped: pip could not install numpy and pandas from
for %%P in ("%WHEELS%") do echo %%~P with their hashes checked. The folder must hold the files the
echo "pip download" command in README.md fetched, for this computer's Windows
echo and Python: fetch them again that way, then run this script again.
exit /b 1

:no_internet
echo.
echo The installation stopped: pip could not install numpy and pandas. Check
echo the internet connection and run this script again, or install from a
echo wheel folder instead (see "Installing" in README.md).
exit /b 1

:no_synthtwin_wheel
echo.
echo The installation stopped: pip could not install the synthtwin wheel in
for %%P in ("%WHEELS%") do echo %%~P. Put the synthtwin wheel from the release into the folder again, in place of this one, and run this script again; if it stops here again, send the lines above to whoever looks after synthtwin.
exit /b 1

:no_synthtwin
echo.
echo The installation stopped: pip could not install synthtwin itself from
echo this folder. Download the synthtwin folder again and run this script
echo again; if it stops here again, send the lines above to whoever looks
echo after synthtwin.
exit /b 1
