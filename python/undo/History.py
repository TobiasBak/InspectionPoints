from typing import Self

from RobotControl.RobotSocketMessages import ReportState
from SocketMessages import CommandMessage
from custom_logging import LogConfig
from undo.CommandStates import CommandStates
from undo.State import State, StateType

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

    def get_latest_rtde_state(self) -> State:
        return self.latest_rtde_state

    def append_state(self, state: State) -> None:
        if state.state_type == StateType.code_state:
            self.latest_code_state = state
        elif state.state_type == StateType.rtde_state:
            self.latest_rtde_state = state

        if self.active_command_state is None:
            recurring_logger.debug("There is no active command state.")
            return
        self.active_command_state.append_state(state)
        recurring_logger.debug(f"we made it out from trying to append to the active command state.")

    def pop_command_state_from_history(self, command_id: int) -> CommandStates:
        # if the active command state is the command_id we are looking for,
        # we need to change the active command state to the previous command state
        if self.active_command_state.get_user_command().get_id() == command_id:
            if len(self.command_state_history) == 1:
                self.active_command_state = None
            else:
                self.active_command_state = self.command_state_history[self._previous_command_id(command_id)]
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

    def _previous_command_id(self, from_index: int) -> int:
        """This requires that there is a command id less than from_index.
        Otherwise, an error is raised."""
        iterator = sorted(self.command_state_history.keys())
        for i in reversed(iterator):
            if i < from_index:
                return i

        raise ValueError(f"Could not find a command id less than {from_index}")

    def new_command(self, command: CommandMessage) -> None:
        self.command_state_history[command.get_id()] = CommandStates(command)

        max_id = max(self.command_state_history.keys())
        if max_id != command.get_id():
            non_recurring_logger.info(f"Resetting command history due to command id mismatch.")
            self.command_state_history = {command.get_id(): CommandStates(command)}
            self.active_command_state = self.command_state_history[command.get_id()]
        if self.active_command_state is None:
            self.active_command_state = self.command_state_history[command.get_id()]
            self.debug_print()
        elif self.active_command_state.is_closed:
            self.active_command_state = self.command_state_history[command.get_id()]
            self._add_pre_states(command.get_id())

        recurring_logger.debug(
            f"New command added to history: {command.get_id()} length: {len(self.command_state_history)}")

    def _add_pre_states(self, command_id: int) -> None:
        if self.active_command_state.get_user_command().get_id() != command_id:
            recurring_logger.error(f"Active command id {self.active_command_state.get_user_command().get_id()} "
                                   f"does not match the provided command id {command_id}")
            raise ValueError(f"Active command id {self.active_command_state.get_user_command().get_id()} "
                             f"does not match the provided command id {command_id}")
        self.append_state(self.latest_code_state)
        self.append_state(self.latest_rtde_state)

    def close_command(self, command_finished) -> None:
        if self.active_command_state is None:
            self.debug_print()
            non_recurring_logger.info(f"There is no active command state. But close was called anyway"
                                      f"Was most likely due to a command_finished send to stop spinner on command undone")

        if command_finished.data.id not in self.command_state_history.keys():
            non_recurring_logger.info(f"Command id {command_finished.data.id} not found in command history."
                                      f"Was due to a command_finished send to stop spinner on command undone")
            return

        command_state = self.command_state_history[command_finished.data.id]
        command_state.close()
        if self._max_command_id() > command_finished.data.id:
            next_id = self._next_command_id(command_finished.data.id)
            self.active_command_state = self.command_state_history[next_id]
            self._add_pre_states(next_id)
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
