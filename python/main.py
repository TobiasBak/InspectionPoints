import asyncio
import traceback

from RtdeConnection import start_rtde_loop
from WebsocketProxy import open_robot_server, start_webserver
from custom_logging import LogConfig

non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)


async def main():
    non_recurring_logger.warning("Starting WebsocketProxy.py")
    try:
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(safe_open_robot_server())
            t2 = tg.create_task(safe_start_webserver())
            t3 = tg.create_task(safe_start_rtde_loop())
    except Exception as e:
        non_recurring_logger.error(f"Error in main: {e}")
        raise e
    non_recurring_logger.error("WebsocketProxy.py has moved to after the with block")


async def safe_open_robot_server():
    try:
        await open_robot_server()
    except Exception as e:
        non_recurring_logger.error(f"Error in open_robot_server, restarting in 5 seconds: {traceback.print_tb(e.__traceback__)}")
        await asyncio.sleep(5)
        await safe_open_robot_server()

async def safe_start_webserver():
    try:
        await start_webserver()
    except Exception as e:
        non_recurring_logger.error(f"Error in start_webserver, restarting in 5 seconds: {traceback.print_tb(e.__traceback__)}")
        await asyncio.sleep(5)
        await safe_start_webserver()

async def safe_start_rtde_loop():
    try:
        await start_rtde_loop()
    except Exception as e:
        non_recurring_logger.error(f"Error in start_rtde_loop, restarting in 5 seconds: {traceback.print_tb(e.__traceback__)}")
        await asyncio.sleep(5)
        await safe_start_rtde_loop()


if __name__ == '__main__':
    asyncio.run(main())
