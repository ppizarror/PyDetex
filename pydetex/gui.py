"""
PyDetex
https://github.com/ppizarror/pydetex

GUI
Basic gui that convers and executes a given pipeline.
"""

__all__ = ['PyDetexGUI']

import tkinter as tk

import platform
import os
import pyperclip

from typing import Callable, Tuple, Dict, Any, List, Type, Union
from warnings import warn

import pydetex.version
from pydetex.pipelines import simple_pipeline
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
    'simple_pipeline': simple_pipeline
}


class _SettingsWindow(object):
    """
    Settings window.
    """

    def __init__(self, window_size: Tuple[int, int]) -> None:
        """
        Constructor.
        """
        self.root = tk.Tk()

        # Configure window
        self.root.title('Settings')
        self.root.minsize(width=window_size[0], height=window_size[1])
        self.root.resizable(width=False, height=False)
        self.root.geometry('%dx%d+%d+%d' % (window_size[0], window_size[1],
                                            (self.root.winfo_screenwidth() - window_size[0]) / 2,
                                            (self.root.winfo_screenheight() - window_size[1]) / 2))


class _Settings(object):
    """
    Settings.
    """

    def __init__(self) -> None:
        """
        Constructor.
        """
        load = []
        try:
            f = open(_respath + 'settings.cfg', 'r')
            load = f.readlines()
            f.close()
        except FileNotFoundError:
            warn('Setting file could not be loaded or not exist. Creating new file')

        # Stores default settings and the valid values
        default_settings: Dict[str, Tuple[str, Type, Union[List[Any], Callable[[Any], bool]]]] = {
            'PIPELINE': ('simple_pipeline', str, list(_PIPELINES.keys())),
            'CHECK_REPETITION': (True, bool, [True, False]),
            'REPETITION_MIN_CHAR': (4, int, lambda x: x > 0),
            'TOTAL_PROCESSED_WORDS': (0, int, lambda x: x > 0)
        }

        # The valid settings
        self._settings = {}
        for k in default_settings.keys():
            self._settings[k] = default_settings[k][0]

        # Load the user settings
        for f in load:
            if '=' in f:  # If string has control character
                sp = f.split('=')
                if len(sp) != 2:
                    continue
                j = sp[0].strip()
                val = sp[1].strip()

                # Apply custom values
                if val == 'True':
                    val = True
                elif val == 'False':
                    val = False
                elif val.isdigit():
                    val = int(val)
                else:
                    try:
                        val = float(val)
                    except ValueError:
                        pass

                if j in default_settings.keys():  # Setting exist
                    val_type = default_settings[j][1]
                    val_valids = default_settings[j][2]
                    # Check val type
                    if not isinstance(val, val_type):
                        warn('Stored setting {0} should be type {1}'.format(j, val_type))
                        continue
                    if isinstance(val_valids, list):
                        if val in val_valids:  # Setting is within valid ones
                            self._settings[j] = val  # Update setting value
                        else:
                            warn('Stored setting {0} value should have these values: {1}'
                                 .format(j, ','.join(val_valids)))
                    else:  # Is a function
                        if not val_valids(val):
                            warn('Stored setting {0} do not pass valid test'.format(j))
                        else:
                            self._settings[j] = val  # Update setting value

        # Save the settings
        self.save()

    def get(self, key: str) -> Any:
        """
        Return the settings value.

        :param key: Setting key
        :return: Value
        """
        val = self._settings[key]

        # Update for some values
        if key == 'PIPELINE':
            val = _PIPELINES[val]

        return val

    def add_words(self, w: int) -> None:
        """
        Add processed words.

        :param w: Words
        """
        self._settings['TOTAL_PROCESSED_WORDS'] += w
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
    pipeline: Callable[[str], str]

    _cfg: '_Settings'
    _copy_clip: 'tk.Button'
    _label_lang: 'tk.Label'
    _ready: bool
    _root: 'tk.Tk'
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
            self._root.iconbitmap(_respath + 'icon.gif')
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

        # Settings button and detected language
        f0 = tk.Frame(self._root, border=10, width=700, height=45)
        f0.pack()
        f0.pack_propagate(0)
        Button(f0, text='Settings', command=self._open_settings, relief=tk.GROOVE).pack(side=tk.LEFT)
        self._label_lang = tk.Label(f0, fg='#CCCCCC')
        self._label_lang.pack(side=tk.RIGHT)

        f1 = tk.Frame(self._root, border=0)
        f1.pack()
        self._text_in = tk.Text(f1, wrap='word', height=11)
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

        # Set the pipeline
        self.pipeline = simple_pipeline

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

    def _process(self) -> None:
        """
        Process and call the pipeline.
        """
        self._text_out['state'] = tk.NORMAL
        self._copy_clip['state'] = tk.NORMAL

        # Process the text and get the language
        text = self._text_in.get(0.0, tk.END)
        out = self.pipeline(text)
        lang = ut.get_language_tag(ut.detect_language(out))
        words = len(out)
        self._cfg.add_words(words)

        # Write results
        self._text_out.delete(0.0, tk.END)
        self._text_out.insert(0.0, out)
        self._label_lang['text'] = 'Detected language: {0}, Words: {1}'.format(lang, words)
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
        app = _SettingsWindow((300, 400))
        app.root.mainloop(1)


if __name__ == '__main__':
    PyDetexGUI().start()
