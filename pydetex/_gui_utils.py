"""
PyDetex
https://github.com/ppizarror/PyDetex

GUI UTILS
Provides utils for the gui.
"""

__all__ = [
    'BorderedFrame',
    'center_window',
    'CustomEntry',
    'DictionaryGUI',
    'make_label',
    'RichText',
    'SettingsWindow'
]

import concurrent.futures
import textwrap
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from tkinter import messagebox

from PyMultiDictionary import MultiDictionary, DICT_THESAURUS
from typing import Callable, Tuple, Optional, Dict, Union, List, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pydetex.gui import PyDetexGUI

import pydetex._fonts as fonts
import pydetex.utils as ut
from pydetex._gui_settings import Settings as _Settings


class SettingsWindow(object):
    """
    Settings window.
    """

    _cfg: '_Settings'
    _dict_langs: Dict[str, str]
    _dict_pipelines: Dict[str, str]
    _pipeline_descr_title: 'tk.Label'
    _pipeline_description: 'tk.Label'
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
        center_window(self.root, window_size)
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
        self._var_pipeline.trace('w', self._change_description_pipeline)

        pipe = tk.OptionMenu(f, self._var_pipeline, *list(self._dict_pipelines.keys()))
        pipe.pack(side=tk.LEFT)

        f = tk.Frame(f0, border=0)
        f.pack(fill='both', pady=0)
        label_fg = '#999999' if ut.IS_OSX else '#666666'
        label_pad = 5 if ut.IS_OSX else 15
        self._pipeline_descr_title = make_label(f, w=70, h=40, side=tk.LEFT, fg=label_fg,  # bg='blue',
                                                bd=0, relief=tk.SUNKEN, anchor=tk.E, pad=(0, label_pad, 5, 7))
        self._pipeline_description = make_label(f, w=window_size[0] - 70, h=40, side=tk.LEFT, fg=label_fg,  # bg='red',
                                                bd=0, relief=tk.SUNKEN, anchor=tk.W, pad=(0, 0, 5, 0), justify=tk.LEFT)
        self._change_description_pipeline()

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
        self._var_repetition_min_char = CustomEntry(f, self._cfg, validate='all', validatecommand=(reg_int, '%P'),
                                                    width=5)
        self._var_repetition_min_char.pack(side=tk.LEFT)
        self.root.after(100, lambda: self._var_repetition_min_char.insert(0, cfg.get(cfg.CFG_REPETITION_MIN_CHAR)))

        # Repetition distance
        f = tk.Frame(f_repetition, border=0)
        f.pack(fill='both')
        tk.Label(f, text=self._cfg.lang('cfg_words_repetition_distance'), width=label_w, anchor='w').pack(
            side=tk.LEFT,
            padx=(5 if ut.IS_OSX else 4, 5 if ut.IS_OSX else 9)
        )
        self._var_repetition_distance = CustomEntry(f, self._cfg, validate='all',
                                                    validatecommand=(reg_int, '%P'), width=5)
        self._var_repetition_distance.pack(side=tk.LEFT)
        self.root.after(100, self._var_repetition_distance.insert(0, cfg.get(cfg.CFG_REPETITION_DISTANCE)))

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
        self._var_repetition_ignore_words = RichText(cfg, f, wrap='word', height=4,
                                                     highlightthickness=3 if ut.IS_OSX else 0,
                                                     highlightcolor='#426392', editable=True)
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

    # noinspection PyUnusedLocal
    def _change_description_pipeline(self, *args) -> None:
        """
        Event raised if pipeline is changed.

        :param args: Args
        """
        t = self._cfg.lang(f'{self._dict_pipelines[self._var_pipeline.get()]}_description')
        # t = f'{self._var_pipeline.get()}: {t}'
        t = '\n'.join(textwrap.wrap(t, 41 if ut.IS_OSX else 50))
        self._pipeline_descr_title['text'] = f'{self._var_pipeline.get()}:'
        self._pipeline_description['text'] = t

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


