import select
import socket
import threading
import queue
import time

import locations
import actions
import server_ui

"""
TODO: Save and load world objects
TODO: Lost socket function to close out connection, remove temp assets

"""

""" Development Notes

server.py hosts and manages the World.
Tracks changes to player objects and their locations associated with connected clients and notifies affected clients as
necessary.
Listens for commands from clients, returns a message regarding the command if needed.

Thread Objects from threading have a join function - which allows multiple threads to wait for another Thread to terminate.
Even Objects can also coordinate activity between threads.

Question of checking client sockets with server socket: Splitting them with the idea
that not checking the server socket for (rare) new connections will keep client scanning
more brisk. However, if all was done in same loop, no threading overhead would be generated.

Question of using a Client class: Operations will be more granular with a class. 
"""

HEADER_LENGTH = 10
VERB_HEADER_LENGTH = 10
CODE_LENGTH = 2
HEADER_AND_CODE = HEADER_LENGTH + 2

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = '10.0.0.43'
port = 1234
server.bind((server_address, port))
server.listen(5)

sockets = [server]
actionable_sockets = []
players = {}  # {client: player}
message_queues = {}
command_queues = {}
online_player_locations = []

world_events = []
world = locations.World()


def receive_message(client_socket):

	try:
		header = client_socket.recv(HEADER_LENGTH).decode('utf-8')
		code = client_socket.recv(CODE_LENGTH).decode('utf-8')

		if not len(header):
			raise Exception

		message_length = int(header)
		message = client_socket.recv(message_length).decode('utf-8')

		return code, message

	except ConnectionResetError as e:
		print(f'ConnectionResetError from {client_socket.getsockname()}:', e)
		return None, None

def login(client):
	pass


def broadcast(client, message):
	broadcast_header = f'{len(message):<{HEADER_LENGTH}}'
	print(f'Broadcasting to {client.getsockname()}: {broadcast_header} {message}')
	client.send(broadcast_header.encode('utf-8') + message.encode('utf-8'))


def run_server():
	print('Server online: Accepting connections...')
	while True:
		readables, actionables, exceptionals = select.select(sockets, actionable_sockets, sockets)

		for sock in readables:
			if sock == server:

				new_client, client_address = server.accept()
				print(f'Connection from {client_address[0]}:{client_address[1]} established')
				sockets.append(new_client)
				message_queues[new_client] = queue.Queue()
				command_queues[new_client] = queue.Queue()

				if new_client not in players:
					pass

			elif sock in sockets:
				try:
					code, data = receive_message(sock)
				except:
					print(f'(From Readables) Lost connection from {sock.getsockname()}.')
					if sock in actionable_sockets:
						actionable_sockets.remove(sock)
					del players[sock]
					sockets.remove(sock)
					del message_queues[sock]
					del command_queues[sock]
					sock.close()
					continue

				if sock not in players:
					login_name = data
					if login_name in [player.name for player in world.players]:
						for player in world.players:
							if login_name == player.name:
								players[sock] = player
								print(f'{sock.getsockname} logged in as {players[sock].name}')
								broadcast(sock, f'Logged in as {players[sock].name}.')
					else:
						players[sock] = locations.people.Player(world, login_name)
						print(f'New player {login_name} created by {sock.getsockname()}')
						world.players.append(players[sock])
						broadcast(sock, f'Welcome to the world, {players[sock].name}')

				else:
					if code == '01':
						verb = data[:10].strip()
						action = data[10:]
						print(f'Received (verb: action) {verb}: {action}')
						player_action = actions.parse_player_action(player, verb, action)
						actions.execute_player_action(player_action)

					elif code == '00':
						pass

		for sock in exceptionals:
			print(f'(From exceptionals list) Lost connection from {sock.getsockname()}.')
			if sock in actionable_sockets:
				actionable_sockets.remove(sock)
			sock.close()
			sockets.remove(sock)
			del message_queues[sock]
			del command_queues[sock]

def timed_broadcast():
	while True:
		time.sleep(3)

		for client in players.keys():
			broadcast(client, 'yo')


thread_server = threading.Thread(target=run_server)
thread_server.start()
# thread_timed = threading.Thread(target=timed_broadcast)
# thread_timed.start()

