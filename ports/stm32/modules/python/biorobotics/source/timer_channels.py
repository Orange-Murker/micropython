"""
Contains a mapping from pins to timers and channels, and a list of available
hardware timers

See the Nucleo pinout:
https://os.mbed.com/platforms/ST-Nucleo-H743ZI2/#board-pinout
"""

# Point pin name to `(timer #, channel #)`
# STM pin names (the blue labels) are used, *not* Arduino pin names, because
# those are the result of pin.name()
# Channels that are marked 'inverted' are disabled
PINS_TO_TIMERS = {
    'A3': (2, 4),
    # 'B1': (1, 3),  # Inverted
    'E9': (1, 1),
    'C8': (3, 3),
    'C9': (3, 4),
    # 'E4': (15, 1),  # Inverted
    'E5': (15, 1),
    'E6': (15, 2),
    'F8': (13, 1),
    'F7': (17, 1),
    'F9': (14, 1),
    'C6': (3, 1),
    # 'B15': (1, 3),  # Inverted
    'C7': (3, 2),
    'B5': (3, 2),
    'B4': (3, 1),
    'F6': (16, 1),
    'D13': (4, 2),
    'D12': (4, 1),
    'A0': (2, 1),
    'B8': (4, 3),
    'B9': (4, 4),
    'A5': (2, 1),
    'A6': (3, 1),
    # 'B5': (3, 2),  # Duplicate pin
    'D14': (4, 3),
    'D15': (4, 4),
    # 'E9': (1, 1),  # Duplicate pin
    'E11': (1, 2),
    'E14': (1, 4),
    'E13': (1, 3),
    'B6': (4, 1),
    'B7': (4, 2),
    # 'E8': (1, 1),  # Inverted
    # 'E10': (1, 2),  # Inverted
    # 'E12': (1, 3),  # Inverted
    # 'E6': (15, 2),  # Duplicate pin
    'B10': (2, 3),
    'B11': (2, 4),
    # 'F6': (16, 1),  # Duplicate pin
    # 'F7': (17, 1),  # Duplicate pin
    'A15': (2, 1),
    # 'B7': (4, 2),  # Duplicate pin
    # 'A0': (2, 1),  # Duplicate pin
    'A1': (2, 2),
    # 'B0': (1, 2),  # Inverted
    'E4': (15, 1),  # Inverted
    # 'E5': (15, 1),  # Duplicate pin
    # 'F8': (13, 1),  # Duplicate pin
    # 'F9': (14, 1),  # Duplicate pin
    # 'E6': (15, 2),  # Duplicate pin
    # 'C9': (3, 4),  # Duplicate pin
    # 'B8': (4, 3),  # Duplicate pin
    # 'B9': (4, 4),  # Duplicate pin
    # 'A5': (2, 1),  # Duplicate pin
    # 'A7': (1, 1),  # Inverted
    # 'B6': (14, 1),  # Duplicate pin
    # 'C7': (3, 2),  # Duplicate pin
    'A9': (1, 2),
    'A8': (1, 1),
    # 'B10': (2, 3),  # Duplicate pin
    # 'B4': (3, 1),  # Duplicate pin
    # 'B5': (3, 2),  # Duplicate pin
    'B3': (2, 2),
    'A10': (1, 3),
    'A2': (2, 3),
    # 'A3': (2, 4),  # Duplicate pin
    # 'D13': (4, 2),  # Duplicate pin
    # 'D12': (4, 1),  # Duplicate pin
    # 'D10': (1, 2),  # Inverted
    # 'E12': (1, 3),  # Inverted
    # 'E14': (1, 4),  # Duplicate pin
    # 'E13': (1, 3),  # Duplicate pin
    # 'C8': (3, 3),  # Duplicate pin
    # 'C6': (3, 1),  # Duplicate pin
    'A11': (1, 4),
    # 'B11': (2, 4),  # Duplicate pin
    # 'B1': (1, 3),  # Inverted
    # 'B15': (1, 3),  # Inverted
    # 'B14': (1, 2),  # Inverted
    # 'B13': (1, 1),  # Inverted
    # 'E8': (1, 1),  # Inverted
    # 'D14': (4, 3),  # Duplicate pin
    # 'D15': (4, 4),  # Duplicate pin
    # 'E9': (1, 1),  # Duplicate pin
    # 'E11': (1, 2)  # Duplicate pin
}
