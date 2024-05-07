from enum import Enum, auto

from RobotControl.SendRobotCommandWithRecovery import send_command_with_recovery, send_command_finished
from SocketMessages import CommandMessage
from undo.History import History
from undo.HistorySupport import new_command
from undo.ReadVariableState import start_read_report_state

class not_good_response_codes(Enum):
    discard = auto()

def send_user_command(command: CommandMessage) -> str:
    start_read_report_state()
    command_id = command.data.id
    command_message = command.data.command
    add_command_to_history(command)

    response_from_command = send_command_with_recovery(command_message, command_id)

    # Fix since command_finished has the command that is discarded, but it is not discarded, when it is wrapped
    # in a socket_send_string(b=p(1)) without defining p
    response_parts = response_from_command.split(":")
    if response_parts[0] == not_good_response_codes.discard.name:
        send_command_finished(command_id, "")
        return response_from_command

    send_command_finished(command_id, command_message)

    if response_from_command is None:
        return ""

    return response_from_command[:-2]  # Removes \n from the end of the response


def add_command_to_history(command):
    new_command(command)
