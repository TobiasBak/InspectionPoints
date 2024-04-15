import asyncio

from RobotControl.RobotControl import get_interpreter_socket
from RobotControl.RobotSocketMessages import ReportState
from RobotControl.SendRobotCommandWithRecovery import send_command_with_recovery
from undo.HistorySupport import _variable_registry, READ_PERIOD


def read_variable_state():
    # print("Reading variable state")
    interpreter_socket = get_interpreter_socket()
    read_commands = _variable_registry.generate_read_commands()
    report_state = ReportState(read_commands)
    send_command_with_recovery(report_state.dump_string_post_urify(), interpreter_socket)


async def start_read_loop():
    while True:
        read_variable_state()
        await asyncio.sleep(READ_PERIOD)