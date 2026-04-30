import os
import uuid
import subprocess
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'

progress_data = {}

def resolve_url(url):
    """
    Finds iframe links from custom or pirate streaming sites.
    If the URL is not recognized by yt-dlp, it downloads the page source and extracts the iframe (video player) link.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find iframe tags
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '')
            # Filter non-ad iframes that likely contain video
            if src and not 'google' in src and not 'ads' in src and ('//' in src or 'http' in src):
                if src.startswith('//'):
                    src = 'https:' + src
                return src
    except Exception:
        pass
    return url

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    format_type = data.get('format', 'best')  # best or audio
    download_id = data.get('download_id')

    if not url or not download_id:
        return jsonify({'error': 'Invalid request (URL or ID missing)'}), 400

    # Background iframe resolution
    url = resolve_url(url)

    progress_data[download_id] = {'status': 'starting', 'percent': '0%'}

    def my_hook(d):
        if d['status'] == 'downloading':
            # _percent_str is formatted like ' 45.0%'
            percent_str = d.get('_percent_str', '0%').strip()
            # remove ansi escape characters yt-dlp might insert
            import re
            percent_clean = re.sub(r'\x1b\[[0-9;]*m', '', percent_str)
            progress_data[download_id] = {'status': 'downloading', 'percent': percent_clean}
        elif d['status'] == 'finished':
            progress_data[download_id] = {'status': 'processing', 'percent': '100%'}

    try:
        if format_type == 'audio':
            selected_format = 'bestaudio/best'
            merge_format = None
        elif format_type == 'video_only':
            selected_format = 'bestvideo[ext=mp4][vcodec^=avc1]/bestvideo[vcodec^=avc1]/bestvideo[ext=mp4]/bestvideo'
            merge_format = 'mp4'
        else:
            selected_format = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best'
            merge_format = 'mp4'

        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'format': selected_format,
            'merge_output_format': merge_format,
            'noplaylist': True,
            'ffmpeg_location': os.path.abspath('ffmpeg.exe'),
            'progress_hooks': [my_hook],
            'concurrent_fragment_downloads': 8, # Reduced to 8 for stability against Windows file locks
            'file_access_retries': 10,
            'keep_fragments': True, # Prevents yt-dlp from crashing on locked files
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            }
        }
        
        if format_type == 'audio':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'video')
            ext = 'mp3' if format_type == 'audio' else 'mp4'
            filename = f"{title}.{ext}"

            if format_type == 'video_only':
                src_path = ydl.prepare_filename(info)
                base, _ = os.path.splitext(src_path)
                actual = None
                for try_ext in ('.mp4', '.mkv', '.webm'):
                    candidate = base + try_ext
                    if os.path.exists(candidate):
                        actual = candidate
                        break
                if actual:
                    progress_data[download_id] = {'status': 'processing', 'percent': '100%'}
                    final = base + '.mp4'
                    tmp = base + '.compat.mp4'
                    try:
                        subprocess.run([
                            os.path.abspath('ffmpeg.exe'), '-y', '-i', actual,
                            '-c:v', 'libx264', '-profile:v', 'main',
                            '-preset', 'fast', '-crf', '23',
                            '-pix_fmt', 'yuv420p', '-an',
                            tmp
                        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        if actual != final and os.path.exists(actual):
                            os.remove(actual)
                        os.replace(tmp, final)
                        filename = os.path.basename(final)
                    except subprocess.CalledProcessError:
                        if os.path.exists(tmp):
                            os.remove(tmp)

        # Clean up fragments manually
        for root, dirs, files in os.walk(DOWNLOAD_FOLDER):
            for file in files:
                if "Frag" in file or file.endswith(".ytdl") or file.endswith(".part"):
                    try:
                        os.remove(os.path.join(root, file))
                    except:
                        pass

        progress_data[download_id] = {'status': 'done', 'percent': '100%'}
        return jsonify({'success': True, 'message': 'Download completed!', 'filename': filename})
    except Exception as e:
        progress_data[download_id] = {'status': 'error', 'percent': '0%'}
        return jsonify({'error': str(e)}), 500

@app.route('/progress/<download_id>')
def get_progress(download_id):
    return jsonify(progress_data.get(download_id, {'status': 'unknown', 'percent': '0%'}))

@app.route('/files')
def files():
    try:
        file_list = []
        for f in os.listdir(DOWNLOAD_FOLDER):
            if f.startswith('.'):
                continue
            file_path = os.path.join(DOWNLOAD_FOLDER, f)
            if os.path.isfile(file_path):
                file_list.append({
                    'name': f,
                    'mtime': os.path.getmtime(file_path)
                })
        # Sort by mtime descending (newest first)
        file_list.sort(key=lambda x: x['mtime'], reverse=True)
        return jsonify([f['name'] for f in file_list])
    except Exception as e:
        return jsonify([])

@app.route('/open_folder/<path:filename>', methods=['POST'])
def open_folder(filename):
    try:
        file_path = os.path.abspath(os.path.join(DOWNLOAD_FOLDER, filename))
        if os.path.exists(file_path):
            # Select the file in Windows Explorer
            subprocess.run(['explorer', '/select,', file_path])
            return jsonify({'success': True})
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
