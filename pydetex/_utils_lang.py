"""
PyDetex
https://github.com/ppizarror/pydetex

UTILS LANG
Language utils.
"""

__all__ = [
    'check_repeated_words',
    'detect_language',
    'get_diff_startend_word',
    'get_language_tag',
    'tokenize'
]

# langdetect supports:
# af, ar, bg, bn, ca, cs, cy, da, de, el, en, es, et, fa, fi, fr, gu, he,
# hi, hr, hu, id, it, ja, kn, ko, lt, lv, mk, ml, mr, ne, nl, no, pa, pl,
# pt, ro, ru, sk, sl, so, sq, sv, sw, ta, te, th, tl, tr, uk, ur, vi, zh-cn, zh-tw
import langdetect

import json
import os

# noinspection PyPackageRequirements
from iso639 import Lang
# noinspection PyPackageRequirements
from iso639.exceptions import InvalidLanguageValue

from nltk.stem import SnowballStemmer
from nltk.tokenize import RegexpTokenizer as _RegexpTokenizer
from typing import List, Tuple, Optional

# Resources path
__actualpath = str(os.path.abspath(os.path.dirname(__file__))).replace('\\', '/') + '/'

# Load all stopwords
with open(__actualpath + 'res/' + 'stopwords.json', encoding='UTF-8') as json_data:
    _STOPWORDS = json.load(json_data)

# Tokenizer
TOKENIZER = _RegexpTokenizer(r'\w+')


def tokenize(s: str) -> str:
    """
    Tokenize a given word.

    :param s: Word
    :return: Tokenized word
    """
    try:
        return TOKENIZER.tokenize(s)[0]
    except IndexError:
        pass
    return s


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
    if lang in available_langs.keys():
        stop = _STOPWORDS[lang]
        stemmer = SnowballStemmer(available_langs[lang])
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
