import select
import socket
import threading
import locations
import queue
import time

"""
TODO: Save and load world objects

Hosts and manages the World.
Tracks changes to player objects and their locations associated with connected clients and notifies affected clients as
necessary.
Listens for commands from clients, returns a message regarding the command if needed.

"""

""" Notes for Development
Thread Objects from threading have a join function - which allows multiple threads to wait for another Thread to terminate.
Even Objects can also coordinate activity between threads.

Question of checking client sockets with server socket: Splitting them with the idea
that not checking the server socket for (rare) new connections will keep client scanning
more brisk. However, if all was done in same loop, no threading overhead would be generated.

Question of using a Client class: Operations will be more granular with a class. 
"""

HEADER_LENGTH = 10
HEADER_AND_CODE = HEADER_LENGTH + 2

server_address = '10.0.0.43'
port = 1234

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sockets = [server]
actionable_sockets = []
players = {} # can match socket to player
command_queues = {}
online_player_locations = []

server.bind((server_address, port))
server.listen(5)

world_events = []

world = locations.World()


def receive_command(client_socket):

	try:
		header = client_socket.recv(HEADER_LENGTH).decode('utf-8')

		if not len(header):
			return False

		command_length = int(header)
		command = client_socket.recv(command_length).decode('utf-8')

		return command

	except ConnectionResetError as e:
		print(f'**Error while receiveing command from {client_socket.getsockname()}:', e)
		return False


def login(client):
	pass


def broadcast(client, message):
	out_message = message.encode('utf-8')
	broadcast_header = f'{len(message):<{HEADER_LENGTH}}'.encode('utf-8')
	client.send(broadcast_header + out_message)


def run_server():
	while True:
		readables, actionables, exceptionals = select.select(sockets, actionable_sockets, sockets)

		for sock in readables:
			if sock == server:
				new_client, client_address = server.accept()
				print(f'Connection from {client_address[0]}:{client_address[1]} established')
				sockets.append(new_client)
				command_queues[new_client] = queue.Queue()

				if new_client not in players:
					pass

			else:
				client_message = receive_command(sock)

				if client_message:
					command_queues[sock].put(client_message)
					if sock not in actionable_sockets:
						actionable_sockets.append(sock)

				else:
					print(f'Connection from {sock.getsockname()} lost.')
					if sock in actionable_sockets:
						actionable_sockets.remove(sock)
					sock.close()
					sockets.remove(sock)
					del command_queues[sock]

		for sock in actionables:
			if sock not in players:
				try:
					login_player = command_queues[sock].get_nowait()
					if login_player in [player.name for player in world.players]:
						for player in world.players:
							if login_player == player.name:
								players[sock] = player
								broadcast(sock, f'Logged in as {players[sock].name}.')
					else:
						print(f'{login_player} needs to login')

				except queue.Empty:
					actionables.remove(sock)

			else:
				try:
					next_command = command_queues[sock].get_nowait()

				except queue.Empty:
					actionables.remove(sock)
				except KeyError as e:
					print(e)
				else:
					pass
					# process command

		for sock in exceptionals:
			print(f'Lost connection from {sock.getsockname()}.')
			if sock in actionable_sockets:
				actionable_sockets.remove(sock)
			sock.close()
			sockets.remove(sock)
			del command_queues[sock]


run_server()
