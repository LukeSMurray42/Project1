# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['hangman.py'],
             pathex=[],
             binaries=[],
             datas=[('words.txt', '.'), ('hangman.db', '.'), ('templates/index.html', 'templates'), ('templates/main.html', 'templates'), ('templates/multi.html', 'templates'), ('templates/play.html', 'templates'), ('templates/sp_dif.html', 'templates'), ('templates/sp_name.html', 'templates'), ('static/bootstrap.min.css', 'static'), ('static/bootstrap.min.js', 'static'), ('static/help.png', 'static'), ('static/jquery.min.js', 'static'), ('static/main.css', 'static'), ('static/main.js', 'static'), ('static/main.png', 'static'), ('static/Picture1.png', 'static'), ('static/purple.jpg', 'static'), ('static/singleplayer.png', 'static'), ('static/title.png', 'static'), ('static/music/Gameplay.mp3', 'static/music'), ('static/music/Homepage.mp3', 'static/music')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
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
          name='hangman',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
