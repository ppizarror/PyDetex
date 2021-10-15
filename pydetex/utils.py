"""
PyDetex
https://github.com/ppizarror/pydetex

UTILS
Several text utils.
"""

__all__ = [
    'apply_tag_between_inside',
    'apply_tag_tex_commands',
    'apply_tag_tex_commands_no_argv',
    'Button',
    'check_repeated_words',
    'detect_language',
    'find_tex_command_char',
    'find_tex_commands',
    'find_tex_commands_noargv',
    'get_diff_startend_word',
    'get_language_tag',
    'IS_OSX',
    'RESOURCES_PATH',
    'split_tags',
    'syntax_highlight',
    'validate_float',
    'validate_int'
]

# langdetect supports:
# af, ar, bg, bn, ca, cs, cy, da, de, el, en, es, et, fa, fi, fr, gu, he,
# hi, hr, hu, id, it, ja, kn, ko, lt, lv, mk, ml, mr, ne, nl, no, pa, pl,
# pt, ro, ru, sk, sl, so, sq, sv, sw, ta, te, th, tl, tr, uk, ur, vi, zh-cn, zh-tw
import langdetect

import nltk
import os
import platform

# noinspection PyPackageRequirements
from iso639 import Lang
# noinspection PyPackageRequirements
from iso639.exceptions import InvalidLanguageValue

from nltk.corpus import stopwords as _stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
from typing import List, Tuple, Optional, Union
from warnings import warn

from pydetex._fonts import FONT_TAGS as _FONT_TAGS

# Resources path
# Set resouces path
__actualpath = str(os.path.abspath(os.path.dirname(__file__))).replace('\\', '/') + '/'
RESOURCES_PATH = __actualpath + 'res/'

# Check OS
IS_OSX = platform.system() == 'Darwin'

# Import Button widget
if IS_OSX:
    from tkmacosx import Button
else:
    from tkinter import Button

_HAS_NLTK = False

# Check if stopwods exists
try:
    _stopwords.words('english')
    _HAS_NLTK = True
except LookupError:
    nltk.download('stopwords')

# Re-try to download
try:
    _stopwords.words('english')
    _HAS_NLTK = True
except LookupError:
    pass

# Valid command chars
VALID_TEX_COMMAND_CHARS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
                           'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
                           'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                           'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
                           'W', 'X', 'Y', 'Z']


def detect_language(s: str) -> str:
    """
    Detects languages.

    :param s: String
    :return: Detected language
    """
    if s == '':
        return '–'
    try:
        return langdetect.detect(s)
    except langdetect.lang_detect_exception.LangDetectException:  # No features in text
        return '–'


def get_language_tag(s: str) -> str:
    """
    Returns a language name from its tag.

    :param s: Language tag
    :return: Language name
    """
    try:
        return Lang(s).name
    except InvalidLanguageValue:
        return 'Unknown'


def get_diff_startend_word(original: str, new: str) -> Tuple[str, str]:
    """
    Return the difference of the word from start and end, for example:

    original XXXwordYY
    new         word
    diff = (XXX, YY)

    :param original: Original word
    :param new: New word
    :return: Diff word
    """
    pos: int = original.find(new)
    if pos == -1:
        return '', ''
    return original[0:pos], original[pos + len(new):len(original)]


