"""
Titanium Downloader - File Converter
Wrapper cho FFmpeg để chuyển đổi định dạng file.
"""
import subprocess
import os
import re
import threading


class Converter:
    """FFmpeg-based file format converter."""
    
    AUDIO_FORMATS = {"mp3", "wav", "flac", "m4a", "aac", "ogg"}
    VIDEO_FORMATS = {"mp4", "mkv", "avi", "webm", "mov"}
    ALL_FORMATS = sorted(AUDIO_FORMATS | VIDEO_FORMATS)
    
    def __init__(self, ffmpeg_path):
        self.ffmpeg_path = ffmpeg_path
        self._process = None
    
    def cancel(self):
        """Hủy quá trình convert."""
        if self._process and self._process.poll() is None:
            self._process.terminate()
    
    def convert(self, input_path, output_format, 
                progress_callback=None, log_callback=None):
        """
        Chuyển đổi file sang format mới.
        
        Args:
            input_path: Đường dẫn file nguồn
            output_format: Format đích (mp3, mp4, wav, etc.)
            progress_callback: fn(percent)
            log_callback: fn(message)
            
        Returns:
            dict: {success, output_path, error}
        """
        if not os.path.exists(input_path):
            return {'success': False, 'error': 'File không tồn tại'}
        
        if not self.ffmpeg_path:
            return {'success': False, 'error': 'FFmpeg không khả dụng'}
        
        # Tạo tên file output
        folder = os.path.dirname(input_path)
        name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(folder, f"{name}_converted.{output_format}")
        
        # Tránh ghi đè
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(folder, f"{name}_converted_{counter}.{output_format}")
            counter += 1
        
        if log_callback:
            log_callback(f"🔄 Bắt đầu convert: {name} → {output_format}")
        
        # Xây dựng command
        cmd = [self.ffmpeg_path, "-i", input_path, "-y"]
        
        # Lấy duration để tính progress
        duration = self._get_duration(input_path)
        
        # Logic format
        if output_format in self.AUDIO_FORMATS:
            cmd.append("-vn")  # Bỏ video track
            if output_format == "mp3":
                cmd.extend(["-acodec", "libmp3lame", "-b:a", "320k"])
            elif output_format == "flac":
                cmd.extend(["-acodec", "flac"])
            elif output_format == "wav":
                cmd.extend(["-acodec", "pcm_s16le"])
        else:
            # Video formats
            if output_format == "mp4":
                cmd.extend(["-c:v", "libx264", "-c:a", "aac", "-b:a", "192k"])
            elif output_format == "mkv":
                cmd.extend(["-c:v", "copy", "-c:a", "copy"])
        
        cmd.append(output_path)
        
        try:
            creationflags = 0x08000000 if os.name == 'nt' else 0
            self._process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True, 
                creationflags=creationflags
            )
            
            # Parse stderr for progress
            _, stderr = self._process.communicate()
            
            if self._process.returncode == 0:
                if log_callback:
                    log_callback(f"✅ Hoàn tất: {os.path.basename(output_path)}")
                if progress_callback:
                    progress_callback(100)
                return {
                    'success': True, 
                    'output_path': output_path,
                    'filename': os.path.basename(output_path),
                }
            else:
                error_msg = stderr[-300:] if stderr else "Unknown error"
                if log_callback:
                    log_callback(f"❌ Lỗi convert: {error_msg}")
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            if log_callback:
                log_callback(f"❌ Lỗi: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            self._process = None
    
    def _get_duration(self, filepath):
        """Lấy duration của file bằng ffprobe."""
        try:
            ffprobe = self.ffmpeg_path.replace("ffmpeg", "ffprobe")
            if not os.path.exists(ffprobe):
                return 0
            
            creationflags = 0x08000000 if os.name == 'nt' else 0
            result = subprocess.run(
                [ffprobe, "-v", "quiet", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", filepath],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True, creationflags=creationflags,
                timeout=10
            )
            return float(result.stdout.strip())
        except Exception:
            return 0
