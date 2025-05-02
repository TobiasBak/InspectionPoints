import asyncio

from WebsocketProxy import open_robot_server, start_webserver
from custom_logging import LogConfig

non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


async def main():
    non_recurring_logger.warning("Starting WebsocketProxy.py")
    try:
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(open_robot_server())
            t2 = tg.create_task(start_webserver())
    except Exception as e:
        non_recurring_logger.error(f"Error in main: {e}")
        raise e
    non_recurring_logger.error("WebsocketProxy.py has moved to after the with block")


if __name__ == '__main__':
    asyncio.run(main())
