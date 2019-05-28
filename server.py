import select
import socket
import threading
import locations
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
"""

HEADER_LENGTH = 10

server_address = '10.0.0.72'
port = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# sockets list possibly could hold Client objects, if select.select will still detect changes to the socket contained in the Client
# But I think this could get messy.
sockets_list = [server_socket]
clients = []
players = {} # can match client to player
online_player_locations = []

server_socket.bind((server_address, port))
server_socket.listen(5)

world = threading.Thread(target=locations.World, name='world thread')
world.start()


class Client:
	def __init__(self, socket, address):
		self.socket = socket
		sockets_list.append(self.socket)
		self.address = address

		self.player_name = ''
		self.player_login()

	def player_login(self):
		self.socket.recv(HEADER_LENGTH)

	def receive_transmission(self):
		transmission_header = self.socket.recv(HEADER_LENGTH)

		if not len(transmission_header):
			return False

		transmission_length = int(transmission_header.decode('utf-8'))
		return {'header': transmission_header, 'message': self.socket.recv(transmission_length)} # Could try decoding here

def listen_for_commands():
	read_clients, _, _e = select.select(clients, [], [])
	for client in read_clients:
		print(client)

def receive_command(client_socket):

	command_header = client_socket.recv(HEADER_LENGTH)

	if not len(command_header):
		return False

	message_length = int(command_header.decode('utf-8'))



print('accepting new connections')


def accept_connections():
	read_sockets, writable_sockets, exception_sockets = select.select(sockets_list, [], sockets_list)

	for s in read_sockets:
		if s == server_socket:
			print('incoming connection attempt')
			client_socket, client_address = server_socket.accept()
			print(f'connection from {client_address[0]}:{client_address[1]} accepted.')
			c = threading.Thread(target=Client, args=(client_socket, client_address))
			c.start()

		else:
			header = s.recv(HEADER_LENGTH)
			message_size = int(header.decode('utf-8'))



	for s in writable_sockets:
		pass


	for s in exception_sockets:
		# close out the socket
		s.close()