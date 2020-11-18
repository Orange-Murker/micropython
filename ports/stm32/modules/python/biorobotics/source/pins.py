"""
Custom extension on pyb.Timer to handle the combination of hardware timers
and pins
"""

from pyb import Pin, Timer

from .timer_channels import PINS_TO_TIMERS


class PWM:
    """Pulse-Width Modulation interface

    Main purpose of the class is to automatically select the correct timers
    and channels based on the target pin.
    """

    def __init__(self, pin_name: str, freq: float = 1000):
        """Constructor

        :param pin_name: Name of the pin (either STM or Arduino name),
            or a Pin object directly
        :param freq: PWM frequency
        """

        if isinstance(pin_name, Pin):
            self.pin = pin_name
        else:
            self.pin = Pin(pin_name)

        self.freq = freq

        stm_name = self.pin.name()
        if stm_name in PINS_TO_TIMERS:
            self.timer_number, self.channel_number = PINS_TO_TIMERS[stm_name]
        else:
            raise ValueError('The pin `{}` does not have a registered PWM '
                             'timer channel connected to it'.format(pin_name))

        # Select the timer to be used and set PWM frequency
        self.timer = Timer(self.timer_number, freq=self.freq)

        # Set channel of timer to PWM mode and attach the pin
        self.channel = self.timer.channel(self.channel_number, Timer.PWM,
                                          pin=self.pin)

    def write(self, pwm: float):
        """Write PWM as a number between 0.0 and 1.0"""
        self.write_percentage(pwm * 100.0)

    def write_percentage(self, percentage: float):
        """Write PWM as a decimal percentage between 0.0 and 100.0"""
        if percentage < 0.0:
            percentage = 0.0
        elif percentage > 100.0:
            percentage = 100.0
        self.channel.pulse_width_percent(percentage)
