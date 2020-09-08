"""
Dummy module that does nothing
Fakes part of the MicroPython modules

Note that the Windows build already has a machine module (outside the frozen modules)
This module neatly overrides that one
"""


class Pin(object):
    OUT = 0
    IN = 1
    OPEN_DRAIN = 2
    ALT = 3
    ALT_OPEN_DRAIN = 4
    PULL_UP = 5
    PULL_DOWN = 6
    PULL_HOLD = 7
    LOW_POWER = 8
    MED_POWER = 9
    HIGH_POWER = 10
    IRQ_FALLING = 11
    IRQ_RISING = 12
    IRQ_LOW_LEVEL = 13
    IRQ_HIGH_LEVEL = 14

    def __init__(self, pin_id, mode_value=-1,
                 pull_value=-1, pin_value=-1, drive_value=-1, alt_value=-1):
        self.pin_id = pin_id
        self.mode_value = mode_value
        self.pull_value = pull_value
        self.pin_value = pin_value
        self.drive_value = drive_value
        self.alt_value = alt_value
        self.callback = None
        return

    def value(self, value=None):
        """
        Set or get dummy pin value
        """
        if value is None:
            return self.pin_value
        self.pin_value = value
        return

    def on(self):
        self.pin_value = 1
        return

    def off(self):
        self.pin_value = 0
        return

    def mode(self, mode=None):
        if mode is None:
            return self.mode_value
        self.mode_value = mode
        return

    def pull(self, pull=None):
        if pull is None:
            return self.pull_value
        self.pull_value = pull
        return

    def drive(self, drive=None):
        if drive is None:
            return self.drive_value
        self.drive_value = drive
        return

    def irq(self, handler, trigger=None, priority=1, wake=None, hard=False):
        self.callback = handler
        return
