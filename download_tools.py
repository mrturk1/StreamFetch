import os
import urllib.request
import zipfile
import shutil
import tempfile
import sys

def download_ffmpeg():
    # Do not download if files already exist
    if os.path.exists('ffmpeg.exe') and os.path.exists('ffprobe.exe'):
        return

    print("===================================================")
    print("[INFO] Downloading required FFmpeg tools for the project...")
    print("[INFO] This process may take 1-2 minutes depending on your internet speed.")
    print("Please wait...")
    
    url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "ffmpeg.zip")
            
            # Downloading process
            urllib.request.urlretrieve(url, zip_path)
            
            print("[INFO] Download complete. Extracting files...")
            # Extracting from Zip
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                
            # Moving required .exe files to the main folder
            base_folder = "ffmpeg-master-latest-win64-gpl/bin"
            ffmpeg_src = os.path.join(temp_dir, base_folder, "ffmpeg.exe")
            ffprobe_src = os.path.join(temp_dir, base_folder, "ffprobe.exe")
            
            shutil.move(ffmpeg_src, "ffmpeg.exe")
            shutil.move(ffprobe_src, "ffprobe.exe")
            
        print("[SUCCESS] FFmpeg tools installed successfully!")
        print("===================================================\n")
    except Exception as e:
        print(f"[ERROR] An error occurred while downloading FFmpeg: {e}")
        print("You can continue using the system, but some features may not work.")
        print("===================================================\n")

if __name__ == "__main__":
    download_ffmpeg()
