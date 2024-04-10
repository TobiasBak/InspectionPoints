from enum import Enum, auto
from typing import Self

from custom_logging import LogConfig
from undo.StateValue import StateValue

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


class StateType(Enum):
    code_state = auto()
    rtde_state = auto()


class State:
    def __init__(self, state_type: StateType, state: list[StateValue] = None):
        self.state_type = state_type
        self.state = state

    def __str__(self):
        return str(self.state) if len(self.state) > 0 else "Empty State"

    def __repr__(self):
        return self.__str__()

    def get_apply_commands(self) -> str:
        output = ""
        for state_value in self.state:
            output += state_value.get_apply_command()
        output += "\n"
        return output

    def has_un_collapsible_difference(self, other: Self) -> bool:
        if self.state is None:
            recurring_logger.warn("self.state is None")
            return False

        # Sort variables by name or reference to their StateVariable
        if len(self.state) != len(other.state):
            return True
        for self_state, other_state in zip(self.state, other.state):
            if self_state.variable_definition.is_collapsible:
                continue
            if self_state.value != other_state.value:
                return True
        return False

    def __eq__(self, other: Self) -> bool:
        match other:
            case State():
                other_state_list = other.state
                if len(self.state) != len(other_state_list):
                    return False
                for self_state, other_state in zip(self.state, other_state_list):
                    if self_state != other_state:
                        return False
                return True
            case _:
                return False
