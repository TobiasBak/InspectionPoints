import json
from array import ArrayType
from builtins import list
from enum import Enum, auto

from custom_logging import LogConfig

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


class InspectionPointFormatFromFrontend:
    def __init__(self, id: int, lineNumber: int, command: str):
        self.id = id
        self.lineNumber = lineNumber
        self.command = command

    def get_id(self):
        return self.id

    def dump(self):
        return {
            "id": self.id,
            "lineNumber": self.lineNumber,
            "command": self.command
        }

    def __str__(self):
        return json.dumps(self.dump())

    def __repr__(self):
        return self.__str__()


# let newCommandExec2 = {
#     type: "Debug",
#     script: [
#         "movej()",
#         "for",
#         "ehkd",
#         "end"
#     ],
#     inspectionPoints: [
#         {
#             id: 1,
#             lineNumber: 1,
#             command: "movej()"
#         },
#         {
#             id: 2,
#             lineNumber: 3,
#             command: "ehkd",
#         }
#     ]
# }
class InspectionPointMessage:
    def __init__(self, script_text: list[str], inspection_points: list[dict]):
        self.type = MessageType.Debug
        self.scriptText: list[str] = script_text
        self.inspectionPoints: list[InspectionPointFormatFromFrontend] = []

        if not isinstance(script_text, list):
            raise ValueError(f"Script text is not a list: {script_text}")

        sorted_inspection_points = sorted(inspection_points, key=lambda i: i["lineNumber"])

        for point in sorted_inspection_points:
            self.inspectionPoints.append(
                InspectionPointFormatFromFrontend(point["id"], point["lineNumber"] - 1, point["command"])
            )



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


class JointState:
    def __init__(self, q_actual: list[float, float, float, float, float, float]):
        self.base = q_actual[0]
        self.shoulder = q_actual[1]
        self.elbow = q_actual[2]
        self.wrist1 = q_actual[3]
        self.wrist2 = q_actual[4]
        self.wrist3 = q_actual[5]

    def __getitem__(self, item) -> float:
        if item == 0:
            return self.base
        elif item == 1:
            return self.shoulder
        elif item == 2:
            return self.elbow
        elif item == 3:
            return self.wrist1
        elif item == 4:
            return self.wrist2
        elif item == 5:
            return self.wrist3
        else:
            raise ValueError(f"Unknown joint index: {item}")

    def dump(self):
        return [self.base, self.shoulder, self.elbow, self.wrist1, self.wrist2, self.wrist3]


class TCPPoseState:
    def __init__(self, pose: list[float, float, float, float, float, float]):
        self.x = pose[0]
        self.y = pose[1]
        self.z = pose[2]
        self.rx = pose[3]
        self.ry = pose[4]
        self.rz = pose[5]

    def __getitem__(self, item) -> float:
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        elif item == 2:
            return self.z
        elif item == 3:
            return self.rx
        elif item == 4:
            return self.ry
        elif item == 5:
            return self.rz
        else:
            raise ValueError(f"Unknown TCP index: {item}")

    def dump(self):
        return [self.x, self.y, self.z, self.rx, self.ry, self.rz]


class TCPSpeedState:
    def __init__(self, speed: list[float, float, float, float, float, float]):
        self.x = speed[0]
        self.y = speed[1]
        self.z = speed[2]
        self.rx = speed[3]
        self.ry = speed[4]
        self.rz = speed[5]

    def __getitem__(self, item) -> float:
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        elif item == 2:
            return self.z
        elif item == 3:
            return self.rx
        elif item == 4:
            return self.ry
        elif item == 5:
            return self.rz
        else:
            raise ValueError(f"Unknown TCP index: {item}")

    def dump(self):
        return [self.x, self.y, self.z, self.rx, self.ry, self.rz]


class TCPForceState:
    def __init__(self, force: list[float, float, float, float, float, float]):
        self.fx = force[0]
        self.fy = force[1]
        self.fz = force[2]
        self.tx = force[3]
        self.ty = force[4]
        self.tz = force[5]

    def __getitem__(self, item) -> float:
        if item == 0:
            return self.fx
        elif item == 1:
            return self.fy
        elif item == 2:
            return self.fz
        elif item == 3:
            return self.tx
        elif item == 4:
            return self.ty
        elif item == 5:
            return self.tz
        else:
            raise ValueError(f"Unknown TCP index: {item}")

    def dump(self):
        return [self.fx, self.fy, self.fz, self.tx, self.ty, self.tz]


class TCPState:
    def __init__(self, pose: TCPPoseState, speed: TCPSpeedState, force: TCPForceState):
        self.pose: TCPPoseState = pose
        self.speed: TCPSpeedState = speed
        self.force: TCPForceState = force

    def dump(self):
        return {
            "pose": self.pose.dump(),
            "speed": self.speed.dump(),
            "force": self.force.dump()
        }


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


class RobotStateData:
    def __init__(self, safety_status: SafetyStatusTypes, runtime_state: RuntimeStateTypes, robot_mode: RobotModeTypes,
                 joints: JointState, tcp: TCPState, payload: float, digital_out: list[bool]):
        self.safety_status: SafetyStatusTypes = safety_status
        self.runtime_state: RuntimeStateTypes = runtime_state
        self.robot_mode: RobotModeTypes = robot_mode
        self.joints: JointState = joints
        self.tcp: TCPState = tcp
        self.payload: float = payload
        self.digital_out = digital_out

    def dump(self):
        """Dumps the data to a dictionary that can be converted to JSON."""
        return {
            "safety_status": self.safety_status.name,
            "runtime_state": self.runtime_state.name,
            "robot_mode": self.robot_mode.name,
            "joints": self.joints.dump(),
            "tcp": self.tcp.dump(),
            "payload": self.payload,
            "digital_out_0": self.digital_out[0],
            "digital_out_1": self.digital_out[1],
            "digital_out_2": self.digital_out[2],
            "digital_out_3": self.digital_out[3],
            "digital_out_4": self.digital_out[4],
            "digital_out_5": self.digital_out[5],
            "digital_out_6": self.digital_out[6],
            "digital_out_7": self.digital_out[7]
        }

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
                'inspectionPoints': inspectionPoints
            }
        }:
            return InspectionPointMessage(scriptText, inspectionPoints)
        case _:
            raise ValueError(f"Unknown message structure: {parsed}")
