"""
PyDetex
https://github.com/ppizarror/pydetex

GUI
Basic gui that convers and executes a given pipeline.
"""

__all__ = ['PyDetexGUI']

import tkinter as tk
from tkinter import messagebox

import pyperclip
import requests
import sys

from outdated import check_outdated
from nltk.tokenize import RegexpTokenizer
from typing import Optional

sys.path.append('../')

import pydetex.version
import pydetex.pipelines as pip
import pydetex.utils as ut

from pydetex._gui_settings import Settings
from pydetex._gui_utils import SettingsWindow, RichText
from pydetex.parsers import FONT_FORMAT_SETTINGS as PARSER_FONT_FORMAT

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


class PyDetexGUI(object):
    """
    GUI.
    """

    _cfg: 'Settings'
    _copy_clip: 'tk.Button'
    _label_lang: 'tk.Label'
    _ready: bool
    _root: 'tk.Tk'
    _settings_window: Optional['SettingsWindow']
    _text_in: 'tk.Text'
    _text_out: 'tk.Text'
    _tokenizer: 'RegexpTokenizer'

    def __init__(self) -> None:
        """
        Constructor.
        """
        self._root = tk.Tk()

        # Load settings
        self._cfg = Settings()
        window_size = self._cfg.get(self._cfg.CFG_WINDOW_SIZE).copy()

        # Fine-tune height based on font size
        fsize = self._cfg.get(self._cfg.CFG_FONT_SIZE)
        if not ut.IS_OSX:
            if window_size[3] == 0:  # small
                if fsize == 9 or fsize == 13:
                    window_size[1] += 5
                elif fsize == 11:
                    window_size[1] -= 10
            elif window_size[3] >= 1:  # medium
                if fsize == 15:
                    window_size[1] += 5
                elif fsize == 11:
                    window_size[1] -= 30
                elif fsize == 10:
                    window_size[1] -= 20

        else:
            if window_size[3] == 2:  # large
                if fsize == 15:
                    window_size[1] += 10
                elif fsize == 13:
                    window_size[1] -= 5
                elif fsize == 11:
                    window_size[1] -= 10
                elif fsize == 10:
                    window_size[1] -= 20

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
        self._root.geometry('%dx%d+%d+%d' % (window_size[0], window_size[1],
                                             (self._root.winfo_screenwidth() - window_size[0]) / 2,
                                             (self._root.winfo_screenheight() - window_size[1]) / 2))
        self._root.protocol('WM_DELETE_WINDOW', self._close)

        # Settings button and detected language
        f0 = tk.Frame(self._root, border=10, width=window_size[0], height=50)
        f0.pack()
        f0.pack_propagate(0)
        tk.Button(f0, text=ut.button_text(self._cfg.lang('settings')), command=self._open_settings,
                  relief=tk.GROOVE).pack(side=tk.LEFT, padx=(0, 7 if ut.IS_OSX else 10))
        tk.Button(f0, text=ut.button_text(self._cfg.lang('about')), command=self._about,
                  relief=tk.GROOVE).pack(side=tk.LEFT)
        self._label_lang = tk.Label(f0, fg='#999999' if ut.IS_OSX else '#666666')
        self._label_lang.pack(side=tk.RIGHT)

        hthick, hcolor = 3 if ut.IS_OSX else 1, '#426392' if ut.IS_OSX else '#475aff'

        f1 = tk.Frame(self._root, border=0)
        hfactor = 0.6
        defaultfz = 11 if ut.IS_OSX else 10

        f1.pack(fill='both', padx=10)
        self._text_in = RichText(f1, wrap='word', height=window_size[2] - (fsize - defaultfz) * hfactor, undo=True,
                                 highlightthickness=hthick, highlightcolor=hcolor,
                                 font_size=fsize)
        self._text_in.pack(fill='both')
        self._text_in.focus_force()
        self._text_in.focus()

        f2 = tk.Frame(self._root, border=0)
        f2.pack(fill='both', padx=10, pady=5)
        self._text_out = RichText(f2, wrap='word', height=window_size[2] - (fsize - defaultfz) * hfactor,
                                  highlightthickness=hthick,
                                  highlightcolor=hcolor, font_size=fsize)
        self._text_out.bind('<Key>', self._process_out_key)
        self._text_out.pack(fill='both')

        f3 = tk.Frame(self._root, border=2)
        f3.pack(pady=(5 if ut.IS_OSX else 10, 0))

        ut.Button(f3, text=ut.button_text(self._cfg.lang('process')), command=self._process, relief=tk.GROOVE,
                  bg='#475aff' if ut.IS_OSX else '#6388ff').pack(side=tk.LEFT)
        tk.Label(f3, text='    ').pack(side=tk.LEFT)

        tk.Button(f3, text=ut.button_text(self._cfg.lang('process_clip')), command=self._process_clip,
                  relief=tk.GROOVE).pack(side=tk.LEFT)
        tk.Label(f3, text='    ').pack(side=tk.LEFT)

        self._copy_clip = tk.Button(f3, text=ut.button_text(self._cfg.lang('process_copy')), command=self._copy_to_clip,
                                    relief=tk.GROOVE)
        self._copy_clip.pack(side=tk.LEFT)
        tk.Label(f3, text='    ').pack(side=tk.LEFT)

        ut.Button(f3, text=ut.button_text(self._cfg.lang('clear')), command=self._clear,
                  relief=tk.GROOVE, bg='#ff7878').pack(side=tk.LEFT)
        # tk.Label(f3, text='    ').pack(side=tk.LEFT)

        self._settings_window = None

        # Write basic text
        self._clear()  # This also changes states
        self._text_in.insert(0.0, self._cfg.lang('placeholder'))
        self._ready = False
        self._tokenizer = RegexpTokenizer(r'\w+')

        self._root.update()

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
        text = self._text_in.get(0.0, tk.END)
        if text.strip() == '':
            return

        self._text_out['state'] = tk.NORMAL
        self._copy_clip['state'] = tk.NORMAL

        # Font format
        font_format = self._cfg.get(self._cfg.CFG_OUTPUT_FONT_FORMAT)

        # Configure text
        PARSER_FONT_FORMAT['cite'] = _FONT_TAGS['bold'] if font_format else ''
        PARSER_FONT_FORMAT['normal'] = _FONT_TAGS['normal'] if font_format else ''
        PARSER_FONT_FORMAT['ref'] = _FONT_TAGS['bold'] if font_format else ''

        # Process the text and get the language
        out = self.pipeline(text)
        lang_code = ut.detect_language(out)
        lang = ut.get_language_tag(lang_code)
        words = len(self._tokenizer.tokenize(out))
        self._cfg.add_words(words)

        # Add formats
        out = _FONT_TAGS['normal'] + out
        tags = list(_FONT_TAGS.values())

        # Check repeated words
        if self._cfg.get(self._cfg.CFG_CHECK_REPETITION):
            out = ut.check_repeated_words(
                s=out,
                lang=lang_code,
                min_chars=self._cfg.get(self._cfg.CFG_REPETITION_MIN_CHAR),
                window=self._cfg.get(self._cfg.CFG_REPETITION_DISTANCE),
                stopwords=self._cfg.get(self._cfg.CFG_REPETITION_USE_STOPWORDS),
                stemming=self._cfg.get(self._cfg.CFG_REPETITION_USE_STEMMING),
                ignore=self._tokenizer.tokenize(self._cfg.get(self._cfg.CFG_REPETITION_IGNORE_WORDS)),
                font_tag_format=_FONT_TAGS['italic'] if font_format else '',
                font_param_format=_FONT_TAGS['bold'] if font_format else '',
                font_normal_format=_FONT_TAGS['normal'] if font_format else '',
                remove_tokens=tags,
                tag=self._cfg.lang('tag_repeated')
            )

        # Write results
        self._text_out.delete(0.0, tk.END)
        for t in ut.split_tags(out, tags):
            tag, text = t
            self._text_out.insert('end', text, _TAGS_FONT[tag])

        self._label_lang['text'] = self._cfg.lang('detected_lang').format(lang, lang_code, words)
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
        self._settings_window = SettingsWindow((365, 425 if ut.IS_OSX else 445), self._cfg)
        self._settings_window.on_destroy = self._close_settings
        try:
            self._settings_window.root.mainloop(1)
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
        # Get current package version
        ver = ''

        # noinspection PyBroadException
        try:
            is_outdated, latest_version = check_outdated('pydetex', str(pydetex.version.ver))
            if is_outdated:
                ver = self._cfg.lang('about_ver_upgrade').format(latest_version)
        except ValueError:
            ver = self._cfg.lang('about_ver_dev')
        except requests.exceptions.ConnectionError:
            ver = self._cfg.lang('about_ver_err_conn')
        except Exception:
            ver = self._cfg.lang('about_ver_err_unkn')

        msg = f'PyDetex v{pydetex.version.ver}\n' \
              f'{self._cfg.lang("about_author")}: {pydetex.__author__}\n\n' \
              f'{self._cfg.lang("about_processed")}: {self._cfg.get(self._cfg.CFG_TOTAL_PROCESSED_WORDS)}\n\n' \
              f'{ver}'
        messagebox.showinfo(title='About', message=msg)


if __name__ == '__main__':
    PyDetexGUI().start()
