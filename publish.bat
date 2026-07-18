@echo off
REM One-time publish helper for the ARIA repo. Requires Git: https://git-scm.com/download/win
cd /d "%~dp0"

echo === Safety check ===
python scan.py || (pause & exit /b 1)

git init
git add .
git status
echo.
echo Review the list above - it must NOT contain any .env or key.
pause
git commit -m "Initial release: ARIA - survivability-first algo-trading project + LLM Council engine"
echo.
echo ============================================================
echo  Now create the empty repo on GitHub:
echo    1. Go to github.com/new
echo    2. Name: ARIA   (Public, NO readme/license - we have them)
echo    3. Then run:
echo.
echo    git remote add origin https://github.com/agisoham/ARIA.git
echo    git push -u origin master
echo ============================================================
pause
