from typing import Callable

from custom_logging import LogConfig

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


class WebsocketNotifier:
    """
    This class can be used to notify all registered observers with a message.

    This is used to send messages to all the clients connected to the websocket server.

    It can also be used by other functions to be notified whenever a message is sent to the clients.
    """

    def __init__(self):
        self._observers = []

    def register_observer(self, observer: Callable[[str], None]):
        """ Register a function that listens for messages to the frontend client"""
        self._observers.append(observer)

    def notify_observers(self, message: str):
        """Use this function to send a message through the websocket.
        All registered functions will be called with the given message.
        The order is not guaranteed.
        """
        for observer in self._observers:
            observer(message)


websocket_notifier = WebsocketNotifier()
