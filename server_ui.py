import tkinter as tk
import shelve

class Server(tk.Tk):
    def __init__(self, world):
        self.world = world

    def save_world(self, event):
        save_name = self.save_name_entry.get()

        d = shelve.open('/'+save_name)
        d['world'] = self.world

    def create_widgets(self):
        self.save_button = tk.Button(text='Save World', command=self.save_world)
        self.save_entry