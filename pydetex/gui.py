"""
PyDetex
https://github.com/ppizarror/PyDetex

GUI
Basic gui that convers and executes a given pipeline.
"""

__all__ = ['PyDetexGUI']

import concurrent.futures
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox

import os
import pyperclip
import requests
import string
import sys

from nltk.tokenize import RegexpTokenizer
from outdated import check_outdated
from PyMultiDictionary import MultiDictionary
from typing import Optional, Tuple
from warnings import warn

sys.path.append('../')

import pydetex._gui_utils as gui_ut
import pydetex.pipelines as pip
import pydetex.utils as ut
import pydetex.version

from pydetex._fonts import FONT_TAGS
from pydetex._gui_settings import Settings
from pydetex.parsers import FONT_FORMAT_SETTINGS as PARSER_FONT_FORMAT

# Settings
_MAX_PASTE_RETRY: int = 3


class PyDetexGUI(object):
    """
    GUI.
    """

    _cfg: 'Settings'
    _copy_clip: 'tk.Button'
    _detect_language_event_id: str
    _detected_lang_tag: str
    _dictionary: 'MultiDictionary'
    _dictionary_window: Optional['gui_ut.DictionaryGUI']
    _dictionary_btn: 'tk.Button'
    _paste_timeout_error: int
    _ready: bool
    _root: 'tk.Tk'
    _settings_window: Optional['gui_ut.SettingsWindow']
    _status_bar_cursor: 'tk.Label'
    _status_bar_cursor_sel: 'tk.Label'
    _status_bar_lang: 'tk.Label'
    _status_bar_status: 'tk.Label'
    _status_bar_words: 'tk.Label'
    _status_clear_event_id: str
    _text_in: 'gui_ut.RichText'
    _text_out: 'gui_ut.RichText'
    _tokenizer: 'RegexpTokenizer'

    def __init__(self) -> None:
        """
        Constructor.
        """

        # ----------------------------------------------------------------------
        # Creates the window
        # ----------------------------------------------------------------------
        self._root = tk.Tk()

        # Dictionary
        self._dictionary = MultiDictionary()
        self._dictionary_window = None

        # Load settings
        self._cfg = Settings()
        window_size = self._cfg.get(self._cfg.CFG_WINDOW_SIZE).copy()

        # Configure window
        self._root.title('PyDetex')
        img = tk.Image('photo', file=ut.RESOURCES_PATH + 'icon.gif')
        # noinspection PyProtectedMember
        self._root.tk.call('wm', 'iconphoto', self._root._w, img)
        if not ut.IS_OSX:
            self._root.iconbitmap(ut.RESOURCES_PATH + 'icon.ico')

        self._root.minsize(width=window_size[0], height=window_size[1])
        self._root.resizable(width=False, height=False)
        gui_ut.center_window(self._root, window_size)
        self._root.protocol('WM_DELETE_WINDOW', self._close)

        # ----------------------------------------------------------------------
        # Settings button
        # ----------------------------------------------------------------------
        f0 = tk.Frame(self._root, border=10, width=window_size[0], height=50)
        f0.pack()
        f0.pack_propagate(0)
        tk.Button(f0, text=ut.button_text(self._cfg.lang('open_file')), command=self._open_file,
                  relief=tk.GROOVE).pack(side=tk.LEFT)
        tk.Button(f0, text=ut.button_text(self._cfg.lang('about')), command=self._about,
                  relief=tk.GROOVE).pack(side=tk.RIGHT)
        tk.Button(f0, text=ut.button_text(self._cfg.lang('settings')), command=self._open_settings,
                  relief=tk.GROOVE).pack(side=tk.RIGHT, padx=(0, 7 if ut.IS_OSX else 11))
        self._dictionary_btn = tk.Button(f0, text=ut.button_text(self._cfg.lang('dictionary')),
                                         command=self._open_dictionary, relief=tk.GROOVE)
        self._dictionary_btn.pack(side=tk.RIGHT, padx=(0, 7 if ut.IS_OSX else 11))

        hthick, hcolor = 3 if ut.IS_OSX else 1, '#426392' if ut.IS_OSX else '#475aff'
        fsize = self._cfg.get(self._cfg.CFG_FONT_SIZE)

        # ----------------------------------------------------------------------
        # Input texts
        # ----------------------------------------------------------------------
        # In text
        f1 = tk.Frame(self._root, border=0, width=window_size[0], height=window_size[2])
        f1.pack(fill='both', padx=10)
        f1.pack_propagate(0)

        self._text_in = gui_ut.RichText(self._cfg, f1, wrap='word', highlightthickness=hthick,
                                        highlightcolor=hcolor, font_size=fsize, editable=True)
        self._text_in.pack(fill='both')
        self._text_in.bind('<Button>', self._process_cursor_in)
        self._text_in.bind('<ButtonRelease>', self._process_cursor_in)
        self._text_in.bind('<FocusIn>', self._process_focusin_in)
        self._text_in.bind('<FocusOut>', self._process_focusout_in)
        self._text_in.bind('<Key>', self._process_in_key)

        # Out text
        f2 = tk.Frame(self._root, border=0, width=window_size[0], height=window_size[2])
        f2.pack(fill='both', padx=10, pady=5)
        f2.pack_propagate(0)

        self._text_out = gui_ut.RichText(self._cfg, f2, wrap='word', highlightthickness=hthick,
                                         highlightcolor=hcolor, font_size=fsize, copy=True)
        self._text_out.bind('<Key>', self._process_out_key)
        self._text_out.pack(fill='both')

        # ----------------------------------------------------------------------
        # Commands buttons
        # ----------------------------------------------------------------------
        command_btn_packx = 15  # margin px
        f3 = tk.Frame(self._root, border=2)
        f3.pack(pady=(9, 18))

        # Process
        ut.Button(f3, text=ut.button_text(self._cfg.lang('process')), command=self._process, relief=tk.GROOVE,
                  bg='#475aff' if ut.IS_OSX else '#6388ff').pack(side=tk.LEFT, padx=(0, command_btn_packx))

        # Process clip
        tk.Button(f3, text=ut.button_text(self._cfg.lang('process_clip')), command=self._process_clip,
                  relief=tk.GROOVE).pack(side=tk.LEFT, padx=(0, command_btn_packx))

        # Copy to clip
        self._copy_clip = tk.Button(f3, text=ut.button_text(self._cfg.lang('process_copy')), command=self._copy_to_clip,
                                    relief=tk.GROOVE)
        self._copy_clip.pack(side=tk.LEFT, padx=(0, command_btn_packx))

        # Clear
        ut.Button(f3, text=ut.button_text(self._cfg.lang('clear')), command=self._clear,
                  relief=tk.GROOVE, bg='#ff7878').pack(side=tk.LEFT)

        # ----------------------------------------------------------------------
        # Status bar
        # ----------------------------------------------------------------------
        ttk.Separator(self._root, orient='horizontal').pack(side='top', fill='x')
        status_fg = '#999999' if ut.IS_OSX else '#666666'

        f4 = tk.Frame(self._root, width=window_size[0], height=26)
        f4.pack(fill='both')
        f4.pack_propagate(0)

        # Detected language
        show_status = 0.2 if window_size[0] > 750 else 0
        self._status_bar_lang = gui_ut.make_label(f4, w=window_size[0] * (0.4 + (0.2 - show_status)), h=20,
                                                  side=tk.LEFT, fg=status_fg, bd=0, relief=tk.SUNKEN, anchor=tk.W,
                                                  pad=(0, 0, 0, 10), separator=True)

        # Status
        self._status_bar_status = gui_ut.make_label(f4, w=window_size[0] * show_status, h=20, side=tk.LEFT,
                                                    fg=status_fg, bd=0, relief=tk.SUNKEN, anchor=tk.W, pad=(0, 0, 0, 5),
                                                    separator=True)

        # Cursor
        self._status_bar_cursor = gui_ut.make_label(f4, w=window_size[0] * 0.11, h=20, side=tk.LEFT, fg=status_fg,
                                                    bd=0, relief=tk.SUNKEN, anchor=tk.W, pad=(0, 0, 0, 5))

        # Cursor selected
        self._status_bar_cursor_sel = gui_ut.make_label(f4, w=window_size[0] * 0.14, h=20, side=tk.LEFT, fg=status_fg,
                                                        bd=0, relief=tk.SUNKEN, anchor=tk.W, pad=(0, 0, 0, 5),
                                                        separator=True)

        # Total processed words
        self._status_bar_words = gui_ut.make_label(f4, w=window_size[0] * 0.15, h=20, side=tk.LEFT, fg=status_fg,
                                                   bd=0, relief=tk.SUNKEN, anchor=tk.W, pad=(0, 0, 0, 5))

        # ----------------------------------------------------------------------
        # Final settings
        # ----------------------------------------------------------------------
        self._status_clear_event_id = ''
        self._clear()  # This also changes states

        # Set variables
        self._detect_language_event_id = ''
        self._detected_lang_tag = '–'
        self._paste_timeout_error = 0
        self._ready = False
        self._settings_window = None
        self._tokenizer = RegexpTokenizer(r'\w+')

        # Inserts the placeholder text
        self._insert_in(self._cfg.lang('placeholder'))
        self._root.update()

    def _open_file(self) -> None:
        """
        Opens a file.
        """
        self._status(self._cfg.lang('status_requesting_file'))
        last_path_cfg = self._cfg.get(self._cfg.CFG_LAST_OPENED_FOLDER)
        initial_dir = '/' if not os.path.isdir(last_path_cfg) else last_path_cfg
        filename = filedialog.askopenfilename(
            title=self._cfg.lang('open_file_select'),
            initialdir=initial_dir,
            filetypes=[(self._cfg.lang('open_file_latex_file'), '*.tex')])
        if filename == '':
            return self._status_clear()
        filename_dir = os.path.dirname(filename)
        self._cfg.set(self._cfg.CFG_LAST_OPENED_FOLDER, filename_dir)
        try:
            f = open(filename, 'r')
            text = ''.join(f.readlines())
            f.close()
            self._clear()
            self._insert_in(text)
            self._cfg.save()
        except PermissionError:
            pass

    def _insert_in(self, text: str) -> None:
        """
        Insert text to in widget.

        :param text: Text
        """
        self._text_in.insert(tk.END, text)
        self._detect_language()
        self._process_cursor_in(None)

    def _status(self, text: str, clear: bool = False, clear_time: int = 500) -> None:
        """
        Set the app status.

        :param text: Status text
        :param clear: Clear after time
        :param clear_time: Clear time in miliseconds
        """
        if self._status_clear_event_id != '':
            self._root.after_cancel(self._status_clear_event_id)
        self._status_bar_status['text'] = text
        if clear:
            self._status_clear_event_id = self._root.after(clear_time, self._status_clear)

    def _status_clear(self) -> None:
        """
        Clear the status text.
        """
        self._status(self._cfg.lang('status_idle'))

    # noinspection PyUnresolvedReferences
    def _process_in_key(self, event: 'tk.Event') -> Optional['tk.Event']:
        """
        Process in keys.

        :param event: Event
        :return: Event
        """
        if self._detect_language_event_id != '':
            self._root.after_cancel(self._detect_language_event_id)

        if event.char in string.printable and event.char != '':
            self._status(self._cfg.lang('status_writing'), True)
        else:
            self._status_clear()
        self._detect_language_event_id = self._root.after(100, self._detect_language)
        self._process_cursor_in(event)
        return event

    def _process_cursor_in(self, event: Optional['tk.Event']) -> Optional['tk.Event']:
        """
        Process cursor on input text.

        :param event: Event
        :return: Event
        """
        self._root.after(50, self._process_cursor_event)
        return event

    def _process_focusin_in(self, event: Optional['tk.Event']) -> Optional['tk.Event']:
        """
        Process focus in on input text.

        :param event: Event
        :return: Event
        """
        self._process_cursor_in(event)
        return event

    def _process_focusout_in(self, event: Optional['tk.Event']) -> Optional['tk.Event']:
        """
        Process focus out on input text.

        :param event: Event
        :return: Event
        """
        fout = self._cfg.lang('status_cursor_input_focusout')
        w = self._cfg.get(self._cfg.CFG_WINDOW_SIZE)[0]
        if w < 1000:
            fout = self._cfg.lang('status_cursor_input_focusout_min')
        if w < 750:
            fout = self._cfg.lang('status_cursor_input_focusout_min2')
        self._status_bar_cursor['text'] = fout
        self._status_bar_cursor_sel['text'] = ''
        return event

    def _process_cursor_event(self) -> None:
        """
        Process cursor position.
        """
        window_w = self._cfg.get(self._cfg.CFG_WINDOW_SIZE)[0]
        cur_pos = self._text_in.index(tk.INSERT)

        # Check cursor position
        if cur_pos is None:
            self._status_bar_cursor['text'] = self._cfg.lang('status_cursor_null')
        else:
            line, pos = tuple(cur_pos.split('.'))
            cur_t = self._cfg.lang('status_cursor') if window_w > 750 else self._cfg.lang('status_cursor_min')
            self._status_bar_cursor['text'] = cur_t.format(pos, line)

        # Get cursor selection
        try:
            sf = self._text_in.count('1.0', 'sel.first')
            sl = self._text_in.count('1.0', 'sel.last')
            if sf is None:
                sf = (0,)
            d = sl[0] - sf[0]
            sel = self._cfg.lang('status_cursor_selected') if window_w > 750 else self._cfg.lang(
                'status_cursor_selected_min')
            chars = self._cfg.lang('status_cursor_selected_chars') if window_w > 900 else self._cfg.lang(
                'status_cursor_selected_chars_min')
            s = f'{sel}: '
            text = self._text_in.get(0.0, tk.END)
            if d == 1:
                self._status_bar_cursor_sel['text'] = \
                    s + self._cfg.lang('status_cursor_selected_chars_single')
            elif d == len(text) or d == len(text.strip()):
                self._status_bar_cursor_sel['text'] = self._cfg.lang('status_cursor_selected_all')
            else:
                self._status_bar_cursor_sel['text'] = s + chars.format(d)

        except tk.TclError:
            self._status_bar_cursor_sel['text'] = ''

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

    def _detect_language(self) -> None:
        """
        Detects the input lang.
        """
        text = self._text_in.get(0.0, tk.END).strip()

        # Check language
        self._detected_lang_tag = ut.detect_language(text)
        lang = self._dictionary.get_language_name(self._detected_lang_tag, self._cfg.get(self._cfg.CFG_LANG))
        if text != '':
            self._status_bar_lang['text'] = self._cfg.lang('detected_lang').format(lang, self._detected_lang_tag)
        else:
            self._status_bar_lang['text'] = self._cfg.lang('detected_lang_write')
        self._detect_language_event_id = ''

        # Check if dictionary is available
        # noinspection PyProtectedMember
        if self._detected_lang_tag in self._dictionary._langs.keys():
            self._status_bar_lang['text'] += f' [{self._cfg.lang("dictionary")}]'
            self._dictionary_btn['state'] = tk.NORMAL
        else:
            self._dictionary_btn['state'] = tk.DISABLED

    def start(self) -> None:
        """
        Starts the application.
        """
        # noinspection PyProtectedMember
        if self._cfg._last_opened_day_diff >= 7:
            self._root.after(1000, self._check_version_event)
        self._root.after(100, lambda: self._root.lift())
        self._root.mainloop()

    def _clear(self) -> None:
        """
        Clear texts.
        """
        self._text_out['state'] = tk.NORMAL
        self._text_in.delete(0.0, tk.END)
        self._text_out.delete(0.0, tk.END)
        self._text_out['state'] = tk.DISABLED
        self._copy_clip['state'] = tk.DISABLED
        self._ready = False
        self._detect_language()
        self._status_bar_words['text'] = self._cfg.lang('status_words').format(0)
        self._status_clear()
        self._process_cursor_event()
        self._text_in.focus_force()

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
        text = self._text_in.get(0.0, tk.END)
        if text.strip() == '':
            return self._clear()
        self._status(self._cfg.lang('status_processing'), True)

        self._text_out['state'] = tk.NORMAL
        self._copy_clip['state'] = tk.NORMAL

        # Font format
        font_format = self._cfg.get(self._cfg.CFG_OUTPUT_FONT_FORMAT)
        PARSER_FONT_FORMAT['cite'] = FONT_TAGS['link'] if font_format else ''
        PARSER_FONT_FORMAT['equation'] = FONT_TAGS['italic'] if font_format else ''
        PARSER_FONT_FORMAT['normal'] = FONT_TAGS['normal'] if font_format else ''
        PARSER_FONT_FORMAT['ref'] = FONT_TAGS['link'] if font_format else ''
        PARSER_FONT_FORMAT['tex_text_tag'] = FONT_TAGS['bold'] if font_format else ''
        PARSER_FONT_FORMAT['tex_text_tag_content'] = FONT_TAGS['italic'] if font_format else ''

        # Process the text and get the language
        out = self.pipeline(text, self._detected_lang_tag)
        words = len(self._tokenizer.tokenize(out))
        self._cfg.add_words(words)

        # Check repeated words
        if self._cfg.get(self._cfg.CFG_CHECK_REPETITION):
            out = ut.check_repeated_words(
                s=out,
                lang=self._detected_lang_tag,
                min_chars=self._cfg.get(self._cfg.CFG_REPETITION_MIN_CHAR),
                window=self._cfg.get(self._cfg.CFG_REPETITION_DISTANCE),
                stopwords=self._cfg.get(self._cfg.CFG_REPETITION_USE_STOPWORDS),
                stemming=self._cfg.get(self._cfg.CFG_REPETITION_USE_STEMMING),
                ignore=self._tokenizer.tokenize(self._cfg.get(self._cfg.CFG_REPETITION_IGNORE_WORDS)),
                font_tag_format=FONT_TAGS['repeated_tag'] if font_format else '',
                font_param_format=FONT_TAGS['repeated_word'] if font_format else '',
                font_normal_format=FONT_TAGS['normal'] if font_format else '',
                remove_tokens=list(FONT_TAGS.values()),
                tag=self._cfg.lang('tag_repeated')
            )

        # Apply syntax highlight
        out = ut.syntax_highlight(out)

        # Insert the text
        self._text_out.insert_highlighted_text(out, True, font_format)

        # Configure status
        self._status_bar_words['text'] = self._cfg.lang('status_words').format(words)
        self._ready = True
        self._text_out['state'] = tk.DISABLED
        self._detect_language()

    def _process_clip(self) -> None:
        """
        Process from clipboard. Tries with pooling.
        """

        def _paste():
            return pyperclip.paste()

        self._status(self._cfg.lang('copy_from_clip'))
        executor = concurrent.futures.ThreadPoolExecutor(1)
        future = executor.submit(_paste)
        try:
            text = future.result(timeout=1)
        except concurrent.futures.TimeoutError:
            self._paste_timeout_error += 1
            if self._paste_timeout_error <= _MAX_PASTE_RETRY:
                # print(f'Paste process failed (TimeoutError), retrying {self._paste_timeout_error}/{_MAX_PASTE_RETRY}')
                self._root.after(100, self._process_clip)
            else:
                self._paste_timeout_error = 0
                error = f'Paste process failed after {_MAX_PASTE_RETRY} attempts'
                warn(error)
            return

        self._paste_timeout_error = 0
        if text.strip() == '':
            return
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
        delta_h = 0 if ut.IS_OSX else 21
        self._settings_window = gui_ut.SettingsWindow((375, 465 + delta_h), self._cfg)
        self._settings_window.on_destroy = self._close_settings
        try:
            # self._settings_window.root.mainloop(1)
            self._settings_window.root.update()
        except AttributeError:
            pass

    def _close_settings(self) -> None:
        """
        Close settings.
        """
        self._settings_window = None
        self._detect_language()
        if self._ready:
            self._process()

    def _get_selected_word(self) -> str:
        """
        Get selected word.

        :return: Return the current selected word
        """
        word = ''

        # Text in
        try:
            if self._text_in.selection_get() != '' and self._root.focus_get() == self._text_in:
                text = self._text_in.get(0.0, tk.END)
                sf = self._text_in.count('1.0', 'sel.first')
                se = self._text_in.count('1.0', 'sel.last')
                if sf is None:
                    sf = (0,)
                # print([text[sf[0]:se[0]]])
                word = ut.get_phrase_from_cursor(text, sf[0], se[0] - 1)
        except tk.TclError:
            pass

        # Text out
        try:
            if self._text_out.selection_get() != '' and self._root.focus_get() == self._text_out and word == '':
                text = self._text_out.get(0.0, tk.END)
                sf = self._text_out.count('1.0', 'sel.first')
                se = self._text_out.count('1.0', 'sel.last')
                if sf is None:
                    sf = (0,)
                word = ut.get_phrase_from_cursor(text, sf[0], se[0] - 1)
        except tk.TclError:
            pass

        # Apply pipeline
        word = pip.strict(word)
        word = ut.tokenize(word)
        return word

    def _open_dictionary(self) -> None:
        """
        Launch dictionary.
        """
        selected_word = self._get_selected_word()
        if self._dictionary_window:
            if selected_word != '':
                self._dictionary_window.insert_word(selected_word)
            self._dictionary_window.root.lift()
            self._dictionary_window.set_lang(self._detected_lang_tag)
            return
        self._dictionary_window = gui_ut.DictionaryGUI((340, 300), self._cfg, self._detected_lang_tag, self)
        self._dictionary_window.insert_word(selected_word)
        self._dictionary_window.on_destroy = self._close_dictionary
        try:
            self._dictionary_window.root.update()
        except (AttributeError, tk.TclError):
            pass

    def _close_dictionary(self) -> None:
        """
        Close dictionary.
        """
        self._dictionary_window = None

    def _close(self) -> None:
        """
        Close the window.
        """
        if self._settings_window:
            self._settings_window.close()
        if self._dictionary_window:
            self._dictionary_window.close()
        self._root.destroy()

    def _about(self) -> None:
        """
        Show about window.
        """
        _, _, ver = self._check_version()
        # f'{self._cfg.lang("about_author")}: {pydetex.__author__}\n\n' \
        n_app_opened = self._cfg.get(self._cfg.CFG_TOTAL_OPENED_APP)
        n_word_processed = self._cfg.get(self._cfg.CFG_TOTAL_PROCESSED_WORDS)
        msg = f'PyDetex v{pydetex.version.ver}\n' \
              f'{ver}\n\n' \
              f'{self._cfg.lang("about_opened")}: {ut.format_number_d(n_app_opened, self._cfg.lang("format_d"))}\n' \
              f'{self._cfg.lang("about_processed")}: {ut.format_number_d(n_word_processed, self._cfg.lang("format_d"))}\n\n' \
              f'{pydetex.__copyright__}'

        messagebox.showinfo(title=self._cfg.lang('about'), message=msg)

    def _check_version(self) -> Tuple[bool, str, str]:
        """
        Check software version.

        :return: (Needs software update, new version, version text about)
        """
        is_outdated = False
        latest_version = '0.0.0'
        # noinspection PyBroadException
        try:
            is_outdated, latest_version = check_outdated('pydetex', str(pydetex.version.ver))
            if is_outdated:
                about_ver = self._cfg.lang('about_ver_upgrade').format(latest_version)
            else:
                about_ver = self._cfg.lang('about_ver_latest')
        except ValueError:
            about_ver = self._cfg.lang('about_ver_dev')
        except requests.exceptions.ConnectionError:
            about_ver = self._cfg.lang('about_ver_err_conn')
        except Exception:
            about_ver = self._cfg.lang('about_ver_err_unkn')
        return is_outdated, latest_version, about_ver

    def _check_version_event(self) -> None:
        """
        Check the version. If outdated, raise a popup.
        """
        outdated, latest, _ = self._check_version()
        if outdated:
            messagebox.showinfo(
                title=self._cfg.lang('version_upgrade_title'),
                message=self._cfg.lang('version_upgrade').format(latest)
            )


if __name__ == '__main__':
    PyDetexGUI().start()
