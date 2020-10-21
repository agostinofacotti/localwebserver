import tkinter as tk
import tkinter.messagebox
from ..localwebserver import main as lws_main
from ..args import Args
from .button_frames import ButtonFrameBase
from .buttons import OnOffSubprocessButton, ColorChangingSubprocessButton
from multiprocessing import Process
from threading import Timer
import webbrowser
import os
from typing import Tuple, List


class AppButtonFrame(ButtonFrameBase):
    pass


class OpentronsButton(ColorChangingSubprocessButton, metaclass=AppButtonFrame.button):
    text: str = "Opentrons APP"
    
    def __init__(self, parent, app_file: str = Args().app, *args, **kwargs):
        self._app_file = app_file
    
    def check_app(self) -> bool:
        return os.path.exists(self._app_file) and os.path.isfile(self._app_file)
    
    _already_running: str = "Opentrons APP running", "Another instance of the Opentrons APP has already been launched"
    
    @property
    def _check_fail(self) -> Tuple[str, str]:
        return "Opentrons APP not found", "Opentrons APP not found at {}\nPlease set the correct path in the environment variable:\n\nOPENTRONS_APP".format(self._app_file)
    
    @property
    def _subprocess_args(self) -> List[str]:
        return [self._app_file]


class ServerButton(OnOffSubprocessButton, metaclass=AppButtonFrame.button):
    text: str = "Local Web Server"
    
    def init_(self):
        self.state = True
        self.update()
    
    def __init__(self, parent, *args, **kwargs):
        Timer(interval=1, function=self.init_).start()  # Delayed launch to allow successful stdout redirection
    
    @OnOffSubprocessButton.state.getter
    def state(self) -> bool:
        return False if self._subprocess is None else self._subprocess.is_alive()
    
    def execute(self):
        if self.state:
            tk.messagebox.showwarning(*self._already_running)
        else:
            self._subprocess = Process(target=lws_main)
            self._subprocess.start()
    
    _already_running: str = "LocalWebServer running", "Another instance of the LocalWebServer has already been launched"
        

class WebAppButton(metaclass=AppButtonFrame.button):
    text: str = "Web App"
    
    def command(self, app_url: str = Args().web_app):
        webbrowser.open(app_url)


# Copyright (c) 2020 Covmatic.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
