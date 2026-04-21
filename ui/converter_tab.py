"""
Titanium Downloader - Converter Tab
Chuyển đổi định dạng file video/audio.
"""
import customtkinter as ctk
from tkinter import filedialog
import threading
import os
from .theme import Colors, Fonts, Spacing


class ConverterTab(ctk.CTkFrame):
    """File format converter tab."""
    
    def __init__(self, master, converter=None, log_callback=None, 
                 ffmpeg_ok=True, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.converter = converter
        self.log_callback = log_callback
        self.ffmpeg_ok = ffmpeg_ok
        
        self.grid_columnconfigure(0, weight=1)
        
        row = 0
        
        # ===== HEADER =====
        ctk.CTkLabel(
            self, text="🔄 Chuyển Đổi Định Dạng",
            font=Fonts.HEADING, text_color=Colors.TEXT_PRIMARY, anchor="w"
        ).grid(row=row, column=0, padx=Spacing.PAD_XL, 
               pady=(Spacing.PAD_XL, Spacing.PAD_SM), sticky="w")
        row += 1
        
        ctk.CTkLabel(
            self, text="Chuyển đổi giữa các định dạng video và audio phổ biến",
            font=Fonts.SMALL, text_color=Colors.TEXT_MUTED, anchor="w"
        ).grid(row=row, column=0, padx=Spacing.PAD_XL, 
               pady=(0, Spacing.PAD_LG), sticky="w")
        row += 1
        
        # ===== FFmpeg Warning =====
        if not ffmpeg_ok:
            warn_frame = ctk.CTkFrame(self, fg_color=Colors.WARNING_BG, 
                                      corner_radius=Spacing.CORNER_RADIUS_SM,
                                      border_width=1, border_color=Colors.WARNING)
            warn_frame.grid(row=row, column=0, padx=Spacing.PAD_XL, 
                           pady=(0, Spacing.PAD_LG), sticky="ew")
            ctk.CTkLabel(
                warn_frame, 
                text="⚠️ FFmpeg không tìm thấy. Tính năng chuyển đổi cần FFmpeg để hoạt động.",
                font=Fonts.SMALL_BOLD, text_color=Colors.WARNING,
                wraplength=500
            ).pack(padx=Spacing.PAD_MD, pady=Spacing.PAD_MD)
            row += 1
        
        # ===== INPUT FILE =====
        self.input_card = ctk.CTkFrame(self, fg_color=Colors.BG_CARD,
                                       corner_radius=Spacing.CORNER_RADIUS,
                                       border_width=1, border_color=Colors.BORDER)
        self.input_card.grid(row=row, column=0, padx=Spacing.PAD_XL, sticky="ew")
        self.input_card.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.input_card, text="📄 File nguồn",
            font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY, anchor="w"
        ).grid(row=0, column=0, padx=Spacing.PAD_MD, pady=(Spacing.PAD_MD, Spacing.PAD_SM), 
               sticky="w", columnspan=2)
        
        self.file_entry = ctk.CTkEntry(
            self.input_card, height=40,
            placeholder_text="Chọn file video hoặc audio...",
            font=Fonts.SMALL, fg_color=Colors.BG_INPUT,
            border_width=0, text_color=Colors.TEXT_PRIMARY,
            corner_radius=Spacing.CORNER_RADIUS_SM
        )
        self.file_entry.grid(row=1, column=0, padx=(Spacing.PAD_MD, Spacing.PAD_SM), 
                            pady=(0, Spacing.PAD_MD), sticky="ew")
        
        self.select_file_btn = ctk.CTkButton(
            self.input_card, text="📁 Chọn", width=80, height=40,
            font=Fonts.SMALL_BOLD, corner_radius=Spacing.CORNER_RADIUS_SM,
            fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
            command=self._select_file
        )
        self.select_file_btn.grid(row=1, column=1, padx=(0, Spacing.PAD_MD), 
                                 pady=(0, Spacing.PAD_MD))
        
        row += 1
        
        # ===== OUTPUT FORMAT =====
        self.format_card = ctk.CTkFrame(self, fg_color=Colors.BG_CARD,
                                        corner_radius=Spacing.CORNER_RADIUS,
                                        border_width=1, border_color=Colors.BORDER)
        self.format_card.grid(row=row, column=0, padx=Spacing.PAD_XL, 
                             pady=Spacing.PAD_MD, sticky="ew")
        
        ctk.CTkLabel(
            self.format_card, text="🎯 Định dạng đích",
            font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY, anchor="w"
        ).pack(anchor="w", padx=Spacing.PAD_MD, pady=(Spacing.PAD_MD, Spacing.PAD_SM))
        
        # Format buttons grid
        self.format_grid = ctk.CTkFrame(self.format_card, fg_color="transparent")
        self.format_grid.pack(fill="x", padx=Spacing.PAD_MD, pady=(0, Spacing.PAD_MD))
        
        self.format_var = ctk.StringVar(value="mp3")
        
        formats = [
            ("🎵 MP3", "mp3"), ("🎬 MP4", "mp4"), ("🎵 WAV", "wav"),
            ("🎬 MKV", "mkv"), ("🎵 FLAC", "flac"), ("🎬 AVI", "avi"),
        ]
        
        for i, (label, fmt) in enumerate(formats):
            btn = ctk.CTkRadioButton(
                self.format_grid, text=label, variable=self.format_var,
                value=fmt, font=Fonts.BODY,
                text_color=Colors.TEXT_PRIMARY,
                fg_color=Colors.PRIMARY,
                border_color=Colors.BORDER,
                hover_color=Colors.PRIMARY_LIGHT
            )
            btn.grid(row=i // 3, column=i % 3, padx=Spacing.PAD_SM, 
                    pady=Spacing.PAD_SM, sticky="w")
        
        row += 1
        
        # ===== PROGRESS =====
        self.conv_progress = ctk.CTkProgressBar(
            self, height=Spacing.PROGRESS_HEIGHT,
            corner_radius=4, fg_color=Colors.PROGRESS_BG,
            progress_color=Colors.WARNING
        )
        self.conv_progress.set(0)
        self.conv_progress.grid(row=row, column=0, padx=Spacing.PAD_XL, pady=Spacing.PAD_SM, sticky="ew")
        row += 1
        
        self.conv_status = ctk.CTkLabel(
            self, text="", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED
        )
        self.conv_status.grid(row=row, column=0, padx=Spacing.PAD_XL, sticky="w")
        row += 1
        
        # ===== CONVERT BUTTON =====
        state = "normal" if ffmpeg_ok else "disabled"
        btn_text = "🔄 CHUYỂN ĐỔI NGAY" if ffmpeg_ok else "⚠️ Cần FFmpeg"
        
        self.convert_btn = ctk.CTkButton(
            self, text=btn_text, height=Spacing.BUTTON_HEIGHT,
            font=Fonts.BUTTON_LARGE, corner_radius=Spacing.CORNER_RADIUS,
            fg_color=Colors.WARNING, hover_color="#E09040",
            text_color=Colors.BG_DARKEST,
            state=state,
            command=self._start_convert
        )
        self.convert_btn.grid(row=row, column=0, padx=Spacing.PAD_XL, 
                             pady=Spacing.PAD_XL, sticky="ew")
    
    def _select_file(self):
        """Select input file."""
        f = filedialog.askopenfilename(
            title="Chọn file cần chuyển đổi",
            filetypes=[
                ("Media files", "*.mp4 *.mkv *.avi *.webm *.mov *.mp3 *.wav *.flac *.m4a *.ogg"),
                ("Video files", "*.mp4 *.mkv *.avi *.webm *.mov"),
                ("Audio files", "*.mp3 *.wav *.flac *.m4a *.ogg"),
                ("All files", "*.*"),
            ]
        )
        if f:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, f)
    
    def _start_convert(self):
        """Start conversion in background."""
        inp = self.file_entry.get().strip()
        fmt = self.format_var.get()
        
        if not inp or not os.path.exists(inp):
            self.conv_status.configure(text="⚠️ Vui lòng chọn file hợp lệ", text_color=Colors.ERROR)
            return
        
        self.convert_btn.configure(state="disabled", text="⏳ Đang xử lý...")
        self.conv_progress.set(0.5)  # Indeterminate-ish
        
        def _convert():
            result = self.converter.convert(
                input_path=inp,
                output_format=fmt,
                progress_callback=lambda p: self.after(0, lambda: self.conv_progress.set(p/100)),
                log_callback=self.log_callback
            )
            self.after(0, lambda: self._on_convert_done(result))
        
        threading.Thread(target=_convert, daemon=True).start()
    
    def _on_convert_done(self, result):
        """Handle conversion result."""
        self.convert_btn.configure(state="normal", text="🔄 CHUYỂN ĐỔI NGAY")
        
        if result.get('success'):
            filename = result.get('filename', '')
            self.conv_status.configure(
                text=f"✅ Hoàn tất: {filename}", text_color=Colors.SUCCESS
            )
            self.conv_progress.set(1.0)
        else:
            error = result.get('error', 'Unknown')
            self.conv_status.configure(
                text=f"❌ Lỗi: {error[:80]}", text_color=Colors.ERROR
            )
            self.conv_progress.set(0)
