@echo off
setlocal enabledelayedexpansion

:: Configuration
set "APP_NAME=DeepSeekChat.exe"
set "REPO_URL=https://api.github.com/repos/LousyBook94/DeepSeek-Desktop/releases/latest"
set "VERSION_FILE=version.txt"
set "TEMP_DIR=%TEMP%\DeepSeekUpdate"
set "BACKUP_DIR=backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "MAX_RETRIES=10"

echo ==========================================
echo    ^>^> DeepSeek Desktop Auto-Updater ^<^<
echo ==========================================
echo.

:: Create temp directory
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

:: Step 1: Check if application is running and close it
echo [1/7] ^>^> Checking if %APP_NAME% is running...
tasklist /FI "IMAGENAME eq %APP_NAME%" 2>NUL | find /I /N "%APP_NAME%">NUL
if "%ERRORLEVEL%"=="0" (
    echo [*] Application is running. Closing it gracefully...
    taskkill /F /IM "%APP_NAME%" >NUL 2>&1
    timeout /t 3 /nobreak >NUL
    echo [+] Application closed successfully!
) else (
    echo [+] Application is not running.
)

:: Step 2: Get current version
echo.
echo [2/7] ^>^> Checking current version...
set "CURRENT_VERSION=0.0.0"
if exist "%VERSION_FILE%" (
    set /p CURRENT_VERSION=<"%VERSION_FILE%"
    echo [*] Current version: !CURRENT_VERSION!
) else (
    echo [!] No version file found. Assuming first installation!
)

:: Step 3: Fetch latest version with retry logic
echo.
echo [3/7] ^>^> Fetching latest release information...
set "RETRY_COUNT=0"

:fetch_release_info
set /a RETRY_COUNT+=1
echo [~] Attempt !RETRY_COUNT!/!MAX_RETRIES!: Fetching release info...

powershell -Command "try { $response = Invoke-RestMethod -Uri '%REPO_URL%' -TimeoutSec 30; $response | ConvertTo-Json -Depth 10 | Out-File -FilePath '%TEMP_DIR%\release_info.json' -Encoding UTF8; exit 0 } catch { Write-Host 'Error: ' $_.Exception.Message; exit 1 }" >NUL 2>&1

if !ERRORLEVEL! neq 0 (
    echo [-] Failed to fetch release information.
    if !RETRY_COUNT! lss !MAX_RETRIES! (
        echo [~] Retrying in 5 seconds...
        timeout /t 5 /nobreak >NUL
        goto fetch_release_info
    ) else (
        echo [X] Maximum retries reached. Update failed.
        goto cleanup_and_exit
    )
)

:: Parse latest version
for /f "tokens=*" %%i in ('powershell -Command "(Get-Content '%TEMP_DIR%\release_info.json' | ConvertFrom-Json).tag_name.TrimStart('v')"') do set "LATEST_VERSION=%%i"

echo [*] Latest version: !LATEST_VERSION!

:: Step 4: Compare versions
echo.
echo [4/7] ^>^> Comparing versions...

:: Use PowerShell to compare versions properly
powershell -Command "try { $current = [System.Version]'!CURRENT_VERSION!'; $latest = [System.Version]'!LATEST_VERSION!'; if ($current -ge $latest) { exit 0 } else { exit 1 } } catch { exit 1 }" >NUL 2>&1

if !ERRORLEVEL! equ 0 (
    echo [+] You already have the latest version ^(!CURRENT_VERSION!^)!
    echo [+] No update needed. You're all set!
    goto cleanup_and_exit
)

echo [!] Update available: !CURRENT_VERSION! --^> !LATEST_VERSION!

:: Step 5: Download latest release with retry logic
echo.
echo [5/7] ^>^> Downloading latest release...
set "RETRY_COUNT=0"

:download_release
set /a RETRY_COUNT+=1
echo [~] Attempt !RETRY_COUNT!/!MAX_RETRIES!: Downloading release...

powershell -Command "try { $release = Get-Content '%TEMP_DIR%\release_info.json' | ConvertFrom-Json; $asset = $release.assets | Where-Object { $_.name -like '*windows.zip' } | Select-Object -First 1; if ($asset) { Write-Host 'Downloading:' $asset.name; Invoke-WebRequest -Uri $asset.browser_download_url -OutFile '%TEMP_DIR%\update.zip' -TimeoutSec 120; Write-Host 'Download completed.'; exit 0 } else { Write-Host 'Windows release asset not found.'; exit 1 } } catch { Write-Host 'Download error:' $_.Exception.Message; exit 1 }"

