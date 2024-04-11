from socket import socket as Socket

from RobotControl.RobotControl import list_of_variables
from RobotControl.RobotSocketMessages import CommandFinished
from RobotControl.SendRobotCommandWithRecovery import send_command_with_recovery
from SocketMessages import CommandMessage
from URIFY import URIFY_return_string
from undo.History import History
from undo.HistorySupport import start_read_report_state


def send_user_command(command: CommandMessage, on_socket: Socket) -> str:
    start_read_report_state()
    command_id = command.data.id
    command_message = command.data.command
    test_history(command)

    response_from_command = send_command_with_recovery(command_message, on_socket, command_id=command.data.id)

    send_command_finished(command_id, command_message, on_socket)

    if response_from_command is None:
        return ""

    return response_from_command[:-2]  # Removes \n from the end of the response


def send_command_finished(command_id: int, command_message: str, on_socket: Socket):
    finish_command = CommandFinished(command_id, command_message, tuple(list_of_variables))
    string_command = finish_command.dump_ur_string()
    wrapping = URIFY_return_string(string_command)
    send_command_with_recovery(wrapping, on_socket, command_id=command_id)


def test_history(command):
    history = History.get_history()
    history.new_command(command)
    history.debug_print()
