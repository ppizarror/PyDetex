"""
PyDetex
https://github.com/ppizarror/PyDetex

UTILS TEX
Latex utils.
"""

__all__ = [
    'apply_tag_between_inside_char_command',
    'apply_tag_tex_commands',
    'apply_tag_tex_commands_no_argv',
    'find_tex_command_char',
    'find_tex_commands',
    'find_tex_commands_noargv',
    'get_tex_commands_args',
    'tex_to_unicode',
    'VALID_TEX_COMMAND_CHARS'
]

import flatlatex
import os
import re

from typing import Tuple, Union, List, Dict, Optional, Any

# Flat latex object
_FLATLATEX = flatlatex.converter()

# Tex to unicode
_TEX_TO_UNICODE: Dict[str, Union[Dict[Any, str], List[Tuple[str, str]]]] = {
    'latex_symbols': [],
    'subscripts': {},
    'superscripts': {},
    'textbb': {},
    'textbf': {},
    'textcal': {},
    'textfrak': {},
    'textit': {},
    'textmono': {}
}

# Valid command chars
VALID_TEX_COMMAND_CHARS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
                           'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
                           'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                           'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
                           'W', 'X', 'Y', 'Z']


def find_tex_command_char(
        s: str,
        symbols_char: Union[Tuple[str, str], str],
        ignore_escape: bool = False
) -> Tuple[Tuple[int, int], ...]:
    """
    Find symbols command positions. Example:

           00000000001111111111....
           01234567890123456789....
    Input: This is a $formula$ and this is not.
    Output: ((10, 18), ...)

    :param s: String
    :param symbols_char: Symbols to check
    :param ignore_escape: Ignores \\char
    :return: Positions
    """
    if isinstance(symbols_char, str):
        symbols_char = (symbols_char, symbols_char)
    assert len(symbols_char) == 2
    assert len(symbols_char[0]) == 1 and len(symbols_char[1]) == 1

    s = '_' + s
    r = False  # Inside tag
    a = 0
    found = []

    for i in range(1, len(s)):
        # Open tag
        if not r and s[i] == symbols_char[0][0] and (not ignore_escape or ignore_escape and s[i - 1] != '\\'):
            a = i
            r = True
        # Close
        elif r and s[i] == symbols_char[1][0] and (not ignore_escape or ignore_escape and s[i - 1] != '\\'):
            r = False
            found.append((a - 1, i - 1))

    return tuple(found)


def apply_tag_between_inside_char_command(
        s: str,
        symbols_char: Tuple[str, str],
        tags: Union[Tuple[str, str, str, str], str],
        ignore_escape: bool = False
) -> str:
    """
    Apply tag between symbols. For example, if symbols are ($, $) and tag is [1,2,3,4]:

    Input: This is a $formula$ and this is not.
    Output: This is a 1$2formula3$4 and this is not

    :param s: String
    :param symbols_char: Symbols to check
    :param tags: Tags to replace
    :param ignore_escape: Ignores \\char
    :return: String with tags
    """
    assert len(symbols_char) == 2
    assert len(symbols_char[0]) == 1 and len(symbols_char[1]) == 1
    if isinstance(tags, str):
        if tags == '':
            return s
        tags = (tags, tags, tags, tags)

    assert len(tags) == 4
    a, b, c, d = tags
    tex_tags = find_tex_command_char(s, symbols_char, ignore_escape)

    if len(tex_tags) == 0:
        return s
    new_s = ''
    k = 0  # Moves through tags

    for i in range(len(s)):
        if k < len(tex_tags) and i in tex_tags[k]:
            if i == tex_tags[k][0]:
                new_s += a + s[i] + b
            else:
                new_s += c + s[i] + d
                k += 1
        else:
            new_s += s[i]

    return new_s


