# -*- mode: python ; coding: utf-8 -*-

import os
import sys; sys.path.insert(0, '.')
import specs
if specs.is_win: exit()

try:
    os.system(f'rm -rf dist/PyDetex_OSX.app')
except:
    pass

# Create the analysis
a = specs.get_analysis(Analysis, TOC)
pyz = specs.get_pyz(PYZ, a)
exe = specs.get_exe(EXE, pyz, a, True)
app = specs.get_bundle(BUNDLE, exe)

# Save to zip
specs.save_zip('PyDetex_macOS.app', 'PyDetex.macOS')