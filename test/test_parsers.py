"""
PyDetex
https://github.com/ppizarror/pydetex

TEST PARSERS
Test several parsers which perform a single operation.
"""

from test._base import BaseTest
import pydetex
import pydetex.parsers as par


class ParserTest(BaseTest):

    def test_version(self) -> None:
        """
        Configure version.
        """
        self.assertNotEqual(pydetex.version.vernum, '')

    def test_find_str(self) -> None:
        """
        Test find string.
        """
        s = 'This is a latex string, \\textbf{in bold}'
        self.assertEqual(par.find_str(s, '\\textit'), -1)
        self.assertEqual(par.find_str(s, '\\textbf'), 24)
        s2 = """
        This is another example, \\cite{A} thinks that it is good, whereas
        \\citep{K} don't. However, \\cite*{A} is more interesting.
        """
        self.assertEqual(par.find_str(s2, '\\cite'), 34)
        self.assertEqual(par.find_str(s2, '\\cite*'), 109)

    def test_remove_tag(self) -> None:
        """
        Test remove tags.
        """
        self.assertEqual(par.remove_tag('lorem ipsum \\textbf{hi}', 'textbf'), 'lorem ipsum hi')
        self.assertEqual(par.remove_tag('lorem ipsum \\textbf{\\textbf{hi}}', 'textbf'), 'lorem ipsum hi')

    def test_process_cite(self) -> None:
        """
        Removes cites from text.
        """
        self.assertEqual(par.process_cite('hello \\cite{number1,number2} epic'), 'hello [1,2] epic')
        self.assertEqual(par.process_cite('this is \\cite{number1} epic \\cite{number2} and \\cite{number1}'),
                         'this is [1] epic [2] and [1]')
        self.assertEqual(
            par.process_cite('This is another example, \\cite*{Downson} et al. suggests that yes, but \\cite{Epic} not')
            , 'This is another example, [1] et al. suggests that yes, but [2] not')

    def test_process_ref(self) -> None:
        """
        Removes references from text.
        """
        self.assertEqual(par.process_ref('this is a \\ref{myref}'), 'this is a 1')

    def test_remove_comments(self) -> None:
        """
        Removes comments.
        """
        self.assertEqual(par.remove_comments('This is a \% percentage, and % a comment'), 'This is a % percentage, and')
        s = """
        This is a multi-line file, typical from latex% comment
        
        % Typical comment lines.....
        
        Whereas this is another line or paragraph. So boring
        """
        self.assertEqual(par.remove_comments(s),
                         'This is a multi-line file, typical from latex\n\nWhereas this is another line or paragraph. So boring')

    def test_simple_replace(self) -> None:
        """
        Test simple replace format.
        """
        self.assertEqual(par.simple_replace('This is an \item a'), 'This is an - a')
