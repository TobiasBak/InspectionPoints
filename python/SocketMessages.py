import json
from builtins import list
from enum import Enum, auto

from rtde.serialize import DataObject

from custom_logging import LogConfig
from variables.VariableDefinition import CodeVariableDefinition

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


class MessageType(Enum):
    Command = auto()
    Undo = auto()
    Ack_response = auto()
    Feedback = auto()
    Robot_state = auto()
    Debug = auto()


class Status(Enum):
    Ok = auto()
    Error = auto()

    @classmethod
    def parse(cls, message: str):
        if message.startswith("ack:"):
            return cls.Ok
        elif "error" in message or "exception" in message:
            return cls.Error
        else:
            raise ValueError(f"Unknown status message: '{message}'")



class CommandMessageData:
    def __init__(self, id: int, command: str):
        self.id = id
        self.command = command


class AckResponseData:
    def __init__(self, id: int, status: Status, command: str, message: str):
        self.id = id
        self.status = status
        self.command = command
        self.message = message


class CommandMessage:
    def __init__(self, id: int, command: str):
        self.type = MessageType.Command
        self.data: CommandMessageData = CommandMessageData(id, command)

    def get_id(self):
        return self.data.id

    def __str__(self):
        return json.dumps({
            "type": self.type.name,
            "data": {
                "id": self.data.id,
                "command": self.data.command
            }
        })

    def __repr__(self):
        return self.__str__()


class InspectionVariable:
    def __init__(self, name: str, readCommand: str):
        self.name = name
        self.readCommand = readCommand
        self.codeVariable: CodeVariableDefinition = CodeVariableDefinition(name, readCommand)

    def dump(self):
        return {
            "name": self.name,
            "readCommand": self.readCommand
        }

    def __str__(self):
        return json.dumps(self.dump())

    def __repr__(self):
        return self.__str__()


class InspectionPointFormatFromFrontend:
    def __init__(self, id: int, lineNumber: int, command: str, additionalVariables: list[InspectionVariable]):
        self.id = id
        self.lineNumber = lineNumber
        self.command = command
        self.additionalVariables: list[InspectionVariable] = additionalVariables

    def get_id(self):
        return self.id

    def dump(self):
        return {
            "id": self.id,
            "lineNumber": self.lineNumber,
            "command": self.command,
            "additionalVariablesToRead": [var.dump() for var in self.additionalVariables]
        }

    def __str__(self):
        return json.dumps(self.dump())

    def __repr__(self):
        return self.__str__()


class InspectionPointMessage:
    def __init__(self, script_text: list[str], inspection_points: list[dict], globalVariables: list[dict]):
        self.type = MessageType.Debug
        self.scriptText: list[str] = script_text
        self.inspectionPoints: list[InspectionPointFormatFromFrontend] = []
        self.globalVariables: list[InspectionVariable] = []

        if not isinstance(script_text, list):
            raise ValueError(f"Script text is not a list: {script_text}")

        sorted_inspection_points = sorted(inspection_points, key=lambda i: i["lineNumber"])

        # Transform the untyped dictionary to a list of InspectionPointFormatFromFrontend objects
        for point in sorted_inspection_points:
            self.inspectionPoints.append(
                InspectionPointFormatFromFrontend(
                    point["id"],
                    point["lineNumber"] - 1,
                    point["command"],
                    [InspectionVariable(var["name"], var["readCommand"]) for var in point["additionalVariablesToRead"]]
                )
            )
            
        # Transform the untyped dictionary to a list of InspectionVariable objects
        for globalVariable in globalVariables:
            parsed = InspectionVariable(globalVariable["name"], globalVariable["readCommand"])
            self.globalVariables.append(parsed)

        #     Check that the commands in the inspection points match the line numbers received.
        for point in self.inspectionPoints:
            line_number = point.lineNumber
            supposed_command = point.command
            if line_number > len(script_text):
                raise ValueError(f"Line number {line_number} is greater than the length of the script text.")
            if supposed_command != script_text[line_number]:
                raise ValueError(f"Command '{supposed_command}' does not match the script text ({script_text[line_number]}) at line {line_number}.")

    def __str__(self):
        return json.dumps({
            "type": self.type.name,
            "script": self.scriptText,
            "inspectionPoints": [point.dump() for point in self.inspectionPoints]
        })

    def __repr__(self):
        return self.__str__()


class AckResponse:
    def __init__(self, id: int, command: str, message: str, status: Status = None):
        self.type = MessageType.Ack_response
        if status is None:
            status = Status.parse(message)
        self.data: AckResponseData = AckResponseData(id, status, command, message)

    def __str__(self):
        return json.dumps({
            "type": self.type.name,
            "data": {
                "id": self.data.id,
                "status": self.data.status.name,
                "command": self.data.command,
                "message": self.data.message
            }
        })

