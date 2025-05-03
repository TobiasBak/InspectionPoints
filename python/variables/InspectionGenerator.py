from RobotControl.RobotSocketMessages import VariableObject
from custom_logging import LogConfig
from variables.VariableDefinition import CodeVariableDefinition, RtdeVariableDefinition

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


class InspectionGenerator:
    """
    This class is used to generate the code that makes inspection points on the robot.

    It must be provided with the variables that should be inspected.

    More variables can be registered after instantiation, using the register_code_variable method.
    """
    def __init__(self, code_variables: list[CodeVariableDefinition] = None,):
        self.variables: set[CodeVariableDefinition] = set()
        if code_variables is not None:
            for variable in code_variables:
                self.variables.add(variable)

    def register_code_variable(self, variable: CodeVariableDefinition) -> None:
        self.variables.add(variable)

    def generate_read_commands(self) -> list[VariableObject]:
        output_list = []
        for variable in self.variables:
            if variable.is_code:
                output_list.append(variable.socket_representation)
            else:
                raise ValueError("Variable in code list is not a code variable")
        return output_list

    def __str__(self):
        return f"Variables: {self.variables}"

    def __repr__(self):
        return self.__str__()

