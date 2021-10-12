"""
PyDetex
https://github.com/ppizarror/pydetex

PIPELINES
Defines the pipelines which apply parsers.
"""

__all__ = [
    'simple_pipeline',
    'PipelineType'
]

import pydetex.parsers as par
from typing import Callable

PipelineType = Callable[[str], str]


def simple_pipeline(s: str) -> str:
    """
    The most simple pipeline ever.

    :param s: String latex
    :return: String with no latex!
    """
    s = par.simple_replace(s)
    s = par.remove_common_tags(s)
    s = par.process_cite(s)
    s = par.process_ref(s)
    s = par.process_labels(s)
    s = par.remove_comments(s)
    s = par.process_quotes(s)
    s = par.process_inputs(s)
    return s
