"""
Custom extension on pyb.Timer to handle the combination of hardware timers
and pins
"""

from pyb import Pin, Timer
from machine import ADC

from .timer_channels import PINS_TO_TIMERS


def make_pin(pin: str) -> Pin:
    """Parse input into a Pin object

    :param pin: Input object
    """

    if isinstance(pin, Pin):
        return pin

    if isinstance(pin, str):
        return Pin(pin)

    raise ValueError('Cannot convert `{}` of type `{}` into a Pin '
                     'object'.format(pin, type(pin)))


class PWM:
    """Pulse-Width Modulation interface

    Main purpose of the class is to automatically select the correct timers
    and channels based on the target pin.
    """

    def __init__(self, pin: str, freq: float = 1000):
        """Constructor

        An error is thrown if the pin is not connected to a timer channel.

        :param pin: Name of the pin (either STM or Arduino name),
            or a Pin object directly
        :param freq: PWM frequency
        """

        self.pin = make_pin(pin)

        self.freq = freq

        stm_name = self.pin.name()
        if stm_name in PINS_TO_TIMERS:
            self.timer_number, self.channel_number = PINS_TO_TIMERS[stm_name]
        else:
            raise ValueError('The pin `P{}` does not have a registered PWM '
                             'timer channel connected to '
                             'it'.format(pin.name()))

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


class AnalogIn:
    """Read analog signal

    Extension of ADC
    """

    def __init__(self, pin: str):
        """Constructor

        An error will be throws if the pin does not have an
        Analog-to-Digital converted connected.

        :param pin: Name of a pin or Pin object
        """

        self.pin = make_pin(pin)
        self.adc = ADC(self.pin)

    def read(self) -> float:
        """Get analog input value between 0.0 and 1.0

        Corresponding to 0 to 3.3V. The Nucleo appears to be 5V tolerant.
        The resolution is 16 bit.
        """
        return float(self.adc.read_u16()) / 65535.0

    def read_u16(self) -> int:
        """Get analog input as integer, from 0 to 65535"""
        return self.adc.read_u16()
