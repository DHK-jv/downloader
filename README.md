# DHK Downloader

Ứng dụng desktop tải và chuyển đổi video/audio bằng `yt-dlp`, CustomTkinter và FFmpeg.

## Chạy bằng Docker

Docker là môi trường phát triển và runtime chuẩn của dự án. Sau khi cài Docker Desktop hoặc Docker Engine + Compose, chạy từ thư mục gốc:

```bash
docker compose up --build
```

Image sử dụng Python 3.12, cài các package từ `requirements.txt`, FFmpeg và Tk. Compose giữ cấu hình ở `config/` và file tải xuống ở `output/` trên máy host.

Để lưu file trực tiếp vào một thư mục Ubuntu, đặt `OUTPUT_DIR` khi chạy. Ví dụ:

```bash
OUTPUT_DIR=/home/$USER/Downloads/dhk docker compose up --build
```

Hoặc lưu vào `/media`:

```bash
OUTPUT_DIR=/media docker compose up --build
```

Trong container, cả hai trường hợp đều xuất hiện dưới `/workspace/output`; Compose sẽ ghi chúng vào đúng thư mục host đã chọn. Tạo thư mục trước nếu cần: `mkdir -p /media` hoặc `mkdir -p /home/$USER/Downloads/dhk`.

### Hiển thị giao diện trên Linux

Tkinter cần kết nối tới X11 của máy host. Trước lệnh Compose, cho phép container truy cập display hiện tại:

```bash
xhost +local:docker
docker compose up --build
```

Sau khi dừng ứng dụng, có thể thu hồi quyền bằng `xhost -local:docker`. Wayland hoặc cấu hình bảo mật X11 khác có thể cần thiết lập tương đương của hệ điều hành.

### Windows và macOS

Docker Desktop vẫn cung cấp môi trường Python/FFmpeg nhất quán, nhưng không cung cấp X server cho cửa sổ Tkinter. Để chạy GUI bằng Compose trên hai hệ điều hành này, cần cài và cấu hình X server riêng, sau đó đặt `DISPLAY`. Nếu không cần Docker GUI, native launcher cũ đã được loại bỏ; hãy dùng X server hoặc bổ sung một frontend phù hợp trong tương lai.

## Cấu trúc dự án

```text
app.py                 # Entry point duy nhất
app/
	core/                # Config, downloader, converter, queue, utilities
	ui/                  # Cửa sổ và các tab CustomTkinter
config/                # Trạng thái cấu hình runtime
output/                # File tải xuống, được tạo khi chạy Compose
tests/                 # Unit tests không phụ thuộc GUI/network
Dockerfile             # Image Python + FFmpeg + Tk
docker-compose.yml     # Runtime/dev service và persistent volumes
requirements.txt       # Python dependencies
```

## Kiểm thử

```bash
python -m unittest discover -s tests -v
docker compose config
```

Docker là lựa chọn ưu tiên vì dự án cần Python, Tk và FFmpeg cùng lúc. GUI vẫn phụ thuộc display của host; Docker không thể tự cung cấp hoặc cài Docker Desktop/X server cho máy mới.