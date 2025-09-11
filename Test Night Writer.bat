@echo off
title Night Writer - Test Optimized Version
echo ============================================
echo NIGHT WRITER - OPTIMIZED TEST
echo ============================================
echo.
echo This will test the optimized version that:
echo   - Only checks RECENT lines for rate limits
echo   - Does NOT send unnecessary commands
echo   - Works with existing Claude windows
echo.
echo INSTRUCTIONS:
echo 1. Make sure you have Claude Code running in a terminal
echo 2. The GUI will open with 2 buttons
echo 3. Click "REFRESH WINDOWS" to see terminals
echo 4. Select the terminal with Claude Code
echo 5. Click "START AUTOMATION"
echo 6. Watch - it should NOT send extra commands!
echo.
pause
python night_writer_simple.py