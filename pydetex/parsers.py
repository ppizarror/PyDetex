"""
PyDetex
https://github.com/ppizarror/PyDetex

PARSERS
Defines parsers, which perform a single task for removal LaTex things.
"""

__all__ = [
    'find_str',
    'process_cite',
    'process_ref',
    'remove_comments',
    'remove_tag',
    'simple_replace'
]

from typing import List, Tuple, Union


def _find_str(s: str, char: str) -> int:
    """
    Finds a sequence within a string, and returns the position. If not exists, returns -1.

    :param s: String
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


def find_str(s: str, char: Union[str, List[str], Tuple[str, ...]]) -> int:
    """
    Finds a sequence within a string, and returns the position. If not exists, returns -1.

    :param s: String
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

    :param s: String
    :param tagname: Tag code
    :return: String without tags
    """
    tagname = '\\' + tagname
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
                s = s[:k] + s[k + len(tagname) + 1:k + j] + s[k + j + 1:]
                break


def process_cite(s: str) -> str:
    """
    Transforms all cites to a text-based with numbers. For example,
    'This is from \\cite{Pizarro}' to 'This is from [1].

    :param s: String
    :return:
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
                s = s[:k] + '[' + c + ']' + s[k + j + 1:]
                break


def process_ref(s) -> str:
    """
    Process references, same as cites, replaces by numbers.

    :param s: String
    :return: String with numbers instead of references.
    """
    r = 1
    while True:
        k = find_str(s, '\\ref{')
        if k == -1:
            return s
        for j in range(len(s)):
            if s[k + j] == '}':
                s = s[:k] + str(r) + s[k + j + 1:]
                r += 1
                break


def remove_comments(s: str) -> str:
    """
    Remove comments from text.

    :param s: Text
    :return: Text without comments
    """
    symbol = '|COMMENTPERCENTAGESYMBOL|'
    s = s.replace('  ', ' ').replace(' %', '%')
    s = s.replace('\\%', symbol)
    k = s.split('\n')
    for r in range(len(k)):
        k[r] = k[r].strip()  # Strips all text
    for r in range(len(k)):
        k[r] = k[r].split('%')[0]  # Removes all comments from list
    w = []  # Removes duplicates '' lines to single ''
    last = ''
    for j in k:
        if j == '' and j == last:
            pass
        else:
            w.append(j)
        last = j
    if w[-1] == '':  # Removes last space
        w.pop()
    s = '\n'.join(w)
    s = s.replace(symbol, '%')
    return s


def simple_replace(s: str) -> str:
    """
    Replace simple tokens.

    :param s: String
    :return: String with replaced items
    """
    library = [
        ('\item', '-'),
        ('--', '–'),
        ('\\alpha', 'α'),
        ('\\beta', 'β'),
        ('\\gamma', 'γ'),
        ('\\delta', 'δ'),
        ('\\epsilon', 'ε'),
        ('\\\\', '\n'),
        ('\\ ', ' '),
    ]
    for w in library:
        s = s.replace(w[0], w[1])
    return s
