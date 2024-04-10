from SocketMessages import UndoMessage, UndoResponseMessage, UndoStatus


def handle_undo_message(message: UndoMessage) -> str:
    response = UndoResponseMessage(message.data.id, UndoStatus.Success)
    print(f"Sending response: {response}")
    return str(response)