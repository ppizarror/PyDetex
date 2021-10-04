"""
PyDetex
https://github.com/ppizarror/pydetex

GUI
Basic gui that convers and executes a given pipeline.
"""

__all__ = ['PyDetexGUI']

import tkinter as tk
from tkmacosx import Button

import platform
import os
from typing import Callable
import pyperclip

from pydetex.pipelines import simple_pipeline

# Check OS
IS_OSX = platform.system() == 'Darwin'

if IS_OSX:
    PROGRAMSIZE = 700, 360
else:
    PROGRAMSIZE = 700, 415

# Set resouces path
__actualpath = str(os.path.abspath(os.path.dirname(__file__))).replace('\\', '/') + '/'
respath = __actualpath + 'res/'


class PyDetexGUI(object):
    """
    GUI.
    """
    pipeline: Callable[[str], str]

    _copy_clip: 'tk.Button'
    _ready: bool
    _root: 'tk.Tk'
    _text_in: 'tk.Text'
    _text_out: 'tk.Text'

    def __init__(self) -> None:
        """
        Constructor.
        """
        self._root = tk.Tk()

        # Configure window
        self._root.title('PyDetex')
        if platform.system() == 'Darwin':
            self._root.iconbitmap(respath + 'icon.gif')
            img = tk.Image('photo', file=respath + 'icon.gif')
            # noinspection PyProtectedMember
            self._root.tk.call('wm', 'iconphoto', self._root._w, img)
        else:
            self._root.iconbitmap(respath + 'icon.ico')
        self._root.minsize(width=PROGRAMSIZE[0], height=PROGRAMSIZE[1])
        self._root.resizable(width=False, height=False)
        self._root.geometry('%dx%d+%d+%d' % (PROGRAMSIZE[0], PROGRAMSIZE[1],
                                             (self._root.winfo_screenwidth() - PROGRAMSIZE[0]) / 2,
                                             (self._root.winfo_screenheight() - PROGRAMSIZE[1]) / 2))

        f1 = tk.Frame(self._root, border=5)
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
        text = self._text_in.get(0.0, tk.END)
        out = self.pipeline(text)
        self._text_out.delete(0.0, tk.END)
        self._text_out.insert(0.0, out)
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


if __name__ == '__main__':
    PyDetexGUI().start()
