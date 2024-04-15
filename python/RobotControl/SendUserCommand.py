from RobotControl.RobotSocketMessages import CommandFinished, VariableObject
from RobotControl.RobotSocketVariableTypes import VariableTypes
from RobotControl.SendRobotCommandWithRecovery import send_command_with_recovery, send_command_finished
from SocketMessages import CommandMessage
from URIFY import URIFY_return_string
from undo.History import History
from undo.VariableReadLoop import start_read_report_state


def send_user_command(command: CommandMessage) -> str:
    start_read_report_state()
    command_id = command.data.id
    command_message = command.data.command
    test_history(command)

    response_from_command = send_command_with_recovery(command_message, command_id=command.data.id)

    send_command_finished(command_id, command_message)

    if response_from_command is None:
        return ""

    return response_from_command[:-2]  # Removes \n from the end of the response


def test_history(command):
    history = History.get_history()
    history.new_command(command)
    history.debug_print()
