import signal
import socket
import struct
import sys
from colorama import Fore
import select
import threading
import select
import time
import ipaddress


LISTEN_PORT = 13117


class Client:

    def __init__(self, name):
        self.name = name
        self.first = True
        self.address = 0
        self.server_port = 0
        self.disconnect = False

    def receive_udp_message(self):
        # Create a UDP socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                sock.bind(('', LISTEN_PORT))  # Bind to all available interfaces

                if self.first:
                    print("Client started, listening for offer requests...")

                # Receive data from the socket
                while True:
                    sock.setblocking(True)
                    data, address = sock.recvfrom(1024)
                    address = address[0]
                    magic_cookie, message_type, server_name, server_port = struct.unpack('!IB32sH', data)
                    server_name = server_name.rstrip(b'\0').decode('utf-8')
                    if magic_cookie != 0xabc or message_type != 0x2:
                        continue
                    else:
                        print(f"Received offer from server '{server_name}' at address {address}, attempting to connect...")
                        self.address = address
                        self.server_port = server_port
                        break
            sock.close()
        except KeyboardInterrupt:
            self.disconnect = True
            print('Disconnecting.... Goodbye!')

    def signal_handler(self,signum, frame):
        raise TimeoutError("Time is up! You did not answer in time.")

    def get_input(self, timeout=10):
        # Set the signal handler to raise TimeoutError after the timeout
        signal.signal(signal.SIGALRM, self.signal_handler)
        signal.alarm(timeout)  # Set the alarm signal after timeout seconds
        try:
            answer = input("Please type in your answer:\n")
            signal.alarm(0)  # Cancel the alarm
            return answer
        except TimeoutError as e:
            print(e)
            return 'NONE'

    def answering_questions(self, client_socket):
        answer = self.get_input()
        client_socket.sendall(answer.encode())

    def tcp_client(self, host, port, isBot = False):
        try:
            # Create a TCP/IP socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                try:
                    client_socket.connect((host, port))
                    client_socket.sendall(self.name.encode())
                    while True:
                        client_socket.settimeout(None)
                        data = client_socket.recv(1024)
                        if data.decode().startswith("Game over") or data.decode().startswith("Game is tied"):
                            if not isBot:
                                print(data.decode())
                            if isBot:
                                self.disconnect = True
                            break
                        elif data.decode().startswith("True or False:"):
                            if not isBot:
                                print(data.decode())
                            self.answering_questions(client_socket)
                        elif data.decode() != "":
                                if not isBot:
                                    print(data.decode())
                        elif data.decode() == "":
                            break
                except ConnectionRefusedError:
                    print("Game currently in progress. Trying again in 10 seconds....\n")
                    time.sleep(10)

        except OSError:
            pass
        except KeyboardInterrupt:
            self.disconnect = True

        finally:
            client_socket.close()
            self.first = False
            if not isBot:
                if self.disconnect:
                    print('Shutting down client.... Goodbye!')
                else:
                    print('Server disconnected, listening for offer requests...\n\n')

    def run(self):
        while not self.disconnect:
            self.receive_udp_message()
            if not self.disconnect:
                self.tcp_client(self.address, self.server_port)


if __name__ == "__main__":
    player_name = 'ruby'
    client = Client(player_name)
    client.run()

