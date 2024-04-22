import socket
import threading
import random

from colorama import Fore

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
            print(Fore.YELLOW + f'{self.name} started, connecting to server...\n')
        while not self.disconnect:
            self.tcp_client(self.address, self.server_port, isBot=self.isBot)


# if __name__ == "__main__":
#     bot_names = [
#         "BOT_columbus",
#         "BOT_magellan",
#         "BOT_cook",
#         "BOT_vespucci",
#         "BOT_hudson",
#         "BOT_cabot",
#         "BOT_drake",
#         "BOT_marco_polo",
#         "BOT_champlain",
#         "BOT_cortes",
#         "BOT_pizarro",
#         "BOT_cartier",
#         "BOT_la_salle",
#         "BOT_park",
#         "BOT_livingstone",
#         "BOT_vasco_da_gama",
#         "BOT_pedro_alvares_cabral",
#         "BOT_zheng_he",
#         "BOT_meriwether_lewis",
#         "BOT_william_clark"
#     ]
#     # # port = server.available_port
#     # bot_name = random.choice(bot_names)
#     # bot = Bot(bot_name, address=get_local_ipv4_address(), server_port=port)
#     # bot.run()
