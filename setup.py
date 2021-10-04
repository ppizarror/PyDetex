"""
PyDetex
https://github.com/ppizarror/pydetex

SETUP DISTRIBUTION
Create setup for PyPI
"""

from setuptools import setup, find_packages
import pydetex

# Load readme
with open('README.rst') as f:
    long_description = f.read()

# Load requirements
with open('requirements.txt') as f:
    requirements = []
    for line in f:
        requirements.append(line.strip())

requirements_docs = requirements.copy()
requirements_docs.extend([
    'sphinx',
    'sphinx-autodoc-typehints>=1.2.0',
    'sphinx-rtd-theme'
])

requirements_tests = requirements.copy()
requirements_tests.extend([
    'codecov',
    # 'pyautogui'
])

# Setup library
setup(
    name=pydetex.__module_name__,
    version=pydetex.__version__,
    author=pydetex.__author__,
    author_email=pydetex.__email__,
    description=pydetex.__description__,
    long_description=long_description,
    url=pydetex.__url__,
    project_urls={
        'Bug Tracker': pydetex.__url_bug_tracker__,
        'Documentation': pydetex.__url_documentation__,
        'Source Code': pydetex.__url_source_code__
    },
    license=pydetex.__license__,
    platforms=['any'],
    keywords=pydetex.__keywords__,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python',
        'Topic :: Multimedia',
        'Topic :: Text Processing'
    ],
    include_package_data=True,
    packages=find_packages(exclude=['test']),
    python_requires='>=3.6, <4',
    install_requires=requirements,
    extras_require={
        'docs': requirements_docs,
        'test': requirements_tests
    },
    setup_requires=[
        'setuptools',
    ],
    options={
        'bdist_wheel': {'universal': False}
    },
    # entry_points={
    #     'pyinstaller40': ['hook-dirs = pydetex.__pyinstaller:get_hook_dirs']
    # }
)
