@echo off
setlocal enabledelayedexpansion

:: Check for auto mode flag
set "AUTO_MODE=false"
if "%1"=="--auto" set "AUTO_MODE=true"

:: Configuration
set "APP_NAME=DeepSeekChat.exe"
set "REPO_URL=https://api.github.com/repos/LousyBook94/DeepSeek-Desktop/releases/latest"
set "VERSION_FILE=version.txt"
set "TEMP_DIR=%TEMP%\DeepSeekUpdate"
:: Create safe timestamp for backup directory
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do set "datestr=%%c%%a%%b"
for /f "tokens=1-3 delims=:." %%a in ('time /t') do set "timestr=%%a%%b%%c"
set "timestr=%timestr: =0%"
set "BACKUP_DIR=backup_%datestr%_%timestr%"
set "MAX_RETRIES=10"

echo ==========================================
echo    ^>^> DeepSeek Desktop Auto-Updater ^<^<
echo ==========================================
echo.

:: Create temp directory
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

:: Step 1: Check if application is running and close it
if "%AUTO_MODE%"=="false" echo [1/7] ^>^> Checking if %APP_NAME% is running...
tasklist /FI "IMAGENAME eq %APP_NAME%" 2>NUL | find /I /N "%APP_NAME%">NUL
if "%ERRORLEVEL%"=="0" (
    if "%AUTO_MODE%"=="false" echo [*] Application is running. Closing it gracefully...
    taskkill /F /IM "%APP_NAME%" >NUL 2>&1
    :: Wait longer for file handles to be released
    timeout /t 5 /nobreak >NUL
    :: Verify process is actually closed
    tasklist /FI "IMAGENAME eq %APP_NAME%" 2>NUL | find /I /N "%APP_NAME%">NUL
    if "!ERRORLEVEL!"=="0" (
        if "%AUTO_MODE%"=="false" echo [-] Warning: Application may still be running
        timeout /t 3 /nobreak >NUL
    )
    if "%AUTO_MODE%"=="false" echo [+] Application closed successfully!
) else (
    if "%AUTO_MODE%"=="false" echo [+] Application is not running.
)

:: Step 2: Get current version
if "%AUTO_MODE%"=="false" (
    echo.
    echo [2/7] ^>^> Checking current version...
)
set "CURRENT_VERSION=0.0.0"
if exist "%VERSION_FILE%" (
    set /p CURRENT_VERSION=<"%VERSION_FILE%"
    if "%AUTO_MODE%"=="false" echo [*] Current version: !CURRENT_VERSION!
) else (
    if "%AUTO_MODE%"=="false" echo [!] No version file found. Assuming first installation!
)

:: Step 3: Fetch latest version with retry logic
if "%AUTO_MODE%"=="false" (
    echo.
    echo [3/7] ^>^> Fetching latest release information...
)
set "RETRY_COUNT=0"

:fetch_release_info
set /a RETRY_COUNT+=1
if "%AUTO_MODE%"=="false" echo [~] Attempt !RETRY_COUNT!/!MAX_RETRIES!: Fetching release info...

powershell -Command "try { $response = Invoke-RestMethod -Uri '%REPO_URL%' -TimeoutSec 30; $response | ConvertTo-Json -Depth 10 | Out-File -FilePath '%TEMP_DIR%\release_info.json' -Encoding UTF8; exit 0 } catch { Write-Host 'Error: ' $_.Exception.Message; exit 1 }" >NUL 2>&1

if !ERRORLEVEL! neq 0 (
    if "%AUTO_MODE%"=="false" echo [-] Failed to fetch release information.
    if !RETRY_COUNT! lss !MAX_RETRIES! (
        if "%AUTO_MODE%"=="false" echo [~] Retrying in 5 seconds...
        if "%AUTO_MODE%"=="false" (
            timeout /t 5 /nobreak >NUL
        ) else (
            timeout /t 1 /nobreak >NUL
        )
        goto fetch_release_info
    ) else (
        if "%AUTO_MODE%"=="false" (
            echo [X] Maximum retries reached. Update failed.
        ) else (
            echo [X] Maximum retries reached. Update failed.
            goto countdown_exit
        )
        goto cleanup_and_exit
    )
)