def find_tex_commands(s: str) -> Tuple[Tuple[int, int, int, int, bool], ...]:
    """
    Find all tex commands within a code.

             00000000001111111111222
             01234567890123456789012
                     a       b c  d
    Example: This is \aCommand{nice}... => ((8,16,18,21), ...)

    :param s: Latex code
    :return: Tuple if found codes (a, b, c, d, command continues)
    """
    found: List = []
    is_cmd = False
    is_argv = False
    s += '_'
    a, b, c0, c1, d = 0, -1, 0, 0, 0
    depth_0 = 0  # {}
    depth_1 = 0  # []
    cont_chars = ('{', '[', ' ', '\n')
    cmd_idx = 0  # index

    for i in range(len(s) - 1):
        # print(i, s[i], depth_0, depth_1, is_cmd, is_argv)

        # Start a command
        if not is_cmd and s[i] == '\\' and s[i + 1] in VALID_TEX_COMMAND_CHARS:
            a, b, is_cmd, is_argv = i, -1, True, False
            cmd_idx += 1

        # If command before args encounter an invalid chad, disables the command
        elif is_cmd and not is_argv and s[i] not in cont_chars and s[i] not in VALID_TEX_COMMAND_CHARS:
            is_cmd = False
            if s[i] == '\\' and s[i + 1] in VALID_TEX_COMMAND_CHARS:
                a, b, is_cmd, is_argv = i, -1, True, False
                cmd_idx += 1

        # If command has a new line, but following chars are not space
        elif is_cmd and not is_argv and s[i] == '\n' and s[i + 1] in VALID_TEX_COMMAND_CHARS:
            is_cmd = False

        # If command, not arg, but an invalid char follows the space, disables the command
        elif is_cmd and not is_argv and s[i - 1] == ' ' and s[i] not in cont_chars:
            is_cmd = False

        # Inits a new arg
        elif is_cmd and s[i] in ('{', '[') and s[i - 1] != '\\':
            is_argv = True
            if b == -1:
                b = i - 1
                depth_0, depth_1 = 0, 0
            if s[i] == '{':
                if depth_0 == 0:
                    c0 = i + 1
                depth_0 += 1
            else:
                if depth_1 == 0:
                    c1 = i + 1
                depth_1 += 1

        # Ends the argument, only if depth condition satisfies
        elif is_cmd and is_argv and s[i] in ('}', ']') and s[i - 1] != '\\':
            if s[i] == '}':
                depth_0 -= 1
            else:
                depth_1 -= 1
            if depth_0 == 0 and depth_1 == 0:  # Finished
                d = i - 1
                found.append([a, b, c0 if s[i] == '}' else c1, d, cmd_idx])
                if s[i + 1] not in cont_chars:
                    is_cmd = False
                is_argv = False
            elif depth_0 < 0 or depth_1 < 0:  # Invalid argument (parenthesis imbalance)
                is_cmd = False
                is_argv = False

    # Check if command continues
    if len(found) == 0:
        return ()
    elif len(found) == 1:
        found[0][4] = False
    else:
        for k in range(1, len(found)):
            if found[k][4] == found[k - 1][4]:
                found[k - 1][4] = True
            else:
                found[k - 1][4] = False
            if k == len(found) - 1:
                found[k][4] = False
    for k in range(len(found)):
        # noinspection PyUnresolvedReferences
        found[k] = tuple(found[k])

    return tuple(found)


def get_tex_commands_args(
        s: str,
        pos: bool = False
) -> Tuple[Tuple[Union[str, Tuple[str, bool], Tuple[int, int]], ...], ...]:
    """
    Get all the arguments from a tex command. Each command argument has a boolean
    indicating if that is optional or not.

    Example: This is \aCommand[\label{}]{nice} and... => (('aCommand', ('\label{}', True), ('nice', False)), ...)

    :param s: Latex code
    :param pos: Add the numerical position of the original string at the last position
    :return: Arguments
    """
    tags = find_tex_commands(s)
    commands = []
    command = []
    for t in tags:
        a, b, c, d, cont = t
        if len(command) == 0:
            command.append(s[a + 1:b + 1].strip())
        arg = s[c - 1:d + 2]
        optional = '[' in arg
        command.append((arg[1:-1], optional))
        if not cont:
            if pos:
                command.append((a, d + 2))
            commands.append(tuple(command))
            command = []
    return tuple(commands)


