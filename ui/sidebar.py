"""
Titanium Downloader - Sidebar Component
Navigation sidebar với branding, mode selector, và quick settings.
"""
import customtkinter as ctk
from tkinter import filedialog
from .theme import Colors, Fonts, Spacing


class Sidebar(ctk.CTkFrame):
    """Modern sidebar with navigation and settings."""
    
    def __init__(self, master, on_mode_change=None, on_cookie_select=None,
                 on_playlist_toggle=None, ffmpeg_ok=True, **kwargs):
        super().__init__(master, width=Spacing.SIDEBAR_WIDTH, corner_radius=0,
                        fg_color=Colors.SIDEBAR_BG, **kwargs)
        
        self.on_mode_change = on_mode_change
        self.on_cookie_select = on_cookie_select
        self.on_playlist_toggle = on_playlist_toggle
        
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(10, weight=1)  # Spacer
        
        row = 0
        
        # ===== LOGO =====
        self.logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.logo_frame.grid(row=row, column=0, padx=Spacing.PAD_XL, pady=(30, 5), sticky="ew")
        
        self.logo_icon = ctk.CTkLabel(self.logo_frame, text="⚡", 
                                       font=(Fonts.FAMILY, 32))
        self.logo_icon.pack(anchor="center")
        
        self.logo_label = ctk.CTkLabel(self.logo_frame, text="TITANIUM",
                                       font=Fonts.LOGO, text_color=Colors.PRIMARY)
        self.logo_label.pack(anchor="center")
        
        self.subtitle = ctk.CTkLabel(self.logo_frame, text="Universal Downloader",
                                     font=Fonts.SMALL, text_color=Colors.TEXT_SECONDARY)
        self.subtitle.pack(anchor="center")
        
        row += 1
        
        # ===== DIVIDER =====
        self.div1 = ctk.CTkFrame(self, height=1, fg_color=Colors.BORDER)
        self.div1.grid(row=row, column=0, padx=Spacing.PAD_XL, pady=Spacing.PAD_LG, sticky="ew")
        row += 1
        
        # ===== MODE SELECTOR (MP3 / MP4) =====
        self.mode_label = ctk.CTkLabel(self, text="CHẾ ĐỘ TẢI", 
                                       font=Fonts.SMALL_BOLD, text_color=Colors.TEXT_SECONDARY)
        self.mode_label.grid(row=row, column=0, padx=Spacing.PAD_XL, pady=(0, Spacing.PAD_SM), sticky="w")
        row += 1
        
        self.mode_var = ctk.StringVar(value="MP4")
        
        self.mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mode_frame.grid(row=row, column=0, padx=Spacing.PAD_XL, pady=(0, Spacing.PAD_MD), sticky="ew")
        self.mode_frame.grid_columnconfigure(0, weight=1)
        self.mode_frame.grid_columnconfigure(1, weight=1)
        
        self.mp4_btn = ctk.CTkButton(
            self.mode_frame, text="🎬 MP4", height=42,
            font=Fonts.BUTTON, corner_radius=Spacing.CORNER_RADIUS_SM,
            fg_color=Colors.MP4_COLOR, hover_color=Colors.MP4_HOVER,
            command=lambda: self._set_mode("MP4")
        )
        self.mp4_btn.grid(row=0, column=0, padx=(0, 4), sticky="ew")
        
        self.mp3_btn = ctk.CTkButton(
            self.mode_frame, text="🎵 MP3", height=42,
            font=Fonts.BUTTON, corner_radius=Spacing.CORNER_RADIUS_SM,
            fg_color=Colors.BG_CARD, hover_color=Colors.BG_CARD_HOVER,
            border_width=1, border_color=Colors.BORDER,
            command=lambda: self._set_mode("MP3")
        )
        self.mp3_btn.grid(row=0, column=1, padx=(4, 0), sticky="ew")
        
        row += 1
        
        # ===== QUALITY SELECTOR =====
        self.quality_label = ctk.CTkLabel(self, text="CHẤT LƯỢNG VIDEO",
                                          font=Fonts.SMALL_BOLD, text_color=Colors.TEXT_SECONDARY)
        self.quality_label.grid(row=row, column=0, padx=Spacing.PAD_XL, pady=(Spacing.PAD_MD, Spacing.PAD_SM), sticky="w")
        row += 1
        
        self.quality_var = ctk.StringVar(value="1080p")
        self.quality_menu = ctk.CTkOptionMenu(
            self, values=["4K", "2K", "1080p", "720p", "480p"],
            variable=self.quality_var,
            height=38, corner_radius=Spacing.CORNER_RADIUS_SM,
            fg_color=Colors.BG_INPUT, button_color=Colors.PRIMARY,
            button_hover_color=Colors.PRIMARY_HOVER,
            dropdown_fg_color=Colors.BG_CARD,
            dropdown_hover_color=Colors.BG_CARD_HOVER,
            font=Fonts.BODY_BOLD
        )
        self.quality_menu.grid(row=row, column=0, padx=Spacing.PAD_XL, sticky="ew")
        row += 1
        
        # ===== AUDIO BITRATE (hiển thị khi MP3) =====
        self.bitrate_label = ctk.CTkLabel(self, text="CHẤT LƯỢNG AUDIO",
                                          font=Fonts.SMALL_BOLD, text_color=Colors.TEXT_SECONDARY)
        self.bitrate_label.grid(row=row, column=0, padx=Spacing.PAD_XL, 
                               pady=(Spacing.PAD_MD, Spacing.PAD_SM), sticky="w")
        row += 1
        
        self.bitrate_var = ctk.StringVar(value="320k")
        self.bitrate_menu = ctk.CTkOptionMenu(
            self, values=["320k (Tối đa)", "256k", "192k", "128k"],
            variable=self.bitrate_var,
            height=38, corner_radius=Spacing.CORNER_RADIUS_SM,
            fg_color=Colors.BG_INPUT, button_color=Colors.MP3_COLOR,
            button_hover_color=Colors.MP3_HOVER,
            dropdown_fg_color=Colors.BG_CARD,
            dropdown_hover_color=Colors.BG_CARD_HOVER,
            font=Fonts.BODY_BOLD
        )
        self.bitrate_menu.grid(row=row, column=0, padx=Spacing.PAD_XL, sticky="ew")
        row += 1
        
        # Ban đầu ẩn bitrate (MP4 mode)
        self.bitrate_label.grid_remove()
        self.bitrate_menu.grid_remove()
        
        # ===== DIVIDER =====
        self.div2 = ctk.CTkFrame(self, height=1, fg_color=Colors.BORDER)
        self.div2.grid(row=row, column=0, padx=Spacing.PAD_XL, pady=Spacing.PAD_LG, sticky="ew")
        row += 1
        
        # ===== OPTIONS =====
        self.playlist_var = ctk.BooleanVar(value=False)
        self.playlist_sw = ctk.CTkSwitch(
            self, text="Tải cả Playlist", variable=self.playlist_var,
            font=Fonts.BODY, text_color=Colors.TEXT_PRIMARY,
            progress_color=Colors.PRIMARY,
            button_color=Colors.TEXT_SECONDARY,
            button_hover_color=Colors.PRIMARY_LIGHT,
            command=lambda: on_playlist_toggle(self.playlist_var.get()) if on_playlist_toggle else None
        )
        self.playlist_sw.grid(row=row, column=0, padx=Spacing.PAD_XL, pady=Spacing.PAD_SM, sticky="w")
        row += 1
        
        # Spacer
        row = 10
        
        # ===== FFMPEG STATUS =====
        self.status_frame = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=Spacing.CORNER_RADIUS_SM)
        self.status_frame.grid(row=11, column=0, padx=Spacing.PAD_XL, pady=(0, Spacing.PAD_SM), sticky="ew")
        
        if ffmpeg_ok:
            ff_text = "✅ FFmpeg hoạt động"
            ff_color = Colors.SUCCESS
        else:
            ff_text = "⚠️ FFmpeg không tìm thấy"
            ff_color = Colors.WARNING
        
        self.ffmpeg_status = ctk.CTkLabel(
            self.status_frame, text=ff_text,
            font=Fonts.SMALL_BOLD, text_color=ff_color
        )
        self.ffmpeg_status.pack(pady=Spacing.PAD_SM)
        
        # ===== COOKIE BUTTON =====
        self.cookie_btn = ctk.CTkButton(
            self, text="🍪 Nạp Cookies", height=36,
            font=Fonts.SMALL_BOLD, corner_radius=Spacing.CORNER_RADIUS_SM,
            fg_color="transparent", hover_color=Colors.SIDEBAR_HOVER,
            border_width=1, border_color=Colors.BORDER,
            text_color=Colors.TEXT_SECONDARY,
            command=self._select_cookie
        )
        self.cookie_btn.grid(row=12, column=0, padx=Spacing.PAD_XL, pady=(0, Spacing.PAD_XL), sticky="ew")
    
    def _set_mode(self, mode):
        """Switch between MP3 and MP4 mode."""
        self.mode_var.set(mode)
        
        if mode == "MP4":
            self.mp4_btn.configure(fg_color=Colors.MP4_COLOR, hover_color=Colors.MP4_HOVER,
                                   border_width=0)
            self.mp3_btn.configure(fg_color=Colors.BG_CARD, hover_color=Colors.BG_CARD_HOVER,
                                   border_width=1, border_color=Colors.BORDER)
            # Hiện quality, ẩn bitrate
            self.quality_label.grid()
            self.quality_menu.grid()
            self.bitrate_label.grid_remove()
            self.bitrate_menu.grid_remove()
        else:
            self.mp3_btn.configure(fg_color=Colors.MP3_COLOR, hover_color=Colors.MP3_HOVER,
                                   border_width=0)
            self.mp4_btn.configure(fg_color=Colors.BG_CARD, hover_color=Colors.BG_CARD_HOVER,
                                   border_width=1, border_color=Colors.BORDER)
            # Ẩn quality, hiện bitrate
            self.quality_label.grid_remove()
            self.quality_menu.grid_remove()
            self.bitrate_label.grid()
            self.bitrate_menu.grid()
        
        if self.on_mode_change:
            self.on_mode_change(mode)
    
    def _select_cookie(self):
        """Open file dialog to select cookies.txt."""
        f = filedialog.askopenfilename(
            title="Chọn Cookies.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if f:
            self.cookie_btn.configure(text="🍪 Đã nạp cookies", text_color=Colors.SUCCESS)
            if self.on_cookie_select:
                self.on_cookie_select(f)
    
    def get_mode(self):
        return self.mode_var.get()
    
    def get_quality(self):
        return self.quality_var.get()
    
    def get_bitrate(self):
        val = self.bitrate_var.get()
        # Extract just the bitrate value (e.g., "320k (Tối đa)" -> "320k")
        return val.split(" ")[0] if " " in val else val
    
    def get_is_playlist(self):
        return self.playlist_var.get()
