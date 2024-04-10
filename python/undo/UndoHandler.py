from SocketMessages import UndoMessage, UndoResponseMessage, UndoStatus
from undo.CommandStates import CommandStates
from undo.History import History


def handle_undo_message(message: UndoMessage) -> str:
    response = UndoResponseMessage(message.data.id, UndoStatus.Success)
    print(f"Sending response: {response}")
    return str(response)


def find_commands_to_undo(command_id: int) -> list[CommandStates]:
    commands_states_to_undo: list[CommandStates] = []
    command_history = History.get_history().command_state_history
    if command_id in command_history.keys():
        command_history_keys = command_history.keys()
        reversed_list_of_keys = reversed(list(command_history_keys))
        for key in reversed_list_of_keys:
            commands_states_to_undo.append(command_history.get(key))
            if key == command_id:
                break
    return commands_states_to_undo


def undo_commands(commands) -> None:
    for command in commands:
        command.get_undo_commands()


def handle_undo_request(command_id: int) -> None:
    commands = find_commands_to_undo(command_id)
    undo_commands(commands)



