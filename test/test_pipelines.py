"""
PyDetex
https://github.com/ppizarror/PyDetex

TEST PIPELINES
Test the pipelines.
"""

from test._base import BaseTest
import pydetex.pipelines as pip
import pydetex.parsers as par
import os


class ParserTest(BaseTest):

    def test_simple(self) -> None:
        """
        Test simple pipeline.
        """
        s = 'Table \\ref{tab:review-rulebased} details the reviewed rule-based ' \
            'methods within floor plan recognition, considering the datasets ' \
            'used (Table \\ref{tab:databases}) and the four categories of tasks,' \
            ' such as (1) \\textit{Graphics separation}, (2) \\textit{Pattern ' \
            'recognition}, (3) \\textit{Vectorization}, and (4) \\textit{Structural modeling}.'
        self.assertEqual(
            pip.simple(s, show_progress=True),
            'Table 1 details the reviewed rule-based methods within floor plan '
            'recognition, considering the datasets used (Table 2) and the four '
            'categories of tasks, such as (1) Graphics separation, (2) Pattern '
            'recognition, (3) Vectorization, and (4) Structural modeling.')

        s = 'aa\\begin{document}x\\end{document}'
        self.assertEqual(pip.simple(s, show_progress=True), 'x')

        s = '$a$a\\def\\a{a}\\a'
        self.assertEqual(pip.simple(s, show_progress=True, replace_defs=True), 'aaa')

        # New lines
        s = 'New space \\ and line \\\\Epic'
        self.assertEqual(pip.simple(s), 'New space and line\nEpic')

        # Empty
        self.assertEqual(pip.simple(''), '')

        # Test with invalid last char
        self.assertEqual(pip.simple('This is epic\\\nThis is epic\\'), 'This is epic\nThis is epic')

        # Test replacers
        s = 'This is a \\Thetamagic but also \\Theta is not or \\Theta\\Epic or \\Theta\n sad'
        t = 'This is a \\Thetamagic but also Θ is not or Θ\Epic or Θ\nsad'
        self.assertEqual(pip.simple(s), t)

        # Check files
        example_files = [
            ('data/example_simple_itemize.txt', 'data/example_simple_itemize_output.txt'),
            ('data/example_simple_comments.txt', 'data/example_simple_comments_output.txt')
        ]
        for f in example_files:
            self.assertEqual(pip.simple(par._load_file_search(f[0])),
                             par._load_file_search(f[1]))

    def test_strict(self) -> None:
        """
        Strict pipeline.
        """
        s = 'This contains \\insertimageanother{\label{1}}{2}{3}commands, but must be removed!\\'
        self.assertEqual(pip.strict(s, show_progress=True),
                         'This contains commands, but must be removed!')

        s = 'This \\quoteepic{code removed!}is removed\\totally. Not epic \\cite{nice}'
        self.assertEqual(pip.strict(s), 'This is removed. Not epic [1]')

        s = 'This \\quoteepic{code removed!}is removed \\totally nice. Not epic \\cite{nice}'
        self.assertEqual(pip.strict(s), 'This is removed nice. Not epic [1]')

        # Empty
        self.assertEqual(pip.strict('', show_progress=True), '')

        s = '\DeclareUnicodeCharacter{2292}{\ensuremath{\ensuremath{\\to}}}'
        self.assertEqual(pip.strict(s), '')

        s = """% !TeX spellcheck = en_US
        \\begin{table*}[t]

        \centering
        % \\vspace{\\baselineskip}
        \\begin{tablenotes}
            \item[a] Graphics separation
            \item[b] Door/Window/Furniture/Others
            \item[c] OCR or Dimensions were recognized
            \item[d] Vectorization
            \item[e] Modeling (Graph, other)
        \end{tablenotes}
        \label{tab:review-rulebased}
        \end{threeparttable}
        \end{table*}
        """
        self.assertEqual(
            pip.strict(s, show_progress=True),
            '- [a] Graphics separation\n- [b] Door/Window/Furniture/Others\n- [c'
            '] OCR or Dimensions were recognized\n- [d] Vectorization\n- [e] Mod'
            'eling (Graph, other)')

        # Check files
        example_files = [
            ('data/example_tables_strict.txt', 'data/example_tables_strict_output.txt'),
            ('data/example_placeholder.txt', 'data/example_placeholder_output.txt'),
            ('data/example_simple_figure_caption.txt', 'data/example_simple_figure_caption_output.txt'),
            ('data/example_simple_cite.txt', 'data/example_simple_cite_output.txt')
        ]
        for f in example_files:
            self.assertEqual(pip.strict(par._load_file_search(f[0])),
                             par._load_file_search(f[1]))

        # Test remove environments
        self.assertEqual(pip.strict(par._load_file_search('data/example_complex_envs.txt'),
                                    show_progress=True).strip(),
                         par._load_file_search('data/example_complex_envs_output.txt'))

        # Exclusive tests
        test_complex = False
        if 'GITHUB' in os.environ:
            return
        example_files = [
            ('data/example_complex_template.txt', 'data/example_complex_template_output.txt')
        ]
        if not test_complex:
            example_files = []
        for f in example_files:
            self.assertEqual(pip.strict(par._load_file_search(f[0])),
                             par._load_file_search(f[1]))
