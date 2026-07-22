@echo off
REM Push updates to an ALREADY-published repo. (Use publish.bat only for the first-ever push.)
cd /d "%~dp0"

echo === Safety check ===
python scan.py || (pause & exit /b 1)

git add .
echo.
echo === Changes to be committed ===
git status --short
echo.
echo Review above - it must NOT contain .env or any key.
pause

set /p MSG="Commit message (e.g. Add docs wiki + two-layer screening): "
if "%MSG%"=="" set MSG=Update
git commit -m "%MSG%"
git push
echo.
echo Done. If push asked for a branch, run:  git push -u origin master   (or main)
pause
