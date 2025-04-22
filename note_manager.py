"""
记事管理模块
负责记事的存储、读取、更新和删除操作。
使用JSON文件作为持久化存储，支持记事的CRUD操作。
"""

import os
import json
from datetime import datetime
import uuid
import sys

class NoteManager:
    """记事管理器类，处理记事的存储和检索"""
    
    def __init__(self):
        """
        初始化记事管理器
        创建存储目录和文件（如果不存在）
        """
        # 获取程序运行路径
        if getattr(sys, 'frozen', False):
            # 如果是打包后的程序
            application_path = os.path.dirname(sys.executable)
        else:
            # 如果是开发环境
            application_path = os.path.dirname(os.path.abspath(__file__))
            
        # 确保数据目录存在
        self.data_dir = os.path.join(application_path, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 设置记事文件路径
        self.notes_file = os.path.join(self.data_dir, 'notes.json')
        
        # 如果文件不存在，创建空的记事数据
        if not os.path.exists(self.notes_file):
            self.save_notes({})
        
        # 加载记事数据
        self.notes = self.load_notes()

    def load_notes(self):
        """
        从文件加载记事数据
        
        Returns:
            dict: 记事数据字典，格式为 {note_id: note_data}
        """
        try:
            with open(self.notes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载记事时出错: {e}")
            return {}

    def save_notes(self, notes):
        """
        将记事数据保存到文件
        
        Args:
            notes (dict): 要保存的记事数据字典
        """
        try:
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                json.dump(notes, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存记事时出错: {e}")

    def add_note(self, title, content, date, reminder_time=""):
        """更健壮的添加记事方法"""
        try:
            # 验证日期格式
            datetime.strptime(date, "%Y-%m-%d")
            if reminder_time:
                datetime.strptime(reminder_time, "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            raise ValueError(f"无效的时间格式: {str(e)}")

        note_id = str(uuid.uuid4())
        note_data = {
            'title': title,
            'content': content,
            'date': date,
            'reminder_time': reminder_time,
            'created_at': datetime.now().isoformat(),
            'recurrence': 'none'  # 默认不循环
        }
        self.notes[note_id] = note_data
        self.save_notes(self.notes)
        print(f"[DEBUG] 新增记事成功 ID: {note_id}")
        return note_id

    def update_note(self, note_id, title, content, date, reminder_time):
        """
        更新现有记事
        
        Args:
            note_id (str): 记事ID
            title (str): 新标题
            content (str): 新内容
            date (str): 新日期，格式：'%Y-%m-%d'
            reminder_time (str): 新提醒时间，格式：'%Y-%m-%d %H:%M:%S'
        """
        if note_id in self.notes:
            self.notes[note_id].update({
                'title': title,
                'content': content,
                'date': date,
                'reminder_time': reminder_time
            })
            self.save_notes(self.notes)

    def delete_note(self, note_id):
        """
        删除指定记事
        
        Args:
            note_id (str): 要删除的记事ID
        """
        if note_id in self.notes:
            del self.notes[note_id]
            self.save_notes(self.notes)

    def get_note(self, note_id):
        """
        获取指定记事的数据
        
        Args:
            note_id (str): 记事ID
            
        Returns:
            dict: 记事数据，如果不存在返回None
        """
        return self.notes.get(note_id)

    def get_all_notes(self):
        """
        获取所有记事
        
        Returns:
            dict: 所有记事的数据字典
        """
        return self.notes

    def get_notes_by_date(self, date):
        """
        按日期获取记事
        
        Args:
            date (str): 日期，格式：'%Y-%m-%d'
        
        Returns:
            dict: 按日期筛选的记事数据字典
        """
        return {
            note_id: note for note_id, note in self.notes.items()
            if note.get('date') == date
        }
