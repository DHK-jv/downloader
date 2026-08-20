"""
Titanium Downloader - Queue Manager Tab
Hiển thị hàng đợi tải xuống, cập nhật tiến trình thời gian thực và quản lý các task.
"""
import customtkinter as ctk
import os
from .theme import Colors, Fonts, Spacing
from .icons import Icons


class QueueTab(ctk.CTkFrame):
    """Tab quản lý hàng đợi tải song song."""
    
    def __init__(self, master, queue_manager=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.queue_manager = queue_manager
        self.task_widgets = {}  # task_id -> dict of widgets
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # ===== HEADER =====
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=Spacing.PAD_XL, 
                               pady=(Spacing.PAD_XL, Spacing.PAD_MD), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.header_frame, text="⏳ Hàng Đợi Tải Xuống",
            font=Fonts.HEADING, text_color=Colors.TEXT_PRIMARY, anchor="w"
        ).grid(row=0, column=0, sticky="w")
        
        self.clear_btn = ctk.CTkButton(
            self.header_frame, text="Xóa các mục đã xong", width=150, height=32,
            font=Fonts.SMALL_BOLD, corner_radius=Spacing.CORNER_RADIUS_SM,
            fg_color=Colors.BG_CARD, hover_color=Colors.ERROR,
            border_width=1, border_color=Colors.BORDER,
            text_color=Colors.TEXT_SECONDARY,
            image=Icons.get("delete", size=14), compound="left",
            command=self._clear_finished
        )
        self.clear_btn.grid(row=0, column=1)
        
        # ===== SCROLLABLE CONTAINER =====
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
            text="📭\n\nHàng đợi trống\nThêm link tải từ tab Tải Xuống",
            font=Fonts.BODY, text_color=Colors.TEXT_MUTED,
            justify="center"
        )
        self.empty_label.grid(row=0, column=0, pady=80)
        
        # Đăng ký nhận sự kiện từ Queue Manager
        if self.queue_manager:
            self.queue_manager.register_callback(self.on_queue_update)
            
        self.refresh()

    def on_queue_update(self):
        """Được gọi từ background thread của QueueManager."""
        # Sử dụng after để đảm bảo chạy trên UI Thread của Tkinter
        self.after(0, self.refresh)

    def refresh(self):
        """Cập nhật lại giao diện hàng đợi."""
        if not self.queue_manager:
            return
            
        tasks = self.queue_manager.tasks
        
        # Nếu trống, hiện empty label
        if not tasks:
            self.empty_label.grid()
            # Xóa các widget thừa
            for task_id in list(self.task_widgets.keys()):
                self.task_widgets[task_id]['frame'].destroy()
            self.task_widgets.clear()
            return
            
        self.empty_label.grid_remove()
        
        # 1. Xóa các widgets của task không còn trong hàng đợi
        current_ids = {t.id for t in tasks}
        for task_id in list(self.task_widgets.keys()):
            if task_id not in current_ids:
                self.task_widgets[task_id]['frame'].destroy()
                del self.task_widgets[task_id]
                
        # 2. Tạo mới hoặc cập nhật các hàng task
        for i, task in enumerate(tasks):
            if task.id not in self.task_widgets:
                self._create_task_row(i, task)
            else:
                self._update_task_row(i, task)

    def _create_task_row(self, index, task):
        """Tạo giao diện cho một dòng task mới."""
        row_frame = ctk.CTkFrame(
            self.scroll_frame, 
            fg_color=Colors.BG_ELEVATED if index % 2 == 0 else "transparent",
            corner_radius=Spacing.CORNER_RADIUS_SM
        )
        row_frame.grid(row=index, column=0, padx=Spacing.PAD_SM, pady=4, sticky="ew")
        row_frame.grid_columnconfigure(1, weight=1)
        
        # Icon MP3/MP4
        icon_name = "mp3" if task.mode == "MP3" else "mp4"
        icon_label = ctk.CTkLabel(
            row_frame, text="", 
            image=Icons.get(icon_name, size=24), 
            width=36
        )
        icon_label.grid(row=0, column=0, rowspan=2, padx=Spacing.PAD_MD, pady=Spacing.PAD_SM)
        
        # Title
        title_text = task.title
        if len(title_text) > 65:
            title_text = title_text[:62] + "..."
        title_label = ctk.CTkLabel(
            row_frame, text=title_text, 
            font=Fonts.SMALL_BOLD, text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        title_label.grid(row=0, column=1, padx=(0, Spacing.PAD_MD), pady=(Spacing.PAD_SM, 2), sticky="w")
        
        # Progress Bar
        progress_bar = ctk.CTkProgressBar(
            row_frame, height=Spacing.PROGRESS_HEIGHT - 2,
            corner_radius=2, fg_color=Colors.PROGRESS_BG,
            progress_color=Colors.MP3_COLOR if task.mode == "MP3" else Colors.PRIMARY
        )
        progress_bar.set(task.percent / 100)
        progress_bar.grid(row=1, column=1, padx=(0, Spacing.PAD_MD), pady=(0, 4), sticky="ew")
        
        # Sub-status (Status, Size, Speed, ETA)
        status_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        status_frame.grid(row=2, column=1, padx=(0, Spacing.PAD_MD), pady=(0, Spacing.PAD_SM), sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)
        
        status_label = ctk.CTkLabel(
            status_frame, text=self._format_status_text(task),
            font=Fonts.TINY, text_color=Colors.TEXT_SECONDARY, anchor="w"
        )
        status_label.pack(side="left")
        
        speed_label = ctk.CTkLabel(
            status_frame, text=self._format_speed_text(task),
            font=Fonts.TINY, text_color=Colors.SUCCESS, anchor="e"
        )
        speed_label.pack(side="right")
        
        # Action button (Cancel/Delete)
        action_btn = ctk.CTkButton(
            row_frame, text="", width=32, height=32,
            font=Fonts.BODY, corner_radius=6,
            fg_color="transparent", hover_color=Colors.BG_CARD_HOVER,
            image=Icons.get("cancel" if task.status in ["Waiting", "Downloading", "Đang tải...", "Đang ghép file..."] else "delete", size=16),
            command=lambda: self._handle_action(task.id)
        )
        action_btn.grid(row=0, column=2, rowspan=3, padx=Spacing.PAD_MD, pady=Spacing.PAD_SM)
        
        # Lưu vào cache
        self.task_widgets[task.id] = {
            'frame': row_frame,
            'title_label': title_label,
            'progress_bar': progress_bar,
            'status_label': status_label,
            'speed_label': speed_label,
            'action_btn': action_btn,
            'mode': task.mode
        }

    def _update_task_row(self, index, task):
        """Cập nhật giao diện của một dòng đã tồn tại."""
        widgets = self.task_widgets[task.id]
        
        # Cập nhật vị trí grid (tránh xáo trộn khi xóa bớt phần tử)
        widgets['frame'].grid(row=index, column=0, padx=Spacing.PAD_SM, pady=4, sticky="ew")
        
        # Cập nhật title
        title_text = task.title
        if len(title_text) > 65:
            title_text = title_text[:62] + "..."
        widgets['title_label'].configure(text=title_text)
        
        # Cập nhật progress bar
        widgets['progress_bar'].set(task.percent / 100)
        
        # Cập nhật màu progress
        prog_color = Colors.MP3_COLOR if task.mode == "MP3" else Colors.PRIMARY
        widgets['progress_bar'].configure(progress_color=prog_color)
        
        # Cập nhật label status & speed
        widgets['status_label'].configure(text=self._format_status_text(task))
        widgets['speed_label'].configure(text=self._format_speed_text(task))
        
        # Cập nhật icon hành động tương ứng với trạng thái
        is_active = task.status in ["Waiting", "Downloading", "Đang tải...", "Đang ghép file...", "Đang kết nối..."] or "tải" in task.status.lower()
        icon_name = "cancel" if is_active else "delete"
        widgets['action_btn'].configure(image=Icons.get(icon_name, size=16))

    def _format_status_text(self, task):
        """Format dòng trạng thái phụ."""
        status_map = {
            "Waiting": "Đang chờ...",
            "Downloading": "Đang tải...",
            "Completed": "✅ Đã tải xong",
            "Failed": f"❌ Lỗi: {task.error_msg[:45]}...",
            "Cancelled": "⏹ Đã hủy"
        }
        status_desc = status_map.get(task.status, task.status)
        
        size_part = f" • {task.size_info}" if task.size_info else ""
        return f"{status_desc}{size_part}"

    def _format_speed_text(self, task):
        """Format dòng tốc độ và ETA."""
        if task.status not in ["Downloading", "Đang tải Video...", "Đang tải Âm thanh...", "Đang tải xuống..."]:
            return ""
        
        speed_part = f"⚡ {task.speed}" if task.speed and task.speed != "N/A" else ""
        eta_part = f"⏱ {task.eta}" if task.eta and task.eta != "N/A" else ""
        
        if speed_part and eta_part:
            return f"{speed_part}  •  {eta_part}"
        return speed_part or eta_part

    def _handle_action(self, task_id):
        """Xử lý sự kiện nhấn nút cancel hoặc xóa."""
        if not self.queue_manager:
            return
            
        # Tìm task
        task = next((t for t in self.queue_manager.tasks if t.id == task_id), None)
        if not task:
            return
            
        is_active = task.status in ["Waiting", "Downloading", "Đang tải...", "Đang ghép file...", "Đang kết nối..."] or "tải" in task.status.lower()
        if is_active:
            self.queue_manager.cancel_task(task_id)
        else:
            self.queue_manager.remove_task(task_id)

    def _clear_finished(self):
        """Xóa toàn bộ task đã hoàn thành/hủy/lỗi khỏi hàng đợi."""
        if self.queue_manager:
            self.queue_manager.clear_all_finished()
