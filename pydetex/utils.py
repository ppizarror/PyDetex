"""
PyDetex
https://github.com/ppizarror/pydetex

UTILS
Several text utils.
"""

__all__ = [
    'check_repeated_words',
    'detect_language',
    'get_language_tag',
    'split_tags'
]

from langdetect import detect as _detect
# langdetect supports:
# af, ar, bg, bn, ca, cs, cy, da, de, el, en, es, et, fa, fi, fr, gu, he,
# hi, hr, hu, id, it, ja, kn, ko, lt, lv, mk, ml, mr, ne, nl, no, pa, pl,
# pt, ro, ru, sk, sl, so, sq, sv, sw, ta, te, th, tl, tr, uk, ur, vi, zh-cn, zh-tw

import nltk
from nltk.corpus import stopwords as _stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import RegexpTokenizer

from typing import List, Tuple, Optional

# Check if stopwods exists
try:
    _stopwords.words('english')
except LookupError:
    nltk.download('stopwords')

_ISO_639_LANGS = {
    'aa': 'Afar',
    'ab': 'Abkhaz',
    'ae': 'Avestan',
    'af': 'Afrikaans',
    'ak': 'Akan',
    'am': 'Amharic',
    'an': 'Aragonese',
    'ar': 'Arabic',
    'as': 'Assamese',
    'av': 'Avaric',
    'ay': 'Aymara',
    'az': 'Azerbaijani',
    'ba': 'Bashkir',
    'be': 'Belarusian',
    'bg': 'Bulgarian',
    'bh': 'Bihari',
    'bi': 'Bislama',
    'bm': 'Bambara',
    'bn': 'Bengali',
    'bo': 'Tibetan',
    'br': 'Breton',
    'bs': 'Bosnian',
    'ca': 'Catalan',
    'ce': 'Chechen',
    'ch': 'Chamorro',
    'co': 'Corsican',
    'cr': 'Cree',
    'cs': 'Czech',
    'cu': 'Old Church Slavonic',
    'cv': 'Chuvash',
    'cy': 'Welsh',
    'da': 'Danish',
    'de': 'German',
    'dv': 'Divehi; Maldivian;',
    'dz': 'Dzongkha',
    'ee': 'Ewe',
    'el': 'Greek, Modern',
    'en': 'English',
    'eo': 'Esperanto',
    'es': 'Spanish',
    'et': 'Estonian',
    'eu': 'Basque',
    'fa': 'Persian',
    'ff': 'Fula',
    'fi': 'Finnish',
    'fj': 'Fijian',
    'fo': 'Faroese',
    'fr': 'French',
    'fy': 'Western Frisian',
    'ga': 'Irish',
    'gd': 'Scottish Gaelic',
    'gl': 'Galician',
    'gn': 'Guaraní',
    'gu': 'Gujarati',
    'gv': 'Manx',
    'ha': 'Hausa',
    'he': 'Hebrew (modern)',
    'hi': 'Hindi',
    'ho': 'Hiri Motu',
    'hr': 'Croatian',
    'ht': 'Haitian',
    'hu': 'Hungarian',
    'hy': 'Armenian',
    'hz': 'Herero',
    'ia': 'Interlingua',
    'id': 'Indonesian',
    'ie': 'Interlingue',
    'ig': 'Igbo',
    'ii': 'Nuosu',
    'ik': 'Inupiaq',
    'io': 'Ido',
    'is': 'Icelandic',
    'it': 'Italian',
    'iu': 'Inuktitut',
    'ja': 'Japanese',
    'jv': 'Javanese',
    'ka': 'Georgian',
    'kg': 'Kongo',
    'ki': 'Kikuyu, Gikuyu',
    'kj': 'Kwanyama, Kuanyama',
    'kk': 'Kazakh',
    'kl': 'Kalaallisut',
    'km': 'Khmer',
    'kn': 'Kannada',
    'ko': 'Korean',
    'kr': 'Kanuri',
    'ks': 'Kashmiri',
    'ku': 'Kurdish',
    'kv': 'Komi',
    'kw': 'Cornish',
    'ky': 'Kirghiz, Kyrgyz',
    'la': 'Latin',
    'lb': 'Luxembourgish',
    'lg': 'Luganda',
    'li': 'Limburgish',
    'ln': 'Lingala',
    'lo': 'Lao',
    'lt': 'Lithuanian',
    'lu': 'Luba-Katanga',
    'lv': 'Latvian',
    'mg': 'Malagasy',
    'mh': 'Marshallese',
    'mi': 'Māori',
    'mk': 'Macedonian',
    'ml': 'Malayalam',
    'mn': 'Mongolian',
    'mr': 'Marathi',
    'ms': 'Malay',
    'mt': 'Maltese',
    'my': 'Burmese',
    'na': 'Nauru',
    'nb': 'Norwegian Bokmål',
    'nd': 'North Ndebele',
    'ne': 'Nepali',
    'ng': 'Ndonga',
    'nl': 'Dutch',
    'nn': 'Norwegian Nynorsk',
    'no': 'Norwegian',
    'nr': 'South Ndebele',
    'nv': 'Navajo, Navaho',
    'ny': 'Chichewa',
    'oc': 'Occitan',
    'oj': 'Ojibwe, Ojibwa',
    'om': 'Oromo',
    'or': 'Oriya',
    'os': 'Ossetian, Ossetic',
    'pa': 'Panjabi, Punjabi',
    'pi': 'Pāli',
    'pl': 'Polish',
    'ps': 'Pashto, Pushto',
    'pt': 'Portuguese',
    'qu': 'Quechua',
    'rm': 'Romansh',
    'rn': 'Kirundi',
    'ro': 'Romanian, Moldavan',
    'ru': 'Russian',
    'rw': 'Kinyarwanda',
    'sa': 'Sanskrit',
    'sc': 'Sardinian',
    'sd': 'Sindhi',
    'se': 'Northern Sami',
    'sg': 'Sango',
    'si': 'Sinhala, Sinhalese',
    'sk': 'Slovak',
    'sl': 'Slovene',
    'sm': 'Samoan',
    'sn': 'Shona',
    'so': 'Somali',
    'sq': 'Albanian',
    'sr': 'Serbian',
    'ss': 'Swati',
    'st': 'Southern Sotho',
    'su': 'Sundanese',
    'sv': 'Swedish',
    'sw': 'Swahili',
    'ta': 'Tamil',
    'te': 'Telugu',
    'tg': 'Tajik',
    'th': 'Thai',
    'ti': 'Tigrinya',
    'tk': 'Turkmen',
    'tl': 'Tagalog',
    'tn': 'Tswana',
    'to': 'Tonga',
    'tr': 'Turkish',
    'ts': 'Tsonga',
    'tt': 'Tatar',
    'tw': 'Twi',
    'ty': 'Tahitian',
    'ug': 'Uighur, Uyghur',
    'uk': 'Ukrainian',
    'ur': 'Urdu',
    'uz': 'Uzbek',
    've': 'Venda',
    'vi': 'Vietnamese',
    'vo': 'Volapük',
    'wa': 'Walloon',
    'wo': 'Wolof',
    'xh': 'Xhosa',
    'yi': 'Yiddish',
    'yo': 'Yoruba',
    'za': 'Zhuang, Chuang',
    'zh': 'Chinese',
    'zu': 'Zulu'
}


def detect_language(s: str) -> str:
    """
    Detects languages.

    :param s: String
    :return: Detected language
    """
    if s == '':
        return '–'
    return _detect(s)


def get_language_tag(s: str) -> str:
    """
    Returns a language name from its tag.

    :param s: Language tag
    :return: Language name
    """
    if s not in _ISO_639_LANGS.keys():
        return 'Unknown'
    else:
        return _ISO_639_LANGS[s]


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
        font_normal_format: str = ''
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
        stop = _stopwords.words(available_langs[lang])
        stemmer = SnowballStemmer(available_langs[lang])
    else:
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
            original_w = '{2}<repeated:{0}>{3}{1}{2}</repeated>{4}' \
                         ''.format(ww, original_w, font_tag_format, font_param_format,
                                   font_normal_format)

        # Push the new word
        wordswin.append(w)
        if len(wordswin) > window:
            wordswin.pop(0)

        # Append word
        new_s.append(original_w)

    # Return string with repeated format
    return ' '.join(new_s)


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
        # print(tagged_lines)

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
