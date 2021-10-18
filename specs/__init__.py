"""
PyDetex
https://github.com/ppizarror/PyDetex

SPECS
Defines spec constructor.
"""

__all__ = [
    'block_cipher',
    'get_analysis',
    'get_collect',
    'get_exe',
    'get_pyz'
]

import os

# Configure
app_name = 'PyDetex'
app_icon = '../pydetex/res/icon.ico'
block_cipher = None

excluded_binaries = []
excluded_modules = [
    'IPython',
    'matplotlib',
    'notebook',
    'numpy',
    'PIL',
    'PyQt5',
    'scipy'
]


def _file_sz(f: str) -> str:
    """
    Computes the file size in KB.
    """
    sz = round(os.path.getsize(f) / 1024, 1)
    return f'{sz} KB'


def _path(p: str, sz: int = 60) -> str:
    """
    Returns a parsed path.
    """
    p = p.replace('\\', '/')
    if len(p) < sz:
        return p
    else:
        return '...' + p[len(p) - sz:len(p)]


def get_analysis(analysis, toc):
    """
    Return the ANALYSIS object.
    """
    # Make object
    a = analysis(
        ['../gui.py'],
        binaries=[],
        cipher=block_cipher,
        datas=[],
        excludes=excluded_modules,
        hiddenimports=['pydetex'],
        hooksconfig={},
        hookspath=[],
        noarchive=False,
        pathex=['../'],
        runtime_hooks=[],
        win_no_prefer_redirects=False,
        win_private_assemblies=False
    )

    # Update its propeties
    print('Updating binaries')
    new_binaries = []
    for i in a.binaries:
        if 'miktex\\bin' in i[1] or i[0] in excluded_binaries:
            print(f'\tRemoved:\t{_path(i[1])} ({_file_sz(i[1])})')
            continue
        new_binaries.append(i)
    print('Program binaries')
    a.binaries = toc(new_binaries)
    for j in a.binaries:
        print(f'\t{j[0]}\n\t\t{_path(j[1])} ({_file_sz(j[1])} KB)')

    # Scripts
    print('Program scripts')
    for j in a.scripts:
        print(f'\t{j[0]}\t{_path(j[1])}')

    # Return the analysis
    return a


def get_collect(collect, a, exe):
    """
    Return the COLLECT object.
    """
    return collect(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        name=app_name,
        upx_exclude=[],
        upx=True
    )


def get_exe(exe, pyz, a, single: bool):
    """
    Return the EXE object.
    """
    if single:
        return exe(
            pyz,
            a.scripts,
            a.binaries,
            a.zipfiles,
            a.datas,
            [],
            bootloader_ignore_signals=False,
            codesign_identity=None,
            console=False,
            debug=False,
            disable_windowed_traceback=False,
            entitlements_file=None,
            icon=app_icon,
            name=app_name,
            runtime_tmpdir=None,
            strip=False,
            target_arch=None,
            upx_exclude=[],
            upx=True
        )
    else:
        return exe(
            pyz,
            a.scripts,
            [],
            bootloader_ignore_signals=False,
            codesign_identity=None,
            console=True,
            debug=False,
            disable_windowed_traceback=False,
            entitlements_file=None,
            exclude_binaries=True,
            icon=app_icon,
            name=app_name,
            strip=False,
            target_arch=None,
            upx=True
        )


def get_pyz(pyz, a):
    """
    Return the PYZ object.
    """
    return pyz(a.pure, a.zipped_data, cipher=block_cipher)
