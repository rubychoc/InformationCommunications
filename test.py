import inputimeout

# def get_user_input():
#     try:
#         answer = inputimeout.inputimeout(prompt='Please type in your answer: ', timeout=10)



def get_local_ipv4_address():
    # Get the local hostname
    temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    temp_sock.connect(("8.8.8.8", 80))
    return temp_sock.getsockname()[0]

ans = -1
listen_event = threading.Event()
listen_event.clear()
def rc_socket():
    global ans
    global listen_event
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the address given on the command line
    sock.bind((get_local_ipv4_address(), 1234))
    sock.listen()
    listen_event.set()
    client_socket, client_address = sock.accept()
    client_socket.settimeout(10)
    try:
        answer = client_socket.recvfrom(1024)[0].decode()
        if answer != "":
            ans = answer
    except socket.timeout:
        ans = 'NONE'
        print("Time is up! You did not answer in time.")
    finally:
        client_socket.close()
        sock.close()


def send_ans():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((get_local_ipv4_address(), 1234))
        ans = input("Please type in your answer: ")
        sock.settimeout(10)
        sock.sendall(ans.encode())
    except socket.timeout:
        print('done')
    except OSError:
        print('Disconnecting.... Goodbye!')


send = threading.Thread(target=send_ans)
receive = threading.Thread(target=rc_socket)
receive.start()
listen_event.wait()
send.start()
send.join()
receive.join()
print(ans)






# class myClass:
#     _input = None
#
#     def __init__(self):
#         get_input_thread = threading.Thread(target=self.get_input)
#         get_input_thread.daemon = True  # Otherwise the thread won't be terminated when the main program terminates.
#         get_input_thread.start()
#         try:
#             get_input_thread.join(timeout=5)
#         except Exception:
#             pass
#
#         if myClass._input is None:
#             print("No input was given within 20 seconds")
#         else:
#             print("Input given was: {}".format(myClass._input))
#
#     @classmethod
#     def get_input(cls):
#         try:
#             cls._input = input("give me some input:")
#             return
#         except Exception:
#             pass





# get_user_input()

# def signal_handler(signum, frame):
#     raise TimeoutError("Time is up! You did not answer in time.")
#
# def get_input(timeout=10):
#     # Set the signal handler to raise TimeoutError after the timeout
#     signal.signal(signal.SIGALRM, signal_handler)
#     signal.alarm(timeout)  # Set the alarm signal after timeout seconds
#     try:
#         answer = input("Please type in your answer:\n")
#         signal.alarm(0)  # Cancel the alarm
#         return answer
#     except TimeoutError as e:
#         print(e)
#         return 'NONE'
#
#
# def answering_questions():
#     answer = get_input()
#     print(f'Your answer is: {answer}\n')
#
#
# while True:
#     answering_questions()
#


















# import threading
#
# def answering_questions():
#     # Create an event to signal when input is received
#     print('new iteration')
#     input_rcv = False
#     answer = 'NONE'
#
#     def get_input():
#         nonlocal answer
#         nonlocal input_rcv
#         answer = input("Please type in your answer:\n")
#         input_rcv = True
#         return
#
#     # Start a new thread to get input
#     input_thread = threading.Thread(target=get_input)
#     input_thread.start()
#
#     # Wait for the input thread to finish or timeout
#     input_thread.join(5)
#
#     # If the input thread is still running, stop it
#     if input_thread.is_alive():
#         input_thread.join(timeout=0)  # Ensure the thread terminates
#     #input_event.wait(5)
#
#     # If user input is provided, return it
#     if input_rcv:
#         print(f'your answer is: {answer}\n')
#     # If timeout occurs, return the default value
#     else:
#         print("Time is up! You did not answer in time.")
#         print(answer+'\n')
#
#
# while True:
#     answering_questions()

