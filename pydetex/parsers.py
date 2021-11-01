"""
PyDetex
https://github.com/ppizarror/PyDetex

PARSERS
Defines parsers, which perform a single task for removal LaTex things.
"""

__all__ = [
    'find_str',
    'FONT_FORMAT_SETTINGS',
    'process_chars_equations',
    'process_cite',
    'process_inputs',
    'process_items',
    'process_labels',
    'process_quotes',
    'process_ref',
    'remove_commands_char',
    'remove_commands_param',
    'remove_commands_param_noargv',
    'remove_comments',
    'remove_common_tags',
    'remove_equations',
    'remove_tag',
    'replace_pydetex_tags',
    'simple_replace',
    'strip_punctuation',
    'unicode_chars_equations'
]

import os
import pydetex.utils as ut

from pydetex._symbols import *
from typing import List, Tuple, Union

# Files
_NOT_FOUND_FILES = []
_PRINT_LOCATION = False

# Tags
_TAG_CLOSE_CITE = '⇱CLOSE_CITE⇲'
_TAG_FILE_ERROR = '⇱FILE_ERROR⇲'
_TAG_ITEM_SPACE = '⇱ITEM_SPACE⇲'
_TAG_OPEN_CITE = '⇱OPEN_CITE⇲'

# Others
_ROMAN_DIGITS = [
    (1000, 'M'),
    (900, 'CM'),
    (500, 'D'),
    (400, 'CD'),
    (100, 'C'),
    (90, 'XC'),
    (50, 'L'),
    (40, 'XL'),
    (10, 'X'),
    (9, 'IX'),
    (5, 'V'),
    (4, 'IV'),
    (1, 'I')
]

# Parser font format. This dict stores the font of some tex elements to be represented
# in the GUI text editor. The values are the same of _fonts.FONT_TAGS. By default
# they are empty, and are updated in the PyDetexGUI._process() method
FONT_FORMAT_SETTINGS = {
    'cite': '',
    'equation': '',
    'normal': '',
    'ref': '',
    'tex_text_tag': '',
    'tex_text_tag_content': ''
}

LANG_TEX_TEXT_TAGS = ut.LangTexTextTags()


def _find_str(s: str, char: str) -> int:
    """
    Finds a sequence within a string, and returns the position. If not exists, returns ``-1``.

    :param s: Latex string code
    :param char: Sequence
    :return: Position
    """
    index = 0

    if char in s:
        c = char[0]
        for ch in s:
            if ch == c:
                if s[index:index + len(char)] == char:
                    return index

            index += 1

    return -1


def _os_listfolder() -> List[str]:
    """
    Returns the folders from the current path.

    :return: Folder list
    """
    dirs = os.listdir('./')
    folders = []
    for k in dirs:
        if os.path.isdir(k):
            folders.append(k + '/')
    return folders


def _load_file(f: str, path: str) -> str:
    """
    Try to load a file.

    :param f: Filename
    :param path: Path to look from
    :return: File contents
    """
    try:
        return ut.open_file(path + f)
    except FileNotFoundError:
        return _TAG_FILE_ERROR


def find_str(s: str, char: Union[str, List[str], Tuple[str, ...]]) -> int:
    """
    Finds a sequence within a string, and returns the position. If not exists, returns ``-1``.

    :param s: Latex string code
    :param char: Sequence or List of sequences
    :return: Position
    """
    if isinstance(char, str):
        return _find_str(s, char)
    else:
        for ch in char:
            j = _find_str(s, ch)
            if j != -1:
                return j
    return -1


def remove_tag(s: str, tagname: str) -> str:
    """
    Removes a latex tag code.

    :param s: Latex string code
    :param tagname: Tag code
    :return: String without tags
    """
    tagname = '\\' + tagname
    tagadd = 1
    if '{' not in tagname:
        tagname += '{'
        tagadd = 0
    while True:
        k = find_str(s, tagname)
        if k == -1:  # No more tags, return
            return s
        deep = 0
        f = False
        for j in range(len(s)):
            if s[k + j] == '{':
                deep += 1
                f = True
                continue
            if s[k + j] == '}':
                deep -= 1
            if deep == 0 and f:
                # update s
                s = s[:k] + s[k + len(tagname) + tagadd:k + j] + s[k + j + 1:]
                break


