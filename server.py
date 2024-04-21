import concurrent.futures
import socket
import struct
import sys
import time
import ipaddress
import threading
from Bot import Bot

# Function to pad server name to 32 characters
def pad_server_name(server_name):
    return server_name.ljust(32, '\0')


def get_local_ipv4_address():
    # Get the local hostname
    temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    temp_sock.connect(("8.8.8.8", 80))
    return temp_sock.getsockname()[0]

# Define constants
MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE_OFFER = 0x2
LOCAL_IP = get_local_ipv4_address()
server_name = pad_server_name("Lucky Bunnies")


def get_local_broadcast_ip():
    # Get the local IP address
    ip = LOCAL_IP
    # Get the local network mask
    mask = ipaddress.IPv4Network(ip + '/24', strict=False)
    # Get the broadcast IP address
    broadcast_ip = str(mask.broadcast_address)
    return broadcast_ip


def udp_broadcast():
    BROADCAST_IP = get_local_broadcast_ip()
    BROADCAST_PORT = 13117
    server_port = 1710
    packed_data = struct.pack('!IB32sH', MAGIC_COOKIE, MESSAGE_TYPE_OFFER, server_name.encode('utf-8'), server_port)

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Set the socket to broadcast and enable reusing addresses
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        print(f'Server started, listening on IP address: {LOCAL_IP}')
        time.sleep(0.5)
        while True:
            # Send new message every second
            sock.sendto(packed_data, (BROADCAST_IP, BROADCAST_PORT))
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping broadcast')
        # Close the socket
        sock.close()


questions = {
    "Aston Villa's current manager is Pep Guardiola": True,
    "Aston Villa's home stadium is Villa Park": True,
    "Aston Villa has won the UEFA Champions League": False,
}

acceptable_answers = {'0': 'F', '1': 'T', 'Y': 'T', 'N': 'F', 'T': 'T', 'F': 'F', 'NONE': None}
disconnected_clients = {}
pid_to_name = {}


