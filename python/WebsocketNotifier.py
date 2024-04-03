from typing import Callable


class WebsocketNotifier:
    """
    This class can be used to notify all registered observers with a message.

    This is used to send messages to all the clients connected to the websocket server.
    """
    def __init__(self):
        self._observers = []

    def register_observer(self, observer: Callable[[str], None]):
        """ Register a function to be called when notify_observers is called"""
        self._observers.append(observer)

    def notify_observers(self, message: str):
        """ Call all registered functions with the given message."""
        for observer in self._observers:
            observer(message)


websocket_notifier = WebsocketNotifier()


