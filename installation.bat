@echo off
echo Checking for ffmpeg installation in the current directory...

REM Check if ffmpeg.exe exists in the current directory
if exist "%cd%\ffmpeg.exe" (
    echo FFmpeg is already installed in the current directory.
) else (
    echo FFmpeg is not installed. Downloading and installing FFmpeg...
    
    REM Download the latest ffmpeg zip (Windows essentials build) from an official source
    curl -L https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip -o ffmpeg.zip
    
    REM Extract all contents to a temporary directory
    mkdir temp_ffmpeg
    tar -xf ffmpeg.zip -C temp_ffmpeg
    
    REM Find the ffmpeg.exe file and move it to the current directory
    move /Y "temp_ffmpeg\ffmpeg-*-essentials_build\bin\ffmpeg.exe" "%cd%"
    
    REM Clean up the temporary files and directory
    rmdir /S /Q temp_ffmpeg
    del ffmpeg.zip

    echo FFmpeg installed successfully in the current directory.
)

echo Creating a virtual environment...
python -m venv venv

echo Activating the virtual environment...
call venv\Scripts\activate

echo Installing Python packages from requirements.txt...
pip install -r requirements.txt

pause
