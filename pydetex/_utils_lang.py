"""
PyDetex
https://github.com/ppizarror/PyDetex

UTILS LANG
Language utils.
"""

__all__ = [
    'check_repeated_words',
    'detect_language',
    'Dictionary',
    'get_diff_startend_word',
    'get_language_name',
    'tokenize'
]

# langdetect supports:
# af, ar, bg, bn, ca, cs, cy, da, de, el, en, es, et, fa, fi, fr, gu, he,
# hi, hr, hu, id, it, ja, kn, ko, lt, lv, mk, ml, mr, ne, nl, no, pa, pl,
# pt, ro, ru, sk, sl, so, sq, sv, sw, ta, te, th, tl, tr, uk, ur, vi, zh-cn, zh-tw
import langdetect

import json
import os
import urllib.error

# noinspection PyPackageRequirements
from iso639 import Lang
# noinspection PyPackageRequirements
from iso639.exceptions import InvalidLanguageValue

from nltk.stem import SnowballStemmer
from nltk.tokenize import RegexpTokenizer as _RegexpTokenizer
from typing import List, Tuple, Optional, Dict

# Dictionaries
from bs4 import BeautifulSoup
from urllib.request import urlopen

# Resources path
__actualpath = str(os.path.abspath(os.path.dirname(__file__))).replace('\\', '/') + '/'

# Load all stopwords
with open(__actualpath + 'res/' + 'stopwords.json', encoding='UTF-8') as json_data:
    _STOPWORDS = json.load(json_data)

# Tokenizer
TOKENIZER = _RegexpTokenizer(r'\w+')

# Dicts
_EDUCALINGO = ('bn', 'de', 'en', 'es', 'fr', 'hi', 'it', 'ja', 'jv', 'ko', 'mr',
               'ms', 'pl', 'pt', 'ro', 'ru', 'ta', 'tr', 'uk', 'zh')

