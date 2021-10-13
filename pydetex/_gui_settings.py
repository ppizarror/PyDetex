"""
PyDetex
https://github.com/ppizarror/pydetex

GUI SETTINGS
Provides settings for the gui.
"""

__all__ = [
    'Settings',
    'SettingsWindow',
    'RichText'
]

import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox

import sys

from typing import Callable, Tuple, Dict, Any, List, Type, Union, Optional
from warnings import warn

sys.path.append('../')

import pydetex.pipelines as pip
import pydetex.utils as ut
from pydetex.utils import IS_OSX

# Store the pipelines
_PIPELINES = {
    'Simple': pip.simple_pipeline
}

# Configure fonts
_FONT_TAGS = {
    'bold': '[PYDETEX_FONT:BOLD]',
    'bold_italic': '[PYDETEX_FONT:BOLD_ITALIC]',
    'italic': '[PYDETEX_FONT:ITALIC]',
    'normal': '[PYDETEX_FONT:NORMAL]',
    'underlined': '[PYDETEX_FONT:UNDERLINED]',
}
_TAGS_FONT = {}
for _tag in _FONT_TAGS.keys():
    _TAGS_FONT[_FONT_TAGS[_tag]] = _tag


class SettingsWindow(object):
    """
    Settings window.
    """

    _cfg: 'Settings'
    on_destroy: Optional[Callable[[], None]]

    def __init__(self, window_size: Tuple[int, int], cfg: 'Settings') -> None:
        """
        Constructor.

        :param window_size: Window size (width, height)
        :param cfg: Settings
        """
        self.root = tk.Tk()
        self.on_destroy = None
        self._cfg = cfg  # Store setting reference

        # Configure window
        self.root.title('Settings')
        self.root.minsize(width=window_size[0], height=window_size[1])
        self.root.resizable(width=False, height=False)
        self.root.geometry('%dx%d+%d+%d' % (window_size[0], window_size[1],
                                            (self.root.winfo_screenwidth() - window_size[0]) / 2,
                                            (self.root.winfo_screenheight() - window_size[1]) / 2))
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        if not IS_OSX:
            self.root.iconbitmap(ut.RESOURCES_PATH + 'cog.ico')

        # Registers
        reg_int = self.root.register(ut.validate_int)

        # Main frame
        f0 = tk.Frame(self.root, border=5)
        f0.pack(fill='both')

        label_w = 17

        # Set pipelines
        f = tk.Frame(f0, border=0)
        f.pack(fill='both', pady=5)
        tk.Label(f, text='Pipeline', width=label_w, anchor='w').pack(side=tk.LEFT, padx=5)

        self._var_pipeline = tk.StringVar(self.root)
        self._var_pipeline.set(cfg.get(cfg.CFG_PIPELINE, update=False))  # default value

        pipe = tk.OptionMenu(f, self._var_pipeline, *list(_PIPELINES.keys()))
        pipe.focus()
        pipe.pack(side=tk.LEFT)

        # Check repetition
        f_repetition = tk.LabelFrame(f0, text='Words repetition', bd=1, relief=tk.GROOVE)
        f_repetition.pack(fill='both')

        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text='Check', width=label_w, anchor='w').pack(
            side=tk.LEFT,
            padx=(5 if IS_OSX else 4, 4))
        self._var_check_repetition = tk.BooleanVar(self.root)
        self._var_check_repetition.set(cfg.get(cfg.CFG_CHECK_REPETITION))
        tk.Checkbutton(f, variable=self._var_check_repetition).pack(side=tk.LEFT)

        # Repetition min chars
        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text='Repetition min chars', width=label_w, anchor='w').pack(
            side=tk.LEFT,
            padx=(5 if IS_OSX else 4, 5 if IS_OSX else 9)
        )
        self._var_repetition_min_char = tk.Entry(f, validate='all', validatecommand=(reg_int, '%P'), width=5)
        self._var_repetition_min_char.pack(side=tk.LEFT)
        self._var_repetition_min_char.insert(0, cfg.get(cfg.CFG_REPETITION_MIN_CHAR))

        # Repetition distance
        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text='Repetition distance', width=label_w, anchor='w').pack(
            side=tk.LEFT,
            padx=(5 if IS_OSX else 4, 5 if IS_OSX else 9)
        )
        self._var_repetition_distance = tk.Entry(f, validate='all', validatecommand=(reg_int, '%P'), width=5)
        self._var_repetition_distance.pack(side=tk.LEFT)
        self._var_repetition_distance.insert(0, cfg.get(cfg.CFG_REPETITION_DISTANCE))

        # Repetition use stemming
        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text='Use stemming', width=label_w, anchor='w').pack(
            side=tk.LEFT,
            padx=(5 if IS_OSX else 4, 4)
        )
        self._var_check_repetition_stemming = tk.BooleanVar(self.root)
        self._var_check_repetition_stemming.set(cfg.get(cfg.CFG_REPETITION_USE_STEMMING))
        tk.Checkbutton(f, variable=self._var_check_repetition_stemming).pack(side=tk.LEFT)

        # Repetition use stopwords
        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text='Use stopwords', width=label_w, anchor='w').pack(
            side=tk.LEFT,
            padx=(5 if IS_OSX else 4, 4)
        )
        self._var_check_repetition_stopwords = tk.BooleanVar(self.root)
        self._var_check_repetition_stopwords.set(cfg.get(cfg.CFG_REPETITION_USE_STOPWORDS))
        tk.Checkbutton(f, variable=self._var_check_repetition_stopwords).pack(side=tk.LEFT)

        # Repetition ignore words
        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text='Repetition ignore words', width=label_w, anchor='w').pack(
            side=tk.LEFT,
            padx=(5 if IS_OSX else 4, 5 if IS_OSX else 9)
        )
        self._var_repetition_ignore_words = tk.Text(f, wrap='word', height=4, highlightthickness=3 if IS_OSX else 0,
                                                    highlightcolor='#426392')
        self._var_repetition_ignore_words.pack(side=tk.LEFT, padx=(0, 5))
        self._var_repetition_ignore_words.insert(0.0, cfg.get(cfg.CFG_REPETITION_IGNORE_WORDS))

        # End repetition
        f = tk.Frame(f_repetition, border=0, height=3 if IS_OSX else 5)
        f.pack()
        f.pack_propagate(0)

        # Font format
        f = tk.Frame(f0, border=0, relief=tk.GROOVE)
        f.pack(fill='both')
        tk.Label(f, text='Output font format', width=label_w, anchor='w').pack(side=tk.LEFT, padx=5)
        self._var_output_font_format = tk.BooleanVar(self.root)
        self._var_output_font_format.set(cfg.get(cfg.CFG_OUTPUT_FONT_FORMAT))
        tk.Checkbutton(f, variable=self._var_output_font_format).pack(side=tk.LEFT)

        # Save
        fbuttons = tk.Frame(f0)
        fbuttons.pack(side=tk.BOTTOM, expand=True)
        ut.Button(fbuttons, text=ut.button_text('Save'), command=self._save,
                  relief=tk.GROOVE).pack(pady=(12 if IS_OSX else 8, 0))

        # Update
        self.root.update()

    def close(self) -> None:
        """
        Close the window.
        """
        if self.on_destroy:
            self.on_destroy()
        self.root.destroy()

    def _save(self) -> None:
        """
        Save the settings.
        """
        store: Tuple[Tuple[str, str, str], ...] = (
            (self._cfg.CFG_PIPELINE, self._var_pipeline.get(),
             'Invalid pipeline value'),
            (self._cfg.CFG_CHECK_REPETITION, self._var_check_repetition.get(),
             'Invalid repetition value'),
            (self._cfg.CFG_REPETITION_DISTANCE, self._var_repetition_distance.get(),
             'Repetition distance be greater than 2'),
            (self._cfg.CFG_REPETITION_IGNORE_WORDS, self._var_repetition_ignore_words.get(0.0, tk.END),
             'Invalid ignore words'),
            (self._cfg.CFG_REPETITION_MIN_CHAR, self._var_repetition_min_char.get(),
             'Repetition min chars must be greater than zero'),
            (self._cfg.CFG_REPETITION_USE_STEMMING, self._var_check_repetition_stemming.get(),
             'Invalid repetition stemming value'),
            (self._cfg.CFG_REPETITION_USE_STOPWORDS, self._var_check_repetition_stopwords.get(),
             'Invalid repetition stemming value'),
            (self._cfg.CFG_OUTPUT_FONT_FORMAT, self._var_output_font_format.get(),
             'Invalid output font format value')
        )
        do_close = True
        for cfg in store:
            try:
                self._cfg.set(cfg[0], cfg[1])
            except ValueError:
                messagebox.showerror('Error', cfg[2])
                do_close = False
        self._cfg.save()
        if do_close:
            self.close()


