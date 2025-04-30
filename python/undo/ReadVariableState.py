import asyncio
from typing import Callable

from RobotControl.RunningWithSSH import run_script_on_robot
from RobotControl.RobotSocketMessages import ReportState
from custom_logging import LogConfig
from undo.HistorySupport import _variable_registry

READ_FREQUENCY_HZ = 1
READ_PERIOD = 1 / READ_FREQUENCY_HZ

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)

_read_report_state = True


def stop_read_report_state():
    global _read_report_state
    recurring_logger.info("Stopping read report state")
    _read_report_state = False


def start_read_report_state():
    global _read_report_state
    recurring_logger.info("Starting read report state")
    _read_report_state = True


def get_closured_functions() -> tuple[Callable[[int], None], Callable[[], None]]:
    shared_state = {
        "read_in_progress": False
    }

    def set_read_in_progress(value: bool):
        shared_state["read_in_progress"] = value

    def get_read_in_progress() -> bool:
        return shared_state["read_in_progress"]

    def report_state_received():
        set_read_in_progress(False)

    def read_variable_state(id: int = 1):
        if not _read_report_state:
            recurring_logger.debug("Read report state is false, skipping read_variable_state")
            return

        if get_read_in_progress():
            recurring_logger.debug("Read in progress, skipping read_variable_state")
            return
        set_read_in_progress(True)
        read_commands = _variable_registry.generate_read_commands()
        report_state = ReportState(id, read_commands)
        read_script_for_robot = report_state.dump_string_post_urify()
        recurring_logger.debug(f"Read script for robot: {read_script_for_robot}")
        response = run_script_on_robot(read_script_for_robot)
        # response = send_command_with_recovery(report_state.dump_string_post_urify(), None)
        recurring_logger.debug(f"Read variable state response: {response}")

    return read_variable_state, report_state_received


read_variable_state, report_state_received = get_closured_functions()


async def start_read_loop():
    while True:
        read_variable_state(1)
        await asyncio.sleep(READ_PERIOD)
