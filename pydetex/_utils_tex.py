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
    'find_tex_environments',
    'get_tex_commands_args',
    'TEX_COMMAND_CHARS',
    'TEX_EQUATION_CHARS',
    'tex_to_unicode'
]

import flatlatex
import os
import re

from flatlatex.parser import LatexSyntaxError
from typing import Tuple, Union, List, Dict, Optional, Any

# Flat latex object
_FLATLATEX = flatlatex.converter(ignore_newlines=False, keep_spaces=True)

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
TEX_COMMAND_CHARS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
                     'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
                     'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                     'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
                     'W', 'X', 'Y', 'Z', '*', '@']
TEX_EQUATION_CHARS = [
    ('$', '$', True),
    ('\(', '\)', False),
    ('\[', '\]', False),
    ('\\begin{align*}', '\end{align*}', False),
    ('\\begin{align}', '\end{align}', False),
    ('\\begin{displaymath}', '\end{displaymath}', False),
    ('\\begin{equation*}', '\\end{equation*}', False),
    ('\\begin{equation}', '\\end{equation}', False),
    ('\\begin{gather*}', '\\end{gather*}', False),
    ('\\begin{gather}', '\\end{gather}', False),
    ('\\begin{math}', '\end{math}', False)
]


def find_tex_command_char(
    s: str,
    symbols_char: List[Tuple[str, str, bool]],
) -> Tuple[Tuple[int, int, int, int], ...]:
    """
    Find symbols command positions.

    Example:

    .. code-block:: none

               00000000001111111111....
               01234567890123456789....
        Input: This is a $formula$ and this is not.
        Output: ((10, 11, 17, 18), ...)

    :param s: Latex string code
    :param symbols_char: Symbols to check ``[(initial, final, ignore escape), ...]``
    :return: Positions
    """
    assert isinstance(symbols_char, list)
    max_len = 0
    for j in symbols_char:
        assert len(j) == 3, f'Format is (initial, final, ignore escape); but received {j}'
        assert isinstance(j[0], str) and len(j[0]) > 0 and ' ' not in j[0]
        assert isinstance(j[1], str) and len(j[1]) > 0 and ' ' not in j[1]
        assert isinstance(j[2], bool)
        max_len = max(max_len, len(j[0]), len(j[1]))

    def _find(k: int, y: int, p: bool = True) -> bool:
        """
        Returns true if from k char (in s) the symbols-char-y element is present.

        :param k: Position to start
        :param y: Indes of the symbol within the list
        :param p: Reads the first (True) or last element
        :return: True if exist
        """
        if y < 0:
            return False
        n, m, ignore_escape = symbols_char[y]
        nm = n if p else m
        total = 0
        for z in range(len(nm)):
            if s[k + z] == nm[z] and (z == 0 and (not ignore_escape or ignore_escape and s[k - 1] != '\\') or z > 0):
                total += 1
        return total == len(nm)

    def _find_initial(k: int) -> int:
        """
        Find which symbol is contained.

        :param k: Position to start from
        :return: The index of the symbol within the list
        """
        for y in range(len(symbols_char)):
            if _find(k, y):
                return y
        return -1

    s = '_' + s + ' ' * max_len
    r = False  # Inside tag
    r_u = -1
    a = 0
    found = []

    for i in range(1, len(s) - max_len):
        u = _find_initial(i)
        v = _find(i, r_u, False)
        # Open tag
        if not r and u >= 0:
            a = i
            r = True
            r_u = u
        # Close
        elif r and v:
            r = False
            f, g = a - 1, i - 1
            found.append((f, f + len(symbols_char[r_u][0]), g - 1, g + len(symbols_char[r_u][1]) - 1))

    return tuple(found)


