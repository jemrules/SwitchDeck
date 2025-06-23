import asyncio
import threading
from enum import Enum

from aioconsole import ainput

from joycontrol import logging_default as log, utils
from joycontrol.command_line_interface import ControllerCLI
from joycontrol.controller import Controller
from joycontrol.controller_state import ControllerState, button_press
from joycontrol.memory import FlashMemory
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server
class EventType(Enum):
    CONNECT_DEVICE = "connect_device"
    DISCONNECT_DEVICE = "disconnect_device"

class test:
    def __init__(self):
        def thread_function():
            try:
                asyncio.run(self.run())
            except RuntimeError as e:
                print(f"RuntimeError: {e}")
            except Exception as e:
                print(f"Exception: {e}")
            print("Thread function completed")
        self.init_variables()
        self.event_queue = asyncio.Queue() #type (EventType, args:list[any])
        self._thread = threading.Thread(target=thread_function)
        self._thread.daemon = True
        self._thread.start()
    def init_variables(self):
        self.factory = None
        self.transport = None
        self.protocol = None
        self.controller_state = None
        self.spi_flash=None
    def event_connect_device(self, address=None):
        print(f"Connecting to device at {address}")
        self.event_queue.put_nowait((EventType.CONNECT_DEVICE, [address]))
    async def connect_device(self, address=None):
        with utils.get_output(default=None) as capture_file:
            controller = Controller.PRO_CONTROLLER
            spi_flash = FlashMemory()
            factory = controller_protocol_factory(controller,spi_flash=spi_flash)
            ctl_psm, itr_psm = 17, 19
            transport, protocol = await create_hid_server(factory,
                                                        reconnect_bt_addr=address,
                                                        ctl_psm=ctl_psm,
                                                        itr_psm=itr_psm)
            controller_state = protocol.get_controller_state()
        await controller_state.connect()
        print(f"Connected to device at {address}")
        self.event_queue.task_done()
    async def run(self):
        while True:
            if self.event_queue.empty():
                await asyncio.sleep(0.1)
                continue
            event_type, args = await self.event_queue.get()
            match event_type:
                case EventType.CONNECT_DEVICE:
                    print(f"Event: {event_type.value}, Args: {args}")
                    address = args[0] if args else None
                    await self.connect_device(address)
                case EventType.DISCONNECT_DEVICE:
                    ...

if __name__ == "__main__":
    print("Finished")
    t = test()
    t.event_connect_device()
    while True:
        ...

