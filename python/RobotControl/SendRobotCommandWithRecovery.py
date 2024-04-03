from enum import Enum
from socket import socket as Socket
from RobotControl.RobotControl import send_command, get_safety_status, \
    get_robot_mode, get_running
from RobotControl.RobotSocketMessages import CommandFinished
from RobotControl.StateRecovery import list_of_variables, States, recover_state
from SocketMessages import CommandMessage
from ToolBox import escape_string
from URIFY import URIFY_return_string
from undo.History import History
from undo.State import State


class ResponseMessages(Enum):
    Invalid_state = "Program is in an invalid state"  # This will be checked before sending the users command
    Too_many_commands = "Too many interpreted messages"  # This is the only one that will be in the "return path/chain"
    Compile_error = "Compile error"  # These will be "disregarded in checking the safe result, since they will always be returned
    Syntax_error = "Syntax error"  # Same as the one above


class ResponseCodes(Enum):
    ACK = "ack"
    DISCARD = "discard"


def send_command_with_recovery(command: str, on_socket: Socket, command_id=None):
    """Command_id is important if a message containing the error should be sent back to the frontend."""
    result = send_command(command, on_socket)
    print(f"send_command_with_recovery method: Result: {escape_string(result)}")

    # TODO: Remove this responsibility from the send_command function
    ensure_state_recovery_if_broken(result, command, command_id)

    return result


def send_user_command(command: CommandMessage, on_socket: Socket) -> str:
    command_message = command.data.command
    test_history(command)

    response_from_command = send_command_with_recovery(command_message, on_socket, command_id=command.data.id)

    finish_command = CommandFinished(command.data.id, command_message, tuple(list_of_variables))
    string_command = finish_command.dump_ur_string()
    print(f"send_user_command method: String command: {escape_string(string_command)}")
    wrapping = URIFY_return_string(string_command)
    send_command_with_recovery(wrapping, on_socket, command_id=command.data.id)

    return response_from_command[:-2]  # Removes \n from the end of the response


def get_state_of_robot() -> States | None:
    safety_status = get_safety_status()
    robot_mode = get_robot_mode()
    running = get_running()
    if safety_status == "PROTECTIVE_STOP":
        return States.Protective_stop
    if safety_status == "NORMAL" and robot_mode == "RUNNING" and running == "false":
        return States.Invalid_state
    return None


def ensure_state_recovery_if_broken(response: str, command: str, command_id=None) -> str:
    """ This method will be extracted out into a wrapper function in a file named something like safeSendCommandToRobot"""
    out = response
    if out == "nothing":
        raise ValueError("Response from robot is nothing. This is not expected.")

    response_array = response.split(":")
    response_code = response_array[0]
    response_message = response_array[1]
    response_message = response_message[1:] if response_message[0] == " " else response_message

    if response_code == ResponseCodes.ACK.value:
        return out

    if response_message == ResponseMessages.Compile_error.value or response_message == ResponseMessages.Syntax_error.value:
        return out

    # If the robot has interpreted too many commands.
    robot_state: States = get_state_of_robot()
    recover_state(robot_state, command, command_id)

    return out


def test_history(command):
    history = History()
    history.new_command(command)
    history.debug_print()
