# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['night_writer_simple.py'],
    pathex=[],
    binaries=[],
    datas=[('tasks.txt', '.')],
    hiddenimports=['win32gui', 'win32con', 'win32api', 'win32process', 'win32clipboard', 'pygetwindow', 'pyautogui', 'PIL.Image', 'PIL.ImageGrab', 'psutil'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['cv2', 'opencv-python', 'numpy', 'scipy', 'matplotlib', 'pandas', 'torch', 'tensorflow', 'easyocr', 'keras', 'sklearn', 'skimage', 'IPython', 'jupyter', 'notebook', 'sphinx'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Night Writer Optimized v2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
