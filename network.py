import socket


class Connection:
    def __init__(self, server_address):
        self.server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = server_address
        self.port = 5555
        self.address = (self.server_address, self.port)
        self.geton = self.connect()

    def connect(self):
        try:
            self.server_connection.connect(self.address)
            return self.server_connection.recv(2048).decode()
        except:
            pass

    def send_action_command(self, action_command):
        pass

    def send(self, text):
        self.server_connection.send(str.encode(text))
        return self.server_connection.recv(2048).decode()

    def listen(self):
        return self.server_connection.recv(2048).decode()



    # ---- Maybe in the future

    def change_server(self, new_server):
        self.server_address = new_server