# noinspection PyProtectedMember
class DictionaryGUI(object):
    """
    Dictionary gui.
    """

    _ant: 'tk.Button'
    _cfg: '_Settings'
    _dictionary: 'MultiDictionary'
    _lang: str
    _main: 'PyDetexGUI'
    _mean: 'tk.Button'
    _query_active: Dict[str, int]
    _query_events_id: Dict[str, str]
    _query_max_trials: int
    _query_output: Dict[str, Any]
    _query_repeat_after: int
    _stemmer: bool
    _syn: 'tk.Button'
    root: 'tk.Tk'

    # noinspection PyProtectedMember
    def __init__(self, window_size: Tuple[int, int], cfg: '_Settings', lang: str, main: 'PyDetexGUI') -> None:
        """
        Constructor.

        :param window_size: Window size (width, height)
        :param cfg: Settings
        :param lang: Dictionary lang
        :param main: Main object
        """
        self.root = tk.Tk()
        self.on_destroy = None

        self._cfg = cfg  # Store setting reference
        self._dictionary = MultiDictionary()
        self._main = main
        self._stemmer = False

        # Configure window
        self.root.minsize(width=window_size[0], height=window_size[1])
        self.root.resizable(width=False, height=False)
        center_window(self.root, window_size)
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        if not ut.IS_OSX:
            self.root.iconbitmap(ut.RESOURCES_PATH + 'dictionary.ico')

        # Main frame
        f0 = tk.Frame(self.root, border=5)
        f0.pack(fill='both')

        # Word
        f = tk.Frame(f0, border=0)
        f.pack(fill='both', pady=5)
        tk.Label(f, text=self._cfg.lang('dictionary_word'), width=5, anchor='w').pack(side=tk.LEFT, padx=(5, 9))

        self._word = CustomEntry(f, self._cfg, width=30 if ut.IS_OSX else 50)
        self._word.pack(side=tk.LEFT)

        # Add commands
        f = tk.Frame(f0, border=0)
        f.pack(fill='both', pady=(5, 2))
        btn_width = 9
        btn_pad = 5 if ut.IS_OSX else 15
        self._mean = tk.Button(f, text=self._cfg.lang('dictionary_meaning'), command=self._meaning, relief=tk.GROOVE,
                               width=btn_width)
        self._mean.pack(padx=(0, btn_pad), side=tk.LEFT)
        self._syn = tk.Button(f, text=self._cfg.lang('dictionary_synonym'), command=self._synonym, relief=tk.GROOVE,
                              width=btn_width)
        self._syn.pack(padx=(0, btn_pad), side=tk.LEFT)
        self._ant = tk.Button(f, text=self._cfg.lang('dictionary_antonym'), command=self._antonym, relief=tk.GROOVE,
                              width=btn_width)
        self._ant.pack(padx=0, side=tk.LEFT)
        # f = tk.Frame(f0, border=0)
        # f.pack(fill='both', pady=(0, 5))
        # tk.Button(f, text=self._cfg.lang('dictionary_translation'), command=self._meaning, relief=tk.GROOVE, width=7).pack()

        # Out text
        f = tk.Frame(f0, border=0, width=window_size[0], height=50)
        f.pack(fill='both', pady=(5, 0))
        f.pack_propagate()

        hthick, hcolor = 3 if ut.IS_OSX else 1, '#426392' if ut.IS_OSX else '#475aff'

        self._text_out = RichText(self._cfg, f, wrap='word', highlightthickness=hthick,
                                  highlightcolor=hcolor, copy=True)
        self._text_out.bind('<Key>', self._process_out_key)
        self._text_out.pack(fill='both')
        self._text_out['state'] = tk.DISABLED

        # Set the language
        self.set_lang(lang)

        # Configure querys
        self._query_active = {}
        self._query_events_id = {}
        self._query_max_trials = 20
        self._query_output = {}
        self._query_repeat_after = 750

    def set_lang(self, lang: str) -> None:
        """
        Set language.

        :param lang: Language
        """
        if lang not in self._dictionary._langs.keys():
            self.close()
        lang_name = self._dictionary.get_language_name(lang, self._cfg.get(self._cfg.CFG_LANG))
        try:
            self.root.title(f'{self._cfg.lang("dictionary")} [{lang_name}]')
        except tk.TclError:
            pass
        self._lang = lang
        self._update_buttons()

    def _update_buttons(self, enable: bool = True) -> None:
        """
        Update app buttons.

        :param enable: Enable or disable
        :return:
        """
        # Check language capability
        try:
            syn, mean, _, ant = self._dictionary._langs[self._lang]
        except KeyError:
            syn, mean, ant = False, False, False
        try:
            self._syn['state'] = tk.NORMAL if (syn and enable) else tk.DISABLED
            self._mean['state'] = tk.NORMAL if (mean and enable) else tk.DISABLED
            self._ant['state'] = tk.NORMAL if (ant and enable) else tk.DISABLED
        except tk.TclError:
            pass

    @staticmethod
    def _process_out_key(event: 'tk.Event') -> Optional['tk.Event']:
        """
        Process out keys.

        :param event: Event
        :return: Event
        """
        # noinspection PyUnresolvedReferences
        if event.char == '':
            return event

    def _get_word(self) -> str:
        """
        Get the word.

        :return: Word
        """
        return self._word.get().strip()

    def _query_thread(self, key: str, query: Callable[[Any], Any], master: Callable[[], None], *args) -> None:
        """
        Starts a new query.

        :param key: Query key
        :param query: Query. Should save to _query_output
        :param master: Master (who called the query)
        """
        self._main._status(self._cfg.lang('dictionary_querying'))
        self._update_buttons(False)
        if key not in self._query_output.keys():
            if key not in self._query_active.keys():
                self._query_active[key] = 0
            after = self._query_repeat_after
            if self._query_active[key] == 0:
                self._write(self._cfg.lang('dictionary_loading'))
                executor = concurrent.futures.ThreadPoolExecutor(1)
                executor.submit(query, *args)
                after = 50
            self._query_active[key] += 1
            if self._query_active[key] <= self._query_repeat_after * self._query_max_trials:
                self._query_events_id[key] = self.root.after(after, master)
            else:
                self._write(self._cfg.lang('dictionary_timeout'))

    def _query_output_pop(self, key: str) -> Any:
        """
        Pop the output.

        :param key: Key
        :return: Data
        """
        if key not in self._query_output.keys():
            return None
        data = self._query_output[key]
        del self._query_output[key]
        del self._query_active[key]
        self._main._status_clear()
        self._update_buttons()
        if self._query_events_id[key] != '':
            self.root.after_cancel(self._query_events_id[key])
            self._query_events_id[key] = ''
        return data

    def _meaning(self) -> None:
        """
        Word meaning.
        """
        key = 'meaning'

        def _process(word: str):
            self._query_output[key] = self._dictionary.meaning(self._lang, word)
            self._query_active[key] = 0
            return

        self._query_thread(key, _process, self._meaning, self._get_word())
        data = self._query_output_pop(key)
        if data is None:
            return
        style, mean, wiki = data
        if mean == '':
            return self._write(self._cfg.lang('dictionary_no_results'))
        style = ', '.join(style)
        self._text_out['state'] = tk.NORMAL
        self._text_out.clear()
        self._text_out.insert('end', f'{style}\n\n', 'bold')
        self._text_out.insert('end', f'{self._cfg.lang("dictionary_meaning")}:\n', 'italic')
        self._text_out.insert('end', mean, 'normal')
        if wiki != '':
            self._text_out.insert('end', '\n\n', 'normal')
            self._text_out.insert('end', f'{self._cfg.lang("dictionary_wikipedia")}:\n', 'italic')
            self._text_out.insert('end', f'{wiki}', 'normal')
        self._text_out['state'] = tk.DISABLED

    def _synonym(self) -> None:
        """
        Word synonym.
        """
        key = 'synonym'

        def _process(word: str):
            if self._lang == 'en':
                self._query_output[key] = self._dictionary.synonym(self._lang, word, DICT_THESAURUS)
            else:
                self._query_output[key] = self._dictionary.synonym(self._lang, word)
            self._query_active[key] = 0
            return

        self._query_thread(key, _process, self._synonym, self._get_word())
        syn = self._query_output_pop(key)
        if syn is None:
            return
        if len(syn) == 0:
            return self._write(self._cfg.lang('dictionary_no_results'))
        self._write(', '.join(syn))

    def _antonym(self) -> None:
        """
        Word aynonym.
        """
        key = 'antonym'

        def _process(word: str):
            self._query_output[key] = self._dictionary.antonym(self._lang, word)
            self._query_active[key] = 0
            return

        self._query_thread(key, _process, self._antonym, self._get_word())
        ant = self._query_output_pop(key)
        if ant is None:
            return
        if len(ant) == 0:
            return self._write(self._cfg.lang('dictionary_no_results'))
        self._write(', '.join(ant))

    def _write(self, text: str) -> None:
        """
        Write a text.

        :param text: Text
        """
        self._text_out['state'] = tk.NORMAL
        self._text_out.delete(0.0, tk.END)
        self._text_out.insert(0.0, text)
        self._text_out['state'] = tk.DISABLED

    def insert_word(self, word: str) -> None:
        """
        Insert a word to the fields.

        :param word: Word
        """
        try:
            self._text_out.clear()
            self._word.delete(0, tk.END)
            stemmer = ut.make_stemmer(self._lang)
            if stemmer is not None and self._stemmer:
                word = stemmer.stem(word)
            self.root.after(50, lambda: self._word.insert(0, word))
        except tk.TclError:
            pass

    def close(self) -> None:
        """
        Close the window.
        """
        if self.on_destroy:
            self.on_destroy()
        self.root.destroy()


