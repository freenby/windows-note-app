# 安装指南

## 系统要求

- Windows 7 或更高版本
- Python 3.6 或更高版本
- 约 50MB 磁盘空间

## 安装方法

### 1. 使用 pip 安装（推荐）

```bash
pip install my-note
```

### 2. 从源码安装

1. 克隆仓库：
```bash
git clone [repository-url]
cd my-note
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 安装应用：
```bash
pip install -e .
```

## 验证安装

安装完成后，可以通过以下方式验证安装：

1. 命令行运行：
```bash
my-note
```

2. 或直接运行 Python 模块：
```bash
python -m my_note
```

## 常见问题

### 1. 依赖安装失败

如果遇到依赖安装失败，可以尝试：

1. 更新 pip：
```bash
python -m pip install --upgrade pip
```

2. 单独安装依赖：
```bash
pip install pywin32==306
pip install pillow==10.0.0
pip install keyboard==0.13.5
pip install tkcalendar==1.6.1
pip install pystray==0.19.5
```

### 2. 运行时找不到模块

确保 Python 环境变量设置正确，可以通过以下命令检查 Python 和 pip 的位置：

```bash
where python
where pip
```