def tcp_server(host, port):
    global pid_to_name
    global disconnected_clients
    welcome_msg = "Please wait for other players to join...\n"

    # Function to send welcome message to all the clients
    def handle_client(client_id, client_socket, players):
        try:
            player_name = client_socket.recv(1024)
            client_socket.sendall(welcome_msg.encode())
            print(f"Player {player_name.decode()} joined the lobby.\n")
            send_to_all(client_sockets_og, f"Player {player_name.decode()} joined the lobby.\n")
            players[client_id] = (player_name.decode())
        except OSError:
            global disconnected_clients
            disconnected_clients[client_id] = players[client_id]


    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the address and port

    con = False
    while not con:
        try:
            server_socket.bind((host, port))
            con = True
        except OSError:

            server_socket.close()
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        while True:
            # Listen for incoming connections
            server_socket.listen()
            pid_to_name = {}
            players = {}
            client_sockets_og = {}
            # Accept incoming connections, create a new thread for each client,
            # and welcome them, while waiting for all players to join the lobby.
            i = 0
            while True:
                client_handlers = []
                try:
                    i += 1
                    client_socket, client_address = server_socket.accept()
                    client_handler = threading.Thread(target=handle_client, args=(i, client_socket, players))
                    client_sockets_og[i] = client_socket
                    client_handler.start()
                    client_handlers.append(client_handler)
                    server_socket.settimeout(10)
                except socket.timeout:
                    # If no new connections are made within the 10 second period, start the game
                    server_socket.settimeout(None)
                    for t in client_handlers:
                        t.join()
                    for client_id, sock in client_sockets_og.copy().items():
                        try:
                            # Check if the socket is still connected
                            sock.sendall("".encode())
                        except OSError:
                            # If an OSError is raised, the socket is no longer connected
                            print(f"Player {players[client_id]} is no longer connected")
                            client_sockets_og.pop(client_id)
                            players.pop(client_id)
                    break

            client_sockets = dict(client_sockets_og)
            # print(welcome_msg)

            time.sleep(1)

            check_if_disconnected(client_sockets, client_sockets_og, players)

            if len(client_sockets) == 0:
                print('No players connected, waiting for new players...\n\n')
                continue
            elif len(client_sockets) == 1:
                print('Not enough players. Adding bots to the game.')
                send_to_all(client_sockets, 'Not enough players. Adding bots to the game.')
                add_bots = []
                i = len(client_sockets)
                for j in range(4 - len(client_sockets)):
                    i += 1
                    server_socket.listen()
                    bot_thread = threading.Thread(target=Bot(f'RandomName{i}', address=LOCAL_IP, server_port=1710, isBot=True).run)
                    bot_thread.start()
                    client_socket, client_address = server_socket.accept()
                    client_handler = threading.Thread(target=handle_client, args=(i, client_socket, players))
                    client_sockets_og[i] = client_socket
                    client_sockets[i] = client_socket
                    client_handler.start()
                    client_handler.join()

            time.sleep(1)
            check_if_disconnected(client_sockets, client_sockets_og, players)


            print('Welcome to LuckyBunnies Server, where we are answering trivia questions about Aston Villa FC.\n')
            send_to_all(client_sockets, 'Welcome to LuckyBunnies Server, where we are answering trivia questions about Aston Villa FC.\n')
            print("Loading game...\n")
            send_to_all(client_sockets, "Loading game...")
            time.sleep(1)
            message = ""
            pid_to_name = dict(players)

            for i, key in enumerate(pid_to_name.keys()):
                message += f"Player {i+1}: {pid_to_name[key]}\n"
            message += "===============\n"
            print(message)
            curr_threads = []
            # send the players list to all the clients
            send_to_all(client_sockets, message)

            curr_threads = []
            time.sleep(2)
            # Start the game: send questions to all the clients and wait for their answers
            i = 1
            for question in questions:
                for dc in disconnected_clients:
                    print(f'{disconnected_clients[dc]} has disconnected from the game.')
                    send_to_all(client_sockets, f'{disconnected_clients[dc]} has disconnected from the game.\n')
                    pid_to_name.pop(dc)
                    client_sockets.pop(dc)

                disconnected_clients = {}

                check_if_disconnected(client_sockets, client_sockets_og, pid_to_name)

                if len(pid_to_name) < 2:
                    break

                next_round = f'Round {i}, played by '
                next_round += ', '.join([pid_to_name[player] for player in client_sockets.keys()]) + ':'
                print(next_round)
                send_to_all(client_sockets, f'{next_round}\n')
                i += 1
                res = play(client_sockets, pid_to_name, question, curr_threads)
                if res is True:
                    if len(pid_to_name) == 1:
                        break

            if len(pid_to_name) == 0:
                send_to_all(client_sockets_og, "Game is tied !")
                print("No players left in the game.\nGame over, sending out offer requests...\n\n")

            elif len(pid_to_name) > 1:
                print("Game is tied !\nLooking for new players... ")
                send_to_all(client_sockets_og, "Game is tied !")

            elif len(pid_to_name) == 1:
                name = next(iter(pid_to_name.values()))
                time.sleep(2)
                print(f'Game over!\nCongratulations to the winner: {name}\n')
                send_to_all(client_sockets_og, f'Game over!\nCongratulations to the winner: {name}\n')
                time.sleep(2)
                print("Game over, sending out offer requests...\n\n")

    except KeyboardInterrupt:
        server_socket.close()
        print("Shutting down the server... Goodbye!")


# def tiebreaker(client_sockets, pid_to_name, curr_threads):
#     question = "The capital of Israel is Ramat Efal"
#     # a timer shown on the console to count down the time for the tiebreaker
#     tiebreak_msg = "Tiebreaker round! The first player to answer correctly wins the game.\n"
#     print(tiebreak_msg)
#     send_to_all(client_sockets, f'{tiebreak_msg}\n')
#     time.sleep(2)
#     for i in range(5, 0, -1):
#         print(f'Tiebreaker starting in {i} seconds...')
#         send_to_all(client_sockets, f'Tiebreaker starting in {i} seconds...\n')
#         time.sleep(1)
#     res = play(client_sockets, pid_to_name, question, curr_threads, tiebreaker = True)
#     if res is True:
#     for i in range(5, 0, -1):
#         print(f'Tiebreaker starting in {i} seconds...')
#         time.sleep(1)


