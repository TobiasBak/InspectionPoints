import socket
from socket import gethostbyname, gethostname
from socket import socket as Socket
from time import sleep

from ToolBox import get_socket
from URIFY import SOCKET_NAME
from constants import ROBOT_IP, DASHBOARD_PORT, SECONDARY_PORT, ROBOT_FEEDBACK_PORT, ROBOT_FEEDBACK_HOST
from custom_logging import LogConfig

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)

class RobotController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RobotController, cls).__new__(cls)
            cls._instance.__initialize(*args, **kwargs)
        return cls._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    def __initialize(self, *args, **kwargs):      
        # Initialize sockets
        self.dashboard_socket: Socket = get_socket(ROBOT_IP, DASHBOARD_PORT)
        self.secondary_socket: Socket = get_socket(ROBOT_IP, SECONDARY_PORT)
        sleep(0.5)  # Wait for sockets to be ready
        
        # Wait for the robot to be reachable
        # TODO 

        # Initialize the robot
        self.power_on()
        self.brake_release()
        sleep(0.5) # Wait for the robot to be ready

    @property
    def robot_mode(self) -> str:
        """
        Property to get the robot mode.

            Returns:
                str: The robot mode. (Starting<program_name> or RUNNING)
        """
        return self.__get_value_from_dashboard("robotmode")

    @property
    def safety_status(self) -> str:
        """
        Property to get the safety status.
        """
        return self.__get_value_from_dashboard("safetystatus")

    @property
    def running(self) -> str:
        """
        Property to check if the robot is running.
        """
        return self.__get_value_from_dashboard("running")

    @property
    def program_state(self) -> str:
        """
        Property to get the program state.

            Returns:
                str: STOPPED<program_name> or PLAYING<program_name>
        """
        return self.__get_value_from_dashboard("programState")
    
    @property
    def open_feedback_socket_string(self, host: str = ROBOT_FEEDBACK_HOST, port: int = ROBOT_FEEDBACK_PORT) -> str:
        try:
            socket.inet_aton(host)
        except socket.error:
            host = gethostbyname(host)
        return f"socket_open(\"{host}\", {port}, {SOCKET_NAME})\n"  

    def send_command(self, socket: Socket, command: str) -> str:
        """
        Sends a command to the specified socket and returns the response.
        """
        sanitized_command = self._sanitize_command(command)
        socket.send(sanitized_command.encode())
        return self.read_from_socket(socket)

    def _sanitize_command(self, command: str) -> str:
        """
        Sanitizes a command by ensuring it ends with a newline character.
        """
        command = command.replace('\n', ' ')
        return command + "\n"

    def read_from_socket(self, socket: Socket) -> str:
        """
        Reads a response from the specified socket.
        """
        import select
        ready_to_read, _, _ = select.select([socket], [], [], 0.1)
        if ready_to_read:
            message = socket.recv(4096)
            try:
                return message.decode()
            except UnicodeDecodeError as e:
                non_recurring_logger.error(f"Error decoding message: {e}")
        return "nothing"
    
    def read_from_socket_till_end(self, socket: Socket) -> str:
        """
        Reads from the socket and returns last message.
        """
        out = ""
        message = self.read_from_socket(socket)
        while message != "nothing":
            out = message
            message = self.read_from_socket(socket)
        return out

    def power_on(self):
        return self.send_command(self.dashboard_socket, "power on")

    def power_off(self):
        return self.send_command(self.dashboard_socket, "power off")

    def brake_release(self):
        return self.send_command(self.dashboard_socket, "brake release")

    def restart_safety(self):
        return self.send_command(self.dashboard_socket, "restart safety")

    def stop_program(self):
        return self.send_command(self.dashboard_socket, "stop")
    
    def load_program(self, program_name: str = "program.urp"):
        assert program_name.endswith(".urp"), "Program name must end with .urp"
        return self.send_command(self.dashboard_socket, f"load {program_name}")
    
    def start_program(self):
        return self.send_command(self.dashboard_socket, "play")

    def unlock_protective_stop(self):
        sleep(5)  # Wait for 5 seconds before attempting to unlock
        result = self.__get_value_from_dashboard("unlock protective stop")
        if result == "Protectivestopreleasing":
            non_recurring_logger.warning("Protective stop releasing")
            return
        else:
            non_recurring_logger.info(f"Unlock protective stop result: {result}")
            self.unlock_protective_stop()  # Retry if release fails

    def __get_value_from_dashboard(self, command: str) -> str:
        response = self.send_command(self.dashboard_socket, command)
        return self.__sanitize_dashboard_reads(response)

    def __sanitize_dashboard_reads(self, response: str) -> str:
        message_parts = response.split(":")
        message = message_parts[-1]
        return message.replace('\\n', '').replace(' ', '').replace('\n', '')

    def close_popup(self):
        sleep(1)
        result = self.send_command(self.dashboard_socket, "close popup")
        non_recurring_logger.debug(f"Popup closed: {result}")

    def close_safety_popup(self):
        sleep(1)
        result = self.send_command(self.dashboard_socket, "close safety popup")
        non_recurring_logger.debug(f"Safety popup closed: {result}")

    def send_popup(self, message: str):
        command = f"popup {message}"
        result = self.send_command(self.dashboard_socket, command)
        non_recurring_logger.debug(f"Popup: {result}")
    