def find_tex_commands_noargv(s: str) -> Tuple[Tuple[int, int], ...]:
    """
    Find all tex commands with no arguments within a code.

             00000000001111111111222
             01234567890123456789012
                     x       x
    Example: This is \aCommand ... => ((8,16), ...)

    :param s: Latex code
    :return: Tuple if found codes
    """
    found = []
    is_cmd = False
    s += '_'
    a = 0
    cont_chars = ('{', '[', ' ')

    for i in range(len(s) - 1):

        if not is_cmd and s[i] == '\\' and s[i + 1] in VALID_TEX_COMMAND_CHARS:
            if i > 0 and s[i - 1] == '⇲':
                continue
            a = i
            is_cmd = True

        elif is_cmd and s[i] == '\\':
            if i - 1 - a > 0:
                found.append([a, i - 1])
            a = i

        elif is_cmd and s[i] in ('{', '['):
            is_cmd = False

        # If command, not arg, but an invalid char follows the space, disables the command
        elif is_cmd and s[i - 1] == ' ' and s[i] not in cont_chars:
            is_cmd = False
            found.append([a, i - 1])

        elif is_cmd and s[i] not in VALID_TEX_COMMAND_CHARS and s[i] not in cont_chars:
            is_cmd = False
            found.append([a, i - 1])

        # print(i, s[i], is_cmd, found)

    if is_cmd and a != len(s) - 2:
        found.append([a, len(s) - 2])

    # Strip chars
    for k in range(len(found)):
        ch = found[k][1]
        for j in range(ch):
            if s[found[k][1]] == ' ':
                found[k][1] -= 1
            else:
                break
        # noinspection PyUnresolvedReferences
        found[k] = tuple(found[k])

    return tuple(found)


def apply_tag_tex_commands(
        s: str,
        tags: Union[Tuple[str, str, str, str, str], str]
) -> str:
    """
    Apply tag to tex command. For example, if tag is [1,2,3,4,5]:

    Input: This is a \formula{epic} and this is not.
    Output: This is a 1\formula2{3epic4}5 and this is not

    :param s: Code
    :param tags: Tags (length 5)
    :return: Code with tags
    """
    if isinstance(tags, str):
        if tags == '':
            return s
        tags = (tags, tags, tags, tags, tags)
    assert len(tags) == 5
    a, b, c, d, e = tags  # Unpack

    tex_tags = find_tex_commands(s)
    if len(tex_tags) == 0:
        return s
    new_s = ''
    k = 0  # Moves through tags
    i = -1
    for _ in range(len(s)):
        i += 1
        if i == len(s):
            break
        if k < len(tex_tags) and i in tex_tags[k][0:4]:
            if i == tex_tags[k][0]:
                new_s += a + s[i]
            elif i == tex_tags[k][1]:
                new_s += s[i] + b
            elif i == tex_tags[k][2] and i != tex_tags[k][3]:
                new_s += c + s[i]
            elif i == tex_tags[k][3]:
                if i == tex_tags[k][2]:
                    new_s += c
                new_s += s[i] + d + s[i + 1] + e
                i += 1
                # if continues
                if tex_tags[k][4]:
                    new_s += b
                k += 1
        else:
            new_s += s[i]

    return new_s[0:len(new_s)]


def apply_tag_tex_commands_no_argv(
        s: str,
        tags: Union[Tuple[str, str], str]
) -> str:
    """
    Apply tag to tex command. For example, if tag is [1,2]:

    Input: This is a \formula and this is not.
    Output: This is a 1\formula2 and this is not

    :param s: Code
    :param tags: Tags (length 5)
    :return: Code with tags
    """
    if isinstance(tags, str):
        if tags == '':
            return s
        tags = (tags, tags)
    assert len(tags) == 2
    a, b = tags  # Unpack

    tex_tags = find_tex_commands_noargv(s)
    if len(tex_tags) == 0:
        return s
    new_s = ''
    k = 0  # Moves through tags
    i = -1
    for _ in range(len(s)):
        i += 1
        if k < len(tex_tags) and i in tex_tags[k]:
            if i == tex_tags[k][0]:
                new_s += a + s[i]
            elif i == tex_tags[k][1]:
                new_s += s[i] + b
                k += 1
        else:
            new_s += s[i]

    return new_s


def _convert_single_symbol(s: str) -> Optional[str]:
    """
    If s is just a latex code 'alpha' or 'beta' it converts it to its
    unicode representation.

    :param s:
    :return:
    """
    ss = '\\' + s
    for (code, val) in _TEX_TO_UNICODE['latex_symbols']:
        if code == ss:
            return val
    return None


