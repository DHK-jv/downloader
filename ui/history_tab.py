"""
Titanium Downloader - History Tab
Hiển thị lịch sử tải xuống.
"""
import customtkinter as ctk
import os
import subprocess
from .theme import Colors, Fonts, Spacing


class HistoryTab(ctk.CTkFrame):
    """Download history tab."""
    
    def __init__(self, master, config=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.config = config
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # ===== HEADER =====
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=Spacing.PAD_XL, 
                              pady=(Spacing.PAD_XL, Spacing.PAD_MD), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.header_frame, text="📋 Lịch Sử Tải Xuống",
            font=Fonts.HEADING, text_color=Colors.TEXT_PRIMARY, anchor="w"
        ).grid(row=0, column=0, sticky="w")
        
        self.clear_btn = ctk.CTkButton(
            self.header_frame, text="🗑 Xóa tất cả", width=110, height=32,
            font=Fonts.SMALL_BOLD, corner_radius=Spacing.CORNER_RADIUS_SM,
            fg_color=Colors.BG_CARD, hover_color=Colors.ERROR,
            border_width=1, border_color=Colors.BORDER,
            text_color=Colors.TEXT_SECONDARY,
            command=self._clear_history
        )
        self.clear_btn.grid(row=0, column=1)
        
        # ===== SCROLLABLE LIST =====
        self.scroll_frame = ctk.CTkScrollableFrame(
            self, fg_color=Colors.BG_CARD, 
            corner_radius=Spacing.CORNER_RADIUS,
            border_width=1, border_color=Colors.BORDER
        )
        self.scroll_frame.grid(row=1, column=0, padx=Spacing.PAD_XL, 
                              pady=(0, Spacing.PAD_XL), sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Empty state
        self.empty_label = ctk.CTkLabel(
            self.scroll_frame, 
            text="📭\n\nChưa có lịch sử tải xuống\nCác file đã tải sẽ hiển thị ở đây",
            font=Fonts.BODY, text_color=Colors.TEXT_MUTED,
            justify="center"
        )
        self.empty_label.grid(row=0, column=0, pady=60)
        
        self._load_history()
    
    def _load_history(self):
        """Load and display history."""
        if not self.config:
            return
        
        history = self.config.get_history()
        
        if not history:
            self.empty_label.grid()
            return
        
        self.empty_label.grid_remove()
        
        # Clear existing items
        for widget in self.scroll_frame.winfo_children():
            if widget != self.empty_label:
                widget.destroy()
        
        for i, entry in enumerate(history):
            self._create_history_item(i, entry)
    
    def _create_history_item(self, index, entry):
        """Create a single history item card."""
        from core.downloader import DownloadEngine
        
        item = ctk.CTkFrame(
            self.scroll_frame, fg_color=Colors.BG_ELEVATED if index % 2 == 0 else "transparent",
            corner_radius=Spacing.CORNER_RADIUS_SM, height=50
        )
        item.grid(row=index, column=0, padx=Spacing.PAD_SM, pady=2, sticky="ew")
        item.grid_columnconfigure(1, weight=1)
        
        # Icon
        is_mp3 = entry.get('quality', '').startswith('MP3')
        icon = "🎵" if is_mp3 else "🎬"
        
        ctk.CTkLabel(
            item, text=icon, font=(Fonts.FAMILY, 18), width=30
        ).grid(row=0, column=0, padx=(Spacing.PAD_SM, Spacing.PAD_SM), pady=Spacing.PAD_SM)
        
        # Info
        info_frame = ctk.CTkFrame(item, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", pady=Spacing.PAD_SM)
        info_frame.grid_columnconfigure(0, weight=1)
        
        title = entry.get('title', entry.get('filename', 'Unknown'))
        if len(title) > 50:
            title = title[:47] + "..."
        
        ctk.CTkLabel(
            info_frame, text=title, font=Fonts.SMALL_BOLD,
            text_color=Colors.TEXT_PRIMARY, anchor="w"
        ).grid(row=0, column=0, sticky="w")
        
        quality = entry.get('quality', '')
        filesize = DownloadEngine.format_filesize(entry.get('filesize', 0))
        timestamp = entry.get('timestamp', '')[:10]
        
        ctk.CTkLabel(
            info_frame, text=f"{quality} • {filesize} • {timestamp}",
            font=Fonts.TINY, text_color=Colors.TEXT_MUTED, anchor="w"
        ).grid(row=1, column=0, sticky="w")
        
        # Open folder button
        filepath = entry.get('filepath', '')
        if filepath and os.path.exists(os.path.dirname(filepath)):
            open_btn = ctk.CTkButton(
                item, text="📂", width=32, height=32,
                font=Fonts.BODY, corner_radius=6,
                fg_color="transparent", hover_color=Colors.BG_CARD_HOVER,
                command=lambda p=filepath: self._open_folder(p)
            )
            open_btn.grid(row=0, column=2, padx=Spacing.PAD_SM)
    
    def _open_folder(self, filepath):
        """Open containing folder in file explorer."""
        try:
            folder = os.path.dirname(filepath)
            if os.path.exists(folder):
                if os.name == 'nt':
                    subprocess.Popen(['explorer', '/select,', filepath])
                else:
                    subprocess.Popen(['xdg-open', folder])
        except Exception:
            pass
    
    def _clear_history(self):
        """Clear all history."""
        if self.config:
            self.config.clear_history()
        
        for widget in self.scroll_frame.winfo_children():
            if widget != self.empty_label:
                widget.destroy()
        
        self.empty_label.grid()
    
    def refresh(self):
        """Refresh history display."""
        self._load_history()
