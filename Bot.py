import socket
import threading
import random

from client import Client


def get_local_ipv4_address():
    # Get the local hostname
    temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    temp_sock.connect(("8.8.8.8", 80))
    return temp_sock.getsockname()[0]

class Bot(Client):
    def __init__(self, name, address, server_port, isBot=False):
        super().__init__(name)
        self.name = name
        self.address = address
        self.server_port = server_port
        self.disconnect = False
        self.isBot = isBot

    def answering_questions(self, client_socket):
        answer = random.choice(
            ['0', '1'])  # Randomly choose from the options
        print(f"{self.name} answered {answer}\n")
        client_socket.sendall(answer.encode())

    def run(self):
        con = False

        if not self.isBot:
            print(f'{self.name} started, connecting to server...\n')
        while not self.disconnect:
            self.tcp_client(self.address, self.server_port, isBot=self.isBot)


if __name__ == "__main__":

    bot_names = [
        "BOTalice",
        "BOTbob",
        "BOTrachel",
        "BOTdavid",
        "BOTemma",
        "BOTfrank",
        "BOTgina",
        "BOThenry",
        "BOTisabel",
        "BOTjack"
    ]

    bot_name = random.choice(bot_names)
    bot = Bot(bot_name, address=get_local_ipv4_address(), server_port=1710)
    bot.run()
