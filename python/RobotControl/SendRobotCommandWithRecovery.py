import time
from enum import Enum

from RobotControl.RobotControl import send_command_interpreter_socket, get_safety_status, \
    get_robot_mode, get_running
from RobotControl.RobotSocketMessages import CommandFinished
from RobotControl.StateRecovery import States, recover_state, generate_command_finished
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


def send_command_with_recovery(command: str, command_id, is_command_finished: bool = False, is_undo_command: bool = False) -> str:
    """
    Command_id is important if a message containing the error should be sent back to the frontend.
    The is_command_finished was added since this method adds new variables to the variable registry.
    And this should only happen if commands are not breaking, which only command_finished knows.
    """

    command_to_send = command

    if is_command_finished:
        # Otherwise robot acknowledges variable definitions before trying to set the variable.
        # p1, p2 = p[1,1,1,1,1,1]
        # p3 = p2-p1 Here the robot will return ack for p3 and return ack for command_finished for p3.
        # However, the robot breaks immediately after the second ack, because it realizes that subtracting is not possible
        time.sleep(0.1)
        command_to_send = generate_command_finished(command_id, command)

    result = send_command_interpreter_socket(command_to_send)
    recurring_logger.debug(f"Result from robot: {result}")

    out = result
    if out == "nothing":
        raise ValueError("Response from robot is nothing. This is not expected.")

    response_array = result.split(":")
    if len(response_array) < 2:
        recurring_logger.debug(f"Response array: {response_array}")
        raise ValueError("Response from robot is not in the expected format.")

    response_code = response_array[0]

    if response_code == ResponseCodes.ACK.value and not is_command_finished and not is_undo_command:
        return out

    _list_of_variables = []
    if response_code == ResponseCodes.ACK.value and is_command_finished or response_code == ResponseCodes.ACK.value and is_undo_command:
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
    time.sleep(0.1)  # So the robot has time to react to the command
    robot_state: States = get_state_of_robot(response_message)
    if robot_state is not None:
        recurring_logger.info(f"\t\tRobot state before fixing: {robot_state}")
        recover_state(robot_state, command, command_id)

    if command_id is None:
        out = ""  # Since we do not want to return the response to the frontend

    return out


def send_command_finished(command_id: int, command_message: str):
    # finish_command = CommandFinished(command_id, command_message)
    # string_command = finish_command.dump_ur_string()
    # wrapping = URIFY_return_string(string_command)
    send_command_with_recovery(command_message, command_id=command_id, is_command_finished=True)


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
