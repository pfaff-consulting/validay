from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import ansible, ansible_runner

# Złap cały katalog ansible i ansible_collections
ansible_data = collect_data_files('ansible', include_py_files=True)
ansible_collections_data = collect_data_files('ansible_collections', include_py_files=True)
ansible_runner_data = collect_data_files('ansible_runner', include_py_files=True)

# Złap podmoduły (żeby nie zabrakło importów)
hiddenimports = (
    collect_submodules('ansible') +
    collect_submodules('ansible_runner')
)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=ansible_data + ansible_collections_data + ansible_runner_data,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='validay',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)