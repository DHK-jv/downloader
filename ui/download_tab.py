"""
Titanium Downloader - Download Tab
Giao diện chính để nhận link tải, hiển thị preview, và chọn lựa các video trong playlist.
"""
import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import requests
from io import BytesIO
from PIL import Image
from .theme import Colors, Fonts, Spacing
from .icons import Icons
from core.utils import format_duration


class DownloadTab(ctk.CTkFrame):
    """Tab chính xử lý nhập URL, hiển thị thông tin và chọn tệp để tải."""
    
    def __init__(self, master, download_engine=None, queue_manager=None, config=None, 
                 get_sidebar_settings=None, log_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.engine = download_engine
        self.queue_manager = queue_manager
        self.config = config
        self.get_sidebar_settings = get_sidebar_settings
        self.log_callback = log_callback
        
        self._video_info = None
        self.playlist_items = []  # Lưu list dict check của playlist: [{'url', 'title', 'var', 'checkbox'}]
        self._thumbnail_image = None
        self.session = requests.Session()
        
        # Layout chính
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Scrollable container chính của tab
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=Colors.BG_CARD,
            scrollbar_button_hover_color=Colors.PRIMARY
        )
        self.scroll.pack(fill="both", expand=True)
        self.scroll.grid_columnconfigure(0, weight=1)
        
        container = self.scroll
        
        # ===== HEADER =====
        self.header = ctk.CTkLabel(
            container, text="Tải Video & Âm Nhạc", 
            font=Fonts.HEADING, text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        self.header.pack(fill="x", padx=Spacing.PAD_XL, pady=(Spacing.PAD_XL, 4))
        
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
            placeholder_text=" Dán link video hoặc playlist vào đây...",
            font=Fonts.BODY, border_width=0,
            fg_color="transparent", text_color=Colors.TEXT_PRIMARY,
            placeholder_text_color=Colors.TEXT_MUTED
        )
        self.url_entry.grid(row=0, column=0, padx=(Spacing.PAD_MD, 0), sticky="ew")
        
        self.paste_btn = ctk.CTkButton(
            self.url_frame, text=" Dán link", width=100, height=36,
            font=Fonts.SMALL_BOLD, corner_radius=Spacing.CORNER_RADIUS_SM,
            fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
            image=Icons.get("paste", size=14), compound="left",
            command=self._paste_url
        )
        self.paste_btn.grid(row=0, column=1, padx=Spacing.PAD_SM, pady=Spacing.PAD_SM)
        
        self.fetch_btn = ctk.CTkButton(
            self.url_frame, text="", width=40, height=36,
            font=Fonts.BODY, corner_radius=Spacing.CORNER_RADIUS_SM,
            fg_color=Colors.SECONDARY, hover_color=Colors.SECONDARY_HOVER,
            text_color=Colors.BG_DARKEST,
            image=Icons.get("search", size=16),
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
            self.preview_card, text="", 
            width=160, height=100,
            font=Fonts.SMALL, text_color=Colors.TEXT_MUTED,
            fg_color=Colors.BG_INPUT, corner_radius=Spacing.CORNER_RADIUS_SM,
            image=Icons.get("download", size=36)
        )
        self.thumb_label.grid(row=0, column=0, rowspan=3, padx=Spacing.PAD_MD, 
                              pady=Spacing.PAD_MD, sticky="nsew")
        
        # Video info
        self.title_label = ctk.CTkLabel(
            self.preview_card, text="Chưa có thông tin video. Hãy nhập link ở trên và tìm kiếm.",
            font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY,
            anchor="w", justify="left", wraplength=450
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
        self.duration_badge.pack_forget()
        
        self.quality_badge = ctk.CTkLabel(
            self.info_badges, text="", font=Fonts.TINY,
            text_color=Colors.SUCCESS, fg_color=Colors.BG_INPUT,
            corner_radius=4, padx=8, pady=2
        )
        self.quality_badge.pack(side="left", padx=(0, 6))
        self.quality_badge.pack_forget()

        # Status label
        self.status_label = ctk.CTkLabel(
            container, text="Trạng thái: Sẵn sàng nhận liên kết",
            font=Fonts.SMALL, text_color=Colors.TEXT_MUTED, anchor="w"
        )
        self.status_label.pack(fill="x", padx=Spacing.PAD_XL, pady=(0, Spacing.PAD_SM))

        # ===== SMART PLAYLIST SELECTOR FRAME =====
        self.playlist_frame = ctk.CTkFrame(
            container, fg_color=Colors.BG_CARD,
            corner_radius=Spacing.CORNER_RADIUS,
            border_width=1, border_color=Colors.BORDER
        )
        # Ẩn ban đầu, chỉ pack khi tìm thấy playlist
        
        # Playlist Header
        self.pl_header = ctk.CTkFrame(self.playlist_frame, fg_color="transparent")
        self.pl_header.pack(fill="x", padx=Spacing.PAD_MD, pady=Spacing.PAD_MD)
        self.pl_header.grid_columnconfigure(0, weight=1)
        
        self.pl_title_lbl = ctk.CTkLabel(
            self.pl_header, text="Trình chọn Playlist thông minh",
            font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY, anchor="w"
        )
        self.pl_title_lbl.grid(row=0, column=0, sticky="w")
        
        self.pl_actions = ctk.CTkFrame(self.pl_header, fg_color="transparent")
        self.pl_actions.grid(row=0, column=1, sticky="e")
        
        self.select_all_btn = ctk.CTkButton(
            self.pl_actions, text="Chọn hết", width=70, height=26,
            font=Fonts.SMALL_BOLD, fg_color=Colors.BG_INPUT,
            hover_color=Colors.BG_CARD_HOVER, text_color=Colors.TEXT_PRIMARY,
            command=lambda: self._select_all_playlist(True)
        )
        self.select_all_btn.pack(side="left", padx=2)
        
        self.deselect_all_btn = ctk.CTkButton(
            self.pl_actions, text="Bỏ chọn", width=70, height=26,
            font=Fonts.SMALL_BOLD, fg_color=Colors.BG_INPUT,
            hover_color=Colors.BG_CARD_HOVER, text_color=Colors.TEXT_PRIMARY,
            command=lambda: self._select_all_playlist(False)
        )
        self.deselect_all_btn.pack(side="left", padx=2)
        
        # List checklist frame
        self.pl_list_frame = ctk.CTkFrame(self.playlist_frame, fg_color="transparent")
        self.pl_list_frame.pack(fill="x", padx=Spacing.PAD_MD, pady=(0, Spacing.PAD_MD))
        
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
            self.path_frame, text="", width=42, height=40,
            font=Fonts.BODY, corner_radius=Spacing.CORNER_RADIUS_SM,
            fg_color=Colors.BG_CARD, hover_color=Colors.BG_CARD_HOVER,
            border_width=1, border_color=Colors.BORDER,
            image=Icons.get("folder", size=16),
            command=self._browse_folder
        )
        self.browse_btn.grid(row=0, column=1)
        
        # ===== DOWNLOAD BUTTON =====
        self.download_btn = ctk.CTkButton(
            container, text=" TẢI XUỐNG NGAY", height=Spacing.BUTTON_HEIGHT,
            font=Fonts.BUTTON_LARGE, corner_radius=Spacing.CORNER_RADIUS,
            fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
            image=Icons.get("download", size=18), compound="left",
            command=self._start_download
        )
        self.download_btn.pack(fill="x", padx=Spacing.PAD_XL, pady=(Spacing.PAD_MD, Spacing.PAD_XL))

    # ===== ACTIONS =====
    
    def _paste_url(self):
        """Dán link từ clipboard và tự tìm kiếm."""
        try:
            clipboard = self.clipboard_get()
            if clipboard:
                self.url_entry.delete(0, "end")
                self.url_entry.insert(0, clipboard.strip())
                self._fetch_info()
        except Exception:
            pass
    
    def _fetch_info(self):
        """Lấy thông tin video ở chế độ bất đồng bộ."""
        url = self.url_entry.get().strip()
        if not url:
            self._update_status("Vui lòng nhập link!", "error")
            return
        
        # Ẩn playlist selector cũ
        self.playlist_frame.pack_forget()
        for item in self.playlist_items:
            item['checkbox'].destroy()
        self.playlist_items.clear()
        
        self.fetch_btn.configure(state="disabled")
        self._update_status("Đang phân tích liên kết...", "normal")
        self.title_label.configure(text="Đang phân tích...")
        self.uploader_label.configure(text="")
        self.duration_badge.pack_forget()
        self.quality_badge.pack_forget()
        self.thumb_label.configure(image=Icons.get("download", size=36))
        
        cookie_path = ""
        if self.get_sidebar_settings:
            settings = self.get_sidebar_settings()
            cookie_path = settings.get('cookie_path', '')
        
        def _fetch():
            info = self.engine.fetch_info(url, cookie_path=cookie_path)
            self.after(0, lambda: self._display_info(info))
            self.after(0, lambda: self.fetch_btn.configure(state="normal"))
        
        threading.Thread(target=_fetch, daemon=True).start()
    
    def _display_info(self, info):
        """Hiển thị thông tin video vừa lấy được."""
        if not info or info.get('error'):
            error = info.get('error', 'Không thể lấy thông tin') if info else 'Không thể lấy thông tin'
            self._update_status(f"Lỗi phân tích: {error[:80]}", "error")
            self.title_label.configure(text="Không thể nhận dạng liên kết này. Thử lại hoặc đổi link khác.")
            return
        
        self._video_info = info
        
        # Title
        title = info.get('title', 'Unknown')
        if len(title) > 60:
            title = title[:57] + "..."
        self.title_label.configure(text=title)
        
        # Uploader
        uploader = info.get('uploader', '')
        if info.get('is_playlist'):
            uploader = f"Playlist: {info.get('playlist_count', '?')} video • {uploader}"
        self.uploader_label.configure(text=uploader)
        
        # Duration badge
        duration = info.get('duration', 0)
        if duration:
            self.duration_badge.configure(text=f"⏱ {format_duration(duration)}")
            self.duration_badge.pack(side="left", padx=(0, 6))
        
        # Quality badge
        qualities = info.get('available_qualities', [])
        if qualities:
            self.quality_badge.configure(text=f"📺 {qualities[0]} max")
            self.quality_badge.pack(side="left", padx=(0, 6))
        
        self._update_status("Phân tích thành công! Sẵn sàng tải xuống.", "success")
        
        # Tải thumbnail
        thumb_url = info.get('thumbnail', '')
        if thumb_url:
            threading.Thread(target=self._load_thumbnail, args=(thumb_url,), daemon=True).start()
            
        # Nếu là playlist, bật Smart Selector
        if info.get('is_playlist'):
            self._load_playlist_selector(info.get('webpage_url', self.url_entry.get().strip()))

    def _load_thumbnail(self, url):
        """Tải thumbnail chạy ngầm."""
        try:
            with self.session.get(url, timeout=8, stream=True) as response:
                if response.status_code == 200:
                    img_data = BytesIO(response.content)
                    img = Image.open(img_data)
                    img = img.resize((160, 100), Image.LANCZOS)
                    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(160, 100))
                    self._thumbnail_image = ctk_img
                    self.after(0, lambda: self.thumb_label.configure(image=ctk_img, text=""))
        except Exception:
            pass

    def _load_playlist_selector(self, url):
        """Bật khung và tải danh sách video trong playlist."""
        self.playlist_frame.pack(fill="x", padx=Spacing.PAD_XL, pady=Spacing.PAD_MD, after=self.preview_card)
        self.pl_title_lbl.configure(text="Đang tải danh sách video trong playlist...")
        
        cookie_path = ""
        if self.get_sidebar_settings:
            settings = self.get_sidebar_settings()
            cookie_path = settings.get('cookie_path', '')
            
        def _fetch_entries():
            res = self.engine.fetch_playlist_entries(url, cookie_path=cookie_path)
            self.after(0, lambda: self._display_playlist_entries(res))
            
        threading.Thread(target=_fetch_entries, daemon=True).start()

    def _display_playlist_entries(self, result):
        """Vẽ danh sách checklist video của playlist."""
        if not result or result.get('error'):
            err = result.get('error', 'Lỗi không rõ') if result else 'Lỗi không rõ'
            self.pl_title_lbl.configure(text=f"❌ Lỗi tải danh sách: {err[:50]}")
            return
            
        playlist_title = result.get('playlist_title', 'Playlist')
        entries = result.get('entries', [])
        
        self.pl_title_lbl.configure(text=f"Chọn video để tải ({len(entries)} video):")
        
        # Tạo checklist các video
        for i, entry in enumerate(entries):
            var = ctk.BooleanVar(value=True)
            
            duration_str = ""
            if entry.get('duration'):
                duration_str = f" [{format_duration(entry['duration'])}]"
                
            entry_title = entry.get('title', 'Video Unknown')
            display_text = f"{i+1}. {entry_title}{duration_str}"
            if len(display_text) > 75:
                display_text = display_text[:72] + "..."
                
            cb = ctk.CTkCheckBox(
                self.pl_list_frame, text=display_text, variable=var,
                font=Fonts.SMALL, text_color=Colors.TEXT_PRIMARY,
                fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_LIGHT,
                corner_radius=Spacing.CORNER_RADIUS_SM - 2
            )
            cb.pack(fill="x", padx=Spacing.PAD_MD, pady=4, anchor="w")
            
            self.playlist_items.append({
                'url': entry.get('url'),
                'title': entry_title,
                'var': var,
                'checkbox': cb
            })

    def _select_all_playlist(self, select=True):
        """Chọn tất cả hoặc bỏ chọn tất cả các video playlist."""
        for item in self.playlist_items:
            item['var'].set(select)

    def _browse_folder(self):
        """Chọn thư mục lưu file."""
        d = filedialog.askdirectory()
        if d:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, d)
            if self.config:
                self.config.set("output_path", d)

    def _update_status(self, text, status_type="normal"):
        color_map = {
            "normal": Colors.TEXT_SECONDARY,
            "success": Colors.SUCCESS,
            "error": Colors.ERROR,
            "warning": Colors.WARNING,
        }
        color = color_map.get(status_type, Colors.TEXT_SECONDARY)
        self.status_label.configure(text=f"Trạng thái: {text}", text_color=color)

    def _start_download(self):
        """Đẩy các tiến trình tải vào hàng đợi và chuyển tab."""
        url = self.url_entry.get().strip()
        if not url:
            self._update_status("Vui lòng nhập link!", "error")
            return
            
        settings = self.get_sidebar_settings() if self.get_sidebar_settings else {}
        mode = settings.get('mode', 'MP4')
        quality = settings.get('quality', '1080p')
        bitrate = settings.get('bitrate', '320k')
        cookie_path = settings.get('cookie_path', '')
        output_path = self.path_entry.get().strip()
        
        # Lưu cấu hình mặc định
        if self.config:
            self.config.set("output_path", output_path, auto_save=False)
            self.config.set("last_mode", mode, auto_save=False)
            self.config.set("last_video_quality", quality, auto_save=False)
            self.config.set("last_audio_bitrate", bitrate)
            
        # 1. Nếu đang hiển thị Playlist Selector
        if self.playlist_items:
            selected_tasks = []
            for item in self.playlist_items:
                if item['var'].get():
                    selected_tasks.append((item['url'], item['title']))
                    
            if not selected_tasks:
                self._update_status("Hãy chọn ít nhất 1 video trong danh sách để tải!", "warning")
                return
                
            # Đẩy hàng loạt vào Queue Manager
            for video_url, video_title in selected_tasks:
                self.queue_manager.add_task(
                    url=video_url,
                    mode=mode,
                    quality=quality,
                    bitrate=bitrate,
                    output_path=output_path,
                    cookie_path=cookie_path,
                    title=video_title
                )
                
            self._update_status(f"Đã thêm {len(selected_tasks)} nhiệm vụ vào Hàng Đợi!", "success")
            
        # 2. Nếu là tải link đơn thông thường
        else:
            video_title = self._video_info.get('title') if self._video_info else None
            self.queue_manager.add_task(
                url=url,
                mode=mode,
                quality=quality,
                bitrate=bitrate,
                output_path=output_path,
                cookie_path=cookie_path,
                title=video_title
            )
            self._update_status("Đã thêm vào Hàng Đợi tải xuống!", "success")
            
        # Tự động nhảy sang tab Hàng Đợi (Queue Manager) để người dùng theo dõi
        try:
            self.master.master.set("Hàng Đợi")
        except Exception:
            pass

    def update_mode(self, mode):
        """Được gọi khi người dùng thay đổi MP3/MP4 từ sidebar."""
        btn_color = Colors.MP3_COLOR if mode == "MP3" else Colors.PRIMARY
        hover_color = Colors.MP3_HOVER if mode == "MP3" else Colors.PRIMARY_HOVER
        self.download_btn.configure(fg_color=btn_color, hover_color=hover_color)
        if mode == "MP3":
            self.download_btn.configure(text=" TẢI NHẠC MP3")
        else:
            self.download_btn.configure(text=" TẢI XUỐNG NGAY")
