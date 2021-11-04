=======
PyDetex
=======

.. image:: https://img.shields.io/badge/author-Pablo%20Pizarro%20R.-lightgray.svg
    :target: https://ppizarror.com?lang=en
    :alt: @ppizarror

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://opensource.org/licenses/MIT
    :alt: License MIT

.. image:: https://img.shields.io/badge/python-3.6+-red.svg
    :target: https://www.python.org/downloads
    :alt: Python 3.6+

.. image:: https://badge.fury.io/py/pydetex.svg
    :target: https://pypi.org/project/pydetex
    :alt: PyPi package

.. image:: https://github.com/ppizarror/PyDetex/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/ppizarror/PyDetex/actions/workflows/tests.yml
    :alt: Build status

.. image:: https://img.shields.io/lgtm/alerts/g/ppizarror/PyDetex.svg?logo=lgtm&logoWidth=18
    :target: https://lgtm.com/projects/g/ppizarror/PyDetex/alerts
    :alt: Total alerts

.. image:: https://img.shields.io/lgtm/grade/python/g/ppizarror/PyDetex.svg?logo=lgtm&logoWidth=18
    :target: https://lgtm.com/projects/g/ppizarror/PyDetex/context:python
    :alt: Language grade: Python

.. image:: https://codecov.io/gh/ppizarror/PyDetex/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/ppizarror/PyDetex
    :alt: Codecov

.. image:: https://img.shields.io/github/issues/ppizarror/PyDetex
    :target: https://github.com/ppizarror/PyDetex/issues
    :alt: Open issues

.. image:: https://img.shields.io/pypi/dm/pydetex?color=purple
    :target: https://pypi.org/project/pydetex
    :alt: PyPi downloads

.. image:: https://static.pepy.tech/personalized-badge/pydetex?period=total&units=international_system&left_color=grey&right_color=lightgrey&left_text=total%20downloads
    :target: https://pepy.tech/project/pydetex
    :alt: Total downloads
    
.. image:: https://img.shields.io/badge/buy%20me%20a-Ko--fi-02b9fe
    :target: https://ko-fi.com/ppizarror
    :alt: Buy me a Ko-fi

Introduction
------------

PyDetex is a Python application that transforms LaTeX code to plain text. It has multiple
language support (15+), detects repeated words, offers a dictionary (synonyms, antonyms,
definitions), and many things more to come!

Comprehensive documentation for the latest version (if you plan to use the API)
is available at https://pydetex.readthedocs.io

Install Instructions
--------------------

PyDetex can be installed via pip, for both MacOS, Windows & Linux. Simply run:

.. code-block:: bash

    $> python3 pip install --upgrade pydetex

Also, there're compiled binaries for Windows (x64) and macOS available through GitHub releases.

Launch the GUI, or use the library
----------------------------------

Simply run this command anywhere to execute the application, or just import pydetex and play.

.. code-block:: bash

    $> python3 -m pydetex.gui

.. figure:: https://raw.githubusercontent.com/ppizarror/pydetex/master/docs/_static/example_simple.png
    :scale: 40%
    :align: center

    **(Simple Pipeline)** Tadada... !!! A simple GUI to process your LaTex, and paste into Grammarly? ＼(^o^)／

.. figure:: https://raw.githubusercontent.com/ppizarror/pydetex/master/docs/_static/example_strict.png
    :scale: 40%
    :align: center

    **(Strict Pipeline)** The strict pipeline removes all commands, or replaces by some known tags.

.. figure:: https://raw.githubusercontent.com/ppizarror/pydetex/master/docs/_static/pydetex_windows.png
    :scale: 40%
    :align: center

    Multiple options to configure: Check repeated words, highlight undetected code, or use different pipelines.

TO-DOs
------

Currently, many things must be improved:

- Learn \def and replace properly
- Support for environments, such as *figure*, *table*, etc..


Author
------

`Pablo Pizarro R. <https://ppizarror.com>`_ | 2021
