from pyjoystick.sdl2 import Key, Joystick, run_event_loop
import math
import time
import threading

class XboxController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self):
        self.DIGITAL = {
            'LeftBumper' : 0,
            'RightBumper': 0,
            'A'          : 0,
            'B'          : 0,
            'X'          : 0,
            'Y'          : 0,
            'LeftThumb'  : 0,
            'RightThumb' : 0,
            'Back'       : 0,
            'Start'      : 0,
            'LeftDPad'   : 0,
            'RightDPad'  : 0,
            'UpDPad'     : 0,
            'DownDPad'   : 0
        }
        self.ANALOG = {
            'LeftJoystickX' : 0,
            'LeftJoystickY' : 0,
            'RightJoystickX': 0,
            'RightJoystickY': 0,
            'LeftTrigger'   : 0,
            'RightTrigger'  : 0
        }
        self.LeftJoystickY  = 0
        self.LeftJoystickX  = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger    = 0
        self.RightTrigger   = 0
        self.LeftBumper     = 0
        self.RightBumper    = 0
        self.A              = 0
        self.X              = 0
        self.Y              = 0
        self.B              = 0
        self.LeftThumb      = 0
        self.RightThumb     = 0
        self.Back           = 0
        self.Start          = 0
        self.LeftDPad       = 0
        self.RightDPad      = 0
        self.UpDPad         = 0
        self.DownDPad       = 0

        self._monitor_thread = threading.Thread(target=run_event_loop, args=(self.added_joystick, self.removed_joystick, self.key_received))
        self._monitor_thread.daemon = True
        self._monitor_thread.start()


    def read(self): # return the buttons/triggers that you care about in this methode
        x = self.LeftJoystickX
        y = self.LeftJoystickY
        a = self.A
        b = self.X # b=1, x=2
        rb = self.RightBumper
        return [x, y, a, b, rb]
    def added_joystick(self, joystick: Joystick):
        print(f"Added {joystick}")
    def removed_joystick(self, joystick: Joystick):
        print(f"Removed {joystick}")
    def key_received(self, key: Key):
        print(f"Key received: {key}")
    def update(self, function=None):
        # Update the ANALOG dictionary
        self.ANALOG = {
            'LeftJoystickX' : self.LeftJoystickX,
            'LeftJoystickY' : self.LeftJoystickY,
            'RightJoystickX': self.RightJoystickX,
            'RightJoystickY': self.RightJoystickY,
            'LeftTrigger'   : self.LeftTrigger,
            'RightTrigger'  : self.RightTrigger
        }
        # Update the DIGITAL dictionary
        self.DIGITAL = {
            'LeftBumper' : self.LeftBumper,
            'RightBumper': self.RightBumper,
            'A'          : self.A,
            'B'          : self.B,
            'X'          : self.X,
            'Y'          : self.Y,
            'LeftThumb'  : self.LeftThumb,
            'RightThumb' : self.RightThumb,
            'Back'       : self.Back,
            'Start'      : self.Start,
            'LeftDPad'   : self.LeftDPad,
            'RightDPad'  : self.RightDPad,
            'UpDPad'     : self.UpDPad,
            'DownDPad'   : self.DownDPad
        }
        if function:
            function(self.DIGITAL, self.ANALOG)

if __name__ == "__main__":
    controller = XboxController()
    while True:
        # Add a small delay to avoid flooding the output
        time.sleep(0.1)  # Adjust the sleep time as needed