import socket
import threading
import random

from colorama import Fore

from client import Client


def get_local_ipv4_address():
    """
        Get the local IPv4 address of the machine.

        :return: The local IPv4 address.
        """
    # Get the local hostname
    temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    temp_sock.connect(("8.8.8.8", 80))
    return temp_sock.getsockname()[0]

class Bot(Client):
    """
        A class representing a bot client for the networking game. The bot acts exactly like a normal client,
        but answers questions randomly.
        """
    def __init__(self, name, address, server_port, isBot=False):
        """
                Initialize the Bot object.

                :param name: The name of the bot.
                :param address: The IP address of the server.
                :param server_port: The port number of the server.
                :param isBot: Boolean indicating whether the client is a bot.
                """
        super().__init__(name)
        self.name = name
        self.address = address
        self.server_port = server_port
        self.disconnect = False
        self.isBot = isBot

    def answering_questions(self, client_socket):
        """
                Answer questions asked by the server.

                :param client_socket: The TCP socket connected to the server.
                """
        answer = random.choice(
            ['0', '1'])  # Randomly choose from the options
        print(f"{self.name} answered {answer}\n")
        client_socket.sendall(answer.encode())

    def run(self):
        """
                Run the bot .
                """
        if not self.isBot:
            print(Fore.YELLOW + f'{self.name} started, connecting to server...\n')
        while not self.disconnect:
            self.tcp_client(self.address, self.server_port, isBot=self.isBot)


