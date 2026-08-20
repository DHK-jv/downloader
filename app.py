"""
Fixed/Optimized by Antigravity:
⚡ DHK Downloader
================================
Tải MP3 & MP4 từ YouTube, Facebook, TikTok, Instagram, Twitter/X, SoundCloud
và hơn 1000 trang web khác.

Cách chạy:
    python app.py
    hoặc
    .venv\\Scripts\\python.exe app.py
"""
from app.core.config import Config
from app.core.downloader import DownloadEngine
from app.core.converter import Converter
from app.ui.app_window import AppWindow


def main():
    # 1. Load config
    config = Config()
    
    # 2. Initialize download engine
    engine = DownloadEngine()
    
    # 3. Initialize converter
    converter = Converter(ffmpeg_path=engine.ffmpeg_path)
    
    # 4. Create and run app window
    app = AppWindow(
        download_engine=engine,
        converter=converter,
        config=config
    )
    
    # Center window on screen
    app.update_idletasks()
    width = 1080
    height = 720
    x = (app.winfo_screenwidth() // 2) - (width // 2)
    y = (app.winfo_screenheight() // 2) - (height // 2)
    app.geometry(f"{width}x{height}+{x}+{y}")
    
    app.mainloop()


if __name__ == "__main__":
    main()
