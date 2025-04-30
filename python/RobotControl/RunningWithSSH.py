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
    robot.interpreter_mode.start()

    interpreter_script = "halt\n" + script
    result = robot.interpreter_mode.send_small_command_on_interpreter(interpreter_script)
    non_recurring_logger.debug(f"Result of sending script to interpreter: {result}")

    error_message = result.lower().split(":")[1]
    out = None

    if "error" in error_message:
        out = f"{result.split(":")[1].strip()}: {result.split(":")[2].strip()}"
    elif "exception" in error_message:
        out = result.split(":")[1].strip()

    if out:
        robot.controller.stop_program()
        return out

    robot.controller.stop_program()

    robot.ssh.write_script(script)
    robot.controller.load_program()
    robot.controller.start_program()
    return "" 