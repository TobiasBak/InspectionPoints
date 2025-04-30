from RobotControl.RobotSocketVariableTypes import VariableTypes
from custom_logging import LogConfig

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)

SOCKET_NAME = '\"abcd\"'  # We use a specific name in the so the user can open his own socket without specifying name


def URIFY_return_string(string_to_urify: str) -> str:
    """
    This function takes a string and returns a string that can be sent to the robot and then sent back to the proxy.\n
    The function does this by replacing all the quotes with socket_send_byte(34).\n
    For values of variables sent, the function ensures that the variable's value is not quoted, so the robot returns the
    actual value of the variable.

    :param string_to_urify: The string to be URIFYed for sending to the robot

    :return: The URIFYed string that can be sent to the robot
    """

    out = f" socket_send_byte(2, {SOCKET_NAME})"  # Start byte

    list_of_strings = string_to_urify.split('\\"\\"')

    for i in range(0, len(list_of_strings)):
        if i % 2 == 0:
            sub_string: str = list_of_strings[i]
            if i < len(list_of_strings) - 1:
                sub_string = sub_string[:-1]
            if i > 0:
                sub_string = sub_string[1:]

            out += __urify_string(sub_string)
        else:
            out += __create_socket_send_string_variable(list_of_strings[i])

    out += f" socket_send_byte(3, {SOCKET_NAME}) "  # End byte
    return out


def __urify_string(string: str) -> str:
    urified_string = ""

    # Split the string by quotes
    between_quotes = string.split('"')
    if len(between_quotes) == 1:
        return __create_socket_send_string(string)

    first = between_quotes.pop(0)
    if first != "":
        urified_string += __create_socket_send_string(first)
    else:
        urified_string += __create_quote_send()

    for part in between_quotes:
        # We want to send strings if empty string
        # This is due to a="Hi" resulting in "a=\\"Hi\\"" before urify_string is called.
        if part == "":
            urified_string += __create_quote_send()
            continue

        urified_string += __create_quote_send()
        urified_string += __create_socket_send_string(part)

    return urified_string


def __create_socket_send_string_variable(string_to_send: str) -> str:
    if string_to_send == "":
        return ""

    wrap_in_quotes = False
    start_char = string_to_send[0]

    match start_char:
        case VariableTypes.String.value:
            string_to_send = string_to_send[1:]
            wrap_in_quotes = True
        case VariableTypes.Integer.value | VariableTypes.Float.value | VariableTypes.Boolean.value | VariableTypes.List.value | VariableTypes.Pose.value:
            string_to_send = string_to_send[1:]
        case _:
            pass

    out = f" socket_send_string({string_to_send}, {SOCKET_NAME}) "

    if wrap_in_quotes:
        out = __create_quote_send() + out + __create_quote_send()

    return out


def __create_socket_send_string(string_to_send: str) -> str:
    if string_to_send == "":
        return ""
    return f" socket_send_string(\"{string_to_send}\", {SOCKET_NAME}) "


def __create_quote_send() -> str:
    return f" socket_send_byte(34, {SOCKET_NAME}) "
