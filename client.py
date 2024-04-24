import socket
import struct
import threading
import time
import warnings

# Filter out the specific warning message
warnings.filterwarnings("ignore", message="Your system is avx2 capable but pygame was not built with support for it.")

import pygame
from colorama import Fore

LISTEN_PORT = 13117

"""
A class representing a client for the networking game. The client runs forever, until the user interrupts the program.
"""
class Client:

    """
    Initialize the Client object.

    :param name: The name of the client.
    """
    def __init__(self, name):
        self.name = name
        self.first = True
        self.address = 0
        self.server_port = 0
        self.disconnect = False

    """
    Play a sound.

    :param sound_file: The file path of the sound.
    :return: The pygame Sound object.
    """
    def play_sound(self, sound_file):
        pygame.mixer.init()  # Initialize the mixer
        sound = pygame.mixer.Sound(sound_file)  # Load the WAV file
        sound.play()
        return sound

    def stop_sound(self, sound):
        """
                Stop playing a sound.

                :param sound: The pygame Sound object to stop.
            """
        if sound:
            sound.stop()

    def receive_udp_message(self):
        """
                Receive UDP messages from the server.
                The client listens for offer requests from the server.
                The offer includes a magic cookie, offer message, server name, and server port.
                If the magic cookie and message type are correct, the client attempts to connect to the server through TCP
                using the provided server port and address.
        """
        # Create a UDP socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('', LISTEN_PORT))  # Bind to all available interfaces

                if self.first:
                    print(Fore.YELLOW + "Client started, listening for offer requests...")

                # Receive data from the socket
                while True:
                    sock.setblocking(True)
                    data, address = sock.recvfrom(1024)
                    address = address[0]
                    magic_cookie, message_type, server_name, server_port = struct.unpack('!IB32sH', data)
                    server_name = server_name.rstrip(b'\0').decode('utf-8')
                    if magic_cookie != 0xabcddcba or message_type != 0x2:
                        continue
                    else:
                        print(
                            Fore.CYAN + f"Received offer from server '{server_name}' at address {address}, attempting to connect...")
                        self.address = address
                        self.server_port = server_port
                        break
            sock.close()
        except KeyboardInterrupt:
            self.disconnect = True
            print(Fore.RED + 'Disconnecting.... Goodbye!')

    def get_input(self):
        """
        Get user input with a 10 second timer. If the user has not answered within the 10 seconds, then a default
        answer will be sent back to the server, eliminating the player.
        :return: user input
        """
        flag = False

        def timeout():
            nonlocal flag
            flag = True
            print(Fore.RED + 'Time is up! Enter any input to proceed')

        my_timer = threading.Timer(10, timeout)
        my_timer.start()
        user_input = input(Fore.YELLOW + 'Please enter your answer: \n').strip()
        my_timer.cancel()
        if flag:
            return 'NONE'
        else:
            return user_input

    def answering_questions(self, client_socket):
        """
                Answer questions asked by the server.

                :param client_socket: The TCP socket connected to the server.
                """
        answer = self.get_input()
        client_socket.sendall(answer.encode())

    def tcp_client(self, host, port, isBot=False):
        """
                Connect to the server via TCP and handle communication.

                :param host: The IP address of the server.
                :param port: The port number of the server.
                :param isBot: Boolean indicating whether the client is a bot.
        """
        try:
            # Create a TCP/IP socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                try:
                    client_socket.connect((host, port))
                    client_socket.sendall(self.name.encode())
                    while True:
                        client_socket.settimeout(None)
                        data = client_socket.recv(1024)
                        if data.decode().startswith("Game over!") or data.decode().startswith("Game is tied"):
                            if not isBot:
                                print(Fore.RED + data.decode())
                                self.stop_sound(sound)
                                if f'Congratulations to the winner: {self.name}' in data.decode():
                                    self.play_sound('win_sound.wav')
                            if isBot:
                                self.disconnect = True
                            break
                        elif data.decode().startswith(f"True or False:"):
                            if not isBot:
                                print(Fore.CYAN + data.decode())
                            self.answering_questions(client_socket)
                        elif data.decode() != "":
                            if not isBot:
                                print(Fore.LIGHTMAGENTA_EX + data.decode())
                                if data.decode().startswith('Round'):
                                    sound = self.play_sound('drum_roll.wav')
                                if data.decode().startswith('Sorry'):
                                    self.stop_sound(sound)

                        elif data.decode() == "":
                            break
                except ConnectionRefusedError:
                    print(Fore.YELLOW + "Game currently in progress. Trying again in 10 seconds....\n")
                    time.sleep(10)

        except (OSError, UnboundLocalError):
            pass
        except (KeyboardInterrupt,UnboundLocalError):
            self.disconnect = True

        finally:
            client_socket.close()
            self.first = False
            if not isBot:
                if self.disconnect:
                    print(Fore.RED + 'Shutting down client.... Goodbye!')
                else:
                    print(Fore.RED + 'Server disconnected, listening for offer requests...\n\n')
                self.stop_sound(sound)

    def run(self):
        while not self.disconnect:
            self.receive_udp_message()
            if not self.disconnect:
                self.tcp_client(self.address, self.server_port)


if __name__ == "__main__":
    player_name = 'gab'
    client = Client(player_name)
    client.run()

