# Enhanced lang names
_LANG_NAMES = {
    'bn': [('af', 'আফ্রিকান'), ('ar', 'আরবী'), ('bn', 'বাংলা'), ('de', 'জার্মান'), ('el', 'গ্রীক্\u200c'),
           ('en', 'ইংরেজী'), ('es', 'স্পেনীয়'), ('fr', 'ফরাসি'), ('hi', 'হিন্দি'), ('it', 'ইতালীয়'), ('ja', 'জাপানি'),
           ('jv', 'জাভানি'), ('ko', 'কোরিয়ান'), ('mr', 'মারাঠি'), ('ms', 'মালে'), ('no', 'নরওয়েজীয়'),
           ('pl', 'পোলীশ'), ('pt', 'পর্তুগীজ'), ('ro', 'রোমানীয়'), ('ru', 'রুশ'), ('sv', 'সুইডিশ'), ('ta', 'তামিল'),
           ('tr', 'তুর্কী'), ('uk', 'ইউক্রেনীয়'), ('vi', 'ভিয়েতনামিয়'), ('zh', 'চীনা')],
    'de': [('af', 'Afrikaans'), ('ar', 'Arabisch'), ('bn', 'Bengalisch'), ('de', 'Deutsch'), ('el', 'Griechisch'),
           ('en', 'Englisch'), ('es', 'Spanisch'), ('fr', 'Französisch'), ('hi', 'Hindi'), ('it', 'Italienisch'),
           ('ja', 'Japanisch'), ('jv', 'Javanisch'), ('ko', 'Koreanisch'), ('mr', 'Marathi'), ('ms', 'Malaysisch'),
           ('no', 'Norwegisch'), ('pl', 'Polnisch'), ('pt', 'Portugiesisch'), ('ro', 'Rumänisch'), ('ru', 'Russisch'),
           ('sv', 'Schwedisch'), ('ta', 'Tamil'), ('tr', 'Türkisch'), ('uk', 'Ukrainisch'), ('vi', 'Vietnamesisch'),
           ('zh', 'Chinesisch')],
    'en': [('af', 'Afrikaans'), ('ar', 'Arabic'), ('bn', 'Bengali'), ('de', 'German'), ('el', 'Greek'),
           ('en', 'English'), ('es', 'Spanish'), ('fr', 'French'), ('hi', 'Hindi'), ('it', 'Italian'),
           ('ja', 'Japanese'), ('jv', 'Javanese'), ('ko', 'Korean'), ('mr', 'Marathi'), ('ms', 'Malay'),
           ('no', 'Norwegian'), ('pl', 'Polish'), ('pt', 'Portuguese'), ('ro', 'Romanian'), ('ru', 'Russian'),
           ('sv', 'Swedish'), ('ta', 'Tamil'), ('tr', 'Turkish'), ('uk', 'Ukrainian'), ('vi', 'Vietnamese'),
           ('zh', 'Chinese')],
    'es': [('af', 'Afrikáans'), ('ar', 'Árabe'), ('bn', 'Bengalí'), ('de', 'Alemán'), ('el', 'Griego'),
           ('en', 'Inglés'), ('es', 'Español'), ('fr', 'Francés'), ('hi', 'Hindi'), ('it', 'Italiano'),
           ('ja', 'Japonés'), ('jv', 'Javanés'), ('ko', 'Coreano'), ('mr', 'Maratí'), ('ms', 'Malayo'),
           ('no', 'Noruego'), ('pl', 'Polaco'), ('pt', 'Portugués'), ('ro', 'Rumano'), ('ru', 'Ruso'), ('sv', 'Sueco'),
           ('ta', 'Tamil'), ('tr', 'Turco'), ('uk', 'Ucraniano'), ('vi', 'Vietnamita'), ('zh', 'Chino')],
    'fr': [('af', 'Afrikaans'), ('ar', 'Arabe'), ('bn', 'Bengali'), ('de', 'Allemand'), ('el', 'Grec'),
           ('en', 'Anglais'), ('es', 'Espagnol'), ('fr', 'Français'), ('hi', 'Hindi'), ('it', 'Italien'),
           ('ja', 'Japonais'), ('jv', 'Javanais'), ('ko', 'Coréen'), ('mr', 'Marathi'), ('ms', 'Malaisien'),
           ('no', 'Norvégien'), ('pl', 'Polonais'), ('pt', 'Portugais'), ('ro', 'Roumain'), ('ru', 'Russe'),
           ('sv', 'Suédois'), ('ta', 'Tamoul'), ('tr', 'Turc'), ('uk', 'Ukrainien'), ('vi', 'Vietnamien'),
           ('zh', 'Chinois')],
    'hi': [
        
    ]
}


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
        lang = langdetect.detect(s)
        if lang == 'zh-cn' or lang == 'zh-tw':
            lang = 'zh'
        return lang
    except langdetect.lang_detect_exception.LangDetectException:  # No features in text
        return '–'


def get_language_name(tag: str) -> str:
    """
    Returns a language name from its tag.

    :param tag: Language tag
    :return: Language name
    """
    try:
        return Lang(tag).name
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


