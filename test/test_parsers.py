"""
PyDetex
https://github.com/ppizarror/PyDetex

TEST PARSERS
Test several parsers which perform a single operation.
"""

from test._base import BaseTest
import pydetex
import pydetex.parsers as par
import pydetex.utils as ut


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
        s = 'hello \\cite{number1,number2} epic'
        self.assertEqual(par.replace_pydetex_tags(par.process_cite(s)),
                         'hello [1, 2] epic')
        s = 'this is \\cite{number1} epic \\cite{number2} and \\cite{number1}'
        self.assertEqual(par.replace_pydetex_tags(par.process_cite(s)),
                         'this is [1] epic [2] and [1]')
        s = 'This is another example, \\cite*{Downson} et al. suggests that yes, but \\cite{Epic} not'
        self.assertEqual(
            par.replace_pydetex_tags(par.process_cite(s)),
            'This is another example, [1] et al. suggests that yes, but [2] not')
        # Test multiple cites
        s = 'This is an example \\cite{b} \\cite{a,    b,    c    , d, e}'
        self.assertEqual(par.replace_pydetex_tags(par.process_cite(s)), 'This is an example [1] [1-5]')
        self.assertEqual(par.replace_pydetex_tags(par.process_cite(s, compress_cite=False)),
                         'This is an example [1] [1, 2, 3, 4, 5]')
        self.assertEqual(par.replace_pydetex_tags(par.process_cite(s, sort_cites=False)),
                         'This is an example [1] [2, 1, 3-5]')

    def test_process_citeauthor(self) -> None:
        """
        Removes citeauthor from text.
        """
        s = 'hello \\citeauthor{number1,number2} epic'
        self.assertEqual(par.replace_pydetex_tags(par.process_citeauthor(par.process_cite(s), 'en')),
                         'hello [authors] epic')
        s = 'hello \\citeauthor{number1} epic'
        self.assertEqual(par.replace_pydetex_tags(par.process_citeauthor(par.process_cite(s), 'en')),
                         'hello [author] epic')

    def test_process_ref(self) -> None:
        """
        Removes references from text.
        """
        self.assertEqual(par.process_ref('this is a \\ref{myref}'), 'this is a 1')
        self.assertEqual(par.process_ref('this is a \\ref{myref} and \\ref*{myref}'), 'this is a 1 and 1')

    def test_remove_common_tags(self) -> None:
        """
        Remove common tags.
        """
        self.assertEqual(par.remove_common_tags('this is \\hl{a}'), 'this is a')
        self.assertEqual(par.remove_common_tags('this is \\textsuperscript{\\hl{nice}}'), 'this is nice')

    def test_remove_comments(self) -> None:
        """
        Removes comments.
        """
        self.assertEqual(par.remove_comments('This is a \% percentage, and % a comment'),
                         'This is a ⇱COMMENT_PERCENTAGE_SYMBOL⇲ percentage, and')
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
        self.assertEqual(
            par.remove_comments(s),
            '\\section{Introduction}\n\nArchitectural floor plans are documents that result from an iterative design, '
            'planning, and engineering pro')

        # Comment right to newline
        s = 'Therefore, the scope was restricted to analyzing vector-based CAD files or retrieving individual elements ' \
            'from plans with a simple format. \\\\% Therefore, the scope was restricted to analyze vector-based CAD files,' \
            ' or retrieving individual elements from plans with a simple format. \\'
        t = 'Therefore, the scope was restricted to analyzing vector-based CAD files or retrieving individual elements ' \
            'from plans with a simple format. \\\\'
        self.assertEqual(par.remove_comments(s), t)

    def test_simple_replace(self) -> None:
        """
        Test simple replace format.
        """
        self.assertEqual(par.simple_replace('This is an \\itemBad a'), 'This is an \\itemBad a')
        self.assertEqual(par.simple_replace('This is a example formula $\\alpha\longrightarrow\\beta+1$'),
                         'This is a example formula $α⟶β+1$')
        self.assertEqual(par.simple_replace('This is \\alphaNot but \\alpha'),
                         'This is \\alphaNot but α')
        self.assertEqual(par.simple_replace('This is a $x_0$ and $x^2$'), 'This is a $x₀$ and $x²$')
        self.assertEqual(par.simple_replace('The following example $\\alpha_0+\\beta^2=0$'),
                         'The following example $α₀+β²=0$')
        self.assertEqual(par.simple_replace('This is a $x_0$ and \(x^2\)'), 'This is a $x₀$ and \(x²\)')
        self.assertEqual(par.simple_replace('This is $\\alpha$'), 'This is $α$')

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
        self.assertEqual(par.process_inputs('This loads a \\input{data/simple} epic', clear_not_found_files=True),
                         'This loads a this is a simple file epic')

    def test_remove_commands_char(self) -> None:
        """
        Remove commands char.
        """
        s = 'This is a $command$!'
        self.assertEqual(par.remove_equations(s), 'This is a !')
        s = 'This is a $command\$ but this does not delete$!'
        self.assertEqual(par.remove_equations(s), 'This is a !')
        s = 'This is a $command!'
        self.assertEqual(par.remove_commands_char(s, chars=ut.TEX_EQUATION_CHARS), s)
        s = 'This is a$$ command!'
        self.assertEqual(par.remove_equations(s), 'This is a command!')
        s = 'This is a $comman$ and $this should be removed too$!'
        self.assertEqual(par.remove_equations(s), 'This is a  and !')
        s = 'This is a \(comman\) and \(this should be removed too\)!'
        self.assertEqual(par.remove_equations(s), 'This is a  and !')
        s = 'This is a \(\) and $X$!'
        self.assertEqual(par.remove_equations(s), 'This is a  and !')
        s = '$X$\(y\)$alpha$$$$$$key$'
        self.assertEqual(par.remove_equations(s), '')

    def test_remove_commands(self) -> None:
        """
        Remove commands.
        """
        s = 'This \\f{must be removed} yes!'
        self.assertEqual(par.remove_commands_param(s, 'en'), 'This  yes!')
        self.assertEqual(par.remove_commands_param('', 'en'), '')
        s = 'This \\texttt{\insertimage{nice}{1}}no'
        self.assertEqual(par.remove_commands_param(s, 'en'), 'This no')
        s = '\\insertimage[\label{epic}]{delete this}'
        self.assertEqual(par.remove_commands_param(s, 'en'), '')
        s = 'Very\\insertimage[\label{epic}]{delete this} Epic'
        self.assertEqual(par.remove_commands_param(s, 'en'), 'Very Epic')
        s = 'Very\\insertimage[\label{epic}]{delete this} Epic \\not yes'
        self.assertEqual(par.remove_commands_param(s, 'en'), 'Very Epic \\not yes')
        s = 'Ni\\f       {}ce'
        self.assertEqual(par.remove_commands_param(s, 'en'), 'Nice')
        s = 'Ni\\f   \n    [][][]{}ce'
        self.assertEqual(par.remove_commands_param(s, 'en'), 'Nice')
        s = '\caption {thus, the analysis \{cannot\} be based \mycommand{only} using {nice} symbols}'
        self.assertEqual(par.replace_pydetex_tags(par.remove_commands_param(s, 'en')).strip(),
                         'CAPTION: thus, the analysis \{cannot\} be based  using nice symbols')

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

    def test_process_chars_equations(self) -> None:
        """
        Process single char equations.
        """
        # Test single only
        s = 'This code does not \$contain any equation$!!'
        self.assertEqual(par.process_chars_equations(s, 'en', single_only=True), s)
        s = 'This code must be $x$ processed!!'
        self.assertEqual(par.process_chars_equations(s, 'en', single_only=True), 'This code must be x processed!!')
        s = par.simple_replace('$\\alpha$-shape is really nice')
        self.assertEqual(par.process_chars_equations(s, 'en', single_only=True), 'α-shape is really nice')
        s = 'Because $x$ no lower needs any other supervision as $y$ or $z$ in \$30 or \$40$$'
        self.assertEqual(par.process_chars_equations(s, 'en', single_only=True),
                         'Because x no lower needs any other supervision as y or z in \$30 or \$40')
        s = 'This code $with several chars$ should not be removed'
        self.assertEqual(par.process_chars_equations(s, 'en', single_only=True), s)
        s = 'This code must be $$ processed!!'
        self.assertEqual(par.process_chars_equations(s, 'en', single_only=True), 'This code must be  processed!!')
        s = 'an $x$$y$$z$'
        self.assertEqual(par.process_chars_equations(s, 'en', single_only=True), 'an xyz')

        # Test multiple
        s = 'This code $with several chars$ should not be removed'
        self.assertEqual(par.process_chars_equations(s, 'en', single_only=False),
                         'This code EQUATION_0 should not be removed')
        s = 'This code \(with several chars\) should not be removed'
        self.assertEqual(par.process_chars_equations(s, 'en', single_only=False),
                         'This code EQUATION_0 should not be removed')
        s = 'This $equation 0$ and \$equation $equation 1$ must by replaced'
        self.assertEqual(par.process_chars_equations(s, '-', single_only=False),
                         'This EQUATION_0 and \$equation EQUATION_1 must by replaced')

        # Test environments
        s = """My new equation:
        \\begin{equation}
        a+b
        \\end{equation}"""
        self.assertEqual(par.process_chars_equations(s, '-', single_only=False),
                         'My new equation:\n        EQUATION_0')

    def test_output_text_for_some_commands(self) -> None:
        """
        Test output text for some commands, like caption or subfigure.
        """

        def out(s_: str) -> str:
            """
            Call method.
            """
            return par.replace_pydetex_tags(par.output_text_for_some_commands(s_, 'en')).strip()

        s = """
        \\begin{figure}
            \centering
            \\reflectbox{%
            \includegraphics[width=0.5\textwidth]{gull}}
            \caption   {A picture of the same gull\nlooking the other way!}
            \caption[invalid]
        \end{figure}
        """
        self.assertEqual(out(s), 'CAPTION: A picture of the same gull looking the other way!')

        # Custom template
        s = '\\insertimage[]{imagefile}{width=5cm}{}'
        self.assertEqual(out(s), '')
        s = '\\insertimage[]{imagefile}{width=5cm}{e}'
        self.assertEqual(out(s), 'FIGURE_CAPTION: e')
        s = '\\insertimage{imagefile}{width=5cm}{e}'
        self.assertEqual(out(s), 'FIGURE_CAPTION: e')
        s = '\\insertimageboxed{imagefile}{width=5cm}{0.5}{legend}'
        self.assertEqual(out(s), 'FIGURE_CAPTION: legend')
        s = 'Nice\n\insertimage[\label{unetmodel}]{unet_compressed}{width=\linewidth}{A U-Net model.}'
        self.assertEqual(out(s), 'FIGURE_CAPTION: A U-Net model.')

        # Test other
        s = 'This is a \\href{https://google.com}{A link}'
        self.assertEqual(out(s), 'LINK: A link')
        s = '\section{a}\section*{a}]'
        self.assertEqual(out(s), 'a\n\na')
        s = '\\texttt{nice!} and \emph{nice!}'
        self.assertEqual(out(s), 'nice!nice!')
        s = '\\textit{\href{a}{link}}'
        self.assertEqual(out(s), 'LINK: link')

        # Test MakeUppercase
        s = '\\MakeUppercase{this is a Test}'
        self.assertEqual(out(s), 'THIS IS A TEST')
        s = '\\uppercase{this is a Test}'
        self.assertEqual(out(s), 'THIS IS A TEST')
        s = '\\MakeLowercase{THIS is a Test}'
        self.assertEqual(out(s), 'this is a test')
        s = '\\lowercase{THIS is a Test}'
        self.assertEqual(out(s), 'this is a test')

        # Test quotes
        s = '\quotes{a quoted}'
        self.assertEqual(out(s), '"a quoted"')
        s = '\enquote{a quoted}'
        self.assertEqual(out(s), '"a quoted"')
        s = '\quotes{\href{a}{link}}'
        self.assertEqual(out(s), '"LINK: link"')
        s = '\doublequotes{\href{a}{link}}'
        self.assertEqual(out(s), '"LINK: link"')

        # Test acronym
        s = '\\ac{XYZ}'
        self.assertEqual(out(s), 'XYZ')
        s = '\\acf{XYZ}'
        self.assertEqual(out(s), 'XYZ')
        s = '\\acs{XYZ}'
        self.assertEqual(out(s), 'XYZ')
        s = '\\acl{XYZ}'
        self.assertEqual(out(s), 'XYZ')

    def test_unicode_chars_equations(self) -> None:
        """
        Test unicode char equations.
        """
        s = 'This is my $\\alpha^2 \cdot \\alpha^{2+3} \equiv \\alpha^7$ equation'
        self.assertEqual(par.unicode_chars_equations(s), 'This is my $α² ⋅ α²⁺³ ≡ α⁷$ equation')
        s = 'This is my $x$ equation'
        self.assertEqual(par.unicode_chars_equations(s), 'This is my $x$ equation')
        s = 'This is my $\{a+b\}=min\{t\}$ equation'
        self.assertEqual(par.replace_pydetex_tags(par.unicode_chars_equations(s)),
                         'This is my ${a+b}=min{t}$ equation')
        s = 'This is my $$ equation'
        self.assertEqual(par.unicode_chars_equations(s), 'This is my $$ equation')
        s = 'This is my \\begin{align}\\alpha^2 \cdot \\alpha^{2+3} \equiv \\alpha^7\\end{align} equation'
        self.assertEqual(par.unicode_chars_equations(s), 'This is my \\begin{align}α² ⋅ α²⁺³ ≡ α⁷\end{align} equation')

    def test_strip_punctuation(self) -> None:
        """
        Test strip punctuation.
        """
        self.assertEqual(par.strip_punctuation('Or , for example : yes !'), 'Or, for example: yes!')

    def test_process_items(self) -> None:
        """
        Test process items.
        """
        s = '\\begin{itemize}\item a \item b\\begin{itemize}\item a \item b\end{itemize}\end{itemize}'
        self.assertEqual(par.replace_pydetex_tags(par.process_items(s, lang='en')),
                         '\n-  a \n-  b\n   •  a\n   •  b')

        s = """\\begin{itemize}[font=\\bfseries]
           \item As shown in Figure \\ref{fignumber}
           \item Proposed
        \end{itemize}"""
        self.assertEqual(par.replace_pydetex_tags(par.process_items(s, lang='en')),
                         '\n-  As shown in Figure \n-  Proposed')

        s = """\\begin{enumerate}
            \\item a
            \\begin{enumerate}
                \\item a
                \\item b
                    \\begin{enumerate}
                        \\item a
                        \\item b
                        \\item c
                        \\begin{enumerate}[font=\\bfseries]
                            \\item a
                            \\item b
                            \\item c
                            \\begin{enumerate}[[font=\\bfseries]]
                                \\item a
                                \\item b
                                \\item c
                            \\end{enumerate}
                        \\end{enumerate}
                    \\end{enumerate}
            \\end{enumerate}
            \\item c
            \\begin{itemize}
                \\item a
                \\item b
                \\item c
            \\end{itemize}
            \\item epic
        \\end{enumerate}
        """

        t = par.replace_pydetex_tags(par.process_items(s, lang='en'))
        self.assertEqual(
            t, '\n1. a\n   a) a\n   b) b\n      i. a\n      ii. b\n      iii. c\n'
               '         A) a\n         B) b\n         C) c\n            I. a\n '
               '           II. b\n            III. c\n2. c\n   •  a\n   •  b\n  '
               ' •  c\n3. epic\n        ')

        self.assertEqual(par._process_item('', ''), '')

        s = """
        \\begin{enumerate}
        \item b
        \end{enumerate}
        
        \\begin{itemize}
        \item a
        \\end{itemize}
        
        \\begin{tablenotes}
        Note: Res - Resolution in pixels (px).
        \\end{tablenotes}
        
        epic
        """
        self.assertEqual(
            par.replace_pydetex_tags(par.process_items(s, lang='en')),
            '\n        \n1. b\n        \n        \n-  a\n        \n        Note:'
            ' Res - Resolution in pixels (px).\n        \n        epic\n        '
        )

        # Multiple non-nested
        s = """
        \\begin{enumerate}
            \item a
        \end{enumerate}
        \\begin{enumeratebf}
            \item a
        \end{enumeratebf}
        \\begin{enumerate}
            \item b
        \end{enumerate}
        \\begin{enumerate}
            \item a
        \end{enumerate}
        \\begin{enumerate}
            \item b
            \\begin{itemize}
                \item c
            \end{itemize}
            \item d
        \end{enumerate}
        \\begin{nice}
        \\end{nice}
        """
        self.assertEqual(
            ut.find_tex_environments(s),
            (('enumerate', 9, 26, 55, 68, '', 0, 0),
             ('enumeratebf', 79, 98, 127, 142, '', 0, 0),
             ('enumerate', 153, 170, 199, 212, '', 0, 0),
             ('enumerate', 223, 240, 269, 282, '', 0, 0),
             ('itemize', 343, 358, 395, 406, 'enumerate', 1, 1),
             ('enumerate', 293, 310, 437, 450, '', 0, 0),
             ('nice', 461, 473, 482, 490, '', 0, -1))
        )
        self.assertEqual(
            par.replace_pydetex_tags(par.process_items(s, lang='en')).strip(),
            '1. a\n        \n1. a\n        \n1. b\n        \n1. a\n        \n1. '
            'b\n   •  c\n2. d\n        \\begin{nice}\n        \\end{nice}')

    def test_remove_environments(self) -> None:
        """
        Remove environment test.
        """
        s = 'e\\begin{nice}x\\end{nice}p\\begin{y}z\\end{y}i\\begin{k}z\\end{k}c'
        self.assertEqual(par.remove_environments(s), s)
        self.assertEqual(par.remove_environments(s, ['y']), 'e\\begin{nice}x\end{nice}pi\\begin{k}z\end{k}c')
        self.assertEqual(par.remove_environments(s, ['y', 'nice']), 'epi\\begin{k}z\end{k}c')
        self.assertEqual(par.remove_environments(s, ['y', 'nice', 'k']), 'epic')

        s = """The following is a tikz figure, and must be removed:
        
        \\begin{tikzpicture}[line cap=round, line join=round, >=triangle 45,
                     x=4.0cm, y=1.0cm, scale=1]
          \draw [->,color=black] (-0.1,0) -- (2.5,0);
          \\foreach \\x in {1,2}
          \draw [shift={(\\x,0)}, color=black] (0pt,2pt)
              -- (0pt,-2pt) node [below] {\\footnotesize $\\x$};
          \draw [color=black] (2.5,0) node [below] {$x$};
          \draw [->,color=black] (0,-0.1) -- (0,4.5);
           \\foreach \y in {1,2,3,4}
          \draw [shift={(0,\y)}, color=black] (2pt,0pt)
              -- (-2pt,0pt) node[left] {\\footnotesize $\y$};
          \draw [color=black] (0,4.5) node [right] {$y$};
          \draw [color=black] (0pt,-10pt) node [left] {\\footnotesize $0$};
          \draw [domain=0:2.2, line width=1.0pt] plot (\\x,{(\\x)^2});
          \clip(0,-0.5) rectangle (3,5);
          \draw (2,0) -- (2,4);
          \\foreach \i in {1,...,\\thehigher}
          \draw [fill=black,fill opacity=0.3, smooth,samples=50] ({1+(\i-1)/\\thehigher},{(1+(\i)/\\thehigher)^2})
                  --({1+(\i)/\\thehigher},{(1+(\i)/\\thehigher)^2})
                  --  ({1+(\i)/\thehigher},0)
                  -- ({1+(\i-1)/\\thehigher},0)
                  -- cycle;
        \end{tikzpicture}and it was removed!!
        
        \\begin{epic}
        But this should not be removed!
        \\end{epic}"""
        self.assertEqual(
            par.remove_environments(s),
            'The following is a tikz figure, and must be removed:\n        \n   '
            '     and it was removed!!\n        \n        \\begin{epic}\n       '
            ' But this should not be removed!\n        \\end{epic}')

    def test_process_def(self) -> None:
        """
        Process defs test.
        """
        par._DEFS.clear()

        s = 'This is my \\def\\code {epic!} but yes \\def\\a{} epic'
        self.assertEqual(par.process_def(s), 'This is my  but yes  epic')
        self.assertEqual(len(par._DEFS), 2)
        self.assertEqual(par._DEFS['\\code'], 'epic!')

        s = """
        \def\\underline#1{\\relax\ifmmode\@@underline{#1}\else $\@@underline{\hbox{#1}}\m@th$\\relax\\fi}
        \def\@greek#1{%
            \ifcase#1%
                \or $\\alpha$%
                \or $\\beta$%
                \or $\gamma$%
                \or $\delta$%
                \or $\epsilon$%
                \or $\zeta$%
                \or $\eta$%
                \or $\\theta$%
                \or $\iota$%
                \or $\kappa$%
                \or $\lambda$%
                \or $\mu$%
                \or $\\nu$%
                \or $\\xi$%
                \or $o$%
                \or $\pi$%
                \or $\\rho$%
                \or $\sigma$%
                \or $\\tau$%
                \or $\\upsilon$%
                \or $\phi$%
                \or $\chi$%
                \or $\psi$%
                \or $\omega$%
            \\fi%
        }
        not epic
        """
        self.assertEqual(par.process_def(s).strip(), 'not epic')
        self.assertEqual(len(par._DEFS), 0)

        s = '\\def\\mycommand{epic}This is really \mycommand yes'
        self.assertEqual(par.process_def(s, replace=True), 'This is really epic yes')
        s = '\\def\\mycommand{epic}This is really \mycommand'
        self.assertEqual(par.process_def(s, replace=True), 'This is really epic')

        s = 'a\\def\e{e}'
        self.assertEqual(par.process_def(s), 'a')
        s = '\\def\e{e}'
        self.assertEqual(par.process_def(s), '')
        s = '\\def\e{e}\\def\p{p}\\def\i       {i}\\def\c\n{c}\e\p\i\c'
        self.assertEqual(par.process_def(s, replace=True), 'epic')
        s = '\epic \def\\a{a} \\nice \\item \\a\\a\\a not \\b'
        self.assertEqual(par.process_def(s, replace=True), '\epic  \\nice \\item aaa not \\b')
        s = 'a\\def\e{e} jjajjajaja'
        self.assertEqual(par.process_def(s, replace=True), 'a jjajjajaja')

        s = """
        \\begin{itemize}[font=\\bfseries]
            \item a
        \end{itemize}
        
        a\def\\a{epic}
        jejeje \\a
        """
        self.assertEqual(
            par.process_def(s, replace=True).strip(),
            '\\begin{itemize}[font=\\bfseries]\n            \item a\n        \\end{itemize}\n        \n'
            '        a\n        jejeje epic'
        )

        # Invalid defs
        s = '\def\\a{a} and \def\\b{b} and \\def   \nc{c} and \\defee\\d{d}: \\a\\b\\c\\d.'
        self.assertEqual(par.process_def(s, replace=True), ' and  and  and \defee\d{d}: ab\c\d.')

        # Def with commands
        s = '\def\\a{\\textsuperscript{a}nice!!} epic \\a'
        self.assertEqual(par.process_def(s, replace=True), ' epic anice!!')

    def test_begin_document(self) -> None:
        """
        Test begin document parser.
        """
        s = '\\begin{document}:end_\\end{document}'
        self.assertEqual(par.process_begin_document(s), ':end_')

        s = ':end_\\end{document}'
        self.assertEqual(par.process_begin_document(s), ':end_\\end{document}')

        # Others
        s = '\\end{document}\\begin{document}:end_\\begin{document}\\end{document}\\begin{document}'
        self.assertEqual(par.process_begin_document(s), ':end_\\begin{document}')

        s = """
        % Document
        \input{epic}
        This line of code should not be included
        \\begin{figure}
        This figure should not be included
        \\end{figure}
        \let\\a\\b
        \\begin    {document}
        Test
        \\end      {document}
        Removed as well!!
        """
        self.assertEqual(par.process_begin_document(s).strip(), 'Test')
