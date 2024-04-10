import logging

ROBOT_FEEDBACK_PORT = 8000

recurring_level = logging.INFO
"""This level defines the level that will be logged in the console"""
non_recurring_level = logging.DEBUG
"""This level defines the level that will be logged in the console"""

_log_folder = "logs"

recurring_filename = _log_folder + "/" + "recurring.log"
"""This is the filename for the recurring log file"""
non_recurring_filename = _log_folder + "/" + "non_recurring.log"
"""This is the filename for the non-recurring log file"""
