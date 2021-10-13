"""
PyDetex
https://github.com/ppizarror/pydetex

TEST GUI
Test guis.
"""

from test._base import BaseTest

# noinspection PyProtectedMember
from pydetex.gui import PyDetexGUI, _Settings, _validate_int, _validate_float
import pydetex.pipelines as pip
import os


class GuiTest(BaseTest):

    def test_gui(self) -> None:
        """
        Gui test.
        """
        if 'TRAVIS' in os.environ:
            return
        gui = PyDetexGUI()
        gui._clear()
        self.assertEqual(gui.pipeline, pip.simple_pipeline)
        self.assertFalse(gui._ready)

        # Process the pipeline
        gui._text_in.insert(0.0, 'This is \\textbf{Latex}')
        gui._process()
        self.assertEqual(gui._get_pipeline_results(), 'This is Latex')
        self.assertTrue(gui._ready)

        # Check clear
        gui._clear()
        self.assertFalse(gui._ready)

        # Check clip
        gui._process_clip()
        gui._copy_to_clip()

    def test_settings(self) -> None:
        """
        Test the app settings.
        """
        cfg = _Settings(ignore_file=True)
        self.assertEqual(cfg.get(cfg.CFG_PIPELINE), pip.simple_pipeline)
        self.assertFalse(cfg.get(cfg.CFG_CHECK_REPETITION))
        cfg.save()

        # Test invalid
        self.assertFalse(cfg.check_setting('UNKNOWN', ''))
        self.assertFalse(cfg.check_setting(cfg.CFG_REPETITION_MIN_CHAR, 3.5))
        self.assertFalse(cfg.check_setting(cfg.CFG_REPETITION_MIN_CHAR, -1))
        self.assertFalse(cfg.check_setting(cfg.CFG_REPETITION_MIN_CHAR, '-1'))
        self.assertTrue(cfg.check_setting(cfg.CFG_REPETITION_MIN_CHAR, '1'))
        self.assertFalse(cfg.check_setting(cfg.CFG_REPETITION_MIN_CHAR, '1f'))
        self.assertTrue(cfg.check_setting(cfg.CFG_REPETITION_MIN_CHAR, 1))

        self.assertFalse(cfg.check_setting(cfg.CFG_PIPELINE, ''))

        # Get
        self.assertEqual(cfg.get(cfg.CFG_REPETITION_MIN_CHAR), 4)
        cfg.set(cfg.CFG_REPETITION_MIN_CHAR, 2)
        self.assertEqual(cfg.get(cfg.CFG_REPETITION_MIN_CHAR), 2)
        cfg.set(cfg.CFG_REPETITION_MIN_CHAR, '3')
        self.assertEqual(cfg.get(cfg.CFG_REPETITION_MIN_CHAR), 3)

        # Test without ignore
        _Settings()

    def test_validate(self) -> None:
        """
        Test validate.
        """
        self.assertTrue(_validate_float('1.32'))
        self.assertTrue(_validate_float('-1.32'))
        self.assertFalse(_validate_float('12e'))
        self.assertTrue(_validate_int('123'))
        self.assertTrue(_validate_int('123.0'))
        self.assertFalse(_validate_int('123.01'))
        self.assertFalse(_validate_int('abc'))
