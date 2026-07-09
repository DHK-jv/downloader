"""
Titanium Downloader - Queue & Multi-threaded Download Manager
Quản lý hàng đợi tải xuống, hỗ trợ tải song song đa luồng sử dụng ThreadPoolExecutor.
"""
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from core.downloader import DownloadEngine


class DownloadTask:
    """Đại diện cho một tiến trình tải trong hàng đợi."""
    
    def __init__(self, url, mode, quality, bitrate, output_path, cookie_path):
        self.id = str(uuid.uuid4())[:8]
        self.url = url
        self.mode = mode
        self.quality = quality
        self.bitrate = bitrate
        self.output_path = output_path
        self.cookie_path = cookie_path
        
        self.title = "Đang kết nối..."
        self.status = "Waiting"  # Waiting, Downloading, Completed, Failed, Cancelled
        self.percent = 0
        self.speed = "N/A"
        self.eta = "N/A"
        self.size_info = ""
        self.error_msg = ""
        self.engine = None
        self._lock = threading.Lock()

    def cancel(self):
        """Hủy tải xuống nhiệm vụ này."""
        with self._lock:
            if self.engine:
                self.engine.cancel()
            self.status = "Cancelled"
            self.percent = 0
            self.speed = "N/A"
            self.eta = "N/A"


class QueueManager:
    """Quản lý hàng đợi và phân phối tải song song."""
    
    def __init__(self, ffmpeg_path=None, max_concurrent=2, 
                 on_task_success=None, on_task_log=None):
        self.ffmpeg_path = ffmpeg_path
        self.max_concurrent = max_concurrent
        self.on_task_success = on_task_success
        self.on_task_log = on_task_log
        
        self.tasks = []
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self._lock = threading.Lock()
        self.on_update_callbacks = []

    def register_callback(self, callback):
        """Đăng ký callback để cập nhật giao diện khi có thay đổi trạng thái."""
        self.on_update_callbacks.append(callback)

    def trigger_update(self):
        """Gọi tất cả các callback để vẽ lại UI."""
        for cb in self.on_update_callbacks:
            try:
                cb()
            except Exception:
                pass

    def add_task(self, url, mode, quality, bitrate, output_path, cookie_path, title=None):
        """Thêm task mới vào hàng đợi và submit chạy."""
        task = DownloadTask(url, mode, quality, bitrate, output_path, cookie_path)
        if title:
            task.title = title
            
        with self._lock:
            self.tasks.append(task)
            
        self.trigger_update()
        
        if self.on_task_log:
            self.on_task_log(f"📥 Đã thêm vào hàng đợi: {title or url}")
            
        # Đưa vào ThreadPool để thực thi
        self.executor.submit(self._run_task, task)
        return task

    def _run_task(self, task):
        # 1. Khởi tạo download engine riêng cho thread này (Thread-safe)
        task.engine = DownloadEngine(ffmpeg_path=self.ffmpeg_path)
        
        # 2. Lấy thông tin tiêu đề trước nếu chưa có
        if task.title == "Đang kết nối...":
            info = task.engine.fetch_info(task.url, cookie_path=task.cookie_path)
            if info and not info.get('error'):
                task.title = info.get('title', task.url)
            else:
                task.title = task.url
            self.trigger_update()
            
        with self._lock:
            if task.status == "Cancelled":
                return
            task.status = "Downloading"
            
        self.trigger_update()
        
        if self.on_task_log:
            self.on_task_log(f"⚡ Bắt đầu tải: {task.title}")

        # Hook bắt tiến độ của yt-dlp
        def progress_hook(percent, speed, eta, status_msg, size_info):
            # Nếu người dùng bấm hủy trong lúc đang tải
            if task.status == "Cancelled":
                raise Exception("Download cancelled by user")
                
            task.percent = percent
            task.speed = speed
            task.eta = eta
            task.size_info = size_info
            task.status = status_msg
            self.trigger_update()

        try:
            result = task.engine.download(
                url=task.url,
                output_path=task.output_path,
                mode=task.mode,
                quality=task.quality,
                bitrate=task.bitrate,
                is_playlist=False,  # Playlist sẽ rã ra từng video nhỏ trong UI
                cookie_path=task.cookie_path,
                progress_callback=progress_hook,
                log_callback=self.on_task_log,
            )
            
            with self._lock:
                if task.status == "Cancelled":
                    return
                    
                if result.get('success'):
                    task.status = "Completed"
                    task.percent = 100
                    task.speed = ""
                    task.eta = ""
                    if self.on_task_success:
                        self.on_task_success(result)
                else:
                    task.status = "Failed"
                    task.error_msg = result.get('error', 'Lỗi không xác định')
                    if self.on_task_log:
                        self.on_task_log(f"❌ Tải thất bại [{task.title}]: {task.error_msg}")
                        
        except Exception as e:
            with self._lock:
                if task.status != "Cancelled":
                    task.status = "Failed"
                    task.error_msg = str(e)
                    if self.on_task_log:
                        self.on_task_log(f"❌ Lỗi ngoại lệ [{task.title}]: {str(e)}")
        finally:
            self.trigger_update()

    def cancel_task(self, task_id):
        """Hủy một nhiệm vụ bằng ID."""
        with self._lock:
            for t in self.tasks:
                if t.id == task_id:
                    t.cancel()
                    if self.on_task_log:
                        self.on_task_log(f"⏹ Đã hủy tải: {t.title}")
                    break
        self.trigger_update()

    def remove_task(self, task_id):
        """Xóa hẳn task ra khỏi hàng đợi (nếu đã xong/hủy/lỗi)."""
        with self._lock:
            self.tasks = [t for t in self.tasks if not (t.id == task_id and t.status in ["Completed", "Failed", "Cancelled"])]
        self.trigger_update()

    def clear_all_finished(self):
        """Xóa sạch các task đã hoàn thành hoặc thất bại khỏi danh sách hiển thị."""
        with self._lock:
            self.tasks = [t for t in self.tasks if t.status not in ["Completed", "Failed", "Cancelled"]]
        self.trigger_update()
