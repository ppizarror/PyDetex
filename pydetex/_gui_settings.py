"""
PyDetex
https://github.com/ppizarror/pydetex

GUI SETTINGS
Provides settings for the gui.
"""

__all__ = [
    'Settings'
]

import os

from typing import Callable, Tuple, Dict, Any, List, Type, Union
from warnings import warn

import datetime
import pydetex.pipelines as pip
import pydetex.utils as ut
import pydetex.version as ver

from pydetex import __author__

_SETTINGS_FILE = [os.path.expanduser('~/') + '.pydetex.cfg']
_SETTINGS_TEST = ut.RESOURCES_PATH + '.pydetex.cfg'

# Store the pipelines
_PIPELINES = {
    'pipeline_simple': pip.simple,
    'pipeline_strict': pip.strict
}

# Store the window sizes (w, h, height_richtext, type)
_WINDOW_SIZE = {
    'window_size_small': [700, 415, 150],
    'window_size_medium': [900, 500, 193],
    'window_size_large': [1200, 600, 243]
}


class _LangManager(object):
    """
    Stores language.
    """

    def __init__(self) -> None:
        """
        Constructor.
        """
        self._lang = {
            'en': {
                'about': 'About',
                'about_author': 'Author',
                'about_opened': 'Total app openings',
                'about_processed': 'Total processed words',
                'about_ver_dev': 'Development version',
                'about_ver_err_conn': 'Cannot check for new versions (Connection Error)',
                'about_ver_err_unkn': 'Cannot check for new versions (Unknown Error)',
                'about_ver_latest': 'Software version up-to-date',
                'about_ver_upgrade': 'Note: You are using an outdated version, consider upgrading to v{0}',
                'cfg_check': 'Check',
                'cfg_error_font_size': 'Invalid font size value',
                'cfg_error_lang': 'Invalid lang value',
                'cfg_error_output_format': 'Invalid output font format value',
                'cfg_error_pipeline': 'Invalid pipeline value',
                'cfg_error_repetition': 'Invalid repetition value',
                'cfg_error_repetition_chars': 'Repetition min chars must be greater than zero',
                'cfg_error_repetition_distance': 'Repetition distance be greater than 2',
                'cfg_error_repetition_words': 'Invalid ignore words',
                'cfg_error_stemming': 'Invalid repetition stemming value',
                'cfg_error_stopwords': 'Invalid repetition stopwords value',
                'cfg_error_window_size': 'Invalid window size value',
                'cfg_font_format': 'Output font format',
                'cfg_font_size': 'Font size',
                'cfg_lang': 'Language',
                'cfg_pipeline': 'Pipeline',
                'cfg_save': 'Save',
                'cfg_window_size': 'Window size',
                'cfg_words_repetition': 'Words repetition',
                'cfg_words_repetition_distance': 'Repetition distance',
                'cfg_words_repetition_ignorew': 'Ignored words',
                'cfg_words_repetition_minchars': 'Repetition min chars',
                'cfg_words_repetition_stemming': 'Use stemming',
                'cfg_words_repetition_stopwords': 'Use stopwords',
                'clear': 'Clear',
                'detected_lang': 'Detected language: {0} ({1}). Words: {2}',
                'lang': 'English',
                'pipeline_simple': 'Simple',
                'pipeline_strict': 'Strict',
                'placeholder': 'Write or paste here your \\texttt{LaTeX} code. It simply removes all tex-things, and returns a nice plain text!',
                'process': 'Process',
                'process_clip': 'Process from clipboard',
                'process_copy': 'Copy to clipboard',
                'reload_message_message': 'To apply these changes, the app must be reloaded',
                'reload_message_title': 'Reload is required',
                'settings': 'Settings',
                'tag_repeated': 'repeated',
                'window_size_small': 'Small',
                'window_size_medium': 'Medium',
                'window_size_large': 'Large'
            },
            'es': {
                'about': 'Acerca de',
                'about_author': 'Autor',
                'about_opened': 'Nº ejecuciones app',
                'about_processed': 'Nº palabras procesadas',
                'about_ver_dev': 'Versión de desarrollo',
                'about_ver_err_conn': 'No se pudo verificar nuevas versiones (Error de Conexión)',
                'about_ver_err_unkn': 'No se pudo verificar nuevas versiones (Error desconocido)',
                'about_ver_latest': 'Software actualizado a la última versión',
                'about_ver_upgrade': 'Nota: Estás usando una versión desactualizada, considera actualizar a la v{0}',
                'cfg_check': 'Activar',
                'cfg_error_font_size': 'Tamaño fuente incorrecta',
                'cfg_error_lang': 'Valor idioma incorrecto',
                'cfg_error_output_format': 'Valor formato output incorrecto',
                'cfg_error_pipeline': 'Valor pipeline incorrecto',
                'cfg_error_repetition': 'Valor repetición incorrecto',
                'cfg_error_repetition_chars': 'Caracter mínimo de repetición debe ser mayor a cero',
                'cfg_error_repetition_distance': 'Distancia de repetición debe ser superior o igual a 2',
                'cfg_error_repetition_words': 'Repetición palabras incorrectas',
                'cfg_error_stemming': 'Valor stemming incorrecto',
                'cfg_error_stopwords': 'Valor stopwords incorrecto',
                'cfg_font_format': 'Formatear fuentes',
                'cfg_font_size': 'Tamaño de la fuente',
                'cfg_lang': 'Idioma',
                'cfg_pipeline': 'Pipeline',
                'cfg_save': 'Guardar',
                'cfg_window_size': 'Tamaño de ventana',
                'cfg_words_repetition': 'Repetición de palabras',
                'cfg_words_repetition_distance': 'Distancia de repetición',
                'cfg_words_repetition_ignorew': 'Palabras ignoradas',
                'cfg_words_repetition_minchars': 'Mínimo de carácteres',
                'cfg_words_repetition_stemming': 'Usar stemming',
                'cfg_words_repetition_stopwords': 'Usar stopwords',
                'cfg_error_window_size': 'Tamaño ventana incorrecto',
                'clear': 'Limpiar',
                'detected_lang': 'Idioma detectado: {0} ({1}). Palabras: {2}',
                'lang': 'Español',
                'pipeline_simple': 'Simple',
                'pipeline_strict': 'Estricto',
                'placeholder': 'Escribe o pega aquí tu código \\texttt{LaTeX}. El programa simplemente eliminará todo lo relacionado a tex y retornará un lindo texto plano!',
                'process': 'Procesar',
                'process_clip': 'Procesar desde portapapeles',
                'process_copy': 'Copiar al portapapeles',
                'reload_message_message': 'Para aplicar estos cambios, la aplicación se debe reiniciar',
                'reload_message_title': 'Se requiere de un reinicio',
                'settings': 'Configuraciones',
                'tag_repeated': 'repetido',
                'window_size_small': 'Pequeño',
                'window_size_medium': 'Mediano',
                'window_size_large': 'Grande'
            }
        }

        # Extend languages if not defined
        for k in self._lang.keys():
            if k == 'en':
                continue
            for t in self._lang['en'].keys():
                if t not in self._lang[k]:
                    warn(f'Language entry "{t}" on lang "{k}" does not exist')
                    self._lang[k][t] = self._lang['en'][t]

    def get_available(self) -> List[str]:
        """
        Return the available langs.

        :return: Lang list
        """
        return list(self._lang.keys())

    def get(self, lang: str, tag: str) -> str:
        """
        Returns a lang entry.

        :param lang: Language code
        :param tag: Language tag
        :return: Language value
        """
        return self._lang[lang][tag]


