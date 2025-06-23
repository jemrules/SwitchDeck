from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from enum import Enum
import asyncio
from threading import Thread

class Indicator(QLabel):
    def __init__(self, text:str="", parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: red; border-radius: 10px;")
        self.setText(text)
        self.attributes={"color":"red","size":20}

    def set_color(self, color):
        self.attributes["color"]=color
        self.setStyleSheet(f"background-color: {self.attributes['color']}; border-radius: 10px; font-size: {self.attributes['size']}px;")
    def set_size(self, size):
        self.attributes["size"]=size
        self.setStyleSheet(f"background-color: {self.attributes['color']}; border-radius: 10px; font-size: {self.attributes["size"]}px;")
class Event(QTimer):
    def __init__(self, parent=None):
        super().__init__(parent)
    def connect(self, func):
        self.timeout.connect(func)
        self.setSingleShot(True)
    def trigger(self):
        self.start(1)
def RunAsync(func,*args, **kwargs):
    loop = asyncio.get_event_loop()
    try:
        return loop.run_until_complete(func(*args, **kwargs))
    except RuntimeError as e:
        raise e
    finally:
        loop.close()
def RunThreadedAsync(func, timeout: float | None, *args, **kwargs):
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()
    thread = Thread(target=run_in_thread)
    thread.start()
    thread.join(timeout)