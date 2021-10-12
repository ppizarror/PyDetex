"""
PyDetex
https://github.com/ppizarror/pydetex

TEST GUI
Test guis.
"""

from test._base import BaseTest

# noinspection PyProtectedMember
from pydetex.gui import PyDetexGUI, _Settings
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
        cfg = _Settings()
        self.assertEqual(cfg.get('PIPELINE'), pip.simple_pipeline)
        self.assertTrue(cfg.get('CHECK_REPETITION'))
        cfg.save()
