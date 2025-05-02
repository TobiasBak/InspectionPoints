from enum import Enum, auto
from typing import Self

from custom_logging import LogConfig
from undo.VariableValue import VariableValue

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


class StateType(Enum):
    code_state = auto()
    rtde_state = auto()


class State:
    def __init__(self, state_type: StateType, variable_values: list[VariableValue] = None):
        self.state_type = state_type
        self.variable_values = variable_values

    def has_un_collapsible_difference(self, other: Self) -> bool:
        if self.variable_values is None:
            recurring_logger.warning("self.state is None")
            return False

        # Sort variables by name or reference to their StateVariable
        if len(self.variable_values) != len(other.variable_values):
            return True
        for self_state, other_state in zip(self.variable_values, other.variable_values):
            if self_state.variable_definition.is_collapsible:
                continue
            if self_state.value != other_state.value:
                return True
        return False

    def __eq__(self, other: Self) -> bool:
        match other:
            case State():
                other_state_list = other.variable_values
                if len(self.variable_values) != len(other_state_list):
                    return False
                for self_state, other_state in zip(self.variable_values, other_state_list):
                    if self_state != other_state:
                        return False
                return True
            case _:
                return False

    def __str__(self):
        return str(self.variable_values) if len(self.variable_values) > 0 else "Empty State"

    def __repr__(self):
        return self.__str__()
