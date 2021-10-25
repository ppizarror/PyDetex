"""
PyDetex
https://github.com/ppizarror/PyDetex

PIPELINES
Defines the pipelines which apply parsers.
"""

__all__ = [
    'simple',
    'strict',
    'PipelineType'
]

import pydetex.parsers as par
from typing import Callable

PipelineType = Callable[[str, str], str]


def simple(s: str, lang: str = 'en') -> str:
    """
    The most simple pipeline ever.

    :param s: String latex
    :param lang: Language tag of the code
    :return: String with no latex!
    """
    if len(s) == 0:
        return s
    s = '\n'.join(s.splitlines())
    s = par.remove_comments(s)
    s = par.simple_replace(s)
    s = par.remove_common_tags(s)
    s = par.process_cite(s)
    s = par.process_ref(s)
    s = par.process_labels(s)
    s = par.remove_comments(s)
    s = par.process_quotes(s)
    s = par.process_inputs(s)
    s = par.process_chars_equations(s, lang, True)
    if len(s) > 0 and s[-1] == '\\':
        s = s[0:len(s) - 1]
    return s


def strict(s: str, lang: str = 'en') -> str:
    """
    Applies simple + removes all commands.

    :param s: String latex
    :param lang: Language tag of the code
    :return: String with no latex!
    """
    s = simple(s, lang)
    s = par.process_chars_equations(s, lang, False)
    s = par.remove_commands_char(s, '$')
    s = par.remove_commands_param(s, lang)
    s = par.remove_commands_param_noargv(s)
    s = par.remove_comments(s)
    return s