def remove_common_tags(s: str) -> str:
    """
    Remove common tags from string.

    :param s: Latex string code
    :return: Text without tags
    """
    for tag in [
        'bigp',
        'chapter',
        'emph',
        'section',
        'subsection',
        'subsubsection',
        'subsubsubsection',
        'textbf',
        'textit',
        'texttt'
    ]:
        s = remove_tag(s, tag)
    return s


def process_cite(s: str) -> str:
    """
    Transforms all cites to a text-based with numbers. For example:
    ``'This is from \\cite{Pizarro}'`` to ``'This is from [1]'``.

    :param s: Latex string code
    :return: Latex with cite as numbers
    """
    cites = {}
    look = ['\\cite*{', '\\citet*{', '\\citep*{', '\\cite{', '\\citet{', '\\citep{']
    k = -1
    while True:
        for j in look.copy():
            k = find_str(s, j)
            if k == -1:
                look.remove(j)
            else:
                break
        if k == -1:
            return s
        for j in range(len(s)):
            if s[k + j] == '}':
                c = s[k + 6:k + j]
                for w in c.split(','):
                    if w not in cites.keys():
                        cites[w] = len(cites.keys()) + 1
                    c = c.replace(w, str(cites[w]))
                s = s[:k] + FONT_FORMAT_SETTINGS['cite'] + _TAG_OPEN_CITE + c + \
                    _TAG_CLOSE_CITE + FONT_FORMAT_SETTINGS['normal'] + s[k + j + 1:]
                break


def replace_pydetex_tags(
        s: str,
        cite_format: Tuple[str, str] = ('[', ']')
) -> str:
    """
    Replaces font tags to an specific format.

    :param s: Latex string code
    :param cite_format: Cite format
    :return: String with no cites
    """
    assert len(cite_format) == 2
    s = s.replace(_TAG_OPEN_CITE, (cite_format[0]))
    s = s.replace(_TAG_CLOSE_CITE, (cite_format[1]))
    s = s.replace(_TAG_ITEM_SPACE, ' ')
    return s


def process_labels(s: str) -> str:
    """
    Removes labels.

    :param s: Latex string code
    :return: String with no labels
    """
    while True:
        k = find_str(s, '\\label{')
        if k == -1:
            return s
        for j in range(len(s)):
            if s[k + j] == '}':
                s = s[:k] + s[k + j + 1:]
                break


def process_ref(s) -> str:
    """
    Process references, same as cites, replaces by numbers.

    :param s: Latex string code
    :return: String with numbers instead of references.
    """
    r = 1
    while True:
        k = find_str(s, '\\ref{')
        if k == -1:
            return s
        for j in range(len(s)):
            if s[k + j] == '}':
                s = s[:k] + FONT_FORMAT_SETTINGS['ref'] + str(r) + FONT_FORMAT_SETTINGS['normal'] + s[k + j + 1:]
                r += 1
                break


def process_quotes(s) -> str:
    """
    Process quotes.

    :param s: Latex string code
    :return: String with "quotes"
    """
    while True:
        k = find_str(s, ['\\quotes{', '\\doublequotes{'])
        if k == -1:
            return s
        m = 0
        for j in range(len(s)):
            if s[k + j] == '{':
                m = j
            if s[k + j] == '}':
                s = s[:k] + '"' + s[k + m + 1:k + j] + '"' + s[k + j + 1:]
                break


def remove_comments(s: str) -> str:
    """
    Remove comments from text.

    :param s: Latex string code
    :return: String without comments
    """
    comment_symbol = '⇱COMMENT_PERCENTAGE_SYMBOL⇲'
    newline_symbol = '⇱NEWLINE_SYMBOL⇲'
    s = s.replace('  ', ' ')
    s = s.replace('\\\\', newline_symbol)
    s = s.replace('\\%', comment_symbol)
    k = s.split('\n')
    for r in range(len(k)):
        k[r] = k[r].strip()  # Strips all text
    line_merge: List[bool] = []
    for r in range(len(k)):
        sp = k[r].split('%')
        k[r] = sp[0]  # Removes all comments from list
        line_merge.append(len(sp) > 1)
    line_merge.append(False)
    line_merge2: List[bool] = line_merge.copy()
    k.append('')
    for r in range(len(k)):
        if line_merge[r] and not line_merge[r + 1] and k[r + 1] != '':
            line_merge2[r + 1] = True
    for r in range(len(k)):
        line_merge[r] = line_merge[r] or line_merge2[r]
    new_k = []
    j = 0
    merged_str = ''
    while True:  # Merge comment lines
        if not line_merge[j]:
            if merged_str != '':  # Add current merged str
                new_k.append(merged_str)
                merged_str = ''
            new_k.append(k[j])
        else:
            merged_str += k[j]
        if j == len(k) - 1:
            break
        j += 1
    if merged_str != '':
        new_k.append(merged_str)
    k = new_k
    w = []  # Removes duplicates '' lines to single ''
    last = ''
    for j in k:
        if j == '' and j == last:
            pass
        else:
            w.append(j)
        last = j
    if len(w) > 0 and w[-1] == '':  # Removes last space
        w.pop()
    s = '\n'.join(w)
    s = s.replace(comment_symbol, '%').strip()
    s = s.replace(newline_symbol, '\\\\')
    return s


