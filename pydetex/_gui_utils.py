"""
PyDetex
https://github.com/ppizarror/pydetex

GUI UTILS
Provides utils for the gui.
"""

__all__ = [
    'SettingsWindow',
    'RichText'
]

import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox

from typing import Callable, Tuple, Optional, Dict

import pydetex.utils as ut
from pydetex._fonts import FONT_PROPERTIES
from pydetex._gui_settings import Settings as _Settings


class SettingsWindow(object):
    """
    Settings window.
    """

    _cfg: '_Settings'
    _dict_langs: Dict[str, str]
    _dict_pipelines: Dict[str, str]
    _var_check_repetition: 'tk.BooleanVar'
    _var_check_repetition_stemming: 'tk.BooleanVar'
    _var_check_repetition_stopwords: 'tk.BooleanVar'
    _var_font_size: 'tk.StringVar'
    _var_lang: 'tk.StringVar'
    _var_output_font_format: 'tk.BooleanVar'
    _var_pipeline: 'tk.StringVar'
    _var_repetition_distance: 'tk.Entry'
    _var_repetition_ignore_words: 'tk.Text'
    _var_repetition_min_char: 'tk.Entry'
    _var_window_size: 'tk.StringVar'
    on_destroy: Optional[Callable[[], None]]
    root: 'tk.Tk'

    # noinspection PyProtectedMember
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
        if not ut.IS_OSX:
            self.root.iconbitmap(ut.RESOURCES_PATH + 'cog.ico')

        # Registers
        reg_int = self.root.register(ut.validate_int)

        # Main frame
        f0 = tk.Frame(self.root, border=5)
        f0.pack(fill='both')

        label_w = 17

        # Set languages
        f = tk.Frame(f0, border=0)
        f.pack(fill='both', pady=5)
        tk.Label(f, text=self._cfg.lang('cfg_lang'), width=label_w, anchor='w').pack(side=tk.LEFT, padx=(5, 9))

        self._dict_langs = {}
        for k in self._cfg._lang.get_available():
            self._dict_langs[self._cfg._lang.get(k, 'lang')] = k

        self._var_lang = tk.StringVar(self.root)
        self._var_lang.set(self._cfg._lang.get(cfg.get(cfg.CFG_LANG), 'lang'))  # default value

        pipe = tk.OptionMenu(f, self._var_lang, *list(self._dict_langs.keys()))
        pipe.focus()
        pipe.pack(side=tk.LEFT)

        # Window size
        f = tk.Frame(f0, border=0)
        f.pack(fill='both', pady=5)
        tk.Label(f, text=self._cfg.lang('cfg_window_size'), width=label_w, anchor='w').pack(side=tk.LEFT, padx=(5, 9))

        self._dict_window_sizes = {}
        for k in self._cfg._valid_window_sizes:
            self._dict_window_sizes[self._cfg.lang(k)] = k

        self._var_window_size = tk.StringVar(self.root)
        self._var_window_size.set(self._cfg.lang(cfg.get(cfg.CFG_WINDOW_SIZE, update=False)))  # default value

        windowsize = tk.OptionMenu(f, self._var_window_size, *list(self._dict_window_sizes.keys()))
        windowsize.pack(side=tk.LEFT)

        # Set pipelines
        f = tk.Frame(f0, border=0)
        f.pack(fill='both', pady=5)
        tk.Label(f, text=self._cfg.lang('cfg_pipeline'), width=label_w,
                 anchor='w').pack(side=tk.LEFT, padx=(5, 9 if ut.IS_OSX else 7))

        self._dict_pipelines = {}
        for k in self._cfg._available_pipelines:
            self._dict_pipelines[self._cfg.lang(k)] = k

        self._var_pipeline = tk.StringVar(self.root)
        self._var_pipeline.set(self._cfg.lang(cfg.get(cfg.CFG_PIPELINE, update=False)))  # default value

        pipe = tk.OptionMenu(f, self._var_pipeline, *list(self._dict_pipelines.keys()))
        pipe.pack(side=tk.LEFT)

        # Check repetition
        f_repetition = tk.LabelFrame(f0, text=self._cfg.lang('cfg_words_repetition'), bd=1, relief=tk.GROOVE)
        f_repetition.pack(fill='both')

        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text=self._cfg.lang('cfg_check'), width=label_w, anchor='w').pack(
            side=tk.LEFT,
            padx=(5 if ut.IS_OSX else 4, 4))
        self._var_check_repetition = tk.BooleanVar(self.root)
        self._var_check_repetition.set(cfg.get(cfg.CFG_CHECK_REPETITION))
        tk.Checkbutton(f, variable=self._var_check_repetition).pack(side=tk.LEFT)

        # Repetition min chars
        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text=self._cfg.lang('cfg_words_repetition_minchars'), width=label_w, anchor='w').pack(
            side=tk.LEFT,
            padx=(5 if ut.IS_OSX else 4, 5 if ut.IS_OSX else 9)
        )
        self._var_repetition_min_char = tk.Entry(f, validate='all', validatecommand=(reg_int, '%P'), width=5)
        self._var_repetition_min_char.pack(side=tk.LEFT)
        self._var_repetition_min_char.insert(0, cfg.get(cfg.CFG_REPETITION_MIN_CHAR))

        # Repetition distance
        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text=self._cfg.lang('cfg_words_repetition_distance'), width=label_w, anchor='w').pack(
            side=tk.LEFT,
            padx=(5 if ut.IS_OSX else 4, 5 if ut.IS_OSX else 9)
        )
        self._var_repetition_distance = tk.Entry(f, validate='all', validatecommand=(reg_int, '%P'), width=5)
        self._var_repetition_distance.pack(side=tk.LEFT)
        self._var_repetition_distance.insert(0, cfg.get(cfg.CFG_REPETITION_DISTANCE))

        # Repetition use stemming
        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text=self._cfg.lang('cfg_words_repetition_stemming'), width=label_w, anchor='w').pack(
            side=tk.LEFT,
            padx=(5 if ut.IS_OSX else 4, 4)
        )
        self._var_check_repetition_stemming = tk.BooleanVar(self.root)
        self._var_check_repetition_stemming.set(cfg.get(cfg.CFG_REPETITION_USE_STEMMING))
        tk.Checkbutton(f, variable=self._var_check_repetition_stemming).pack(side=tk.LEFT)

        # Repetition use stopwords
        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text=self._cfg.lang('cfg_words_repetition_stopwords'), width=label_w, anchor='w').pack(
            side=tk.LEFT,
            padx=(5 if ut.IS_OSX else 4, 4)
        )
        self._var_check_repetition_stopwords = tk.BooleanVar(self.root)
        self._var_check_repetition_stopwords.set(cfg.get(cfg.CFG_REPETITION_USE_STOPWORDS))
        tk.Checkbutton(f, variable=self._var_check_repetition_stopwords).pack(side=tk.LEFT)

        # Repetition ignore words
        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text=self._cfg.lang('cfg_words_repetition_ignorew'), width=label_w, anchor='w').pack(
            side=tk.LEFT,
            padx=(5 if ut.IS_OSX else 4, 5 if ut.IS_OSX else 9)
        )
        self._var_repetition_ignore_words = tk.Text(f, wrap='word', height=4, highlightthickness=3 if ut.IS_OSX else 0,
                                                    highlightcolor='#426392')
        self._var_repetition_ignore_words.pack(side=tk.LEFT, padx=(0, 5))
        self._var_repetition_ignore_words.insert(0.0, cfg.get(cfg.CFG_REPETITION_IGNORE_WORDS).strip())

        # End repetition
        f = tk.Frame(f_repetition, border=0, height=3 if ut.IS_OSX else 5)
        f.pack()
        f.pack_propagate(0)

        # Font format
        f = tk.Frame(f0, border=0, relief=tk.GROOVE)
        f.pack(fill='both')
        tk.Label(f, text=self._cfg.lang('cfg_font_format'), width=label_w,
                 anchor='w').pack(side=tk.LEFT, padx=(5, 9 if ut.IS_OSX else 7))
        self._var_output_font_format = tk.BooleanVar(self.root)
        self._var_output_font_format.set(cfg.get(cfg.CFG_OUTPUT_FONT_FORMAT))
        tk.Checkbutton(f, variable=self._var_output_font_format).pack(side=tk.LEFT)

        # Set font size
        f = tk.Frame(f0, border=0)
        f.pack(fill='both', pady=5)
        tk.Label(f, text=self._cfg.lang('cfg_font_size'), width=label_w,
                 anchor='w').pack(side=tk.LEFT, padx=(5, 9 if ut.IS_OSX else 7))

        self._var_font_size = tk.StringVar(self.root)
        self._var_font_size.set(cfg.get(cfg.CFG_FONT_SIZE))

        fontsize = tk.OptionMenu(f, self._var_font_size, *cfg._valid_font_sizes)
        fontsize.pack(side=tk.LEFT)

        # Save
        fbuttons = tk.Frame(f0)
        fbuttons.pack(side=tk.BOTTOM, expand=True)
        ut.Button(fbuttons, text=ut.button_text(self._cfg.lang('cfg_save')), command=self._save,
                  relief=tk.GROOVE).pack(pady=(12 if ut.IS_OSX else 8, 0))

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
        lang_value, current_lang = (self._dict_langs[self._var_lang.get()],
                                    self._cfg.get(self._cfg.CFG_LANG))
        windowsz_value, current_windowsz = (self._dict_window_sizes[self._var_window_size.get()],
                                            self._cfg.get(self._cfg.CFG_WINDOW_SIZE, update=False))
        fontsize_value, current_fontsize = (self._var_font_size.get(),
                                            self._cfg.get(self._cfg.CFG_FONT_SIZE))

        store: Tuple[Tuple[str, str, str], ...] = (
            (self._cfg.CFG_LANG, lang_value,
             self._cfg.lang('cfg_error_lang')),
            (self._cfg.CFG_WINDOW_SIZE, windowsz_value,
             self._cfg.lang('cfg_error_window_size')),
            (self._cfg.CFG_PIPELINE, self._dict_pipelines[self._var_pipeline.get()],
             self._cfg.lang('cfg_error_pipeline')),
            (self._cfg.CFG_CHECK_REPETITION, self._var_check_repetition.get(),
             self._cfg.lang('cfg_error_repetition')),
            (self._cfg.CFG_REPETITION_DISTANCE, self._var_repetition_distance.get(),
             self._cfg.lang('cfg_error_repetition_distance')),
            (self._cfg.CFG_REPETITION_IGNORE_WORDS, self._var_repetition_ignore_words.get(0.0, tk.END),
             self._cfg.lang('cfg_error_repetition_words')),
            (self._cfg.CFG_REPETITION_MIN_CHAR, self._var_repetition_min_char.get(),
             self._cfg.lang('cfg_error_repetition_chars')),
            (self._cfg.CFG_REPETITION_USE_STEMMING, self._var_check_repetition_stemming.get(),
             self._cfg.lang('cfg_error_stemming')),
            (self._cfg.CFG_REPETITION_USE_STOPWORDS, self._var_check_repetition_stopwords.get(),
             self._cfg.lang('cfg_error_stopwords')),
            (self._cfg.CFG_OUTPUT_FONT_FORMAT, self._var_output_font_format.get(),
             self._cfg.lang('cfg_error_output_format')),
            (self._cfg.CFG_FONT_SIZE, fontsize_value,
             self._cfg.lang('cfg_error_font_size'))
        )

        # Set values
        do_close = True
        for cfg in store:
            try:
                self._cfg.set(cfg[0], cfg[1])
            except ValueError:
                messagebox.showerror('Error', cfg[2])
                do_close = False

        # Check if lang has changed
        if lang_value != current_lang or int(fontsize_value) != current_fontsize or \
                windowsz_value != current_windowsz:
            messagebox.showinfo(title=self._cfg.lang('reload_message_title'),
                                message=self._cfg.lang('reload_message_message'))

        # Save
        self._cfg.save()
        if do_close:
            self.close()


