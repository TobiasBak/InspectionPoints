from time import sleep

from custom_logging import LogConfig
from RobotControl.RobotClasses.RobotController import RobotController
from RobotControl.RobotClasses.SSH import SSH
from RobotControl.RobotClasses.InterpreterMode import InterpreterMode
from constants import IS_PHYSICAL_ROBOT

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)

class Robot:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Robot, cls).__new__(cls)
            cls._instance.__initialize(*args, **kwargs)
        return cls._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance
    
    def __initialize(self):
        self.controller: RobotController = RobotController.get_instance()
        self.ssh: SSH = SSH.get_instance()
        self.interpreter_mode: InterpreterMode = InterpreterMode.get_instance()

        self.program_name= "eris_v3.urp"
        # Write program.urp to the robot
        self.ssh.write_file(f"RobotControl/{self.program_name}", f"/programs/{self.program_name}")

        self.controller.load_program(self.program_name)

        non_recurring_logger.info("Waiting for program to load")
        sleep(5)
        self.controller.power_on()
        non_recurring_logger.info("Waiting for robot to power on")
        sleep(5)
        self.controller.brake_release()
        non_recurring_logger.info("Waiting for brake release")
        sleep(2)
    