class Settings(object):
    """
    Settings.
    """

    _available_pipelines: List[str]
    _default_settings: Dict[str, Tuple[Any, Type, Union[List[Any], Callable[[Any], bool]]]]
    _lang: '_LangManager'
    _settings: Dict[str, Any]
    _valid_font_sizes: List[int]
    _valid_window_sizes: List[str]

    def __init__(self, ignore_file: bool = False) -> None:
        """
        Constructor.

        :param ignore_file: If True, the settings file is ignored
        """
        load = []

        def _load_file() -> List[str]:
            """
            Loads the setting file.
            """
            _load = []
            try:
                _f = open(_SETTINGS_FILE[0], 'r')
                _load = _f.readlines()
                _f.close()
            except FileNotFoundError:
                warn(f'Setting file {_SETTINGS_FILE[0]} could not be loaded or not exist. Creating new file')
            return _load

        if not ignore_file:
            try:
                load = _load_file()
            except PermissionError:
                warn(f'Settings file {_SETTINGS_FILE[0]} could not be opened (PermissionError)')
        else:
            _SETTINGS_FILE[0] = _SETTINGS_TEST

        # Creates the lang manager
        self._lang = _LangManager()

        # General settings
        self.CFG_CHECK_REPETITION = 'CHECK_REPETITION'
        self.CFG_FONT_SIZE = 'FONT_SIZE'
        self.CFG_LANG = 'LANG'
        self.CFG_OUTPUT_FONT_FORMAT = 'OUTPUT_FONT_FORMAT'
        self.CFG_PIPELINE = 'PIPELINE'
        self.CFG_WINDOW_SIZE = 'WINDOW_SIZE'

        # Words repetition
        self.CFG_REPETITION_DISTANCE = 'REPETITION_DISTANCE'
        self.CFG_REPETITION_IGNORE_WORDS = 'REPETITION_IGNORE_WORDS'
        self.CFG_REPETITION_MIN_CHAR = 'REPETITION_MIN_CHAR'
        self.CFG_REPETITION_USE_STEMMING = 'REPETITION_USE_STEMMING'
        self.CFG_REPETITION_USE_STOPWORDS = 'REPETITION_USE_STOPWORDS'

        # Stats
        self.CFG_TOTAL_OPENED_APP = 'TOTAL_OPENED_APP'
        self.CFG_TOTAL_PROCESSED_WORDS = 'TOTAL_PROCESSED_WORDS'

        # Stores default settings and the valid values
        self._available_pipelines = list(_PIPELINES.keys())
        self._valid_font_sizes = [9, 10, 11, 12, 13, 14, 15]
        self._valid_window_sizes = list(_WINDOW_SIZE.keys())

        self._default_settings = {
            self.CFG_CHECK_REPETITION: (False, bool, [True, False]),
            self.CFG_FONT_SIZE: (11, int, self._valid_font_sizes),
            self.CFG_LANG: ('en', str, self._lang.get_available()),
            self.CFG_OUTPUT_FONT_FORMAT: (True, bool, [True, False]),
            self.CFG_PIPELINE: (self._available_pipelines[0], str, self._available_pipelines),
            self.CFG_REPETITION_DISTANCE: (15, int, lambda x: x > 1),
            self.CFG_REPETITION_IGNORE_WORDS: ('ignored_word_1, ignored_word_2', str, None),
            self.CFG_REPETITION_MIN_CHAR: (4, int, lambda x: x > 0),
            self.CFG_REPETITION_USE_STEMMING: (True, bool, [True, False]),
            self.CFG_REPETITION_USE_STOPWORDS: (True, bool, [True, False]),
            self.CFG_TOTAL_OPENED_APP: (0, int, lambda x: x >= 0),
            self.CFG_TOTAL_PROCESSED_WORDS: (0, int, lambda x: x >= 0),
            self.CFG_WINDOW_SIZE: (self._valid_window_sizes[0], str, self._valid_window_sizes)
        }

        # The valid settings
        self._settings = {}
        for k in self._default_settings.keys():
            self._settings[k] = self._default_settings[k][0]

        # Load the user settings
        for f in load:
            if '#' in f:
                continue
            if '=' in f:  # If string has control character
                sp = f.split('=')
                if len(sp) != 2:
                    continue
                j = sp[0].strip()
                val = sp[1].strip()
                if self.check_setting(j, val):
                    self._settings[j] = self._parse_str(val)  # Update setting value

        # Update the value
        self.set(self.CFG_TOTAL_OPENED_APP, self.get(self.CFG_TOTAL_OPENED_APP) + 1)

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
            else:
                value = value.strip()
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
                warn(f'Setting {key} should be type {val_type}, but received {type(value)}')
                return False
            if isinstance(val_valids, list):
                if value in val_valids:  # Setting is within valid ones
                    return True
                else:
                    str_valids = []
                    for t in val_valids:
                        str_valids.append(str(t))
                    warn(f'Setting {key} value should have these values: {",".join(str_valids)}')
            elif val_valids is None:
                return True
            else:  # Is a function
                if not val_valids(value):
                    warn(f'Setting {key} do not pass valid test')
                else:
                    return True
        else:
            warn(f'Setting {key} does not exist')
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
            elif key == self.CFG_WINDOW_SIZE:
                val = _WINDOW_SIZE[val]

        return val

    def set(self, key: str, value: Any) -> None:
        """
        Update a setting value.

        :param key: Setting key
        :param value: Value
        """
        if not self.check_setting(key, value):
            raise ValueError(f'Invalid value for {key}')
        self._settings[key] = self._parse_str(value)

    def lang(self, tag: str) -> str:
        """
        Get a lang tag.

        :param tag: Lang's tag
        :return: Lang value
        """
        return self._lang.get(self.get(self.CFG_LANG), tag)

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
        try:
            f = open(_SETTINGS_FILE[0], 'w')
            keys = list(self._settings.keys())
            keys.sort()
            f.write(f'# PyDetex v{ver.vernum} @ {__author__}\n')
            f.write(f'# Settings stored on {datetime.datetime.today().ctime()}\n')
            for k in keys:
                f.write(f'{k} = {str(self._settings[k]).strip()}\n')
            f.close()
        except PermissionError:
            warn(f'Settings file {_SETTINGS_FILE[0]} could not saved (PermissionError)')
