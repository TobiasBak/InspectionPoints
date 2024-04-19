from enum import Enum, auto

from RobotControl.ClearingInterpreter import clear_is_pending, call_and_clear_callback, queued_clear_interpreter
from RobotControl.RobotControl import send_command_interpreter_socket, unlock_protective_stop, \
    _start_interpreter_mode_and_connect_to_backend_socket, get_interpreter_socket
from RobotControl.RobotSocketMessages import InterpreterCleared
from SocketMessages import AckResponse
from WebsocketNotifier import websocket_notifier
from custom_logging import LogConfig
from undo.HistorySupport import get_latest_code_state, get_latest_active_command_state, \
    find_variables_in_command, delete_variables_from_variable_registry

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
            recurring_logger.error(f"Unknown state sent to recover_state functionality: {state}")
            raise ValueError(f"Unknown state sent to recover_state functionality: {state}")


def recover_from_invalid_state(command: str, command_id: int | None):
    recurring_logger.warning(f"\t\t\tInterpreter mode is stopped, restarting interpreter ")
    _start_interpreter_mode_and_connect_to_backend_socket()
    __recover_latest_code_state()
    if command_id is not None:
        # Todo: We need ssh to see the logs for optimal feedback

        actual_command_that_caused_invalid_state = get_latest_active_command_state().get_user_command().data.command
        list_of_definitions = find_variables_in_command(actual_command_that_caused_invalid_state)
        delete_variables_from_variable_registry(list_of_definitions)

        non_recurring_logger.debug(f"Removing variable definition: {list_of_definitions}")
        ack_response = AckResponse(command_id, "",
                                   f"discard: Command caused invalid state. Can be due to following reasons:\n"
                                   f"1. array out of bounds.\n"
                                   f"2. Reassigning variable to new type.\n"
                                   f"3. Error occurred in the program. Did you write a proper command?\n")
        websocket_notifier.notify_observers(str(ack_response))
    send_command_interpreter_socket(command)




def recover_from_too_many_commands(command: str, command_id: int | None):
    if clear_is_pending():
        recurring_logger.debug(f"\t\t\tClear command already pending.")
        return
    recurring_logger.info(f"\t\t\tToo many commands detected. Will fix the state.")

    def callback() -> None:
        __recover_latest_code_state()
        result = send_command(command, get_interpreter_socket())  # Resend command since it was lost.
        if command_id is not None:
            ack_response = AckResponse(command_id, command, result)
            websocket_notifier.notify_observers(str(ack_response))

    queued_clear_interpreter(callback)


def handle_cleared_interpreter(robot_message: InterpreterCleared) -> None:
    non_recurring_logger.info(f"Interpreter cleared: {robot_message}")
    call_and_clear_callback(robot_message.cleared_id)


def recover_from_protective_stop(command: str, command_id: int | None):
    recurring_logger.warning(f"\t\t\tRobot is in protective stop. Attempting to unlock; Command id: {command_id}")
    if command_id is not None:
        # Todo: We need ssh to see the logs for optimal feedback
        ack_response = AckResponse(command_id, command,
                                   f"discard: Command caused protective stop. Please investigate the cause before continuuing. Unlocking in 5 seconds. \n")
        websocket_notifier.notify_observers(str(ack_response))

    unlock_protective_stop()
    _start_interpreter_mode_and_connect_to_backend_socket()
    __recover_latest_code_state()
    send_command_interpreter_socket(command)


def __recover_latest_code_state() -> None:
    send_command_interpreter_socket(get_latest_code_state().get_apply_commands())
    recurring_logger.debug(f"Recovering latest code state: {get_latest_code_state()}")