if !ERRORLEVEL! neq 0 (
    echo [-] Download failed.
    if !RETRY_COUNT! lss !MAX_RETRIES! (
        echo [~] Retrying in 10 seconds...
        timeout /t 10 /nobreak >NUL
        goto download_release
    ) else (
        echo [X] Maximum retries reached. Update failed.
        goto cleanup_and_exit
    )
)

:: Verify download
if not exist "%TEMP_DIR%\update.zip" (
    echo [-] Error: Downloaded file not found.
    goto cleanup_and_exit
)

:: Step 6: Backup and extract with retry logic
echo.
echo [6/7] ^>^> Creating backup and installing update...
set "RETRY_COUNT=0"

:install_update
set /a RETRY_COUNT+=1
echo [~] Attempt !RETRY_COUNT!/!MAX_RETRIES!: Installing update...

:: Create backup
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
echo [*] Creating backup...
xcopy /E /I /H /Y "%APP_NAME%" "%BACKUP_DIR%\" >NUL 2>&1
if exist "injection" xcopy /E /I /H /Y "injection" "%BACKUP_DIR%\injection\" >NUL 2>&1
if exist "%VERSION_FILE%" copy "%VERSION_FILE%" "%BACKUP_DIR%\" >NUL 2>&1

:: Extract update
echo [*] Extracting update...
powershell -Command "try { Expand-Archive -Path '%TEMP_DIR%\update.zip' -DestinationPath '%TEMP_DIR%\extracted' -Force; exit 0 } catch { Write-Host 'Extraction error:' $_.Exception.Message; exit 1 }" >NUL 2>&1

if !ERRORLEVEL! neq 0 (
    echo [-] Extraction failed.
    if !RETRY_COUNT! lss !MAX_RETRIES! (
        echo [~] Retrying in 5 seconds...
        timeout /t 5 /nobreak >NUL
        goto install_update
    ) else (
        echo [X] Maximum retries reached. Restoring backup...
        goto restore_backup
    )
)

:: Copy new files (preserve data folder)
echo [*] Installing new files...
if exist "%TEMP_DIR%\extracted\%APP_NAME%" (
    copy /Y "%TEMP_DIR%\extracted\%APP_NAME%" "." >NUL 2>&1
    if !ERRORLEVEL! neq 0 (
        echo [-] Failed to copy executable. Restoring backup...
        goto restore_backup
    )
)

if exist "%TEMP_DIR%\extracted\injection" (
    if exist "injection" rmdir /S /Q "injection" >NUL 2>&1
    xcopy /E /I /H /Y "%TEMP_DIR%\extracted\injection" "injection\" >NUL 2>&1
)

if exist "%TEMP_DIR%\extracted\deepseek.ico" copy /Y "%TEMP_DIR%\extracted\deepseek.ico" "." >NUL 2>&1

:: Update version file
echo !LATEST_VERSION! > "%VERSION_FILE%"

echo [+] Update installed successfully!
goto start_application

:restore_backup
echo [~] Restoring from backup...
if exist "%BACKUP_DIR%\%APP_NAME%" copy /Y "%BACKUP_DIR%\%APP_NAME%" "." >NUL 2>&1
if exist "%BACKUP_DIR%\injection" (
    if exist "injection" rmdir /S /Q "injection" >NUL 2>&1
    xcopy /E /I /H /Y "%BACKUP_DIR%\injection" "injection\" >NUL 2>&1
)
if exist "%BACKUP_DIR%\%VERSION_FILE%" copy /Y "%BACKUP_DIR%\%VERSION_FILE%" "." >NUL 2>&1
echo [+] Backup restored. Update failed.
goto cleanup_and_exit

:start_application
:: Step 7: Start application
echo.
echo [7/7] ^>^> Starting application...
if exist "%APP_NAME%" (
    start "" "%APP_NAME%"
    echo [+] %APP_NAME% started successfully!
    echo.
    echo ==========================================
    echo   *** UPDATE COMPLETED SUCCESSFULLY! ***
    echo   Version: !CURRENT_VERSION! --^> !LATEST_VERSION!
    echo   *** Enjoy your updated DeepSeek Desktop! ***
    echo ==========================================
) else (
    echo [-] Error: %APP_NAME% not found after update.
    goto restore_backup
)

:cleanup_and_exit
:: Cleanup
echo.
echo [*] Cleaning up temporary files...
if exist "%TEMP_DIR%" rmdir /S /Q "%TEMP_DIR%" >NUL 2>&1

echo.
echo Press any key to exit...
pause >NUL
exit /b 0