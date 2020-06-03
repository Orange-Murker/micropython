# Biorobotics hardware timer ISR abstraction
# 
# - Removing the need of explicit tim.callback(micropython.schedule()) etc. garbage
# - Timely garbage collection set on a ticker with GC=Enable
# - Other timer related functions

# Imports
import pyb, micropython, gc, utime

# set mem for inerrupting error messages
micropython.alloc_emergency_exception_buf(100)

# Time measurement function similar to Matlab's tic/toc
# tic();toc() itself takes 6us, excluding the print statements
t0 = 0
def tic():
    global t0
    t0 = utime.ticks_us()

def toc():
    t1 = utime.ticks_us()
    print('Time elapsed [us]: ', '{:,}'.format(t1 - t0))

# Class that takes care of callback/schedule linking and gc.collect()
class ticker:

    # Maybe add list of all defined tickers for lookup which are active
    list = []

    def __init__(self, timer, freq, fun, GC = False):
        self.timer = timer
        self.freq = freq
        self.fun = fun
        # for fun_wrap_ref necessity see ISR part of micropython documentation 
        self.fun_wrap_ref = self.fun_wrap
        self.GC = GC

        self.start()

    def fun_wrap(self, _):
        # Execute the callback function 
        self.fun()
        # Collect garbage if this is the "main" loop
        if self.GC:
            gc.disable()
            gc.collect()

    def start(self):
        # Enable timer at set frequency
        self.timer_instance = pyb.Timer(self.timer, freq = self.freq)
        # Attach callback function wrapper
        # callback() passes one argument, here replaced by _
        # schedule(function, object) must get both argumenbts where object can be anything
        self.timer_instance.callback(lambda _ : micropython.schedule(self.fun_wrap_ref, 0))

    def stop(self):
        self.timer_instance.deinit()




