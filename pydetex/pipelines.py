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
from pydetex.utils import ProgressBar
from typing import Callable

PipelineType = Callable[[str, str], str]


def simple(
        s: str,
        lang: str = 'en',
        replace_pydetex_tags: bool = True,
        remove_common_tags: bool = True,
        **kwargs
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
    pb = kwargs.get('progressbar', ProgressBar(steps=16))
    pb.update('Splitting lines')
    s = '\n'.join(s.splitlines())  # Removes \r\n
    s = par.process_inputs(s, pb=pb)
    s = par.remove_comments(s, pb=pb)
    s = par.process_begin_document(s, pb=pb)
    s = par.simple_replace(s, pb=pb)
    if remove_common_tags:
        s = par.remove_common_tags(s, pb=pb)
    s = par.process_cite(s, pb=pb)
    s = par.process_ref(s, pb=pb)
    s = par.process_labels(s, pb=pb)
    s = par.process_items(s, pb=pb)
    s = par.process_quotes(s, pb=pb)
    s = par.process_chars_equations(s, lang, True, pb=pb)
    s = par.unicode_chars_equations(s, pb=pb)
    s = par.remove_comments(s, pb=pb)  # comments, replace tags, strip
    if replace_pydetex_tags:
        s = par.replace_pydetex_tags(s, pb=pb)
    s = par.strip_punctuation(s, pb=pb)
    if s[-1] == '\\':
        s = s[0:len(s) - 1]
    return s


def strict(s: str, lang: str = 'en') -> str:
    """
    Apply simple + removes all commands.

    :param s: String latex
    :param lang: Language tag of the code
    :return: String with no latex!
    """
    pb = ProgressBar(steps=22)
    s = simple(s, lang, replace_pydetex_tags=False, remove_common_tags=False, progressbar=pb)
    s = par.process_chars_equations(s, lang, False, pb=pb)
    s = par.remove_equations(s, pb=pb)
    s = par.process_def(s, pb=pb)
    s = par.remove_environments(s, pb=pb)
    s = par.remove_commands_param(s, lang, pb=pb)
    s = par.remove_commands_param_noargv(s, pb=pb)
    s = par.remove_comments(s, pb=pb)
    s = par.replace_pydetex_tags(s, pb=pb)
    s = par.strip_punctuation(s, pb=pb)
    return s
