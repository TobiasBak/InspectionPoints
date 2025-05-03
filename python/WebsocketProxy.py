import asyncio
import json
from asyncio import StreamReader, StreamWriter, Task
from socket import gethostbyname, gethostname
from time import sleep
from typing import Final

from websockets.server import serve

from RobotControl.Robot import Robot
from RobotControl.RobotSocketMessages import parse_robot_message, CommandFinished, ReportState, RobotSocketMessageTypes
from RobotControl.RunningWithSSH import run_script_on_robot
from SocketMessages import AckResponse
from SocketMessages import InspectionPointFormatFromFrontend, InspectionVariable
from SocketMessages import parse_message, CommandMessage, InspectionPointMessage
from WebsocketNotifier import websocket_notifier
from constants import ROBOT_FEEDBACK_PORT, FRONTEND_WEBSOCKET_PORT
from custom_logging import LogConfig
from undo.HistorySupport import create_variable_registry
from undo.HistorySupport import handle_report_state, handle_command_finished

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)

clients = dict()
_START_BYTE: Final = b'\x02'
_END_BYTE: Final = b'\x03'
_EMPTY_BYTE: Final = b''

_connected_web_clients = set()
_new_client = False

def handle_command_message(message: CommandMessage) -> str:
    command_string = message.data.command
    non_recurring_logger.debug(f"Command string: {command_string}")

    result = run_script_on_robot(command_string)
    non_recurring_logger.debug(f"Result of command: {result}")
    if result == "":
        return ""
    response = AckResponse(message.data.id, command_string, result)
    str_response = str(response)
    non_recurring_logger.debug(f"Sending response: {str_response}")
    return str_response


def generate_read_point(inspectionPoint: InspectionPointFormatFromFrontend, globalVariables: list[InspectionVariable])->str:
    registry = create_variable_registry([v.codeVariable for v in globalVariables])
    for v in inspectionPoint.additionalVariables:
        registry.register_code_variable(v.codeVariable, ensure_single_definition=True)
    read_commands = registry.generate_read_commands()
    report_state = ReportState(inspectionPoint.id, read_commands)
    return report_state.dump_string_post_urify()

def handle_inspection_point_message(message: InspectionPointMessage) -> str:
    for i in reversed(message.inspectionPoints):
        read_command = generate_read_point(i, message.globalVariables)
        if message.scriptText[i.lineNumber] != i.command:
            raise Exception(f"The insert is going wrong. linenumber-1: {message.scriptText[i.lineNumber-1]}, linenumber+1: {message.scriptText[i.lineNumber+1]}. Should be: {i.command}. Length of inspectionpints: {len(message.scriptText)}")
        message.scriptText.insert(i.lineNumber, read_command)

    final_script = "\n".join(message.scriptText)
    response = run_script_on_robot(final_script)

    return response

def handle_new_client():
    global _new_client
    _new_client = True


def has_new_client() -> bool:
    global _new_client
    if _new_client:
        non_recurring_logger.debug("New client connected")
        _new_client = False
        return True
    return False


def __get_handler() -> callable:
    async def echo(websocket):
        try:
            _connected_web_clients.add(websocket)
            handle_new_client()
            async for message in websocket:
                recurring_logger.debug(f"Received following command from frontend: {message}")

                message = parse_message(message)

                match message:
                    case CommandMessage():
                        str_response = handle_command_message(message)
                    case InspectionPointMessage():
                        str_response = handle_inspection_point_message(message)

                    case _:
                        raise ValueError(f"Unknown message type: {message}")

                if str_response != "":
                    send_to_all_web_clients(str_response)
        except Exception as e:
            recurring_logger.error(f"Error in websocket handler: {e}")
            raise e
    return echo


def send_to_all_web_clients(message: str):
    removed_clients = []

    for websocket in _connected_web_clients:
        if websocket.closed:
            removed_clients.append(websocket)
            continue
        recurring_logger.debug(f"Sending message to webclient: {message}")
        asyncio.create_task(websocket.send(message))
        recurring_logger.debug(f"Message sent to webclient: {message}")

    for websocket in removed_clients:
        _connected_web_clients.remove(websocket)


# To prevent circular dependencies
websocket_notifier.register_observer(send_to_all_web_clients)


async def open_robot_server():
    host = '0.0.0.0'
    srv = await asyncio.start_server(client_connected_cb, host=host, port=ROBOT_FEEDBACK_PORT)
    non_recurring_logger.info(f"ip_address of this container: {gethostbyname(gethostname())}")
    async with srv:
        non_recurring_logger.info('server listening for robot connections')
        await srv.serve_forever()


