"""
Dummy module for pyb
Does not actually do much
"""


class LED:
    """
    Stub class for LED

    Does not actually do anything
    """

    on = False
    intensity = 0

    def __init__(self, id):
        return

    def intensity(self, value=None):
        if value is None:
            return self.intensity
        self.intensity = value

    def off(self):
        self.on = False

    def on(self):
        self.on = True

    def toggle(self):
        self.on = not self.on


"""Global methods"""


def delay(ms):
    return


def udelay(us):
    return


def millis():
    return 0


def micros():
    return 0


def elapsed_millis(start=0):
    return 0