:: Parse latest version
for /f "tokens=*" %%i in ('powershell -Command "(Get-Content '%TEMP_DIR%\release_info.json' | ConvertFrom-Json).tag_name.TrimStart('v')"') do set "LATEST_VERSION=%%i"

if "%AUTO_MODE%"=="false" echo [*] Latest version: !LATEST_VERSION!

:: Step 4: Compare versions
if "%AUTO_MODE%"=="false" (
    echo.
    echo [4/7] ^>^> Comparing versions...
)

:: Use PowerShell to compare versions properly (handle version format variations)
powershell -Command "try { $current = '!CURRENT_VERSION!' -replace '^v', ''; $latest = '!LATEST_VERSION!' -replace '^v', ''; $currentVer = [System.Version]$current; $latestVer = [System.Version]$latest; if ($currentVer -ge $latestVer) { exit 0 } else { exit 1 } } catch { Write-Host 'Version comparison failed, proceeding with update'; exit 1 }" >NUL 2>&1

if !ERRORLEVEL! equ 0 (
    if "%AUTO_MODE%"=="false" (
        echo [+] You already have the latest version ^(!CURRENT_VERSION!^)!
        echo [+] No update needed. You're all set!
    )
    if "%AUTO_MODE%"=="true" (
        goto countdown_exit
    ) else (
        goto cleanup_and_exit
    )
)

if "%AUTO_MODE%"=="false" echo [!] Update available: !CURRENT_VERSION! --^> !LATEST_VERSION!

