"""BioRobotics package."""

from utime import ticks_us
import micropython
from pyb import Timer, UART
import machine
import gc
import stm

# Imported C function that contains non-blocking uart3br.send()
# See uart3br.c in micropython external C modules folder
import uart3br

# Time measurement function similar to Matlab's tic/toc
# tic();toc() itself takes 6us, excluding the print statements
t0 = 0


def tic() -> None:
    """Start time measurement"""
    global t0
    t0 = ticks_us()


def toc() -> float:
    """End time measurement, print and return results"""
    global t0
    t1 = ticks_us()
    time_taken = t1 - t0
    print('Time elapsed: %.3f us' % time_taken)
    return time_taken


# Set mem for error messages while in Interrupt Service Routines (ISR)
# Without setting this memory exceptions cannot be mentioned properly
micropython.alloc_emergency_exception_buf(100)


class Ticker:
    """Timed callback manager

    BioRobotics hardware timer ISR abstraction
     - Removing the need of explicit tim.callback(micropython.schedule())
        etc. garbage
     - Timely garbage collection set on a ticker with GC=Enable
     - Other timer related functions

     Note: the ticker is not started on initialization!
    """

    def __init__(self, timer: int, freq: float, fun: callable,
                 enable_gc: bool = False):
        """Construct Ticker

        :param timer: Number of the on-board hardware timer to use
        :param freq: Frequency (in Hz) of the callback
        :param fun: Callback to be attached to the timer
        :param enable_gc: Set to True to disable general automatic garbage
            collection and instead run GC at the end of the user callback -
            This is most recommended when the function is the `loop()` of the
            program
        """
        self.timer_number = timer
        self.freq = freq
        self.fun = fun
        self.enable_gc = enable_gc

        if self.enable_gc:
            gc.disable()

        # Create Timer, but don't set callback yet (it won't do anything)
        self.timer = Timer(self.timer_number, freq=self.freq)

        self.is_started = False

    def fun_wrap(self, *args):
        """Wrapper around the user callback

        The schedule function passes a single argument, so we have to
        capture it in this method definition.
        """
        self.fun()

        # Collect garbage if this is the "main" loop
        if self.enable_gc:
            gc.collect()

    def start(self):
        """Start ticker"""
        # Attach callback function wrapper
        # callback() passes a single argument, which is not used now
        self.timer.callback(
            lambda arg: micropython.schedule(self.fun_wrap, arg)
        )
        self.is_started = True

    def stop(self):
        """Stop ticker"""
        self.timer.deinit()  # Clears all callbacks
        self.is_started = False


# Enable the uart and set baudrate
uart_pc = UART(3, 115200)

# Disable the default enabled useless RX IRQ
machine.mem8[stm.USART3 + stm.USART_CR1] &= ~(1 << 5)

# Reserved address in ram where to exchange data between micropython and C
# layer
# Addresses incrementing of 1 means 1 8mem
REG = 0x30040000
REG_L = 16

# Reset data exchange counters
machine.mem32[REG + 0] = 0  # c
machine.mem32[REG + 4] = 0  # n


class SerialPC:
    """Create serial connection to send data asynchronously

    Non-blocking serial TX over CN1 (ST-Link VCOM, UART3) on STM32 H743ZI2

    On every .send(), a floating point value (4 bytes) for every channel is
    transmitted.
    The protocol is:
        - 3 identifier header bytes
        - 1 byte with the number of channels
        - 4 bytes with the current runtime in microseconds
        - multiples of 4 bytes
    """

    def __init__(self, channels: int):
        """Constructor

        :param channels: Number of channels to send data over
        """
        self._channels = channels
        self._data = channels * [float('nan')]
        self._time = 0.0
        self._identifier = 0x7FFFBF00

    def set(self, channel, value):
        """Set data in channel, prepared to be sent"""
        self._data[channel] = float(value)  # Force parse to float

    def send(self):
        """Send packet"""

        # 3 identifier bytes, followed by one byte channel number
        uart3br.send(self._identifier ^ self._channels)

        # Timestamp integer in microseconds
        self._time = ticks_us()
        uart3br.send(self._time)

        # Data
        for item in self._data:
            uart3br.send(item)

        # Reset data to nans, such that sending data is explicit
        self._data = self._channels * [float('nan')]