def simple_replace(s: str) -> str:
    """
    Replace simple tokens.

    :param s: Latex string code
    :return: String with replaced items
    """
    for w in REPLACE_SYMBOLS_LIBRARY:
        s = s.replace(w[0], w[1])

    # Replace unique symbols
    s += ' '
    invalid_tag = '⇱SYMBOL_REPLACE_TAG_TOKEN⇲'
    for w in REPLACE_TEX_COMMANDS_LIBRARY:
        word, repl = w
        while True:
            k = s.find(word)
            if k == -1:
                break
            if s[k + len(word)] not in ut.TEX_COMMAND_CHARS:
                s = s[0:k] + repl + s[k + len(word):]
            else:
                s = s[0:k + 1] + invalid_tag + s[k + 1:]  # format ...\\INVALID_TAG...
    s = s[0:len(s) - 1].replace(invalid_tag, '')

    # Replace equation symbols
    tex_tags = ut.find_tex_command_char(s, ut.TEX_EQUATION_CHARS)
    new_s = ''
    k = 0  # Moves through tags
    added_s = False
    for i in range(len(s)):
        if k < len(tex_tags):
            if i < tex_tags[k][1]:
                new_s += s[i]
            elif tex_tags[k][1] <= i < tex_tags[k][2] and not added_s or tex_tags[k][1] == i == tex_tags[k][2]:
                if not added_s:
                    k_s: str = s[tex_tags[k][1]:tex_tags[k][2] + 1]
                    # Replace
                    for j in REPLACE_EQUATION_SYMBOLS_LIBRARY:
                        k_s = k_s.replace(j[0], j[1])
                    new_s += k_s
                added_s = True
            elif tex_tags[k][2] < i < tex_tags[k][3]:
                new_s += s[i]
            elif i == tex_tags[k][3]:  # Advance to other tag
                new_s += s[i]
                k += 1
                added_s = False
        else:
            new_s += s[i]

    return new_s


def process_inputs(s: str) -> str:
    """
    Process inputs, and try to copy the content.

    :param s: Latex string code with inputs
    :return: Text copied with data from inputs
    """
    global _PRINT_LOCATION, _NOT_FOUND_FILES
    symbol = '⇱INPUT_FILE_TAG⇲'
    tx = ''
    while True:
        k = find_str(s, '\\input{')
        if k == -1:
            return s.replace(symbol, '\\input{')
        m = 0
        for j in range(len(s)):
            if s[k + j] == '{':
                m = j
            if s[k + j] == '}':
                tex_file = s[k + m + 1:k + j]
                if '.tex' not in tex_file:
                    tex_file += '.tex'
                if tex_file not in _NOT_FOUND_FILES:
                    if not _PRINT_LOCATION:
                        print(f'Current path location: {os.getcwd()}')
                        _PRINT_LOCATION = True
                    print(f'Detected file {tex_file}:')

                    # Get folder locations
                    folders = _os_listfolder()
                    folders.insert(0, '../')
                    folders.insert(0, './')
                    for f in folders:
                        tx = _load_file(tex_file, f)
                        if tx == _TAG_FILE_ERROR:
                            print(f'\tFile not found in {f}')
                        else:
                            break
                    if tx == _TAG_FILE_ERROR:
                        _NOT_FOUND_FILES.append(tex_file)
                        s = s[:k] + symbol + s[k + m + 1:]
                    else:
                        print('\tFile found and loaded')
                        s = s[:k] + tx + s[k + j + 1:]
                else:
                    s = s[:k] + symbol + s[k + m + 1:]
                break