def client_connected_cb(client_reader: StreamReader, client_writer: StreamWriter):
    # Use peername as client ID
    non_recurring_logger.info("########### We got a customer<<<<<<<<<<<<<")
    client_id = client_writer.get_extra_info('peername')

    non_recurring_logger.info(f'Client connected: {client_id}')

    # Define the cleanup function here
    def client_cleanup(fu: Task[None]):
        non_recurring_logger.warning('Cleaning up client {}'.format(client_id))
        try:  # Retrieve the result and ignore whatever returned, since it's just cleaning
            fu.result()
        except Exception as e:
            non_recurring_logger.error(f"Client cleaned up, Exception: {e}")
            raise e
        # Remove the client from client records
        del clients[client_id]

    task = asyncio.ensure_future(client_task(client_reader, client_writer))
    non_recurring_logger.debug(f"Task created for client: {client_id}")
    task.add_done_callback(client_cleanup)
    # Add the client and the task to client records
    clients[client_id] = task


async def client_task(reader: StreamReader, writer: StreamWriter):
    client_addr = writer.get_extra_info('peername')
    non_recurring_logger.info(f'Start echoing back to {client_addr}')
    extra_data = []

    while True:
        data = await reader.read(4096)

        if data == _EMPTY_BYTE:
            non_recurring_logger.debug("Empty data received. Closing connection")
            return

        # When using _START_BYTE[0] we return the integer value of the byte in the ascii table, so here it returns 2
        if data[0] == _START_BYTE[0] and extra_data:
            # We have extra data that needs to be recovered and processed
            await recover_mangled_data(extra_data)

            # Clean extra data, since the extra data was mangled
            extra_data = []

            continue

        if extra_data:
            data = extra_data + data
            extra_data = []

        # Check if the data received starts with the start byte
        # When using _START_BYTE[0] we return the integer value of the byte in the ascii table, so here it returns 2
        if data[0] != _START_BYTE[0]:
            recurring_logger.error(f"Something is WRONG. Data not started with start byte: {data}")

        if _END_BYTE not in data:
            recurring_logger.debug(f"End byte not in data, extra_data is set to data: {data}")
            extra_data = data
        else:
            # Split the data into messages within the data
            list_of_data = data.split(_END_BYTE)

            # If the last element is not empty, then it's not the end of the message
            if list_of_data[len(list_of_data) - 1] != _EMPTY_BYTE:
                extra_data = list_of_data.pop()

            for message in list_of_data:
                # If message contains multiple start bytes, discard message
                if message.count(_START_BYTE) > 1:
                    recurring_logger.warning(f"Trying to recover messages because of multiple start bytes: {message}")
                    messages = message.split(_START_BYTE)
                    for sub_message in messages:
                        await recover_mangled_data(sub_message)

                if message:
                    message = message[1:]  # remove the start byte
                    message_from_robot_received(message)


async def recover_mangled_data(extra_data: bytes) -> None:
    recurring_logger.debug(f"Mangled data: {extra_data}")
    # We have extra data and the rest was lost
    mangled_data = extra_data.decode()

    if await search_for_report_state(mangled_data):
        return

    recurring_logger.error("Pattern not found in the message.")


async def search_for_report_state(mangled_data: str) -> bool:
    pattern = r'"type":\s*"([^"]+)"'
    # Use re.search to find the pattern in the string
    match = re.search(pattern, mangled_data)
    # If match is found, extract the values
    if match:
        message_type = match.group(1)
        data_value = int(match.group(2))
        match message_type:
            case RobotSocketMessageTypes.Report_state.name:
                recurring_logger.warning("Found a match for report state in mangled data")
                # WE SHOULD PROLLY DO SOMETHING IF WE FIND A MATCH, BEFORE WE STARTED A NEW READ REPORT STATE
                return True
    return False


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True


def message_from_robot_received(message: bytes):
    decoded_message = message.decode()
    recurring_logger.debug(f"Decoded message before parsing: {decoded_message}")

    if not is_json(decoded_message):
        recurring_logger.debug(f"Message is not json: {decoded_message}")
        return

    robot_message = parse_robot_message(decoded_message)
    match robot_message:
        case CommandFinished():
            handle_command_finished(robot_message)
            send_to_all_web_clients(str(robot_message))
        case ReportState():
            handle_report_state(robot_message)
            send_to_all_web_clients(str(robot_message))
        case _:
            raise ValueError(f"Unknown RobotSocketMessage message: {robot_message}")


async def start_webserver():
    robot = Robot.get_instance()

    while not robot.controller.is_polyscope_ready:
        recurring_logger.debug("Waiting for polyscope to be ready")
        sleep(0.1)

    try:
        non_recurring_logger.debug("Starting websocket server")
        async with serve(__get_handler(), "0.0.0.0", FRONTEND_WEBSOCKET_PORT):
            await asyncio.Future()  # run forever
    except Exception as e:
        recurring_logger.error(f"Error starting websocket server: {e}")


