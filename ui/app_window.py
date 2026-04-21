"""
Titanium Downloader - Main Application Window
Cửa sổ chính kết hợp sidebar và tabs.
"""
import customtkinter as ctk
from .theme import Colors, Fonts, Spacing
from .sidebar import Sidebar
from .download_tab import DownloadTab
from .history_tab import HistoryTab
from .converter_tab import ConverterTab


class AppWindow(ctk.CTk):
    """Main application window."""
    
    def __init__(self, download_engine, converter, config):
        super().__init__()
        
        self.engine = download_engine
        self.converter = converter
        self.config = config
        self._cookie_path = config.get("cookie_path", "")
        
        # --- Window Setup ---
        self.title("Titanium Universal Downloader")
        self.geometry("1080x720")
        self.minsize(700, 450)
        self.configure(fg_color=Colors.BG_DARK)
        
        # Appearance
        ctk.set_appearance_mode("Dark")
        
        # Grid layout: sidebar | main content
        self.grid_columnconfigure(0, weight=0)  # Sidebar fixed
        self.grid_columnconfigure(1, weight=1)  # Main expandable
        self.grid_rowconfigure(0, weight=1)
        
        # ===== SIDEBAR =====
        self.sidebar = Sidebar(
            self,
            on_mode_change=self._on_mode_change,
            on_cookie_select=self._on_cookie_select,
            on_playlist_toggle=self._on_playlist_toggle,
            ffmpeg_ok=self.engine.is_ffmpeg_ok
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # ===== MAIN CONTENT =====
        self.main_frame = ctk.CTkFrame(self, fg_color=Colors.BG_DARK, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Tab View
        self.tabview = ctk.CTkTabview(
            self.main_frame, 
            fg_color=Colors.BG_DARK,
            segmented_button_fg_color=Colors.BG_CARD,
            segmented_button_selected_color=Colors.PRIMARY,
            segmented_button_selected_hover_color=Colors.PRIMARY_HOVER,
            segmented_button_unselected_color=Colors.BG_CARD,
            segmented_button_unselected_hover_color=Colors.BG_CARD_HOVER,
            text_color=Colors.TEXT_PRIMARY,
            corner_radius=Spacing.CORNER_RADIUS
        )
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=Spacing.PAD_MD, pady=Spacing.PAD_MD)
        
        # Create tabs
        self.tab_download = self.tabview.add("⬇ Tải Xuống")
        self.tab_history = self.tabview.add("📋 Lịch Sử")
        self.tab_convert = self.tabview.add("🔄 Chuyển Đổi")
        self.tab_log = self.tabview.add("📝 Nhật Ký")
        
        # Configure tab grids
        for tab in [self.tab_download, self.tab_history, self.tab_convert, self.tab_log]:
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)
        
        # --- Download Tab ---
        self.download_tab = DownloadTab(
            self.tab_download,
            download_engine=self.engine,
            config=self.config,
            get_sidebar_settings=self._get_sidebar_settings,
            log_callback=self._log
        )
        self.download_tab.grid(row=0, column=0, sticky="nsew")
        
        # --- History Tab ---
        self.history_tab = HistoryTab(
            self.tab_history,
            config=self.config
        )
        self.history_tab.grid(row=0, column=0, sticky="nsew")
        
        # --- Converter Tab ---
        self.converter_tab = ConverterTab(
            self.tab_convert,
            converter=self.converter,
            log_callback=self._log,
            ffmpeg_ok=self.engine.is_ffmpeg_ok
        )
        self.converter_tab.grid(row=0, column=0, sticky="nsew")
        
        # --- Log Tab ---
        self.log_frame = ctk.CTkFrame(self.tab_log, fg_color="transparent")
        self.log_frame.grid(row=0, column=0, sticky="nsew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(0, weight=1)
        
        self.console = ctk.CTkTextbox(
            self.log_frame, 
            fg_color=Colors.BG_DARKEST, 
            text_color=Colors.SUCCESS,
            font=Fonts.CONSOLE,
            corner_radius=Spacing.CORNER_RADIUS,
            border_width=1, border_color=Colors.BORDER,
            state="disabled"
        )
        self.console.grid(row=0, column=0, sticky="nsew", padx=Spacing.PAD_MD, pady=Spacing.PAD_MD)
        
        self.clear_log_btn = ctk.CTkButton(
            self.log_frame, text="🗑 Xóa log", width=100, height=30,
            font=Fonts.SMALL, corner_radius=Spacing.CORNER_RADIUS_SM,
            fg_color=Colors.BG_CARD, hover_color=Colors.BG_CARD_HOVER,
            text_color=Colors.TEXT_SECONDARY,
            command=self._clear_log
        )
        self.clear_log_btn.grid(row=1, column=0, padx=Spacing.PAD_MD, 
                               pady=(0, Spacing.PAD_MD), sticky="e")
        
        # Welcome log
        self._log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self._log("⚡ TITANIUM Universal Downloader")
        self._log(f"   FFmpeg: {'✅ Hoạt động' if self.engine.is_ffmpeg_ok else '⚠️ Không tìm thấy'}")
        self._log("   Hỗ trợ: YouTube, Facebook, TikTok, Instagram, Twitter/X, SoundCloud...")
        self._log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Tab change callback - refresh history when switching
        self.tabview.configure(command=self._on_tab_change)
    
    def _get_sidebar_settings(self):
        """Get current settings from sidebar."""
        return {
            'mode': self.sidebar.get_mode(),
            'quality': self.sidebar.get_quality(),
            'bitrate': self.sidebar.get_bitrate(),
            'is_playlist': self.sidebar.get_is_playlist(),
            'cookie_path': self._cookie_path,
        }
    
    def _on_mode_change(self, mode):
        """Handle mode change from sidebar."""
        self.download_tab.update_mode(mode)
        self._log(f"🔀 Chế độ: {mode}")
    
    def _on_cookie_select(self, path):
        """Handle cookie file selection."""
        self._cookie_path = path
        self.config.set("cookie_path", path)
        self._log(f"🍪 Đã nạp cookies: {path}")
    
    def _on_playlist_toggle(self, enabled):
        """Handle playlist toggle."""
        self._log(f"📃 Tải playlist: {'Bật' if enabled else 'Tắt'}")
    
    def _on_tab_change(self):
        """Handle tab change."""
        current = self.tabview.get()
        if "Lịch Sử" in current:
            self.history_tab.refresh()
    
    def _log(self, msg):
        """Write message to log console."""
        try:
            self.console.configure(state="normal")
            self.console.insert("end", f"  {msg}\n")
            self.console.see("end")
            self.console.configure(state="disabled")
        except Exception:
            pass
    
    def _clear_log(self):
        """Clear log console."""
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")
