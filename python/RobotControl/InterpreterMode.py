from socket import socket as Socket
from time import sleep

from RobotControl.RobotController import RobotController
from ToolBox import escape_string, get_socket
from constants import ROBOT_IP, INTERPRETER_PORT
from custom_logging import LogConfig

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)

class InterpreterMode:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(InterpreterMode, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    def __init__(self):
        self.controller: RobotController = RobotController.get_instance()
        self.interpreter_socket: Socket = get_socket(ROBOT_IP, INTERPRETER_PORT)

    def start(self):
        """
        Starts the interpreter mode.
        """
        command = f"interpreter_mode(clearQueueOnEnter = True, clearOnEnd = True)"
        response = self.controller.send_command(self.controller.secondary_socket, command)
        sleep(0.5) # Wait for the interpreter mode to be ready
        return response

    def stop(self):
        """
        Stops the interpreter mode.
        """
        return self.send_small_command_on_interpreter("end_interpreter()")

    def clear(self, clear_id: int = None):
        """
        Clears the interpreter mode.
        """
        return self.send_small_command_on_interpreter("clear_interpreter()")

    _extremely_randomized_command = f' FKSUYFCGSHILU213Y4387RGFBEI87 = "KFJSHEUIFYGEWIURG3" '
    
    def send_command(self, command: str) -> str:
        """Returns the ack_response from the robot. The ack_response is a string."""

        if "clear_interpreter()" in command:
            return self.send_small_command_on_interpreter(command)

        recurring_logger.debug(f"Modifying command: {escape_string(command)}")
        command += self._extremely_randomized_command  # To ensure that the command is read till the end.

        command = self.controller._sanitize_command(command)
        recurring_logger.debug(f"Sending command to robot: {escape_string(command)}")

        self.interpreter_socket.send(command.encode())
        result = self.controller.read_from_socket(self.interpreter_socket)

        while self._extremely_randomized_command not in result:
            result += self.controller.read_from_socket(self.interpreter_socket)

        result = result.replace(self._extremely_randomized_command, "")

        recurring_logger.debug(f"Result from robot: {escape_string(result)}")
        return escape_string(result)
    
    def send_small_command_on_interpreter(self, command: str) -> str:
        sanitized_command = self.controller._sanitize_command(command)
        self.interpreter_socket.send(sanitized_command.encode())
        return self.controller.read_from_socket_till_end(self.interpreter_socket)