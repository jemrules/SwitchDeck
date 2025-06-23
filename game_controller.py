from pyjoystick.sdl2 import Key, Joystick, run_event_loop
import math
import time
import threading

class SteamDeckController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self,function=None):
        self.function = function
        self.DIGITAL = {
            'A'           : 0,
            'B'           : 0,
            'X'           : 0,
            'Y'           : 0,
            'LeftBumper'  : 0,
            'RightBumper' : 0,
            'LeftTrigger' : 0,
            'RightTrigger': 0,
            'Back'        : 0,
            'Start'       : 0,
            'LeftThumb'   : 0,
            'RightThumb'  : 0,
            'UpDPad'      : 0,
            'DownDPad'    : 0,
            'LeftDPad'    : 0,
            'RightDPad'   : 0,
            'Steam'       : 0,
            'QuickAccess' : 0,
            'L4'          : 0,
            'L5'          : 0,
            'R4'          : 0,
            'R5'          : 0
        }
        self.DIGITAL_KEYS = {
            "Button 0" : "A",
            "Button 1" : "B",
            "Button 2" : "Y",
            "Button 3" : "X",
            "Button 4" : "Back",
            "Button 5" : "Steam",
            "Button 6" : "Start",
            "Button 7" : "LeftThumb",
            "Button 8" : "RightThumb",
            "Button 9" : "LeftTrigger",
            "Button 10": "RightTrigger",
            "Button 11": "",
            "Button 12": "",
            "Button 13": "",
            "Button 14": "",
            "Button 15": "QuickAccess",
            "Button 16": "R4",
            "Button 17": "L4",
            "Button 18": "R5",
            "Button 19": "L5",
            "Button 20": ""
        }
        self.ANALOG = {
            'LeftJoystickX' : 0,
            'LeftJoystickY' : 0,
            'RightJoystickX': 0,
            'RightJoystickY': 0,
            'LeftTrigger'   : 0,
            'RightTrigger'  : 0
        }
        self.ANALOG_KEYS = {
            "Axis 0" : "",
            "-Axis 0" : "",
            "Axis 1" : "",
            "-Axis 1" : "",
            "Axis 2" : "",
            "Axis 3" : ""
        }
        self._monitor_thread = threading.Thread(target=run_event_loop, args=(self.added_joystick, self.removed_joystick, self.key_received))
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
    def added_joystick(self, joystick: Joystick):
        print(f"Added {joystick}")
    def removed_joystick(self, joystick: Joystick):
        print(f"Removed {joystick}")
    def key_received(self, key: Key):
        if not key.keyname.lower().__contains__("axis"):
            print(f"Key received: {key.value} ({key.keyname})")
        elif abs(key.value) >0.03:
            print(f"Key received: {key.value} ({key.keyname}) - Ignored due to low value")
        for key_name, key_value in self.DIGITAL_KEYS.items():
            if key.keyname.lower() == key_name.lower():
                self.DIGITAL[key_name] = key.value
                break
        self.update(self.function)
    def update(self, function=None):
        if function:
            function(self.DIGITAL, self.ANALOG)

if __name__ == "__main__":
    controller = SteamDeckController()
    while True:
        # Add a small delay to avoid flooding the output
        time.sleep(0.1)  # Adjust the sleep time as needed