def play(client_sockets, pid_to_name, question, curr_threads, tiebreaker = False):
    print(f"True or False: {question}\n")
    client_answers = {}
    for client_id, sock in client_sockets.items():
        t = threading.Thread(target=send_question, args=(client_id, sock, question))
        t.start()
        curr_threads.append(t)
    for t in curr_threads:
        t.join()
    curr_threads = []
    for idx, client_id in enumerate(client_sockets):
        sock = client_sockets[client_id]
        t = threading.Thread(target=play_trivia, args=(client_id,sock, idx, question, client_answers))
        t.start()
        curr_threads.append(t)
    for t in curr_threads:
        t.join()
    if everyone_wrong_or_right(list(client_answers.values())):
        print('Nobody is eliminated this round! Let"s move to the next round.')
        send_to_all(client_sockets, 'Nobody is eliminated this round! Let"s move to the next round.')
        time.sleep(1)
        return True
    time.sleep(2)
    mess = ''
    if len(pid_to_name) > 2:
        for player in client_answers.keys():
            print(f'{pid_to_name[player]} {client_answers[player]}')
            mess += f'{pid_to_name[player]} {client_answers[player]}\n'
    else:
        for player in client_answers.keys():
            ans = client_answers[player]
            if ans == "is correct!":
                print(f'{pid_to_name[player]} is correct! {pid_to_name[player]} wins!')
                mess += f'{pid_to_name[player]} is correct! {pid_to_name[player]} wins!\n'
            else:
                print(f'{pid_to_name[player]} {client_answers[player]}')
                mess += f'{pid_to_name[player]} {client_answers[player]}\n'

    send_to_all(client_sockets, mess)

    for player in client_answers.keys():
        if client_answers[player] != 'is correct!':
            t = threading.Thread(target=elimination_msg, args=(client_sockets[player], pid_to_name[player]))
            t.start()
            client_sockets.pop(player)
            pid_to_name.pop(player)



def check_if_disconnected(client_sockets, client_sockets_og, players):
    for client_id, sock in client_sockets.copy().items():
        try:
            # Check if the socket is still connected
            sock.sendall("".encode())
        except OSError:
            # If an OSError is raised, the socket is no longer connected
            print(f"{players[client_id]} has disconnected.")
            client_sockets.pop(client_id)
            client_sockets_og.pop(client_id)
            players.pop(client_id)


def everyone_wrong_or_right(lst):
    return all([x != 'is correct!' for x in lst]) or all([x == 'is correct!' for x in lst])


def safe_sendall(client_id,sock, message):
    try:
        sock.sendall(message.encode())
    except (OSError, socket.timeout, ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
        if client_id in pid_to_name:
            global disconnected_clients
            disconnected_clients[client_id] = pid_to_name[client_id]


def send_to_all(list_of_sockets, msg):
    try:
        curr_threads = []
        curr = None
        for client_id, sock in list_of_sockets.copy().items():
            curr = client_id
            t = threading.Thread(target=lambda sockt, message: safe_sendall(client_id, sockt,msg), args=(sock, msg))
            t.start()
            curr_threads.append(t)
        for t in curr_threads:
            t.join()
    except (OSError, socket.timeout, ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
        if curr in pid_to_name:
            global disconnected_clients
            disconnected_clients[curr] = pid_to_name[curr]


# def gameover_msg(conn, name):
#     try:
#         conn.sendall(f'Game over!\nCongratulations to the winner: {name}'.encode())
#     except (OSError, socket.timeout, ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
#         pass

def elimination_msg(conn, name):
    try:
        conn.sendall(
            f"Sorry {name}, you are out of the game!\nPlease wait for the final results.\n".encode())
    except (OSError,socket.timeout, ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        pass


def send_question(client_id, conn, question):
    try:
        conn.sendall(f"True or False: {question}\n".encode())
    except (OSError, socket.timeout, ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        if client_id in pid_to_name:
            global disconnected_clients
            disconnected_clients[client_id] = pid_to_name[client_id]


def play_trivia(client_id, conn, idx, question, client_answers):
    global disconnected_clients
    try:
        ans = conn.recv(1024).decode().strip().upper()
        if ans == "":
            disconnected_clients[client_id] = pid_to_name[client_id]
            return
        client_answer = acceptable_answers.get(ans, 'bad answer')
        correct_answer = 'T' if questions[question] else 'F'

        if client_answer is None:
            client_answers[client_id] = 'did not answer in time !'
        elif client_answer == 'bad answer':
            client_answers[client_id] = 'gave an invalid input !'
        elif client_answer == correct_answer:
            client_answers[client_id] = 'is correct!'
        else:
            client_answers[client_id] = 'is incorrect!'
    except (socket.timeout, ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        # client_answers[client_id] = 'incorrect'
        if client_id in pid_to_name:
            disconnected_clients[client_id] = pid_to_name[client_id]


if __name__ == "__main__":
    # Start the server
   try:
        thread_a = threading.Thread(target=udp_broadcast)
        thread_b = threading.Thread(target=tcp_server, args=(LOCAL_IP, 1710))
        # Start both threads
        thread_a.start()
        thread_b.start()

        thread_a.join()
        thread_b.join()
   except KeyboardInterrupt:
       pass
   finally:
       print("Server is shutting down...Goodbye!")



# tcp_server(LOCAL_IP, 1710)
# #
# udp_broadcast()