class Settings(object):
    """
    Settings.
    """

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
        pipelines = list(_PIPELINES.keys())
        self._default_settings = {
            self.CFG_CHECK_REPETITION: (False, bool, [True, False]),
            self.CFG_OUTPUT_FONT_FORMAT: (True, bool, [True, False]),
            self.CFG_PIPELINE: (pipelines[0], str, pipelines),
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


# noinspection PyShadowingNames,PyMissingOrEmptyDocstring
class RichText(tk.Text):
    """
    Rich text.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        default_font = tkfont.nametofont(self.cget('font'))

        em = default_font.measure('m')
        default_size = default_font.cget('size')

        bold_font = tkfont.Font(**default_font.configure())
        bold_italic_font = tkfont.Font(**default_font.configure())
        h1_font = tkfont.Font(**default_font.configure())
        italic_font = tkfont.Font(**default_font.configure())
        normal_font = tkfont.Font(**default_font.configure())
        underlined_font = tkfont.Font(**default_font.configure())

        bold_font.configure(weight='bold')
        italic_font.configure(slant='italic')
        bold_italic_font.configure(weight='bold', slant='italic')
        h1_font.configure(size=int(default_size * 2), weight='bold')
        underlined_font.configure(underline=True)

        self.tag_configure('bold', font=bold_font)
        self.tag_configure('bold_italic', font=bold_italic_font)
        self.tag_configure('h1', font=h1_font, spacing3=default_size)
        self.tag_configure('italic', font=italic_font)
        self.tag_configure('normal', font=normal_font)
        self.tag_configure('underlined', font=underlined_font, spacing3=default_size)

        lmargin2 = em + default_font.measure("\u2022 ")
        self.tag_configure('bullet', lmargin1=em, lmargin2=lmargin2)

    def insert_bullet(self, index, text):
        self.insert(index, f'\u2022 {text}', 'bullet')
