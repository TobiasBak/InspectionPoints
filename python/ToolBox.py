from time import sleep
import socket 
from socket import socket as Socket
from typing import Callable

from custom_logging import LogConfig

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)

def escape_string(string: str) -> str:
    try:
        out = string.encode('unicode_escape').decode('utf-8')
    except Exception as e:
        out = string
    return out

def _create_get_socket_function() -> Callable[[str, int], Socket]:
        inner_socket_bank: dict[tuple[str, int], Socket] = dict()

        def inner_get_socket(ip: str, port: int) -> Socket | None:
            if (ip, port) in inner_socket_bank:
                return inner_socket_bank[(ip, port)]
            try:
                my_socket: Socket = Socket(socket.AF_INET, socket.SOCK_STREAM)
                non_recurring_logger.debug(f"Socket successfully created for {ip}:{port}")
            except socket.error as err:
                non_recurring_logger.error(f"socket creation failed with error {err}")
                return

            try:
                my_socket.connect((ip, port))
                non_recurring_logger.debug(f"Socket connected to {ip}:{port}")
            except ConnectionRefusedError:
                non_recurring_logger.info(f"Connection to {ip}:{port} refused - retrying in 1 second")
                my_socket.close()
                sleep(1)
                return get_socket(ip, port)

            my_socket.setblocking(False)
            inner_socket_bank[(ip, port)] = my_socket
            return my_socket

        return inner_get_socket

get_socket = _create_get_socket_function()
