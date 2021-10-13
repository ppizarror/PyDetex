"""
PyDetex
https://github.com/ppizarror/pydetex

GUI SETTINGS
Provides settings for the gui.
"""

__all__ = [
    'Settings'
]

from typing import Callable, Tuple, Dict, Any, List, Type, Union
from warnings import warn

import pydetex.pipelines as pip
import pydetex.utils as ut

# Store the pipelines
_PIPELINES = {
    'Simple': pip.simple_pipeline
}


class Settings(object):
    """
    Settings.
    """

    _available_pipelines: List[str]
    _default_settings: Dict[str, Tuple[Any, Type, Union[List[Any], Callable[[Any], bool]]]]
    _settings: Dict[str, Any]

    def __init__(self, ignore_file: bool = False) -> None:
        """
        Constructor.

        :param ignore_file: If True, the settings file is ignored
        """
        load = []
        if not ignore_file:
            try:
                f = open(ut.RESOURCES_PATH + 'settings.cfg', 'r')
                load = f.readlines()
                f.close()
            except FileNotFoundError:
                warn('Setting file could not be loaded or not exist. Creating new file')

        # General settings
        self.CFG_CHECK_REPETITION = 'CHECK_REPETITION'
        self.CFG_OUTPUT_FONT_FORMAT = 'OUTPUT_FONT_FORMAT'
        self.CFG_PIPELINE = 'PIPELINE'

        # Words repetition
        self.CFG_REPETITION_DISTANCE = 'REPETITION_DISTANCE'
        self.CFG_REPETITION_IGNORE_WORDS = 'REPETITION_IGNORE_WORDS'
        self.CFG_REPETITION_MIN_CHAR = 'REPETITION_MIN_CHAR'
        self.CFG_REPETITION_USE_STEMMING = 'REPETITION_USE_STEMMING'
        self.CFG_REPETITION_USE_STOPWORDS = 'REPETITION_USE_STOPWORDS'

        # Stats
        self.CFG_TOTAL_PROCESSED_WORDS = 'TOTAL_PROCESSED_WORDS'

        # Stores default settings and the valid values
        self._available_pipelines = list(_PIPELINES.keys())
        self._default_settings = {
            self.CFG_CHECK_REPETITION: (False, bool, [True, False]),
            self.CFG_OUTPUT_FONT_FORMAT: (True, bool, [True, False]),
            self.CFG_PIPELINE: (self._available_pipelines[0], str, self._available_pipelines),
            self.CFG_REPETITION_DISTANCE: (15, int, lambda x: x > 1),
            self.CFG_REPETITION_IGNORE_WORDS: ('ignored_word_1, ignored_word_2', str, None),
            self.CFG_REPETITION_MIN_CHAR: (4, int, lambda x: x > 0),
            self.CFG_REPETITION_USE_STEMMING: (True, bool, [True, False]),
            self.CFG_REPETITION_USE_STOPWORDS: (True, bool, [True, False]),
            self.CFG_TOTAL_PROCESSED_WORDS: (0, int, lambda x: x >= 0)
        }

        # The valid settings
        self._settings = {}
        for k in self._default_settings.keys():
            self._settings[k] = self._default_settings[k][0]

        # Load the user settings
        for f in load:
            if '=' in f:  # If string has control character
                sp = f.split('=')
                if len(sp) != 2:
                    continue
                j = sp[0].strip()
                val = sp[1].strip()
                if self.check_setting(j, val):
                    self._settings[j] = self._parse_str(val)  # Update setting value

        # Save the settings
        self.save()

    @staticmethod
    def _parse_str(value: Any) -> Any:
        """
        Parse common string values.

        :param value: Value
        :return: Parsed value
        """
        if isinstance(value, str):
            if value == 'True':
                value = True
            elif value == 'False':
                value = False
            elif value.replace('.', '').replace('-', '').replace('+', '').isdigit():
                try:
                    old_val = value
                    value = float(value)
                    if '.' not in old_val and int(value) == value:
                        value = int(value)
                except ValueError:
                    pass
        return value

    def check_setting(self, key: str, value: Any) -> bool:
        """
        Check if a setting is valid.

        :param key: Key setting
        :param value: Value
        :return: True if valid
        """
        # Apply custom values
        if isinstance(value, str):
            value = self._parse_str(value)

        # Checks
        if key in self._default_settings.keys():
            val_type = self._default_settings[key][1]
            val_valids = self._default_settings[key][2]
            # Check val type
            if not isinstance(value, val_type):
                warn('Setting {0} should be type {1}, but received {2}'.format(key, val_type, type(value)))
                return False
            if isinstance(val_valids, list):
                if value in val_valids:  # Setting is within valid ones
                    return True
                else:
                    warn('Setting {0} value should have these values: {1}'
                         .format(key, ','.join(val_valids)))
            elif val_valids is None:
                return True
            else:  # Is a function
                if not val_valids(value):
                    warn('Setting {0} do not pass valid test'.format(key))
                else:
                    return True
        else:
            warn('Setting {0} does not exist'.format(key))
        return False

    def get(self, key: str, update: bool = True) -> Any:
        """
        Return the settings value.

        :param key: Setting key
        :param update: Updates settings value
        :return: Value
        """
        val = self._settings[key]

        # Update for some values
        if update:
            if key == self.CFG_PIPELINE:
                val = _PIPELINES[val]

        return val

    def set(self, key: str, value: Any) -> None:
        """
        Update a setting value.

        :param key: Setting key
        :param value: Value
        """
        if not self.check_setting(key, value):
            raise ValueError('Invalid value for {0}'.format(key))
        self._settings[key] = self._parse_str(value)

    def add_words(self, w: int) -> None:
        """
        Add processed words.

        :param w: Words
        """
        self._settings[self.CFG_TOTAL_PROCESSED_WORDS] += w
        self.save()

    def save(self) -> None:
        """
        Save the settings to the file.
        """
        f = open(ut.RESOURCES_PATH + 'settings.cfg', 'w')
        keys = list(self._settings.keys())
        keys.sort()
        for k in keys:
            f.write('{0} = {1}\n'.format(k, str(self._settings[k]).strip()))
        f.close()
