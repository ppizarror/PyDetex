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

PipelineType = Callable


def simple(
        s: str,
        lang: str = 'en',
        show_progress: bool = False,
        replace_pydetex_tags: bool = True,
        remove_common_tags: bool = True,
        **kwargs
) -> str:
    """
    The most simple pipeline ever.

    :param s: String latex
    :param lang: Language tag of the code
    :param show_progress: Show progress bar
    :param replace_pydetex_tags: Replace pydetex tags like symbols, cites
    :param remove_common_tags: Call ``remove_common_tags`` parser
    :return: String with no latex!
    """
    if len(s) == 0:
        return s
    pb = kwargs.get('progressbar', ProgressBar(steps=17 if replace_pydetex_tags else 16)) if show_progress else None
    s = '\n'.join(s.splitlines())  # Removes \r\n
    s = par.process_inputs(s, pb=pb)
    s = par.remove_comments(s, pb=pb)
    s = par.process_begin_document(s, pb=pb)
    s = par.simple_replace(s, pb=pb)
    s = par.process_def(s, pb=pb, replace=kwargs.get('replace_defs', False))
    if remove_common_tags:
        s = par.remove_common_tags(s, pb=pb)
    s = par.process_cite(s, pb=pb, compress_cite=kwargs.get('compress_cite', True))
    s = par.process_citeauthor(s, lang, pb=pb)
    s = par.process_ref(s, pb=pb)
    s = par.process_labels(s, pb=pb)
    s = par.process_items(s, pb=pb)
    s = par.process_quotes(s, pb=pb)
    s = par.process_chars_equations(s, lang, True, pb=pb)
    s = par.unicode_chars_equations(s, pb=pb)
    s = par.remove_comments(s, pb=pb)  # comments, replace tags, strip
    if replace_pydetex_tags:
        s = par.replace_pydetex_tags(s, pb=pb, **kwargs)
    s = par.strip_punctuation(s, pb=pb)
    if s[-1] == '\\':
        s = s[0:len(s) - 1]
    return s


def strict(
        s: str,
        lang: str = 'en',
        show_progress: bool = False,
        **kwargs
) -> str:
    """
    Apply simple + removes all commands.

    :param s: String latex
    :param lang: Language tag of the code
    :param show_progress: Show progress bar
    :return: String with no latex!
    """
    pb = ProgressBar(steps=22) if show_progress else None
    if 'progressbar' not in kwargs.keys():
        # noinspection PyTypeChecker
        kwargs['progressbar'] = pb
    s = simple(s, lang, replace_pydetex_tags=False, remove_common_tags=False,
               show_progress=show_progress, **kwargs)
    s = par.process_chars_equations(s, lang, False, pb=pb)
    s = par.remove_equations(s, pb=pb)
    s = par.remove_environments(s, pb=pb)
    s = par.remove_commands_param(s, lang, pb=pb)
    s = par.remove_commands_param_noargv(s, pb=pb)
    s = par.remove_comments(s, pb=pb)
    s = par.replace_pydetex_tags(s, pb=pb, **kwargs)
    s = par.strip_punctuation(s, pb=pb)
    return s
