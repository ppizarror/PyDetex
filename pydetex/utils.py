"""
PyDetex
https://github.com/ppizarror/PyDetex

UTILS
Module that contain all util methods and classes used in parsers and pipelines,
from tex, language, and low-level.
"""

__all__ = [
    'apply_tag_between_inside_char_command',
    'apply_tag_tex_commands',
    'apply_tag_tex_commands_no_argv',
    'Button',
    'check_repeated_words',
    'complete_langs_dict',
    'detect_language',
    'find_tex_command_char',
    'find_tex_commands',
    'find_tex_commands_noargv',
    'find_tex_environments',
    'format_number_d',
    'get_diff_startend_word',
    'get_language_name',
    'get_number_of_day',
    'get_tex_commands_args',
    'get_word_from_cursor',
    'IS_OSX',
    'LangTexTextTags',
    'make_stemmer',
    'open_file',
    'ProgressBar',
    'RESOURCES_PATH',
    'split_tags',
    'syntax_highlight',
    'TEX_COMMAND_CHARS',
    'TEX_EQUATION_CHARS',
    'tex_to_unicode',
    'tokenize',
    'validate_float',
    'validate_int'
]

import datetime
import os
import platform
import sys
import time

from typing import List, Tuple, Dict

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
    :return: Split tags
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

    :param s: Latex string code
    :return: Code with format
    """
    # Add initial normal
    s = _FONT_TAGS['normal'] + s.strip()

    # Format equations
    s = apply_tag_between_inside_char_command(
        s=s,
        symbols_char=TEX_EQUATION_CHARS,
        tags=(_FONT_TAGS['equation_char'], _FONT_TAGS['equation_inside'],
              _FONT_TAGS['equation_char'], _FONT_TAGS['normal'])
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


def open_file(f: str) -> str:
    """
    Open file and return its string.

    :param f: Filename
    :return: File content
    """
    o = open(f, 'r', encoding='utf-8')
    text = ''.join(o.readlines())
    o.close()
    return text


class ProgressBar(object):
    """
    Basic progress bar implementation.
    """

    _current: int
    _last_step: float
    _size: int
    _step_times: Dict[str, float]
    _steps: int
    _t0: float

    def __init__(self, steps: int, size: int = 15) -> None:
        """
        Constructor.

        :param steps: How many steps have the procedure
        :param size: Bar size
        """
        assert isinstance(steps, int) and steps >= 1
        assert isinstance(size, int) and size >= 1
        self._current = 0
        self._last_step = time.time()
        self._size = size  # Bar size
        self._step_times = {}
        self._steps = steps - 1
        self._t0 = time.time()

    def _print_progress_bar(self, i: int, max_: int, post_text: str) -> None:
        """
        Prints a progress bar.

        :param i: Progress bar
        :param max_: Max steps
        :param post_text: Status
        """
        j = i / max_
        sys.stdout.write('\r')
        sys.stdout.write(f"[{'=' * int(self._size * j):{self._size}s}] {int(100 * j)}%  {post_text}")
        sys.stdout.flush()

    def update(self, status: str = '', print_total_time: bool = True) -> None:
        """
        Update the current status to a new step.

        :param status: Status text
        :param print_total_time: Prints total computing time
        """
        if self._current > self._steps:
            return
        self._print_progress_bar(self._current, self._steps, status)
        dt = time.time() - self._last_step
        self._last_step = time.time()
        self._step_times[status] = dt
        self._current += 1
        if self._current == self._steps + 1:
            print('')
            sys.stdout.flush()
            if print_total_time:
                print(f'Process finished in {time.time() - self._t0:.3f} seconds')

    def detail_times(self) -> None:
        """
        Print times.
        """
        for k in self._step_times.keys():
            print(f'{self._step_times[k]:.3f}s\t{k}')

    def reset(self) -> None:
        """
        Reset the steps.
        """
        self._current = 0
        self._t0 = time.time()
        self._last_step = time.time()
        self._step_times.clear()
