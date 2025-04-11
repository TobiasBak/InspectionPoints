


def create_get_socket_function() -> Callable[[str, int], Socket]:
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


get_socket = create_get_socket_function()

def _get_dashboard_socket():
    return get_socket(ROBOT_IP, DASHBOARD_PORT)


def send_command_dashboard_socket(command: str) -> str:
    dashboard_socket = _get_dashboard_socket()
    sanitized_command = sanitize_command(command)
    dashboard_socket.send(sanitized_command.encode())
    return read_from_socket(dashboard_socket)

# TODO Load urp program througrh dashboard server
# TODO Play program through dashboard server  

# TODO SSH and write urp file to server (maybe we can juste write to the urprograms)

# TODO SSH and read the log file to get variables


