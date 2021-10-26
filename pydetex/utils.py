"""
PyDetex
https://github.com/ppizarror/PyDetex

UTILS
Several text utils.
"""

__all__ = [
    'apply_tag_between_inside',
    'apply_tag_tex_commands',
    'apply_tag_tex_commands_no_argv',
    'Button',
    'check_repeated_words',
    'complete_langs_dict',
    'detect_language',
    'find_tex_command_char',
    'find_tex_commands',
    'find_tex_commands_noargv',
    'format_number_d',
    'get_diff_startend_word',
    'get_language_name',
    'get_number_of_day',
    'get_tex_commands_args',
    'get_word_from_cursor',
    'IS_OSX',
    'LangTexTextTags',
    'make_stemmer',
    'RESOURCES_PATH',
    'split_tags',
    'syntax_highlight',
    'tokenize',
    'VALID_TEX_COMMAND_CHARS',
    'validate_float',
    'validate_int'
]

import datetime
import os
import platform

from typing import List, Tuple

from pydetex._fonts import FONT_TAGS as _FONT_TAGS
from pydetex._utils_lang import *
from pydetex._utils_tex import *

# Resources path
__actualpath = str(os.path.abspath(os.path.dirname(__file__))).replace('\\', '/') + '/'
RESOURCES_PATH = __actualpath + 'res/'

# Check OS
IS_OSX = platform.system() == 'Darwin'

# Import Button widget
if IS_OSX:
    from tkmacosx import Button
else:
    from tkinter import Button


def split_tags(s: str, tags: List[str]) -> List[Tuple[str, str]]:
    """
    Split a string based on tags, each line is then tagged.

    String format:
    [TAG1]new line[TAG2]this is[TAG1]very epic

    Output:
    [('TAG1', 'newline'), ('TAG', 'this is), ('TAG1', 'very epic')]

    :param s: String
    :param tags: Tag list
    :return: Splitted tags
    """
    assert len(tags) > 0
    tagged_lines: List[Tuple[str, str]] = []
    r = 0
    for tag in tags:
        if r == 0:  # First occurence
            new = s.split(tag)
            for j in new:
                if j == '':
                    continue
                tagged_lines.append((tag, j))
        else:
            new_tagged_lines: List[Tuple[str, str]] = []
            for j in range(len(tagged_lines)):
                if tag in tagged_lines[j][1]:  # If tag exists
                    new = tagged_lines[j][1].split(tag)
                    new_tagged_lines.append((tagged_lines[j][0], new[0]))
                    for w in range(len(new) - 1):
                        new_tagged_lines.append((tag, new[w + 1]))
                else:
                    new_tagged_lines.append(tagged_lines[j])
            tagged_lines = new_tagged_lines

        r += 1

    # Merge consecutive tags
    merged_tags: List[Tuple[str, str]] = []
    r = 0
    for tagged in tagged_lines:
        if len(merged_tags) == 0 or tagged[0] != merged_tags[r - 1][0]:
            merged_tags.append(tagged)
            r += 1
        else:
            merged_tags[r - 1] = (tagged[0], merged_tags[r - 1][1] + tagged[1])

    return merged_tags


def button_text(s: str) -> str:
    """
    Generates the button text.

    :param s: Button's text
    :return: Text
    """
    return s if IS_OSX else f'  {s}  '


def validate_int(p: str) -> bool:
    """
    Validate an integer.

    :param p: Value
    :return: True if integer
    """
    if p == '' or p == '-':
        return True
    try:
        p = float(p)
        return int(p) == p
    except ValueError:
        pass
    return False


def validate_float(p: str) -> bool:
    """
    Validate a float.

    :param p: Value
    :return: True if integer
    """
    if p == '' or p == '-':
        return True
    try:
        float(p)
        return True
    except ValueError:
        pass
    return False


def syntax_highlight(s: str) -> str:
    """
    Syntax highlighter.

    :param s: Latex code
    :return: Code with format
    """
    # Add initial normal
    s = _FONT_TAGS['normal'] + s

    # Format equations
    s = apply_tag_between_inside(
        s=s,
        symbols_char=('$', '$'),
        tags=(_FONT_TAGS['equation_char'], _FONT_TAGS['equation_inside'],
              _FONT_TAGS['equation_char'], _FONT_TAGS['normal']),
        ignore_escape=True
    )

    # Format commands with {arguments}
    s = apply_tag_tex_commands(
        s=s,
        tags=(_FONT_TAGS['tex_command'],
              _FONT_TAGS['normal'],
              _FONT_TAGS['tex_argument'],
              _FONT_TAGS['normal'],
              '')
    )

    # Format commands without arguments
    s = apply_tag_tex_commands_no_argv(
        s=s,
        tags=(_FONT_TAGS['tex_command'], _FONT_TAGS['normal'])
    )

    # Return formatted string
    return s


def format_number_d(n: int, c: str) -> str:
    """
    Formats a number on thousands.

    :param n: Number
    :param c: Format char
    :return: Formatted number
    """
    assert isinstance(n, int)
    return format(n, ',').replace(',', c)


def get_number_of_day() -> int:
    """
    Return the number of the day from the current year.

    :return: Day number
    """
    return datetime.datetime.now().timetuple().tm_yday
