import asyncio
from typing import Callable

from RobotControl.RobotControl import get_interpreter_socket
from RobotControl.SendRobotCommandWithRecovery import send_command_with_recovery
from RobotControl.RobotSocketMessages import ReportState
from custom_logging import LogConfig
from undo.HistorySupport import _variable_registry, READ_PERIOD

recurring_logger = LogConfig.get_recurring_logger(__name__)


def get_closured_functions() -> tuple[Callable[[], None], Callable[[], None]]:
    shared_state = {
        "read_in_progress": False
    }

    def set_read_in_progress(value: bool):
        shared_state["read_in_progress"] = value

    def get_read_in_progress() -> bool:
        return shared_state["read_in_progress"]

    def report_state_received():
        set_read_in_progress(False)

    def read_variable_state():
        if get_read_in_progress():
            recurring_logger.debug("Read in progress, skipping read_variable_state")
            return
        set_read_in_progress(True)
        interpreter_socket = get_interpreter_socket()
        read_commands = _variable_registry.generate_read_commands()
        report_state = ReportState(read_commands)
        response = send_command_with_recovery(report_state.dump_string_post_urify(), interpreter_socket)
        recurring_logger.debug(f"Read variable state response: {response}")

    return read_variable_state, report_state_received


read_variable_state, report_state_received = get_closured_functions()


async def start_read_loop():
    while True:
        read_variable_state()
        await asyncio.sleep(READ_PERIOD)
