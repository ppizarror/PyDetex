"""
PyDetex
https://github.com/ppizarror/PyDetex

UTILS LANG
Language utils.
"""

__all__ = [
    'check_repeated_words',
    'complete_langs_dict',
    'detect_language',
    'get_diff_startend_word',
    'get_language_name',
    'get_phrase_from_cursor',
    'get_word_from_cursor',
    'LangTexTextTags',
    'make_stemmer',
    'tokenize'
]

# langdetect supports:
# af, ar, bg, bn, ca, cs, cy, da, de, el, en, es, et, fa, fi, fr, gu, he,
# hi, hr, hu, id, it, ja, kn, ko, lt, lv, mk, ml, mr, ne, nl, no, pa, pl,
# pt, ro, ru, sk, sl, so, sq, sv, sw, ta, te, th, tl, tr, uk, ur, vi, zh-cn, zh-tw
import langdetect

import json
import os

# noinspection PyProtectedMember
from PyMultiDictionary._utils import tokenize, get_language_name
from nltk.stem import SnowballStemmer
from typing import List, Tuple, Optional, Dict
from warnings import warn

# Resources path
__actualpath = str(os.path.abspath(os.path.dirname(__file__))).replace('\\', '/') + '/'

# Load all stopwords
with open(__actualpath + 'res/' + 'stopwords.json', encoding='UTF-8') as json_data:
    _STOPWORDS = json.load(json_data)

_AVAILABLE_STEMMER_LANGS: Dict[str, str] = {
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


class LangTexTextTags(object):
    """
    Stores the tex tags for several commands.
    """

    _lang: Dict[str, Dict[str, str]]

    def __init__(self) -> None:
        """
        Constructor.
        """
        self._lang = {
            'en': {
                'caption': 'CAPTION: {0}',
                'citeauthor_multiple': 'authors',
                'citeauthor_single': 'author',
                'figure_caption': 'FIGURE_CAPTION: {0}',
                'link': 'LINK: {0}',
                'multi_char_equ': 'EQUATION_{0}',
                'sub_figure_title': 'SUB_FIGURE TITLE: {0}'
            },
            'es': {
                'caption': 'LEYENDA: {0}',
                'citeauthor_multiple': 'autores',
                'citeauthor_single': 'autor',
                'figure_caption': 'LEYENDA_FIGURA: {0}',
                'link': 'ENLACE: {0}',
                'multi_char_equ': 'ECUACIÓN_{0}',
                'sub_figure_title': 'TÍTULO SUB_FIGURA: {0}'
            }
        }
        complete_langs_dict(self._lang)

    def get(self, lang: str, tag: str) -> str:
        """
        Retrieves a language tag value.

        :param lang: Language
        :param tag: Tag to retrieve
        :return: Value of the language's tag
        """
        if lang not in self._lang.keys():
            lang = 'en'
        if tag not in self._lang[lang].keys():
            raise ValueError(f'Lang {lang} tag {tag} does not exist')
        return self._lang[lang][tag]


def complete_langs_dict(lang: Dict[str, Dict[str, str]]) -> None:
    """
    Completes a language dict. Assumes ``'en'`` is the main language.

    :param lang: Language dict
    """
    for k in lang.keys():
        if k == 'en':
            continue
        for t in lang['en'].keys():
            if t not in lang[k]:
                error = f'Language entry "{t}" on lang "{k}" does not exist'
                warn(error)
                lang[k][t] = lang['en'][t]


def detect_language(s: str) -> str:
    """
    Detects languages.

    :param s: String
    :return: Detected language
    """
    if s == '':
        return '–'
    try:
        lang = langdetect.detect(s)
        if lang == 'zh-cn' or lang == 'zh-tw':
            lang = 'zh'
        return lang
    except langdetect.lang_detect_exception.LangDetectException:  # No features in text
        return '–'


def get_diff_startend_word(original: str, new: str) -> Tuple[str, str]:
    """
    Return the difference of the word from start and end, for example:

    .. code-block:: none

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


def make_stemmer(lang: str) -> Optional['SnowballStemmer']:
    """
    Returns a stemmer.

    :param lang: Lang code
    :return: Stemmer or None if not available
    """
    if lang in _AVAILABLE_STEMMER_LANGS.keys():
        return SnowballStemmer(_AVAILABLE_STEMMER_LANGS[lang])
    return None


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
    :param font_normal_format: Normal's format
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
    if lang in _AVAILABLE_STEMMER_LANGS.keys():
        stop = _STOPWORDS[lang]
        stemmer = make_stemmer(lang)
    else:
        return s

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
            w = tokenize(w)
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
            stemmed_word = tokenize(original_w)
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


def get_word_from_cursor(s: str, pos: int) -> Tuple[str, int, int]:
    """
    Return the word from a string on a given cursor.

    :param s: String
    :param pos: Position to check the string
    :return: Word, position start, position end
    """
    assert 0 <= pos < len(s)
    pos += 1
    s = ' ' + s
    p = 0

    # Check if pos is an empty character, find the following word
    if s[pos].strip() == '':
        found = False
        for k in range(pos, len(s)):  # First
            if s[k].strip() != '' and not found:
                p = k
                found = True
            elif s[k].strip() == '' and found:
                return s[p:k].strip(), p, k - 1

    else:
        for w in range(pos):  # Find prev
            j = pos - w - 1
            if s[j].strip() == '':
                p = j
                break
            elif s[j].strip() == '>':
                p = j + 1
                break
        for j in range(pos + 1, len(s)):  # Find next
            if s[j].strip() in ('', '<'):
                return s[p:j].strip(), p, j - 1

    return '', -1, -1


def get_phrase_from_cursor(s: str, pos_init: int, pos_end: int) -> str:
    """
    Get a phrase from the cursor. It tries to retrieve the entire words selected.

    :param s: String
    :param pos_init: Initial position
    :param pos_end: End position
    :return: Retrieved word
    """
    assert pos_init <= pos_end

    # Get first word
    s0, i, _ = get_word_from_cursor(s, pos_init)
    j = i

    if s[pos_end].strip() == '':  # Is empty, find the previous word
        for k in range(1, pos_end):
            _k = pos_end - k
            if s[_k].strip() != '':
                j = _k + 1
                break
    else:
        _, _, j = get_word_from_cursor(s, pos_end)

    if j <= i:
        return s0

    return s[i:j]
