"""
DHK Downloader - Common Utilities
Các hàm bổ trợ định dạng dung lượng, thời gian, xử lý chuỗi.
"""

def format_filesize(size_bytes):
    """Định dạng số byte sang đơn vị đọc được (B, KB, MB, GB)."""
    if not size_bytes or size_bytes == 0:
        return "0 B"
    units = ['B', 'KB', 'MB', 'GB']
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return f"{size:.1f} {units[i]}"


def format_duration(seconds):
    """Định dạng số giây sang định dạng HH:MM:SS hoặc MM:SS."""
    if not seconds:
        return "N/A"
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"
