"""
TODO: Attempting to connect ... 3.. 2.. 1.. (for loop in range(TIMEOUT))
TODO: Allow connect only at appropriate times

TODO: Store recent user commands to recall

TODO: the color tag checker is reviewing all text each time text is displayed. It is changing previous tags (I think the order is based tag declaration order) and redoing all previous work each time. Have it just look at text being posted, possibly before insertion?
TODO: Find better alternative to command_readback system
TODO: Special text reading system, to break large strings into multiple display_text_outputs.

TODO: Verbs come from actions.py

TODO: Get listen to broadcasts to end smoothly

ISSUES

LISTENING FOR BROADCASTS
Will listen for broadcasts work? can that thread fly? Will a "server tick" 1 second timout on the
recv keep cpu usage acceptable?

"""

import tkinter as tk
import actions
import socket
import datetime
import threading

HEADER_LENGTH = 10
VERB_HEADER_LENGTH = 10

PORT = 1234
TIMEOUT = 3

INPUT = ''
LOGGING_IN = True

BOUND_KEYS = ['<Return>']


class ClientUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(TIMEOUT)

        self.title('Hearthfire')
        self.geometry('1500x800')
        self.config(background='black')

        self.game_screen = GameScreen(self)
        self.game_screen.grid(row=0, column=0)

        self.game_screen.player_input.focus_force()
        self.connect_prompt()

    def connect_prompt(self):
        self.display_text_output('Hearthfire')
        self.display_text_output('By Biff Willaburs')
        self.display_text_output('To join a game, enter a server address to connect to: ')

        self.bind_connect()

    def login_prompt(self):
        self.bind_login()
        self.display_text_output('Your essence is drawn through space and time to a particular point.')
        self.display_text_output('You se nse your destination is nearing...')
        self.display_text_output('As you are pulled into the fire, you must decide: Who are you?')

        self.bind_login()

    def connect(self, event):
        server_ip = self.get_player_input()

        if not self.validate_server_ip(server_ip):
            return False

        try:
            print('trying to connect to: ', self.server_ip)
            self.socket.connect((self.server_ip, PORT))
        except socket.timeout as e:
            self.display_text_output(
                f'Attempt to connect to {self.server_ip} timed out. Please check server status and try again.')
            self.refresh_socket()
            print(e)
        except socket.gaierror:
            self.display_text_output(f'{self.server_ip} is not a valid server address.')
        else:
            print(f'Connected to host at {server_ip}.')
            self.login_prompt()

    def validate_server_ip(self, server_ip):
        valid_chars = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.']
        for char in server_ip:
            if char not in valid_chars:
                self.display_text_output(f'{char} is not a valid character. Please specify a valid server address to connect to.', command_readback=True)
                return False

        self.server_ip = server_ip
        return True

    def login(self, event):
        login_name = self.get_player_input()

        if not login_name:
            self.display_text_output('You must give a name to incarnate.')
            return False

        if not login_name.isalpha():
            self.display_text_output('One\'s name must be speakable. Offer another...')
            return False

        self.send_message(login_name)

        response_header = self.socket.recv(HEADER_LENGTH).decode('utf-8')
        if not len(response_header):
            return False
        response_length = int(response_header)
        login_response = self.socket.recv(response_length).decode('utf-8')

        self.display_text_output(login_response)
        self.bind_game_keys()
        
        self.listen_thread = threading.Thread(target=self.listen_for_broadcasts, name='listen thread')
        self.listen_thread.start()

    def receive_broadcast(self):
        message_header = self.socket.recv(HEADER_LENGTH)
        message_length = int(message_header.decode('utf-8'))
        message = self.socket.recv(message_length).decode('utf-8')
        return message

    def refresh_socket(self):
        self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(TIMEOUT)

    def listen_for_broadcasts(self):
        self.socket.setblocking(True)

        while True:
            try:
                broadcast_header = self.socket.recv(HEADER_LENGTH)
                if not broadcast_header:
                    return
                broadcast_length = int(broadcast_header.decode('utf-8'))
                broadcast = self.socket.recv(broadcast_length).decode('utf-8')

                self.display_text_output(broadcast)
            except RuntimeError as e:
                print(f'RuntimeError: {e}. Goodbye!')
                return

    def process_action(self, event):
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

        if words[0] in actions.verb_list:
            self.send_message(f'{words[0]:<{VERB_HEADER_LENGTH}}'+' '.join(words[1:]), code='01')

        else:
            self.display_text_output(f'You want to {words[0]}? I don\'t even know what that is...')
            return False

    def send_message(self, message, code='00'):

        message_header = f'{len(message):<{HEADER_LENGTH}}'

        print(f'Sending: {message}')
        self.socket.send(message_header.encode('utf-8') + code.encode('utf-8') + message.encode('utf-8'))

    # ---- Key Bindings

    def bind_connect(self):
        self.unbind_game_keys()

        BOUND_KEYS.append('<Return>')
        self.bind('<Return>', self.connect)

    def bind_login(self):
        self.unbind_game_keys()

        BOUND_KEYS.append('<Return>')
        self.bind('<Return>', self.login)

    def bind_game_keys(self):
        self.unbind_game_keys()

        BOUND_KEYS.append('<Return>')
        self.bind('<Return>', self.process_action)
        print('Game Keys Active')

    def bind_client_level_keys(self):
        self.bind('<Escape>', self.escape_main_menu)

    def unbind_game_keys(self):
        for bound_key in BOUND_KEYS:
            self.unbind(bound_key)

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
        if self.socket:
            self.socket.shutdown(socket.SHUT_WR)
        self.destroy()
        quit()

    # ---- Text Display

    def get_player_input(self):

        player_input_text = self.game_screen.player_input.get(1.0, 'end-2l lineend')
        self.game_screen.player_input.delete(1.0, 'end')

        return player_input_text

    def enter_to_continue(self):
        # Make a function which takes function as argument. '<Return>' gets bound with a function that prints the next
        # line when user hits key. This way user can "scroll" through story dialog, not have it all pop up at once.
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
