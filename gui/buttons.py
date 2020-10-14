import tkinter as tk
import tkinter.messagebox
import subprocess
import threading
from typing import Tuple, List
from . import _kill_app


_palette = {
    "off": {
        "bg": "#fafafa",
        "activebackground": "#ffffff",
        "fg": "black",
        "activeforeground": "black",
    },
    "on": {
        "bg": "#0477FC",
        "activebackground": "#318ff9",
        "fg": "white",
        "activeforeground": "white",
    }
}


class SubprocessButton(tk.Button):
    def __init__(self, parent, kill_app: bool = _kill_app, *args, **kwargs):
        super(SubprocessButton, self).__init__(parent, *args, **kwargs)
        self._kill_app = kill_app
        self._subprocess = None
    
    def destroy(self):
        if self._kill_app and self.state:
            self._subprocess.kill()
            self._subprocess = None
        super(SubprocessButton, self).destroy()
    
    @property
    def state(self) -> bool:
        if self._subprocess is not None:
            self._subprocess.poll()
            if self._subprocess.returncode is None:
                return True
            else:
                self._subprocess = None
        return False
    
    @state.setter
    def state(self, value: bool):
        if self.state != value:
            if self.state:
                self._subprocess.kill()
                self._subprocess = None
            else:
                self.execute()
    
    def check_app(self) -> bool:
        return True
    
    def command(self):
        self.execute()
    
    def execute(self):
        if self.check_app():
            if self.state:
                    tk.messagebox.showwarning(*self._already_running)
            else:
                self._subprocess = subprocess.Popen(self._subprocess_args)
        else:
            tk.messagebox.showwarning(*self._check_fail)
    
    _already_running: str = ""
    _check_fail: Tuple[str, str] = "", ""
    _subprocess_args: List[str] = []


class ColorChangingButton(tk.Button):
    def __init__(
        self,
        parent,
        bg: Tuple[str, str] = (_palette["off"]["bg"], _palette["on"]["bg"]),
        activebackground: Tuple[str, str] = (_palette["off"]["activebackground"], _palette["on"]["activebackground"]),
        fg: Tuple[str, str] = (_palette["off"]["fg"], _palette["on"]["fg"]),
        activeforeground: Tuple[str, str] = (_palette["off"]["activeforeground"], _palette["on"]["activeforeground"]),
        *args,
        **kwargs
    ):
        super(ColorChangingButton, self).__init__(parent, *args, **kwargs)
        self._bg = bg
        self._activebackground = activebackground
        self._fg = fg
        self._activeforeground = activeforeground
        self.update()
    
    def update(self):
        s = self.state
        self.configure(bg=self._bg[s], activebackground=self._activebackground[s], fg=self._fg[s], activeforeground=self._activeforeground[s])
    
    def command(self):
        self.state = not self.state


class OnOffSubprocessButton(ColorChangingButton, SubprocessButton):
    @SubprocessButton.state.setter
    def state(self, value: bool):
        SubprocessButton.state.fset(self, value)
        self.update()


class ColorChangingSubprocessButton(ColorChangingButton, SubprocessButton):
    def __init__(self, parent, interval: float = 1, *args, **kwargs):
        super(ColorChangingSubprocessButton, self).__init__(parent, *args, **kwargs)
        self._interval = interval
        self._thread = None
        self.update_thread()
    
    def _update_thread(self):
        self.update()
        self.update_thread()
    
    def update_thread(self):
        self._thread = threading.Timer(self._interval, self._update_thread)
        self._thread.start()
        
    def command(self):
        self.execute()
        self.update()
    
    def destroy(self):
        if self._thread is not None:
            self._thread.cancel()
            self._thread = None
        super(ColorChangingSubprocessButton, self).destroy()
