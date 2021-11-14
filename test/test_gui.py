"""
PyDetex
https://github.com/ppizarror/PyDetex

TEST GUI
Test guis.
"""

from test._base import BaseTest

from pydetex.gui import PyDetexGUI
# noinspection PyProtectedMember
from pydetex._gui_settings import Settings, _SETTINGS_FILE, _SETTINGS_TEST
# noinspection PyProtectedMember
from pydetex._gui_utils import SettingsWindow
import pydetex.pipelines as pip

import os

# Configure settings to default
_SETTINGS_FILE[0] = _SETTINGS_TEST


class GuiTest(BaseTest):

    def test_gui(self) -> None:
        """
        Gui test.
        """
        if 'GITHUB' in os.environ:
            return
        gui = PyDetexGUI()
        cfg = gui._cfg
        cfg.set(cfg.CFG_CHECK_REPETITION, False)
        cfg.set(cfg.CFG_OUTPUT_FONT_FORMAT, False)
        gui._clear()
        self.assertEqual(gui.pipeline, pip.simple)
        self.assertFalse(gui._ready)

        # Process the pipeline
        gui._text_in.insert(0.0, 'This is \\textbf{Latex}')
        gui._process_inner()
        self.assertEqual(gui._get_pipeline_results(), 'This is Latex')
        self.assertTrue(gui._ready)

        # Check clear
        gui._clear()
        self.assertFalse(gui._ready)

        # Check clip
        gui._process_clip_button()
        gui._copy_to_clip()

        # Test gui settings
        gui_settings = SettingsWindow((360, 320), cfg)
        gui_settings.close()

        gui._open_dictionary()

    def test_settings(self) -> None:
        """
        Test the app settings.
        """
        cfg = Settings(ignore_file=True)
        self.assertEqual(cfg.get(cfg.CFG_PIPELINE), pip.simple)
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

        # Test day diff
        self.assertEqual(cfg._last_opened_day_diff, 0)

        # Test font size
        self.assertFalse(cfg.check_setting(cfg.CFG_FONT_SIZE, 55))
        self.assertTrue(cfg.check_setting(cfg.CFG_FONT_SIZE, 11))

        self.assertFalse(cfg.check_setting(cfg.CFG_PIPELINE, ''))

        # Get
        self.assertEqual(cfg.get(cfg.CFG_REPETITION_MIN_CHAR), 4)
        cfg.set(cfg.CFG_REPETITION_MIN_CHAR, 2)
        self.assertEqual(cfg.get(cfg.CFG_REPETITION_MIN_CHAR), 2)
        cfg.set(cfg.CFG_REPETITION_MIN_CHAR, '3')
        self.assertEqual(cfg.get(cfg.CFG_REPETITION_MIN_CHAR), 3)

        # Test without ignore
        Settings()

        # Test language entries
        cfg.set(cfg.CFG_LANG, 'en')
        self.assertEqual(cfg.lang('lang'), 'English')
        cfg.set(cfg.CFG_LANG, 'es')
        self.assertEqual(cfg.lang('lang'), 'Español')
