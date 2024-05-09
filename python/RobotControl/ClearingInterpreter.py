from typing import Callable

from RobotControl.RobotControl import clear_interpreter_mode
from custom_logging import LogConfig

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)

_pending_clears = {
    "open": False,
    "pending_id": 0,
}

type CallbackSignature = Callable[[], None]
_clear_callbacks: dict[int, CallbackSignature] = {}


def clear_is_pending() -> bool:
    return _pending_clears["open"]


def open_new_pending_command(callback: CallbackSignature) -> int:
    """Registers a new pending id and registers the callback."""
    _pending_clears["open"] = True
    _pending_clears["pending_id"] += 1
    _clear_callbacks[_pending_clears["pending_id"]] = callback
    return _pending_clears["pending_id"]


def get_pending_id() -> int:
    return _pending_clears["pending_id"]


def call_and_clear_callback(message_id: int | None) -> None:
    """This will clear callbacks even if the ids do not match."""
    _pending_clears["open"] = False

    if _pending_clears["pending_id"] != message_id:
        non_recurring_logger.warning(
            f"Pending clear id: {_pending_clears['pending_id']} does not match cleared id: {message_id}")

    if message_id in _clear_callbacks:
        callback = _clear_callbacks[message_id]
        if callback is not None:
            callback()
    _clear_callbacks.clear()


def do_nothing():
    pass


def queued_clear_interpreter(callback: CallbackSignature = do_nothing):
    new_id = open_new_pending_command(callback)
    clear_interpreter_mode(new_id)