def remove_commands_char(s: str, chars: List[Tuple[str, str, bool]]) -> str:
    """
    Remove all char commands.

    :param s: Latex string code
    :param chars: Char that define equations [(initial, final, ignore escape), ...]
    :return: Code with removed chars
    """
    tex_tags = ut.find_tex_command_char(s, symbols_char=chars)
    if len(tex_tags) == 0:
        return s
    new_s = ''
    k = 0  # Moves through tags

    for i in range(len(s)):
        if k < len(tex_tags):
            if i < tex_tags[k][0]:
                new_s += s[i]
            elif tex_tags[k][0] <= i < tex_tags[k][3]:
                pass
            elif i == tex_tags[k][3]:  # Advance to other tag
                k += 1
        else:
            new_s += s[i]

    return new_s


def remove_equations(s: str) -> str:
    """
    Remove all equations from a string.

    :param s: Latex string code
    :return: Latex without equation
    """
    return remove_commands_char(s, chars=ut.TEX_EQUATION_CHARS)


def output_text_for_some_commands(s: str, lang: str) -> str:
    """
    Replaces the command for a particular text.

    :param s: Latex string code
    :param lang: Language tag of the code
    :return: Text string or empty if error
    """
    # Stores the commands to be transformed
    # (
    #   command name,
    #   [(argument number, argument is optional), ...],
    #   tag to be replaced,
    #   total commands,
    #   add new line
    # )
    # All *arguments will be formatted using the tag
    commands: List[Tuple[str, List[Tuple[int, bool]], str, int, bool]] = [
        ('caption', [(1, False)], LANG_TEX_TEXT_TAGS.get(lang, 'caption'), 1, True),
        ('href', [(2, False)], LANG_TEX_TEXT_TAGS.get(lang, 'link'), 2, False),
        ('insertimage', [(3, False)], LANG_TEX_TEXT_TAGS.get(lang, 'figure_caption'), 3, True),
        ('insertimage', [(4, False)], LANG_TEX_TEXT_TAGS.get(lang, 'figure_caption'), 4, True),
        ('insertimageboxed', [(4, False)], LANG_TEX_TEXT_TAGS.get(lang, 'figure_caption'), 4, True),
        ('insertimageboxed', [(5, False)], LANG_TEX_TEXT_TAGS.get(lang, 'figure_caption'), 5, True),
        ('subfloat', [(1, True)], LANG_TEX_TEXT_TAGS.get(lang, 'sub_figure_title'), 1, True)
    ]
    new_s = ''

    # Get the commands
    cmd_args = ut.get_tex_commands_args(s)
    for c in cmd_args:
        for cmd in commands:
            if c[0] == cmd[0]:
                _, cmd_args, cmd_tag, total_commands, cmd_newline = cmd
                if len(c) - 1 == total_commands:
                    args = []
                    for j in cmd_args:
                        cmd_argnum, cmd_is_optional = j
                        if len(c) - 1 >= j[0] >= 0 and c[cmd_argnum][1] == cmd_is_optional:
                            argv = c[cmd_argnum][0].replace('\n', ' ')  # Command's argument to process
                            argv = remove_commands_param(argv, lang)  # Remove commands within the argument
                            argv = argv.strip()
                            if argv != '':
                                args.append(argv)
                    if len(args) == len(cmd_args):
                        args.insert(0, FONT_FORMAT_SETTINGS['tex_text_tag_content'])  # Add format text
                        text = cmd_tag.format(*args)
                        new_s += FONT_FORMAT_SETTINGS['tex_text_tag'] + text + FONT_FORMAT_SETTINGS['normal']
                        if cmd_newline:
                            new_s += '\n'

                        break

    return new_s


