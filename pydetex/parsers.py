"""
PyDetex
https://github.com/ppizarror/pydetex

PARSERS
Defines parsers, which perform a single task for removal LaTex things.
"""

__all__ = [
    'find_str',
    'FONT_FORMAT_SETTINGS',
    'process_cite',
    'process_inputs',
    'process_labels',
    'process_quotes',
    'process_ref',
    'remove_comments',
    'remove_common_tags',
    'remove_tag',
    'simple_replace'
]

import os
from typing import List, Tuple, Union

TAG_FILE_ERROR = '|FILEERROR|'

NOT_FOUND_FILES = []
PRINT_LOCATION = False

FONT_FORMAT_SETTINGS = {
    'cite': '',
    'normal': '',
    'ref': '',
}


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


def remove_common_tags(s: str) -> str:
    """
    Remove common tags from string.

    :param s: Text
    :return: Text without tags
    """
    for tag in [
        'emph',
        'textbf',
        'textit',
        'texttt',
        'section',
        'subsection',
        'chapter',
        'subsubsection',
        'subsubsubsection',
        'end{itemize}',
        'begin{itemize}'
    ]:
        s = remove_tag(s, tag)
    return s


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
                s = s[:k] + FONT_FORMAT_SETTINGS['cite'] + '[' + c + ']' + FONT_FORMAT_SETTINGS['normal'] + s[
                                                                                                            k + j + 1:]
                break


def process_labels(s: str) -> str:
    """
    Removes labels.

    :param s: String
    :return:
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
                s = s[:k] + FONT_FORMAT_SETTINGS['ref'] + str(r) + FONT_FORMAT_SETTINGS['normal'] + s[k + j + 1:]
                r += 1
                break


def process_quotes(s) -> str:
    """
    Process quotes.

    :param s: String
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

    :param s: Text
    :return: Text without comments
    """
    symbol = '|COMMENTPERCENTAGESYMBOL|'
    s = s.replace('  ', ' ')
    s = s.replace('\\%', symbol)
    k = s.split('\n')
    for r in range(len(k)):
        k[r] = k[r].strip()  # Strips all text
    line_merge = []
    for r in range(len(k)):
        sp = k[r].split('%')
        k[r] = sp[0]  # Removes all comments from list
        line_merge.append(len(sp) > 1)
    line_merge.append(False)
    k.append('')
    for r in range(len(k)):
        if line_merge[r] and not line_merge[r + 1] and k[r + 1] != '':
            line_merge[r + 1] = True
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
    s = s.replace(symbol, '%').strip()
    return s


def simple_replace(s: str) -> str:
    """
    Replace simple tokens.

    :param s: String
    :return: String with replaced items
    """
    library = [
        ('\\item', '-'),
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


def _load_file(f: str, path: str) -> str:
    """
    Try to load a file.

    :param f: Filename
    :param path: Path to look from
    :return: File contents
    """
    try:
        fo = open(path + f, 'r')
        s = '\n'.join(fo.readlines())
        fo.close()
        return s
    except FileNotFoundError:
        return TAG_FILE_ERROR


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


def process_inputs(s: str) -> str:
    """
    Process inputs, and try to copy the content.

    :param s: Text with inputs
    :return: Text copied with data
    """
    global PRINT_LOCATION, NOT_FOUND_FILES
    tx = ''
    while True:
        k = find_str(s, '\\input{')
        if k == -1:
            return s.replace('|INPUTFILETAG', '\\input{')
        m = 0
        for j in range(len(s)):
            if s[k + j] == '{':
                m = j
            if s[k + j] == '}':
                tex_file = s[k + m + 1:k + j]
                if '.tex' not in tex_file:
                    tex_file += '.tex'
                if tex_file not in NOT_FOUND_FILES:
                    if not PRINT_LOCATION:
                        print(f'Current path location: {os.getcwd()}')
                        PRINT_LOCATION = True
                    print(f'Detected file {tex_file}:')

                    # Get folder locations
                    folders = _os_listfolder()
                    folders.insert(0, '../')
                    folders.insert(0, './')
                    for f in folders:
                        tx = _load_file(tex_file, f)
                        if tx == TAG_FILE_ERROR:
                            print(f'\tFile not found in {f}')
                        else:
                            break
                    if tx == TAG_FILE_ERROR:
                        NOT_FOUND_FILES.append(tex_file)
                        s = s[:k] + '|INPUTFILETAG' + s[k + m + 1:]
                    else:
                        print('\tFile found and loaded')
                        s = s[:k] + tx + s[k + j + 1:]
                else:
                    s = s[:k] + '|INPUTFILETAG' + s[k + m + 1:]
                break
