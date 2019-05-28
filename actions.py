# Home of action_command shit, including verb lists, and parse and execute functions


system_commands = ['main menu', 'pause', 'quit']
player_only_verbs = ['i', 'inv', 'inventory', 'friends']
world_verbs = ['look', 'go', 'n', 'north', 'e', 'east', 'w', 'west', 's', 'south']
subject_verbs = ['eat', ' drink']  # Subject acts on self
social_verbs = ['talk', 'shop', 'buy', 'sell', 'give']  # Involves other people
item_verbs = ['get', 'take', 'drop']
verb_list = world_verbs + subject_verbs + social_verbs + item_verbs + player_only_verbs

ALL_VALID_TARGETS = ''


class ActionCommand:
	def __init__(self):
		self.subject = None
		self.verb = None
		self.target = None
		self.direct_object = None
		self.quantity = 0
		self.system_command = None

	def execute(self):
		pass


def reassign_if_move_direction(action_command):
	if action_command.verb in ['n', 'north', 'e', 'east', 's', 'south', 'w', 'west']:
		action_command.target = action_command.verb
		action_command.verb = 'go'


def parse_player_action_command(player, command_message):


	player_command = ActionCommand()

	player_command.subject = player

