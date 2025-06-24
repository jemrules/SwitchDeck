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
            "button 0" : "A",
            "button 1" : "B",
            "button 2" : "Y",
            "button 3" : "X",
            "button 4" : "LeftBumper",
            "button 5" : "RightBumper",
            "button 6" : "Back",
            "button 7" : "Start",
            "button 8" : "",
            "button 9" : "LeftThumb",
            "button 10": "RightThumb",
            "button 11": "",
            "button 12": "",
            "button 13": "",
            "button 14": "",
            "button 15": "",
            "button 16": "",
            "button 17": "",
            "button 18": "",
            "button 19": ""
            # "button 0" : "A",
            # "button 1" : "B",
            # "button 2" : "Y",
            # "button 3" : "X",
            # "button 4" : "Back",
            # "button 5" : "Steam",
            # "button 6" : "Start",
            # "button 7" : "LeftThumb",
            # "button 8" : "RightThumb",
            # "button 9" : "LeftBumper",
            # "button 10": "RightBumper",
            # "button 11": "UpDPad",
            # "button 12": "DownDPad",
            # "button 13": "LeftDPad",
            # "button 14": "RightDPad",
            # "button 15": "QuickAccess",
            # "button 16": "R4",
            # "button 17": "L4",
            # "button 18": "R5",
            # "button 19": "L5",
        }
        self.ANALOG_KEYS = {
            # "axis 0" : "",
            # "axis 1" : "",
            # "axis 2" : "",
            # "axis 3" : "",
            # "axis 4" : "",
            # "axis 5" : "",
            # "axis 6" : "",
            # "axis 7" : "",
            # "axis 8" : "",
            # "axis 9" : "",
            # "axis 10": ""
            "button 0" : "A",
            "button 1" : "B",
            "button 2" : "Y",
            "button 3" : "X",
            "button 4" : "Back",
            "button 5" : "Steam",
            "button 6" : "Start",
            "button 7" : "LeftThumb",
            "button 8" : "RightThumb",
            "button 9" : "LeftBumper",
            "button 10": "RightBumper",
            "button 11": "UpDPad",
            "button 12": "DownDPad",
            "button 13": "LeftDPad",
            "button 14": "RightDPad",
            "button 15": "QuickAccess",
            "button 16": "R4",
            "button 17": "L4",
            "button 18": "R5",
            "button 19": "L5",
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
            "axis 0" : "LeftJoystickX+",
            "-axis 0": "LeftJoystickX-",
            "axis 1" : "LeftJoystickY-",
            "-axis 1": "LeftJoystickY+",

            "axis 2" : "RightJoystickX+",
            "-axis 2": "RightJoystickX-",
            "axis 3" : "RightJoystickY-",
            "-axis 3": "RightJoystickY+",

            "axis 4" : "LeftTrigger+",
            "axis 5" : "RightTrigger+"
        }
        self.Found=[]
        print("All joysticks:",Joystick.get_joysticks())
        self._monitor_thread = threading.Thread(target=run_event_loop, args=(self.added_joystick, self.removed_joystick, self.key_received))
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
    def added_joystick(self, joystick: Joystick):
        print(f"Added {joystick}")
    def removed_joystick(self, joystick: Joystick):
        print(f"Removed {joystick}")
    def key_received(self, key: Key):
        # if not key.keyname.lower().__contains__("axis"):
        #     print(f"Key received: {key.value} ({key.keyname})")
        # elif abs(key.value) >0.07:
        #     print(f"Key received: {key.value} ({key.keyname}) - Ignored due to low value")
        if key.keyname.lower().__contains__("button"):
            print(f"Key received: {key.value} ({key.keyname})")
            for key_name, key_value in self.DIGITAL_KEYS.items():
                if key.keyname.lower() == key_name.lower():
                    try:
                        self.DIGITAL[self.DIGITAL_KEYS[key_name]] = key.value
                    except KeyError:
                        # print(f"Key {key_name} not found in DIGITAL_KEYS")
                        continue
                    # if key.value>0.5:
                    #     try:
                    #         print(f"Key pressed: {self.DIGITAL_KEYS[key_name]} ({self.DIGITAL[key_name]})")
                    #     except:
                    #         print(f"Key pressed: {key_name} ({key.value})")
                    break
        elif key.keyname.lower().__contains__("axis"):
            if not key.keyname.lower() in self.Found:
                self.Found.append(key.keyname.lower())
                print(f"Found axis: {key.keyname} ({key.value})")
            for key_name, key_value in self.ANALOG_KEYS.items():
                if key.keyname.lower() == key_name.lower():
                    self.ANALOG[key_value[:-1]] = -key.value if (key_value.endswith('-')) != (key_name.startswith("-")) else key.value
                    break
        self.DIGITAL['LeftTrigger']  = 1 if self.ANALOG['LeftTrigger'] > 0.25 else 0
        self.DIGITAL['RightTrigger'] = 1 if self.ANALOG['RightTrigger'] > 0.25 else 0
        self.update(self.function)
    def update(self, function=None):
        if function:
            function(self.DIGITAL, self.ANALOG)

if __name__ == "__main__":
    controller = SteamDeckController()
    while True:
        # Add a small delay to avoid flooding the output
        time.sleep(0.1)  # Adjust the sleep time as needed