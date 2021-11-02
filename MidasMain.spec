# -*- mode: python ; coding: utf-8 -*-

#command: pyinstaller -F MidasMain.spec
#to reduce file size: pyinstaller -F -w --exclude pandas, --exclude numpy MidasMain.spec
#icon: pyinstaller -F --onefile --icon=./gui/icons/Main.ico MidasMain.spec

block_cipher = None


a = Analysis(['MidasMain.py'],
             pathex=['E:\\Dropbox\\Programming\\Midas'],
             binaries=[],
             datas=[('./gui/*.ui','./gui'),
             ('./gui/icons/*.png','./gui/icons')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Midas',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
