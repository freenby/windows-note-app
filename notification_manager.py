"""
通知管理器模块
用于管理记事本的提醒功能，包括添加提醒、移除提醒、显示提醒窗口等功能。
支持延迟提醒功能，可以在提醒时设置延迟时间再次提醒。
"""

import threading
import time
from datetime import datetime, timedelta
import win32gui
import win32con
import winsound
import tkinter as tk
from tkinter import messagebox, ttk
import calendar  # 新增导入calendar模块

class NotificationManager:
    """通知管理器类，负责处理所有提醒相关的功能"""
    
    def __init__(self):
        """初始化通知管理器"""
        # 存储所有提醒的字典，格式：{note_id: (title, content, reminder_datetime, recurrence)}
        self.reminders = {}
        # 控制后台检查线程的标志
        self.running = True
        # 存储更新回调函数
        self.update_callback = None
        # 创建后台检查线程
        self.thread = threading.Thread(target=self._check_reminders, daemon=True)
        self.thread.start()
        print("通知管理器已启动")

    def set_update_callback(self, callback):
        """设置更新回调函数"""
        self.update_callback = callback

    def add_reminder(self, note_id, title, content, reminder_time, recurrence="none"):
        """增强版添加提醒方法"""
        try:
            # 支持多种时间格式
            try:
                reminder_datetime = datetime.strptime(reminder_time, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                reminder_datetime = datetime.strptime(reminder_time, '%Y-%m-%d %H:%M')
            
            self.reminders[note_id] = (title, content, reminder_datetime, recurrence)
            print(f"[SUCCESS] 提醒设置成功 | ID: {note_id} | 时间: {reminder_time} | 类型: {recurrence}")
            
        except Exception as e:
            print(f"[ERROR] 添加提醒失败: {str(e)}")
            messagebox.showerror("错误", f"提醒设置失败: {str(e)}")

    def remove_reminder(self, note_id):
        """
        移除指定的提醒
        
        Args:
            note_id: 要移除的提醒的记事ID
        """
        if note_id in self.reminders:
            print(f"移除提醒: {self.reminders[note_id][0]}")
            del self.reminders[note_id]

    def _show_reminder(self, title, content, note_id):
        """
        显示提醒窗口
        
        Args:
            title: 提醒标题
            content: 提醒内容
            note_id: 记事ID
        """
        # 创建提醒窗口
        reminder_window = tk.Toplevel()
        reminder_window.title("记事提醒")
        reminder_window.geometry("500x400")
        reminder_window.minsize(400, 300)
        reminder_window.attributes('-topmost', True)  # 窗口置顶
        reminder_window.configure(bg='#f0f0f0')  # 设置背景色
        
        # 创建主框架
        main_frame = ttk.Frame(reminder_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题标签
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(title_frame, text=title, font=('微软雅黑', 12, 'bold'), 
                 foreground='#333333').pack(anchor=tk.CENTER)
        
        # 内容文本框
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        content_text = tk.Text(content_frame, height=10, width=40, font=('微软雅黑', 10),
                             wrap=tk.WORD, bg='#ffffff', relief='flat', padx=10, pady=10)
        content_text.pack(fill=tk.BOTH, expand=True)
        content_text.insert('1.0', content)
        content_text.config(state='disabled')
        
        # 延迟提醒框架
        delay_frame = ttk.Frame(main_frame)
        delay_frame.pack(fill=tk.X, pady=(15, 0))
        
        # 延迟时间输入
        ttk.Label(delay_frame, text="延迟提醒(分钟):", 
                 font=('微软雅黑', 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        delay_var = tk.StringVar(value="5")  # 默认5分钟
        delay_entry = ttk.Entry(delay_frame, textvariable=delay_var, width=10)
        delay_entry.pack(side=tk.LEFT)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        def delay_reminder():
            """延迟提醒按钮的回调函数"""
            try:
                # 获取延迟时间
                delay_minutes = int(delay_var.get())
                if delay_minutes <= 0:
                    messagebox.showerror("错误", "延迟时间必须大于0分钟！")
                    return
                
                # 获取当前时间作为基准
                current_time = datetime.now()
                new_time = current_time + timedelta(minutes=delay_minutes)
                formatted_time = new_time.strftime('%Y-%m-%d %H:%M:%S')
                
                # 获取当前的循环设置（如果存在）
                current_recurrence = "none"
                if note_id in self.reminders:
                    _, _, _, current_recurrence = self.reminders[note_id]
                
                # 更新提醒
                self.reminders[note_id] = (title, content, new_time, current_recurrence)
                
                # 如果有回调函数，通知更新
                if self.update_callback:
                    self.update_callback(note_id, formatted_time)
                
                # 关闭提醒窗口
                reminder_window.destroy()
                messagebox.showinfo("成功", f"提醒已延迟{delay_minutes}分钟")
                
            except ValueError:
                messagebox.showerror("错误", "请输入有效的延迟时间！")
            except Exception as e:
                messagebox.showerror("错误", f"设置延迟提醒时出错：{str(e)}")
        
        # 创建按钮
        ttk.Button(button_frame, text="延迟提醒", 
                  command=delay_reminder).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", 
                  command=reminder_window.destroy).pack(side=tk.LEFT, padx=5)
        
        # 播放提示音
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        
        # 闪烁任务栏
        win32gui.FlashWindow(reminder_window.winfo_id(), True)

    def _check_reminders(self):
        """检查提醒的后台线程"""
        print("开始检查提醒")
        while self.running:
            current_time = datetime.now()
            # 检查每个提醒
            for note_id, (title, content, reminder_time, recurrence) in list(self.reminders.items()):
                if isinstance(reminder_time, datetime) and current_time >= reminder_time:
                    # 直接弹出提醒窗口
                    self._show_reminder(title, content, note_id)
                    # 移除已触发的提醒
                    if note_id in self.reminders:
                        del self.reminders[note_id]
            time.sleep(1)  # 每秒检查一次

    def add_one_month(self, dt):
        """辅助函数：为指定日期加一个月"""
        year = dt.year
        month = dt.month
        day = dt.day
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        max_day = calendar.monthrange(year, month)[1]
        day = min(day, max_day)
        return dt.replace(year=year, month=month, day=day)

    def cleanup(self):
        """清理资源，停止后台线程"""
        print("正在清理通知管理器...")
        self.running = False
        if self.thread and self.thread.is_alive():
            try:
                self.thread.join(timeout=1.0)  # 等待最多1秒
                print("通知管理器已清理完成")
            except:
                print("清理通知管理器时出错")

    def add_reminder_with_time(self, note_id, title, content, reminder_time):
        """
        添加新的提醒
        
        Args:
            note_id: 记事的唯一标识
            title: 提醒标题
            content: 提醒内容
            reminder_time: 提醒时间，格式：'%Y-%m-%d %H:%M:%S'
        """
        try:
            # 尝试解析不同格式的时间
            try:
                # 首先尝试带秒的格式
                reminder_datetime = datetime.strptime(reminder_time, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # 如果失败，尝试不带秒的格式，并设置秒为0
                reminder_datetime = datetime.strptime(reminder_time, '%Y-%m-%d %H:%M')
            
            self.reminders[note_id] = (title, content, reminder_datetime)
            print(f"成功添加提醒: {title} 将在 {reminder_datetime.strftime('%Y-%m-%d %H:%M:%S')} 提醒")
            print(f"当前所有提醒: {self.reminders}")
        except Exception as e:
            print(f"添加提醒时出错: {e}")
