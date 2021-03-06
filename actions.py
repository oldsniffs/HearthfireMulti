# Home of action_command shit, including verb lists, and parse and execute functions


system_commands = ['main menu', 'pause', 'quit']
player_only_verbs = ['i', 'inv', 'inventory', 'friends']
world_verbs = ['look', 'go', 'n', 'north', 'e', 'east', 'w', 'west', 's', 'south']
subject_verbs = ['eat', ' drink']  # Subject acts on self
social_verbs = ['talk', 'shop', 'buy', 'sell', 'give']  # Involves other people
item_verbs = ['get', 'take', 'drop']
verb_list = world_verbs + subject_verbs + social_verbs + item_verbs + player_only_verbs

ALL_VALID_TARGETS = ''


class Action:
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


def parse_player_action(player, verb, action):

	player_action = Action()

	player_action.subject = player
	player_action.verb = verb

	# strip() in case value is blank space. may not be necessary
	words = action.split()

	# I would check action instead of words, but unsure about blank space.
	if not words:
		return player_action

	if len(words) == 1:
		print(f'assigning {words[0]} as target')
		player_action.target = words[0]

	return player_action


def execute_player_action(player_action):

	# TODO: A covert system. Subject attempts to do something hidden, a check is performed for others to view it

	observation = None

	if player_action.verb == 'look':
		response = player_action.subject.location.describe()

	if player_action.verb == 'go':
		print('Executing "go"')
		if not player_action.target:
			print('returning where do you want to go')
			return 'Where do you want to go?'

		elif player_action.target in ['n', 'e', 'w', 's', 'north', 'east', 'west', 'south']:
			if player_action.target == 'n':
				player_action.target = 'north'
			elif player_action.target == 'e':
				player_action.target = 'east'
			elif player_action.target == 'w':
				player_action.target = 'west'
			elif player_action.target == 's':
				player_action.target = 'south'

			if player_action.target in player_action.subject.location.get_exits():
				player_action.subject.move(direction=player_action.target)
				return player_action.subject.location.describe()
			else:
				return 'You can\'t go that way!'

		elif player_action.target:
			for es in player_action.subject.location.special_exits:
				if player_action.target == es.name:
					player_action.subject.move(exit=es)

		else:
			response = 'I don\'t understand where you\'re trying to go.'

	return response, observation