def remove_commands_param(s: str, lang: str) -> str:
    """
    Remove all commands with params.

    :param s: Latex string code
    :param lang: Language tag of the code
    :return: Code with removed chars
    """
    tex_tags = ut.find_tex_commands(s)
    if len(tex_tags) == 0:
        return s
    new_s = ''
    k = 0  # Moves through tags

    for i in range(len(s)):
        if k < len(tex_tags):
            if i < tex_tags[k][0]:
                new_s += s[i]
            elif i < tex_tags[k][3] + 1:
                pass
            else:  # Advance to other tag
                sub_s = s[tex_tags[k][0]:tex_tags[k][3] + 2]
                if not tex_tags[k][4]:  # If the command does not continue
                    new_s += output_text_for_some_commands(sub_s, lang)
                k += 1
        else:
            new_s += s[i]

    # Replace all command symbols
    parenthesis_open_symbol = '⇱PARENTHESIS_OPEN_SYMBOL⇲'
    parenthesis_close_symbol = '⇱PARENTHESIS_CLOSE_SYMBOL⇲'
    parenthesis_sq_open_symbol = '⇱PARENTHESIS_SQ_OPEN_SYMBOL⇲'
    parenthesis_sq_close_symbol = '⇱PARENTHESIS_SQ_CLOSE_SYMBOL⇲'
    new_s = new_s.replace('\\{', parenthesis_open_symbol)
    new_s = new_s.replace('\\}', parenthesis_close_symbol)
    new_s = new_s.replace('\\[', parenthesis_sq_open_symbol)
    new_s = new_s.replace('\\]', parenthesis_sq_close_symbol)
    new_s = new_s.replace('{', '').replace('}', '')  # .replace('[', '').replace(']', '')
    new_s = new_s.replace(parenthesis_open_symbol, '\\{')
    new_s = new_s.replace(parenthesis_close_symbol, '\\}')
    new_s = new_s.replace(parenthesis_sq_open_symbol, '\\[')
    new_s = new_s.replace(parenthesis_sq_close_symbol, '\\]')

    return new_s


def remove_commands_param_noargv(s: str) -> str:
    """
    Remove all commands without arguments.

    :param s: Latex string code
    :return: Code with removed chars
    """
    tex_tags = ut.find_tex_commands_noargv(s)
    if len(tex_tags) == 0:
        return s
    new_s = ''
    k = 0  # Moves through tags

    for i in range(len(s)):
        if k < len(tex_tags):
            if i < tex_tags[k][0]:
                new_s += s[i]
            elif i < tex_tags[k][1]:
                pass
            else:  # Advance to other tag
                k += 1
        else:
            new_s += s[i]

    return new_s


def unicode_chars_equations(s: str) -> str:
    """
    Converts all ecuations to unicode.

    :param s: Latex string code
    :return: Latex with unicode converted
    """
    tex_tags = ut.find_tex_command_char(s, ut.TEX_EQUATION_CHARS)
    new_s = ''
    k = 0  # Moves through tags
    added_s = False
    for i in range(len(s)):
        if k < len(tex_tags):
            if i < tex_tags[k][1]:
                new_s += s[i]
            elif tex_tags[k][1] <= i < tex_tags[k][2] and not added_s or tex_tags[k][1] == i == tex_tags[k][2]:
                if not added_s:
                    k_s: str = s[tex_tags[k][1]:tex_tags[k][2] + 1]
                    new_s += ut.tex_to_unicode(k_s)
                added_s = True
            elif tex_tags[k][2] < i < tex_tags[k][3]:
                new_s += s[i]
            elif i == tex_tags[k][3]:  # Advance to other tag
                new_s += s[i]
                k += 1
                added_s = False
        else:
            new_s += s[i]

    return new_s


def process_chars_equations(s: str, lang: str, single_only: bool) -> str:
    """
    Process single char equations, removing the symbols.

    :param s: Latex string code
    :param lang: Language tag of the code
    :param single_only: Only process single char equations. If False, replaces the equation by a text-label
    :return: Code without symbols
    """
    tex_tags = ut.find_tex_command_char(s, ut.TEX_EQUATION_CHARS)
    if len(tex_tags) == 0:
        return s
    new_s = ''
    k = 0  # Moves through tags
    eqn_number = 0
    added_equ = False

    for i in range(len(s)):
        if k < len(tex_tags):
            if i < tex_tags[k][0]:
                new_s += s[i]
            elif tex_tags[k][0] <= i < tex_tags[k][1]:
                continue
            elif tex_tags[k][1] <= i <= tex_tags[k][2] and not added_equ:
                equ = s[tex_tags[k][1]:tex_tags[k][2] + 1]
                if len(equ) == 1:
                    new_s += FONT_FORMAT_SETTINGS['equation'] + s[i] + FONT_FORMAT_SETTINGS['normal']
                else:
                    equ = s[tex_tags[k][0]:tex_tags[k][3] + 1]
                    if not single_only:
                        new_s += LANG_TEX_TEXT_TAGS.get(lang, 'multi_char_equ').format(eqn_number)
                        eqn_number += 1
                    else:
                        new_s += equ
                added_equ = True
            elif tex_tags[k][2] < i < tex_tags[k][3]:
                continue
            elif tex_tags[k][3] == i:
                k += 1
                added_equ = False
                continue
        else:
            new_s += s[i]

    return new_s


