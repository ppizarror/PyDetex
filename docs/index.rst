
:orphan:

.. This page is orphan because its content concerns the internal working of the
.. library. However it is necessary in order to be able to quote its items in the
.. documentation.

.. include:: ../README.rst


===
API
===

Although PyDetex is intended to be used through its GUI, the module contains several
practical methods to detect LaTex commands, environments, equations, among others.
The GUI only uses the pipelines to transform the tex code to plain text. On the
other hand, the pipelines use parsers.

You can check for the parsers, pipelines, and util’s methods to create your
pipelines in the left menu!

.. toctree::
    :maxdepth: 2
    :hidden:
    :caption: API

    _source/parsers
    _source/pipelines
    _source/utils


=================
About PyDetex
=================

This project does not have a mailing list and so the issues tab should be the first
point of contact if wishing to discuss the project. If you have questions that you
do not feel are relevant to the issues tab or just want to let me know what you
think about the software, feel free to email me at pablo@ppizarror.com

.. toctree::
    :maxdepth: 2
    :hidden:
    :caption: About PyDetex

    _source/license
    _source/contributors


==================
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
