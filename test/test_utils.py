"""
PyDetex
https://github.com/ppizarror/PyDetex

TEST UTILS
Test utils.
"""

from test._base import BaseTest

import pydetex.utils as ut
from typing import Tuple, List


class UtilsTest(BaseTest):

    def test_lang(self) -> None:
        """
        Test language recognition.
        """
        s = """From anchor-based frameworks, Wu et al. [1] used Mask-RCNN [2] to vectorize the walls
            by finding a rectangle proposal representing each segment's width, thickness, angle,
            and location. """
        self.assertEqual(ut.detect_language(s), 'en')
        self.assertEqual(ut.get_language_name('en'), 'English')
        self.assertEqual(ut.get_language_name('en', 'es'), 'Inglés')
        self.assertEqual(ut.get_language_name('es'), 'Spanish')
        self.assertEqual(ut.get_language_name('unknown'), 'Unknown')
        self.assertEqual(ut.get_language_name('zh'), 'Chinese')
        s = """El modelo propuesto contiene diferentes métricas para coordenar las tareas de segmentación"""
        self.assertEqual(ut.detect_language(s), 'es')
        self.assertEqual(ut.detect_language(''), '–')
        self.assertEqual(ut.detect_language('https://epic.com'), '–')
        self.assertEqual(ut.detect_language('好的'), 'zh')

    def test_repeat_words(self) -> None:
        """
        Test repeated words.
        """
        # Test basic
        s = 'Abierto abierto abierto'
        t = 'Abierto <repeated:1>abierto</repeated> <repeated:1>abierto</repeated>'
        self.assertEqual(ut.check_repeated_words(s, 'es', 3, 15, True, True), t)

        # Ignore
        self.assertEqual(ut.check_repeated_words(s, 'es', 3, 15, True, True, ['Abierto']), s)

        s = 'The authors proposed a model which consider many semantic things, but overall the proposal is not good'
        t = 'The authors proposed a model which consider many semantic things, but overall the <repeated:11>proposal</repeated> is not good'
        self.assertEqual(ut.check_repeated_words(s, 'en', 3, 15, True, True), t)
        self.assertEqual(ut.check_repeated_words(s, 'unk', 3, 15, True, True), s)  # Unknown language

        s = 'Los autores propusieron un modelo sintáctico, sin embargo, éste se descartó. Descartando esto'
        t = 'Los autores propusieron un modelo sintáctico, sin embargo, éste se descartó. <repeated:1>Descartando</repeated> esto'
        self.assertEqual(ut.check_repeated_words(s, 'es', 3, 15, True, True), t)

        s = 'Le français est parlé, en 2018, sur tous les continents par environ 300 millions de personnes qui personne parle'
        t = 'Le français est parlé, en 2018, sur tous les continents par environ 300 millions de personnes qui <repeated:2>personne</repeated> <repeated:15>parle</repeated>'
        self.assertEqual(ut.check_repeated_words(s, 'fr', 3, 15, True, True), t)

        s = 'أسماء أخرى: لغة فرنسية؛ اللغة الفرنسية؛ فرنسية'
        t = 'أسماء أخرى: لغة فرنسية؛ اللغة الفرنسية؛ <repeated:3>فرنسية</repeated>'
        self.assertEqual(ut.check_repeated_words(s, 'ar', 3, 15, True, True), t)

        s = 'fremtrædende Fransk er udbredt i diplomatiet og har en fremtrædende position i den Europæiske Union'
        t = 'fremtrædende Fransk er udbredt i diplomatiet og har en <repeated:9>fremtrædende</repeated> position i den Europæiske Union'
        self.assertEqual(ut.check_repeated_words(s, 'da', 3, 15, True, True), t)

        s = 'Dies Frankreich liegt unter anderem daran, dass Frankreich ein Gründungsmitglied'
        t = 'Dies Frankreich liegt unter anderem daran, dass <repeated:6>Frankreich</repeated> ein Gründungsmitglied'
        self.assertEqual(ut.check_repeated_words(s, 'de', 3, 15, True, True), t)

        s = 'мнение о себе в мире, используется он всё меньше и меньше. В ООН Агентство Франкофонии используется'
        t = 'мнение о себе в мире, используется он всё меньше и <repeated:2>меньше</repeated>. В ООН Агентство Франкофонии <repeated:10>используется</repeated>'
        self.assertEqual(ut.check_repeated_words(s, 'ru', 3, 15, True, True), t)

        # Test with removed tokens
        s = 'This should not be repeated [NOT_REPEAT][NOT_REPEAT]a [OTHER_TAG][OTHER_TAG] [NOT_REPEAT][NOT_REPEAT]a'
        self.assertEqual(ut.check_repeated_words(s, 'en', 3, 15, True, True, remove_tokens=['[NOT_REPEAT]']), s)

        # Test with commands
        s = 'These commands \\texttt be removed \\texttt not \\texttt \\texttt \\texttt'
        self.assertEqual(ut.check_repeated_words(s, 'en', 3, 15, True, True), s)

        # Split points
        s = 'review objective. Finally, articles were selected and used for the present review.\nEach selected'
        t = 'review objective. Finally, articles were selected and used for the present <repeated:11>review</repeated>.\nEach <repeated:13>selected</repeated>'
        self.assertEqual(ut.check_repeated_words(s, 'en', 3, 15, True, True), t)

        # Stemmed words
        s = 'this review was made by several other ¿reviewers! but also this review.'
        t = 'this review was made by several other ¿<repeated:6>reviewers</repeated>! but also this <repeated:4>review</repeated>.'
        self.assertEqual(ut.check_repeated_words(s, 'en', 3, 15, True, True), t)

    def test_get_diff_startend_word(self) -> None:
        """
        Test word diff.
        """
        self.assertEqual(ut.get_diff_startend_word('XXXwordYYY', 'word'), ('XXX', 'YYY'))
        self.assertEqual(ut.get_diff_startend_word('word.', 'word'), ('', '.'))
        self.assertEqual(ut.get_diff_startend_word('!!word---', 'word'), ('!!', '---'))
        self.assertEqual(ut.get_diff_startend_word('wording', 'worg'), ('', ''))

    def test_split_tags(self) -> None:
        """
        Test split.
        """
        s = '[TAG1]new line[TAG2]this is[TAG1]very epic'
        self.assertEqual(ut.split_tags(s, ['[TAG1]', '[TAG2]']),
                         [('[TAG1]', 'new line'), ('[TAG2]', 'this is'), ('[TAG1]', 'very epic')])

        s = '[TAG1]new line[TAG1]this is[TAG1]very epic'
        self.assertEqual(ut.split_tags(s, ['[TAG1]', '[TAG2]']), [('[TAG1]', 'new linethis isvery epic')])

        # Merged tags
        s = '[TAG1]new line[TAG2][TAG2]this is[TAG1]very epic'
        self.assertEqual(ut.split_tags(s, ['[TAG1]', '[TAG2]']),
                         [('[TAG1]', 'new line'), ('[TAG2]', 'this is'), ('[TAG1]', 'very epic')])

        # No tags
        self.assertEqual(ut.split_tags(s, ['[TAG]']), [('[TAG]', '[TAG1]new line[TAG2][TAG2]this is[TAG1]very epic')])

        # Complex tagged
        s = '<A>This is a complex<B>example<A>but however <A>we should focus on<C>these<B>ideas<A>and<B>core <B>concepts<A>yes'
        self.assertEqual(ut.split_tags(s, ['<A>', '<B>', '<C>']),
                         [('<A>', 'This is a complex'), ('<B>', 'example'), ('<A>', 'but however we should focus on'),
                          ('<C>', 'these'), ('<B>', 'ideas'), ('<A>', 'and'), ('<B>', 'core concepts'), ('<A>', 'yes')])

    def test_validate(self) -> None:
        """
        Test validate.
        """
        self.assertTrue(ut.validate_int(''))
        self.assertTrue(ut.validate_int('-'))
        self.assertTrue(ut.validate_int('1'))
        self.assertTrue(ut.validate_int('-1'))
        self.assertTrue(ut.validate_int('-1.0000000000'))
        self.assertFalse(ut.validate_int('-1.01'))
        self.assertFalse(ut.validate_int('eee'))
        self.assertTrue(ut.validate_float('1'))
        self.assertTrue(ut.validate_float(''))
        self.assertTrue(ut.validate_float('-'))
        self.assertTrue(ut.validate_float('1.324'))
        self.assertTrue(ut.validate_float('-0.000123'))
        self.assertFalse(ut.validate_float('-0.123e'))

    def test_button_text(self) -> None:
        """
        Test button text.
        """
        self.assertEqual(ut.button_text('test'), 'test' if ut.IS_OSX else '  test  ')

    def test_find_tex_command_char(self) -> None:
        """
        Test find tex command char.
        """
        s = '$aaa$'
        self.assertEqual(ut.find_tex_command_char(s, [('$', '$', False)]), ((0, 1, 3, 4),))
        s = 'New $$ equation'
        self.assertEqual(ut.find_tex_command_char(s, [('$', '$', False)]), ((4, 5, 4, 5),))
        s = 'This is a $formula$ and this is not.'
        self.assertEqual(ut.find_tex_command_char(s, [('$', '$', False)]), ((10, 11, 17, 18),))
        s = 'This is a $formula\$ and this is not.'
        self.assertEqual(ut.find_tex_command_char(s, [('$', '$', False)]), ((10, 11, 18, 19),))
        s = 'This is a $formula\$ and this is not.'
        self.assertEqual(ut.find_tex_command_char(s, [('$', '$', True)]), ())
        s = 'This is a $formula\$$ and this is not.'
        self.assertEqual(ut.find_tex_command_char(s, [('$', '$', True)]), ((10, 11, 19, 20),))
        s = 'This is a \(formula\) and this is not.'
        self.assertEqual(ut.find_tex_command_char(s, [('\(', '\)', False)]), ((10, 12, 18, 20),))
        s = 'This is a \($formula$\) and this is not.'
        self.assertEqual(ut.find_tex_command_char(s, [('\(', '\)', False), ('$', '$', False)]), ((10, 12, 20, 22),))
        s = 'This is a \\begin{math}fo$\$rmula\end{math} and I like it'
        self.assertEqual(ut.find_tex_command_char(s, [('$', '$', True)]), ())
        self.assertEqual(ut.find_tex_command_char(s, [('\\begin{math}', '\end{math}', False)]), ((10, 22, 31, 41),))

    def test_apply_tag_between(self) -> None:
        """
        Test apply tags between.
        """
        self.assertEqual(ut.apply_tag_between_inside_char_command(
            'This is a $formula$ and this is not', [('$', '$', False)], ('a', 'b', 'c', 'd')),
            'This is a a$bformulac$d and this is not')

        self.assertEqual(ut.apply_tag_between_inside_char_command(
            '$formula$', [('$', '$', False)], ('X', '', '', 'X')), 'X$formula$X')

        self.assertEqual(ut.apply_tag_between_inside_char_command(
            '$formula$', [('$', '$', False)], ''), '$formula$')

        self.assertEqual(ut.apply_tag_between_inside_char_command(
            '$formula$', [('$', '$', False)], 'a'), 'a$aformulaa$a')

        self.assertEqual(ut.apply_tag_between_inside_char_command(
            '$formula$ jaja $x$', [('$', '$', False)], 'a'), 'a$aformulaa$a jaja a$axa$a')

        self.assertEqual(ut.apply_tag_between_inside_char_command(
            '$form\\$ula$', [('$', '$', True)], ('X', '', '', 'X')), 'X$form\\$ula$X')

        self.assertEqual(ut.apply_tag_between_inside_char_command(
            '\\$formula\\$', [('$', '$', True)], ('X', '', '', 'X')), '\\$formula\\$')

        self.assertEqual(ut.apply_tag_between_inside_char_command(
            '$formula$ jaja $x$', [('$', '$', False)], ('a', '', '', 'b')), 'a$formula$b jaja a$x$b')

        self.assertEqual(ut.apply_tag_between_inside_char_command(
            'a formula $$', [('$', '$', False)], ('a', 'b', 'c', 'd')), 'a formula a$$d')

        self.assertEqual(ut.apply_tag_between_inside_char_command(
            'a formula \(xx+yy\)', [('\(', '\)', False)], ('a', 'b', 'c', 'd')), 'a formula a\(bxx+yyc\)d')

        self.assertEqual(ut.apply_tag_between_inside_char_command(
            '$x$$y$$z$', [('$', '$', False)], ('a', '', '', 'b')), 'a$x$ba$y$ba$z$b')

    def test_find_tex_commands(self) -> None:
        """
        Test find tex commands.
        """

        def _test(_s: str, _query: Tuple[str, ...] = ()) -> None:
            _k = ut.find_tex_commands(_s)
            self.assertEqual(len(_k), len(_query))
            if len(_query) == 0:
                self.assertEqual(_k, ())
            else:
                for _j in range(len(_query)):
                    self.assertEqual(_s[_k[_j][2]:_k[_j][3] + 1], _query[_j])

        # Test empty
        _test('This is \\a0Command{nice}')
        _test('This is \\ {nice}')
        _test('This is \\aComm\n    and  {nice}')
        _test('This is \\aComm\nand  {nice}')
        _test('This is \\aCommand\{nice}')
        _test('This is \\aCommand{nice invalid!')
        _test('This is \\aCommand{nice invalid! \\anothercommand{yes}!')

        # Test simple
        _test('This is \\aComm\n {nice}', ('nice',))
        _test('This is \\aCommand{nice}', ('nice',))
        _test('This is \\aCommand{nice}}}}}}', ('nice',))
        _test('This is \\aCommand{ni[c]e}}}}}', ('ni[c]e',))
        _test('This is \\aCommand \\aCommand{nice2}', ('nice2',))
        _test('This is \\aCommand\\{ \\aCommand{nice2}', ('nice2',))
        _test('This is \\aCommand{ \\aCommand{nice2}}', (' \\aCommand{nice2}',))
        _test('This is \\aCommand{not \\} close} nice', ('not \\} close',))
        _test('This is \\aCommand{nice invalid! \\anothercommand{yes}}!',
              ('nice invalid! \\anothercommand{yes}',))
        _test('This is \\aCommand{\\command{inside}} nice',
              ('\\command{inside}',))

        # Test nested
        _test('\\a{{{{{{b}}}}}} c', ('{{{{{b}}}}}',))
        _test('\\a{{{{{{b}}}}} c}', ('{{{{{b}}}}} c',))
        _test('\\a{\\b{D}\\c{E}}', ('\\b{D}\\c{E}',))
        _test('\\a{\\b{D\\c{E}}}', ('\\b{D\\c{E}}',))

        # Test multiple
        _test('\\a{b} \\c{d}', ('b', 'd'))
        _test('\\a{b}\\c{d}', ('b', 'd'))
        _test('\\a{\\c{d}} \\e{f}', ('\\c{d}', 'f'))
        _test('\\a{\\c{d}} \\e{{f}}', ('\\c{d}', '{f}'))
        _test('\\a{\\c{d}}\\e{{f}}', ('\\c{d}', '{f}'))
        _test('\\a{\\c{d}\\}\\{} \\e{{f}}', ('\\c{d}\\}\\{', '{f}'))

        # Other parenthesis
        _test('\\a[b] \\c[d]', ('b', 'd'))

        # Test with spaces
        _test('This is \\aCommand    {nice}', ('nice',))
        _test('This is \\aCommand  }  \\aCommand{nice}', ('nice',))

        _test('This is \\aCommand                  {  nice}', ('  nice',))
        _test('This is \\aCommand                  [  nice]', ('  nice',))
        _test('This is \\aCommand        X         {{ nice} \\command    {nice2}', ('nice2',))

        # Invalids with spaces
        _test('This is \\aCommand        X         {{ nice}')

        # Test with spaces but an invalid letter
        _test('This is \\aCommand        X          {  nice}')
        _test('This is \\aCommand        X          {{ nice}')

        # Test with two parethesis format
        _test('This is \\aCommand   [  nice} ')
        _test('This is \\aCommand[nice2]', ('nice2',))

        # Test multi-command
        _test('This is \\aCommand{nice}{nice2}', ('nice', 'nice2'))
        _test('This is \\aCommand{nice}[nice2]', ('nice', 'nice2'))
        _test('This is \\aCommand{nice\}\[nice2] nice')
        _test('This is \\aCommand{nice\}\[nice2} nice', ('nice\}\[nice2',))
        _test('This is \\aCommand[{nice}]{nice!!} nice', ('{nice}', 'nice!!'))
        _test('This is \\aCommand[{{{{{{nice}}}}}}]{nice!!} nice', ('{{{{{{nice}}}}}}', 'nice!!'))
        _test('This is \\aCommand[1]{2} nice', ('1', '2'))
        _test('This is \\aCommand [1] {2} nice', ('1', '2'))
        _test('This is \\aCommand [1]\n {2} nice', ('1', '2'))

        # Test corrupt
        _test('This is a \\caption {epic \\caption{nice} sad')

        # Check continues
        s = 'This is \\f[1]{2} \\g{3} \\h{[}{4}{5} \\g \\f{6}[7]]{8} \\f{9}[10]{11} k {12}'
        _test(s, ('1', '2', '3', '[', '4', '5', '6', '7', '9', '10', '11'))
        t = [k[4] for k in ut.find_tex_commands(s)]
        self.assertEqual(t, [True, False, False, True, True, False, True, False, True, True, False])

        # Test empty
        s = '\DeclareUnicodeCharacter{2292}{\ensuremath{\ensuremath{}}}j nice \\f{g}'
        w = ut.find_tex_commands(s)
        self.assertEqual(len(w), 3)
        self.assertEqual(s[w[1][2]:w[1][3] + 1], '\\ensuremath{\\ensuremath{}}')
        self.assertEqual(s[w[2][2]:w[2][3] + 1], 'g')

    def test_find_tex_environments(self) -> None:
        """
        Test find tex environments.
        """

        def _test(s: str, envname: List[str], envargs: List[str], parents: List[str], depths: List[int]) -> None:
            k = ut.find_tex_environments(s)
            lk = len(k)
            if len(envargs) != 0:
                self.assertEqual(lk, len(envargs))
            self.assertEqual(lk, len(envname))
            for j in range(lk):
                self.assertEqual(k[j][0], envname[j])
                a, b = k[j][2], k[j][3]
                if len(envargs) != 0:
                    self.assertEqual(s[a:b], envargs[j])
                self.assertEqual(k[j][5], parents[j])
                self.assertEqual(k[j][6], depths[j])

        _test('This is \\begin{nice}[cmd]my...\end{nice}', ['nice'], ['[cmd]my...'], [''], [0])
        _test('This is \\begin{itemize*}\end{itemize*}', ['itemize*'], [''], [''], [0])
        _test('This is \\begin{enumerate*}\\begin{enumerate*}\item a\end{enumerate*}\end{enumerate*}',
              ['enumerate*', 'enumerate*'], ['\item a', '\\begin{enumerate*}\item a\end{enumerate*}'],
              ['enumerate*', ''], [1, 0])

        t = """This is \\latex{command}
        \\begin{minipage}[l][0][t]
        New \\mycommand[\\texttt{epic}]{nice}
            \\begin{itemize}[label=\\arabic]
                \\item A
                \\item B
                \\item C
                \\begin{itemize}
                    \\item D
                    \\item E
                    \\item F
                \\end{itemize}
            \\end{itemize}
        \\end{minipage}
        """
        _test(t, ['itemize', 'itemize', 'minipage'], [], ['itemize', 'minipage', ''], [2, 1, 0])

        t = """This is \\latex{command}
        \\begin{minipage}[l][0][t]
        New \\mycommand[\\texttt{epic}]{nice}
            \\begin{itemize}[label=\\arabic]
                \\item A
                \\item B
                \\item C
                \\begin{itemize}
                    \\item D
                    \\item E
                    \\begin{itemize}
                        \\item D
                        \\item E
                        \\item F
                    \\end{itemize}
                \\end{itemize}
            \\end{itemize}
        \\end{minipage}
        """
        _test(t, ['itemize', 'itemize', 'itemize', 'minipage'], [],
              ['itemize', 'itemize', 'minipage', ''], [3, 2, 1, 0])

        _s = """
        \\begin{figure}
            \\begin{animateinline}[poster = first, controls]{5}
            \whiledo{\\thehigher<30}{
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
               \end{tikzpicture}
            %
            \stepcounter{higher}
            \ifthenelse{\\thehigher<30}{ \\newframe }{\end{animateinline} }
          }
          \caption{Upper Riemann Sum}
          \label{epic}
        \end{figure}
        
        % Environments inside newenvironment should be ignored
        \\
        """
        self.assertEqual(
            ut.find_tex_environments(_s),
            (('tikzpicture', 137, 156, 1435, 1450, 'animateinline', 2, -1),
             ('animateinline', 36, 57, 1552, 1569, 'figure', 1, -1),
             ('figure', 9, 23, 1655, 1665, '', 0, -1)))

    def test_get_tex_commands_args(self) -> None:
        """
        Test get tex command args.
        """
        s = 'This is a \\aCommand[optional]{argument} nice'
        self.assertEqual(ut.get_tex_commands_args(s), (('aCommand', ('optional', True), ('argument', False)),))
        s = 'This is a \\caption {epic} \\caption{nice} sad'
        self.assertEqual(ut.get_tex_commands_args(s), (('caption', ('epic', False)), ('caption', ('nice', False))))
        s = 'This is \\subfloat[a title]'
        self.assertEqual(ut.get_tex_commands_args(s), (('subfloat', ('a title', True)),))
        self.assertEqual(ut.get_tex_commands_args(s, True), (('subfloat', ('a title', True), (8, 26)),))

    def test_find_tex_commands_no_argv(self) -> None:
        """
        Test find tex commands without arguments.
        """

        def _test(_s: str, _query: Tuple[str, ...] = ()) -> None:
            _k = ut.find_tex_commands_noargv(_s)
            self.assertEqual(len(_k), len(_query))
            if len(_query) == 0:
                self.assertEqual(_k, ())
            else:
                for _j in range(len(_query)):
                    self.assertEqual(_s[_k[_j][0]:_k[_j][1] + 1], _query[_j])

        _test('This is \\acommand', ('\\acommand',))
        _test('This is \\acommand\n{}', ('\\acommand',))
        _test('This is \\acomm\nand', ('\\acomm',))
        _test('This is \\acommand ', ('\\acommand',))
        _test('This is \\acommand{no} epic')
        _test('This is \\acommand   {no} epic')
        _test('This is \\acommand   k', ('\\acommand',))
        _test('This is \\acommand\\', ('\\acommand',))
        _test('This is \\a\\b', ('\\a', '\\b'))
        _test('This is \\\\\\\\\\\\\\\\\\a', ('\\a',))
        _test('This is \\a\\\\\\\\\\\\\\\\b', ('\\a', '\\b'))
        _test('This is \\a \\\\\\\\\\\\\\\\b', ('\\a', '\\b'))
        _test('This is \\0 \\\\\\\\\\\\\\\\b', ('\\b',))
        _test('This is \\   \\\\\\\\\\\\\\\\b', ('\\b',))
        _test('This is \\a{}\\\\\\\\\\\\\\\\b', ('\\b',))
        _test('This is \\a{\\c}\\\\\\\\\\\\\\\\d', ('\\c', '\\d',))
        _test('This is \\acommand{\\no} epic', ('\\no',))
        _test('This is \\acommand{\\no{}\\no{}} epic')
        _test('This is \\acommand{\\no{a}\\no{b}} epic')
        _test('This is \\acommand{\\1} epic')
        _test('This is \\ \\ \\1 \\2 \\_')
        _test('This is \\acommand{\\no{\\a}\\no{b}} epic', ('\\a',))
        _test('This is \\acommand{\\no{\\a{}}\\no{b}} epic')
        _test('This is \\acommand{\\no{\\a{\\c}}\\no{b}} epic', ('\\c',))
        _test('This is \\acommand{\\no{\\a{\\c1234}}\\no{b}} epic', ('\\c',))
        _test('nice \\c', ('\\c',))
        _test('\\c', ('\\c',))
        _test('\\\\')
        _test('This is a \\formula', ('\\formula',))
        _test('\\f \\g{1} \\h', ('\\f', '\\h'))
        _test('\\f \\g{1}[\\z] \\h', ('\\f', '\\z', '\\h'))
        _test('\\f \\g{1}[\\z     ] \\h', ('\\f', '\\z', '\\h'))
        _test('\\f \\g{1}[\\z    {} ] \\h', ('\\f', '\\h'))
        _test('\\f \\g{1}[\\z]{} \\h', ('\\f', '\\z', '\\h'))
        _test('\insertimage[]{pix2pix_compressed}{width=\linewidth}', ('\linewidth',))

    def test_apply_tag_tex_commands(self) -> None:
        """
        Test tag tex commands.
        """
        s = 'This does not contain any command'
        self.assertEqual(ut.apply_tag_tex_commands(s, ''), s)
        nums = ('1', '2', '3', '4', '5')

        s = 'This is a \\formula{epic} and this is not'
        b = 'This is a 1\\formula2{3epic4}5 and this is not'
        self.assertEqual(ut.apply_tag_tex_commands(s, nums), b)

        s = 'This is a \\formula{epic} and this is not'
        b = 'This is a |\\formula|{|epic|}| and this is not'
        self.assertEqual(ut.apply_tag_tex_commands(s, '|'), b)

        s = 'This is a \\formula{epic} and this \\i{s} not'
        b = 'This is a 1\\formula2{3epic4}5 and this 1\\i2{3s4}5 not'
        self.assertEqual(ut.apply_tag_tex_commands(s, nums), b)

        s = 'This is a \\formula{\\epic{nice}} and this is not'
        b = 'This is a 1\\formula2{3\\epic{nice}4}5 and this is not'
        self.assertEqual(ut.apply_tag_tex_commands(s, nums), b)

        s = 'This is a \\formula{nice}'
        b = 'This is a 1\\formula2{3nice4}5'
        self.assertEqual(ut.apply_tag_tex_commands(s, nums), b)

        s = 'This is a \\formula{\\formula{nice}}'
        b = 'This is a 1\\formula2{3\\formula{nice}4}5'
        self.assertEqual(ut.apply_tag_tex_commands(s, nums), b)

        # Multiple commands
        s = 'This is a \\f{A}[B]'
        b = 'This is a 1\\f2{3A4}52[3B4]5'
        self.assertEqual(ut.apply_tag_tex_commands(s, nums), b)

        s = 'This is a \\f{A} \\f \\g[B][C][D]'
        b = 'This is a 1\\f2{3A4}5 \\f 1\\g2[3B4]52[3C4]52[3D4]5'
        self.assertEqual(ut.apply_tag_tex_commands(s, nums), b)

    def test_apply_tag_tex_commands_noargv(self) -> None:
        """
        Test tag tex commands no arguments.
        """
        s = 'This does not contain any command'
        self.assertEqual(ut.apply_tag_tex_commands_no_argv(s, ''), s)

        s = 'This does not contain any \\command{command!}'
        self.assertEqual(ut.apply_tag_tex_commands_no_argv(s, ('1', '2')), s)

        s = 'This does not contain any \\command  {command!}'
        self.assertEqual(ut.apply_tag_tex_commands_no_argv(s, ('1', '2')), s)

        s = 'This is a \\formula and this is not'
        b = 'This is a 1\\formula2 and this is not'
        self.assertEqual(ut.apply_tag_tex_commands_no_argv(s, ('1', '2')), b)

        s = 'This is a \\formula and this is not'
        b = 'This is a |\\formula| and this is not'
        self.assertEqual(ut.apply_tag_tex_commands_no_argv(s, '|'), b)

        s = 'This is a \\formula and this \\i not'
        b = 'This is a 1\\formula2 and this 1\\i2 not'
        self.assertEqual(ut.apply_tag_tex_commands_no_argv(s, ('1', '2')), b)

        s = 'This is a \\formula{\\a{} not \\b{\\c}} and this \\i not'
        b = 'This is a \\formula{\\a{} not \\b{1\\c2}} and this 1\\i2 not'
        self.assertEqual(ut.apply_tag_tex_commands_no_argv(s, ('1', '2')), b)

        s = 'This is a \\formula'
        b = 'This is a 1\\formula2'
        self.assertEqual(ut.apply_tag_tex_commands_no_argv(s, ('1', '2')), b)

    def test_syntax_highlight(self) -> None:
        """
        Test synthax.
        """
        self.assertEqual(ut.syntax_highlight('nice'),
                         '⇱PYDETEX_FONT:NORMAL⇲nice')
        self.assertEqual(ut.syntax_highlight('nice \\epic'),
                         '⇱PYDETEX_FONT:NORMAL⇲nice ⇱PYDETEX_FONT:TEX_COMMAND⇲\epic⇱PYDETEX_FONT:NORMAL⇲')

        s = '\insertimage[]{pix2pix_compressed}{width=\linewidth}{Pix2Pix model}'
        t = '⇱PYDETEX_FONT:NORMAL⇲⇱PYDETEX_FONT:TEX_COMMAND⇲\insertimage⇱PYDETEX_FONT:NORMAL⇲' \
            '[⇱PYDETEX_FONT:NORMAL⇲]⇱PYDETEX_FONT:NORMAL⇲{⇱PYDETEX_FONT:TEX_ARGUMENT⇲' \
            'pix2pix_compressed⇱PYDETEX_FONT:NORMAL⇲}⇱PYDETEX_FONT:NORMAL⇲{⇱PYDETEX_FONT:TEX_ARGUMENT⇲' \
            'width=⇱PYDETEX_FONT:TEX_COMMAND⇲\linewidth⇱PYDETEX_FONT:NORMAL⇲⇱PYDETEX_FONT:NORMAL⇲}' \
            '⇱PYDETEX_FONT:NORMAL⇲{⇱PYDETEX_FONT:TEX_ARGUMENT⇲Pix2Pix model⇱PYDETEX_FONT:NORMAL⇲}'
        self.assertEqual(ut.syntax_highlight(s), t)

    # noinspection PyTypeChecker
    def test_format_number_d(self) -> None:
        """
        Test format number.
        """
        self.assertEqual(ut.format_number_d(5, ','), '5')
        self.assertEqual(ut.format_number_d(500, ','), '500')
        self.assertEqual(ut.format_number_d(5000, ','), '5,000')
        self.assertEqual(ut.format_number_d(5000, ','), '5,000')
        self.assertEqual(ut.format_number_d(5000000, '.'), '5.000.000')
        self.assertRaises(AssertionError, lambda: ut.format_number_d(1.5, ','))

    def test_tokenize(self) -> None:
        """
        Test tokenize.
        """
        s = """
        # ----------------------------------------------------------------------
        # Settings button
        # ----------------------------------------------------------------------
        

        """
        t = []
        for w in s.split(' '):
            tw = ut.tokenize(w)
            if tw == '' or '\n' in tw or '-' in tw:
                continue
            t.append(tw)
        self.assertEqual(t, ['Settings', 'button'])
        self.assertEqual(ut.tokenize('hello!!___..'), 'hello')
        self.assertEqual(ut.tokenize('tex-things!!___..'), 'tex-things')
        self.assertEqual(ut.tokenize('tex–things!!___..'), 'tex-things')

    def test_get_number_of_day(self) -> None:
        """
        Test day number.
        """
        self.assertIsInstance(ut.get_number_of_day(), int)

    def test_word_from_cursor(self) -> None:
        """
        Get the word from a cursor.
        """
        #    0000000000111111111
        #    0123456789012345678
        s = 'This is an example '
        self.assertEqual(ut.get_word_from_cursor(s, 0)[0], 'This')
        self.assertEqual(ut.get_word_from_cursor(s, 1)[0], 'This')
        self.assertEqual(ut.get_word_from_cursor(s, 2)[0], 'This')
        self.assertEqual(ut.get_word_from_cursor(s, 3)[0], 'This')
        self.assertEqual(ut.get_word_from_cursor(s, 4)[0], 'is')
        self.assertEqual(ut.get_word_from_cursor(s, 5)[0], 'is')
        self.assertEqual(ut.get_word_from_cursor(s, 6)[0], 'is')
        self.assertEqual(ut.get_word_from_cursor(s, 7)[0], 'an')
        self.assertEqual(ut.get_word_from_cursor(s, 8)[0], 'an')
        self.assertEqual(ut.get_word_from_cursor(s, 9)[0], 'an')
        self.assertEqual(ut.get_word_from_cursor(s, 10)[0], 'example')
        self.assertEqual(ut.get_word_from_cursor(s, 18)[0], '')
        self.assertRaises(AssertionError, lambda: ut.get_word_from_cursor(s, -1))
        self.assertRaises(AssertionError, lambda: ut.get_word_from_cursor(s, 19))

        # Test with more invalid chars
        s = 'This         is     \t\t\n\nan\n\n\nexample\t\t\n'
        self.assertEqual(ut.get_word_from_cursor(s, 0)[0], 'This')
        self.assertEqual(ut.get_word_from_cursor(s, 5)[0], 'is')
        self.assertEqual(ut.get_word_from_cursor(s, 13)[0], 'is')
        self.assertEqual(ut.get_word_from_cursor(s, 15)[0], 'an')
        self.assertEqual(ut.get_word_from_cursor(s, 26)[0], 'example')

        # With tags
        s = '<repeated:3>This</repeated> is an example '
        self.assertEqual(ut.get_word_from_cursor(s, 12)[0], 'This')
        self.assertEqual(ut.get_word_from_cursor(s, 16)[0], 'This</repeated>')

    def test_phrase_from_cursor(self) -> None:
        """
        Get the phrase from a cursor.
        """
        s = '        a nice plain '
        self.assertEqual(ut.get_phrase_from_cursor(s, 0, 1), 'a')

        s = '...well, this performed relativelly well. For these reasons,    the ...'
        self.assertEqual(s[43:55], 'or these rea')
        self.assertEqual(ut.get_phrase_from_cursor(s, 43, 55), 'For these reasons,')
        self.assertEqual(ut.get_phrase_from_cursor(s, 43, 60), 'For these reasons,')
        self.assertEqual(ut.get_phrase_from_cursor(s, 55, 55), 'reasons,')
        self.assertEqual(ut.get_phrase_from_cursor(s, 62, 62), 'the')

        s = 'returns a nice'
        self.assertEqual(ut.get_phrase_from_cursor(s, 0, 9), 'returns a')

    def test_lang_text_tex_langs(self) -> None:
        """
        Test the LangTexTextTags object.
        """
        lang = ut.LangTexTextTags()
        self.assertEqual(lang.get('en', 'multi_char_equ'), 'EQUATION_{0}')
        self.assertEqual(lang.get('it', 'multi_char_equ'), 'EQUATION_{0}')
        self.assertRaises(ValueError, lambda: lang.get('en', 'unknown_tag'))

    def test_tex_to_unicode(self) -> None:
        """
        Test tex to unicode.
        """
        s = '\\alpha^2 \cdot \\alpha^{2+3} \equiv \\alpha^7'
        self.assertEqual(ut.tex_to_unicode(s), 'α² ⋅ α²⁺³ ≡ α⁷')
        s = '\itA \in \\bbR^{nxn}, \\bfv \in \\bbR^n, \lambda_i \in \\bbR: \itA\\bfv = \lambda_i\\bfv'
        self.assertEqual(ut.tex_to_unicode(s), '𝐴 ∈ ℝⁿˣⁿ, 𝐯 ∈ ℝⁿ, λᵢ ∈ ℝ: 𝐴𝐯 = λᵢ𝐯')
        s = '\\bf{boldface} \it{italic} \\bb{blackboard} \cal{calligraphic} \\frak{fraktur} \mono{monospace}'
        self.assertEqual(ut.tex_to_unicode(s),
                         '𝐛𝐨𝐥𝐝𝐟𝐚𝐜𝐞 𝑖𝑡𝑎𝑙𝑖𝑐 𝕓𝕝𝕒𝕔𝕜𝕓𝕠𝕒𝕣𝕕 𝓬𝓪𝓵𝓵𝓲𝓰𝓻𝓪𝓹𝓱𝓲𝓬 𝔣𝔯𝔞𝔨𝔱𝔲𝔯 𝚖𝚘𝚗𝚘𝚜𝚙𝚊𝚌𝚎')
        s = 'bf This is all boldface'
        self.assertEqual(ut.tex_to_unicode(s), '𝐓𝐡𝐢𝐬 𝐢𝐬 𝐚𝐥𝐥 𝐛𝐨𝐥𝐝𝐟𝐚𝐜𝐞')
        s = '\\frac{a}{b}'
        self.assertEqual(ut.tex_to_unicode(s), 'a/b')
        s = '                 '
        self.assertEqual(ut.tex_to_unicode(s), s)
        s = '\\sqrt{a+b}'
        self.assertEqual(ut.tex_to_unicode(s), '√a+b')
        s = '\\alpha'
        self.assertEqual(ut.tex_to_unicode(s), 'α')
        s = 'alpha'
        self.assertEqual(ut.tex_to_unicode(s), 'α')

    def test_progress_bar(self) -> None:
        """
        Tests the progress bar.
        """
        pb = ut.ProgressBar(3)
        pb.update('A')
        pb.update('B')
        pb.update('C')
        self.assertEqual(pb._current, 3)
        pb.update('none')
        self.assertEqual(pb._current, 3)
        pb.reset()
        self.assertEqual(pb._current, 0)
        pb.detail_times()
