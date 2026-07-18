@echo off
REM Whitelist sync: copies ONLY safe files from your live council-engine into this repo copy.
REM NEVER copies .env. Run whenever you've changed the engine.
cd /d "%~dp0"
set LIVE=..\..\council-engine

echo Syncing whitelisted files from live folder...
copy /y "%LIVE%\council.py"                 "llm-council\council.py"              >nul && echo   ok council.py
copy /y "%LIVE%\topics\sentiment-engine.md" "llm-council\topics\example-topic.md" >nul && echo   ok example topic
if exist "llm-council\.env" del "llm-council\.env"

echo.
echo === Safety check ===
python scan.py || (pause & exit /b 1)
echo.
echo Done. Review: git status   then: git add . ^&^& git commit -m "update" ^&^& git push
pause
