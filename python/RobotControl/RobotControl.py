import socket  # for socket
from socket import gethostbyname, gethostname
from socket import socket as Socket
from time import sleep
from typing import Callable

import select

from RobotControl.RobotSocketMessages import VariableObject
from RobotControl.RobotSocketVariableTypes import VariableTypes
from ToolBox import escape_string
from URIFY import SOCKET_NAME
from constants import ROBOT_FEEDBACK_PORT, ROBOT_IP, DASHBOARD_PORT, SECONDARY_PORT, INTERPRETER_PORT
from custom_logging import LogConfig

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


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

_interpreter_open = False


def get_dashboard_socket():
    return get_socket(ROBOT_IP, DASHBOARD_PORT)


def get_secondary_socket():
    return get_socket(ROBOT_IP, SECONDARY_PORT)


def get_interpreter_socket():
    """This function is safe to call multiple times.
    If the interpreter_socket is opened, then it will be returned from cache"""
    return get_socket(ROBOT_IP, INTERPRETER_PORT)


def start_interpreter_mode():
    secondary_socket = get_secondary_socket()
    clear_queue_on_enter = "clearQueueOnEnter = True"
    clear_on_end = "clearOnEnd = True"
    send_command(f"interpreter_mode({clear_queue_on_enter}, {clear_on_end})", secondary_socket)
    non_recurring_logger.debug("Interpreter mode command sent")


def start_robot():
    non_recurring_logger.debug("Power on robot")
    _power_on_robot()
    non_recurring_logger.info("Brake release robot")
    _brake_release_on_robot()
    non_recurring_logger.info("Start interpreter mode and connect to backend socket")
    _start_interpreter_mode_and_connect_to_backend_socket()


def apply_variables_to_robot(variables: list[VariableObject]):
    command = ""
    for variable in variables:
        if variable.variable_type == VariableTypes.String:
            command += f'{variable.name} = "{variable.value}" '
        else:
            command += f"{variable.name} = {variable.value} "
    send_command(command, get_interpreter_socket())
    non_recurring_logger.debug(f"\t\tVariables applied to robot: {command}")


def _start_interpreter_mode_and_connect_to_backend_socket():
    start_interpreter_mode()
    # Todo: For some reason the robot needs a sleep here, otherwise open_socket does not work.
    #  I thought the parameters on interpreter_mode would fix this. (clear_queue_on_enter, clear_on_end)
    sleep(1)
    connect_robot_to_feedback_socket()

    # Ensure that non-user inputted commands are not sent to the websocket.
    # We sleep, because the message has to be processed by the robot first.
    # I have tested values below 0.5, but they did not give reliable results.
    sleep(0.5)
    delayed_read = read_from_socket_till_end(get_interpreter_socket())
    non_recurring_logger.debug(f"Delayed read: {escape_string(delayed_read)}")


def clear_interpreter_mode():
    send_command("clear_interpreter()", get_interpreter_socket())
    recurring_logger.info("Clear command sent")


def _power_on_robot():
    dashboard_socket = get_dashboard_socket()
    send_command("power on", dashboard_socket)


def _brake_release_on_robot():
    dashboard_socket = get_dashboard_socket()
    send_command("brake release", dashboard_socket)


def unlock_protective_stop():
    # Unlock of the protective stop fails if less than 5 seconds have passed since the protective stop was triggered.
    sleep(5)

    result = get_value_from_dashboard("unlock protective stop")
    if result == "Protectivestopreleasing":
        non_recurring_logger.warning("Protective stop releasing")
        return
    else:
        non_recurring_logger.info(f"Unlock protective stop result: {result}")

    unlock_protective_stop()  # If release fails, try again


def get_safety_status():
    return get_value_from_dashboard("safetystatus")


def get_robot_mode():
    return get_value_from_dashboard("robotmode")


def get_running():
    return get_value_from_dashboard("running")


def get_value_from_dashboard(command: str):
    response = send_command(command, get_dashboard_socket())
    return sanitize_dashboard_reads(response)


def sanitize_dashboard_reads(response: str) -> str:
    message_parts = response.split(":")
    message = message_parts[-1]
    return message.replace('\\n', '').replace(' ', '')


def connect_robot_to_feedback_socket(host: str = gethostbyname(gethostname()), port: int = ROBOT_FEEDBACK_PORT):
    non_recurring_logger.debug(f"Connecting robot to feedback socket: {host}:{port}")
    send_command(f"socket_open(\"{host}\", {port}, {SOCKET_NAME})\n", get_interpreter_socket())


def sanitize_command(command: str) -> str:
    command = command.replace('\n', ' ')
    command += "\n"  # Add a trailing \n character
    return command


_extremely_randomized_command = f' FKSUYFCGSHILU213Y4387RGFBEI87 = "KFJSHEUIFYGEWIURG3" '


def send_command(command: str, on_socket: Socket) -> str:
    """Returns the ack_response from the robot. The ack_response is a string."""
    running_on_interpreter = on_socket == get_interpreter_socket() and "clear_interpreter()" not in command

    if running_on_interpreter:
        recurring_logger.debug(f"Modifying command: {escape_string(command)}")
        command += _extremely_randomized_command

    command = sanitize_command(command)
    recurring_logger.debug(f"Sending command to robot: {escape_string(command)}")

    on_socket.send(command.encode())
    recurring_logger.debug(f"Command sent to robot: {escape_string(command)}")

    result = read_from_socket(on_socket)
    out = ""
    count = 1
    while result != "nothing" and count < 2:
        out += result
        # time_print(f"Received {count}: {escape_string(result)}")
        result = read_from_socket(on_socket)
        count += 1

    if running_on_interpreter:
        recurring_logger.debug(f"Running while loop until end: {escape_string(out)}")
        while _extremely_randomized_command not in out:
            out += read_from_socket(on_socket)

        out = out.replace(_extremely_randomized_command, "")
        recurring_logger.debug(f"replacing randomized with empty strings: {escape_string(out)}")

    recurring_logger.debug(f"Result from robot: {escape_string(out)}")
    return escape_string(out)


def read_from_socket(socket: Socket) -> str:
    ready_to_read, ready_to_write, in_error = select.select([socket], [], [], 0.1)
    if ready_to_read:
        message = socket.recv(4096)

        try:
            return message.decode()
        except UnicodeDecodeError as e:
            # Intentionally not returning anything.
            # Returning nothing if a decode error occurs.
            recurring_logger.error(f"Error decoding message: {e}")

    return "nothing"


def read_from_socket_till_end(socket: Socket) -> str:
    out = ""
    message = read_from_socket(socket)
    while message != "nothing":
        out += message
        message = read_from_socket(socket)
    return out


if __name__ == '__main__':
    non_recurring_logger.info("Starting RobotControl.py")
    interpreter_socket: Socket = get_interpreter_socket()

    interpreter_socket.close()
