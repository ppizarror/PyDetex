"""
PyDetex
https://github.com/ppizarror/PyDetex

PYDETEX HOOK
Used by Pyinstaller.
"""

import os

# noinspection PyProtectedMember
from pydetex import __file__ as pydetex_main_file

# Get pydetex's folder
pydetex_folder = os.path.dirname(os.path.abspath(pydetex_main_file))

# datas is the variable that pyinstaller looks for while processing hooks
datas = []


# A helper to append the relative path of a resource to hook variable - datas
def _append_to_datas(file_path: str, target_folder: str, base_target_folder: str = 'pydetex',
                     relative: bool = True) -> None:
    """
    Add path to datas.

    :param file_path: File path
    :param target_folder: Folder to paste the resources. If empty uses the containing folder of the file as ``base_target_folder+target_folder``
    :param base_target_folder: Base folder of the resource
    :param relative: If ``True`` append ``pygame_menu_folder``
    :return: None
    """
    global datas
    if relative:
        res_path = os.path.join(pydetex_folder, file_path)
    else:
        res_path = file_path
    if target_folder == '':
        target_folder = os.path.basename(os.path.dirname(res_path))
    if os.path.exists(res_path):
        datas.append((res_path, os.path.join(base_target_folder, target_folder)))


# Append resources
res_files = [
    'res/cog.ico',
    'res/dictionary.ico',
    'res/icon.gif',
    'res/icon.ico',
    'res/stopwords.json'
]

for f in res_files:
    _append_to_datas(f, target_folder='')
