"""
Encoder class
"""

from pyb import Timer
from math import floor

from .timer_channels import PINS_TO_TIMERS
from .pins import make_pin


class Encoder:
    """Class to wrap around hardware timers used for motor encoders

    The encoder takes two digital-in pins, A and B, which need to be connected
    to the same hardware timer.
    The encoder is always type X4.

    The class also takes care of unwrapping the value. The returned value
    will continue indefinitely, ignoring the integer overflow.
    """

    def __init__(self, pin_a: str, pin_b: str):
        """Constructor

        :param pin_a: Encoder pin A (name or Pin object)
        :param pin_b: Encoder pin B (name or Pin object)
        """

        self.pin_a = make_pin(pin_a)
        self.pin_b = make_pin(pin_b)

        for pin in [self.pin_a.name(), self.pin_b.name()]:
            if pin not in PINS_TO_TIMERS:
                raise ValueError('Pin `P{}` it not connected to a hardware '
                                 'timer'.format(pin))

        timer_a, channel_a = PINS_TO_TIMERS[self.pin_a.name()]
        timer_b, channel_b = PINS_TO_TIMERS[self.pin_b.name()]

        if timer_a != timer_b:
            raise ValueError('The pins `P{}` and `P{}` are not connected to '
                             'the same hardware timer and cannot be used for '
                             'an encoder together'.format(self.pin_a.name(),
                                                          self.pin_b.name))

        self._period = 0xFFFF  # 65535

        self.timer = Timer(timer_a, prescaler=0, period=self._period)
        # Note: the hardware timer has 16 bits, so after 65535 the counter
        # will fall back to 0.

        self.timer.channel(channel_a, Timer.ENC_AB, pin=self.pin_a)
        self.timer.channel(channel_b, Timer.ENC_AB, pin=self.pin_b)

        self._loop_count = 0  # Number of integer overflows (not the number
        # of axis revolutions!
        self._last_counter = 0  # Value of the counter on the last check

    def counter(self) -> int:
        """Return pulse count

        Pulse count has already been unwrapped, it will start at 0 and
        increase and decrease indefinitely (including going negative).

        Note: the unwrap happens when calling this read function, so it is
        possible to miss an encoder wrap if the read function is called only
        very rarely.
        """

        counter = self.timer.counter()

        diff = counter - self._last_counter  # If diff is to large we
        # probably wrapped
        if 2 * abs(diff) > self._period:
            if diff < 0:
                self._loop_count += 1  # If counter is suddenly low
            else:
                self._loop_count -= 1  # If counter is suddenly high

        self._last_counter = counter  # Update history

        # (period + 1) because counter = 0 with 1 loop should be output 65536
        return counter + self._loop_count * (self._period + 1)

    def set_counter(self, new_counter: int):
        """Reset the counter to a specified value"""

        pulses = new_counter % self._period  # Always positive
        self.timer.counter(pulses)  # Reset timer counter

        self._loop_count = floor(new_counter / self._period)  # Set loops
