import re
from time import sleep

from RobotControl.ClearingInterpreter import queued_clear_interpreter
from RobotControl.RobotControl import sanitize_command, clear_interpreter_mode
from RobotControl.SendRobotCommandWithRecovery import send_command_with_recovery
from SocketMessages import UndoMessage, UndoResponseMessage, UndoStatus
from custom_logging import LogConfig
from undo.CommandStates import CommandStates
from undo.History import History
from undo.HistorySupport import get_command_state_history, remove_command_state_from_history, \
    clean_variable_code_registry, get_variable_registry
from undo.ReadVariableState import stop_read_report_state, start_read_report_state

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


def handle_undo_message(message: UndoMessage) -> str:
    response = UndoResponseMessage(message.data.id, UndoStatus.Success)
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


def undo_command_states(command_states: list[CommandStates], command_id: int) -> None:
    history = History.get_history()
    for command_state in command_states:
        apply_undo_state(command_state, history.get_active_command_state())

    non_recurring_logger.debug(f"After sleep")
    apply_undo_state(command_states[-1], history.get_active_command_state(), last=True)

    send_command_with_recovery("", command_id, is_command_finished=True)  # Stop spinner on frontend


def apply_undo_state(command_state: CommandStates, active_command_state: CommandStates, last=False) -> None:
    non_recurring_logger.debug(f"Active command state: {active_command_state}")
    if last:
        new_string = command_state.get_first_rtde_state()
        new_string = sanitize_command(new_string)
        expression = r'(movej\([^)]*)(,\s*r\s*=\s*\d+\.\d+)'
        new_string = re.sub(expression, r'\1', new_string)
        result = send_command_with_recovery(new_string, None, is_undo_command=True)
    else:
        clean_variable_code_registry()
        queued_clear_interpreter()
        command_undo_strings = command_state.get_undo_commands()
        result = ""
        start = 0
        end = len(command_undo_strings)
        step = int(end / 10) + 1
        for i in range(start, end, step):
            for command_undo_string in command_undo_strings[i:i+step]:
                sanitized = sanitize_command(command_undo_string)
                result += send_command_with_recovery(sanitized, None, is_undo_command=True)

    if last:
        non_recurring_logger.debug(f"Result from last command: {result}")


def remove_undone_command_states(command_ids: list[int]) -> None:
    for key in command_ids:
        remove_command_state_from_history(key)
        recurring_logger.debug(f"Removed command state: {key}")
    recurring_logger.debug(f"Removed command states: {command_ids}")


def handle_undo_request(command_id: int) -> None:
    command_states_keys = get_reversed_list_of_command_keys(command_id)
    command_states = find_command_states_to_undo(command_states_keys)
    stop_read_report_state()
    queued_clear_interpreter()
    undo_command_states(command_states, command_id)
    remove_undone_command_states(command_states_keys)
    start_read_report_state()
