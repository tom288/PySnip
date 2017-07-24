"""
Day night cycle implemented using continuous changes to the fog
Fully compatible with disco
RGB interpolation is used, which is ugly if the night sky is not black
"""

import math

from twisted.internet.task import LoopingCall

import commands

COL_DAY = (68, 138, 255) # Blue daytime sky
COL_NIGHT = (0, 0, 0) # Black night sky
DAY_SECS = 60 * 15 # Real-life seconds per in-game day
DAY_TICKS = 1024 # Ticks per in-game day, powers of 2 avoid rounding errors

@commands.name('starttime') # Begin the day night cycle
@commands.admin
def start_time(connection):
    if (connection.protocol.day_enable):
        return ('Time is already running')
    else:
        connection.protocol.day_enable = True
        return ('Time has been started')
commands.add(start_time)

@commands.name('stoptime') # Pause the day night cycle
@commands.alias('pausetime')
@commands.admin
def stop_time(connection):
    if (connection.protocol.day_enable):
        connection.protocol.day_enable = False
        return ('Time has been stopped')
    else:
        return ('Time is already stopped')
commands.add(stop_time)

@commands.name('toggletime') # Toggle the day night cycle
@commands.admin
def toggle_time(connection):
    connection.protocol.day_enable = not connection.protocol.day_enable
    if (connection.protocol.day_enable):
        return ('Time has been started')
    else:
        return ('Time has been stopped')
commands.add(toggle_time)

@commands.name('whattime') # Get the time printed in chat
@commands.alias('gettime')
def what_time(connection):
    h = int(connection.protocol.day_hours)
    return('The time is {}:{:0>2} {}'.format(
        h - 12 if h > 12 else h,
        int(connection.protocol.day_hours * 60 % 60),
        'AM' if h < 12 else 'PM'))
commands.add(what_time)

@commands.name('settime') # Set the time to X:00 in 24h time
@commands.admin
def set_time(connection, t = None):
    if (not t):
        return ('Specify the number of hours to set the time to ' \
            'e.g. /settime 16 to set the time to 4 PM')
    if (not t.isdecimal() or int(t) < 0 or int(t) > 23):
        return ('You must specify a whole number of hours between 0 and 23')
    connection.protocol.day_hours = int(t)
    connection.protocol.day_enable = True # Reduces complexity of time_tick
    connection.protocol.time_tick()
    return ('Set the time to ' + str(t) + ':00')
commands.add(set_time)

def apply_script(protocol, connection, config):
    class DayProtocol(protocol):
        def __init__(self, *arg, **kw): # Load the plugin
            protocol.__init__(self, *arg, **kw)
            self.day_hours = 12.0
            self.day_enable = True
            self.day_loop = LoopingCall(self.time_tick)
            self.day_loop.start(DAY_SECS / float(DAY_TICKS))

        def time_tick(self): # Cycle between day and night
            if (hasattr(self, 'disco') and self.disco or not self.day_enable):
                return
            self.day_hours += 24.0 / float(DAY_TICKS)
            if (self.day_hours >= 12.0
            and self.day_hours - 24.0 / DAY_TICKS < 12.0):
                self.send_chat('It is now midday')
            if (self.day_hours >= 24.0):
                self.day_hours -= 24.0
                self.send_chat('It is now midnight')
            n = (math.sin((self.day_hours-6.0)/12.0*math.pi)+1.0) / 2.0
            self.set_fog_color(self.lerp_color(COL_DAY, COL_NIGHT, n))

        def lerp_color(self, a, b, n): # RGB colour interpolation
            r = []
            for i in range(len(a)):
                r.append(int(round(a[i]*n+b[i]*(n-1))))
            return tuple(r)

    return DayProtocol, connection
