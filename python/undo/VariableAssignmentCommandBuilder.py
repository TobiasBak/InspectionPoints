from enum import Enum

from custom_logging import LogConfig

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


class AssignmentStrategies(Enum):
    FUNCTION_CALL = 1
    VARIABLE_ASSIGNMENT = 2
    VARIABLE_ASSIGNMENT_STRING = 3


class VariableAssignmentCommandBuilder:
    def __init__(self, command: str, strategy: AssignmentStrategies):
        self.command = command
        self.strategy = strategy

    def build(self, value: str = None) -> str:
        if self.strategy == AssignmentStrategies.FUNCTION_CALL:
            return self._build_function_call(value)
        elif self.strategy == AssignmentStrategies.VARIABLE_ASSIGNMENT:
            return self._build_variable_assignment(value)
        elif self.strategy == AssignmentStrategies.VARIABLE_ASSIGNMENT_STRING:
            return self._build_variable_assignment_string(value)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

    def _build_function_call(self, value: str) -> str:
        out = f"{self.command}({value}) "
        non_recurring_logger.debug(f"Building function call with value: {value}. This results in '{out}'")
        return out

    def _build_variable_assignment(self, value: str) -> str:
        out = f"{self.command} = {value} "
        non_recurring_logger.debug(f"Building variable assignment with value: {value}. This results in '{out}'")
        return out

    def _build_variable_assignment_string(self, value: str) -> str:
        out = f"{self.command} = \"{value}\" "
        non_recurring_logger.debug(f"Building variable assignment with value: {value}. This results in '{out}'")
        return out
