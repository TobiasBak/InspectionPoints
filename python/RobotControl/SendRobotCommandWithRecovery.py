from enum import Enum
from RobotControl.RobotControl import send_command_interpreter_socket, get_safety_status, \
    get_robot_mode, get_running
from RobotControl.RobotSocketMessages import CommandFinished
from RobotControl.StateRecovery import States, recover_state
from URIFY import URIFY_return_string
from custom_logging import LogConfig
from undo.HistorySupport import find_variables_in_command, add_new_variable

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


class ResponseMessages(Enum):
    Invalid_state = "Program is in an invalid state"  # This will be checked before sending the users command
    Too_many_commands = "Too many interpreted messages"  # This is the only one that will be in the "return path/chain"
    Compile_error = "Compile error"  # These will be "disregarded in checking the safe result, since they will always be returned
    Syntax_error = "Syntax error"  # Same as the one above


class ResponseCodes(Enum):
    ACK = "ack"
    DISCARD = "discard"


def send_command_with_recovery(command: str, command_id=None) -> str:
    """Command_id is important if a message containing the error should be sent back to the frontend."""
    result = send_command_interpreter_socket(command)
    recurring_logger.debug(f"Result from robot: {result}")

    # TODO: Remove this responsibility from the send_command function
    out = result
    if out == "nothing":
        raise ValueError("Response from robot is nothing. This is not expected.")

    response_array = result.split(":")
    if len(response_array) < 2:
        recurring_logger.debug(f"Response array: {response_array}")
        raise ValueError("Response from robot is not in the expected format.")

    response_code = response_array[0]

    _list_of_variables = []

    if response_code == ResponseCodes.ACK.value:
        # If we get an ack, we need to get all the multiple variable definitions and single them out
        _list_of_variables = find_variables_in_command(command)
        for variable_definition in _list_of_variables:
            add_new_variable(variable_definition)
        return out

    response_message = response_array[1]
    response_message = response_message[1:] if response_message[0] == " " else response_message

    if response_message == ResponseMessages.Compile_error.value or response_message == ResponseMessages.Syntax_error.value:
        return out

    # We are in an invalid state, find out which one and recover
    robot_state: States = get_state_of_robot(response_message)
    if robot_state is not None:
        recurring_logger.info(f"\t\tRobot state before fixing: {robot_state}")
        recover_state(robot_state, command, command_id)

    out = ""  # Since we do not want to return the response to the frontend

    return out


def send_command_finished(command_id: int, command_message: str):
    finish_command = CommandFinished(command_id, command_message)
    string_command = finish_command.dump_ur_string()
    wrapping = URIFY_return_string(string_command)
    send_command_with_recovery(wrapping, command_id=command_id)


def get_state_of_robot(response_message: str) -> States | None:
    safety_status = get_safety_status()
    robot_mode = get_robot_mode()
    running = get_running()
    if response_message == ResponseMessages.Too_many_commands.value:
        return States.Too_many_commands
    if safety_status == "PROTECTIVE_STOP":
        return States.Protective_stop
    if safety_status == "NORMAL" and robot_mode == "RUNNING" and running == "false":
        return States.Invalid_state
    return None
