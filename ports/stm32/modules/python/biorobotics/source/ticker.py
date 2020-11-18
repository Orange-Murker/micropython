"""
tic/toc function and a Ticker class
"""

from utime import ticks_us
import micropython
from pyb import Timer
import gc

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

        # Create Timer, but leave callback for until it is started
        self.timer = Timer(self.timer_number, freq=self.freq)

        # Create a reference to the callback wrapper
        # This is necessary to force correct allocation, see ISR documentation
        self.fun_wrap_ref = self.fun_wrap

        self.is_started = False

    def fun_wrap(self, _):
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
            lambda _: micropython.schedule(self.fun_wrap_ref, 0)
        )
        self.is_started = True

    def stop(self):
        """Stop ticker"""
        self.timer.deinit()  # Clears all callbacks
        self.is_started = False
