from RobotControl.RobotSocketMessages import VariableObject
from custom_logging import LogConfig
from undo.VariableDefinition import CodeVariableDefinition, RtdeVariableDefinition
from undo.VariableAssignmentCommandBuilder import VariableAssignmentCommandBuilder, AssignmentStrategies

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


class VariableRegistry:
    def __init__(self):
        self._code_variables: list[CodeVariableDefinition] = []
        self._code_variable_dict: dict[str, CodeVariableDefinition] = {}
        self._rtde_variables: list[RtdeVariableDefinition] = []

    def register_code_variable(self, variable: CodeVariableDefinition) -> None:
        recurring_logger.debug(f"Registering variable: {variable.name}")
        self._code_variables.append(variable)
        self._code_variable_dict[variable.name] = variable
        recurring_logger.debug(f"Code variables: {self._code_variables}")

    def remove_code_variable(self, variable: CodeVariableDefinition) -> None:
        self._code_variables.remove(variable)
        self._code_variable_dict.pop(variable.name)
        recurring_logger.debug(f"Removed variable: {variable.name}")
        recurring_logger.debug(f"Code variables: {self._code_variables}")
        recurring_logger.debug(f"Code variable dict: {self._code_variable_dict}")
        # We are checking if the variable still exists because it is possible to redefine variables
        # Scenario of commands: {c=2 c=3 c="f"}. We then want to remove c="f" and keep c=3
        for var in reversed(self._code_variables):
            if var.name == variable.name:
                self._code_variable_dict[variable.name] = var
                break
        recurring_logger.info(f"Code variable dict after reassignment: {self._code_variable_dict}")

    def clean_variable_code_registry(self) -> None:
        self._code_variables = []
        self._code_variable_dict = {}
        recurring_logger.debug(f"Cleaned code variables: {self._code_variables}")
        recurring_logger.debug(f"Cleaned code variable dict: {self._code_variable_dict}")

    def register_rtde_variable(self, variable: RtdeVariableDefinition) -> None:
        self._rtde_variables.append(variable)
        # and some handling of how to enable rtde listening for this variable

    def generate_read_commands(self) -> list[VariableObject]:
        output_list = []
        for variable in self._code_variable_dict.values():
            if variable.is_code:
                output_list.append(variable.socket_representation)
            else:
                raise ValueError("Variable in code list is not a code variable")
        return output_list

    def get_code_variables(self) -> list[CodeVariableDefinition]:
        return self._code_variables

    def get_code_variable_dict(self) -> dict[str, CodeVariableDefinition]:
        return self._code_variable_dict

    def get_rtde_variables(self) -> list[RtdeVariableDefinition]:
        return self._rtde_variables

    def __str__(self):
        return f"Code variables: {self._code_variables}, RTDE variables: {self._rtde_variables}"

    def __repr__(self):
        return self.__str__()


def register_all_rtde_variables(in_registry: VariableRegistry):

    variables = [
        # RtdeStateVariable("safety status", "safety_status"),
        # RtdeStateVariable("runtime state", "runtime_state"),
        # RtdeStateVariable("robot mode", "robot_mode"),
        RtdeVariableDefinition("joints", "joints", False,
                               VariableAssignmentCommandBuilder("movej(%,r=0.005)",
                                                                AssignmentStrategies.FUNCTION_CALL)),
        # RtdeStateVariable("tcp", "tcp"),
        RtdeVariableDefinition("payload", "payload", False,
                               VariableAssignmentCommandBuilder("set_payload", AssignmentStrategies.FUNCTION_CALL)),
        RtdeVariableDefinition("digital_out_0", "digital_out_0", False,
                               VariableAssignmentCommandBuilder("set_digital_out(0, %)",
                                                                AssignmentStrategies.FUNCTION_CALL)),
        RtdeVariableDefinition("digital_out_1", "digital_out_1", False,
                               VariableAssignmentCommandBuilder("set_digital_out(1, %)",
                                                                AssignmentStrategies.FUNCTION_CALL)),
        RtdeVariableDefinition("digital_out_2", "digital_out_2", False,
                               VariableAssignmentCommandBuilder("set_digital_out(2, %)",
                                                                AssignmentStrategies.FUNCTION_CALL)),
        RtdeVariableDefinition("digital_out_3", "digital_out_3", False,
                               VariableAssignmentCommandBuilder("set_digital_out(3, %)",
                                                                AssignmentStrategies.FUNCTION_CALL)),
        RtdeVariableDefinition("digital_out_4", "digital_out_4", False,
                               VariableAssignmentCommandBuilder("set_digital_out(4, %)",
                                                                AssignmentStrategies.FUNCTION_CALL)),
        RtdeVariableDefinition("digital_out_5", "digital_out_5", False,
                               VariableAssignmentCommandBuilder("set_digital_out(5, %)",
                                                                AssignmentStrategies.FUNCTION_CALL)),
        RtdeVariableDefinition("digital_out_6", "digital_out_6", False,
                               VariableAssignmentCommandBuilder("set_digital_out(6, %)",
                                                                AssignmentStrategies.FUNCTION_CALL)),
        RtdeVariableDefinition("digital_out_7", "digital_out_7", False,
                               VariableAssignmentCommandBuilder("set_digital_out(7, %)",
                                                                AssignmentStrategies.FUNCTION_CALL))
    ]
    for variable in variables:
        in_registry.register_rtde_variable(variable)
