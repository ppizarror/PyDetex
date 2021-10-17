"""
PyDetex
https://github.com/ppizarror/PyDetex

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

    def test_process_labels(self) -> None:
        """
        Removes labels.
        """
        self.assertEqual(par.process_labels('\\section{Research method}\\label{researchmethod}'),
                         '\\section{Research method}')
        self.assertEqual(par.process_labels('This is \\label{epic} a very nice latex'),
                         'This is  a very nice latex')

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
            par.process_cite(
                'This is another example, \\cite*{Downson} et al. suggests that yes, but \\cite{Epic} not'),
            'This is another example, [1] et al. suggests that yes, but [2] not')

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

        # Comments right to text
        s = """
        Web of Science, % https://webofknowledge.com/
        Scopus, % https://www.scopus.com/
        IEEE/IET Xplore, % https://ieeexplore.ieee.org/
        Science Direct, % https://uchile.idm.oclc.org/login?url=https://www.sciencedirect.com/
        """
        self.assertEqual(par.remove_comments(s), 'Web of Science, Scopus, IEEE/IET Xplore, Science Direct,')

        # Comments at start
        s = """% !TeX spellcheck = en_US

        \section{Introduction}
        
        Architectural floor plans are documents that result from an iterative design, planning, and engineering pro"""
        self.assertEqual(par.remove_comments(s),
                         '\\section{Introduction}\n\nArchitectural floor plans are documents that result from an iterative design, planning, and engineering pro')

    def test_simple_replace(self) -> None:
        """
        Test simple replace format.
        """
        self.assertEqual(par.simple_replace('This is an \\item a'), 'This is an - a')
        self.assertEqual(par.simple_replace('This is a example formula $\\alpha\longrightarrow\\beta+1$'),
                         'This is a example formula $α⟶β+1$')

    def test_remove_common_tags(self) -> None:
        """
        Remove common tags.
        """
        self.assertEqual(par.simple_replace('This is an \\item a'), 'This is an - a')

    def test_process_quotes(self) -> None:
        """
        Test quotes.
        """
        self.assertEqual(par.process_quotes('This is \\quotes{a quoted} string'), 'This is "a quoted" string')

    def test_parse_inputs(self) -> None:
        """
        Parse inputs.
        """
        self.assertEqual(par._NOT_FOUND_FILES, [])
        self.assertEqual(par.process_inputs('This loads a \\input{latex} or \\input{} epic'),
                         'This loads a \\input{latex} or \\input{} epic')
        self.assertEqual(par._NOT_FOUND_FILES, ['latex.tex', '.tex'])
        self.assertEqual(par.process_inputs('This loads a \\input{latex} or \\input{} epic'),
                         'This loads a \\input{latex} or \\input{} epic')
        self.assertEqual(par.process_inputs('This loads a \\input{data/simple} epic'),
                         'This loads a this is a simple file epic')

    def test_remove_commands_char(self) -> None:
        """
        Remove commands char.
        """
        s = 'This is a $command$!'
        self.assertEqual(par.remove_commands_char(s, '$'), 'This is a !')
        s = 'This is a $command\$ but this does not delete$!'
        self.assertEqual(par.remove_commands_char(s, '$'), 'This is a !')
        s = 'This is a $command!'
        self.assertEqual(par.remove_commands_char(s, '$'), s)

        s = 'This is a$$ command!'
        self.assertEqual(par.remove_commands_char(s, '$'), 'This is a command!')

        s = 'This is a $comman$ and $this should be removed too$!'
        self.assertEqual(par.remove_commands_char(s, '$'), 'This is a  and !')

    def test_remove_commands(self) -> None:
        """
        Remove commands.
        """
        s = 'This \\f{must be removed} yes!'
        self.assertEqual(par.remove_commands_param(s), 'This  yes!')
        self.assertEqual(par.remove_commands_param(''), '')
        s = 'This \\texttt{\insertimage{nice}{1}}no'
        self.assertEqual(par.remove_commands_param(s), 'This no')
        s = '\\insertimage[\label{epic}]{delete this}'
        self.assertEqual(par.remove_commands_param(s), '')
        s = 'Very\\insertimage[\label{epic}]{delete this} Epic'
        self.assertEqual(par.remove_commands_param(s), 'Very Epic')
        s = 'Very\\insertimage[\label{epic}]{delete this} Epic \\not yes'
        self.assertEqual(par.remove_commands_param(s), 'Very Epic \\not yes')
        s = 'Ni\\f       {}ce'
        self.assertEqual(par.remove_commands_param(s), 'Nice')
        s = 'Ni\\f   \n    [][][]{}ce'
        self.assertEqual(par.remove_commands_param(s), 'Nice')

    def test_remove_commands_noargv(self) -> None:
        """
        Remove commands without arguments.
        """
        s = 'This\\image remove'
        self.assertEqual(par.remove_commands_param_noargv(s), 'This remove')
        s = 'This inserts an \\insertimage[width=1\linewidth]'
        self.assertEqual(par.remove_commands_param_noargv(s), 'This inserts an \\insertimage[width=1]')
        s = 'This \\delete'
        self.assertEqual(par.remove_commands_param_noargv(s), 'This ')
        s = 'This \\delete '
        self.assertEqual(par.remove_commands_param_noargv(s), 'This  ')
        s = '\\delete yes'
        self.assertEqual(par.remove_commands_param_noargv(s), ' yes')
        s = '\\delete'
        self.assertEqual(par.remove_commands_param_noargv(s), '')
