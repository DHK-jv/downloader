"""
Titanium Downloader - Configuration Manager
Quản lý cài đặt ứng dụng, lưu/load từ file JSON.
"""
import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = Path(os.environ.get("DHK_CONFIG_PATH", PROJECT_ROOT / "config" / "dhk_config.json"))

DEFAULT_CONFIG = {
    "theme": "Dark",
    "output_path": os.environ.get("DHK_OUTPUT_PATH", os.path.join(os.path.expanduser("~"), "Downloads")),
    "cookie_path": "",
    "last_video_quality": "1080p",
    "last_audio_bitrate": "320k",
    "last_mode": "MP4",
    "download_history": [],
}

class Config:
    """Singleton config manager."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data = {}
            cls._instance._load()
        return cls._instance
    
    def _load(self):
        """Load config from JSON file."""
        try:
            if CONFIG_FILE.exists():
                with CONFIG_FILE.open("r", encoding="utf-8") as f:
                    saved = json.load(f)
                # Merge with defaults (keep new keys)
                self._data = {**DEFAULT_CONFIG, **saved}
                # Docker/native environment variables must override paths saved by another machine.
                if os.environ.get("DHK_OUTPUT_PATH"):
                    self._data["output_path"] = os.environ["DHK_OUTPUT_PATH"]
            else:
                self._data = DEFAULT_CONFIG.copy()
        except (json.JSONDecodeError, IOError):
            self._data = DEFAULT_CONFIG.copy()
    
    def save(self):
        """Save config to JSON file."""
        try:
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with CONFIG_FILE.open("w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"[Config] Save error: {e}")
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def set(self, key, value, auto_save=True):
        self._data[key] = value
        if auto_save:
            self.save()
    
    def add_history(self, entry):
        """Add download history entry. Keep last 100."""
        history = self._data.get("download_history", [])
        history.insert(0, entry)
        self._data["download_history"] = history[:100]
        self.save()
    
    def get_history(self):
        return self._data.get("download_history", [])
    
    def clear_history(self):
        self._data["download_history"] = []
        self.save()
