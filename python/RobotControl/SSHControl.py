import socket
from socket import socket as Socket
from time import sleep
from typing import Callable
import select


from constants import ROBOT_IP, DASHBOARD_PORT

def create_get_socket_function() -> Callable[[str, int], Socket]:
    inner_socket_bank: dict[tuple[str, int], Socket] = dict()

    def inner_get_socket(ip: str, port: int) -> Socket | None:
        if (ip, port) in inner_socket_bank:
            return inner_socket_bank[(ip, port)]
        try:
            my_socket: Socket = Socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as err:
            return
        try:
            my_socket.connect((ip, port))
        except ConnectionRefusedError:
            my_socket.close()
            sleep(1)
            return get_socket(ip, port)

        my_socket.setblocking(False)
        inner_socket_bank[(ip, port)] = my_socket
        return my_socket

    return inner_get_socket

get_socket = create_get_socket_function()

def _get_dashboard_socket():
    return get_socket(ROBOT_IP, DASHBOARD_PORT)

def read_from_socket(socket: Socket) -> str:
    ready_to_read, ready_to_write, in_error = select.select([socket], [], [], 0.1)
    if ready_to_read:
        message = socket.recv(4096)

        try:
            return message.decode()
        except UnicodeDecodeError as e:
            # Intentionally not returning anything.
            # Returning nothing if a decode error occurs.
            print(f"Decode error: {e}")

    return "nothing"


def read_from_socket_till_end(socket: Socket) -> str:
    out = ""
    message = read_from_socket(socket)
    while message != "nothing":
        out += message
        message = read_from_socket(socket)
    return out

def sanitize_command(command: str) -> str:
    command = command.replace('\n', ' ')
    command += "\n"  # Add a trailing \n character
    return command

def send_command_dashboard_socket(command: str) -> str:
    dashboard_socket = _get_dashboard_socket()
    sanitized_command = sanitize_command(command)
    dashboard_socket.send(sanitized_command.encode())
    return read_from_socket(dashboard_socket)

def load_urp_program(program_name: str):
    assert(program_name.endswith(".urp"), "Program name must end with .urp")
    send_command_dashboard_socket(f"load {program_name}")

def start_loaded_program():
    send_command_dashboard_socket("play")


# TODO SSH and write urp file to server (maybe we can juste write to the urprograms)

# TODO SSH and read the log file to get variables


