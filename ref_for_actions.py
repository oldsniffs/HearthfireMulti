# This file covers UI classes and user input handling
# It is intended as the main file to be run

import tkinter as tk
from tkinter import font as tkfont
import sys
import random

import menu

class Game(tk.Tk):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.title('Hearthfire')
		self.geometry('1500x800')
		self.config(background='black')

		self.world = None
		self.player = None
		self.current_game = 'Unsaved Game'
		self.game_screen = GameScreen(self)
		self.game_screen.grid(row=0, column=0)


		self.verblist = self.world_verbs + self.subject_verbs + self.social_verbs + self.item_verbs + self.player_only_verbs

		# This is a dynamic variable that may need to be updated
		self.all_valid_targets = menu.locations.people.all_people + menu.locations.people.items.all_terminal_items


	# ---------- Text handling methods ------------
	def random_color(self):
		colors = ['red','orange-red','dark-turquoise','light-turquoise','cocoa''vanilla','overcast','light-mudfish','muted-purple','light-brown','light-salmon','red','mudfish']
		return colors[random.randint(0, len(colors)-1)]

	def display_text_output(self, text, pattern1=None, tag1=None, pattern2=None, tag2=None, command_readback = False, tagging='default'):
		# TODO: the color tag checker is reviewing all text each time text is displayed. It is changing previous tags (I think the order is based tag declaration order) and redoing all previous work each time.

		if command_readback == True:
			text = text + '\n'

		else:
			text = text + '\n> '

		self.game_screen.text_output.configure(state='normal')
		self.game_screen.text_output.insert('end', text)
		
		if tagging == 'default':
			# TODO: I'd like a good way to not apply colors to 'story' type text, such as the meat of a look description, or a conversation. I feel the colors disrupt the reading flow.
			# Possibly execute look, talk, could grab sections of the description.
			# Possibly a regex match here could direct tag application. That seems vulnerable to later conflicts.

			self.game_screen.text_output.apply_tag_to_pattern(self.player.location.name, 'dark-turquoise')
			self.game_screen.text_output.apply_tag_to_pattern(self.player.location.zone.name, 'dark-turquoise')

			for exit in self.player.location.capitalize_exits():
				self.game_screen.text_output.apply_tag_to_pattern(exit, 'dark-turquoise')
			for i_n in self.player.location.items:
				self.game_screen.text_output.apply_tag_to_pattern(i_n.name, 'salmon')

		self.game_screen.text_output.configure(state='disabled')
		self.game_screen.text_output.see('end')

# ---- Keybound functions ----
	def execute_player_command(self, event):
		# Does 1 thing: when <return> is pressed, sends player input to parse_player_action_command. If valid command is returned, sends it to execute_command
		player_action_command = self.parse_player_action_command()
		if player_action_command != None:
			self.execute_command(player_action_command)

	def escape_main_menu(self, event):
		self.main_menu()	