def apply_tag_between_inside_char_command(
    s: str,
    symbols_char: List[Tuple[str, str, bool]],
    tags: Union[Tuple[str, str, str, str], str]
) -> str:
    """
    Apply tag between symbols.

    For example, if symbols are ``($, $)`` and tag is ``[1,2,3,4]``:

    .. code-block:: none

        Input: This is a $formula$ and this is not.
        Output: This is a 1$2formula3$4 and this is not

    :param s: Latex string code
    :param symbols_char:  ``[(initial, final, ignore escape), ...]``
    :param tags: Tags to replace
    :return: String with tags
    """
    if isinstance(tags, str):
        if tags == '':
            return s
        tags = (tags, tags, tags, tags)

    assert len(tags) == 4
    a, b, c, d = tags
    tex_tags = find_tex_command_char(s, symbols_char)

    if len(tex_tags) == 0:
        return s
    new_s = ''
    k = 0  # Moves through tags
    for i in range(len(s)):
        if k < len(tex_tags):
            if i == tex_tags[k][0]:
                new_s += a + s[i]
                continue
            elif tex_tags[k][0] < i < tex_tags[k][1]:
                pass
            elif i == tex_tags[k][1] and tex_tags[k][1] != tex_tags[k][3]:
                new_s += b + s[i]
                if tex_tags[k][2] - tex_tags[k][1] == 0:
                    new_s += c
                continue
            elif i == tex_tags[k][2] and tex_tags[k][2] != tex_tags[k][0]:
                new_s += s[i] + c
                continue
            elif tex_tags[k][2] < i < tex_tags[k][3]:
                pass
            elif i == tex_tags[k][3]:
                new_s += s[i] + d
                k += 1
                continue
        new_s += s[i]

    return new_s


