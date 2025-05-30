#!/usr/bin/env python
# Copyright (c) 2016-2022, Universal Robots A/S,
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Universal Robots A/S nor the names of its
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL UNIVERSAL ROBOTS A/S BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import asyncio
import sys
from typing import Callable, Coroutine

from rtde import rtde_config, rtde
from rtde.serialize import DataObject

from SocketMessages import RtdeState
from WebsocketNotifier import websocket_notifier
from WebsocketProxy import has_new_client
from constants import ROBOT_IP, RTDE_PORT, RTDE_CONFIG_FILE
from custom_logging import LogConfig

conf = rtde_config.ConfigFile(RTDE_CONFIG_FILE)
state_names, state_types = conf.get_recipe("state")

TRANSMIT_FREQUENCY_IN_HERTZ = 30
SLEEP_TIME = 1 / TRANSMIT_FREQUENCY_IN_HERTZ

type ListenerFunction = Callable[[DataObject], Coroutine[None, None, None]]
listeners: list[ListenerFunction] = []

recurring_logger = LogConfig.get_recurring_logger(__name__)


async def start_rtde_loop():
    con = rtde.RTDE(ROBOT_IP, RTDE_PORT)
    con.connect()
    # get controller version
    con.get_controller_version()
    # setup recipes
    con.send_output_setup(state_names, state_types)
    # start data synchronization
    if not con.send_start():
        recurring_logger.error("Unable to start synchronization")
        sys.exit()

    register_listener(send_state_through_websocket)

    previous_state = None

    while True:
        try:
            new_state = con.receive()
            if has_new_client():
                await call_listeners(new_state)
            if state_is_new(new_state, previous_state):
                await call_listeners(new_state)
                previous_state = new_state
        except Exception as e:
            recurring_logger.error(f"Error in recieve_rtde_data: {e}")
        await asyncio.sleep(SLEEP_TIME)


def states_are_equal(obj1: DataObject, obj2: DataObject):
    return obj1.__dict__ == obj2.__dict__


async def send_state_through_websocket(state: DataObject) -> None:
    robot_state = RtdeState(state)
    websocket_notifier.notify_observers(str(robot_state))


def state_is_new(new_state: DataObject | None, old_state: DataObject | None):
    if old_state is None and new_state is not None:
        return True
    if old_state is None and new_state is None:
        return False
    if states_are_equal(old_state, new_state):
        return False

    return True


def register_listener(listener: ListenerFunction):
    listeners.append(listener)


async def call_listeners(with_state: DataObject):
    for listener in listeners:
        await listener(with_state)
    recurring_logger.debug(f"All listeners called with state: {with_state}")
