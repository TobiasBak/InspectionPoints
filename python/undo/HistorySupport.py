import re

from rtde.serialize import DataObject

from RobotControl.RobotSocketMessages import ReportState, CommandFinished

from SocketMessages import RobotState
from custom_logging import LogConfig
from undo.CommandStates import CommandStates
from undo.History import History, CommandStateHistory
from undo.State import State, StateType
from undo.StateValue import StateValue
from undo.StateVariable import CodeStateVariable
from undo.VariableAssignmentCommandBuilder import VariableAssignmentCommandBuilder, AssignmentStrategies
from undo.VariableRegistry import VariableRegistry, register_all_rtde_variables

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)

_variable_registry = VariableRegistry()


def get_variable_registry():
    return _variable_registry


def create_state_from_rtde_state(state: DataObject) -> State:
    state_values: list[StateValue] = []
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
                f"Variable {variable_definition.name} not found in received state,"
                f" with keys: {received_variables.keys()}")

        state_values.append(StateValue(variable_value, variable_definition))

    if len(state_values) != len(received_variables):
        # raise ValueError(f"Received state has {len(received_variables)} variables,"
        #                  f" but only {len(state_values)} were processed.")
        pass

    return State(StateType.rtde_state, state_values)


def register_all_variables():
    register_all_rtde_variables(_variable_registry)


def register_code_variable(variable: str):
    variable_assignment_builder = VariableAssignmentCommandBuilder(variable, AssignmentStrategies.VARIABLE_ASSIGNMENT)
    code_variable = CodeStateVariable(variable, variable, command_for_changing=variable_assignment_builder)
    _variable_registry.register_code_variable(code_variable)


register_all_variables()


def find_variable_definition_in_command(command: str) -> list[str]:
    # Regular expression pattern to match variable definitions excluding those within method parameters
    pattern = r'\b(\w+)\s*=\s*("[^"]*"|\S+)\b(?![^(]*\))(?![^:]*end)'
    # Use re.findall to find all matches in the string
    matches = re.findall(pattern, command)
    list_of_matches = []
    if matches:
        for match in matches:
            variable_name = match[0]
            list_of_matches.append(variable_name)
    return list_of_matches


def add_new_variable(variable: str):
    register_code_variable(variable)


def delete_latest_new_variables(variables: list[str]):
    copy_of_variable_list = _variable_registry.get_code_variables().copy()
    copy_of_variable_list = copy_of_variable_list[-len(variables):]

    for variable in variables:
        for code_variable in copy_of_variable_list:
            if code_variable.name == variable:
                _variable_registry.remove_code_variable(code_variable)


def create_state_from_report_state(report_state: ReportState) -> State:
    state_values: list[StateValue] = []

    code_variables = get_variable_registry().get_code_variables()
    code_variables_names = []

    for code_variable in code_variables:
        code_variable_name = code_variable.name
        code_variables_names.append(code_variable_name)

    received_variables = report_state.variables

    for variable in received_variables:
        variable_name = variable.name
        if variable_name not in code_variables_names:
            raise ValueError(f"Variable {variable_name} not found in code variables")
        code_variable = code_variables[code_variables_names.index(variable_name)]
        state_values.append(StateValue(variable.value, code_variable))

    if len(state_values) != len(received_variables):
        raise ValueError(f"Received state has {len(received_variables)} variables,"
                         f" but only {len(state_values)} were processed.")

    return State(StateType.code_state, state_values)


def handle_report_state(reported_state: ReportState):
    recurring_logger.debug(f"Handling report state: {reported_state}")
    state = create_state_from_report_state(reported_state)
    history = History.get_history()

    history.set_latest_code_state(state)

    history.append_state(state)


def handle_command_finished(command_finished: CommandFinished):
    recurring_logger.debug(f"Handling command finished: {command_finished}")
    history = History.get_history()
    history.close_command(command_finished)


def get_command_state_history() -> CommandStateHistory:
    return History.get_history().get_command_state_history()


def get_latest_active_command_state() -> CommandStates:
    return History.get_history().get_active_command_state()


def get_latest_code_state() -> State:
    return History.get_history().get_latest_code_state()
