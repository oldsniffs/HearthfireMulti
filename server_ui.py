import tkinter as tk
from tkinter import font as tkfont
import shelve
import os

class Server(tk.Tk):
    def __init__(self, world):
        self.world = world

        self.base_path = os.path.dirname(os.path.realpath(__file__))
        self.save_path = os.path.join(self.base_path, 'saves')
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def save_world(self, event):
        save_name = self.save_name_entry.get()

        d = shelve.open('/'+save_name)
        d['world'] = self.world

    def create_widgets(self):
        self.save_entry_var = tk.StringVar()
        self.save_entry_var.trace('w', self.toggle_save_button)
        self.save_entry = tk.Entry(self, textvariable=self.save_entry_var)
        self.save_button = tk.Button(self, text='Save World', command=self.save_world)

        self.save_button.pack()
        self.save_entry.pack()

    def toggle_save_button(self, *args):
        x = self.save_entry_var.get()
        if len(x) > 0:
            self.save_button.config(state='normal')
        if len(x) == 0:
            self.save_button.config(stat='disabled')