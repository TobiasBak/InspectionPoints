import logging
from decouple import config


ROBOT_FEEDBACK_PORT: int = config("ROBOT_FEEDBACK_PORT", default=8000)
ROBOT_FEEDBACK_HOST: str = config("ROBOT_FEEDBACK_HOST", default="proxy")
ROBOT_IP: str = config("ROBOT_IP", default="polyscope")

FRONTEND_WEBSOCKET_PORT: int = config("FRONTEND_WEBSOCKET_PORT", default=8767)

DASHBOARD_PORT = 29999
PRIMARY_PORT = 30001
SECONDARY_PORT = 30002
RTDE_PORT = 30004
INTERPRETER_PORT = 30020

SSH_USERNAME: str = config("SSH_USERNAME", default="robot")

RTDE_CONFIG_FILE: str = config("RTDE_CONFIG_FILE", default="rtde_configuration.xml")

recurring_level = logging.DEBUG
"""This level defines the level that will be logged in the console"""
non_recurring_level = logging.DEBUG
"""This level defines the level that will be logged in the console"""

_log_folder = "logs"

recurring_filename = _log_folder + "/" + "recurring.log"
"""This is the filename for the recurring log file"""
non_recurring_filename = _log_folder + "/" + "non_recurring.log"
"""This is the filename for the non-recurring log file"""
