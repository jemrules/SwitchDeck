
#! Some code is commented out because joycontrol package doesn't work on windows add them later on the Steam Deck
from time import sleep
from enum import Enum
import subprocess
import threading
import argparse
import asyncio
import logging
import sys
import os
import re

from game_controller import SteamDeckController
from misc import Indicator, Event, RunAsync, RunThreadedAsync
from switch_connection_handler import ConnectionStatus, SwitchConnectionHandler

from aioconsole import ainput

from joycontrol import logging_default as log, utils
from joycontrol.command_line_interface import ControllerCLI
from joycontrol.controller import Controller
from joycontrol.controller_state import ControllerState, button_press
from joycontrol.memory import FlashMemory
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

async def press_btn(controller_state,btn,duration=0.1):
    # Available buttons: {'y','x','b','a','r','zr','minus','plus','r_stick','l_stick','home','capture','down','up','right','left','l','zl'}
    controller_state.button_state.set_button(btn, True)
    await controller_state.send()
    await asyncio.sleep(duration)
    controller_state.button_state.set_button(btn, False)
    await controller_state.send()
# async def btnpush(btn,controller_state):
#     print(f"Pushing button: {btn}")
#     controller_state.button_state.set_button(btn, True)
#     print(f"Button {btn} pushed.")
# def button_push(controller_state, btn):
#     asyncio.run(btnpush(btn, controller_state))
# async def btnrelease(btn,controller_state):
#     print(f"Releasing button: {btn}")
#     controller_state.button_state.set_button(btn, False)
#     print(f"Button {btn} released.")
# def button_release(controller_state, btn):
#     asyncio.run(btnrelease(btn, controller_state))
# async def move_stick(controller_state,stick="l",direction="x",scale=1):
#     scale=min((scale+1)/2*(0x1000),0x1000-1)
#     a=None
#     match stick.lower()[0]:
#         case "l":
#             a=controller_state.l_stick_state
#         case "r":
#             a=controller_state.r_stick_state
#     match direction.lower()[0]:
#         case "x":
#             a.set_h(scale)
#         case "y":
#             a.set_v(scale)

# async def ConnectToController(address:str=None,parent=None):
#     global GLOBAL_controller_state, GLOBAL_transport
#     with utils.get_output(default=None) as capture_file:
#         controller = Controller.PRO_CONTROLLER
#         spi_flash = FlashMemory()
#         factory = controller_protocol_factory(controller,spi_flash=spi_flash)
#         ctl_psm, itr_psm = 17, 19
#         transport, protocol = await create_hid_server(factory,
#                                                       reconnect_bt_addr=address,
#                                                       ctl_psm=ctl_psm,
#                                                       itr_psm=itr_psm)
#         controller_state = protocol.get_controller_state()
#         await controller_state.connect()
#         if parent:
#             parent.controller_state = controller_state
#             parent.transport = transport
#         GLOBAL_controller_state = controller_state
#         GLOBAL_transport = transport
#         print(f"transport: {transport}, controller_state: {controller_state}")
#         return controller_state, transport
#         # await transport.close()
def list_switches():
    raw_addrs=subprocess.getoutput("bluetoothctl devices")
    addrs=raw_addrs.split("\n")
    addrs=[re.findall(r"(((([0-9A-Z]{2}):){5})[0-9A-Z][0-9A-Z])",x)[0][0] for x in addrs if x.lower().__contains__("nintendo")]
    return addrs

class InputHandler(SteamDeckController):
    def __init__(self, SwitchHandler: SwitchConnectionHandler):
        super().__init__(self.handle_input)
        self.SwitchHandler = SwitchHandler
        self.running = True
        self.JOYCON_DIGITAL_KEYS = {
            "LeftTrigger": "zl",
            "RightTrigger": "zr",
            "LeftBumper": "l",
            "RightBumper": "r",
            "A": "a",
            "B": "b",
            "X": "x",
            "Y": "y",
            "LeftThumb": "l_stick",
            "RightThumb": "r_stick",
            "Back": "minus",
            "Start": "plus",
            "LeftDPad": "left",
            "RightDPad": "right",
            "UpDPad": "up",
            "DownDPad": "down"
        }
    
    def handle_input(self,digital: dict,analog: dict): #* This method is called after every input loop in super _monitor_controller
        if not self.running:
            return
        print("Handling input...")
        for key, value in self.JOYCON_DIGITAL_KEYS.items():
            print(f"Key: {key}, Value: {value}, Digital Value: {self.DIGITAL[key]}")
            if digital[key]>0.5:
                self.SwitchHandler.button_press(value)
            else:
                self.SwitchHandler.button_release(value)
        print("Done handling input!")