def find_tex_commands(s: str, offset: int = 0) -> Tuple[Tuple[int, int, int, int, bool], ...]:
    """
    Find all tex commands within a code.

    .. code-block:: none

                 00000000001111111111222
                 01234567890123456789012
                         a        b c  d
        Example: This is \\aCommand{nice}...
        Output: ((8, 16, 18, 21), ...)

    :param s: Latex string code
    :param offset: Offset added to the positioning, useful when using recursive calling on substrings
    :return: Tuple if found codes ``(a, b, c, d, command continues)``
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
    mode_arg = -1

    for i in range(len(s) - 1):
        # Start a command
        if not is_cmd and s[i] == '\\' and s[i + 1] in TEX_COMMAND_CHARS:
            a, b, is_cmd, is_argv = i, -1, True, False
            cmd_idx += 1
            mode_arg = -1
            depth_0, depth_1 = 0, 0

        # If command before args encounter an invalid chad, disables the command
        elif is_cmd and not is_argv and s[i] not in cont_chars and s[i] not in TEX_COMMAND_CHARS:
            is_cmd = False
            if s[i] == '\\' and s[i + 1] in TEX_COMMAND_CHARS:
                a, b, is_cmd, is_argv = i, -1, True, False
                cmd_idx += 1

        # If command has a new line, but following chars are not space
        elif is_cmd and not is_argv and s[i] == '\n' and s[i + 1] in TEX_COMMAND_CHARS:
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
                    if mode_arg < 0:
                        mode_arg = 0
                depth_0 += 1
            else:
                if depth_1 == 0:
                    c1 = i + 1
                    if mode_arg < 0:
                        mode_arg = 1
                depth_1 += 1

        # Ends the argument, only if depth condition satisfies
        elif is_cmd and is_argv and s[i] in ('}', ']') and s[i - 1] != '\\':
            if s[i] == '}':
                depth_0 -= 1
            else:  # ]
                depth_1 -= 1

            if (depth_0 == 0 and mode_arg == 0) or (depth_1 == 0 and mode_arg == 1):  # Finished
                d = i - 1
                found.append([a, b, c0 if s[i] == '}' else c1, d, cmd_idx])
                if s[i + 1] not in cont_chars:
                    is_cmd = False
                is_argv = False
                mode_arg = -1
            # elif depth_0 < 0 or depth_1 < 0:  # Invalid argument (parenthesis imbalance)
            #     is_cmd = False
            #     is_argv = False
            # mode_arg = -1

    # Add the offsets
    for f in found:
        f[0] += offset
        f[1] += offset
        f[2] += offset
        f[3] += offset

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


def _find_tex_env_recursive(original_s: str, s: str, offset: int = 0, depth: int = 0) -> List:
    """
    Find all environments.

    :param s: Latex string code
    :param offset: Offset applied to the search
    :return: Tuple of all commands
    """
    tags = find_tex_commands(s, offset=offset)
    new_tags = []
    for t in tags:
        a, b, c, d, _ = t
        source_cmd = s[a - offset:b - offset + 1]
        if 'begin' not in source_cmd and 'end' not in source_cmd:
            # Get the arguments of the command, and check more environments there
            cmd_args = s[c - offset:d - offset + 1]
            if 'begin' in cmd_args or 'end' in cmd_args:
                if 'newenvironment' in source_cmd or 'newcommand' in source_cmd:  # Prone to bugs
                    continue
                for tr in _find_tex_env_recursive(original_s, cmd_args, offset=c, depth=depth + 1):
                    new_tags.append(tr)
        else:
            new_tags.append(t)
    return new_tags


def find_tex_environments(s: str) -> Tuple[Tuple[str, int, int, int, int, str, int, int], ...]:
    """
    Find all tex commands within a code.

    Example:

    .. code-block:: none

                 0000000000111111111122222222223333333333
                 0123456789012345678901234567890123456789
                         a           b        c         d
        Example: This is \begin{nice}[cmd]my...\end{nice}
        Output: (('nice', 8, 20, 29, 39, 'parentenv', 0, -1), ...)

    This method also returns the name of the parent environment, the depth of the
    environment, and the depth of the item enviroment (if itemizable).

    :param s: Latex string code
    :return: Tuple if found environment ``(env_name, a, b, c, d, parent_env_name, env_depth, env_item_depth)``
    """

    def _env_common(e: str) -> str:
        """
        Return the common environment for a given name.

        :param e: Environment name
        :return: Common environment
        """
        if ('itemize' in e) or ('enumerate' in e) or ('tablenotes' in e):
            return 'item_'
        return ''

    tags = _find_tex_env_recursive(s, s)
    envs = []
    env: Dict[str, List[Tuple[int, int, str, int]]] = {}
    last_env = ''
    env_depth = 0
    cmds_cont = []
    env_depths: Dict[str, int] = {}

    for t in tags:
        a, b, c, d, _ = t
        if 'begin' in s[a:b + 1]:
            env_name = s[c:d + 1]
            c_env_name = _env_common(env_name)  # Common environment name
            if c_env_name not in env_depths.keys():
                env_depths[c_env_name] = 0
            else:
                env_depths[c_env_name] += 1
            env_i = (a, d + 2, last_env, env_depth)
            if env_name not in env:
                env[env_name] = [env_i]
            else:
                env[env_name].append(env_i)
            if a not in cmds_cont:
                cmds_cont.append(a)
                last_env = env_name
                env_depth += 1
        elif 'end' in s[a:b + 1]:
            env_name = s[c:d + 1]
            c_env_name = _env_common(env_name)  # Common environment name

            if env_name in env.keys():
                env_i = env[env_name].pop()

                # Update env itemize depth
                env_depth_item = -1
                if c_env_name != '':
                    env_depth_item = env_depths[c_env_name]
                    env_depths[c_env_name] -= 1

                envs.append((
                    env_name,  # Environment name
                    env_i[0],  # a-position of the env
                    env_i[1],  # b-position
                    a,  # c-position
                    d,  # d-position
                    env_i[2],  # parent environment name
                    env_i[3],  # depth of the environment
                    env_depth_item  # itemize depth
                ))

                if len(env[env_name]) == 0:
                    del env[env_name]
                last_env = env_i[2]
                env_depth -= 1

    return tuple(envs)


def get_tex_commands_args(
    s: str,
    pos: bool = False
) -> Tuple[Tuple[Union[str, Tuple[str, bool], Tuple[int, int]], ...], ...]:
    """
    Get all the arguments from a tex command. Each command argument has a boolean
    indicating if that is optional or not.

    .. code-block:: none

        Example: This is \aCommand[\label{}]{nice} and...
        Output: (('aCommand', ('\label{}', True), ('nice', False)), ...)

    :param s: Latex string code
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

    .. code-block:: none

                 00000000001111111111222
                 01234567890123456789012
                         x       x
        Example: This is \aCommand ...
        Output: ((8,16), ...)

    :param s: Latex string code
    :return: Tuple if found codes
    """
    found = []
    is_cmd = False
    s += '_'
    a = 0
    cont_chars = ('{', '[', ' ')

    for i in range(len(s) - 1):
        if not is_cmd and s[i] == '\\' and s[i + 1] in TEX_COMMAND_CHARS:
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

        elif is_cmd and s[i] not in TEX_COMMAND_CHARS and s[i] not in cont_chars:
            is_cmd = False
            found.append([a, i - 1])

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
    Apply tag to tex command.

    For example, if tag is ``[1,2,3,4,5]``:

    .. code-block:: none

        Input: This is a \\formula{epic} and this is not
        Output: This is a 1\\formula2{3epic4}5 and this is not

    :param s: Latex string code
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
    Apply tag to tex command.

    For example, if tag is ``[1,2]``:

    .. code-block:: none

        Input: This is a \\formula and this is not.
        Output: This is a 1\\formula2 and this is not

    :param s: Latex string code
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
    If ``s`` is just a latex code ``'alpha'`` or ``'beta'`` it converts it to its
    unicode representation.

    :param s: Latex string code
    :return: Latex with converted single symbols
    """
    if '\\' not in s[0]:
        s = '\\' + s
    for (code, val) in _TEX_TO_UNICODE['latex_symbols']:
        if code == s:
            return val
    return None


