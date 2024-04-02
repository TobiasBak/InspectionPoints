from SocketMessages import CommandMessage
from undo.State import State, StateType


class CommandStates:
    def __init__(self, command: CommandMessage):
        self.user_command = command
        self.states: list[State] = []
        self.is_closed = False
        self.previous_states: dict[StateType, tuple[int, State]] = {}

    def append_state(self, state: State):
        if state.state_type not in self.previous_states:
            print(f"state appended because it is the first state of its type: {state.state_type}.")
            self._append_state(state)
            return

        from_index, from_state = self.previous_states[state.state_type]

        if self.is_closed and from_state != state:
            raise ValueError("The states differ after the command has been closed.")

        if from_state.has_un_collapsible_difference(state):
            self._append_state(state)
        elif from_state != state:
            self.states.pop(from_index)
            self._append_state(state)

    def _append_state(self, state: State):
        self.states.append(state)
        self.previous_states[state.state_type] = (len(self.states) - 1, state)

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
