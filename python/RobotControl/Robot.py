from time import sleep

from custom_logging import LogConfig
from RobotControl.RobotController import RobotController
from RobotControl.SSH import SSH
from RobotControl.InterpreterMode import InterpreterMode

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
        program_name = "eris_v2.urp"
        # Write program.urp to the robot
        self.ssh.write_file("/app/urprograms/eris_v2.urp", f"/programs/{program_name}")
        # self.ssh.write_file("RobotControl/program.urp", "../ursim/programs/program.urp")

    
        self.controller.load_program(program_name)  # Sagde du ikke at load program ikke var nødvendigt på den fysiske robot?

        non_recurring_logger.info("Waiting for program to load")
        sleep(5)
        self.controller.power_on()
        non_recurring_logger.info("Waiting for robot to power on")
        sleep(5)
        self.controller.brake_release()
        non_recurring_logger.info("Waiting for brake release")
        sleep(2)
    