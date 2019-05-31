"""
TODO: Attempting to connect ... 3.. 2.. 1..

TODO: Store recent user inputs to recall
TODO: Implement universal unbinding for all keys

TODO: If any parse can be done client side (at least verb), client could just send command object, easing burden on server
TODO: Probably merge send_non_command with send_command, and let the process methods handle different protocols

TODO: the color tag checker is reviewing all text each time text is displayed. It is changing previous tags (I think the order is based tag declaration order) and redoing all previous work each time. Have it just look at text being posted, possibly before insertion?
TODO: Determine if send command and send non_command can be consolidated

TODO: Special text reading system, to break down strings of text from a file into multiple
display_text_outputs. Will obsolete login function

TODO: (Possible) Implement purpose headers, so server knows what to do with incoming data
TODO: (Possible) send_command more speicalized

ISSUES

LISTENING FOR BROADCASTS
Will listen for broadcasts work? can that thread fly? Will a "server tick" 1 second timout on the
recv keep cpu usage acceptable?

"""

import tkinter as tk
from actions import *
import sys
import socket
import datetime
import threading

HEADER_LENGTH = 10

PORT = 1234
TIMEOUT = 1

INPUT = ''
LOGGING_IN = True


class ClientUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(TIMEOUT)

        self.player_name = ''

        self.title('Hearthfire')
        self.geometry('1500x800')
        self.config(background='black')

        self.game_screen = GameScreen(self)
        self.game_screen.grid(row=0, column=0)

        self.verb_list = world_verbs + subject_verbs + social_verbs + item_verbs + player_only_verbs

        self.game_screen.player_input.focus_force()
        self.bind_game_keys()

    def login(self):
        self.bind_login()
        self.display_text_output('Your essence is drawn through spacetime to a particular point.')
        self.display_text_output('You sense your destination is nearing...')
        self.display_text_output('As you are pulled into the hearthfire, you must decide: Who are you?')

    def get_login(self, event):
        login_name = self.get_player_input()

        self.send_command(login_name)


        response_header = self.socket.recv(HEADER_LENGTH).decode('utf-8')

        if not len(response_header):
            return False

        response_length = int(response_header)
        response = self.socket.recv(response_length).decode('utf-8').lower()

        print(response)


    def refresh_socket(self):
        self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(TIMEOUT)

    def connect(self):
        try:
            print('trying to connect to: ', self.server_ip)
            self.socket.connect((self.server_ip, PORT))
        except socket.timeout as e:
            self.display_text_output(f'Attempt to connect to {self.server_ip} timed out. Please check server status and try again.')
            self.refresh_socket()
            print(e)
        except socket.gaierror:
            self.display_text_output(f'{self.server_ip} is not a valid server address.')
        else:
            self.socket.settimeout(TIMEOUT)
            self.login()

    def listen_for_broadcasts(self):
        while True:
            # Check tag for 'special' broadcasts, run through a filter
            broadcast_header = self.socket.recv(HEADER_LENGTH)

            if not len(broadcast_header):
                print('Connection closed by server')
                sys.exit()

            broadcast_length = int(broadcast_header.decode('utf-8'))
            broadcast = self.socket.recv(broadcast_length).decode('utf-8')

            print(datetime.now(), broadcast)

            self.display_text_output(broadcast)

    def process_command(self, event):
        # TODO: see if event argument is needed
        player_input = self.get_player_input()
        self.display_text_output(player_input, command_readback=True)

        if player_input == 'quit':
            self.quit()
            return None
        elif player_input == 'menu':
            pass

        words = player_input.lower().split()

        if len(words) == 0:
            self.display_text_output('Please enter something.')
            return None

        if words[0] == 'connect':
            valid_chars = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.']
            for char in words[1]:
                if char not in valid_chars:
                    self.display_text_output('Please specify a valid server address to connect to.', command_readback=True) # use a different kwarg
                    return None
            else:
                self.server_ip = words[1]
                print('attempting')
                self.display_text_output(f'Attempting to connect to {self.server_ip}', command_readback=True)
                print(self.server_ip)
                self.connect()
                return None

        player_input = ' '.join(words)

        self.send_command(player_input)

    def send_command(self, command):
        out_command = command.encode('utf-8')
        command_header = f'{len(out_command):<{HEADER_LENGTH}}'.encode('utf-8')
        self.socket.send(command_header + out_command)
        print(out_command)

    def get_player_input(self):

        player_input_text = self.game_screen.player_input.get(1.0, 'end-2l lineend')
        self.game_screen.player_input.delete(1.0, 'end')

        return player_input_text


    # ---- Key Bindings

    def bind_login(self):
        self.bind('<Return>', self.get_login)

    def bind_game_keys(self):
        self.bind('<Return>', self.process_command)

    def bind_client_keys(self):
        # Bind client level keys that are used in all game modes. Client keys like escape
        self.bind('<Escape>', self.escape_main_menu)

    def unbind_keys(self):
        # Does not unbind client level keys
        self.unbind('<Return>')

    def escape_main_menu(self, event):
        self.main_menu()

    # ---- Menu

    def main_menu(self):
        # Opens small popup menu, a la aoe2
        pass

    # ---- System

    def start(self):
        self.main_menu()
        self.mainloop()

    def quit(self):
        self.destroy()
        sys.exit()

    # ---- Text Display
    def display_location(self, location):
        pass

    def display_text_output(self, text, pattern1=None, tag1=None, pattern2=None, tag2=None, command_readback=False,
                            tagging='default'):

        if command_readback == True:
            text = text + '\n'

        else:
            text = text + '\n> '

        self.game_screen.output_display.display_text(text)

        if tagging == 'future default':

            self.game_screen.output_display.apply_tag_to_pattern(self.player.location.name, 'dark-turquoise')
            self.game_screen.output_display.apply_tag_to_pattern(self.player.location.zone.name, 'dark-turquoise')

            for e in self.player.location.capitalize_exits():
                self.game_screen.output_display.apply_tag_to_pattern(e, 'dark-turquoise')
            for i_n in self.player.location.items:
                self.game_screen.output_display.apply_tag_to_pattern(i_n.name, 'salmon')

    # ---- Text Input
    #
    # def combine_2_word_terms(self, a_list):
    #     count = 0
    #     while count < len(a_list) - 1:
    #         print(' '.join((a_list[count], a_list[count + 1])))
    #         if ' '.join((a_list[count], a_list[
    #             count + 1])) in locations.people.items.all_terminal_item_names + locations.people.all_people_names + self.verblist:
    #             a_list[count] = ' '.join((a_list[count], a_list[count + 1]))
    #             del a_list[count + 1]
    #         count += 1