class ConnectionType(Enum):
    PAIRED = "paired"
    UNPAIRED = "unpaired"
    DIRECT_CONNECT = "direct_connect"

class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Procontroller GUI")
        self.setGeometry(100, 100, 600, 400)
        self.center_widget = QWidget(self)
        self.setCentralWidget(self.center_widget)
        self.layout = QVBoxLayout()
        self.centralWidget().setLayout(self.layout)

        # Indicators
        self.connection_indicator = Indicator("Disconnected",self)
        self.layout.addWidget(self.connection_indicator)
        self.connection_indicator.set_size(20)
        self.connection_indicator.setAlignment(Qt.AlignCenter)
        self.connection_indicator.move(20,40)
        self.connection_indicator.adjustSize()
        
        # List of Nintendo Switches
        self.list_of_switches = QListWidget(self)
        self.layout.addWidget(self.list_of_switches)
        self.list_of_switches.setGeometry(20, 80, 200, 300)
        self.list_of_switches.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_of_switches.setStyleSheet("font-size: 16px;")
        self.switch_addresses=[]  # Placeholder for switch addresses
        for address in self.switch_addresses:
            item = QListWidgetItem(address)
            item.setData(Qt.UserRole, address)
            self.list_of_switches.addItem(item)
        self.list_of_switches.itemClicked.connect(self.on_switch_selected)

        #Menu Bar
        self.mb=self.menuBar()
        self.connection_menu = QMenu("&Connection", self)
        connection=self.mb.addMenu("Connection")
        connection.mousePressEvent = lambda event: self.update_connection_menu()

        self.reconnect_action = connection.addAction("Reconnect")
        self.reconnect_action.setShortcut("Ctrl+R")
        self.reconnect_action.triggered.connect(self.reconnect_switch)
        self.reconnect_action.setEnabled(False)
        self.disconnect_action = connection.addAction("Disconnect")
        self.disconnect_action.setShortcut("Ctrl+D")
        self.disconnect_action.triggered.connect(self.disconnect_switch)
        self.disconnect_action.setEnabled(False)
        self.pair_action = connection.addAction("Pair to New Device")
        self.pair_action.setShortcut("Ctrl+C")
        self.pair_action.triggered.connect(self.pair_switch)
        self.exit_action = connection.addAction("Exit")
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.Close)
        self.remove_action = connection.addAction("Remove")
        self.remove_action.setShortcut("Del")
        self.remove_action.triggered.connect(self.remove_switch)
        self.remove_action.setEnabled(False)
        
        self.refresh_timer=QTimer(self)
        self.refresh_timer.timeout.connect(self.update_switch_list)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds

        self.SwitchHandler = SwitchConnectionHandler()  # Initialize the switch connection handler

        self.SWITCH_ADDRESS = "00:00:00:00:00:00"  # Placeholder for switch address
        
        self.XboxController = InputHandler(self.SwitchHandler)  # Initialize Xbox controller

        from typing import Tuple
        self.update_switch_list()
    def on_switch_selected(self, item):
        self.reconnect_action.setEnabled(True)
        self.remove_action.setEnabled(True)
    def update_switch_list(self):
        self.update_connection_menu()
        # Here you would normally fetch the list of connected switches
        raw_addrs=subprocess.getoutput("bluetoothctl devices")
        addrs=raw_addrs.split("\n")
        addrs=[re.findall(r"(((([0-9A-Z]{2}):){5})[0-9A-Z][0-9A-Z])",x)[0][0] for x in addrs if x.lower().__contains__("nintendo")]
        self.switch_addresses = addrs  # Update the switch addresses
        # For now, we will just re-add the same placeholder addresses
        for address in self.switch_addresses:
            if self.list_of_switches.findItems(address, Qt.MatchExactly):
                continue
            item = QListWidgetItem(address)
            item.setData(Qt.UserRole, address)
            self.list_of_switches.addItem(item)
        logging.info("Switch list updated.")
        self.refresh_timer.start(5000)  # Restart the timer
    def Close(self):
        super().close()
        return None
    def close(self):
        sys.exit(0)
        return super().close()
    def update_connection_menu(self):
        # print("Updating connection menu...")
        match self.SwitchHandler.status:
            case ConnectionStatus.CONNECTED:
                self.disconnect_action.setEnabled(True)
                self.reconnect_action.setEnabled(False)
                self.pair_action.setEnabled(False)
            case ConnectionStatus.DISCONNECTED:
                self.disconnect_action.setEnabled(False)
                self.reconnect_action.setEnabled(False)
                self.pair_action.setEnabled(True)
            case ConnectionStatus.RECONNECTING:
                self.disconnect_action.setEnabled(False)
                self.reconnect_action.setEnabled(False)
                self.pair_action.setEnabled(False)
            case ConnectionStatus.PAIRING:
                self.disconnect_action.setEnabled(False)
                self.reconnect_action.setEnabled(False)
                self.pair_action.setEnabled(False)
        if self.list_of_switches.currentItem() is not None:
            self.reconnect_action.setEnabled(True)
            self.remove_action.setEnabled(True)
    def pair_switch(self):
        self.connection_indicator.setText("Pairing...")
        self.connection_indicator.set_color("yellow")
        self.SwitchHandler.status = (ConnectionStatus.PAIRING)
        # Here you would implement the pairing logic
        def pairing():
            self.SwitchHandler.event_connect_device()
            while self.SwitchHandler.status == ConnectionStatus.PAIRING:
                sleep(0.1)
            match self.SwitchHandler.status:
                case ConnectionStatus.CONNECTED:
                    self.connection_indicator.setText("Paired!")
                    self.connection_indicator.set_color("green")
                case ConnectionStatus.DISCONNECTED:
                    self.connection_indicator.setText("Pairing Failed")
                    self.connection_indicator.set_color("red")
                case ConnectionStatus.ERROR:
                    self.connection_indicator.setText("Pairing Error")
                    self.connection_indicator.set_color("red")
            print(f"Pairing successful. {self.SwitchHandler.status}")
        pair_event=Event(self)
        pair_event.connect(pairing)
        pair_event.trigger()
    def disconnect_switch(self):
        # Here you would implement the disconnection logic
        if self.SwitchHandler.controller_state:
            # Assuming controller_state has a disconnect method
            try:
                self.SwitchHandler.event_disconnect_device()
                self.SwitchHandler.transport.close()
            except Exception as e:
                logging.error(f"Disconnection failed: {e}")
        self.SwitchHandler.controller_state, self.SwitchHandler.transport = None, None
        self.connection_indicator.setText("Disconnected")
        self.connection_indicator.set_color("red")
        self.SwitchHandler.status = (ConnectionStatus.DISCONNECTED)
        self.reconnect_action.setEnabled(False)
        self.remove_action.setEnabled(False)
    def reconnect_switch(self):
        self.connection_indicator.setText("Reconnecting...")
        self.connection_indicator.set_color("yellow")
        self.SwitchHandler.status = (ConnectionStatus.RECONNECTING)
        self.SWITCH_ADDRESS = self.list_of_switches.currentItem().data(Qt.UserRole) if self.list_of_switches.currentItem() else None
        def reconnecting():
            self.SwitchHandler.event_connect_device(self.SWITCH_ADDRESS)
            while self.SwitchHandler.status == ConnectionStatus.RECONNECTING:
                sleep(0.1)
            match self.SwitchHandler.status:
                case ConnectionStatus.CONNECTED:
                    self.connection_indicator.setText("Reconnected!")
                    self.connection_indicator.set_color("green")
                case ConnectionStatus.DISCONNECTED:
                    self.connection_indicator.setText("Disconnected")
                    self.connection_indicator.set_color("red")
                case ConnectionStatus.ERROR:
                    self.connection_indicator.setText("Reconnection Failed")
                    self.connection_indicator.set_color("red")
        reconnect_event = Event(self)
        reconnect_event.connect(reconnecting)
        reconnect_event.trigger()
    def remove_switch(self):
        selected_items: list = self.list_of_switches.selectedItems()
        if len(selected_items) == 0:
            return
        for item in selected_items:
            self.list_of_switches.takeItem(self.list_of_switches.row(item))
            # Here you would implement the logic to remove the switch from the system
            os.system(f"bluetoothctl remove {item.text()}")
            logging.info(f"Removed switch: {item.text()}")
        self.remove_action.setEnabled(False)
        self.reconnect_action.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())