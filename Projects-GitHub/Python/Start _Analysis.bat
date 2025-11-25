@echo off
title Market Analysis v2.3.3 - Easy Start
color 0A

echo ========================================
echo    MARKET ANALYSIS v2.3.3
echo    Easy One-Click Analysis
echo ========================================
echo.

REM Step 1: Open the form
echo Step 1: Opening the input form...
start "" "market_analysis_form.html"
echo Form opened in your browser!
echo.

REM Wait for user to complete form
echo ========================================
echo INSTRUCTIONS - FOLLOW THESE STEPS:
echo.
echo 1. Fill out the form in your browser
echo 2. Click the "Run Analysis" button
echo 3. Click "OK" on the popup message
echo.
echo 4. CLICK ON THIS GREEN WINDOW
echo    (to make it active)
echo.
echo 5. Then press the SPACEBAR
echo.
echo ========================================
echo.
echo Waiting for you to complete the form...
pause

REM Step 2: Move JSON file from Downloads
echo.
echo ========================================
echo Working... Please wait...
echo ========================================
echo.
echo Step 2: Looking for your input file...
set "downloads=%USERPROFILE%\Downloads"
set "project=%~dp0"

REM Find the most recent JSON file in Downloads with "_input.json" suffix
for /f "delims=" %%F in ('dir /b /od "%downloads%\*_input.json" 2^>nul') do set "jsonfile=%%F"

if defined jsonfile (
    echo Found: %jsonfile%
    echo Moving file to project folder...
    move "%downloads%\%jsonfile%" "%project%%jsonfile%"
    echo File moved successfully!
) else (
    echo.
    echo ERROR: No JSON file found in Downloads folder.
    echo.
    echo Make sure you:
    echo 1. Filled out the form
    echo 2. Clicked "Run Analysis" button
    echo 3. Clicked "OK" on the popup
    echo.
    pause
    exit /b
)

REM Step 3: Run the Python analysis
echo.
echo ========================================
echo Step 3: Running Python analysis...
echo This may take 1-2 minutes...
echo ========================================
echo.
python market_analysis_v2.3.3.py

REM Step 4: Show results
echo.
echo ========================================
echo ANALYSIS COMPLETE!
echo ========================================
echo.
echo Opening output folder to show your reports...
start "" "%project%"

echo.
echo SUCCESS! Your analysis is ready.
echo Check the folder that just opened.
echo.
echo Press any key to close this window...
pause
```

3. **Paste into Notepad**

4. **File → Save As**
   - File name: `START_ANALYSIS.bat`
   - Save as type: **All Files (*.*)**
   - Save to: `C:\Users\Craig\OneDrive\Documents\market_analysis_v2.3.3`
   - Click **Yes** to replace

---

**After saving, go back to the Command Prompt window and type:**
```
START_ANALYSIS.bat