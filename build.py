"""
PyDetex
https://github.com/ppizarror/PyDetex

BUILD.
"""

import os
import struct
import sys

assert len(sys.argv) == 2, 'Argument is required, usage: build.py pyinstaller/pip/twine/gource'
mode = sys.argv[1].strip()
python = 'python3' if not sys.platform == 'win32' else 'py -3'
sys_arch = struct.calcsize('P') * 8

if mode == 'pyinstaller':
    # Check upx
    upx = ''
    if sys.platform == 'win32' and sys_arch == 64:
        upx = '--upx-dir build/upx_64'
    pyinstaller = f'{python} -m PyInstaller' if sys.platform == 'win32' else 'pyinstaller'

    # os.system(f'{pyinstaller} specs/PyDetex_Win.spec --noconfirm {upx}')
    os.system(f'{pyinstaller} specs/PyDetex_Win_Single.spec --noconfirm {upx}')
    os.system(f'{pyinstaller} specs/PyDetex_macOS.spec --noconfirm')

elif mode == 'pip':
    if os.path.isdir('dist/pip'):
        for k in os.listdir('dist'):
            if '.egg' in k:
                os.remove(f'dist/{k}')
    if os.path.isdir('dist/pip'):
        for k in os.listdir('dist/pip'):
            if 'pydetex-' in k:
                os.remove(f'dist/pip/{k}')
    if os.path.isdir('build'):
        for k in os.listdir('build'):
            if 'bdist.' in k or k == 'lib':
                os.system(f'rm -rf build/{k}')
    os.system(f'{python} setup.py sdist --dist-dir dist/pip bdist_wheel --dist-dir dist/pip')

elif mode == 'twine':
    if os.path.isdir('dist/pip'):
        os.system(f'{python} -m twine upload dist/pip/*')
    else:
        raise FileNotFoundError('Not distribution been found, execute build.py pip')

elif mode == 'gource':
    os.system('gource -s 0.25 --title PyDetex --disable-auto-rotate --key '
              '--highlight-users --disable-bloom --multi-sampling -w --transparent --path ./')

else:
    raise ValueError(f'Unknown mode {mode}')
