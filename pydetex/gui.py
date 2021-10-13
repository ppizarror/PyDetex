"""
PyDetex
https://github.com/ppizarror/pydetex

GUI
Basic gui that convers and executes a given pipeline.
"""

__all__ = ['PyDetexGUI']

import tkinter as tk
from tkinter import messagebox

import platform
import os
import pyperclip

from typing import Callable, Tuple, Dict, Any, List, Type, Union, Optional
from warnings import warn

import pydetex.version
import pydetex.pipelines as pip
import pydetex.utils as ut

# Check OS
IS_OSX = platform.system() == 'Darwin'

if IS_OSX:
    from tkmacosx import Button

    PROGRAMSIZE = 700, 400
else:
    from tkinter import Button

    PROGRAMSIZE = 700, 475

# Set resouces path
__actualpath = str(os.path.abspath(os.path.dirname(__file__))).replace('\\', '/') + '/'
_respath = __actualpath + 'res/'

# Store the pipelines
_PIPELINES = {
    'Simple': pip.simple_pipeline
}


def _validate_int(p: str) -> bool:
    """
    Validate an integer.

    :param p: Value
    :return: True if integer
    """
    if p == '' or p == '-':
        return True
    try:
        p = float(p)
        return int(p) == p
    except ValueError:
        pass
    return False


def _validate_float(p: str) -> bool:
    """
    Validate a float.

    :param p: Value
    :return: True if integer
    """
    if p == '' or p == '-':
        return True
    try:
        float(p)
        return True
    except ValueError:
        pass
    return False


class _SettingsWindow(object):
    """
    Settings window.
    """

    _cfg: '_Settings'
    on_destroy: Optional[Callable[[], None]]

    def __init__(self, window_size: Tuple[int, int], cfg: '_Settings') -> None:
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

        # Registers
        reg_int = self.root.register(_validate_int)

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

        tk.OptionMenu(f, self._var_pipeline, *list(_PIPELINES.keys())).pack(side=tk.LEFT)

        # Check repetition
        f_repetition = tk.LabelFrame(f0, text='Words repetition', bd=1)
        f_repetition.pack(fill='both')

        f = tk.Frame(f_repetition, border=0, relief=tk.GROOVE)
        f.pack(fill='both')
        tk.Label(f, text='Check', width=label_w, anchor='w').pack(side=tk.LEFT, padx=5)
        self._var_check_repetition = tk.BooleanVar(self.root)
        self._var_check_repetition.set(cfg.get(cfg.CFG_CHECK_REPETITION))
        tk.Checkbutton(f, variable=self._var_check_repetition).pack(side=tk.LEFT)

        # Repetition min chars
        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text='Repetition min chars', width=label_w, anchor='w').pack(side=tk.LEFT, padx=5)
        self._var_repetition_min_char = tk.Entry(f, validate='all', validatecommand=(reg_int, '%P'))
        self._var_repetition_min_char.pack(side=tk.LEFT)
        self._var_repetition_min_char.insert(0, cfg.get(cfg.CFG_REPETITION_MIN_CHAR))

        # Repetition distance
        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text='Repetition distance', width=label_w, anchor='w').pack(side=tk.LEFT, padx=5)
        self._var_repetition_distance = tk.Entry(f, validate='all', validatecommand=(reg_int, '%P'))
        self._var_repetition_distance.pack(side=tk.LEFT)
        self._var_repetition_distance.insert(0, cfg.get(cfg.CFG_REPETITION_DISTANCE))

        # Repetition use stemming
        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text='Use stemming', width=label_w, anchor='w').pack(side=tk.LEFT, padx=5)
        self._var_check_repetition_stemming = tk.BooleanVar(self.root)
        self._var_check_repetition_stemming.set(cfg.get(cfg.CFG_REPETITION_USE_STEMMING))
        tk.Checkbutton(f, variable=self._var_check_repetition_stemming).pack(side=tk.LEFT)

        # Repetition use stopwords
        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text='Use stopwords', width=label_w, anchor='w').pack(side=tk.LEFT, padx=5)
        self._var_check_repetition_stopwords = tk.BooleanVar(self.root)
        self._var_check_repetition_stopwords.set(cfg.get(cfg.CFG_REPETITION_USE_STOPWORDS))
        tk.Checkbutton(f, variable=self._var_check_repetition_stopwords).pack(side=tk.LEFT)

        # Repetition ignore words
        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text='Repetition ignore words', width=label_w, anchor='w').pack(side=tk.LEFT, padx=5)
        self._var_repetition_ignore_words = tk.Text(f, wrap='word', height=4)
        self._var_repetition_ignore_words.pack(side=tk.LEFT)
        self._var_repetition_ignore_words.insert(0.0, cfg.get(cfg.CFG_REPETITION_IGNORE_WORDS))

        # Save
        fbuttons = tk.Frame(f0, border=10)
        fbuttons.pack(side=tk.BOTTOM, expand=True)
        Button(fbuttons, text='Save', command=self._save, relief=tk.GROOVE).pack()

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
             'Invalid repetition stemming value')
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