def _convert_latex_symbols(s: str) -> str:
    """
    Replace each ``'\alpha'``, ``'\beta'`` and similar latex symbols with
    their unicode representation.

    :param s: Latex string code
    :return: Replaced symbols
    """
    for (code, val) in _TEX_TO_UNICODE['latex_symbols']:
        s = s.replace(code, val)
    return s


def _process_starting_modifiers(s: str) -> str:
    """
    If s start with ``'it '``, ``'cal '``, etc. then make the whole string
    italic, calligraphic, etc.

    :param s: Latex string code
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

    :param s: Latex string code
    :return: Text with replaced chars
    """
    s = _apply_modifier(s, '^', _TEX_TO_UNICODE['superscripts'])
    s = _apply_modifier(s, '_', _TEX_TO_UNICODE['subscripts'])

    s = _apply_modifier(s, '\\bb', _TEX_TO_UNICODE['textbb'])
    s = _apply_modifier(s, '\\bf', _TEX_TO_UNICODE['textbf'])
    s = _apply_modifier(s, '\\cal', _TEX_TO_UNICODE['textcal'])
    s = _apply_modifier(s, '\\emph', _TEX_TO_UNICODE['textit'])
    s = _apply_modifier(s, '\\frak', _TEX_TO_UNICODE['textfrak'])
    s = _apply_modifier(s, '\\it', _TEX_TO_UNICODE['textit'])
    s = _apply_modifier(s, '\\mono', _TEX_TO_UNICODE['textmono'])

    return s


def _apply_modifier(s: str, modifier: str, d: Dict[Any, str]) -> str:
    """
    This will search for the ^ signs and replace the next
    digit or (digits when {} is used) with its/their uppercase representation.

    :param s: Latex string code
    :param modifier: Modifier command
    :param d: Dict to look upon
    :return: New text with replaced text.
    """
    s = s.replace(modifier, "^")
    newtext = ""
    mode_normal, mode_modified, mode_long = range(3)
    mode = mode_normal
    for ch in s:
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
            with open(f'{respath}symbols.txt', 'r', encoding='utf-8') as f:
                line = f.readline()
                while line != "":
                    words = line.split()
                    code = words[0]
                    val = words[1]
                    _TEX_TO_UNICODE['latex_symbols'].append((code, val))
                    line = f.readline()
        else:
            with open(f'{respath}{j}.txt', 'r', encoding='utf-8') as f:
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

    :param s: Latex string code
    :return: Text in unicode
    """
    if s.strip() == '':
        return s
    ss = _convert_single_symbol(s)
    if ss is not None:
        return ss

    s = _convert_latex_symbols(s)
    s = _process_starting_modifiers(s)
    s = _apply_all_modifiers(s)

    # Last filter
    s = s.replace('\n\n', '\n').replace('  ', ' ').replace('\t', ' ')
    try:
        s = _FLATLATEX.convert(s)
    except LatexSyntaxError:
        pass

    return s


# Loads the unicode data
__load_unicode()
