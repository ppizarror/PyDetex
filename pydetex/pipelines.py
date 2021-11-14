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


def simple(
        s: str,
        lang: str = 'en',
        replace_pydetex_tags: bool = True,
        remove_common_tags: bool = True
) -> str:
    """
    The most simple pipeline ever.

    :param s: String latex
    :param lang: Language tag of the code
    :param replace_pydetex_tags: Replace cite tags
    :param remove_common_tags: Call ``remove_common_tags`` parser
    :return: String with no latex!
    """
    if len(s) == 0:
        return s
    s = '\n'.join(s.splitlines())  # Removes \r\n
    s = par.process_inputs(s)
    s = par.remove_comments(s)
    s = par.process_begin_document(s)
    s = par.simple_replace(s)
    if remove_common_tags:
        s = par.remove_common_tags(s)
    s = par.process_cite(s)
    s = par.process_ref(s)
    s = par.process_labels(s)
    s = par.process_items(s)
    s = par.process_quotes(s)
    s = par.process_chars_equations(s, lang, True)
    s = par.unicode_chars_equations(s)
    if len(s) > 0 and s[-1] == '\\':
        s = s[0:len(s) - 1]
    s = par.remove_comments(s)  # comments, replace tags, strip
    if replace_pydetex_tags:
        s = par.replace_pydetex_tags(s)
    s = par.strip_punctuation(s)
    return s


def strict(s: str, lang: str = 'en') -> str:
    """
    Applies simple + removes all commands.

    :param s: String latex
    :param lang: Language tag of the code
    :return: String with no latex!
    """
    s = simple(s, lang, replace_pydetex_tags=False, remove_common_tags=False)
    s = par.process_chars_equations(s, lang, False)
    s = par.remove_equations(s)
    s = par.process_def(s)
    s = par.remove_environments(s)
    s = par.remove_commands_param(s, lang)
    s = par.remove_commands_param_noargv(s)
    s = par.remove_comments(s)
    s = par.replace_pydetex_tags(s)
    s = par.strip_punctuation(s)
    return s