class _Settings(object):
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
                f = open(_respath + 'settings.cfg', 'r')
                load = f.readlines()
                f.close()
            except FileNotFoundError:
                warn('Setting file could not be loaded or not exist. Creating new file')

        # General settings
        self.CFG_CHECK_REPETITION = 'CHECK_REPETITION'
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
            self.CFG_PIPELINE: (pipelines[0], str, pipelines),
            self.CFG_REPETITION_DISTANCE: (15, int, lambda x: x > 1),
            self.CFG_REPETITION_IGNORE_WORDS: ('', str, None),
            self.CFG_REPETITION_MIN_CHAR: (4, int, lambda x: x > 0),
            self.CFG_REPETITION_USE_STEMMING: (True, bool, [True, False]),
            self.CFG_REPETITION_USE_STOPWORDS: (True, bool, [True, False]),
            self.CFG_TOTAL_PROCESSED_WORDS: (0, int, lambda x: x >= 0),
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
        f = open(_respath + 'settings.cfg', 'w')
        keys = list(self._settings.keys())
        keys.sort()
        for k in keys:
            f.write('{0} = {1}\n'.format(k, str(self._settings[k])))
        f.close()


class PyDetexGUI(object):
    """
    GUI.
    """

    _cfg: '_Settings'
    _copy_clip: 'tk.Button'
    _label_lang: 'tk.Label'
    _ready: bool
    _root: 'tk.Tk'
    _settings_window: Optional['_SettingsWindow']
    _text_in: 'tk.Text'
    _text_out: 'tk.Text'

    def __init__(self) -> None:
        """
        Constructor.
        """
        self._root = tk.Tk()

        # Load settings
        self._cfg = _Settings()

        # Configure window
        self._root.title('PyDetex v{}'.format(pydetex.version.ver))
        if platform.system() == 'Darwin':
            # self._root.iconbitmap(_respath + 'icon.gif')
            img = tk.Image('photo', file=_respath + 'icon.gif')
            # noinspection PyProtectedMember
            self._root.tk.call('wm', 'iconphoto', self._root._w, img)
        else:
            self._root.iconbitmap(_respath + 'icon.ico')
        self._root.minsize(width=PROGRAMSIZE[0], height=PROGRAMSIZE[1])
        self._root.resizable(width=False, height=False)
        self._root.geometry('%dx%d+%d+%d' % (PROGRAMSIZE[0], PROGRAMSIZE[1],
                                             (self._root.winfo_screenwidth() - PROGRAMSIZE[0]) / 2,
                                             (self._root.winfo_screenheight() - PROGRAMSIZE[1]) / 2))
        self._root.protocol('WM_DELETE_WINDOW', self._close)

        # Settings button and detected language
        f0 = tk.Frame(self._root, border=10, width=700, height=45)
        f0.pack()
        f0.pack_propagate(0)
        Button(f0, text='Settings', command=self._open_settings, relief=tk.GROOVE).pack(side=tk.LEFT)
        self._label_lang = tk.Label(f0, fg='#CCCCCC')
        self._label_lang.pack(side=tk.RIGHT)

        f1 = tk.Frame(self._root, border=0)
        f1.pack()
        self._text_in = tk.Text(f1, wrap='word', height=11, undo=True)
        self._text_in.pack()
        self._text_in.focus_force()
        self._text_in.focus()

        f2 = tk.Frame(self._root, border=5)
        f2.pack()
        self._text_out = tk.Text(f2, wrap='word', height=11)
        self._text_out.pack()

        f3 = tk.Frame(self._root, border=2)
        f3.pack()

        Button(f3, text='Process', command=self._process, relief=tk.GROOVE, bg='#475aff').pack(side=tk.LEFT)
        tk.Label(f3, text='    ').pack(side=tk.LEFT)

        tk.Button(f3, text='Process from clipboard', command=self._process_clip, relief=tk.GROOVE).pack(side=tk.LEFT)
        tk.Label(f3, text='    ').pack(side=tk.LEFT)

        self._copy_clip = tk.Button(f3, text='Copy to clipboard', command=self._copy_to_clip, relief=tk.GROOVE)
        self._copy_clip.pack(side=tk.LEFT)
        tk.Label(f3, text='    ').pack(side=tk.LEFT)

        Button(f3, text='Clear', command=self._clear, relief=tk.GROOVE, bg='#ff7878').pack(side=tk.LEFT)
        # tk.Label(f3, text='    ').pack(side=tk.LEFT)

        self._settings_window = None

        # Write basic text
        self._clear()  # This also changes states
        self._text_in.insert(0.0, 'Write or paste here your LaTeX code')
        self._ready = False

    def start(self) -> None:
        """
        Starts the application.
        """
        self._root.mainloop()

    def _clear(self) -> None:
        """
        Clear texts.
        """
        self._text_in.delete(0.0, tk.END)
        self._text_out.delete(0.0, tk.END)
        self._text_out['state'] = tk.DISABLED
        self._copy_clip['state'] = tk.DISABLED
        self._ready = False

    @property
    def pipeline(self) -> pip.PipelineType:
        """
        Return the pipeline.

        :return: Pipeline
        """
        return self._cfg.get(self._cfg.CFG_PIPELINE)

    def _process(self) -> None:
        """
        Process and call the pipeline.
        """
        self._text_out['state'] = tk.NORMAL
        self._copy_clip['state'] = tk.NORMAL

        # Process the text and get the language
        text = self._text_in.get(0.0, tk.END)
        out = self.pipeline(text)
        lang_code = ut.detect_language(out)
        lang = ut.get_language_tag(lang_code)
        words = len(out)
        self._cfg.add_words(words)

        # Check repeated words
        if self._cfg.get(self._cfg.CFG_CHECK_REPETITION):
            out = ut.check_repeated_words(
                s=out,
                lang=lang_code,
                min_chars=self._cfg.get(self._cfg.CFG_REPETITION_MIN_CHAR),
                window=self._cfg.get(self._cfg.CFG_REPETITION_DISTANCE),
                stopwords=self._cfg.get(self._cfg.CFG_REPETITION_USE_STOPWORDS),
                stemming=self._cfg.get(self._cfg.CFG_REPETITION_USE_STEMMING),
                ignore=self._cfg.get(self._cfg.CFG_REPETITION_IGNORE_WORDS).split(',')
            )

        # Write results
        self._text_out.delete(0.0, tk.END)
        self._text_out.insert(0.0, out)
        self._label_lang['text'] = 'Detected language: {0} ({1}). Words: {2}'.format(lang, lang_code, words)
        self._ready = True

    def _process_clip(self) -> None:
        """
        Process from clipboard.
        """
        text = pyperclip.paste()
        self._text_in.delete(0.0, tk.END)
        self._text_in.insert(0.0, text)
        self._process()

    def _get_pipeline_results(self) -> str:
        """
        Returns the pipeline results.

        :return: Text
        """
        return str(self._text_out.get(0.0, tk.END)).strip()

    def _copy_to_clip(self) -> None:
        """
        Copy results to clip.
        """
        text = self._text_out.get(0.0, tk.END)
        pyperclip.copy(text)

    def _open_settings(self) -> None:
        """
        Launch settings.
        """
        if self._settings_window:
            self._settings_window.root.lift()
            return
        self._settings_window = _SettingsWindow((340, 300), self._cfg)
        self._settings_window.on_destroy = self._close_settings
        self._settings_window.root.mainloop(1)

    def _close_settings(self) -> None:
        """
        Close settings.
        """
        self._settings_window = None

    def _close(self) -> None:
        """
        Close the window.
        """
        if self._settings_window:
            self._settings_window.close()
        self._root.destroy()


if __name__ == '__main__':
    PyDetexGUI().start()
