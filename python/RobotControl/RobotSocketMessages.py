import json
import math
import time
from enum import Enum, auto

from URIFY import URIFY_return_string

from RobotControl.RobotSocketVariableTypes import VariableTypes
from custom_logging import LogConfig

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


class RobotSocketMessageTypes(Enum):
    Command_finished = auto()
    Report_state = auto()

class VariableObject:
    def __init__(self, name: str, variable_type: VariableTypes,
                 value: str | int | float | bool | list | tuple[float, float, float, float, float, float],
                 global_variable: bool = False):
        self.name = name
        self.variable_type = variable_type
        self.value = value
        self.global_variable = global_variable

    def dump(self, ur_prep=False):
        value = self.value if not ur_prep else f'\"\"{self.variable_type.value}{self.name}\"\"'
        return {
            "name": self.name,
            "type": self.variable_type.name,
            "value": value,
            "global": self.global_variable
        }

    def dump_ur_string_for_report_state(self):
        value = f'\"\"{self.variable_type.value}{self.value}\"\"'
        return {
            "name": self.name,
            "type": self.variable_type.name,
            "value": value,
            "global": self.global_variable
        }

    def __str__(self):
        non_recurring_logger.debug(f"stringing: {self.dump()['value']}")
        return json.dumps(self.dump())

class ReportState:
    def __init__(self, id: int, variables: list[VariableObject], timestamp: int | None = None):
        self.id = id
        self.type = RobotSocketMessageTypes.Report_state
        self.variables: list[VariableObject] = variables
        local_timestamp = math.floor(time.time_ns() / 1000)
        self.timestamp = local_timestamp if timestamp is None else timestamp

    def __str__(self):
        return json.dumps(self.dump(True, True))

    def dump(self, raw_values=False, with_timestamp=False):
        out = {
            "type": self.type.name,
            "data": [variable.dump() if raw_values else variable.dump_ur_string_for_report_state()
                     for variable in self.variables],
            "id": self.id,
        }
        if with_timestamp:
            out["timestamp"] = self.timestamp
        return out

    def dump_string_pre_urify(self):
        return json.dumps(self.dump())

    def dump_string_post_urify(self):
        return URIFY_return_string(self.dump_string_pre_urify())


def parse_list_to_variable_objects(variable_list: list[dict]) -> list[VariableObject]:
    out: list[VariableObject] = list()
    for variable in variable_list:
        match variable:
            case {
                'name': name,
                'type': variable_type,
                'value': value,
                'global': global_variable
            }:
                out.append(VariableObject(name, VariableTypes[variable_type], value, global_variable))
            case _:
                non_recurring_logger.error(f"Unknown VariableObject type: {variable}")
                # raise ValueError(f"Unknown VariableObject type: {variable}")
    return out


def parse_robot_message(message: str) -> ReportState:
    timestamp = math.floor(time.time_ns() / 1_000_000)
    parsed = json.loads(message)

    match parsed:
        case {
            'type': RobotSocketMessageTypes.Report_state.name,
            'data': variable_list,
            'id': parsed_id
        }:
            parsed_variable_list = parse_list_to_variable_objects(variable_list)
            return ReportState(parsed_id, parsed_variable_list, timestamp)
        case _:
            raise ValueError(f"Unknown RobotSocketMessage type: {parsed}")
