"""
PyDetex
https://github.com/ppizarror/PyDetex

PIPELINES
Defines the pipelines which apply parsers.
"""

__all__ = [
    'simple',
    'strict',
    'strict_eqn',
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
    replace_single_chars_eqn: bool = True,
    **kwargs
) -> str:
    """
    The most simple pipeline ever.

    :param s: String latex
    :param lang: Language tag of the code
    :param show_progress: Show progress bar
    :param replace_pydetex_tags: Replace pydetex tags like symbols, cites
    :param remove_common_tags: Call ``remove_common_tags`` parser
    :param replace_single_chars_eqn: Replaces all single char equations
    :return: String with no latex!
    """
    if len(s) == 0:
        return s
    steps = 17
    if not replace_pydetex_tags:
        steps -= 1
    if not replace_single_chars_eqn:
        steps -= 1
    pb = kwargs.get('progressbar', ProgressBar(steps)) if show_progress else None
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
    s = par.process_items(s, lang, pb=pb)
    if replace_single_chars_eqn:
        s = par.process_chars_equations(s, lang, single_only=True, pb=pb)
    s = par.unicode_chars_equations(s, pb=pb)
    s = par.remove_comments(s, pb=pb)  # comments, replace tags, strip
    if replace_pydetex_tags:
        s = par.replace_pydetex_tags(s, pb=pb, **kwargs)
    s = par.strip_punctuation(s, pb=pb)
    s = par.simple_replace(s, pb=pb)
    if s[-1] == '\\':
        s = s[0:len(s) - 1]
    return s


def strict(
    s: str,
    lang: str = 'en',
    show_progress: bool = False,
    eqn_simple: bool = True,
    **kwargs
) -> str:
    """
    Apply simple + removes all commands.

    :param s: String latex
    :param lang: Language tag of the code
    :param show_progress: Show progress bar
    :param eqn_simple: If true, replace equations with a label, else, attempt to write it as-is
    :return: String with no latex!
    """
    pb = ProgressBar(steps=24) if show_progress else None
    if 'progressbar' not in kwargs.keys():
        # noinspection PyTypeChecker
        kwargs['progressbar'] = pb
    s = simple(s, lang, replace_pydetex_tags=False, remove_common_tags=False,
               show_progress=show_progress, replace_single_chars_eqn=False, **kwargs)  # 15 steps
    s = par.process_chars_equations(s, lang, single_only=not eqn_simple, pb=pb)
    s = par.remove_equations(s, pb=pb)
    s = par.remove_environments(s, pb=pb)
    s = par.remove_commands_param(s, lang, pb=pb)
    s = par.remove_commands_param_noargv(s, pb=pb)
    s = par.remove_comments(s, pb=pb)
    s = par.replace_pydetex_tags(s, pb=pb, **kwargs)
    s = par.strip_punctuation(s, pb=pb)
    s = par.simple_replace(s, pb=pb)
    return s


def strict_eqn(
    s: str,
    lang: str = 'en',
    show_progress: bool = False,
    **kwargs
) -> str:
    """
    Same as strict, but replaces the equations with their string representation.

    :param s: String latex
    :param lang: Language tag of the code
    :param show_progress: Show progress bar
    :return: String with no latex!
    """
    return strict(s, lang, show_progress, eqn_simple=False, **kwargs)
