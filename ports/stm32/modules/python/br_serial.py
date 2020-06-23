# Biorobotics non-blocking serial TX over CN1 (ST-Link VCOM, UART3) on STM32 H743ZI2

# Imports
import machine, stm, pyb, utime

# Imported C function that contains non-blocking uart3br.send()
# See uart3br.c in micropython external C modules folder
import uart3br

# Enable the uart and set baudrate
uart_pc = pyb.UART(3, 115200)

# Disable the default enabled useless RX IRQ
machine.mem8[stm.USART3+stm.USART_CR1] &= ~(1 << 5)

# Reserved adress in ram where to exchange data between micropython and C layer
# Adresses incrementing of 1 means 1 8mem
REG = 0x30040000
REG_L = 16

# Reset data exchange counters
machine.mem32[REG+0]=0 # c
machine.mem32[REG+4]=0 # n

class serial_pc:

    def __init__(self, nch):
        self.nch = nch
        self.data = nch*[float('nan')]
        self.time = []

    def set(self, ch, word):
        self.data[ch] = float(word)

    
    def send(self):

        # 3 identifier bytes, one byte channel number
        uart3br.send(0x7FFFBF00^self.nch)

        # Timestamp integer in microseconds
        self.time = utime.ticks_us()
        uart3br.send(self.time)

        # Data
        for word in self.data:
            uart3br.send(word) 
        
        # Reset data to nan's, such that sending data is explicit
        self.data = self.nch*[float('nan')]
    
