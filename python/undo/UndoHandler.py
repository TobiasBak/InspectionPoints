from RobotControl.RobotControl import get_interpreter_socket, sanitize_command
from RobotControl.SendRobotCommandWithRecovery import send_command_with_recovery
from SocketMessages import UndoMessage, UndoResponseMessage, UndoStatus
from custom_logging import LogConfig
from undo.CommandStates import CommandStates
from undo.HistorySupport import stop_read_report_state, get_command_state_history, get_latest_state

recurring_logger = LogConfig.get_recurring_logger(__name__)


def handle_undo_message(message: UndoMessage) -> str:
    response = UndoResponseMessage(message.data.id, UndoStatus.Success)
    print(f"Sending response: {response}")
    return str(response)


def get_reversed_list_of_command_keys(command_id: int) -> list[int]:
    command_states_keys: list[int] = []
    if command_id not in get_command_state_history().keys():
        recurring_logger.debug(f"Command id: {command_id} not found in command history.")
        return command_states_keys

    list_of_keys_to_undo = []
    for key in get_command_state_history().keys():
        if key >= command_id:
            list_of_keys_to_undo.append(key)

    command_states_keys = list(reversed(sorted(list_of_keys_to_undo)))
    recurring_logger.debug(f"Found command states keys: {command_states_keys}")
    return command_states_keys


def find_command_states_to_undo(command_ids: list[int]) -> list[CommandStates]:
    commands_states_to_undo: list[CommandStates] = []
    for key in command_ids:
        commands_states_to_undo.append(get_command_state_history().get(key))
    recurring_logger.debug(f"Found command states to undo: {commands_states_to_undo}")
    return commands_states_to_undo


def undo_command_states(command_states: list[CommandStates]) -> None:
    for command_state in command_states:
        command_undo_string = command_state.get_undo_commands()
        new_string = sanitize_command(command_undo_string)
        recurring_logger.debug(f"Undoing command: {new_string}")
        send_command_with_recovery(command_undo_string, get_interpreter_socket())


def remove_undone_command_states(command_ids: list[int]) -> None:
    for key in command_ids:
        get_command_state_history().pop(key)
        recurring_logger.debug(f"Removed command state: {key}")
    recurring_logger.debug(f"Removed command states: {command_ids}")


def handle_undo_request(command_id: int) -> None:
    command_states_keys = get_reversed_list_of_command_keys(command_id)
    command_states = find_command_states_to_undo(command_states_keys)
    stop_read_report_state()
    undo_command_states(command_states)
    remove_undone_command_states(command_states_keys)
    send_command_with_recovery(get_latest_state().get_apply_commands(True), get_interpreter_socket())
