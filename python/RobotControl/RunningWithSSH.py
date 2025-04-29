from time import sleep
import re
import asyncio
import threading

from custom_logging import LogConfig
from RobotControl.Robot import Robot
from SocketMessages import AckResponse
from WebsocketNotifier import  websocket_notifier


recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)

robot = Robot.get_instance()

def run_script_on_robot(script: str) -> str:
    """
    Run a script on the robot using SSH.
    
        Args:
            script (str): The script to run.
    
        Returns: 
            An error message or an empty string.
    """
    robot.ssh.write_script(script)
    robot.controller.load_program()
    robot.controller.start_program()
    sleep(0.2)

    latest_errors = robot.ssh.read_lines_from_log(2)

    if "Compile error" in latest_errors or "Lexer exception" in latest_errors:
        non_recurring_logger.debug("Compile error or Lexer exception found")
        error = latest_errors.split("\n")[1]
        parts = re.split(r'ERROR\s+-', error, maxsplit=1)
        return parts[1]

    #Start thread to check for errors
    def run_async_checker():
        asyncio.run(run_script_finished_error_checker(script))

    error_checker_thread = threading.Thread(target=run_async_checker)
    error_checker_thread.start()

    return "" 

async def run_script_finished_error_checker(script: str):
    """
    Check for errors in the script after it has finished running.
    Sends the error to all web clients if an error is found.

        Args:
            script (str): The script to check.
    
        Returns: 
            None
    """
    max_wait_time = 60
    sleep_time = 0.1
    runs = 0

    while "Starting" in robot.controller.robot_mode:
        sleep(sleep_time)
        runs += 1

    while "PLAYING" in robot.controller.program_state and runs < max_wait_time / sleep_time:
        sleep(0.1)
        runs += 1
    
    non_recurring_logger.debug(f"Run took {runs * sleep_time} seconds")
    
    latest_errors = robot.ssh.read_lines_from_log(3)
    non_recurring_logger.debug(f"Latest errors:\n{latest_errors}")
    if "Type error" in latest_errors or "Runtime error" in latest_errors:
        error = latest_errors.split("\n")[0]
        parts = re.split(r'ERROR\s+-', error, maxsplit=1)

        # Subtract 29 from the line number
        # TODO

        response = AckResponse(0, script, parts[1]) # id 0, cause I dunno
        str_response = str(response)
        non_recurring_logger.debug(f"Sending error to web clients: {str_response}")
        websocket_notifier.notify_observers(str_response)


    