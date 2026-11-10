# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules


hiddenimports = collect_submodules("PIL")
hiddenimports += ["tkinter", "turtle", "colorgram"]


a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name="ArtMakerStudio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    exclude_binaries=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ArtMakerStudio",
)

app = BUNDLE(
    coll,
    name="ArtMakerStudio.app",
    icon=None,
    bundle_identifier="com.artmaker.studio",
    info_plist={
        "CFBundleDisplayName": "Art Maker Studio",
        "CFBundleShortVersionString": "1.1.0",
        "NSHighResolutionCapable": True,
    },
)
