from typing import Self

from RobotControl.RobotSocketMessages import CommandFinished
from SocketMessages import CommandMessage
from custom_logging import LogConfig
from undo.CommandStates import CommandStates
from undo.State import State

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)

type CommandStateHistory = dict[int, CommandStates]


class History(object):
    _instance: Self | None = None

    def __init__(self):
        self.command_state_history: CommandStateHistory = {}
        self.active_command_state: CommandStates | None = None
        self.latest_code_state: State | None = None
        self.latest_rtde_state: State | None = None

    def get_active_command_state(self) -> CommandStates:
        return self.active_command_state

    def get_command_state_history(self) -> CommandStateHistory:
        return self.command_state_history

    def get_latest_code_state(self) -> State:
        return self.latest_code_state

    def set_latest_code_state(self, state: State) -> None:
        self.latest_code_state = state

    def get_latest_rtde_state(self) -> State:
        return self.latest_rtde_state

    def set_latest_rtde_state(self, state: State) -> None:
        self.latest_rtde_state = state

    def append_state(self, state: State) -> None:
        if self.active_command_state is None:
            recurring_logger.debug("There is no active command state.")
            return
            # raise ValueError("There is no active command state.")
        self.active_command_state.append_state(state)
        recurring_logger.debug(f"we made it out from trying to append to the active command state.")

    def pop_command_state_from_history(self, command_id: int) -> CommandStates:
        return self.command_state_history.pop(command_id)

    def _max_command_id(self) -> int:
        return max(self.command_state_history.keys())

    def _next_command_id(self, from_index: int) -> int:
        """This requires that there is a command id greater than from_index.
        Otherwise, an error is raised.
        See _max_command_id() for the maximum command id."""
        iterator = sorted(self.command_state_history.keys())
        for i in iterator:
            if i > from_index:
                return i

        raise ValueError(f"Could not find a command id greater than {from_index}")

    def new_command(self, command: CommandMessage) -> None:
        self.command_state_history[command.get_id()] = CommandStates(command)
        self._add_pre_states(command.get_id())

        max_id = max(self.command_state_history.keys())
        if max_id != command.get_id():
            raise ValueError(f"The provided command does not have the highest id."
                             f"The highest id is {max_id} and the provided id is {command.get_id()}"
                             f"The command with that id is"
                             f" {self.command_state_history[max_id].user_command.data.command}")
        if self.active_command_state is None:
            self.active_command_state = self.command_state_history[command.get_id()]
            self.debug_print()
        elif self.active_command_state.is_closed:
            self._add_pre_states(command.get_id())

            self.active_command_state = self.command_state_history[command.get_id()]

        recurring_logger.debug(
            f"New command added to history: {command.get_id()} length: {len(self.command_state_history)}")

    def _add_pre_states(self, command_id: int) -> None:
        new_command_state = self.command_state_history[command_id]
        new_command_state.append_state(self.latest_code_state)
        new_command_state.append_state(self.latest_rtde_state)

    def close_command(self, command_finished: CommandFinished) -> None:
        if self.active_command_state is None:
            self.debug_print()
            raise ValueError("There is no active command state, but it was attempted to close a command anyway.")
        command_state = self.command_state_history[command_finished.data.id]
        command_state.close()
        if self._max_command_id() > command_finished.data.id:
            next_id = self._next_command_id(command_finished.data.id)
            self._add_pre_states(next_id)
            self.active_command_state = self.command_state_history[next_id]
        elif self._max_command_id() < command_finished.data.id:
            raise ValueError(f"Command id {command_finished.data.id} is greater than the maximum command id.")

    def debug_print(self) -> None:
        debug_string = f"History: length={len(self.command_state_history)}\n"
        debug_string += f"==Active command state: {self.active_command_state}\n"
        for key, value in self.command_state_history.items():
            debug_string += f"\tKey: {key}, Value: {value}\n"
        recurring_logger.info(debug_string)

    @classmethod
    def get_history(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