# noinspection PyShadowingNames,PyMissingOrEmptyDocstring
class RichText(tk.Text):
    """
    Rich text.
    """

    _default_font: 'tkfont.Font'
    _default_size: int
    _em: int

    def __init__(self, *args, **kwargs):
        font_size = kwargs.pop('font_size', 11)
        super().__init__(*args, **kwargs)
        self._default_font = tkfont.nametofont(self.cget('font'))
        self._default_font.configure(size=font_size)

        self._em = self._default_font.measure('m')
        self._default_size = self._default_font.cget('size')

        # Configure specials
        self.tag_configure('bullet', lmargin1=self._em,
                           lmargin2=self._em + self._default_font.measure('\u2022 '))

        # Add fonts
        for tag in FONT_PROPERTIES.keys():
            style = FONT_PROPERTIES[tag]
            if style is None:
                continue
            self._add_font(tag, **style)

    def _add_font(self, tag: str, **kwargs) -> None:
        font = tkfont.Font(**self._default_font.configure())

        # Update kwargs for font
        if 'size' not in kwargs.keys():
            kwargs['size'] = self._default_size
        else:
            kwargs['size'] = int(kwargs['size'] * self._default_size)

        # Move kwargs to tag
        if kwargs.pop('ignore_font', False):
            tag_kwargs = {}
        else:
            tag_kwargs = {'font': font}
        for t in ['foreground', 'background', 'spacing3']:
            if t in kwargs.keys():
                tag_kwargs[t] = kwargs.pop(t)
        if 'spacing3' in tag_kwargs.keys():
            tag_kwargs['spacing3'] *= self._default_size

        font.configure(**kwargs)
        self.tag_configure(tag, **tag_kwargs)

    def insert_bullet(self, index, text):
        self.insert(index, f'\u2022 {text}', 'bullet')
