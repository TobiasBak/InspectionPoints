from time import sleep
import re

from custom_logging import LogConfig
from RobotControl.Robot import Robot

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
    sleep(0.1)

    latest_errors = robot.ssh.read_lines_from_log(2)

    if "Compile error" or "Lexer exception" in latest_errors:
        error = latest_errors.split("\n")[1]
        parts = re.split(r'ERROR\s+-', error, maxsplit=1)
        return parts[1]

    return "" 