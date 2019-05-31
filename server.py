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


def receive_command(client_socket):

	try:
		header = client_socket.recv(HEADER_LENGTH).decode('utf-8')

		if not len(header):
			return False

		command_length = int(header)
		command = client_socket.recv(command_length).decode('utf-8')
		command = command.lower()

		return command

	except ConnectionResetError as e:
		print(f'**Error while receiveing command from {client_socket.getsockname()}:', e)
		return False


def login(client):
	pass

def broadcast(client):
	pass


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
					# Instead of adding a message by socket, add it by player.
					print(f'Connection from {sock.getsockname()} lost.')
					if sock in actionable_sockets:
						actionable_sockets.remove(sock)
					sock.close()
					sockets.remove(sock)
					del command_queues[sock]

		for sock in actionables:
			try:
				next_command = command_queues[sock].get_nowait()
				print(next_command)
				print(command_queues[sock])
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
