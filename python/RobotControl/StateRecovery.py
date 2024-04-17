from enum import Enum, auto
from typing import Callable

from RobotControl.RobotControl import send_command, get_interpreter_socket, clear_interpreter_mode, \
    unlock_protective_stop, _start_interpreter_mode_and_connect_to_backend_socket, apply_variables_to_robot, \
    list_of_variables
from RobotControl.RobotSocketMessages import InterpreterCleared
from SocketMessages import AckResponse
from WebsocketNotifier import websocket_notifier
from custom_logging import LogConfig

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


class States(Enum):
    Invalid_state = auto()
    Too_many_commands = auto()
    Protective_stop = auto()


def recover_state(state: States, command: str, command_id: int | None):
    match state:
        case States.Invalid_state:
            recover_from_invalid_state(command, command_id)
        case States.Too_many_commands:
            recover_from_too_many_commands(command, command_id)
        case States.Protective_stop:
            recover_from_protective_stop(command, command_id)
        case _:
            raise ValueError(f"Unknown state send to recover_state functionality: {state}")


def recover_from_invalid_state(command: str, command_id: int | None):
    recurring_logger.warning(f"\t\t\tInterpreter mode is stopped, restarting interpreter ")
    _start_interpreter_mode_and_connect_to_backend_socket()
    apply_variables_to_robot(list_of_variables)  # Temporary fix
    if command_id is not None:
        # Todo: We need ssh to see the logs for optimal feedback
        ack_response = AckResponse(command_id, command,
                                   f"discard: Command caused invalid state. Can be due to following reasons:\n"
                                   f"1. array out of bounds.\n"
                                   f"2. Reassigning variable to new type.\n"
                                   f"3. Error occurred in the program. Did you write a proper command?\n")
        websocket_notifier.notify_observers(str(ack_response))
    send_command(command, get_interpreter_socket())


_pending_clears = {
    "open": False,
    "pending_id": 0,
}

_clear_callbacks: dict[int, Callable[[], None]] = {

}


def recover_from_too_many_commands(command: str, command_id: int | None):
    if _pending_clears["open"]:
        recurring_logger.debug(f"\t\t\tClear command already pending.")
        return
    recurring_logger.info(f"\t\t\tToo many commands detected. Will fix the state.")
    _pending_clears["open"] = True
    _pending_clears["pending_id"] += 1
    clear_interpreter_mode(_pending_clears["pending_id"])

    def callback() -> None:
        apply_variables_to_robot(list_of_variables)  # Temporary fix
        result = send_command(command, get_interpreter_socket())  # Resend command since it was lost.
        if command_id is not None:
            ack_response = AckResponse(command_id, command, result)
            websocket_notifier.notify_observers(str(ack_response))

    _clear_callbacks[_pending_clears["pending_id"]] = callback


def handle_cleared_interpreter(robot_message: InterpreterCleared) -> None:
    non_recurring_logger.info(f"Interpreter cleared: {robot_message}")
    _pending_clears["open"] = False

    if _pending_clears["pending_id"] != robot_message.cleared_id:
        non_recurring_logger.warning(f"Pending clear id: {_pending_clears['pending_id']} does not match cleared id: {robot_message.cleared_id}")

    callback = _clear_callbacks[robot_message.cleared_id]
    if callback is not None:
        callback()
        _clear_callbacks.clear()


def recover_from_protective_stop(command: str, command_id: int | None):
    recurring_logger.warning(f"\t\t\tRobot is in protective stop. Attempting to unlock; Command id: {command_id}")
    if command_id is not None:
        # Todo: We need ssh to see the logs for optimal feedback
        ack_response = AckResponse(command_id, command,
                                   f"discard: Command caused protective stop. Please investigate the cause before continuuing. Unlocking in 5 seconds. \n")
        websocket_notifier.notify_observers(str(ack_response))

    unlock_protective_stop()
    _start_interpreter_mode_and_connect_to_backend_socket()
    apply_variables_to_robot(list_of_variables)  # Temporary fix
    send_command(command, get_interpreter_socket())
