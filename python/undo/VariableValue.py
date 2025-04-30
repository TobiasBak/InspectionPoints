from custom_logging import LogConfig
from undo.VariableDefinition import VariableDefinition

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


class VariableValue:
    def __init__(self, value, variable_definition: VariableDefinition):
        self.value = value
        self.variable_definition = variable_definition

    def __str__(self):
        return "{" + f"{self.variable_definition.name}: {self.value}" + "}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, VariableValue):
            return False
        return self.value == other.value and self.variable_definition == other.variable_definition
