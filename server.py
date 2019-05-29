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

# sockets list possibly could hold Client objects, if select.select will still detect changes to the socket contained in the Client
# But I think this could get messy.
sockets = [server]
actionable_sockets = []
players = {} # can match client to player
command_queues = {}
online_player_locations = []

server.bind((server_address, port))
server.listen(5)

world_events = []


def receive_command(client_socket):

	command_header = client_socket.recv(HEADER_LENGTH)

	if not len(command_header):
		return False

	message_length = int(command_header.decode('utf-8'))
	return client_socket.recv(message_length).decode('utf-8')


def run_server():
	while True:
		readables, actionables, exceptionals = select.select(sockets, actionable_sockets, sockets)

		for sock in readables:
			if sock == server:
				new_client, client_address = server.accept()
				print(f'connection from {client_address[0]}:{client_address[1]} accepted.')
				sockets.append(new_client)
				command_queues[new_client] = queue.Queue()

			else:
				client_message = receive_command(sock)

				if client_message:
					command_queues[sock].put(client_message)
					if sock not in actionable_sockets:
						actionable_sockets.append(sock)

				else:
					print(f'Lost connection from {sock.getsockname()}.')
					if sock in actionable_sockets:
						actionable_sockets.remove(sock)
					sock.close()
					sockets.remove(sock)
					del command_queues[sock]

		for sock in actionables:
			try:
				next_command = command_queues[sock].get_nowait()
				print(next_command)
				print(command_queues)
			except queue.Empty:
				actionables.remove(sock)
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