from typing import Callable


class WebsocketNotifier:
    def __init__(self):
        self._observers = []

    def register_observer(self, observer: Callable[[str], None]):
        self._observers.append(observer)

    def notify_observers(self, message: str):
        for observer in self._observers:
            observer(message)


websocket_notifier = WebsocketNotifier()


