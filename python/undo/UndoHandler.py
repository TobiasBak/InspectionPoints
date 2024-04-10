from RobotControl.RobotControl import get_interpreter_socket, sanitize_command
from RobotControl.SendRobotCommandWithRecovery import send_command_with_recovery
from SocketMessages import UndoMessage, UndoResponseMessage, UndoStatus
from custom_logging import LogConfig
from undo.CommandStates import CommandStates
from undo.History import History

recurring_logger = LogConfig.get_recurring_logger(__name__)


def handle_undo_message(message: UndoMessage) -> str:
    response = UndoResponseMessage(message.data.id, UndoStatus.Success)
    print(f"Sending response: {response}")
    return str(response)


def find_command_states_to_undo(command_id: int) -> list[CommandStates]:
    commands_states_to_undo: list[CommandStates] = []
    command_history = History.get_history().command_state_history
    if command_id in command_history.keys():
        command_history_keys = command_history.keys()
        reversed_list_of_keys = reversed(list(command_history_keys))
        for key in reversed_list_of_keys:
            commands_states_to_undo.append(command_history.get(key))
            if key == command_id:
                break
    recurring_logger.debug(f"Found command states to undo: {commands_states_to_undo}")
    return commands_states_to_undo


def undo_command_states(command_states: list[CommandStates]) -> None:
    for command_state in command_states:
        command_undo_string = command_state.get_undo_commands()
        new_string = sanitize_command(command_undo_string)
        recurring_logger.debug(f"Undoing command: {new_string}")
        send_command_with_recovery(command_undo_string, get_interpreter_socket())


def handle_undo_request(command_id: int) -> None:
    command_states = find_command_states_to_undo(command_id)
    undo_command_states(command_states)
