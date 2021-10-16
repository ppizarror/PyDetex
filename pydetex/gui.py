"""
PyDetex
https://github.com/ppizarror/pydetex

GUI
Basic gui that convers and executes a given pipeline.
"""

__all__ = ['PyDetexGUI']

import concurrent.futures
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import pyperclip
import requests
import sys

from outdated import check_outdated
from nltk.tokenize import RegexpTokenizer
from typing import Optional, Tuple
from warnings import warn

sys.path.append('../')

import pydetex._gui_utils as gui_ut
import pydetex.pipelines as pip
import pydetex.utils as ut
import pydetex.version

from pydetex._fonts import FONT_TAGS, TAGS_FONT
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
    _paste_timeout_error: int
    _ready: bool
    _root: 'tk.Tk'
    _settings_window: Optional['gui_ut.SettingsWindow']
    _status_bar_lang: 'tk.Label'
    _status_bar_status: 'tk.Label'
    _status_bar_words: 'tk.Label'
    _status_clear_event_id: str
    _text_in: 'tk.Text'
    _text_out: 'tk.Text'
    _tokenizer: 'RegexpTokenizer'

    def __init__(self) -> None:
        """
        Constructor.
        """

        # ----------------------------------------------------------------------
        # Creates the window
        # ----------------------------------------------------------------------
        self._root = tk.Tk()

        # Load settings
        self._cfg = Settings()
        window_size = self._cfg.get(self._cfg.CFG_WINDOW_SIZE).copy()

        # Configure window
        self._root.title('PyDetex')
        if ut.IS_OSX:
            img = tk.Image('photo', file=ut.RESOURCES_PATH + 'icon.gif')
            # noinspection PyProtectedMember
            self._root.tk.call('wm', 'iconphoto', self._root._w, img)
        else:
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
        tk.Button(f0, text=ut.button_text(self._cfg.lang('about')), command=self._about,
                  relief=tk.GROOVE).pack(side=tk.RIGHT)
        tk.Button(f0, text=ut.button_text(self._cfg.lang('settings')), command=self._open_settings,
                  relief=tk.GROOVE).pack(side=tk.RIGHT, padx=(0, 7 if ut.IS_OSX else 10))

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
                                        highlightcolor=hcolor, font_size=fsize)
        self._text_in.pack(fill='both')
        self._text_in.bind('<Key>', self._process_in_key)
        self._text_in.focus_force()
        self._text_in.focus()

        # Out text
        f2 = tk.Frame(self._root, border=0, width=window_size[0], height=window_size[2])
        f2.pack(fill='both', padx=10, pady=5)
        f2.pack_propagate(0)

        self._text_out = gui_ut.RichText(self._cfg, f2, wrap='word', highlightthickness=hthick,
                                         highlightcolor=hcolor, font_size=fsize, editable=False)
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
        self._status_bar_lang = gui_ut.make_label(f4, w=window_size[0] * 0.5, h=20, side=tk.LEFT, fg=status_fg,
                                                  bd=0, relief=tk.SUNKEN, anchor=tk.W, pad=(0, 0, 0, 10),
                                                  separator=True)

        # Status
        self._status_bar_status = gui_ut.make_label(f4, w=window_size[0] * 0.4, h=20, side=tk.LEFT, fg=status_fg,
                                                    bd=0, relief=tk.SUNKEN, anchor=tk.W, pad=(0, 0, 0, 5),
                                                    separator=True)

        # Total processed words
        self._status_bar_words = gui_ut.make_label(f4, w=window_size[0] * 0.1, h=20, side=tk.LEFT, fg=status_fg,
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
        self._text_in.insert(0.0, self._cfg.lang('placeholder'))
        self._detect_language()

        self._root.update()

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

    def _process_in_key(self, event: 'tk.Event') -> Optional['tk.Event']:
        """
        Process in keys.

        :param event: Event
        :return: Event
        """
        if self._detect_language_event_id != '':
            self._root.after_cancel(self._detect_language_event_id)

        self._status(self._cfg.lang('status_writing'), True)
        self._detect_language_event_id = self._root.after(100, self._detect_language)
        return event

    # noinspection PyUnresolvedReferences
    @staticmethod
    def _process_out_key(event: 'tk.Event') -> Optional['tk.Event']:
        """
        Process out keys.

        :param event: Event
        :return: Event
        """
        if event.char == '':
            return event

    def _detect_language(self) -> None:
        """
        Detects the input lang.
        """
        text = self._text_in.get(0.0, tk.END).strip()
        self._detected_lang_tag = ut.detect_language(text)
        lang = ut.get_language_tag(self._detected_lang_tag)
        if text != '':
            self._status_bar_lang['text'] = self._cfg.lang('detected_lang').format(lang, self._detected_lang_tag)
        else:
            self._status_bar_lang['text'] = self._cfg.lang('detected_lang_write')
        self._detect_language_event_id = ''

    def start(self) -> None:
        """
        Starts the application.
        """
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

        self._text_out['state'] = tk.NORMAL
        self._copy_clip['state'] = tk.NORMAL

        # Font format
        font_format = self._cfg.get(self._cfg.CFG_OUTPUT_FONT_FORMAT)
        PARSER_FONT_FORMAT['cite'] = FONT_TAGS['link'] if font_format else ''
        PARSER_FONT_FORMAT['normal'] = FONT_TAGS['normal'] if font_format else ''
        PARSER_FONT_FORMAT['ref'] = FONT_TAGS['link'] if font_format else ''

        # Process the text and get the language
        out = self.pipeline(text)
        words = len(self._tokenizer.tokenize(out))
        self._cfg.add_words(words)

        # Add formats
        tags = list(FONT_TAGS.values())

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
                remove_tokens=tags,
                tag=self._cfg.lang('tag_repeated')
            )

        # Apply syntax highlight
        out = ut.syntax_highlight(out)

        # Write results and split tags
        self._text_out.delete(0.0, tk.END)
        for t in ut.split_tags(out, tags):
            tag, text = t
            self._text_out.insert('end', text, TAGS_FONT[tag] if font_format else 'normal')

        self._status_bar_words['text'] = self._cfg.lang('status_words').format(words)
        self._ready = True

        # Lock output
        self._text_out['state'] = tk.DISABLED
        self._detect_language()

    def _process_clip(self) -> None:
        """
        Process from clipboard. Tries with pooling.
        """

        def _paste():
            return pyperclip.paste()

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
                warn(f'Paste process failed after {_MAX_PASTE_RETRY} attempts')
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
        self._settings_window = gui_ut.SettingsWindow((375, 427 if ut.IS_OSX else 448), self._cfg)
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
        if self._ready:
            self._process()

    def _close(self) -> None:
        """
        Close the window.
        """
        if self._settings_window:
            self._settings_window.close()
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

        messagebox.showinfo(title='About', message=msg)

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


if __name__ == '__main__':
    PyDetexGUI().start()