# noinspection PyShadowingNames,PyMissingOrEmptyDocstring
class RichText(tk.Text):
    """
    Rich text.
    """

    _default_font: 'tkfont.Font'
    _default_size: int
    _em: int

    def __init__(self, cfg: '_Settings', *args, **kwargs):
        font_size = kwargs.pop('font_size', 11)
        editable = kwargs.pop('editable', False)
        copy = kwargs.pop('copy', False)
        if editable:
            kwargs['undo'] = True

        super().__init__(*args, **kwargs)
        self._default_font = tkfont.nametofont(self.cget('font'))
        self._default_font.configure(size=font_size)

        self._em = self._default_font.measure('m')
        self._default_size = self._default_font.cget('size')

        # Editable gui
        if editable:
            EditableTextGUI(self, cfg)
        elif copy:
            CopyTextGUI(self, cfg)

        # Configure specials
        self.tag_configure('bullet', lmargin1=self._em,
                           lmargin2=self._em + self._default_font.measure('\u2022 '))

        # Add fonts
        for tag in fonts.FONT_PROPERTIES.keys():
            style = fonts.FONT_PROPERTIES[tag]
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

    def insert_bullet(self, index: float, text: str) -> None:
        """
        Inserts a bullet.

        :param index: Position
        :param text: Text
        """
        self.insert(index, f'\u2022 {text}', 'bullet')

    def insert_highlighted_text(self, s: str, clear: bool = False, font_format: bool = True) -> None:
        """
        Insert a highlighted text.

        :param s: Text
        :param clear: Clear before insert
        :param font_format: If False, use normal font instead
        """
        # Write results and split tags
        if clear:
            self.clear()
        for t in ut.split_tags(s, list(fonts.FONT_TAGS.values())):
            tag, text = t
            self.insert('end', text, fonts.TAGS_FONT[tag] if font_format else 'normal')

    def clear(self) -> None:
        """
        Clears the text.
        """
        self.delete(0.0, tk.END)