# ---- Command Processing ----

	def execute_command(self, action_command):

		# If subject is an npc and player is present, a display message may be needed to describe events to player.
		player_present = False
		if action_command.subject != self.player and action_command.subject.location == self.player.location:
			player_present = True

		# if action_command:
		# 	print('verb: ' + action_command.verb)
		# 	print('target: ' + action_command.target)
		# 	print('DO: ' + action_command.direct_object)
		# 	print('quantity: ' + str(action_command.quantity))
		# 	print(action_command.system_command)
		# else:
		# 	print('no action_command object generated')

		# ---- Handle system commands ----


		# ---- Handle Verbs ----

		if action_command.verb == 'look':
			# TODO: Include visible nearby locations in present list, and let player look at locations they can currently see.
			if not action_command.target:
				self.display_text_output(self.player.location.describe())
			else:
				self.display_text_output(action_command.target.describe())


		elif action_command.verb == 'go':

			if not action_command.target:
				self.display_text_output('Where do you want to go?')

			elif action_command.target in ['n','e','w','s','north','east','west','south']:
				if action_command.target == 'n':
					action_command.target = 'north'
				elif action_command.target == 'e':
					action_command.target = 'east'
				elif action_command.target == 'w':
					action_command.target = 'west'
				elif action_command.target == 's':
					action_command.target = 'south'

				if action_command.target in action_command.subject.location.get_exits():
					action_command.subject.move(direction=action_command.target)
				else:
					self.display_text_output('You can\'t go that way!')

			elif action_command.target:
				for es in action_command.subject.location.special_exits:
					if action_command.target == es.name:
						action_command.subject.move(exit=es)

			else:
				self.display_text_output('I\'m not sure where you want to go.')

			if action_command.subject == self.player:
				self.display_text_output(self.player.location.describe())

		# Player only verbs
		elif action_command.verb == 'i' or 'inv' or 'inventory':
			self.player.get_inventory()


		# Subject verbs
		elif action_command.verb == 'eat':
			pass

		elif action_command.verb == 'get' or 'take':
			if action_command.direct_object:
				action_command.subject.get_item(action_command.direct_object, target=action_command.target)
			else:
				action_command.subject.get_item(action_command.target)

	def parse_player_action_command(self):
		# Does 1 thing: builds a command object with strings from player input

		player_command = ActionCommand(self)
		player_command.subject = self.player

		player_input = self.get_player_input()
		self.display_text_output(player_input, command_readback=True)

		if player_input in self.system_commands:
			player_command.system_command = player_input
			return player_command

		words = player_input.split()

		if len(words) == 0:
			self.display_text_output('Please enter something.')
			return None
 
 		# ---- Clean user's input:

		words = [w for w in words if w not in ['the','The']]

		self.combine_2_word_terms(words)
		print(words)

		# ---- Begin parse ----

		if words[0] not in self.verblist:
			self.display_text_output('I don\'t even know what {}ing is!'.format(words[0]))
			return None

		player_command.verb = words[0]

		# Single verb commands
		if len(words) == 1:
			return player_command

		if len(words) == 2:
			player_command.target = words[1]
			print(player_command.target)

		# Quantity
		for w in words:
			if w.isdigit():
				# -- checks --
				# ensure number is not last word
				if words.index(w) == len(words)-1:
					self.display_text_output(player_command.verb + ' ' + w + ' of what?')
					return None
				# ensure only 1 number. Improve by checking full words[] for any 2 numbers
				if words[words.index(w)+1].isdigit():
					player_command.not_understood()
					return None
				player_command.quantity = w

		# Prepositions
		if 'for' in words:
			player_command.indirect_object = words[words.index('for')+1]

		if 'at' in words:
			player_command.target = words[words.index('at')+1]

		if 'to' in words:
			if player_command.verb == 'give': # Verb requires DO
				player_command.direct_object = words[words.index('to')-1]
			player_command.target = words[words.index('to')+1]

		# Handle getting item from a container, interactable's container, stealing
		if 'from' in words:
			if player_command.verb == 'get' or 'take': # Verbs that require DO
				player_command.direct_object = words[words.index('from')-1]
			player_command.target = words[words.index('from')+1]

		# Verb grouping defaults
		if player_command.verb in self.subject_verbs:
			player_command.target = self.player


		
		present_stuff = self.player.inventory + self.player.location.items + self.player.location.special_exits + self.player.location.denizens + self.player.location.harvestables + self.player.location.interactables
		print(player_command.target)
		for ps in present_stuff:
			if player_command.target == ps.name:
				player_command.target = ps
			else:
				self.display_text_output('I can not find "'+ player_command.target + '" here.')
				return None

		print('verb:',player_command.verb)
		print('target:',player_command.target)

		self.substantiate_command(player_command)
		self.reassign_if_move_direction(player_command)

		print(player_command.target)
		return player_command



	def reassign_if_move_direction(self, action_command):

		if action_command.verb in ['n','north','e','east','s','south','w','west']:
			action_command.target = action_command.verb
			action_command.verb = 'go'

	def substantiate_command(self, action_command):
		# 1 thing: Confirms .target (and DO if there is one) exists, and reassign corresponding object in place of the string value.
		# If targets don't exist, or exist but are not present, values will be strings "not present" or "not exist"
		# Some verbs can target something present in the location. Some, like info, can target many things not present.
		# Verb lists direct attribute assignments.
		# No display messages in this function, that is the purview of execute.
		present_valid_targets = self.player.location.items + self.player.location.denizens + self.player.location.harvestables + self.player.location.interactables


	def get_player_input(self):

		player_input_text = self.game_screen.player_input.get(1.0, 'end-2l lineend')
		self.game_screen.player_input.delete(1.0, 'end')

		return player_input_text


# ---- Utility methods ----

	def combine_2_word_terms(self, a_list): # Could be expanded to combine more than 2 terms.
		count = 0
		while count < len(a_list)-1:
			print (' '.join((a_list[count], a_list[count+1])))
			if ' '.join((a_list[count], a_list[count+1])) in menu.locations.people.items.all_terminal_item_names+menu.locations.people.all_people_names+self.verblist:
				a_list[count] = ' '.join((a_list[count], a_list[count+1]))
				del a_list[count+1]
			count += 1

# ---- Game system methods ----

	def bind_game_keys(self):
		self.bind('<Escape>', self.escape_main_menu)
		self.bind('<Return>', self.execute_player_command)

	def unbind_game_keys(self):
		self.unbind('<Escape>')
		self.unbind('<Return>')

	def new_game(self):
		pass

	def main_menu(self):
		self.unbind_game_keys()
		self.menu = menu.MainMenu(self)
		self.menu.grid(row=0, column=0, rowspan=3, columnspan=5, sticky='nsew')

	def start(self):
		self.main_menu()
		self.mainloop()

	def quit(self):
		self.destroy()


class ActionCommand:
	def __init__(self, controller): # Add subject assignment
		self.subject = None
		self.verb = None
		self.target = None
		self.direct_object = None
		self.quantity = 0
		self.system_command = None
		self.controller = controller

	def not_understood(self):
		self.controller.display_text_output('I don\'t understand what you\'re trying to do.')


Game().start()