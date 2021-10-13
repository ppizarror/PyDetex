"""
PyDetex
https://github.com/ppizarror/pydetex

TEST UTILS
Test utils.
"""

from test._base import BaseTest

import pydetex.utils as ut


class UtilsTest(BaseTest):

    def test_lang(self) -> None:
        """
        Test language recognition.
        """
        s = """From anchor-based frameworks, Wu et al. [1] used Mask-RCNN [2] to vectorize the walls
            by finding a rectangle proposal representing each segment's width, thickness, angle,
            and location. """
        self.assertEqual(ut.detect_language(s), 'en')
        self.assertEqual(ut.get_language_tag('en'), 'English')
        s = """El modelo propuesto contiene diferentes métricas para coordenar las tareas de segmentación"""
        self.assertEqual(ut.detect_language(s), 'es')
        self.assertEqual(ut.detect_language(''), '–')

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
        t = 'мнение о себе в мире, используется он всё меньше и <repeated:2>меньше.</repeated> В ООН Агентство Франкофонии <repeated:10>используется</repeated>'
        self.assertEqual(ut.check_repeated_words(s, 'ru', 3, 15, True, True), t)

        # Test with removed tokens
        s = 'This should not be repeated [NOT_REPEAT][NOT_REPEAT]a [OTHER_TAG][OTHER_TAG] [NOT_REPEAT][NOT_REPEAT]a'
        self.assertEqual(ut.check_repeated_words(s, 'en', 3, 15, True, True, remove_tokens=['[NOT_REPEAT]']), s)

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
        self.assertTrue(ut.validate_int('1'))
        self.assertTrue(ut.validate_int('-1'))
        self.assertTrue(ut.validate_int('-1.0000000000'))
        self.assertFalse(ut.validate_int('-1.01'))
        self.assertTrue(ut.validate_float('1'))
        self.assertTrue(ut.validate_float('1.324'))
        self.assertTrue(ut.validate_float('-0.000123'))
        self.assertFalse(ut.validate_float('-0.123e'))

    def test_button_text(self) -> None:
        """
        Test button text.
        """
        self.assertEqual(ut.button_text('test'), 'test' if ut.IS_OSX else '  test  ')
