# StreamFetch

StreamFetch is a modern, fast, and robust web application designed to download videos and audio from virtually any streaming platform (YouTube, Twitter, Instagram, Vimeo, and custom HLS/m3u8 streams).

## Features
- **16x Turbo Download:** Downloads HLS (m3u8) streams using concurrent fragments for blazing fast speeds.
- **Auto-Merge:** Automatically merges video and audio tracks in the highest available quality using FFmpeg.
- **Bypass Protections:** Paste the master `.m3u8` link from any sniffer extension (like FetchV) to download from protected streaming sites.
- **Beautiful UI:** A sleek, glassmorphism-inspired interface with real-time progress tracking.

## How to Run

### Method 1: The Easiest Way (Recommended for Windows)
1. Double-click the **`Start.bat`** file in the project folder.
2. **Smart Setup:** If Python is not installed on your computer, the script will automatically detect this and open the Python download page for you! Just install it (remember to check "Add Python to PATH" during installation).
3. The script will automatically download and install all necessary background tools (like yt-dlp, Flask) if you don't have them.
4. A black terminal window will open (do not close this while using the app).
5. Your default web browser will automatically open the application interface!

### Method 2: Using Terminal / Command Prompt
1. Open a terminal in this project folder.
2. Run the following command:
   ```bash
   python app.py
   ```
3. Open your web browser and go to: `http://127.0.0.1:5000`

---

## Where are my files?
All downloaded video and audio files are automatically saved to the **`downloads`** folder inside this directory. You can also click the "Folder" icon next to any downloaded file in the web interface to instantly locate it in your file explorer.

## Stopping the Server
To stop the application, simply close the black terminal window.
