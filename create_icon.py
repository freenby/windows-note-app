"""
创建应用程序图标
生成一个现代化的笔记本图标，使用 PIL 库绘制
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_modern_note_icon(size=(256, 256), bg_color="#4A90E2", save_path="app_icon.ico"):
    """
    创建一个现代化的笔记本图标
    
    Args:
        size: 图标尺寸，默认 256x256
        bg_color: 背景颜色，默认使用现代蓝色
        save_path: 保存路径
    """
    # 创建图像和绘图对象
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # 计算基本尺寸
    width, height = size
    padding = width // 8
    note_width = width - (padding * 2)
    note_height = height - (padding * 2)
    
    # 绘制主要笔记本形状（带圆角的矩形）
    def rounded_rectangle(draw, xy, radius, fill):
        x1, y1, x2, y2 = xy
        draw.rectangle((x1 + radius, y1, x2 - radius, y2), fill=fill)
        draw.rectangle((x1, y1 + radius, x2, y2 - radius), fill=fill)
        draw.ellipse((x1, y1, x1 + radius * 2, y1 + radius * 2), fill=fill)
        draw.ellipse((x2 - radius * 2, y1, x2, y1 + radius * 2), fill=fill)
        draw.ellipse((x1, y2 - radius * 2, x1 + radius * 2, y2), fill=fill)
        draw.ellipse((x2 - radius * 2, y2 - radius * 2, x2, y2), fill=fill)
    
    # 绘制主体
    rounded_rectangle(draw, 
                     (padding, padding, width - padding, height - padding),
                     radius=20,
                     fill=bg_color)
    
    # 添加装饰线条（模拟纸张）
    line_spacing = (note_height - 40) // 4
    line_color = "#FFFFFF"
    line_opacity = 96  # 透明度
    for i in range(4):
        y = padding + 30 + (i * line_spacing)
        draw.line([(padding + 20, y), (width - padding - 20, y)],
                 fill=line_color + hex(line_opacity)[2:].zfill(2),
                 width=2)
    
    # 添加一个小装饰，比如一个圆点或者别的标记
    dot_size = 12
    dot_color = "#FFFFFF"
    draw.ellipse((width - padding - 30, padding + 10,
                  width - padding - 30 + dot_size,
                  padding + 10 + dot_size),
                 fill=dot_color)
    
    # 保存不同尺寸的图标
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icons = []
    for s in sizes:
        icon = image.resize(s, Image.Resampling.LANCZOS)
        icons.append(icon)
    
    # 保存为ICO文件
    icons[0].save(save_path, format='ICO', sizes=sizes, append_images=icons[1:])
    print(f"图标已保存到: {save_path}")

if __name__ == '__main__':
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "app_icon.ico")
    
    # 创建图标
    create_modern_note_icon(save_path=icon_path)
