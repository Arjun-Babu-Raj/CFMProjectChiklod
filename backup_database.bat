@echo off
REM Automated backup script for Village Health Tracking System (Windows)
REM This script creates backups of the database and uploaded photos

setlocal enabledelayedexpansion

REM Configuration
set DB_FILE=health_tracking.db
set BACKUP_DIR=backups
set PHOTOS_DIR=uploaded_photos
set DATE=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set DATE=%DATE: =0%

echo ==========================================
echo Village Health Tracking System - Backup
echo ==========================================
echo.

REM Create backup directory if it doesn't exist
if not exist "%BACKUP_DIR%" (
    echo Creating backup directory...
    mkdir "%BACKUP_DIR%"
)

REM Check if database exists
if not exist "%DB_FILE%" (
    echo ERROR: Database file '%DB_FILE%' not found!
    exit /b 1
)

REM Backup database file
echo 1. Backing up database...
copy "%DB_FILE%" "%BACKUP_DIR%\health_tracking_%DATE%.db" >nul
if %errorlevel% equ 0 (
    echo    [OK] Database backup created: health_tracking_%DATE%.db
) else (
    echo    [FAIL] Database backup failed!
    exit /b 1
)

REM Backup photos directory if it exists
if exist "%PHOTOS_DIR%" (
    echo 2. Backing up photos...
    powershell Compress-Archive -Path "%PHOTOS_DIR%" -DestinationPath "%BACKUP_DIR%\photos_%DATE%.zip" -Force
    if %errorlevel% equ 0 (
        echo    [OK] Photos backup created: photos_%DATE%.zip
    ) else (
        echo    [FAIL] Photos backup failed!
    )
) else (
    echo 2. No photos directory found, skipping...
)

REM Remove old backups (older than 30 days)
echo 3. Cleaning old backups ^(older than 30 days^)...
forfiles /P "%BACKUP_DIR%" /S /M health_tracking_*.db /D -30 /C "cmd /c del @path" 2>nul
forfiles /P "%BACKUP_DIR%" /S /M photos_*.zip /D -30 /C "cmd /c del @path" 2>nul
echo    [OK] Old backups cleaned

REM Display backup summary
echo.
echo ==========================================
echo Backup Summary
echo ==========================================
echo Backup completed: %DATE%
echo Location: %BACKUP_DIR%\
echo.
echo Recent backups:
dir /B /O-D "%BACKUP_DIR%\health_tracking_*.db" 2>nul | findstr /R ".*" >nul && dir /B /O-D "%BACKUP_DIR%\health_tracking_*.db" | more +0 | findstr /R ".*"

echo.
echo ==========================================
echo Backup completed successfully!
echo ==========================================

endlocal
