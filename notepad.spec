# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data', 'data'),  # 包含数据目录
        ('requirements.txt', '.'),  # 包含依赖文件
        ('README.md', '.'),  # 包含说明文件
    ],
    hiddenimports=[
        'pystray._win32', 
        'PIL._tkinter_finder',
        'PIL.Image', 
        'PIL.ImageDraw',
        'tkcalendar', 
        'win32api',
        'win32gui', 
        'win32con', 
        'win32process',
        'winsound',
        'babel.numbers',
        'tkinter',
        'tkinter.ttk',
        'json',
        'datetime',
        'uuid',
        'os',
        'threading',
        'dateutil.relativedelta'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MyNotepad',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 临时设置为 True 以便查看错误信息
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # 如果有图标文件的话
)

# 使用目录集合模式打包
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='我的记事本',
) 