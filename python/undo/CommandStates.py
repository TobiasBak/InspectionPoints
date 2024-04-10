from SocketMessages import CommandMessage
from custom_logging import LogConfig
from undo.State import State, StateType

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


class CommandStates:
    def __init__(self, command: CommandMessage):
        self.user_command = command
        self.states: list[State] = []
        self.is_closed = False
        self.previous_states: dict[StateType, tuple[int, State]] = {}

    def append_state(self, state: State):
        if state.state_type not in self.previous_states:
            recurring_logger.debug(f"state appended because it is the first state of its type: {state.state_type}.")
            self._append_state(state)
            return

        from_index, from_state = self.previous_states[state.state_type]
        recurring_logger.debug(f"from_index: {from_index}, from_state: {from_state}")

        if self.is_closed:  # and from_state != state
            return
            # recurring_logger.error(f"Command is closed, but the states differ after the command has been closed."
            #                        f" from_state: {from_state}, state: {state}")
            # raise ValueError("The states differ after the command has been closed.")

        if from_state.has_un_collapsible_difference(state):
            self._append_state(state)
            recurring_logger.debug(f"Appending state because it has an un-collapsible difference.: {state}")
        elif from_state != state:
            self.states.pop(from_index)
            self._append_state(state)
            recurring_logger.debug(f"Collapsable state difference, replacing state at index {from_index} : {state}")
        else:
            recurring_logger.debug(
                f"State is the same as the previous state from_index: {from_index}, no further action: {state}")

    def _append_state(self, state: State):
        self.states.append(state)
        recurring_logger.debug(f"State appended: {state}")
        self.previous_states[state.state_type] = (len(self.states) - 1, state)
        recurring_logger.debug(f"Previous states: {self.previous_states}")

    def close(self):
        self.is_closed = True

    def get_undo_commands(self) -> str:
        output = ""
        for state in reversed(self.states):
            output += state.get_apply_commands()
        return output

    def __str__(self):
        if self.states is None:
            code_count = "States is None"
            rtde_count = code_count
        else:
            code_states = [state for state in self.states if state.state_type == StateType.code_state]
            rtde_states = [state for state in self.states if state.state_type == StateType.rtde_state]
            code_count = len(code_states)
            rtde_count = len(rtde_states)

        return (f"User Command: {self.user_command}, "
                f"number of rtde states: {rtde_count}, "
                f"number of code states: {code_count}")

    def __repr__(self):
        return self.__str__()