def check_repeated_words(
        s: str,
        lang: str,
        min_chars: int,
        window: int,
        stopwords: bool,
        stemming: bool,
        ignore: Optional[List[str]] = None,
        remove_tokens: Optional[List[str]] = None,
        font_tag_format: str = '',
        font_param_format: str = '',
        font_normal_format: str = '',
        tag: str = 'repeated'
) -> str:
    """
    Check repeated words.

    :param s: Text
    :param lang: Language code
    :param min_chars: Min chars to accept
    :param window: Window words span to check
    :param stopwords: Use stopwords
    :param stemming: Use stemming
    :param ignore: Ignore a list of words
    :param remove_tokens: Remove keys before verify repeat
    :param font_tag_format: Tag's format
    :param font_param_format: Param's format
    :param font_normal_format. Normal's format
    :param tag: Tag's name
    :return: Text with repeated words marked
    """
    assert isinstance(window, int) and window > 1
    assert isinstance(min_chars, int) and min_chars >= 1

    if not ignore:
        ignore = []
    if not remove_tokens:
        remove_tokens = []

    # Check languages
    available_langs = {
        'ar': 'arabic',
        'da': 'danish',
        'de': 'german',
        'en': 'english',
        'es': 'spanish',
        'fi': 'finnish',
        'fr': 'french',
        'hu': 'hungarian',
        'it': 'italian',
        'nb': 'norwegian',
        'nd': 'norwegian',
        'nl': 'dutch',
        'nn': 'norwegian',
        'no': 'norwegian',
        'pt': 'portuguese',
        'ro': 'romanian',
        'ru': 'russian',
        'sv': 'swedish'
    }
    if lang in available_langs.keys() and _HAS_NLTK:
        stop = _stopwords.words(available_langs[lang])
        stemmer = SnowballStemmer(available_langs[lang])
    else:
        if not _HAS_NLTK:
            warn('nltk library does not exist. Check for your internet connection in order to use this feature')
        return s

    tokenizer = RegexpTokenizer(r'\w+')

    ignored_words = []
    # Apply filters to ignored words
    for w in ignore:
        if stemming:
            w = stemmer.stem(w)
        if stopwords and w in stop:
            w = ''
        if w == '':
            continue
        ignored_words.append(w)

    # Add space to newline
    newline_format = '      \n'
    s = s.replace('\n', newline_format)

    # Separeate words
    wordswin = []  # Stores the words
    words = s.split(' ')
    new_s = []

    for w in words:
        original_w = w

        # Remove tokens
        if len(remove_tokens) > 0:
            for rt in remove_tokens:
                w = w.replace(rt, '')

        # If command in word
        if '\\' in w:
            w = ''

        # Apply filters
        if len(w) <= min_chars:
            w = ''
        if w != '':
            w = tokenizer.tokenize(w)[0]
        if stemming:
            w = stemmer.stem(w)
        if stopwords and w in stop:
            w = ''

        # Check if word is ignored
        if w in ignored_words:
            w = ''

        # Check if the word exist on list
        if w in wordswin and w != '':
            ww = wordswin[::-1].index(w) + 1
            stemmed_word = tokenizer.tokenize(original_w)[0]
            diff_word = get_diff_startend_word(original_w, stemmed_word)
            if diff_word == ('', ''):
                stemmed_word = original_w
            original_w = f'{diff_word[0]}{font_tag_format}<{tag}:{ww}>' \
                         f'{font_param_format}{stemmed_word}' \
                         f'{font_tag_format}</{tag}>{font_normal_format}{diff_word[1]}'

        # Push the new word
        wordswin.append(w)
        if len(wordswin) > window:
            wordswin.pop(0)

        # Append word
        new_s.append(original_w)

    # Return string with repeated format
    out_s = ' '.join(new_s)
    out_s = out_s.replace(newline_format, '\n')
    return out_s


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
    return s if IS_OSX else '  {0}  '.format(s)


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
        if not r and s[i] == symbols_char[0] and (not ignore_escape or ignore_escape and s[i - 1] != '\\'):
            a = i
            r = True
        # Close
        elif r and s[i] == symbols_char[1] and (not ignore_escape or ignore_escape and s[i - 1] != '\\'):
            r = False
            found.append((a - 1, i - 1))

    return tuple(found)


def apply_tag_between_inside(
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
                     x       x x  x
    Example: This is \aCommand{nice}... => ((8,16,18,21), ...)

    :param s: Latex code
    :return: Tuple if found codes
    """
    found = []
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