# noinspection PyUnresolvedReferences,PyUnusedLocal
class EditableTextGUI(object):
    """
    Editable gui text.
    """

    _w: Union['tk.Entry', 'tk.Text', 'RichText']

    def __init__(self, widget: Union['tk.Entry', 'tk.Text', 'RichText'], cfg: '_Settings') -> None:
        """
        Constructor.

        :param widget: Widget object
        :param cfg: Settings
        """
        self._w = widget

        self.changes = ['']
        self.steps = int()

        self.context_menu = tk.Menu(self._w, tearoff=0)
        self.context_menu.add_command(label=cfg.lang('menu_cut'))
        self.context_menu.add_command(label=cfg.lang('menu_copy'))
        self.context_menu.add_command(label=cfg.lang('menu_paste'))

        self._w.bind('<Button-3>' if not ut.IS_OSX else '<Button-2>', self.popup)
        self._w.bind('<Control-z>', self.undo)
        self._w.bind('<Control-y>', self.redo)
        self._w.bind('<Key>', self.add_changes)

        if ut.IS_OSX:
            self._w.bind('<Control-c>', lambda _: self._w.event_generate('<<Copy>>'))
            self._w.bind('<Control-v>', lambda _: self._w.event_generate('<<Paste>>'))

    def popup(self, event: 'tk.Event') -> None:
        """
        Raise popup.

        :param event: Event
        """
        self.context_menu.post(event.x_root, event.y_root)
        self.context_menu.entryconfigure('Cut', command=lambda: self._w.event_generate('<<Cut>>'))
        self.context_menu.entryconfigure('Copy', command=lambda: self._w.event_generate('<<Copy>>'))
        self.context_menu.entryconfigure('Paste', command=lambda: self._w.event_generate('<<Paste>>'))

    def undo(self, event: Optional['tk.Event'] = None) -> None:
        """
        Undo operation.

        :param event: Event
        """
        if self.steps != 0:
            self.steps -= 1
            self._w.delete(0, tk.END)
            self._w.insert(tk.END, self.changes[self.steps])

    def redo(self, event: Optional['tk.Event'] = None) -> None:
        """
        Redo operation.

        :param event: Event
        """
        if self.steps < len(self.changes):
            self._w.delete(0, tk.END)
            self._w.insert(tk.END, self.changes[self.steps])
            self.steps += 1

    def add_changes(self, event: Optional['tk.Event'] = None) -> None:
        """
        Add changes.

        :param event: Event
        """
        if self._w.get() != self.changes[-1]:
            self.changes.append(self._w.get())
            self.steps += 1


