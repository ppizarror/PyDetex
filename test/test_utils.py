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

    def test_repeat_words(self) -> None:
        pass
