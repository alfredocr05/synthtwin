@echo off
rem synthtwin.bat (plan P4-D483): the word synthtwin in the Command
rem Prompt window START-HERE opens where PowerShell is blocked. It runs
rem this folder's own python.exe with -I -B -X utf8 -m synthtwin and the
rem words typed after it, and gives back synthtwin's exit status.
"%~dp0python\python.exe" -I -B -X utf8 -m synthtwin %*
exit /b %ERRORLEVEL%
