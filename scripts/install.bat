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
rem then the py launcher); makes a private environment, .venv, inside the
rem synthtwin folder; installs numpy and pandas from
rem requirements-install.lock with the hash of every file checked
rem (--require-hashes) -- given a wheel folder, from that folder and
rem nothing else (--no-index), then the synthtwin wheel found there with
rem --no-deps, the same two pip commands README.md gives by hand; without
rem one, the same locked, hash-checked files over the internet and this
rem folder itself -- and ends by running "synthtwin doctor", whose exit
rem code it returns.

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
if exist "%LOCK%" goto :found_lock
echo.
echo The installation stopped: requirements-install.lock is missing from
echo %HERE%. Download the synthtwin folder again; the lock file is part of it.
exit /b 1

:found_lock
echo Installing synthtwin into %ENVDIR%
if exist "%ENVDIR%\Scripts\python.exe" goto :have_env
%PY% -m venv "%ENVDIR%"
if errorlevel 1 goto :no_env
:have_env
set "VPY=%ENVDIR%\Scripts\python.exe"
if "%WHEELS%"=="" goto :from_folder

for %%I in ("%WHEELS%") do set "WHEELS=%%~fI"
if "%WHEELS:~-1%"=="\" set "WHEELS=%WHEELS:~0,-1%"
if not exist "%WHEELS%\" goto :no_wheel_folder
set "WHEEL="
set "COUNT=0"
for %%W in ("%WHEELS%\synthtwin-*.whl") do call :count_wheel "%%~fW"
if not "%COUNT%"=="1" goto :wrong_wheels
echo from the wheel folder %WHEELS%, with no internet
"%VPY%" -m pip install --disable-pip-version-check --no-index --find-links "%WHEELS%" --require-hashes -r "%LOCK%"
if errorlevel 1 goto :no_locked_wheels
"%VPY%" -m pip install --disable-pip-version-check --no-index --no-deps "%WHEEL%"
if errorlevel 1 goto :no_synthtwin
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
echo synthtwin is installed. Run it by its full path, for example:
echo   "%ENVDIR%\Scripts\synthtwin" profile my-table.csv
exit /b %STATUS%

:count_wheel
set "WHEEL=%~1"
set /a COUNT+=1
goto :eof

:no_env
echo.
echo The installation stopped: Python could not make the private environment
echo in %ENVDIR%.
exit /b 1

:no_wheel_folder
echo.
echo The installation stopped: there is no folder at %WHEELS%. Name the folder
echo that holds the wheels you copied across.
exit /b 1

:wrong_wheels
echo.
echo The installation stopped: the folder %WHEELS% must hold exactly one
echo synthtwin wheel, synthtwin-VERSION-py3-none-any.whl, and it holds %COUNT%.
exit /b 1

:no_locked_wheels
echo.
echo The installation stopped: pip could not install numpy and pandas from
echo %WHEELS% with their hashes checked. The folder must hold the files the
echo "pip download" command in README.md fetched, for this computer's Windows
echo and Python.
exit /b 1

:no_internet
echo.
echo The installation stopped: pip could not install numpy and pandas. Check
echo the internet connection, or install from a wheel folder instead (see
echo "Installing" in README.md).
exit /b 1

:no_synthtwin
echo.
echo The installation stopped: pip could not install synthtwin itself.
exit /b 1