# noinspection PyUnresolvedReferences,PyUnusedLocal
class CopyTextGUI(object):
    """
    Enables a menu for only copy.
    """

    _w: Union['tk.Entry', 'tk.Text', 'RichText']

    def __init__(self, widget: Union['tk.Entry', 'tk.Text', 'RichText'], cfg: '_Settings') -> None:
        """
        Constructor.

        :param widget: Widget object
        :param cfg: Settings
        """
        self._w = widget

        self.context_menu = tk.Menu(self._w, tearoff=0)
        self.context_menu.add_command(label=cfg.lang('menu_copy'))

        self._w.bind('<Button-3>' if not ut.IS_OSX else '<Button-2>', self.popup)

        if ut.IS_OSX:
            self._w.bind('<Control-c>', lambda _: self._w.event_generate('<<Copy>>'))

    def popup(self, event: 'tk.Event') -> None:
        """
        Raise popup.

        :param event: Event
        """
        self.context_menu.post(event.x_root, event.y_root)
        self.context_menu.entryconfigure('Copy', command=lambda: self._w.event_generate('<<Copy>>'))


class CustomEntry(tk.Entry):
    """
    Entry with undo/redo and menu.
    """

    def __init__(self, parent, cfg: '_Settings', *args, **kwargs):
        tk.Entry.__init__(self, parent, *args, **kwargs)
        EditableTextGUI(self, cfg)


class BorderedFrame(tk.Frame):
    """
    Bordered frame widget.
    """

    def __init__(self, master, bordercolor=None, borderleft=0, bordertop=0, borderright=0, borderbottom=0,
                 interiorwidget=tk.Frame, **kwargs):
        tk.Frame.__init__(self, master, background=bordercolor, bd=0, highlightthickness=0)

        self.interior = interiorwidget(self, **kwargs)
        self.interior.pack(padx=(borderleft, borderright), pady=(bordertop, borderbottom))


def center_window(root: 'tk.Tk', window_size: Union[Tuple[int, int], List[int]]) -> None:
    """
    Center window.

    :param root: Window object
    :param window_size: Window size
    """
    if ut.IS_OSX:
        root.geometry('%dx%d+%d+%d' % (window_size[0], window_size[1],
                                       (root.winfo_screenwidth() - window_size[0]) / 2,
                                       (root.winfo_screenheight() - window_size[1]) / 2 - 25))
    else:
        root.geometry('%dx%d+%d+%d' % (window_size[0], window_size[1],
                                       (root.winfo_screenwidth() - window_size[0]) / 2,
                                       (root.winfo_screenheight() - window_size[1]) / 2))


def make_label(master, h, w, side, *args, pad=(0, 0, 0, 0), separator=False, **kwargs) -> 'tk.Label':
    """
    Makes a label with defined width/height.

    :param master: Master object
    :param h: Height in pixels
    :param w: Width in pixels
    :param side: Packing side
    :param args: Label arguments
    :param pad: Padding (top, right, bottom, left)
    :param separator: Add separator
    :param kwargs: Optional keyword-arguments
    :return: Label
    """
    f = tk.Frame(master, height=int(h), width=int(w))
    f.pack_propagate(0)  # don't shrink
    f.pack(side=side)
    label = tk.Label(f, *args, **kwargs)
    if w > 0:
        label.pack(fill=tk.BOTH, expand=1, padx=(int(pad[3]), int(pad[1])), pady=(int(pad[0]), int(pad[2])))
        if separator:
            ttk.Separator(master, orient='vertical').pack(side=tk.LEFT, fill='y')
    return label