class GameScreen(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.create_widgets()

    def create_widgets(self):

        # Container Frames
        self.text_frame = tk.Frame(self, height=760, width=850, bg='black')
        self.visual_frame = tk.Frame(self, height=760, width=575, bg='thistle3')

        self.text_frame.grid(row=1, column=1, sticky='nsew')
        self.visual_frame.grid(row=1, column=3)

        # Text Panels

        self.output_display = OutputText(self.text_frame, width=105, bg='black', foreground='#CCCCFF', wrap='word',
                                      relief='sunken', state='disabled')
        self.player_input = tk.Text(self.text_frame, height=2, width=105, bg='black', foreground='white',
                                    relief="sunken")
        self.output_display.pack(expand=True, fill='y')
        self.player_input.pack()


class OutputText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        self.configure(state='disabled')
        # TODO: see if this can be overloaded

        # self.output_font = tkfont.Font('system', 8)
        # self.configure(font=self.output_font)

        # ---- Tags ----

        self.tag_configure('red', foreground='#ff0000')
        self.tag_configure('orange-red', foreground='#FF4500')
        self.tag_configure('dark-turquoise', foreground='#2C7B80')
        self.tag_configure('light-turquoise', foreground='#3FB1B7')
        self.tag_configure('salmon', foreground='#D76565')
        self.tag_configure('light-salmon', foreground='#6B3232')
        self.tag_configure('teal', foreground='#01B8AA')
        self.tag_configure('mudfish', foreground='#2E3A22')
        self.tag_configure('light-mudfish', foreground='#12170D')
        self.tag_configure('light-lavender', foreground='#9797FF')
        self.tag_configure('vanilla', foreground='#fff68f')
        self.tag_configure('overcast', foreground='#939FAB')
        self.tag_configure('cocoa', foreground='#3E2323')
        self.tag_configure('blood', foreground='#6D0F0F')
        self.tag_configure('lavender-blue', foreground='#CCCCFF')
        self.tag_configure('light-brown', foreground='#AB9481')
        self.tag_configure('muted-purple', foreground='#6F404B')

    def display_text(self, text):
        # Tagging, custom formatting should be worked out at higher level

        self.configure(state='normal')
        self.insert('end', text)
        self.configure(state='disabled')
        self.see('end')

    def apply_tag_to_pattern(self, pattern, tag, start='1.0', end='end', regexp=False):

        start = self.index(start)
        end = self.index(end)

        self.mark_set('matchStart', start)
        self.mark_set('matchEnd', start)
        self.mark_set('searchLimit', end)

        count = tk.IntVar()  # initiates at 0
        while True:
            index = self.search(pattern, 'matchEnd', 'searchLimit', count=count, regexp=regexp)
            if index == '':
                break
            if count.get() == 0:
                break
            self.mark_set('matchStart', index)
            self.mark_set('matchEnd', '%s+%sc' % (index, count.get()))
            self.tag_add(tag, 'matchStart', 'matchEnd')