class FeedbackData:
    def __init__(self, id: int, message: str):
        self.id = id
        self.message = message

class Feedback:
    def __init__(self, id: int, message: str):
        self.type = MessageType.Feedback
        self.data: FeedbackData = FeedbackData(id, message)


class SafetyStatusTypes(Enum):
    normal_mode = 1
    reduced_mode = 2
    protective_stop = 3
    recovery_mode = 4
    safeguard_stop = 5
    system_emergency_stop = 6
    robot_emergency_stop = 7
    violation = 8
    fault = 9
    validate_joint_id = 10
    undefined_safety_mode = 11
    automatic_mode_safeguard_stop = 12
    system_three_position_enabling_stop = 13


lookup_state_types: dict[int, SafetyStatusTypes] = {element.value: element for element in SafetyStatusTypes}


class RuntimeStateTypes(Enum):
    stopping = 0
    stopped = 1
    playing = 2
    pausing = 3
    paused = 4
    resuming = 5


lookup_runtime_state_types: dict[int, RuntimeStateTypes] = {element.value: element for element in RuntimeStateTypes}


class RobotModeTypes(Enum):
    no_controller = -1
    disconnected = 0
    confirm_safety = 1
    booting = 2
    power_off = 3
    power_on = 4
    idle = 5
    backdrive = 6
    running = 7
    updating_firmware = 8


lookup_robot_mode_types: dict[int, RobotModeTypes] = {element.value: element for element in RobotModeTypes}


class RtdeStateData:
    def __init__(self, safety_status: SafetyStatusTypes, runtime_state: RuntimeStateTypes, robot_mode: RobotModeTypes):
        self.safety_status: SafetyStatusTypes = safety_status
        self.runtime_state: RuntimeStateTypes = runtime_state
        self.robot_mode: RobotModeTypes = robot_mode

    def dump(self):
        """Dumps the data to a dictionary that can be converted to JSON."""
        return {
            "safety_status": self.safety_status.name,
            "runtime_state": self.runtime_state.name,
            "robot_mode": self.robot_mode.name
        }


class TransmittedInformationOptions(Enum):
    state = "safety_status"
    runtime_state = "runtime_state"
    robot_mode = "robot_mode"


class RtdeState:
    def __init__(self, state: DataObject):
        self.type = MessageType.Robot_state
        status: SafetyStatusTypes = ensure_type_of_status(
            state.__getattribute__(TransmittedInformationOptions.state.value))
        runtime_state: RuntimeStateTypes = ensure_type_of_runtime_status(
            state.__getattribute__(TransmittedInformationOptions.runtime_state.value))
        robot_mode: RobotModeTypes = ensure_type_of_robot_mode(
            state.__getattribute__(TransmittedInformationOptions.robot_mode.value))
        self.data: RtdeStateData = RtdeStateData(status, runtime_state, robot_mode)

    def __str__(self):
        return json.dumps({
            "type": self.type.name,
            "data": self.data.dump()
        })


def ensure_type_of_status(status: any) -> SafetyStatusTypes:
    if not isinstance(status, int):
        raise ValueError(f"Status is not of type int: {status}")
    if status not in lookup_state_types:
        raise ValueError(f"Status is not a known state: {status}")
    return lookup_state_types[status]


def ensure_type_of_runtime_status(runtime_status: any) -> RuntimeStateTypes:
    if not isinstance(runtime_status, int):
        raise ValueError(f"Runtime status is not of type int: {runtime_status}")
    if runtime_status not in lookup_runtime_state_types:
        raise ValueError(f"Runtime status is not a known state: {runtime_status}")
    return lookup_runtime_state_types[runtime_status]


def ensure_type_of_robot_mode(robot_mode: any) -> RobotModeTypes:
    if not isinstance(robot_mode, int):
        raise ValueError(f"Robot mode is not of type int: {robot_mode}")
    if robot_mode not in lookup_robot_mode_types:
        raise ValueError(f"Robot mode is not a known state: {robot_mode}")
    return lookup_robot_mode_types[robot_mode]


def parse_message(message: str) -> CommandMessage | InspectionPointMessage:
    parsed = json.loads(message)

    match parsed:
        case {
            'type': MessageType.Command.name,
            'data': {
                'id': id,
                'command': command
            }
        }:
            return CommandMessage(id, command)
        case {
            'type': MessageType.Debug.name,
            'data': {
                'script': scriptText,
                'inspectionPoints': inspectionPoints,
                'globalVariables': globalVariables
            }
        }:
            return InspectionPointMessage(scriptText, inspectionPoints, globalVariables)
        case _:
            raise ValueError(f"Unknown message structure: {parsed}")
