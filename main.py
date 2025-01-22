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
        
        # 设置窗口最小尺寸
        self.root.minsize(800, 600)
        
        # 配置主题和样式
        self.style = ttk.Style()
        self.style.theme_use('clam')  # 使用clam主题获得现代外观
        self.configure_styles()
        
        # 初始化管理器
        self.note_manager = NoteManager()
        self.notification_manager = NotificationManager()
        
        # 设置提醒时间更新回调
        self.notification_manager.set_update_callback(self.update_reminder_time)
        
        # 创建主界面
        self.create_widgets()
        
        # 加载现有记事
        self.load_notes()
        
        # 创建系统托盘图标
        self.setup_system_tray()
        
        # 绑定窗口事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind("<Unmap>", self.on_minimize)  # 最小化事件
        
        # 窗口状态标志
        self.is_minimized = False

    def setup_system_tray(self):
        """设置系统托盘图标和菜单"""
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
        self.tray_icon.run_detached()

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
        if not self.is_minimized:
            self.hide_window()
            return "break"  # 阻止默认的最小化行为

    def quit_app(self, icon=None, item=None):
        """退出应用程序"""
        self.on_closing()  # 复用关闭窗口的逻辑

    def on_closing(self):
        """处理窗口关闭事件"""
        if messagebox.askyesno("确认退出", "确定要退出应用吗？"):
            # 清理提醒管理器
            self.notification_manager.cleanup()
            # 停止系统托盘图标
            if hasattr(self, 'tray_icon'):
                self.tray_icon.stop()
            # 退出应用
            self.root.quit()
            self.root.destroy()

    def configure_styles(self):
        """配置主题和样式"""
        # 设置窗口样式
        self.style.configure('Treeview', rowheight=25)  # 设置表格行高
        self.style.configure('TButton', padding=5)  # 设置按钮内边距
        self.style.configure('Treeview.Heading', font=('微软雅黑', 10))  # 设置表头字体
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 设置窗口初始大小为屏幕的60%
        window_width = int(screen_width * 0.6)
        window_height = int(screen_height * 0.6)
        self.root.geometry(f"{window_width}x{window_height}")
        
        # 设置窗口图标和背景色
        self.root.configure(bg='#f0f0f0')

    def create_widgets(self):
        """创建主界面"""
        # 创建左右分隔的窗格
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧记事列表框架
        left_frame = ttk.Frame(self.paned, style='Card.TFrame')
        self.paned.add(left_frame, weight=2)

        # 创建记事列表
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ('title', 'date', 'reminder_time')
        self.note_list = ttk.Treeview(list_frame, columns=columns, show='headings', style='Custom.Treeview')
        
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
            title_width = max([len(str(note.get('title', ''))) * 20 for note in notes.values()], default=200)
            title_width = max(title_width, 200)  # 最小宽度200
            
            date_width = 120  # 固定日期列宽
            reminder_width = 120  # 固定提醒时间列宽
            
            # 设置列宽
            self.note_list.column('title', width=title_width, minwidth=200)
            self.note_list.column('date', width=date_width, minwidth=120)
            self.note_list.column('reminder_time', width=reminder_width, minwidth=120)
        
        # 绑定列宽调整函数到事件
        self.note_list.bind('<Configure>', adjust_columns)
        
        # 布局记事列表和滚动条
        self.note_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.note_list.bind('<<TreeviewSelect>>', self.on_select_note)

        # 右侧编辑区域框架
        right_frame = ttk.Frame(self.paned)
        self.paned.add(right_frame, weight=1)

        # 创建文本编辑区
        self.text_edit = tk.Text(right_frame, wrap=tk.WORD)
        self.text_edit.pack(fill=tk.BOTH, expand=True)
        
        # 绑定文本变化事件
        self.text_edit.bind('<<Modified>>', self.on_text_modified)
        
        # 创建按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="新建记事", command=self.new_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除记事", command=self.delete_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="设置日期", command=self.set_date).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="设置提醒时间", command=self.set_reminder).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="退出", command=self.quit_app).pack(side=tk.RIGHT, padx=5)
        
        # 初次调整列宽
        self.root.update()  # 确保窗口已经创建
        adjust_columns()
        
        # 设置初始分隔位置
        window_width = self.root.winfo_width()
        self.paned.sashpos(0, int(window_width * 0.65))  # 增加左侧比例到65%

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
            self.note_list.insert('', 'end', note_id, values=(title, date, reminder_time))

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
        
        # 使窗口置顶
        new_note_window.transient(self.root)
        new_note_window.grab_set()
        
        # 标题框架
        title_frame = ttk.Frame(new_note_window)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(title_frame, text="标题：").pack(side=tk.LEFT)
        title_entry = ttk.Entry(title_frame)
        title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 内容框架
        content_frame = ttk.Frame(new_note_window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(content_frame, text="内容：").pack(anchor=tk.W)
        content_text = tk.Text(content_frame, wrap=tk.WORD)
        content_text.pack(fill=tk.BOTH, expand=True)
        
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
        button_frame = ttk.Frame(new_note_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="取消", command=new_note_window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存", command=save_note).pack(side=tk.LEFT, padx=5)

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
        """设置日期"""
        selected_items = self.note_list.selection()
        if not selected_items:
            messagebox.showwarning("提示", "请先选择一个记事！")
            return
        
        note_id = selected_items[0]
        note = self.note_manager.get_note(note_id)
        if not note:
            return
        
        # 创建日期选择窗口
        date_window = tk.Toplevel(self.root)
        date_window.title("选择日期")
        
        # 设置窗口大小和位置
        window_width = 300
        window_height = 250
        screen_width = date_window.winfo_screenwidth()
        screen_height = date_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        date_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 使窗口置顶
        date_window.transient(self.root)
        date_window.grab_set()
        
        # 创建日期选择器
        cal = DateEntry(date_window, width=12, background='darkblue',
                       foreground='white', borderwidth=2,
                       locale='zh_CN',  # 使用中文
                       date_pattern='yyyy-mm-dd')  # 设置日期格式
        cal.pack(padx=10, pady=10)
        
        def save_date():
            """保存选择的日期"""
            try:
                selected_date = cal.get_date()
                formatted_date = selected_date.strftime("%Y-%m-%d")
                
                # 更新记事的日期
                note = self.note_manager.get_note(note_id)
                if note:
                    note['date'] = formatted_date
                    self.note_manager.update_note(
                        note_id,
                        note['title'],
                        note['content'],
                        formatted_date,
                        note.get('reminder_time', '')
                    )
                    
                    # 刷新记事列表
                    self.load_notes()
                    
                    # 显示成功消息
                    messagebox.showinfo("成功", "日期已更新！")
                    
                # 关闭窗口
                date_window.destroy()
                
            except Exception as e:
                messagebox.showerror("错误", f"设置日期时出错：{str(e)}")
        
        # 创建按钮框架
        button_frame = ttk.Frame(date_window)
        button_frame.pack(pady=10)
        
        # 确定按钮
        confirm_button = ttk.Button(button_frame, text="确定", command=save_date)
        confirm_button.pack(side=tk.LEFT, padx=5)
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=date_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)

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
        window_height = 300
        screen_width = reminder_window.winfo_screenwidth()
        screen_height = reminder_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        reminder_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建主框架
        main_frame = ttk.Frame(reminder_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建日期选择器
        ttk.Label(main_frame, text="选择日期：", font=('微软雅黑', 10)).pack(anchor=tk.W, pady=(0, 5))
        date_picker = DateEntry(main_frame, width=20, background='darkblue',
                              foreground='white', borderwidth=2)
        date_picker.pack(anchor=tk.W, pady=(0, 20))
        
        # 创建时间输入框架
        time_frame = ttk.Frame(main_frame)
        time_frame.pack(fill=tk.X)
        
        ttk.Label(time_frame, text="选择时间：", font=('微软雅黑', 10)).pack(anchor=tk.W)
        
        time_inputs_frame = ttk.Frame(time_frame)
        time_inputs_frame.pack(anchor=tk.W, pady=(5, 0))
        
        # 时间变量
        hour_var = tk.StringVar(value="00")
        minute_var = tk.StringVar(value="00")
        second_var = tk.StringVar(value="00")
        
        # 如果已有提醒时间，则填充
        if note.get('reminder_time'):
            try:
                reminder_datetime = datetime.strptime(note['reminder_time'], "%Y-%m-%d %H:%M:%S")
                date_picker.set_date(reminder_datetime.date())
                hour_var.set(f"{reminder_datetime.hour:02d}")
                minute_var.set(f"{reminder_datetime.minute:02d}")
                second_var.set(f"{reminder_datetime.second:02d}")
            except ValueError:
                pass  # 如果日期格式不正确，使用默认值
        
        # 时间输入框样式
        spinbox_style = {'width': 5, 'font': ('微软雅黑', 10)}
        
        hour_spinbox = ttk.Spinbox(time_inputs_frame, from_=0, to=23,
                                  format="%02.0f", textvariable=hour_var, **spinbox_style)
        hour_spinbox.pack(side=tk.LEFT, padx=2)
        ttk.Label(time_inputs_frame, text="时", font=('微软雅黑', 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        minute_spinbox = ttk.Spinbox(time_inputs_frame, from_=0, to=59,
                                    format="%02.0f", textvariable=minute_var, **spinbox_style)
        minute_spinbox.pack(side=tk.LEFT, padx=2)
        ttk.Label(time_inputs_frame, text="分", font=('微软雅黑', 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        second_spinbox = ttk.Spinbox(time_inputs_frame, from_=0, to=59,
                                    format="%02.0f", textvariable=second_var, **spinbox_style)
        second_spinbox.pack(side=tk.LEFT, padx=2)
        ttk.Label(time_inputs_frame, text="秒", font=('微软雅黑', 10)).pack(side=tk.LEFT)
        
        # 创建按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # 按钮样式
        style = ttk.Style()
        style.configure('Custom.TButton', font=('微软雅黑', 10), padding=5)
        
        def save_reminder():
            try:
                hour = int(hour_var.get())
                minute = int(minute_var.get())
                second = int(second_var.get())
                
                if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
                    messagebox.showerror("错误", "请输入有效的时间！")
                    return
                
                # 获取选择的日期
                selected_date = date_picker.get_date()
                
                # 组合日期和时间
                reminder_time = datetime.combine(
                    selected_date,
                    datetime.strptime(f"{hour}:{minute}:{second}", "%H:%M:%S").time()
                )
                
                # 检查是否是过去的时间
                if reminder_time < datetime.now():
                    messagebox.showerror("错误", "不能设置过去的时间！")
                    return
                
                formatted_time = reminder_time.strftime("%Y-%m-%d %H:%M:%S")
                
                # 更新记事的提醒时间
                if note_id in self.note_manager.notes:
                    self.note_manager.notes[note_id]['reminder_time'] = formatted_time
                    self.note_manager.save_notes(self.note_manager.notes)
                    
                    # 更新提醒管理器
                    if note_id in self.notification_manager.reminders:
                        self.notification_manager.reminders[note_id].cancel()
                    self.notification_manager.add_reminder(
                        note_id,
                        note['title'],
                        note['content'],
                        formatted_time  # 使用格式化后的时间字符串
                    )
                    
                    # 直接更新主窗口中的提醒时间显示
                    for item in self.note_list.get_children():
                        if item == note_id:
                            values = list(self.note_list.item(item)['values'])
                            values[2] = formatted_time
                            self.note_list.item(item, values=values)
                            break
                    
                    # 关闭窗口并显示成功消息
                    reminder_window.destroy()
                    messagebox.showinfo("成功", "提醒时间设置成功！")
                    return True
                
                return False
                
            except ValueError as e:
                print(f"Error: {e}")  # 添加错误日志
                messagebox.showerror("错误", "请输入有效的时间！")
                return False
        
        # 创建按钮
        ttk.Button(button_frame, text="取消", command=reminder_window.destroy,
                  style='Custom.TButton').pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="确定", command=save_reminder,
                  style='Custom.TButton').pack(side=tk.RIGHT, padx=5)
        
        # 设置窗口为模态
        reminder_window.transient(self.root)
        reminder_window.grab_set()

    def show_reminder(self, note_id):
        """显示提醒窗口"""
        note = self.note_manager.get_note(note_id)
        if note:
            reminder_window = tk.Toplevel(self.root)
            reminder_window.title("记事提醒")
            
            # 设置窗口大小和位置
            window_width = 400
            window_height = 300
            screen_width = reminder_window.winfo_screenwidth()
            screen_height = reminder_window.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            reminder_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # 标题标签
            title_label = ttk.Label(reminder_window, text=note['title'], font=("Arial", 12, "bold"))
            title_label.pack(pady=10)
            
            # 内容文本框
            content_frame = ttk.Frame(reminder_window)
            content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            content_text = tk.Text(content_frame, wrap=tk.WORD, height=8)
            content_text.insert("1.0", note['content'])
            content_text.config(state="disabled")
            content_text.pack(fill=tk.BOTH, expand=True)
            
            # 延迟提醒选项
            delay_frame = ttk.Frame(reminder_window)
            delay_frame.pack(fill=tk.X, padx=10, pady=5)
            
            delay_var = tk.BooleanVar()
            delay_check = ttk.Checkbutton(delay_frame, text="延迟提醒", variable=delay_var)
            delay_check.pack(side=tk.LEFT)
            
            delay_time = ttk.Spinbox(delay_frame, from_=1, to=60, width=5)
            delay_time.set(5)  # 默认5分钟
            delay_time.pack(side=tk.LEFT, padx=5)
            delay_time.config(state="disabled")
            
            ttk.Label(delay_frame, text="分钟后再次提醒").pack(side=tk.LEFT)
            
            def toggle_delay_options():
                """切换延迟选项的启用状态"""
                if delay_var.get():
                    delay_time.config(state="normal")
                else:
                    delay_time.config(state="disabled")
            
            delay_check.config(command=toggle_delay_options)
            
            def on_confirm():
                """确认按钮点击事件"""
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
                            self.note_manager.save_notes()  # 保存到文件
                            
                            # 更新提醒管理器中的提醒时间
                            if note_id in self.notification_manager.reminders:
                                self.notification_manager.reminders[note_id].cancel()  # 取消旧的提醒
                            self.notification_manager.add_reminder(
                                note_id,
                                note['title'],
                                note['content'],
                                new_reminder_time
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
            
            # 确定按钮
            ttk.Button(reminder_window, text="确定", command=on_confirm).pack(pady=10)
            
            # 播放提示音
            reminder_window.bell()
            
            # 窗口置顶
            reminder_window.lift()
            reminder_window.focus_force()

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

if __name__ == "__main__":
    root = tk.Tk()
    app = NoteApp(root)
    app.root.mainloop()
