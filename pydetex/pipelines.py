"""
PyDetex
https://github.com/ppizarror/pydetex

PIPELINES
Defines the pipelines which apply parsers.
"""

__all__ = ['simple_pipeline']

import pydetex.parsers as par


def simple_pipeline(s: str) -> str:
    """
    The most simple pipeline ever.

    :param s: String latex
    :return: String with no latex!
    """
    s = par.simple_replace(s)
    for tag in ['textbf', 'textit', 'texttt', 'doublequotes', 'section',
                'subsection', 'chapter', 'subsubsection', 'subsubsubsection']:
        s = par.remove_tag(s, tag)
    s = par.process_cite(s)
    s = par.process_ref(s)
    s = par.remove_comments(s)
    return s
