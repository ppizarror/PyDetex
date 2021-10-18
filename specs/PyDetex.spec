# -*- mode: python ; coding: utf-8 -*-

import sys; sys.path.insert(0, '.')
import specs

# Create the analysis
a = specs.get_analysis(Analysis, TOC)
pyz = specs.get_pyz(PYZ, a)
exe = specs.get_exe(EXE, pyz, a, False)
coll = specs.get_collect(COLLECT, a, exe)