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
        self.send_input = False
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
    def event_disconnect_device(self):
        print("Disconnecting device")
        self.event_queue.put_nowait((EventType.DISCONNECT_DEVICE, []))
    
    def button_press(self, button_name):
        if self.controller_state:
            self.controller_state.button_state.set_button(button_name, True)
            self.send_input = True
        else:
            print("Controller is not connected")
    def button_release(self, button_name):
        if self.controller_state:
            self.controller_state.button_state.set_button(button_name, False)
            self.send_input = True
        else:
            print("Controller is not connected")
    def move_stick(self,stick="l",direction="x",scale=1):
        if not self.controller_state:
            print("Controller is not connected")
            return
        scale=min((scale+1)/2*(0x1000),0x1000-1)
        a=None
        match stick.lower()[0]:
            case "l":
                a=self.controller_state.l_stick_state
            case "r":
                a=self.controller_state.r_stick_state
        match direction.lower()[0]:
            case "x":
                a.set_h(scale)
            case "y":
                a.set_v(scale)

    async def connect_device(self, address=None):
        controller = Controller.PRO_CONTROLLER
        self.spi_flash = FlashMemory()
        self.factory = controller_protocol_factory(controller,spi_flash=self.spi_flash)
        ctl_psm, itr_psm = 17, 19
        self.transport, self.protocol = await create_hid_server(self.factory,reconnect_bt_addr=address,ctl_psm=ctl_psm,itr_psm=itr_psm)
        self.controller_state = self.protocol.get_controller_state()
        if not self.controller_state or not self.transport:
            print("Failed to connect to device")
            return
        await self.controller_state.connect()
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
            if self.controller_state and self.send_input:
                if self.controller_state.is_connected():
                    print(f"Controller state: {self.controller_state}")
                else:
                    print("Controller is not connected")

if __name__ == "__main__":
    print("Finished")
    t = test()
    t.event_connect_device("60:6B:FF:9B:65:C9")
    while True:
        ...

