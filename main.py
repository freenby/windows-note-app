"""
记事本应用程序主模块
提供记事本的主要功能，包括创建、编辑、删除记事，以及设置提醒功能。
使用tkinter构建GUI界面，支持富文本编辑和定时提醒功能。
"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry
from note_manager import NoteManager
from notification_manager import NotificationManager
import pystray
from PIL import Image, ImageDraw
from calendar import Calendar
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import threading

class NoteApp:
    """记事本应用程序的主类，管理所有UI组件和业务逻辑"""

    def __init__(self, root):
        """
        初始化记事本应用程序
        
        Args:
            root: tkinter主窗口对象
        """
        self.root = root
        self.root.title("我的记事本")
        
        # 设置窗口最小尺寸 - 增加最小高度确保按钮可见
        self.root.minsize(800, 680)
        
        # 配置主题和样式
        self.style = ttk.Style()
        self.style.theme_use('clam')  # 使用clam主题获得现代外观
        self.configure_styles()
        
        # 创建按钮框架，使用现代布局
        button_frame = ttk.Frame(self.root, style='TFrame')
        button_frame.pack(fill=tk.X, padx=15, pady=(5, 15), side=tk.BOTTOM)
        
        # 左侧操作按钮组
        left_buttons = ttk.Frame(button_frame, style='TFrame')
        left_buttons.pack(side=tk.LEFT)
        
        ttk.Button(left_buttons, text="✚ 新建记事", style='Accent.TButton', command=self.new_note).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_buttons, text="🗑️ 删除记事", style='Warning.TButton', command=self.delete_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(left_buttons, text="📅 设置日期", command=self.set_date).pack(side=tk.LEFT, padx=5)
        ttk.Button(left_buttons, text="⏰ 设置提醒", command=self.set_reminder).pack(side=tk.LEFT, padx=5)
        
        # 右侧退出按钮
        right_buttons = ttk.Frame(button_frame, style='TFrame')
        right_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(right_buttons, text="退出", style='Warning.TButton', command=self.quit_app).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 创建主内容框架
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 初始化管理器
        self.note_manager = NoteManager()
        self.notification_manager = NotificationManager()
        
        # 设置提醒时间更新回调
        self.notification_manager.set_update_callback(self.update_reminder_time)
        
        # 创建主界面
        self.create_widgets(content_frame)
        
        # 加载现有记事
        self.load_notes()
        
        # 窗口状态标志
        self.is_minimized = False
        # 添加一个标志来控制是否应该响应Unmap事件
        self.allow_minimize_to_tray = False
        
        # 创建系统托盘图标
        self.setup_system_tray()
        
        # 绑定窗口事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind("<Unmap>", self.on_minimize)  # 最小化事件
        
        # 延迟设置允许最小化到托盘的标志，确保初始启动时不会触发最小化
        self.root.after(1000, self.enable_minimize_to_tray)

    def setup_system_tray(self):
        """设置系统托盘图标和菜单"""
        try:
            # 创建托盘图标
            icon_image = self.create_tray_icon()
            
            # 创建托盘菜单
            menu = (
                pystray.MenuItem("显示", self.show_window),
                pystray.MenuItem("退出", self.quit_app)
            )
            
            # 创建系统托盘图标
            self.tray_icon = pystray.Icon(
                "note_app",
                icon_image,
                "我的记事本",
                menu
            )
            
            # 在单独的线程中启动托盘图标
            def run_icon_detached():
                try:
                    self.tray_icon.run_detached()
                except Exception as e:
                    print(f"托盘图标启动错误: {str(e)}")
            
            threading.Thread(target=run_icon_detached, daemon=True).start()
        except Exception as e:
            print(f"设置系统托盘图标失败: {str(e)}")
            # 如果托盘图标设置失败，应用程序仍可以继续运行
            pass

    def create_tray_icon(self, size=(64, 64)):
        """
        创建托盘图标图像
        
        Returns:
            PIL.Image: 托盘图标图像
        """
        # 创建图像
        image = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 绘制一个简单的图标
        padding = 4
        draw.rectangle(
            [padding, padding, size[0]-padding, size[1]-padding],
            fill='#4A90E2',
            outline='white',
            width=2
        )
        
        # 添加一些装饰线条
        line_y = size[1] // 4
        for i in range(3):
            y = line_y + (i * line_y)
            draw.line(
                [size[0]//4, y, size[0]*3//4, y],
                fill='white',
                width=2
            )
        
        return image

    def show_window(self, icon=None, item=None):
        """显示主窗口"""
        self.root.deiconify()  # 显示窗口
        self.root.state('normal')  # 确保窗口不是最小化状态
        self.root.focus_force()  # 强制获取焦点
        self.is_minimized = False

    def hide_window(self):
        """隐藏主窗口"""
        self.root.withdraw()  # 隐藏窗口
        self.is_minimized = True

    def on_minimize(self, event=None):
        """处理窗口最小化事件"""
        # 只有当allow_minimize_to_tray为True时才响应最小化事件
        if self.allow_minimize_to_tray and not self.is_minimized:
            self.hide_window()
            return "break"  # 阻止默认的最小化行为
        return None  # 允许默认最小化行为

    def quit_app(self, icon=None, item=None):
        """退出应用程序"""
        # 如果从系统托盘图标调用，确保在主线程执行关闭操作
        if icon is not None:
            # 显示窗口，然后在主线程中调用关闭方法
            self.show_window()
            self.root.after(100, self.on_closing)
        else:
            # 直接从应用程序界面调用
            self.on_closing()

    def on_closing(self):
        """处理窗口关闭事件"""
        # 询问用户是否要最小化到托盘或退出应用
        response = messagebox.askyesnocancel(
            "关闭选项", 
            "您要将应用最小化到系统托盘吗？\n\n选择\"是\"：最小化到托盘\n选择\"否\"：退出应用\n选择\"取消\"：取消操作"
        )
        
        # 用户选择"是"，最小化到托盘
        if response is True:
            self.hide_window()
            return
        
        # 用户选择"否"，退出应用
        elif response is False:
            try:
                # 清理提醒管理器
                self.notification_manager.cleanup()
                
                # 停止系统托盘图标 - 在单独的线程中执行
                if hasattr(self, 'tray_icon'):
                    try:
                        # 使用线程安全的方式停止图标
                        threading.Thread(target=self.tray_icon.stop).start()
                    except:
                        pass
                
                # 退出应用
                self.root.quit()
                self.root.destroy()
            except Exception as e:
                print(f"退出时发生错误: {str(e)}")
                # 确保应用程序退出
                import os
                os._exit(0)
        
        # 用户选择"取消"，保持当前状态
        # 不做任何操作

    def configure_styles(self):
        """配置主题和样式"""
        # 设置窗口样式
        self.style = ttk.Style()
        self.style.theme_use('clam')  # 使用clam主题作为基础
        
        # 定义主题颜色
        primary_color = "#4A86E8"     # 主色调 - 蓝色
        secondary_color = "#f5f5f5"   # 次要色调 - 浅灰色
        accent_color = "#34A853"      # 强调色 - 绿色
        warning_color = "#EA4335"     # 警告色 - 红色
        text_color = "#333333"        # 文本色 - 深灰色
        light_text = "#FFFFFF"        # 浅色文本 - 白色
        border_color = "#E0E0E0"      # 边框色 - 浅灰色
        hover_color = "#3D75D6"       # 悬停色 - 深蓝色
        
        # 字体设置
        main_font = ('微软雅黑', 10)
        header_font = ('微软雅黑', 11, 'bold')
        button_font = ('微软雅黑', 10)
        
        # 配置Treeview样式
        self.style.configure('Treeview', 
                             background=secondary_color,
                             fieldbackground=secondary_color,
                             foreground=text_color,
                             font=main_font,
                             rowheight=30,
                             borderwidth=0)
        
        self.style.map('Treeview', 
                      background=[('selected', primary_color)],
                      foreground=[('selected', light_text)])
        
        self.style.configure('Treeview.Heading', 
                             font=header_font,
                             background=primary_color,
                             foreground=light_text,
                             padding=5)
        
        # 配置按钮样式
        self.style.configure('TButton', 
                            font=button_font,
                            background=primary_color,
                            foreground=light_text,
                            padding=(10, 5),
                            relief='flat')
        
        self.style.map('TButton',
                      background=[('active', hover_color), ('pressed', hover_color)],
                      relief=[('pressed', 'flat'), ('!pressed', 'flat')])
        
        # 创建强调按钮样式
        self.style.configure('Accent.TButton',
                            font=button_font,
                            background=accent_color,
                            foreground=light_text,
                            padding=(10, 5))
        
        self.style.map('Accent.TButton',
                      background=[('active', "#2D964A"), ('pressed', "#2D964A")])
        
        # 配置警告按钮样式
        self.style.configure('Warning.TButton',
                            font=button_font,
                            background=warning_color,
                            foreground=light_text,
                            padding=(10, 5))
        
        self.style.map('Warning.TButton',
                      background=[('active', "#D03B2F"), ('pressed', "#D03B2F")])
        
        # 配置Frame样式
        self.style.configure('TFrame', background=secondary_color)
        
        # 配置标签样式
        self.style.configure('TLabel', 
                            font=main_font,
                            background=secondary_color,
                            foreground=text_color)
        
        self.style.configure('Header.TLabel',
                            font=header_font,
                            background=secondary_color,
                            foreground=primary_color)
        
        # 配置文本框样式
        self.style.configure('TEntry', 
                            font=main_font,
                            fieldbackground=light_text,
                            foreground=text_color,
                            borderwidth=1,
                            relief='solid')
        
        # 配置复选框样式
        self.style.configure('TCheckbutton',
                            font=main_font,
                            background=secondary_color,
                            foreground=text_color)
        
        # 配置下拉框样式
        self.style.configure('TCombobox',
                            font=main_font,
                            background=light_text,
                            foreground=text_color)
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 设置窗口初始大小为屏幕的70%
        window_width = int(screen_width * 0.7)
        window_height = int(screen_height * 0.7)
        self.root.geometry(f"{window_width}x{window_height}")
        
        # 设置窗口背景色和图标
        self.root.configure(bg=secondary_color)
        
        # 尝试设置窗口图标，如果文件不存在则忽略
        try:
            self.root.iconbitmap('app.ico')
        except:
            pass

    def create_widgets(self, parent_frame):
        """创建主界面"""
        # 创建左右分隔的窗格
        self.paned = ttk.PanedWindow(parent_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # 左侧记事列表框架
        left_frame = ttk.Frame(self.paned)
        self.paned.add(left_frame, weight=2)
        
        # 添加标题标签
        ttk.Label(left_frame, text="我的记事", style='Header.TLabel', font=('微软雅黑', 14, 'bold')).pack(side=tk.TOP, anchor=tk.W, padx=10, pady=(10, 5))

        # 创建记事列表框架，添加边框效果
        list_frame = ttk.Frame(left_frame, style='TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ('title', 'date', 'reminder_time')
        self.note_list = ttk.Treeview(list_frame, columns=columns, show='headings', style='Treeview')
        
        # 设置列标题
        self.note_list.heading('title', text='标题')
        self.note_list.heading('date', text='日期')
        self.note_list.heading('reminder_time', text='提醒时间')
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.note_list.yview)
        self.note_list.configure(yscrollcommand=scrollbar.set)
        
        # 设置列宽自动调整
        def adjust_columns(event=None):
            # 获取所有记事数据
            notes = self.note_manager.get_all_notes()
            
            # 计算每列需要的最大宽度（使用中文字符宽度）
            title_width = max([len(str(note.get('title', ''))) * 20 for note in notes.values()], default=250)
            title_width = max(title_width, 250)  # 最小宽度增加到250
            
            date_width = 150  # 增加日期列宽
            reminder_width = 180  # 增加提醒时间列宽
            
            # 设置列宽
            self.note_list.column('title', width=title_width, minwidth=250)
            self.note_list.column('date', width=date_width, minwidth=150)
            self.note_list.column('reminder_time', width=reminder_width, minwidth=180)
        
        # 绑定列宽调整函数到事件
        self.note_list.bind('<Configure>', adjust_columns)
        
        # 布局记事列表和滚动条
        self.note_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.note_list.bind('<<TreeviewSelect>>', self.on_select_note)

        # 右侧编辑区域框架
        right_frame = ttk.Frame(self.paned)
        self.paned.add(right_frame, weight=3)
        
        # 添加内容编辑标题
        ttk.Label(right_frame, text="记事内容", style='Header.TLabel', font=('微软雅黑', 14, 'bold')).pack(side=tk.TOP, anchor=tk.W, padx=10, pady=(10, 5))

        # 创建文本编辑区，添加边框和内边距
        text_frame = ttk.Frame(right_frame, style='TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 设置文本编辑区样式
        self.text_edit = tk.Text(text_frame, wrap=tk.WORD, font=('微软雅黑', 11),
                               bg='white', fg='#333333', padx=10, pady=10,
                               relief='flat', borderwidth=0)
        
        # 添加文本滚动条
        text_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_edit.yview)
        self.text_edit.configure(yscrollcommand=text_scrollbar.set)
        
        self.text_edit.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定文本变化事件
        self.text_edit.bind('<<Modified>>', self.on_text_modified)
        
        # 初次调整列宽
        parent_frame.update()  # 确保窗口已经创建
        adjust_columns()
        
        # 设置初始分隔位置
        window_width = parent_frame.winfo_width()
        self.paned.sashpos(0, int(window_width * 0.55))  # 左侧占55%，增加比例

    def load_notes(self):
        """加载现有记事"""
        # 清空现有项目
        for item in self.note_list.get_children():
            self.note_list.delete(item)
        
        # 重新加载所有记事
        notes = self.note_manager.get_all_notes()
        # 按创建时间倒序排序，最新的记事显示在最上面
        sorted_notes = sorted(
            notes.items(),
            key=lambda x: datetime.strptime(x[1].get('created_at', '1970-01-01'), '%Y-%m-%dT%H:%M:%S.%f'),
            reverse=True
        )
        
        for note_id, note in sorted_notes:
            title = note.get('title', '无标题')
            date = note.get('date', '')
            reminder_time = note.get('reminder_time', '')
            
            # 确保提醒时间字段不为None
            if reminder_time is None:
                reminder_time = ''
                
            self.note_list.insert('', 'end', note_id, values=(title, date, reminder_time))
            
            # 调试输出，帮助排查问题
            print(f"加载记事: ID={note_id}, 标题={title}, 日期={date}, 提醒时间={reminder_time}")

    def new_note(self):
        """创建新记事"""
        # 创建新记事窗口
        new_note_window = tk.Toplevel(self.root)
        new_note_window.title("新建记事")
        
        # 设置窗口大小和位置
        window_width = 500
        window_height = 400
        screen_width = new_note_window.winfo_screenwidth()
        screen_height = new_note_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        new_note_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置窗口样式
        new_note_window.configure(bg="#f5f5f5")
        
        # 使窗口置顶
        new_note_window.transient(self.root)
        new_note_window.grab_set()
        
        # 主内容框架
        main_frame = ttk.Frame(new_note_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加标题标签
        ttk.Label(main_frame, text="创建新记事", style='Header.TLabel', font=('微软雅黑', 14, 'bold')).pack(anchor=tk.W, pady=(0, 15))
        
        # 标题框架
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="标题：", font=('微软雅黑', 10, 'bold')).pack(side=tk.LEFT)
        title_entry = ttk.Entry(title_frame, font=('微软雅黑', 10))
        title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 内容框架
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(content_frame, text="内容：", font=('微软雅黑', 10, 'bold')).pack(anchor=tk.W)
        
        # 内容文本编辑区和滚动条
        text_container = ttk.Frame(content_frame)
        text_container.pack(fill=tk.BOTH, expand=True)
        
        content_text = tk.Text(text_container, wrap=tk.WORD, font=('微软雅黑', 10),
                             height=10, padx=10, pady=10,
                             bg='white', fg='#333333',
                             relief='flat', borderwidth=0)
        content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        text_scroll = ttk.Scrollbar(text_container, orient=tk.VERTICAL, command=content_text.yview)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        content_text.configure(yscrollcommand=text_scroll.set)
        
        def save_note():
            """保存新记事"""
            title = title_entry.get().strip()
            content = content_text.get("1.0", tk.END).strip()
            
            if not title:
                messagebox.showwarning("警告", "请输入标题！")
                return
            
            if not content:
                messagebox.showwarning("警告", "请输入内容！")
                return
                
            # 创建新记事，设置当前日期为默认日期
            current_date = datetime.now().strftime("%Y-%m-%d")
            note_id = self.note_manager.add_note(
                title=title,
                content=content,
                date=current_date  # 添加默认日期
            )
            self.load_notes()
            new_note_window.destroy()
            
            # 添加到提醒管理器
            self.notification_manager.add_note(note_id, title)
            
            # 选中新创建的记事
            self.note_list.selection_set(note_id)
            self.note_list.see(note_id)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="取消", command=new_note_window.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="保存", style='Accent.TButton', command=save_note).pack(side=tk.RIGHT)

    def delete_note(self):
        """删除选中的记事"""
        selected_items = self.note_list.selection()
        if not selected_items:
            messagebox.showwarning("提示", "请先选择要删除的记事")
            return
            
        if messagebox.askyesno("确认", "确定要删除选中的记事吗？"):
            note_id = selected_items[0]
            # 从提醒管理器中移除
            self.notification_manager.remove_reminder(note_id)
            # 从记事管理器中删除
            self.note_manager.delete_note(note_id)
            # 清空编辑区
            self.text_edit.delete("1.0", tk.END)
            # 刷新列表
            self.load_notes()

    def set_date(self):
        """设置记事日期"""
        selected_items = self.note_list.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择一条记事！")
            return
        
        note_id = selected_items[0]
        note = self.note_manager.get_note(note_id)
        if not note:
            return
        
        # 创建日期选择窗口
        date_window = tk.Toplevel(self.root)
        date_window.title("设置日期")
        date_window.geometry("360x350")  # 增加窗口尺寸
        date_window.configure(bg="#f5f5f5")  # 设置背景色
        
        # 主内容框架
        main_frame = ttk.Frame(date_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加标题标签
        title_label = ttk.Label(main_frame, text="设置日期", style='Header.TLabel', font=('微软雅黑', 14, 'bold'))
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # 记事标题显示 - 显示当前编辑的记事标题
        note_title = note.get('title', '无标题')
        if len(note_title) > 20:  # 如果标题太长，截断显示
            note_title = note_title[:20] + "..."
            
        ttk.Label(main_frame, text=f"记事: {note_title}", font=('微软雅黑', 10)).pack(anchor=tk.W, pady=(0, 15))
        
        # 日期选择器框架
        cal_frame = ttk.Frame(main_frame)
        cal_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 创建日期选择器
        cal = DateEntry(cal_frame, width=12, background='#4A86E8',
                       foreground='white', borderwidth=0,
                       locale='zh_CN',  # 使用中文
                       date_pattern='yyyy-mm-dd',  # 设置日期格式
                       font=('微软雅黑', 10))
        cal.pack(fill=tk.X)
        
        # 如果记事有日期，则设置为默认值
        if note.get('date'):
            try:
                date_obj = datetime.strptime(note['date'], "%Y-%m-%d").date()
                cal.set_date(date_obj)
            except ValueError:
                pass
        
        # 显示星期几的标签
        weekday_label = ttk.Label(main_frame, text="", font=('微软雅黑', 10, 'bold'))
        weekday_label.pack(anchor=tk.CENTER, pady=(5, 15))
        
        def update_weekday(*args):
            weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
            selected_date = cal.get_date()
            weekday_idx = selected_date.weekday()  # 0 = Monday, 6 = Sunday
            weekday_label.config(text=weekdays[weekday_idx])
        
        # 绑定日期变化事件
        cal.bind('<<DateEntrySelected>>', update_weekday)
        # 初始化显示当前选择日期的星期
        update_weekday()

        # 循环提醒选项
        recurrence_frame = ttk.Frame(main_frame)
        recurrence_frame.pack(fill=tk.X, pady=(5, 15))
        
        # 标题
        ttk.Label(recurrence_frame, text="循环提醒:", font=('微软雅黑', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        # 循环选项
        options_frame = ttk.Frame(recurrence_frame)
        options_frame.pack(fill=tk.X)
        
        recurrence_day_var = tk.BooleanVar(value=False)
        recurrence_week_var = tk.BooleanVar(value=False)
        recurrence_month_var = tk.BooleanVar(value=False)
        
        # 根据记事的循环类型选择对应选项
        current_recurrence = note.get('recurrence', 'none')
        if current_recurrence == 'daily':
            recurrence_day_var.set(True)
        elif current_recurrence == 'weekly':
            recurrence_week_var.set(True)
        elif current_recurrence == 'monthly':
            recurrence_month_var.set(True)
        
        def on_recurrence_change(selected_var):
            # 当选中一个选项时，取消其他选项
            vars_dict = {
                'day': recurrence_day_var,
                'week': recurrence_week_var,
                'month': recurrence_month_var
            }
            for var_name, var in vars_dict.items():
                if var_name != selected_var and vars_dict[selected_var].get():
                    var.set(False)
        
        # 创建三个互斥的复选框
        day_cb = ttk.Checkbutton(options_frame, text="按日循环",
                                variable=recurrence_day_var,
                                command=lambda: on_recurrence_change('day'))
        day_cb.pack(side=tk.LEFT, padx=(0, 15))
        
        week_cb = ttk.Checkbutton(options_frame, text="按周循环",
                                 variable=recurrence_week_var,
                                 command=lambda: on_recurrence_change('week'))
        week_cb.pack(side=tk.LEFT, padx=(0, 15))
        
        month_cb = ttk.Checkbutton(options_frame, text="按月循环",
                                  variable=recurrence_month_var,
                                  command=lambda: on_recurrence_change('month'))
        month_cb.pack(side=tk.LEFT)
        
        def save_date():
            """保存选择的日期"""
            try:
                selected_date = cal.get_date()
                formatted_date = selected_date.strftime("%Y-%m-%d")
                
                # 确定循环类型
                if recurrence_day_var.get():
                    recurrence = "daily"
                elif recurrence_week_var.get():
                    recurrence = "weekly"
                elif recurrence_month_var.get():
                    recurrence = "monthly"
                else:
                    recurrence = "none"

                # 先更新原记事的日期和循环类型
                note['date'] = formatted_date
                note['recurrence'] = recurrence
                # 确保不会清除原记事的提醒时间
                if note.get('reminder_time'):
                    # 如果已有提醒时间，更新日期部分但保留时间部分
                    original_time = datetime.strptime(note['reminder_time'], "%Y-%m-%d %H:%M:%S")
                    new_reminder = datetime.combine(
                        datetime.strptime(formatted_date, "%Y-%m-%d").date(),
                        original_time.time()
                    )
                    note['reminder_time'] = new_reminder.strftime("%Y-%m-%d %H:%M:%S")
                    # 更新提醒管理器中的提醒
                    self.notification_manager.remove_reminder(note_id)
                    self.notification_manager.add_reminder(
                        note_id,
                        note['title'],
                        note['content'],
                        note['reminder_time'],
                        recurrence
                    )
                    
                    # 直接更新UI中的提醒时间显示
                    for item in self.note_list.get_children():
                        if item == note_id:
                            values = list(self.note_list.item(item)['values'])
                            values[2] = note['reminder_time']  # 更新提醒时间列
                            self.note_list.item(item, values=values)
                            break
                
                self.note_manager.notes[note_id] = note
                self.note_manager.save_notes(self.note_manager.notes)

                # 如果选择了循环模式但没有设置提醒时间，询问用户是否要设置提醒时间
                if recurrence in ("daily", "weekly", "monthly") and not note.get('reminder_time'):
                    if messagebox.askyesno("提示", "您选择了循环提醒，是否立即设置提醒时间？"):
                        date_window.destroy()  # 先关闭日期窗口
                        # 延迟一点时间调用set_reminder，确保UI更新
                        self.root.after(100, self.set_reminder)
                        return

                # 如果设置了循环提醒，则克隆一份新的记事
                if recurrence in ("daily", "weekly", "monthly"):
                    try:
                        # 创建新记事
                        new_note = note.copy()
                        
                        # 根据循环类型计算新的日期
                        if recurrence == "daily":
                            delta = timedelta(days=1)
                        elif recurrence == "weekly":
                            delta = timedelta(days=7)
                        else:  # monthly
                            delta = relativedelta(months=1)
                        
                        new_date = datetime.strptime(formatted_date, "%Y-%m-%d") + delta
                        new_note['date'] = new_date.strftime("%Y-%m-%d")

                        # 处理提醒时间
                        if note.get('reminder_time'):
                            # 如果原记事有提醒时间，保持相同的时间部分
                            original_time = datetime.strptime(note['reminder_time'], "%Y-%m-%d %H:%M:%S")
                            # 使用新日期，但保留原始时间部分
                            new_reminder_time = datetime.combine(
                                new_date.date(),
                                original_time.time()
                            )
                            new_note['reminder_time'] = new_reminder_time.strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            # 如果原记事没有提醒时间，新记事也不设置提醒时间
                            new_note['reminder_time'] = ""

                        # 保存新记事
                        new_note_id = self.note_manager.add_note(
                            title=new_note['title'],
                            content=new_note['content'],
                            date=new_note['date'],
                            reminder_time=new_note['reminder_time']
                        )

                        # 如果有提醒时间，添加到提醒管理器
                        if new_note['reminder_time']:
                            self.notification_manager.add_reminder(
                                new_note_id,
                                new_note['title'],
                                new_note['content'],
                                new_note['reminder_time'],
                                recurrence
                            )
                        print(f"[DEBUG] 已克隆新记事: ID={new_note_id}, 时间={new_note.get('reminder_time', '无')}")
                        
                        # 直接更新UI中的克隆记事显示
                        title = new_note.get('title', '无标题')
                        date = new_note.get('date', '')
                        reminder_time = new_note.get('reminder_time', '')
                        self.note_list.insert('', 'end', new_note_id, values=(title, date, reminder_time))

                    except Exception as e:
                        print(f"克隆失败: {str(e)}")
                        messagebox.showerror("错误", f"创建循环提醒失败: {str(e)}")

                # 刷新记事列表
                self.load_notes()
                
                # 显示成功消息
                messagebox.showinfo("成功", "日期已更新！")
                date_window.destroy()
                
            except Exception as e:
                messagebox.showerror("错误", f"设置日期时出错：{str(e)}")
        
        # 创建按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 创建按钮
        ttk.Button(button_frame, text="取消", command=date_window.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="确定", style='Accent.TButton', command=save_date).pack(side=tk.RIGHT, padx=(0, 5))
        
        # 设置窗口为模态
        date_window.transient(self.root)
        date_window.grab_set()

    def set_reminder(self):
        """设置提醒时间"""
        selected_items = self.note_list.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择一条记事！")
            return
        
        note_id = selected_items[0]
        note = self.note_manager.get_note(note_id)
        if not note:
            return
        
        # 创建提醒设置窗口
        reminder_window = tk.Toplevel(self.root)
        reminder_window.title("设置提醒时间")
        
        # 设置窗口大小和位置
        window_width = 400
        window_height = 320
        screen_width = reminder_window.winfo_screenwidth()
        screen_height = reminder_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        reminder_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        reminder_window.configure(bg="#f5f5f5")  # 设置背景色
        
        # 创建主框架
        main_frame = ttk.Frame(reminder_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加标题
        ttk.Label(main_frame, text="设置提醒时间", style='Header.TLabel', 
                 font=('微软雅黑', 14, 'bold')).pack(anchor=tk.W, pady=(0, 15))
        
        # 记事标题显示
        note_title = note.get('title', '无标题')
        if len(note_title) > 20:  # 如果标题太长，截断显示
            note_title = note_title[:20] + "..."
            
        ttk.Label(main_frame, text=f"记事: {note_title}", 
                 font=('微软雅黑', 10)).pack(anchor=tk.W, pady=(0, 15))
        
        # 显示当前提醒日期 (从记事中获取，若未设置则使用当前日期)
        note_date = note.get('date', datetime.now().strftime("%Y-%m-%d"))
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(date_frame, text="提醒日期:", 
                 font=('微软雅黑', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(date_frame, text=note_date, 
                 font=('微软雅黑', 10)).pack(side=tk.LEFT)
        
        # 创建时间输入框架
        ttk.Label(main_frame, text="设置提醒时间:", 
                 font=('微软雅黑', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        time_frame = ttk.Frame(main_frame)
        time_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 时间变量
        spinbox_style = {'width': 5, 'font': ('微软雅黑', 10)}
        hour_var = tk.StringVar(value="00")
        minute_var = tk.StringVar(value="00")
        second_var = tk.StringVar(value="00")
        
        # 如果已有提醒时间，则填充时间部分
        if note.get('reminder_time'):
            try:
                reminder_datetime = datetime.strptime(note['reminder_time'], "%Y-%m-%d %H:%M:%S")
                hour_var.set(f"{reminder_datetime.hour:02d}")
                minute_var.set(f"{reminder_datetime.minute:02d}")
                second_var.set(f"{reminder_datetime.second:02d}")
            except ValueError:
                pass
        
        hour_spinbox = ttk.Spinbox(time_frame, from_=0, to=23,
                                  format="%02.0f", textvariable=hour_var, **spinbox_style)
        hour_spinbox.pack(side=tk.LEFT, padx=(0, 2))
        ttk.Label(time_frame, text="时", font=('微软雅黑', 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        minute_spinbox = ttk.Spinbox(time_frame, from_=0, to=59,
                                    format="%02.0f", textvariable=minute_var, **spinbox_style)
        minute_spinbox.pack(side=tk.LEFT, padx=(0, 2))
        ttk.Label(time_frame, text="分", font=('微软雅黑', 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        second_spinbox = ttk.Spinbox(time_frame, from_=0, to=59,
                                    format="%02.0f", textvariable=second_var, **spinbox_style)
        second_spinbox.pack(side=tk.LEFT, padx=(0, 2))
        ttk.Label(time_frame, text="秒", font=('微软雅黑', 10)).pack(side=tk.LEFT)
        
        # 显示循环提醒设置
        recurrence_type = note.get('recurrence', 'none')
        if recurrence_type != 'none':
            recurrence_text = {
                'daily': '按日循环',
                'weekly': '按周循环',
                'monthly': '按月循环'
            }.get(recurrence_type, '')
            
            if recurrence_text:
                recurrence_frame = ttk.Frame(main_frame)
                recurrence_frame.pack(fill=tk.X, pady=(0, 15))
                
                ttk.Label(recurrence_frame, text="循环类型:", 
                         font=('微软雅黑', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
                ttk.Label(recurrence_frame, text=recurrence_text, 
                         foreground="#4A86E8", font=('微软雅黑', 10, 'bold')).pack(side=tk.LEFT)
        
        # 创建按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def save_reminder():
            try:
                hour = int(hour_var.get())
                minute = int(minute_var.get())
                second = int(second_var.get())
                
                if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
                    messagebox.showerror("错误", "请输入有效的时间！")
                    return
                
                # 使用记事中的日期与用户设置的时间组成完整提醒时间
                reminder_date = note_date  # note_date 为已设置的日期
                reminder_time = datetime.strptime(reminder_date, "%Y-%m-%d")
                reminder_time = reminder_time.replace(hour=hour, minute=minute, second=second)
                
                formatted_time = reminder_time.strftime("%Y-%m-%d %H:%M:%S")
                
                # 更新记事本身的提醒时间
                note['reminder_time'] = formatted_time
                self.note_manager.notes[note_id] = note
                self.note_manager.save_notes(self.note_manager.notes)
                
                # 更新提醒管理器（循环选项由记事中保存的 set_date 设置）
                self.notification_manager.remove_reminder(note_id)
                self.notification_manager.add_reminder(
                    note_id,
                    note['title'],
                    note['content'],
                    formatted_time,
                    note.get('recurrence', "none")
                )
                
                # 更新主窗口中的提醒时间显示
                for item in self.note_list.get_children():
                    if item == note_id:
                        values = list(self.note_list.item(item)['values'])
                        values[2] = formatted_time
                        self.note_list.item(item, values=values)
                        break
                
                reminder_window.destroy()
                messagebox.showinfo("成功", "提醒时间设置成功！")
                return True
                
            except ValueError as e:
                print(f"Error: {e}")
                messagebox.showerror("错误", "请输入有效的时间！")
                return False
        
        ttk.Button(button_frame, text="取消", command=reminder_window.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="确定", style='Accent.TButton', command=save_reminder).pack(side=tk.RIGHT, padx=(0, 5))
        
        # 设置窗口为模态
        reminder_window.transient(self.root)
        reminder_window.grab_set()

    def show_reminder(self, note_id):
        """显示提醒窗口"""
        try:
            note = self.note_manager.get_note(note_id)
            if not note:
                print(f"提醒显示错误: 找不到ID为 {note_id} 的记事")
                return
                
            reminder_window = tk.Toplevel(self.root)
            reminder_window.title("记事提醒")
            reminder_window.configure(bg="#f5f5f5")
            
            # 设置窗口大小和位置
            window_width = 400
            window_height = 350
            screen_width = reminder_window.winfo_screenwidth()
            screen_height = reminder_window.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            reminder_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # 创建主框架
            main_frame = ttk.Frame(reminder_window, padding=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 标题部分
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill=tk.X, pady=(0, 15))
            
            # 标题图标和文本
            ttk.Label(header_frame, text="⏰", font=("Arial", 24, "bold"), foreground="#4A86E8").pack(side=tk.LEFT, padx=(0, 10))
            ttk.Label(header_frame, text="记事提醒", style="Header.TLabel", font=("微软雅黑", 16, "bold")).pack(side=tk.LEFT)
            
            # 记事标题
            title_frame = ttk.Frame(main_frame)
            title_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(title_frame, text="标题:", font=("微软雅黑", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Label(title_frame, text=note.get('title', '无标题'), font=("微软雅黑", 10)).pack(side=tk.LEFT)
            
            # 内容标签
            ttk.Label(main_frame, text="内容:", font=("微软雅黑", 10, "bold")).pack(anchor=tk.W)
            
            # 内容文本框
            content_frame = ttk.Frame(main_frame)
            content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 15))
            
            content_text = tk.Text(content_frame, wrap=tk.WORD, height=8, 
                                 font=("微软雅黑", 10), bg="white", fg="#333333",
                                 padx=10, pady=10, relief="flat")
            content_text.insert("1.0", note.get('content', ''))
            content_text.config(state="disabled")
            
            # 添加滚动条
            text_scroll = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=content_text.yview)
            content_text.configure(yscrollcommand=text_scroll.set)
            
            content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 延迟提醒选项
            options_frame = ttk.Frame(main_frame)
            options_frame.pack(fill=tk.X, pady=(0, 15))
            
            # 标签
            ttk.Label(options_frame, text="延迟选项:", font=("微软雅黑", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
            
            delay_option_frame = ttk.Frame(options_frame)
            delay_option_frame.pack(fill=tk.X)
            
            delay_var = tk.BooleanVar()
            delay_check = ttk.Checkbutton(delay_option_frame, text="延迟提醒", variable=delay_var)
            delay_check.pack(side=tk.LEFT)
            
            delay_time_frame = ttk.Frame(delay_option_frame)
            delay_time_frame.pack(side=tk.LEFT, padx=(5, 0))
            
            delay_time = ttk.Spinbox(delay_time_frame, from_=1, to=60, width=5, format="%02.0f", font=("微软雅黑", 10))
            delay_time.set(5)  # 默认5分钟
            delay_time.pack(side=tk.LEFT, padx=(0, 5))
            delay_time.config(state="disabled")
            
            ttk.Label(delay_time_frame, text="分钟后再次提醒").pack(side=tk.LEFT)
            
            def toggle_delay_options():
                """切换延迟选项的启用状态"""
                if delay_var.get():
                    delay_time.config(state="normal")
                else:
                    delay_time.config(state="disabled")
            
            delay_check.config(command=toggle_delay_options)
            
            def on_confirm():
                """确认按钮点击事件"""
                try:
                    if delay_var.get():
                        try:
                            delay_minutes = int(delay_time.get())
                            # 计算新的提醒时间
                            current_time = datetime.now()
                            new_reminder_time = current_time + timedelta(minutes=delay_minutes)
                            formatted_time = new_reminder_time.strftime("%Y-%m-%d %H:%M:%S")
                            
                            # 更新记事的提醒时间
                            if note_id in self.note_manager.notes:
                                # 更新记事管理器中的数据
                                self.note_manager.notes[note_id]['reminder_time'] = formatted_time
                                self.note_manager.save_notes(self.note_manager.notes)  # 修正保存方法
                                
                                # 更新提醒管理器中的提醒时间
                                if note_id in self.notification_manager.reminders:
                                    self.notification_manager.remove_reminder(note_id)
                                    self.notification_manager.add_reminder(
                                        note_id,
                                        note.get('title', ''),
                                        note.get('content', ''),
                                        formatted_time,
                                        note.get('recurrence', "none")
                                    )
                                
                                # 直接更新记事列表中的显示
                                for item in self.note_list.get_children():
                                    if item == note_id:
                                        values = list(self.note_list.item(item)['values'])
                                        values[2] = formatted_time
                                        self.note_list.item(item, values=values)
                                        break
                                
                        except ValueError:
                            messagebox.showerror("错误", "请输入有效的延迟时间！")
                            return
                    
                    reminder_window.destroy()
                except Exception as e:
                    print(f"提醒确认错误: {str(e)}")
                    try:
                        reminder_window.destroy()
                    except:
                        pass
            
            # 按钮框架
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            # 确定按钮
            ttk.Button(button_frame, text="确定", style="Accent.TButton", command=on_confirm).pack(side=tk.RIGHT)
            
            # 播放提示音
            try:
                reminder_window.bell()
            except:
                pass
            
            # 窗口置顶
            reminder_window.lift()
            reminder_window.focus_force()
            try:
                reminder_window.attributes('-topmost', True)  # 确保窗口始终在最前
            except:
                pass
                
        except Exception as e:
            print(f"显示提醒窗口时发生错误: {str(e)}")
            # 错误处理 - 确保应用程序继续运行

    def on_select_note(self, event):
        """处理记事选择事件"""
        selected_items = self.note_list.selection()
        if not selected_items:
            return
            
        note_id = selected_items[0]
        note = self.note_manager.get_note(note_id)
        if note:
            # 清空当前内容
            self.text_edit.delete("1.0", tk.END)
            # 插入新内容
            self.text_edit.insert("1.0", note.get('content', ''))

    def on_text_modified(self, event=None):
        """处理文本修改事件"""
        if self.text_edit.edit_modified():
            selected_items = self.note_list.selection()
            if selected_items:
                note_id = selected_items[0]
                note = self.note_manager.get_note(note_id)
                if note:
                    content = self.text_edit.get("1.0", tk.END).strip()
                    self.note_manager.update_note(
                        note_id,
                        note['title'],
                        content,
                        note.get('date', ''),
                        note.get('reminder_time', '')
                    )
            self.text_edit.edit_modified(False)

    def update_reminder_time(self, note_id, new_time):
        """
        更新提醒时间的回调函数
        
        Args:
            note_id: 记事ID
            new_time: 新的提醒时间
        """
        # 更新记事管理器中的提醒时间
        if note_id in self.note_manager.notes:
            self.note_manager.notes[note_id]['reminder_time'] = new_time
            self.note_manager.save_notes(self.note_manager.notes)
            
            # 更新主窗口中的提醒时间显示
            for item in self.note_list.get_children():
                if item == note_id:
                    values = list(self.note_list.item(item)['values'])
                    values[2] = new_time
                    self.note_list.item(item, values=values)
                    break

    def enable_minimize_to_tray(self):
        """启用最小化到托盘的功能"""
        self.allow_minimize_to_tray = True

if __name__ == "__main__":
    root = tk.Tk()
    app = NoteApp(root)
    app.root.mainloop()
