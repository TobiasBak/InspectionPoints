from enum import Enum


class VariableTypes(Enum):
    """
    This is a list of variable types that can be sent to the robot
    Each type has a corresponding character that is used to identify the type
    """
    STRING = None
    String = "<"
    Integer = "|"
    Float = "@"
    Boolean = "£"
    List = "?"
    Pose = "!"
