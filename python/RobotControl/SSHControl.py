import os
import socket
from socket import socket as Socket
from time import sleep
from typing import Callable
import select
import paramiko

from constants import ROBOT_IP, DASHBOARD_PORT
from custom_logging import LogConfig

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


def create_get_socket_function() -> Callable[[str, int], Socket]:
    inner_socket_bank: dict[tuple[str, int], Socket] = dict()

    def inner_get_socket(ip: str, port: int) -> Socket | None:
        if (ip, port) in inner_socket_bank:
            return inner_socket_bank[(ip, port)]
        try:
            my_socket: Socket = Socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as err:
            return
        try:
            my_socket.connect((ip, port))
        except ConnectionRefusedError:
            my_socket.close()
            sleep(1)
            return get_socket(ip, port)

        my_socket.setblocking(False)
        inner_socket_bank[(ip, port)] = my_socket
        return my_socket

    return inner_get_socket

get_socket = create_get_socket_function()

def _get_dashboard_socket():
    return get_socket(ROBOT_IP, DASHBOARD_PORT)

def read_from_socket(socket: Socket) -> str:
    ready_to_read, ready_to_write, in_error = select.select([socket], [], [], 0.1)
    if ready_to_read:
        message = socket.recv(4096)

        try:
            return message.decode()
        except UnicodeDecodeError as e:
            # Intentionally not returning anything.
            # Returning nothing if a decode error occurs.
            print(f"Decode error: {e}")

    return "nothing"


def read_from_socket_till_end(socket: Socket) -> str:
    out = ""
    message = read_from_socket(socket)
    while message != "nothing":
        out += message
        message = read_from_socket(socket)
    return out

def sanitize_command(command: str) -> str:
    command = command.replace('\n', ' ')
    command += "\n"  # Add a trailing \n character
    return command

def send_command_dashboard_socket(command: str) -> str:
    dashboard_socket = _get_dashboard_socket()
    sanitized_command = sanitize_command(command)
    dashboard_socket.send(sanitized_command.encode())
    return read_from_socket(dashboard_socket)

def run_script_on_robot(script: str) -> str:
    """
    Run a script on the robot using SSH.
    
        Args:
            script (str): The script to run.
    
        Returns: 
            An error message or an empty string.
    """
    _write_script_with_ssh(script)
    _load_urp_program()
    _start_loaded_program()

    last_line = _read_latest_error_log()
    non_recurring_logger.debug(f"Last line of error log: {last_line}")
    if check_for_compile_error(last_line):
        return last_line.split("-")[-1].strip()
    return ""

def _load_urp_program(program_name: str = "program.urp"):
    assert(program_name.endswith(".urp"), "Program name must end with .urp")
    send_command_dashboard_socket(f"load {program_name}")
    non_recurring_logger.debug("Loaded program: " + program_name)

def _start_loaded_program():
    send_command_dashboard_socket("play")
    non_recurring_logger.debug("Started loaded program")

def _write_script_with_ssh(content: str, filename: str = "script_code.script"):
    filepath = os.path.join("../ursim/programs", filename)

    ssh = _get_ssh_connection()
    assert ssh is not None, "SSH connection failed"
    
    try:
        _write_to_file_with_ssh(content, filepath, ssh)
    except Exception as e:
        non_recurring_logger.error(f"Failed to write script to robot: {e}")
    finally:
        recurring_logger.debug("Closing SSH connection")
        ssh.close()

def _get_ssh_connection() -> paramiko.SSHClient | None:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ROBOT_IP, username='root', password='easybot')
        recurring_logger.debug("Connected to the robot via SSH")
        return ssh
    except Exception as e:
        non_recurring_logger.error(f"Failed to connect to the robot: {e}")
        return None

def _write_to_file_with_ssh(content: str, filepath: str, ssh: paramiko.SSHClient):
    try: 
        sftp = ssh.open_sftp()
        recurring_logger.debug("Opened SFTP connection")
    except Exception as e:
        non_recurring_logger.error(f"Failed to open SFTP connection: {e}")
    try:
        with sftp.file(filepath, 'w') as f:
            f.write(content)
            recurring_logger.debug(f"Wrote script to {filepath}")
    except Exception as e:
        non_recurring_logger.error(f"Failed to write script to robot: {e}")
    finally:
        recurring_logger.debug("Closing SFTP connection")
        sftp.close()


def check_for_compile_error(log: str) -> bool:
    last_line: str = log
    non_recurring_logger.debug(f"Last line of error log: {last_line}")
    if last_line == "":
        non_recurring_logger.error("Exception in error log reading")
        return False

    if "compile error" in last_line:
        recurring_logger.error("Compile error detected in the latest error log")
        return True
    return False


def _read_latest_error_log() -> str:
    ssh: paramiko.SSHClient | None = _get_ssh_connection()
    assert ssh is not None, "SSH connection failed"
    error_log_path = "../ursim/URControl.log"

    try:
        sftp = ssh.open_sftp()
        recurring_logger.debug("Opened SFTP connection")
    except Exception as e:
        non_recurring_logger.error(f"Failed to open SFTP connection: {e}")
        return ""
    try:
        with sftp.file(error_log_path, 'rb') as f:
            # Move to the end of the file
            f.seek(0, os.SEEK_END)
            position = f.tell()
            line = b""
            
            # Read backwards until a newline is found
            while position >= 0:
                f.seek(position)
                char = f.read(1)
                if char == b'\n' and line:
                    break
                line = char + line
                position -= 1
            
            return line.decode("utf-8")
    except Exception as e:
        non_recurring_logger.error(f"Failed to read error log: {e}")
        return ""
    