:: Auto mode: Bring window to front and ask for download confirmation
if "%AUTO_MODE%"=="true" (
    :: Bring console window to front
    powershell -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32 { [DllImport(\"kernel32.dll\")] public static extern IntPtr GetConsoleWindow(); [DllImport(\"user32.dll\")] public static extern bool SetForegroundWindow(IntPtr hWnd); }'; $consolePtr = [Win32]::GetConsoleWindow(); [Win32]::SetForegroundWindow($consolePtr)" >NUL 2>&1
    
    :: Brief pause to ensure window focus
    timeout /t 1 /nobreak >NUL
    
    echo.
    echo ==========================================
    echo    ^>^> DeepSeek Desktop Auto-Updater ^<^<
    echo ==========================================
    echo.
    echo [!] NEW VERSION AVAILABLE!
    echo     Current: !CURRENT_VERSION!
    echo     Latest:  !LATEST_VERSION!
    echo.
    echo You have 30 seconds to respond...
    echo If no response, update will proceed automatically.
    echo.
    
    :: Use choice command with timeout for auto-confirmation
    choice /C YN /T 30 /D Y /M "Do you want to download and install the update? (Y/N)"
    if !ERRORLEVEL! equ 2 (
        echo [*] Update cancelled by user.
        goto countdown_exit
    )
    if !ERRORLEVEL! equ 0 (
        echo [*] No response received. Auto-proceeding with update...
    ) else (
        echo [*] Proceeding with update...
    )
)

:: Step 5: Download latest release with retry logic
if "%AUTO_MODE%"=="false" (
    echo.
    echo [5/7] ^>^> Downloading latest release...
)
set "RETRY_COUNT=0"

:download_release
set /a RETRY_COUNT+=1
if "%AUTO_MODE%"=="false" echo [~] Attempt !RETRY_COUNT!/!MAX_RETRIES!: Downloading release...

powershell -Command "try { $release = Get-Content '%TEMP_DIR%\release_info.json' | ConvertFrom-Json; $asset = $release.assets | Where-Object { $_.name -like '*windows.zip' } | Select-Object -First 1; if ($asset) { Write-Host 'Downloading:' $asset.name; Write-Host 'File size:' ([math]::Round($asset.size / 1MB, 2)) 'MB'; Write-Host ''; $startTime = Get-Date; $webClient = New-Object System.Net.WebClient; $webClient.add_DownloadProgressChanged({ param($sender, $e) $elapsed = (Get-Date) - $startTime; $speed = if ($elapsed.TotalSeconds -gt 0) { $e.BytesReceived / $elapsed.TotalSeconds } else { 0 }; $eta = if ($speed -gt 0) { [TimeSpan]::FromSeconds(($e.TotalBytesToReceive - $e.BytesReceived) / $speed) } else { [TimeSpan]::Zero }; $progress = [math]::Round(($e.BytesReceived / $e.TotalBytesToReceive) * 100, 1); $downloaded = [math]::Round($e.BytesReceived / 1MB, 2); $total = [math]::Round($e.TotalBytesToReceive / 1MB, 2); $speedMB = [math]::Round($speed / 1MB, 2); $elapsedStr = '{0:mm\:ss}' -f $elapsed; $progressBar = '█' * [math]::Floor($progress / 2) + '░' * (50 - [math]::Floor($progress / 2)); Write-Host (\"[{0}] {1}% | {2}/{3} MB | {4} MB/s | Elapsed: {5} | ETA: {6:mm\:ss}\" -f $progressBar, $progress, $downloaded, $total, $speedMB, $elapsedStr, $eta) -NoNewline; Write-Host \"`r\" -NoNewline; }); $webClient.DownloadFile($asset.browser_download_url, '%TEMP_DIR%\update.zip'); Write-Host ''; Write-Host 'Download completed successfully!'; exit 0 } else { Write-Host 'Windows release asset not found.'; exit 1 } } catch { Write-Host 'Download error:' $_.Exception.Message; exit 1 }"

if !ERRORLEVEL! neq 0 (
    if "%AUTO_MODE%"=="false" echo [-] Download failed.
    if !RETRY_COUNT! lss !MAX_RETRIES! (
        if "%AUTO_MODE%"=="false" echo [~] Retrying in 10 seconds...
        if "%AUTO_MODE%"=="false" (
            timeout /t 10 /nobreak >NUL
        ) else (
            timeout /t 2 /nobreak >NUL
        )
        goto download_release
    ) else (
        if "%AUTO_MODE%"=="false" (
            echo [X] Maximum retries reached. Update failed.
        ) else (
            echo [X] Maximum retries reached. Update failed.
            goto countdown_exit
        )
        goto cleanup_and_exit
    )
)

:: Verify download
if not exist "%TEMP_DIR%\update.zip" (
    if "%AUTO_MODE%"=="false" (
        echo [-] Error: Downloaded file not found.
        goto cleanup_and_exit
    ) else (
        echo [-] Error: Downloaded file not found.
        goto countdown_exit
    )
)

:: Step 6: Backup and extract with retry logic
if "%AUTO_MODE%"=="false" (
    echo.
    echo [6/7] ^>^> Creating backup and installing update...
)
set "RETRY_COUNT=0"

:install_update
set /a RETRY_COUNT+=1
if "%AUTO_MODE%"=="false" echo [~] Attempt !RETRY_COUNT!/!MAX_RETRIES!: Installing update...

:: Create backup
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
if "%AUTO_MODE%"=="false" echo [*] Creating backup...
if exist "%APP_NAME%" (
    copy /Y "%APP_NAME%" "%BACKUP_DIR%\" >NUL 2>&1
    if !ERRORLEVEL! neq 0 (
        if "%AUTO_MODE%"=="false" echo [-] Failed to backup executable
        goto cleanup_and_exit
    )
)
if exist "injection" (
    xcopy /E /I /H /Y "injection" "%BACKUP_DIR%\injection\" >NUL 2>&1
    if !ERRORLEVEL! neq 0 (
        if "%AUTO_MODE%"=="false" echo [-] Failed to backup injection folder
    )
)
if exist "%VERSION_FILE%" (
    copy "%VERSION_FILE%" "%BACKUP_DIR%\" >NUL 2>&1
    if !ERRORLEVEL! neq 0 (
        if "%AUTO_MODE%"=="false" echo [-] Failed to backup version file
    )
)

:: Extract update
if "%AUTO_MODE%"=="false" echo [*] Extracting update...
powershell -Command "try { Expand-Archive -Path '%TEMP_DIR%\update.zip' -DestinationPath '%TEMP_DIR%\extracted' -Force; exit 0 } catch { Write-Host 'Extraction error:' $_.Exception.Message; exit 1 }" >NUL 2>&1

if !ERRORLEVEL! neq 0 (
    if "%AUTO_MODE%"=="false" echo [-] Extraction failed.
    if !RETRY_COUNT! lss !MAX_RETRIES! (
        if "%AUTO_MODE%"=="false" echo [~] Retrying in 5 seconds...
        if "%AUTO_MODE%"=="false" (
            timeout /t 5 /nobreak >NUL
        ) else (
            timeout /t 1 /nobreak >NUL
        )
        goto install_update
    ) else (
        if "%AUTO_MODE%"=="false" (
            echo [X] Maximum retries reached. Restoring backup...
        ) else (
            echo [X] Maximum retries reached. Restoring backup...
        )
        goto restore_backup
    )
)

:: Copy new files (preserve data folder)
if "%AUTO_MODE%"=="false" echo [*] Installing new files...
if exist "%TEMP_DIR%\extracted\%APP_NAME%" (
    copy /Y "%TEMP_DIR%\extracted\%APP_NAME%" "." >NUL 2>&1
    if !ERRORLEVEL! neq 0 (
        if "%AUTO_MODE%"=="false" echo [-] Failed to copy executable. Restoring backup...
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

if "%AUTO_MODE%"=="false" echo [+] Update installed successfully!
goto start_application

:restore_backup
if "%AUTO_MODE%"=="false" (
    echo [~] Restoring from backup...
) else (
    echo [~] Restoring from backup...
)
if exist "%BACKUP_DIR%\%APP_NAME%" copy /Y "%BACKUP_DIR%\%APP_NAME%" "." >NUL 2>&1
if exist "%BACKUP_DIR%\injection" (
    if exist "injection" rmdir /S /Q "injection" >NUL 2>&1
    xcopy /E /I /H /Y "%BACKUP_DIR%\injection" "injection\" >NUL 2>&1
)
if exist "%BACKUP_DIR%\%VERSION_FILE%" copy /Y "%BACKUP_DIR%\%VERSION_FILE%" "." >NUL 2>&1
if "%AUTO_MODE%"=="false" (
    echo [+] Backup restored. Update failed.
    goto cleanup_and_exit
) else (
    echo [+] Backup restored. Update failed.
    goto countdown_exit
)

:start_application
:: Step 7: Start application
if "%AUTO_MODE%"=="false" (
    echo.
    echo [7/7] ^>^> Starting application...
)
if exist "%APP_NAME%" (
    if "%AUTO_MODE%"=="false" (
        start "" "%APP_NAME%"
        echo [+] %APP_NAME% started successfully!
        echo.
        echo ==========================================
        echo   *** UPDATE COMPLETED SUCCESSFULLY! ***
        echo   Version: !CURRENT_VERSION! --^> !LATEST_VERSION!
        echo   *** Enjoy your updated DeepSeek Desktop! ***
        echo ==========================================
    ) else (
        echo.
        echo ==========================================
        echo   *** UPDATE COMPLETED SUCCESSFULLY! ***
        echo   Version: !CURRENT_VERSION! --^> !LATEST_VERSION!
        echo ==========================================
        echo.
        echo Starting application in 3 seconds...
        for /l %%i in (3,-1,1) do (
            echo Starting in %%i...
            timeout /t 1 /nobreak >NUL
        )
        start "" "%APP_NAME%"
        echo [+] %APP_NAME% started successfully!
        goto countdown_exit
    )
) else (
    if "%AUTO_MODE%"=="false" (
        echo [-] Error: %APP_NAME% not found after update.
        goto restore_backup
    ) else (
        echo [-] Error: %APP_NAME% not found after update.
        goto restore_backup
    )
)

:countdown_exit
:: Countdown exit for auto mode
if "%AUTO_MODE%"=="true" (
    echo.
    for /l %%i in (5,-1,1) do (
        echo Closing in %%i...
        timeout /t 1 /nobreak >NUL
    )
    goto cleanup_and_exit
)

:cleanup_and_exit
:: Cleanup
if "%AUTO_MODE%"=="false" (
    echo.
    echo [*] Cleaning up temporary files...
)
if exist "%TEMP_DIR%" rmdir /S /Q "%TEMP_DIR%" >NUL 2>&1

if "%AUTO_MODE%"=="true" (
    :: Auto-close after countdown
    exit /b 0
) else (
    echo.
    echo Press any key to exit...
    pause >NUL
    exit /b 0
)