import customtkinter as ctk
import yt_dlp
import threading
import os
import shutil
import subprocess
from tkinter import filedialog
import re
import sys

# --- CẤU HÌNH GIAO DIỆN ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") 

class TitaniumFinal(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Titanium Universal - Fixed Audio & Progress")
        self.geometry("1000x680")
        self.resizable(True, True)

        # --- 1. TÌM VÀ KIỂM TRA FFMPEG (Rất quan trọng) ---
        self.ffmpeg_path = self.find_ffmpeg()
        self.is_ffmpeg_working = self.check_ffmpeg_working() # Kiểm tra xem nó có chạy được không

        self.cookie_path = ""

        # Layout Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= SIDEBAR =================
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="TITANIUM", 
                                     font=ctk.CTkFont(size=24, weight="bold"), text_color="#3B8ED0")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))

        # Hiển thị trạng thái FFmpeg
        if self.is_ffmpeg_working:
            ff_text = "✅ FFmpeg: Hoạt động tốt"
            ff_color = "#2cc985"
        else:
            ff_text = "⚠️ FFmpeg: Lỗi/Thiếu"
            ff_color = "#FF5555"
            
        self.ffmpeg_lbl = ctk.CTkLabel(self.sidebar, text=ff_text, text_color=ff_color, font=("Arial", 11, "bold"))
        self.ffmpeg_lbl.grid(row=1, column=0, pady=(0, 20))
        
        if not self.is_ffmpeg_working:
            self.warn_lbl = ctk.CTkLabel(self.sidebar, text="(Chế độ an toàn: Max 720p)", text_color="orange", font=("Arial", 10))
            self.warn_lbl.grid(row=2, column=0, pady=(0, 10))

        # Cài đặt Download
        self.mode_label = ctk.CTkLabel(self.sidebar, text="Chế độ tải:", font=ctk.CTkFont(weight="bold"))
        self.mode_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.type_var = ctk.StringVar(value="Video")
        self.seg_button = ctk.CTkSegmentedButton(self.sidebar, values=["Video", "Audio"], 
                                                variable=self.type_var, command=self.toggle_menus)
        self.seg_button.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.playlist_var = ctk.BooleanVar(value=False)
        self.playlist_sw = ctk.CTkSwitch(self.sidebar, text="Tải cả Playlist", variable=self.playlist_var)
        self.playlist_sw.grid(row=5, column=0, padx=20, pady=10, sticky="w")

        self.cookie_btn = ctk.CTkButton(self.sidebar, text="🍪 Nạp Cookies.txt", fg_color="transparent", 
                                      border_width=1, text_color="white", command=self.select_cookie)
        self.cookie_btn.grid(row=7, column=0, padx=20, pady=20)

        # ================= MAIN CONTENT =================
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self.main_content, height=400)
        self.tabview.grid(row=0, column=0, sticky="nsew")
        
        self.tab_download = self.tabview.add("Tải Xuống")
        self.tab_convert = self.tabview.add("Chuyển Đổi File")
        self.tab_log = self.tabview.add("Nhật Ký")

        # --- TAB DOWNLOAD ---
        self.url_entry = ctk.CTkEntry(self.tab_download, height=45, placeholder_text="Dán link Video/Playlist (YouTube, Facebook, TikTok...)")
        self.url_entry.pack(fill="x", padx=20, pady=(20, 10))

        # Path
        self.path_frame = ctk.CTkFrame(self.tab_download, fg_color="transparent")
        self.path_frame.pack(fill="x", padx=20, pady=10)
        
        default_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.path_entry = ctk.CTkEntry(self.path_frame, height=40)
        self.path_entry.insert(0, default_path)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_btn = ctk.CTkButton(self.path_frame, text="📁", width=45, command=self.select_folder)
        self.browse_btn.pack(side="right")

        # Quality
        self.qual_frame = ctk.CTkFrame(self.tab_download, fg_color="transparent")
        self.qual_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(self.qual_frame, text="Chất lượng:").pack(side="left", padx=(0, 10))
        self.res_menu = ctk.CTkOptionMenu(self.qual_frame, values=["4K", "2K", "1080p", "720p", "480p"], width=120)
        self.res_menu.set("1080p")
        self.res_menu.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(self.qual_frame, text="Audio Bitrate:").pack(side="left", padx=(0, 10))
        self.audio_menu = ctk.CTkOptionMenu(self.qual_frame, values=["320k", "192k", "128k"], width=120, state="disabled")
        self.audio_menu.pack(side="left")

        # --- TAB CONVERTER ---
        self.setup_converter_ui()

        # --- TAB LOG ---
        self.console_log = ctk.CTkTextbox(self.tab_log, fg_color="#1a1a1a", text_color="#00FF00", font=("Consolas", 12))
        self.console_log.pack(fill="both", expand=True, padx=10, pady=10)

        # --- BOTTOM PROGRESS ---
        self.bottom_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.bottom_frame.grid(row=1, column=0, pady=(10, 0), sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(self.bottom_frame, height=18)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=5)

        self.status_label = ctk.CTkLabel(self.bottom_frame, text="Sẵn sàng...", font=ctk.CTkFont(size=13))
        self.status_label.pack()

        self.download_btn = ctk.CTkButton(self.main_content, text="BẮT ĐẦU TẢI XUỐNG", height=50, 
                                        font=ctk.CTkFont(size=16, weight="bold"), 
                                        fg_color="#3B8ED0", hover_color="#36719F",
                                        command=self.start_download)
        self.download_btn.grid(row=2, column=0, pady=(15, 0), sticky="ew")

    # ================= HỆ THỐNG XỬ LÝ FFMPEG =================
    def find_ffmpeg(self):
        # 1. Tìm trong PATH
        path = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
        # 2. Tìm trong thư mục hiện tại của script
        if not path:
            local = os.path.join(os.getcwd(), "ffmpeg.exe")
            if os.path.exists(local):
                path = local
        return path

    def check_ffmpeg_working(self):
        # Chạy thử lệnh version để chắc chắn ffmpeg không bị lỗi
        if not self.ffmpeg_path: return False
        try:
            # Dùng creationflags=0x08000000 để ẩn cửa sổ console trên Windows
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            subprocess.run([self.ffmpeg_path, "-version"], 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                         startupinfo=startupinfo, check=True)
            return True
        except Exception as e:
            print(f"FFmpeg check failed: {e}")
            return False

    # ================= GIAO DIỆN CONVERTER =================
    def setup_converter_ui(self):
        ctk.CTkLabel(self.tab_convert, text="Chọn file nguồn (Video/Audio):").pack(anchor="w", padx=20, pady=(20, 5))
        
        self.conv_input_frame = ctk.CTkFrame(self.tab_convert, fg_color="transparent")
        self.conv_input_frame.pack(fill="x", padx=20, pady=0)
        
        self.conv_file_entry = ctk.CTkEntry(self.conv_input_frame, height=35)
        self.conv_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(self.conv_input_frame, text="Chọn File", width=90, 
                     command=self.select_convert_file).pack(side="right")

        ctk.CTkLabel(self.tab_convert, text="Đổi sang đuôi:").pack(anchor="w", padx=20, pady=(15, 5))
        self.conv_format = ctk.CTkOptionMenu(self.tab_convert, values=["mp3", "mp4", "wav", "mkv", "avi", "flac"])
        self.conv_format.pack(anchor="w", padx=20, pady=0)

        self.conv_btn = ctk.CTkButton(self.tab_convert, text="Chuyển Đổi Ngay", height=45, 
                                     fg_color="#E07A5F", hover_color="#D16045",
                                     command=self.start_conversion)
        self.conv_btn.pack(padx=20, pady=30, fill="x")
        
        if not self.is_ffmpeg_working:
            self.conv_btn.configure(state="disabled", text="⚠️ Cần FFmpeg để chuyển đổi file")

    def select_convert_file(self):
        file = filedialog.askopenfilename()
        if file:
            self.conv_file_entry.delete(0, "end")
            self.conv_file_entry.insert(0, file)

    def start_conversion(self):
        inp = self.conv_file_entry.get()
        ext = self.conv_format.get()
        if not inp or not os.path.exists(inp): return
        
        self.conv_btn.configure(state="disabled", text="Đang xử lý...")
        self.tabview.set("Nhật Ký")
        threading.Thread(target=self.run_converter, args=(inp, ext), daemon=True).start()

    def run_converter(self, inp, ext):
        try:
            folder = os.path.dirname(inp)
            name = os.path.splitext(os.path.basename(inp))[0]
            out = os.path.join(folder, f"{name}_converted.{ext}")
            
            self.log(f"Bắt đầu convert: {name} -> {ext}")
            
            cmd = [self.ffmpeg_path, "-i", inp, "-y"]
            
            # Logic thông minh: Nếu đích là âm thanh, bỏ hình ảnh
            if ext in ["mp3", "wav", "flac", "m4a"]:
                cmd.append("-vn") # Video None
                if ext == "mp3":
                    cmd.extend(["-acodec", "libmp3lame", "-q:a", "2"]) # MP3 High Quality

            cmd.append(out)
            
            # Chạy lệnh (ẩn cửa sổ đen)
            creationflags = 0x08000000 if os.name == 'nt' else 0
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                     universal_newlines=True, creationflags=creationflags)
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.after(0, lambda: self.log(f"✅ Xong: {out}"))
                self.after(0, lambda: self.update_status(f"Đã lưu: {os.path.basename(out)}", "success"))
            else:
                self.after(0, lambda: self.log(f"❌ Lỗi: {stderr[-200:]}")) # Lấy 200 ký tự lỗi cuối
                self.after(0, lambda: self.update_status("Lỗi Convert", "error"))
                
        except Exception as e:
            self.after(0, lambda: self.log(f"Lỗi: {e}"))
        finally:
            self.after(0, lambda: self.conv_btn.configure(state="normal", text="Chuyển Đổi Ngay"))

    # ================= LOGIC DOWNLOAD (ĐÃ FIX AUDIO) =================
    def log(self, msg):
        self.console_log.configure(state="normal")
        self.console_log.insert("end", f">> {msg}\n")
        self.console_log.see("end")
        self.console_log.configure(state="disabled")

    def toggle_menus(self, value):
        if value == "Audio":
            self.res_menu.configure(state="disabled")
            self.audio_menu.configure(state="normal")
        else:
            self.res_menu.configure(state="normal")
            self.audio_menu.configure(state="disabled")

    def select_folder(self):
        d = filedialog.askdirectory()
        if d: 
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, d)

    def select_cookie(self):
        f = filedialog.askopenfilename(filetypes=[("Text", "*.txt")])
        if f: self.cookie_path = f

    def update_status(self, text, type="normal"):
        c = "white"
        if type == "success": c = "#2cc985"
        elif type == "error": c = "#FF5555"
        self.status_label.configure(text=text, text_color=c)

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url: return self.update_status("Thiếu Link!", "error")
        
        self.download_btn.configure(state="disabled", text="ĐANG KẾT NỐI...")
        self.tabview.set("Nhật Ký")
        self.progress_bar.set(0)
        
        threading.Thread(target=self.download_task, args=(url,), daemon=True).start()

    def download_task(self, url):
        path = self.path_entry.get()
        mode = self.type_var.get()
        is_playlist = self.playlist_var.get()
        res_txt = self.res_menu.get()
        height = 2160 if "4K" in res_txt else (1440 if "2K" in res_txt else int(res_txt.replace("p","")))

        ydl_opts = {
            'outtmpl': f'{path}/%(title)s.%(ext)s',
            'noplaylist': not is_playlist,
            'progress_hooks': [self.on_progress],
            'cookiefile': self.cookie_path if self.cookie_path else None,
            'quiet': True,
            'no_warnings': True,
        }

        # --- LOGIC QUAN TRỌNG ĐỂ CÓ TIẾNG ---
        if mode == "Audio":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': self.audio_menu.get().replace("k","")}]
            })
            if self.is_ffmpeg_working: ydl_opts['ffmpeg_location'] = self.ffmpeg_path
        
        else: # VIDEO MODE
            if self.is_ffmpeg_working:
                self.after(0, lambda: self.log("ℹ️ Đang dùng chế độ Video+Audio Merge (Chất lượng cao)"))
                # QUAN TRỌNG: 
                # 1. bestvideo[height<=X]: Lấy video theo độ phân giải
                # 2. bestaudio[ext=m4a]: Ưu tiên lấy audio m4a (AAC) để ghép vào mp4 cho chuẩn
                # 3. Nếu không có m4a thì lấy bestaudio bất kỳ
                # 4. Fallback cuối cùng là 'best' (file đơn)
                fmt_str = f'bestvideo[height<={height}]+bestaudio[ext=m4a]/bestvideo[height<={height}]+bestaudio/best'
                
                ydl_opts.update({
                    'format': fmt_str,
                    'merge_output_format': 'mp4',
                    'ffmpeg_location': self.ffmpeg_path,
                })
            else:
                self.after(0, lambda: self.log("⚠️ FFmpeg hỏng/thiếu: Chuyển về chế độ 'best' (Max 720p, đảm bảo có tiếng)"))
                # Chế độ này KHÔNG ghép, mà tải file có sẵn do Youtube cung cấp
                # File này chắc chắn có tiếng, nhưng thường chỉ max 720p
                ydl_opts.update({'format': 'best[ext=mp4]/best'})

        # Fake User-Agent
        if "youtube" not in url:
            ydl_opts['user_agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.after(0, lambda: self.log(f"Đang xử lý: {url}"))
                ydl.download([url])
            self.after(0, lambda: self.update_status("✅ HOÀN TẤT!", "success"))
        except Exception as e:
            self.after(0, lambda: self.log(f"LỖI: {str(e)}"))
            self.after(0, lambda: self.update_status("Thất bại", "error"))
        finally:
            self.after(0, lambda: self.download_btn.configure(state="normal", text="BẮT ĐẦU TẢI XUỐNG"))

    def on_progress(self, d):
        if d['status'] == 'downloading':
            try:
                p_str = d.get('_percent_str', '0%').strip()
                # Dùng regex để lọc số phần trăm chính xác
                found = re.search(r"(\d+\.?\d*)", p_str)
                if found:
                    val = float(found.group(1)) / 100
                    spd = d.get('_speed_str', 'N/A')
                    # Update UI an toàn
                    self.after(0, lambda: self.progress_bar.set(val))
                    self.after(0, lambda: self.status_label.configure(text=f"Đang tải: {int(val*100)}% | Tốc độ: {spd}", text_color="white"))
            except: pass

if __name__ == "__main__":
    app = TitaniumFinal()
    app.mainloop()