class Dictionary(object):
    """
    Dictionary. Support synonyms, antonyms and definitions from some languages.
    """

    _cached_soups: Dict[str, 'BeautifulSoup']  # Stores cached web
    _langs: Dict[str, Tuple[bool, bool]]  # synonyms, definition, translation
    _test_cached_file: str = ''  # If defined, loads that file instead

    def __init__(self) -> None:
        """
        Constructor.
        """
        self._langs = {  # iso 639 codes
            'en': (True, True),
            'es': (True, True)
        }
        self._cached_soups = {}
        self._test_cached_file = ''

    @staticmethod
    def _process(word: str) -> str:
        """
        Process a given word.

        :param word: Word
        :return: Word without invalid chars
        """
        s = ''.join(i for i in word if not i.isdigit())  # remove numbers
        s = tokenize(s).lower()  # tokenize
        s = s.replace(' ', '').replace('\n', '')  # remove spaces
        return s

    def _bsoup(self, link: str, encoding: str = 'utf-8') -> Optional['BeautifulSoup']:
        """
        Returns a parsed web.

        :param link: Link
        :param encoding: Web encoding
        :return: Parsed web. None if error
        """
        if self._test_cached_file != '':  # Load test file
            f = open(self._test_cached_file)
            data = ''.join(f.readlines())
            f.close()
            return BeautifulSoup(data, 'html.parser')
        bs_keys = list(self._cached_soups.keys())
        if link in bs_keys:
            return self._cached_soups[link]
        try:
            data = str(urlopen(link).read().decode(encoding))
        except urllib.error.HTTPError:
            return None
        bs = BeautifulSoup(data, 'html.parser')
        self._cached_soups[link] = bs
        if len(bs_keys) >= 50:
            del self._cached_soups[bs[0]]
        return bs

    def synonym(self, lang: str, word: str) -> List[str]:
        """
        Finds a synonym for a given word.

        :param lang: Lang code
        :param word: Word to retrieve
        :return: Synonyms list
        """
        words = []
        word = self._process(word)
        if lang not in self._langs.keys():
            return words
        if lang in _EDUCALINGO:
            bs = self._bsoup(f'https://educalingo.com/en/dic-{lang}/{word}')
            if bs is None:
                return words
            results = [i for i in bs.find_all('div', {'class': 'contenido_sinonimos_antonimos0'})]
            if len(results) > 0:
                results = results[0]
            else:
                return words
            for j in results.findAll('a'):
                words.append(j.get('title').strip())
        return words

    def definition(self, lang: str, word: str) -> str:
        """
        Finds a definition for a given word.

        :param lang: Lang code
        :param word: Word to retrieve
        :return: Definition
        """
        words = ''
        word = self._process(word)
        if lang not in self._langs.keys():
            return words
        if lang in _EDUCALINGO:
            bs = self._bsoup(f'https://educalingo.com/en/dic-{lang}/{word}')
            if bs is None:
                return words

            # Definition
            results = [i for i in bs.find_all('div', {
                'id': 'significado_de'})]
            if len(results) > 0:
                results = results[0]
            else:
                return words
            words = results.text

            # Wikipedia
            results = [i for i in bs.find_all('span', {
                'id': 'wiki_introduccion'})]
            if len(results) > 0:
                results = results[0]
            else:
                return words
            words += '\n\n' + results.text

        return words.strip()

    def translate(self, lang: str, word: str) -> List[Tuple[str, str, str]]:
        """
        Translate a word.
l
        :param lang: Lang tag
        :param word: Word to translate
        :return: List of (Lang name, Lang tag, translated word)
        """
        words = []
        word = self._process(word)
        if lang not in self._langs.keys():
            return words
        if lang in _EDUCALINGO:
            bs = self._bsoup(f'https://educalingo.com/fr/dic-{lang}/{word}')
            if bs is None:
                return words
            results = [i for i in bs.find_all('div', {'class': 'traduccion0'})]
            if len(results) == 0:
                return words
            for j in results:
                lang_tag = j.get('id')
                lang_name = j.find_all('h4', {'class', 'traductor'})
                if len(lang_name) != 1:
                    continue
                lang_name = lang_name[0].find_all('strong', {})
                if len(lang_name) != 1:
                    continue
                lang_name = lang_name[0].text.strip().capitalize()

                # Find non-links
                lang_nonlink = j.find_all('span', {'class': 'negro'})
                if len(lang_nonlink) == 1:
                    words.append((lang_name, lang_tag, lang_nonlink[0].text.strip()))
                    continue

                # Find links
                lang_link = j.find_all('strong', {})
                if len(lang_link) != 2:
                    continue
                lang_link = lang_link[1].find_all('a', {})
                if len(lang_link) == 1:
                    words.append((lang_name, lang_tag, lang_link[0].text.strip()))

        return words