def strip_punctuation(s: str) -> str:
    """
    Strips punctuation. For example, ``'mycode :'`` to ``'mycode:'``.

    :param s: Latex string code
    :return: Stripped punctuation
    """
    for j in [',', ':', '=', ';', '!', '?', '.']:  # Before
        s = s.replace(f' {j}', j)
    return s


def process_items(s: str) -> str:
    """
    Process itemize and enumerate.

    :param s: Latex string code
    :return: Processed items
    """
    if not ('itemize' in s or 'enumerate' in s):
        return s

    def _get_name(e: str) -> str:
        """
        Get the environment name.

        :param e: Environment name
        :return: New name
        """
        if 'itemize' in e:
            return 'itemize'
        if 'enumerate' in e:
            return 'enumerate'
        return ''

    def _are_item(e: str) -> bool:
        """
        Return true if both are enumerate.

        :param e: Environment name
        :return: True if item
        """
        return e == 'itemize' or e == 'enumerate'

    # First, process the nested ones
    while True:
        equal = False
        envs = ut.find_tex_environments(s)
        for tag in envs:
            t, a, b, c, d, t2, _, item_depth = tag
            t, t2 = _get_name(t), _get_name(t2)
            if t == '' or t2 == '':
                continue
            if t == t2 or _are_item(t) and _are_item(t2):
                s = s[0:a] + _process_item(s[b:c].strip(), t, item_depth) + s[d + 2:]
                equal = True
                break
        if not equal:
            break

    # Not nested
    while True:
        conv = False
        envs = ut.find_tex_environments(s)
        for tag in envs:
            t, a, b, c, d, _, _, _ = tag
            t = _get_name(t)
            if t == '':
                continue
            s = s[0:a] + _process_item(s[b:c].strip(), t) + s[d + 2:]
            conv = True
        if not conv:
            break

    return s


def _process_item(s: str, t: str, depth: int = 0) -> str:
    """
    Process the items.

    :param s: Latex string code
    :param t: Type (enumerate, itemize)
    :param depth: Depth
    :return: Processed items
    """
    assert t in ('enumerate', 'itemize')
    line = '\n' + _TAG_ITEM_SPACE * (3 * depth)

    def _num(x: int) -> str:
        """
        Get number based on the depth.

        :param x: Number
        :return: Number format by depth
        """
        if depth % 5 == 0:
            return f'{line}{x}. '
        elif depth % 5 == 1:
            x = _int_to_alph(x).lower()
            return f'{line}{x}) '
        elif depth % 5 == 2:
            x = _int_to_roman(x).lower()
            return f'{line}{x}. '
        elif depth % 5 == 3:
            x = _int_to_alph(x).upper()
            return f'{line}{x}) '
        elif depth % 5 == 4:
            x = _int_to_roman(x).upper()
            return f'{line}{x}. '

    def _itm() -> str:
        """
        :return: The item string based on depth.
        """
        char = ['-', '•', '◦', '■', '*']
        x = char[depth % 5]
        return f'{line}{x} '

    # Remove optional arguments list
    # print('old', [s])
    if s[0] == '[':
        sqd = 1
        for j in range(1, len(s)):
            if s[j] == '[':
                sqd += 1
            elif s[j] == ']':
                sqd -= 1
            if sqd == 0:
                s = s[j + 1:len(s)].strip()
                break

    # Remove invalid newlines
    s_ = []
    for v in s.split('\n'):
        v = v.strip()
        if v != '':
            s_.append(v)
    s_ = '\n'.join(s_)
    # print('new', [s_])
    s = s_

    if t == 'enumerate':
        s += ' ' * 5
        new_s = ''
        k = 1
        for j in range(len(s) - 5):
            if s[j:j + 5] == '\\item':
                new_s += _num(k)
                j += 5
                k += 1
            else:
                new_s += s[j]
    else:
        new_s = s.replace('\\item', _itm())

    # Last operations
    new_s = new_s.replace('\n\n', '\n').strip(' ')
    return new_s


def _int_to_roman(number: int) -> str:
    """
    Convert a arabic integer number to a roman.

    :param number: Number
    :return: Number in roman
    """
    result = ''
    for (arabic, roman) in _ROMAN_DIGITS:
        (factor, number) = divmod(number, arabic)
        result += roman * factor
    return result


def _int_to_alph(n: int) -> str:
    """
    Integer to a..z.

    :param n: Number
    :return: Number in AABB..
    """
    string = ''
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string
