import re

from rtde.serialize import DataObject

from RobotControl.RobotSocketMessages import ReportState
from SocketMessages import RobotState, CommandMessage
from custom_logging import LogConfig
from undo.CommandStates import CommandStates
from undo.History import History, CommandStateHistory
from undo.State import State, StateType
from undo.VariableValue import VariableValue
from undo.VariableDefinition import CodeVariableDefinition
from undo.VariableRegistry import VariableRegistry, register_all_rtde_variables

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)

_variable_registry = VariableRegistry()


def get_variable_registry():
    return _variable_registry


def create_state_from_rtde_state(state: DataObject) -> State:
    state_values: list[VariableValue] = []
    robot_state = RobotState(state)

    rtde_variables = get_variable_registry().get_rtde_variables()

    received_variables = robot_state.data.dump()

    for variable_definition in rtde_variables:
        try:
            variable_value = received_variables[variable_definition.rtde_variable_name]
        except KeyError:
            raise ValueError(
                f"Variable {variable_definition.name} not found in received state,"
                f" with keys: {received_variables.keys()}")
        if variable_value is None:
            raise ValueError(
                f"Variable {variable_definition.name} is none in received state,"
                f" with keys: {received_variables.keys()}")

        state_values.append(VariableValue(variable_value, variable_definition))

    if len(state_values) != len(received_variables):
        recurring_logger.debug(f"Received state has {len(received_variables)} variables,"
                                   f" but only {len(state_values)} were processed.")
        pass

    return State(StateType.rtde_state, state_values)


def register_all_variables():
    register_all_rtde_variables(_variable_registry)


register_all_variables()


def find_variables_in_command(command: str) -> list[tuple[str, str]]:
    # Regular expression pattern to match variable definitions excluding those within method parameters
    pattern = r'\b(\w+)\s*=\s*("[^"]*"|\S+)\b(?![^(]*\))(?![^:]*end)'
    # Use re.findall to find all matches in the string
    matches = re.findall(pattern, command)
    list_of_matches = []
    if matches:
        for match in matches:
            non_recurring_logger.debug(f"Match: {match}")
            variable = match
            list_of_matches.append(variable)
    return list_of_matches


def register_code_variable(variable: str):
    code_variable = CodeVariableDefinition(variable, variable)
    _variable_registry.register_code_variable(code_variable)


def add_new_variable(variable: tuple[str, str]):
    variable_name = variable[0]
    register_code_variable(variable_name)


def delete_variables_from_variable_registry(variables: list[tuple[str, str]]):
    copy_of_variable_list = _variable_registry.get_code_variables().copy()
    copy_of_variable_list = copy_of_variable_list[-len(variables):]

    for variable in variables:
        for code_variable in copy_of_variable_list:
            if code_variable.name == variable[0]:
                _variable_registry.remove_code_variable(code_variable)


def create_state_from_report_state(report_state: ReportState) -> State:
    state_values: list[VariableValue] = []
    code_variable_dict = get_variable_registry().get_code_variable_dict()
    received_variables = report_state.variables

    for variable in received_variables:
        variable_name = variable.name
        if variable_name not in code_variable_dict:
            recurring_logger.debug(f"Variable {variable_name} not found in code variable dict.")
            continue
        code_variable = code_variable_dict[variable_name]
        state_values.append(VariableValue(variable.value, code_variable))

    if len(state_values) != len(received_variables):
        recurring_logger.debug(f"Received state has {len(received_variables)} variables,"
                                    f" but only {len(state_values)} were processed.")

    return State(StateType.code_state, state_values)


def handle_report_state(reported_state: ReportState):
    recurring_logger.debug(f"Handling report state: {reported_state}")
    state = create_state_from_report_state(reported_state)
    history = History.get_history()
    history.append_state(state)

def history_debug_print():
    history = History.get_history()
    history.debug_print()

def clean_variable_code_registry():
    _variable_registry.clean_variable_code_registry()

def new_command(command: CommandMessage):
    history = History.get_history()

    if history.active_command_state is None:
        recurring_logger.debug("No active command state, creating new command state.")
        history.new_command(command)
        return

    max_id = max(history.command_state_history.keys())

    if max_id >= command.get_id():
        non_recurring_logger.info(f"Resetting command history due to command id mismatch.")
        history.command_state_history = {}
        history.active_command_state = None
        clean_variable_code_registry()
        # clear_interpreter_mode()

    history.new_command(command)


def get_command_state_history() -> CommandStateHistory:
    return History.get_history().get_command_state_history()


def remove_command_state_from_history(command_id: int) -> CommandStates:
    return History.get_history().pop_command_state_from_history(command_id)


def get_latest_active_command_state() -> CommandStates:
    return History.get_history().get_active_command_state()


def get_latest_code_state() -> State:
    return History.get_history().get_latest_code_state()
