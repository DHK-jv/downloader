"""
Titanium Downloader - Icon Generator & Manager
Sinh và quản lý các ảnh icon vẽ bằng Pillow dưới dạng Vector-like PNG.
Giúp sửa triệt để lỗi không hiển thị emoji trên một số máy Windows.
"""
import customtkinter as ctk
from PIL import Image, ImageDraw
from .theme import Colors


class Icons:
    """Manager class to generate and retrieve CTkImages."""
    
    _cache = {}
    
    @classmethod
    def get(cls, name, size=24):
        """Lấy CTkImage theo tên và kích thước (mặc định 24x24)."""
        cache_key = (name, size)
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        
        # Tạo ảnh cho Light theme (màu tối) và Dark theme (màu sáng)
        # Chúng ta dùng màu text hoặc primary thích hợp cho từng icon
        light_color = Colors.BG_DARKEST  # Cho Light Mode
        dark_color = Colors.TEXT_PRIMARY  # Cho Dark Mode
        
        # Override màu sắc cho một số icon đặc thù
        if name == "download" or name == "mp4":
            light_color = Colors.PRIMARY
            dark_color = Colors.PRIMARY
        elif name == "mp3":
            light_color = Colors.MP3_COLOR
            dark_color = Colors.MP3_COLOR
        elif name == "delete" or name == "cancel":
            light_color = Colors.ERROR
            dark_color = Colors.ERROR
        elif name == "convert":
            light_color = Colors.WARNING
            dark_color = Colors.WARNING
        elif name == "play":
            light_color = Colors.SUCCESS
            dark_color = Colors.SUCCESS
            
        light_img = cls._draw_icon(name, size, light_color)
        dark_img = cls._draw_icon(name, size, dark_color)
        
        ctk_img = ctk.CTkImage(
            light_image=light_img,
            dark_image=dark_img,
            size=(size, size)
        )
        cls._cache[cache_key] = ctk_img
        return ctk_img

    @classmethod
    def _draw_icon(cls, name, size, color):
        """Vẽ icon lên ảnh RGBA trong bộ nhớ."""
        # Vẽ ở size lớn (64x64) sau đó scale xuống size mục tiêu để chống răng cưa (Super Sampling)
        draw_size = 64
        img = Image.new("RGBA", (draw_size, draw_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        c = color
        
        if name == "download":
            # Mũi tên đi xuống + vạch ngang ở dưới
            draw.rounded_rectangle([10, 52, 54, 58], radius=3, fill=c)
            draw.rounded_rectangle([28, 6, 36, 42], radius=3, fill=c)
            draw.polygon([(16, 32), (48, 32), (32, 48)], fill=c)
            
        elif name == "history":
            # Đồng hồ
            draw.ellipse([8, 8, 56, 56], outline=c, width=5)
            draw.line([32, 32, 32, 18], fill=c, width=5)
            draw.line([32, 32, 44, 32], fill=c, width=5)
            
        elif name == "queue":
            # Danh sách có các vạch dòng
            draw.rounded_rectangle([22, 14, 56, 20], radius=3, fill=c)
            draw.rounded_rectangle([22, 29, 56, 35], radius=3, fill=c)
            draw.rounded_rectangle([22, 44, 56, 50], radius=3, fill=c)
            # Dấu tick hoặc ô vuông bên trái
            draw.rounded_rectangle([8, 14, 14, 20], radius=1, fill=c)
            draw.rounded_rectangle([8, 29, 14, 35], radius=1, fill=c)
            draw.rounded_rectangle([8, 44, 14, 50], radius=1, fill=c)
            
        elif name == "convert":
            # Hai mũi tên ngược chiều (chuyển đổi)
            # Mũi tên 1: Trái qua phải
            draw.line([8, 22, 48, 22], fill=c, width=5)
            draw.polygon([(40, 12), (56, 22), (40, 32)], fill=c)
            # Mũi tên 2: Phải qua trái
            draw.line([56, 42, 16, 42], fill=c, width=5)
            draw.polygon([(24, 32), (8, 42), (24, 52)], fill=c)
            
        elif name == "log":
            # Hộp console hoặc terminal chứa dấu > _
            draw.rounded_rectangle([6, 6, 58, 58], radius=6, outline=c, width=4)
            # Dấu >
            draw.line([16, 20, 26, 28], fill=c, width=4)
            draw.line([26, 28, 16, 36], fill=c, width=4)
            # Dấu _
            draw.line([30, 36, 44, 36], fill=c, width=4)
            
        elif name == "dhk_logo":
            # Biểu trưng DHK cách điệu trong khung hình lục giác
            # Vẽ hình lục giác làm khung ngoài
            draw.polygon([(32, 6), (54, 19), (54, 45), (32, 58), (10, 45), (10, 19)], outline=c, width=4)
            # Chữ D (x=18 đến 25)
            draw.line([18, 22, 18, 42], fill=c, width=4)
            draw.line([18, 22, 22, 22], fill=c, width=4)
            draw.line([18, 42, 22, 42], fill=c, width=4)
            draw.line([22, 22, 25, 25, 25, 39, 22, 42], fill=c, width=4)
            # Chữ H (x=29 đến 35)
            draw.line([29, 22, 29, 42], fill=c, width=4)
            draw.line([35, 22, 35, 42], fill=c, width=4)
            draw.line([29, 32, 35, 32], fill=c, width=4)
            # Chữ K (x=39 đến 46)
            draw.line([39, 22, 39, 42], fill=c, width=4)
            draw.line([39, 32, 46, 22], fill=c, width=4)
            draw.line([39, 32, 46, 42], fill=c, width=4)

        elif name == "playlist":
            # Chồng các thẻ lên nhau đại diện cho album/playlist
            draw.rounded_rectangle([18, 8, 56, 40], radius=4, outline=c, width=4)
            draw.rounded_rectangle([13, 16, 51, 48], radius=4, outline=c, width=4)
            draw.rounded_rectangle([8, 24, 46, 56], radius=4, outline=c, width=4)
            
        elif name == "mp4":
            # Biểu tượng Play trong hình tròn/vuông bo góc
            draw.rounded_rectangle([6, 6, 58, 58], radius=12, outline=c, width=4)
            draw.polygon([(24, 18), (46, 32), (24, 46)], fill=c)
            
        elif name == "mp3":
            # Nốt nhạc kép
            # Nốt 1
            draw.ellipse([10, 42, 24, 54], fill=c)
            draw.line([22, 46, 22, 16], fill=c, width=5)
            # Nốt 2
            draw.ellipse([36, 34, 50, 46], fill=c)
            draw.line([48, 38, 48, 8], fill=c, width=5)
            # Thanh nối
            draw.polygon([(22, 16), (48, 8), (48, 16), (22, 24)], fill=c)
            
        elif name == "folder":
            # Thư mục
            # Thân thư mục
            draw.rounded_rectangle([8, 20, 56, 56], radius=4, outline=c, width=4)
            # Tab thư mục
            draw.polygon([(8, 20), (22, 20), (28, 28), (8, 28)], fill=c)
            
        elif name == "cookie":
            # Bánh quy cookie có các chấm chocolate
            draw.ellipse([8, 8, 56, 56], outline=c, width=4)
            draw.ellipse([20, 20, 26, 26], fill=c)
            draw.ellipse([40, 24, 46, 30], fill=c)
            draw.ellipse([24, 40, 30, 46], fill=c)
            draw.ellipse([42, 42, 48, 48], fill=c)
            draw.ellipse([32, 32, 36, 36], fill=c)
            
        elif name == "paste":
            # Bảng kẹp giấy (Clipboard)
            draw.rounded_rectangle([14, 16, 50, 58], radius=4, outline=c, width=4)
            draw.rounded_rectangle([24, 8, 40, 20], radius=2, fill=c)
            
        elif name == "search":
            # Kính lúp
            draw.ellipse([10, 10, 42, 42], outline=c, width=5)
            draw.line([38, 38, 54, 54], fill=c, width=6)
            
        elif name == "delete":
            # Thùng rác
            draw.rounded_rectangle([24, 6, 40, 12], radius=1, outline=c, width=3)
            draw.line([10, 14, 54, 14], fill=c, width=4)
            draw.polygon([(14, 16), (50, 16), (44, 58), (20, 58)], outline=c, width=4)
            draw.line([26, 24, 26, 50], fill=c, width=3)
            draw.line([38, 24, 38, 50], fill=c, width=3)
            
        elif name == "cancel":
            # Dấu X
            draw.line([14, 14, 50, 50], fill=c, width=6)
            draw.line([50, 14, 14, 50], fill=c, width=6)
            
        elif name == "play":
            # Tam giác Play đơn
            draw.polygon([(20, 12), (52, 32), (20, 52)], fill=c)
            
        elif name == "pause":
            # Hai vạch đứng
            draw.rounded_rectangle([18, 12, 28, 52], radius=2, fill=c)
            draw.rounded_rectangle([36, 12, 46, 52], radius=2, fill=c)
            
        else:
            # Fallback hình vuông hỏi chấm
            draw.rounded_rectangle([10, 10, 54, 54], radius=6, outline=c, width=4)
            draw.line([22, 22, 42, 42], fill=c, width=4)
            draw.line([42, 22, 22, 42], fill=c, width=4)
            
        # Thu nhỏ bằng LANCZOS để chống răng cưa đẹp mắt
        return img.resize((size, size), Image.Resampling.LANCZOS)
