# 开发者指南

## 项目结构

```
my-note/
├── data/                  # 数据存储目录
│   └── notes.json        # 记事数据文件
├── docs/                 # 文档目录
├── main.py              # 主程序入口
├── note_manager.py      # 记事管理模块
├── notification_manager.py # 提醒管理模块
├── setup.py             # 安装配置文件
├── requirements.txt     # 依赖列表
├── README.md           # 项目说明
└── LICENSE             # 许可证文件
```

## 核心模块

### 1. main.py
- 主程序入口
- GUI 界面实现
- 事件处理
- 用户交互逻辑

### 2. note_manager.py
- 记事数据管理
- JSON 文件操作
- 数据结构：
```python
{
    "note_id": {
        "title": "记事标题",
        "content": "记事内容",
        "date": "2025-01-22",
        "reminder_time": "2025-01-22 15:30:00",
        "created_at": "2025-01-22T15:30:00.000000"
    }
}
```

### 3. notification_manager.py
- 提醒功能实现
- 后台线程管理
- Windows 通知集成

## 开发环境设置

1. 克隆仓库：
```bash
git clone [repository-url]
cd my-note
```

2. 创建虚拟环境：
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. 安装开发依赖：
```bash
pip install -r requirements.txt
pip install -e .
```

## 开发指南

### 1. 代码风格
- 遵循 PEP 8 规范
- 使用类型注解
- 添加详细的文档字符串

### 2. 提交规范
- 使用清晰的提交信息
- 每个提交解决一个问题
- 保持提交粒度适中

### 3. 测试
- 添加单元测试
- 进行集成测试
- 测试覆盖率要求：>80%

## 构建和发布

### 1. 构建包
```bash
python setup.py sdist bdist_wheel
```

### 2. 测试安装
```bash
pip install dist/my_note-1.0.0-py3-none-any.whl
```

### 3. 发布到 PyPI
```bash
python -m twine upload dist/*
```

## 常见开发问题

### 1. GUI 更新
- 使用 after() 方法处理定时任务
- 避免在主线程中进行耗时操作
- 使用 queue 进行线程间通信

### 2. 数据持久化
- 定期保存数据
- 实现数据备份机制
- 处理并发访问

### 3. 系统集成
- 处理 Windows 特定的 API
- 管理系统托盘图标
- 实现全局快捷键
