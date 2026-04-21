"""
Titanium Downloader - Download Engine
Wrapper cho yt-dlp với smart format selection, retry logic, và progress tracking.
"""
import yt_dlp
import os
import re
import time
import shutil
import subprocess
from datetime import datetime


class DownloadEngine:
    """Core download engine using yt-dlp."""
    
    # Quality mapping
    QUALITY_MAP = {
        "4K": 2160,
        "2K": 1440,
        "1080p": 1080,
        "720p": 720,
        "480p": 480,
    }
    
    def __init__(self, ffmpeg_path=None):
        self.ffmpeg_path = ffmpeg_path or self._find_ffmpeg()
        self.is_ffmpeg_ok = self._check_ffmpeg()
        self._cancel_flag = False
    
    def _find_ffmpeg(self):
        """Tìm ffmpeg trong PATH hoặc thư mục project."""
        path = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
        if not path:
            # Tìm trong thư mục project
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            local = os.path.join(project_dir, "ffmpeg.exe")
            if os.path.exists(local):
                path = local
        return path
    
    def _check_ffmpeg(self):
        """Kiểm tra ffmpeg có hoạt động không."""
        if not self.ffmpeg_path:
            return False
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run(
                [self.ffmpeg_path, "-version"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                startupinfo=startupinfo, check=True, timeout=10
            )
            return True
        except Exception:
            return False
    
    def cancel(self):
        """Hủy tải xuống hiện tại."""
        self._cancel_flag = True
    
    def reset_cancel(self):
        self._cancel_flag = False
    
    def fetch_info(self, url, cookie_path=None):
        """
        Lấy thông tin video/audio trước khi tải.
        Returns dict: {title, duration, thumbnail, formats, uploader, view_count, ...}
        """
        opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
            'cookiefile': cookie_path if cookie_path else None,
        }
        
        # User agent cho non-YouTube
        if url and "youtube" not in url.lower() and "youtu.be" not in url.lower():
            opts['http_headers'] = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info is None:
                    return None
                
                # Nếu là playlist, lấy entry đầu tiên
                if info.get('_type') == 'playlist':
                    entries = info.get('entries', [])
                    playlist_count = info.get('playlist_count', len(entries))
                    first = entries[0] if entries else {}
                    return {
                        'is_playlist': True,
                        'playlist_title': info.get('title', 'Playlist'),
                        'playlist_count': playlist_count,
                        'title': first.get('title', info.get('title', 'Unknown')),
                        'duration': first.get('duration', 0),
                        'thumbnail': first.get('thumbnail', ''),
                        'uploader': first.get('uploader', info.get('uploader', '')),
                    }
                
                # Tìm các chất lượng video có sẵn
                available_qualities = set()
                formats = info.get('formats', [])
                for f in formats:
                    h = f.get('height')
                    if h and f.get('vcodec', 'none') != 'none':
                        if h >= 2160:
                            available_qualities.add("4K")
                        if h >= 1440:
                            available_qualities.add("2K")
                        if h >= 1080:
                            available_qualities.add("1080p")
                        if h >= 720:
                            available_qualities.add("720p")
                        if h >= 480:
                            available_qualities.add("480p")
                
                return {
                    'is_playlist': False,
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', ''),
                    'view_count': info.get('view_count', 0),
                    'available_qualities': sorted(available_qualities, 
                        key=lambda x: self.QUALITY_MAP.get(x, 0), reverse=True),
                    'webpage_url': info.get('webpage_url', url),
                }
        except Exception as e:
            return {'error': str(e)}
    
    def _sanitize_filename(self, title):
        """Loại bỏ ký tự không hợp lệ trên Windows."""
        # Loại bỏ ký tự không hợp lệ trên Windows
        sanitized = re.sub(r'[<>:"/\\|?*]', '', title)
        # Giới hạn độ dài
        if len(sanitized) > 200:
            sanitized = sanitized[:200]
        return sanitized.strip()
    
    def download(self, url, output_path, mode="MP4", quality="1080p", 
                 bitrate="320k", is_playlist=False, cookie_path=None,
                 progress_callback=None, log_callback=None, max_retries=3):
        """
        Tải video/audio.
        
        Args:
            url: URL cần tải
            output_path: Thư mục lưu file 
            mode: "MP4" hoặc "MP3"
            quality: "4K", "2K", "1080p", "720p", "480p"
            bitrate: "320k", "192k", "128k" (cho MP3)
            is_playlist: Tải cả playlist
            cookie_path: Đường dẫn file cookies.txt
            progress_callback: fn(percent, speed, eta)
            log_callback: fn(message)
            max_retries: Số lần retry
            
        Returns:
            dict: {success, filename, filepath, filesize, error}
        """
        self._cancel_flag = False
        
        height = self.QUALITY_MAP.get(quality, 1080)
        
        # Template output - sanitize tên file
        outtmpl = os.path.join(output_path, '%(title)s.%(ext)s')
        
        ydl_opts = {
            'outtmpl': outtmpl,
            'noplaylist': not is_playlist,
            'cookiefile': cookie_path if cookie_path else None,
            'quiet': True,
            'no_warnings': True,
            'restrictfilenames': False,
            'windowsfilenames': True,  # Tự động sanitize cho Windows
            'retries': max_retries,
            'fragment_retries': max_retries,
            'retry_sleep_functions': {'http': lambda n: 2 ** n},  # Exponential backoff
        }
        
        # Progress hook
        if progress_callback:
            def _hook(d):
                if self._cancel_flag:
                    raise Exception("Download cancelled by user")
                if d['status'] == 'downloading':
                    try:
                        p_str = d.get('_percent_str', '0%').strip()
                        found = re.search(r"(\d+\.?\d*)", p_str)
                        if found:
                            percent = float(found.group(1))
                            speed = d.get('_speed_str', 'N/A').strip()
                            eta = d.get('_eta_str', 'N/A').strip()
                            progress_callback(percent, speed, eta)
                    except Exception:
                        pass
                elif d['status'] == 'finished':
                    progress_callback(100, '', '')
            
            ydl_opts['progress_hooks'] = [_hook]
        
        # --- FORMAT SELECTION ---
        if mode == "MP3":
            if log_callback:
                log_callback("🎵 Chế độ MP3 - Chất lượng tối đa")
            
            bitrate_num = bitrate.replace("k", "")
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': bitrate_num,
                }, {
                    'key': 'EmbedThumbnail',
                }, {
                    'key': 'FFmpegMetadata',
                }],
                'writethumbnail': True,
            })
            if self.is_ffmpeg_ok:
                ydl_opts['ffmpeg_location'] = self.ffmpeg_path
        
        else:  # MP4
            if self.is_ffmpeg_ok:
                if log_callback:
                    log_callback(f"🎬 Chế độ MP4 - Chất lượng {quality} (Video+Audio Merge)")
                
                # Smart format: ưu tiên mp4/m4a cho compatibility
                fmt_str = (
                    f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/'
                    f'bestvideo[height<={height}]+bestaudio[ext=m4a]/'
                    f'bestvideo[height<={height}]+bestaudio/'
                    f'best[height<={height}]/'
                    f'best'
                )
                
                ydl_opts.update({
                    'format': fmt_str,
                    'merge_output_format': 'mp4',
                    'ffmpeg_location': self.ffmpeg_path,
                    'postprocessors': [{
                        'key': 'FFmpegMetadata',
                    }],
                })
            else:
                if log_callback:
                    log_callback("⚠️ FFmpeg không khả dụng - Chế độ fallback (max 720p)")
                ydl_opts.update({
                    'format': f'best[ext=mp4][height<={min(height, 720)}]/best[ext=mp4]/best',
                })
        
        # User-Agent cho non-YouTube
        if url and "youtube" not in url.lower() and "youtu.be" not in url.lower():
            ydl_opts['http_headers'] = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        
        # --- DOWNLOAD WITH RETRY ---
        last_error = None
        for attempt in range(1, max_retries + 1):
            if self._cancel_flag:
                return {'success': False, 'error': 'Đã hủy tải xuống'}
            
            try:
                if attempt > 1 and log_callback:
                    log_callback(f"🔄 Thử lại lần {attempt}/{max_retries}...")
                    time.sleep(2 ** (attempt - 1))  # Exponential backoff
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    if log_callback:
                        log_callback(f"📥 Đang xử lý: {url}")
                    
                    info = ydl.extract_info(url, download=True)
                    
                    if info is None:
                        continue
                    
                    # Lấy thông tin file đã tải
                    title = info.get('title', 'Unknown')
                    ext = 'mp3' if mode == "MP3" else 'mp4'
                    filename = ydl.prepare_filename(info)
                    
                    # Nếu là MP3, ext đã bị đổi bởi postprocessor
                    if mode == "MP3":
                        base = os.path.splitext(filename)[0]
                        filename = base + ".mp3"
                    
                    filesize = 0
                    if os.path.exists(filename):
                        filesize = os.path.getsize(filename)
                    
                    return {
                        'success': True,
                        'title': title,
                        'filename': os.path.basename(filename),
                        'filepath': filename,
                        'filesize': filesize,
                        'quality': quality if mode == "MP4" else f"MP3 {bitrate}",
                        'timestamp': datetime.now().isoformat(),
                    }
            
            except Exception as e:
                last_error = str(e)
                if "cancelled" in last_error.lower():
                    return {'success': False, 'error': 'Đã hủy tải xuống'}
                if log_callback:
                    log_callback(f"❌ Lỗi lần {attempt}: {last_error[:150]}")
        
        return {'success': False, 'error': last_error or 'Unknown error'}
    
    @staticmethod
    def format_filesize(size_bytes):
        """Format file size to human readable."""
        if size_bytes == 0:
            return "0 B"
        units = ['B', 'KB', 'MB', 'GB']
        i = 0
        size = float(size_bytes)
        while size >= 1024 and i < len(units) - 1:
            size /= 1024
            i += 1
        return f"{size:.1f} {units[i]}"
    
    @staticmethod
    def format_duration(seconds):
        """Format seconds to HH:MM:SS."""
        if not seconds:
            return "N/A"
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"
