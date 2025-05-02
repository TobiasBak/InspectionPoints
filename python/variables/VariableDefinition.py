from abc import ABC

from RobotControl.RobotSocketMessages import VariableObject, VariableTypes
from custom_logging import LogConfig

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


class VariableDefinition(ABC):
    def __init__(self, name: str):
        self.name = name
        self.is_rtde = False
        self.is_code = False

    def __str__(self):
        return self.name


class RtdeVariableDefinition(VariableDefinition):
    def __init__(self, name: str, rtde_variable_name: str):
        super().__init__(name)
        self.is_rtde = True
        self.rtde_variable_name = rtde_variable_name


class CodeVariableDefinition(VariableDefinition):
    def __init__(self, name: str, command_for_reading: str):
        super().__init__(name)
        self.is_code = True
        self.command_for_reading = command_for_reading
        "This must be the urscript code that is necessary to return a value for this variable."
        self.socket_representation = VariableObject(name, VariableTypes.String, command_for_reading)

    def __str__(self):
        return f"Codevariable {self.name} with command for reading: {self.command_for_reading}"

    def __repr__(self):
        return self.__str__()