def convert_latex_symbols(s: str) -> str:
    """
    Replace each '\alpha', '\beta' and similar latex symbols with
    their unicode representation.

    :param s: Text
    :return: Replaced symbols
    """
    for (code, val) in _TEX_TO_UNICODE['latex_symbols']:
        s = s.replace(code, val)
    return s


def _process_starting_modifiers(s: str) -> str:
    """
    If s start with 'it ', 'cal ', etc. then make the whole string
    italic, calligraphic, etc.

    :param s: Text
    :return: Modified text
    """
    s = re.sub('^bb ', r'\\bb{', s)
    s = re.sub('^bf ', r'\\bf{', s)
    s = re.sub('^it ', r'\\it{', s)
    s = re.sub('^cal ', r'\\cal{', s)
    s = re.sub('^frak ', r'\\frak{', s)
    s = re.sub('^mono ', r'\\mono{', s)
    return s


def _apply_all_modifiers(s: str) -> str:
    """
    Applies all modifiers.

    :param s: Text
    :return: Text with replaced chars
    """
    s = _apply_modifier(s, '^', _TEX_TO_UNICODE['superscripts'])
    s = _apply_modifier(s, '_', _TEX_TO_UNICODE['subscripts'])
    s = _apply_modifier(s, '\\bb', _TEX_TO_UNICODE['textbb'])
    s = _apply_modifier(s, '\\bf', _TEX_TO_UNICODE['textbf'])
    s = _apply_modifier(s, '\\it', _TEX_TO_UNICODE['textit'])
    s = _apply_modifier(s, '\\cal', _TEX_TO_UNICODE['textcal'])
    s = _apply_modifier(s, '\\frak', _TEX_TO_UNICODE['textfrak'])
    s = _apply_modifier(s, '\\mono', _TEX_TO_UNICODE['textmono'])
    return s


def _apply_modifier(text: str, modifier: str, d: Dict[Any, str]) -> str:
    """
    This will search for the ^ signs and replace the next
    digit or (digits when {} is used) with its/their uppercase representation.

    :param text: Text
    :param modifier: Modifier command
    :param d: Dict to look upon
    :return: New text with replaced text.
    """
    text = text.replace(modifier, "^")
    newtext = ""
    mode_normal, mode_modified, mode_long = range(3)
    mode = mode_normal
    for ch in text:
        if mode == mode_normal and ch == '^':
            mode = mode_modified
            continue
        elif mode == mode_modified and ch == '{':
            mode = mode_long
            continue
        elif mode == mode_modified:
            newtext += d.get(ch, ch)
            mode = mode_normal
            continue
        elif mode == mode_long and ch == '}':
            mode = mode_normal
            continue

        if mode == mode_normal:
            newtext += ch
        else:
            newtext += d.get(ch, ch)
    return newtext


def __load_unicode() -> None:
    """
    Loads the unicode data.
    """
    respath = str(os.path.abspath(os.path.dirname(__file__))).replace('\\', '/') + '/res/u_'
    for j in _TEX_TO_UNICODE.keys():
        if j == 'latex_symbols':
            with open(f'{respath}symbols.txt', "r") as f:
                line = f.readline()
                while line != "":
                    words = line.split()
                    code = words[0]
                    val = words[1]
                    _TEX_TO_UNICODE['latex_symbols'].append((code, val))
                    line = f.readline()
        else:
            with open(f'{respath}{j}.txt', 'r') as f:
                line = f.readline()
                while line != '':
                    words = line.split()
                    code = words[0]
                    val = words[1]
                    _TEX_TO_UNICODE[j][code] = val
                    line = f.readline()


def tex_to_unicode(s: str) -> str:
    """
    Transforms tex code to unicode.

    :param s: Latex code
    :return: Text in unicode
    """
    if s.strip() == '':
        return s
    ss = _convert_single_symbol(s)
    if ss is not None:
        return ss

    s = convert_latex_symbols(s)
    s = _process_starting_modifiers(s)
    s = _apply_all_modifiers(s)

    # Last filter
    s = _FLATLATEX.convert(s)
    return s


# Loads the unicode data
__load_unicode()
