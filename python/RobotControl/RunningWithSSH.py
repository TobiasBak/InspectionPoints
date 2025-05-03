import asyncio
import re
import threading
from time import sleep
from typing import Callable

from RobotControl.Robot import Robot
from SocketMessages import AckResponse, Status
from WebsocketNotifier import websocket_notifier
from constants import IS_PHYSICAL_ROBOT
from custom_logging import LogConfig

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)

robot = Robot.get_instance()

def augment_script(script: str) -> str:

    socket_connection_text = robot.controller.open_feedback_socket_string
    out = socket_connection_text + script

    return out

def run_script_on_robot(script: str) -> str:
    """
    Run a script on the robot using SSH.
    
        Args:
            script (str): The script to run.
    
        Returns: 
            An error message or an empty string.
    """
    augmented_script = augment_script(script)
    robot.ssh.write_script(augmented_script)
    sleep(0.1)
    
    if not IS_PHYSICAL_ROBOT: 
        robot.controller.load_program()
    
    robot.controller.start_program()
    sleep(0.1)

    latest_errors = robot.ssh.read_lines_from_log(2)

    if "Compile error" in latest_errors or "Lexer exception" in latest_errors:
        non_recurring_logger.debug("Compile error or Lexer exception found")
        recurring_logger.debug(f"Error in script: {latest_errors}")
        error = latest_errors.split("\n")[1]
        parts = re.split(r'ERROR\s+-', error, maxsplit=1)
        return parts[1]

    #Start thread to check for runtime errors
    def run_async_checker():
        asyncio.run(run_script_finished_error_checker(0))

    error_checker_thread = threading.Thread(target=run_async_checker)
    error_checker_thread.start()

    return "" 

async def run_script_finished_error_checker(id: int):
    """
    Check for errors in the script after it has finished running.
    Sends the error to all web clients if an error is found.

        Args:
            script (str): The script to check.
    
        Returns: 
            None
    """
    recurring_logger.debug(f"Robot mode: {robot.controller.robot_mode}")
    __wait_for_condition(lambda: "Starting" not in robot.controller.robot_mode)
    
    recurring_logger.debug(f"Program state: {robot.controller.program_state}")
    __wait_for_condition(lambda: "PLAYING" not in robot.controller.program_state)
    
    latest_errors = robot.ssh.read_lines_from_log(3)
    recurring_logger.debug(f"Latest errors:\n{latest_errors}")
    if "Type error" in latest_errors or "Runtime error" in latest_errors:
        error_line = latest_errors.split("\n")[0]
        error_text = re.split(r'ERROR\s+-', error_line, maxsplit=1)[1]

        # Way to add line number to thed error message, but will not work with inspection points
        # error = retrieve_line_number_text(error_text)

        __send_error_message_to_web_clients(id, error_text)
        return
    
    if "New safety mode: SAFETY_MODE_PROTECTIVE_STOP" in latest_errors:
        error_text = """
        PROTECTIVE STOP: Reconsider how the robot is moving.
        You will not be able to run a program for five seconds.
        """
        __send_error_message_to_web_clients(id, error_text)

        # Close safety popup
        robot.controller.close_safety_popup()
        robot.controller.unlock_protective_stop()
        return

def add_line_number_text(text: str) -> str:
    """
    Modifies the text to include line number. 
    Uses 29 as the constant for the line difference.

        Args:
            text (str): The error message.
    
        Returns: 
            str: The modified error message with line number.
    """
    line_difference = 29
    match = re.search(r'\((\d+:\d+)\)', text)
    if match:
        line_number = match.group(1) 
        number = int(line_number.split(":")[0])
        text = text.replace(match.group(0), f"(line {number - line_difference})")
        return text
    return text

def __send_error_message_to_web_clients(id: int, message: str):
    """
    Sends an error message to all web clients.

        Args:
            message (str): The error message.
    
        Returns: 
            None
    """
    response = AckResponse(id, "Error", message, Status.Error)
    str_response = str(response)
    recurring_logger.debug(f"Sending error to web clients: {str_response}")
    websocket_notifier.notify_observers(str_response)

def __wait_for_condition(condition: Callable[[], bool]):
    max_wait_time = 60
    sleep_time = 0.1
    runs = 0
    
    while True:
        if condition() or runs >= max_wait_time / sleep_time:
            recurring_logger.debug(f"Condition met: {condition}")
            recurring_logger.debug(f"Run took {runs * sleep_time} seconds")
            break
        sleep(sleep_time)
        runs += 1
    