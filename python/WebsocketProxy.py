import asyncio
import json
import re
from asyncio import StreamReader, StreamWriter, Task
from socket import gethostbyname, gethostname
from socket import socket as Socket
from time import sleep
from typing import Final

from websockets.server import serve

from RobotControl.RobotControl import get_interpreter_socket, get_robot_mode, start_robot
from RobotControl.RobotSocketMessages import parse_robot_message, CommandFinished, ReportState, RobotSocketMessageTypes
from RobotControl.SendUserCommand import send_user_command, send_command_finished
from SocketMessages import AckResponse
from SocketMessages import parse_message, CommandMessage, UndoMessage
from WebsocketNotifier import websocket_notifier
from constants import ROBOT_FEEDBACK_PORT
from custom_logging import LogConfig
from undo.HistorySupport import handle_report_state, start_read_loop, handle_command_finished
from undo.UndoHandler import handle_undo_message, handle_undo_request

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)

clients = dict()
_START_BYTE: Final = b'\x02'
_END_BYTE: Final = b'\x03'
_EMPTY_BYTE: Final = b''

_connected_web_clients = set()

_new_client = False


def handle_command_message(message: CommandMessage, socket: Socket) -> str:
    command_string = message.data.command
    result = send_user_command(message, socket)
    if result == "":
        return ""
    response = AckResponse(message.data.id, command_string, result)
    str_response = str(response)
    recurring_logger.debug(f"Sending response: {str_response}")
    return str_response


def handle_new_client():
    global _new_client
    _new_client = True


def has_new_client() -> bool:
    global _new_client
    if _new_client:
        _new_client = False
        return True
    return False


def get_handler(socket: Socket) -> callable:
    async def echo(websocket):
        try:
            _connected_web_clients.add(websocket)
            handle_new_client()
            async for message in websocket:
                # print(f"Received message: {message}")

                message = parse_message(message)

                match message:
                    case CommandMessage():
                        str_response = handle_command_message(message, socket)
                        # print(f"Message is a CommandMessage")
                    case UndoMessage():
                        str_response = handle_undo_message(message)
                        handle_undo_request(message.data.id)
                        recurring_logger.debug(f"Message is an UndoMessage")
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
        await asyncio.create_task(start_read_loop())
        await srv.serve_forever()


def client_connected_cb(client_reader: StreamReader, client_writer: StreamWriter):
    # Use peername as client ID
    non_recurring_logger.info("########### We got a customer<<<<<<<<<<<<<")
    client_id = client_writer.get_extra_info('peername')

    non_recurring_logger.info(f'Client connected: {client_id}')

    # Define the cleanup function here
    def client_cleanup(fu: Task[None]):
        non_recurring_logger.warn('Cleaning up client {}'.format(client_id))
        try:  # Retrieve the result and ignore whatever returned, since it's just cleaning
            fu.result()
        except Exception as e:
            raise e
        # Remove the client from client records
        del clients[client_id]

    task = asyncio.ensure_future(client_task(client_reader, client_writer))
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
            continue

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
                    recurring_logger.debug(f"Discarding message because of multiple start bytes: {message}")
                    continue

                if message:
                    message = message[1:]  # remove the start byte
                    message_from_robot_received(message)


async def recover_mangled_data(extra_data: bytes) -> None:
    recurring_logger.debug(f"Fucked data: {extra_data}")
    # We have extra data and the rest was lost
    fucked_data = extra_data.decode()
    # Regular expression pattern to extract "type", "id", and "data.command"
    pattern = r'"type":\s*"([^"]+)".*?"id":\s*(\d+).*?"command":\s*"([^"]+)'
    # Use re.search to find the pattern in the string
    match = re.search(pattern, fucked_data)
    # If match is found, extract the values
    if match:
        message_type = match.group(1)
        id_value = int(match.group(2))
        command = match.group(3)
        match message_type:
            case RobotSocketMessageTypes.Command_finished.name:
                send_command_finished(id_value, command, get_interpreter_socket())
                recurring_logger.debug(f"Sending new Command finished with: id: '{id_value}' Command: '{command}'")
    else:
        recurring_logger.debug("Pattern not found in the message.")


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
        case _:
            raise ValueError(f"Unknown RobotSocketMessage message: {robot_message}")


async def start_webserver():
    ensure_polyscope_is_ready()
    non_recurring_logger.info(f"Polyscope is ready. The robot mode is: {get_robot_mode()}")

    start_robot()

    interpreter_socket: Socket = get_interpreter_socket()
    recurring_logger.info("Starting websocket server")
    async with serve(get_handler(interpreter_socket), "0.0.0.0", 8767):
        await asyncio.Future()  # run forever


def ensure_polyscope_is_ready():
    initial_startup_messages = ('', 'BOOTING')
    starting_phases = ('NO_CONTROLLER', 'DISCONNECTED', 'UniversalRobotsDashboardServer')
    sleep_time = 0.1

    robot_mode = get_robot_mode()

    while get_robot_mode() in initial_startup_messages:
        recurring_logger.info(f"Polyscope is still starting: {robot_mode}")
        sleep(sleep_time)

    # UniversalRobotsDashboardServer is a not documented state, but it is a state that the robot can be in
    while get_robot_mode() in starting_phases:
        recurring_logger.info(f"Polyscope is in current state of starting: {robot_mode}")
        sleep(sleep_time)
