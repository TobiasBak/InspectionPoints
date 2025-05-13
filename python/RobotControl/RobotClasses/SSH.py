import os
import paramiko

from constants import ROBOT_IP, SSH_USERNAME, SSH_PASSWORD, IS_PHYSICAL_ROBOT
from custom_logging import LogConfig
from RobotControl.RobotClasses.RobotController import RobotController

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)

class SSH:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SSH, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    def __init__(self):
        self.controller: RobotController = RobotController.get_instance()
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        non_recurring_logger.debug(f"SSH: Connecting to {ROBOT_IP} with username {SSH_USERNAME}")
        self.ssh_client.connect(ROBOT_IP, username=SSH_USERNAME, password=SSH_PASSWORD)

        self.path_to_programs_dir = "/programs"

        self.path_to_error_log = "../ursim/URControl.log"
        if IS_PHYSICAL_ROBOT:
            self.path_to_error_log = "/tmp/log/urcontrol/current"

    def close(self):
        """
        Closes the SSH connection.
        """
        self.ssh_client.close()

    def write_script(self, content: str, filename: str = "script_code.script"):
        """
        Writes a script to the robot's file system using SSH.
        """
        filepath = os.path.join(self.path_to_programs_dir, filename)

        try:
            sftp = self.ssh_client.open_sftp()
            recurring_logger.debug("Opened SFTP connection")
        except Exception as e:
            non_recurring_logger.error(f"Failed to open SFTP connection: {e}")
            return

        try:
            with sftp.file(filepath, 'w') as f:
                f.write(content)
                recurring_logger.debug(f"Script written to {filepath}")
        except Exception as e:
            non_recurring_logger.error(f"Failed to write script: {e}")
        finally:
            recurring_logger.debug("Closing SFTP connection")
            sftp.close()

    def write_file(self, filepath: str, endpath: str):
        """
        Writes a binary file (e.g., .URP) to the robot's file system using SSH.
        :param filepath: The local path to the file to be transferred.
        :param endpath: The destination path on the robot's file system.
        """
        try:
            # Open an SFTP connection
            sftp = self.ssh_client.open_sftp()
            recurring_logger.debug("Opened SFTP connection")
        except Exception as e:
            non_recurring_logger.error(f"Failed to open SFTP connection: {e}")
            return

        try:
            # Open the local file in binary read mode
            with open(filepath, 'rb') as local_file:
                # Open the remote file in binary write mode
                with sftp.file(endpath, 'wb') as remote_file:
                    # Read and write the file in chunks to handle large files
                    while chunk := local_file.read(4096):  # Read 4KB at a time
                        remote_file.write(chunk)
                    recurring_logger.debug(f"Binary file written to {endpath}")
        except Exception as e:
            non_recurring_logger.error(f"Failed to write binary file: {e}")
        finally:
            # Close the SFTP connection
            recurring_logger.debug("Closing SFTP connection")
            sftp.close()

    def read_lines_from_log(self, lines: int):
        """
        Reads the last `lines` number of lines from the robot's log file.
        """
        try:
            sftp = self.ssh_client.open_sftp()
            recurring_logger.debug("Opened SFTP connection")
        except Exception as e:
            non_recurring_logger.error(f"Failed to open SFTP connection: {e}")
            return ""

        try:
            with sftp.file(self.path_to_error_log, 'rb') as f:
                # Move to the end of the file
                f.seek(0, os.SEEK_END)
                position = f.tell()
                lines_read = 0
                line = b""

                # Read backwards until the desired number of lines is found
                while position >= 0 and lines_read < lines:
                    f.seek(position)
                    char = f.read(1)
                    if char == b'\n' and line:
                        lines_read += 1
                        if lines_read == lines:
                            break
                    line = char + line
                    position -= 1

                return line.decode("utf-8")
        except Exception as e:
            non_recurring_logger.error(f"Failed to read error log: {e}")
            return ""
        finally:
            recurring_logger.debug("Closing SFTP connection")
            sftp.close()

    def get_logs_from_last_program_run(self) -> list[str]:
        """
        Reads the logs up to the last "Starting program" line.
        This is used to get the logs from the last program run.
        """
        try:
            sftp = self.ssh_client.open_sftp()
            recurring_logger.debug("Opened SFTP connection")
        except Exception as e:
            non_recurring_logger.error(f"Failed to open SFTP connection: {e}")
            return []

        try:
            with sftp.file(self.path_to_error_log, 'rb') as f:
                # Move to the end of the file
                f.seek(0, os.SEEK_END)
                position = f.tell()
                line = b""
                logs = []
                
                # Read backwards until the "Starting program" line is found
                while position >= 0:
                    f.seek(position)
                    char = f.read(1)
                    if char == b'\n' and line:
                        line_decoded = line.decode("utf-8")
                        if "Starting program" in line_decoded:
                            break
                        logs.append(line_decoded)
                        line = b""
                    line = char + line
                    position -= 1
                
                return logs  
        except Exception as e:
            non_recurring_logger.error(f"Failed to read error log: {e}")
            return []
        finally:
            recurring_logger.debug("Closing SFTP connection")
            sftp.close()

