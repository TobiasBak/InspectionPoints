import asyncio

from RobotControl.RobotSocketMessages import ReportState
from RobotControl.SendRobotCommandWithRecovery import send_command_with_recovery
from custom_logging import LogConfig
from undo.HistorySupport import get_variable_registry

READ_FREQUENCY_HZ = 1
READ_PERIOD = 1 / READ_FREQUENCY_HZ

recurring_logger = LogConfig.get_recurring_logger(__name__)


def read_variable_state():
    recurring_logger.info(f"Variable Registry dict: {get_variable_registry().get_code_variable_dict()}")
    read_commands = get_variable_registry().generate_read_commands()
    report_state = ReportState(read_commands)
    recurring_logger.info(f"Reading variable state: {report_state}")
    send_command_with_recovery(report_state.dump_string_post_urify())


_read_report_state = True


def stop_read_report_state():
    global _read_report_state
    recurring_logger.info("Stopping read report state")
    _read_report_state = False


def start_read_report_state():
    global _read_report_state
    recurring_logger.info("Starting read report state")
    _read_report_state = True


async def start_read_loop():
    try:
        while True:
            if _read_report_state:
                recurring_logger.info("Reading variable state")
                read_variable_state()
            await asyncio.sleep(READ_PERIOD)
    except Exception as e:
        recurring_logger.error(f"Error in start_read_loop: {e}")
        raise e
