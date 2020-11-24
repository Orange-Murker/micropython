"""
Modifications to the PWR_USB port and a PC class to transmit data
"""

import stm
import machine
from pyb import UART
from utime import ticks_us

# Imported C function that contains non-blocking uart3br.send()
# See uart3br.c in micropython external C modules folder
import uart3br

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

    def set_list(self, array):
        """Set all channels with an array"""
        if len(array) != self._channels:
            raise ValueError('{} channels were specified, but the given '
                             'array has {} elements'.format(self._channels,
                                                            len(array)))
        for i, value in enumerate(array):
            self._data[i] = float(value)  # Force cast to float

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
