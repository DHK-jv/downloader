"""
Titanium Downloader - Download Tab
Tab chính với URL input, video preview, và download controls.
"""
import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import requests
from io import BytesIO
from PIL import Image
from .theme import Colors, Fonts, Spacing


class DownloadTab(ctk.CTkFrame):
    """Main download tab with URL input, preview, and progress."""
    
    def __init__(self, master, download_engine=None, config=None, 
                 get_sidebar_settings=None, log_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.engine = download_engine
        self.config = config
        self.get_sidebar_settings = get_sidebar_settings
        self.log_callback = log_callback
        self._video_info = None
        self._is_downloading = False
        self._thumbnail_image = None  # Keep reference
        
        # Scrollable container - cho phép scroll khi cửa sổ nhỏ
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                              scrollbar_button_color=Colors.BG_CARD,
                                              scrollbar_button_hover_color=Colors.PRIMARY)
        self.scroll.pack(fill="both", expand=True)
        self.scroll.grid_columnconfigure(0, weight=1)
        
        # All content goes inside self.scroll
        container = self.scroll
        
        # ===== HEADER =====
        self.header = ctk.CTkLabel(
            container, text="Tải Video & Nhạc", 
            font=Fonts.HEADING, text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        self.header.pack(fill="x", padx=Spacing.PAD_XL, pady=(Spacing.PAD_XL, Spacing.PAD_SM))
        
        self.subheader = ctk.CTkLabel(
            container, text="Hỗ trợ YouTube, Facebook, TikTok, Instagram, Twitter/X, SoundCloud và 1000+ trang",
            font=Fonts.SMALL, text_color=Colors.TEXT_MUTED, anchor="w"
        )
        self.subheader.pack(fill="x", padx=Spacing.PAD_XL, pady=(0, Spacing.PAD_LG))
        
        # ===== URL INPUT =====
        self.url_frame = ctk.CTkFrame(container, fg_color=Colors.BG_INPUT, 
                                      corner_radius=Spacing.CORNER_RADIUS)
        self.url_frame.pack(fill="x", padx=Spacing.PAD_XL)
        self.url_frame.grid_columnconfigure(0, weight=1)
        
        self.url_entry = ctk.CTkEntry(
            self.url_frame, height=Spacing.INPUT_HEIGHT,
            placeholder_text="🔗  Dán link video hoặc playlist vào đây...",
            font=Fonts.BODY, border_width=0,
            fg_color="transparent", text_color=Colors.TEXT_PRIMARY,
            placeholder_text_color=Colors.TEXT_MUTED
        )
        self.url_entry.grid(row=0, column=0, padx=(Spacing.PAD_MD, 0), sticky="ew")
        
        self.paste_btn = ctk.CTkButton(
            self.url_frame, text="📋 Dán", width=70, height=36,
            font=Fonts.SMALL_BOLD, corner_radius=Spacing.CORNER_RADIUS_SM,
            fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
            command=self._paste_url
        )
        self.paste_btn.grid(row=0, column=1, padx=Spacing.PAD_SM, pady=Spacing.PAD_SM)
        
        self.fetch_btn = ctk.CTkButton(
            self.url_frame, text="🔍", width=40, height=36,
            font=Fonts.BODY, corner_radius=Spacing.CORNER_RADIUS_SM,
            fg_color=Colors.SECONDARY, hover_color=Colors.SECONDARY_HOVER,
            text_color=Colors.BG_DARKEST,
            command=self._fetch_info
        )
        self.fetch_btn.grid(row=0, column=2, padx=(0, Spacing.PAD_SM), pady=Spacing.PAD_SM)
        
        # ===== VIDEO PREVIEW CARD =====
        self.preview_card = ctk.CTkFrame(
            container, fg_color=Colors.BG_CARD, 
            corner_radius=Spacing.CORNER_RADIUS,
            border_width=1, border_color=Colors.BORDER
        )
        self.preview_card.pack(fill="x", padx=Spacing.PAD_XL, pady=Spacing.PAD_MD)
        self.preview_card.grid_columnconfigure(1, weight=1)
        
        # Thumbnail placeholder
        self.thumb_label = ctk.CTkLabel(
            self.preview_card, text="🎬\nDán link và\nnhấn 🔍", 
            width=160, height=100,
            font=Fonts.SMALL, text_color=Colors.TEXT_MUTED,
            fg_color=Colors.BG_INPUT, corner_radius=Spacing.CORNER_RADIUS_SM
        )
        self.thumb_label.grid(row=0, column=0, rowspan=3, padx=Spacing.PAD_MD, 
                             pady=Spacing.PAD_MD, sticky="nsew")
        
        # Video info
        self.title_label = ctk.CTkLabel(
            self.preview_card, text="Chưa có thông tin video",
            font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY,
            anchor="w", wraplength=350
        )
        self.title_label.grid(row=0, column=1, padx=(0, Spacing.PAD_MD), 
                             pady=(Spacing.PAD_MD, 2), sticky="w")
        
        self.uploader_label = ctk.CTkLabel(
            self.preview_card, text="",
            font=Fonts.SMALL, text_color=Colors.TEXT_SECONDARY, anchor="w"
        )
        self.uploader_label.grid(row=1, column=1, padx=(0, Spacing.PAD_MD), sticky="w")
        
        self.info_badges = ctk.CTkFrame(self.preview_card, fg_color="transparent")
        self.info_badges.grid(row=2, column=1, padx=(0, Spacing.PAD_MD), 
                             pady=(2, Spacing.PAD_MD), sticky="w")
        
        self.duration_badge = ctk.CTkLabel(
            self.info_badges, text="", font=Fonts.TINY,
            text_color=Colors.SECONDARY, fg_color=Colors.BG_INPUT,
            corner_radius=4, padx=8, pady=2
        )
        self.duration_badge.pack(side="left", padx=(0, 6))
        self.duration_badge.pack_forget()  # Ẩn ban đầu
        
        self.quality_badge = ctk.CTkLabel(
            self.info_badges, text="", font=Fonts.TINY,
            text_color=Colors.SUCCESS, fg_color=Colors.BG_INPUT,
            corner_radius=4, padx=8, pady=2
        )
        self.quality_badge.pack(side="left", padx=(0, 6))
        self.quality_badge.pack_forget()
        
        # ===== OUTPUT PATH =====
        self.path_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.path_frame.pack(fill="x", padx=Spacing.PAD_XL, pady=(Spacing.PAD_SM, 0))
        self.path_frame.grid_columnconfigure(0, weight=1)
        
        default_path = self.config.get("output_path") if self.config else os.path.join(os.path.expanduser("~"), "Downloads")
        
        self.path_entry = ctk.CTkEntry(
            self.path_frame, height=40,
            font=Fonts.SMALL, fg_color=Colors.BG_INPUT,
            border_width=1, border_color=Colors.BORDER,
            text_color=Colors.TEXT_SECONDARY,
            corner_radius=Spacing.CORNER_RADIUS_SM
        )
        self.path_entry.insert(0, default_path)
        self.path_entry.grid(row=0, column=0, padx=(0, Spacing.PAD_SM), sticky="ew")
        
        self.browse_btn = ctk.CTkButton(
            self.path_frame, text="📁", width=42, height=40,
            font=Fonts.BODY, corner_radius=Spacing.CORNER_RADIUS_SM,
            fg_color=Colors.BG_CARD, hover_color=Colors.BG_CARD_HOVER,
            border_width=1, border_color=Colors.BORDER,
            command=self._browse_folder
        )
        self.browse_btn.grid(row=0, column=1)
        
        # ===== PROGRESS AREA =====
        self.progress_frame = ctk.CTkFrame(container, fg_color=Colors.BG_CARD,
                                           corner_radius=Spacing.CORNER_RADIUS)
        self.progress_frame.pack(fill="x", padx=Spacing.PAD_XL, pady=Spacing.PAD_MD)
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame, height=Spacing.PROGRESS_HEIGHT,
            corner_radius=4, fg_color=Colors.PROGRESS_BG,
            progress_color=Colors.PROGRESS_FILL
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, padx=Spacing.PAD_MD, 
                              pady=(Spacing.PAD_MD, Spacing.PAD_SM), sticky="ew")
        
        self.progress_info = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        self.progress_info.grid(row=1, column=0, padx=Spacing.PAD_MD, 
                               pady=(0, Spacing.PAD_MD), sticky="ew")
        self.progress_info.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            self.progress_info, text="Sẵn sàng tải xuống",
            font=Fonts.CONSOLE, text_color=Colors.TEXT_SECONDARY, anchor="w"
        )
        self.status_label.grid(row=0, column=0, sticky="w")
        
        self.speed_label = ctk.CTkLabel(
            self.progress_info, text="",
            font=Fonts.CONSOLE, text_color=Colors.SUCCESS, anchor="e"
        )
        self.speed_label.grid(row=0, column=1, sticky="e")
        
        # ===== DOWNLOAD BUTTON =====
        self.download_btn = ctk.CTkButton(
            container, text="⬇  BẮT ĐẦU TẢI XUỐNG", height=Spacing.BUTTON_HEIGHT,
            font=Fonts.BUTTON_LARGE, corner_radius=Spacing.CORNER_RADIUS,
            fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
            command=self._start_download
        )
        self.download_btn.pack(fill="x", padx=Spacing.PAD_XL, pady=(Spacing.PAD_SM, Spacing.PAD_XL))
        
        # ===== CANCEL BUTTON (ẩn) =====
        self.cancel_btn = ctk.CTkButton(
            container, text="✕ HỦY TẢI", height=40,
            font=Fonts.BUTTON, corner_radius=Spacing.CORNER_RADIUS,
            fg_color=Colors.ERROR, hover_color="#CC4040",
            command=self._cancel_download
        )
        # Ban đầu ẩn
    
    # ===== ACTIONS =====
    
    def _paste_url(self):
        """Paste URL from clipboard."""
        try:
            clipboard = self.clipboard_get()
            if clipboard:
                self.url_entry.delete(0, "end")
                self.url_entry.insert(0, clipboard.strip())
                # Auto-fetch info
                self._fetch_info()
        except Exception:
            pass
    
    def _fetch_info(self):
        """Fetch video information in background."""
        url = self.url_entry.get().strip()
        if not url:
            self._update_status("Vui lòng nhập link!", "error")
            return
        
        self.fetch_btn.configure(state="disabled", text="⏳")
        self._update_status("Đang lấy thông tin...", "normal")
        
        cookie_path = ""
        if self.get_sidebar_settings:
            settings = self.get_sidebar_settings()
            cookie_path = settings.get('cookie_path', '')
        
        def _fetch():
            info = self.engine.fetch_info(url, cookie_path=cookie_path)
            self.after(0, lambda: self._display_info(info))
            self.after(0, lambda: self.fetch_btn.configure(state="normal", text="🔍"))
        
        threading.Thread(target=_fetch, daemon=True).start()
    
    def _display_info(self, info):
        """Display fetched video info."""
        if not info or info.get('error'):
            error = info.get('error', 'Không thể lấy thông tin') if info else 'Không thể lấy thông tin'
            self._update_status(f"Lỗi: {error[:80]}", "error")
            self.title_label.configure(text="❌ Không thể tải thông tin")
            return
        
        self._video_info = info
        
        # Update title
        title = info.get('title', 'Unknown')
        if len(title) > 60:
            title = title[:57] + "..."
        self.title_label.configure(text=title)
        
        # Update uploader
        uploader = info.get('uploader', '')
        if info.get('is_playlist'):
            uploader = f"📃 Playlist: {info.get('playlist_count', '?')} video • {uploader}"
        self.uploader_label.configure(text=uploader)
        
        # Duration badge
        from core.downloader import DownloadEngine
        duration = info.get('duration', 0)
        if duration:
            self.duration_badge.configure(text=f"⏱ {DownloadEngine.format_duration(duration)}")
            self.duration_badge.pack(side="left", padx=(0, 6))
        
        # Quality badge
        qualities = info.get('available_qualities', [])
        if qualities:
            self.quality_badge.configure(text=f"📺 {qualities[0]} max")
            self.quality_badge.pack(side="left", padx=(0, 6))
        
        self._update_status("✅ Sẵn sàng tải xuống", "success")
        
        # Load thumbnail
        thumb_url = info.get('thumbnail', '')
        if thumb_url:
            threading.Thread(target=self._load_thumbnail, args=(thumb_url,), daemon=True).start()
    
    def _load_thumbnail(self, url):
        """Load and display thumbnail."""
        try:
            response = requests.get(url, timeout=10, stream=True)
            if response.status_code == 200:
                img_data = BytesIO(response.content)
                img = Image.open(img_data)
                img = img.resize((160, 100), Image.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(160, 100))
                self._thumbnail_image = ctk_img  # Keep reference
                self.after(0, lambda: self.thumb_label.configure(image=ctk_img, text=""))
        except Exception:
            pass
    
    def _browse_folder(self):
        """Select output folder."""
        d = filedialog.askdirectory()
        if d:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, d)
            if self.config:
                self.config.set("output_path", d)
    
    def _update_status(self, text, status_type="normal"):
        """Update status label."""
        color_map = {
            "normal": Colors.TEXT_SECONDARY,
            "success": Colors.SUCCESS,
            "error": Colors.ERROR,
            "warning": Colors.WARNING,
        }
        color = color_map.get(status_type, Colors.TEXT_SECONDARY)
        self.status_label.configure(text=text, text_color=color)
    
    def _update_progress(self, percent, speed, eta, status_msg="Đang tải...", size_info=""):
        """Update progress bar and info with terminal-like details."""
        # 1. Cập nhật thanh progress
        self.after(0, lambda: self.progress_bar.set(percent / 100))
        
        # 2. Cập nhật nhãn trạng thái (ví dụ: [Đang tải Video] 45% (15 MB / 100 MB))
        display_status = f"[{status_msg}] {int(percent)}%"
        if size_info:
            display_status += f"  ({size_info})"
            
        self.after(0, lambda: self.status_label.configure(
            text=display_status, text_color=Colors.SECONDARY
        ))
        
        # 3. Cập nhật nhãn tốc độ và ETA
        speed_text = f"⚡ {speed}" if speed and speed != 'N/A' else ""
        if eta and eta != 'N/A':
            speed_text += f"  •  ⏱ {eta}"
        self.after(0, lambda: self.speed_label.configure(text=speed_text))
    
    def _start_download(self):
        """Start download in background thread."""
        url = self.url_entry.get().strip()
        if not url:
            self._update_status("⚠ Vui lòng nhập link!", "error")
            return
        
        if self._is_downloading:
            return
        
        self._is_downloading = True
        self.download_btn.configure(state="disabled", text="⏳ ĐANG KẾT NỐI...",
                                   fg_color=Colors.TEXT_MUTED)
        self.progress_bar.set(0)
        self.speed_label.configure(text="")
        
        # Get settings from sidebar
        settings = self.get_sidebar_settings() if self.get_sidebar_settings else {}
        mode = settings.get('mode', 'MP4')
        quality = settings.get('quality', '1080p')
        bitrate = settings.get('bitrate', '320k')
        is_playlist = settings.get('is_playlist', False)
        cookie_path = settings.get('cookie_path', '')
        output_path = self.path_entry.get().strip()
        
        # Save settings
        if self.config:
            self.config.set("output_path", output_path, auto_save=False)
            self.config.set("last_mode", mode, auto_save=False)
            self.config.set("last_video_quality", quality, auto_save=False)
            self.config.set("last_audio_bitrate", bitrate)
        
        # Update button color based on mode
        btn_color = Colors.MP3_COLOR if mode == "MP3" else Colors.PRIMARY
        self.download_btn.configure(fg_color=btn_color)
        
        def _download():
            try:
                result = self.engine.download(
                    url=url,
                    output_path=output_path,
                    mode=mode,
                    quality=quality,
                    bitrate=bitrate,
                    is_playlist=is_playlist,
                    cookie_path=cookie_path,
                    progress_callback=self._update_progress,
                    log_callback=self.log_callback,
                )
                
                if result.get('success'):
                    self.after(0, lambda: self._on_download_complete(result))
                else:
                    error = result.get('error', 'Unknown error')
                    self.after(0, lambda: self._on_download_error(error))
            except Exception as e:
                self.after(0, lambda: self._on_download_error(str(e)))
        
        threading.Thread(target=_download, daemon=True).start()
    
    def _cancel_download(self):
        """Cancel current download."""
        if self.engine:
            self.engine.cancel()
        self._update_status("⏹ Đã hủy tải xuống", "warning")
        self._reset_download_state()
    
    def _on_download_complete(self, result):
        """Handle successful download."""
        from core.downloader import DownloadEngine
        filename = result.get('filename', 'Unknown')
        filesize = DownloadEngine.format_filesize(result.get('filesize', 0))
        
        self._update_status(f"✅ Hoàn tất: {filename} ({filesize})", "success")
        self.progress_bar.set(1.0)
        self.speed_label.configure(text="")
        
        if self.log_callback:
            self.log_callback(f"✅ Đã tải thành công: {filename} ({filesize})")
        
        # Add to history
        if self.config:
            self.config.add_history(result)
        
        self._reset_download_state()
    
    def _on_download_error(self, error):
        """Handle download error."""
        self._update_status(f"❌ Thất bại: {error[:80]}", "error")
        if self.log_callback:
            self.log_callback(f"❌ Lỗi: {error}")
        self._reset_download_state()
    
    def _reset_download_state(self):
        """Reset UI after download completes/fails."""
        self._is_downloading = False
        
        # Get current mode for button color
        mode = "MP4"
        if self.get_sidebar_settings:
            settings = self.get_sidebar_settings()
            mode = settings.get('mode', 'MP4')
        
        btn_color = Colors.MP3_COLOR if mode == "MP3" else Colors.PRIMARY
        hover_color = Colors.MP3_HOVER if mode == "MP3" else Colors.PRIMARY_HOVER
        
        self.download_btn.configure(
            state="normal", 
            text="⬇  BẮT ĐẦU TẢI XUỐNG",
            fg_color=btn_color,
            hover_color=hover_color
        )
    
    def update_mode(self, mode):
        """Called when mode changes in sidebar."""
        btn_color = Colors.MP3_COLOR if mode == "MP3" else Colors.PRIMARY
        hover_color = Colors.MP3_HOVER if mode == "MP3" else Colors.PRIMARY_HOVER
        if not self._is_downloading:
            self.download_btn.configure(fg_color=btn_color, hover_color=hover_color)
            if mode == "MP3":
                self.download_btn.configure(text="🎵  TẢI NHẠC MP3")
            else:
                self.download_btn.configure(text="⬇  BẮT ĐẦU TẢI XUỐNG")
