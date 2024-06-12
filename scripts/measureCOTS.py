from pyarc2 import Instrument, find_ids, ReadAt, ReadAfter, \
    IdleMode, DataMode, ControlMode, AuxDACFn, BiasOrder
import numpy as np
import sys
sys.path.insert(0, '../')
import connect2arc

try:
    arc
except NameError:
    arc = connect2arc()

############ Defining connection environment for the experiment ############
# Generalized read-out voltage
VREAD = 1
# Channel definitions
# R 1K, _H is for PLUST, _L is for MINUS
R1K_H = 32
R1K_L = 48

# R 10K, _H is for PLUST, _L is for MINUS
R1K_H = 0
R1K_L = 16

# R 100K, _H is for PLUST, _L is for MINUS
R1K_H = 15
R1K_L = 31

# R 1M, _H is for PLUST, _L is for MINUS
R1K_H = 47
R1K_L = 63

# BS107 gate, source and drain
BS107_G = 55
BS107_S = 58
BS107_D = 56
############ Connection environment definition complete ############♣


# Set connection from Channels to Header banks
arc.set_control_mode(ControlMode.Header)

# Read a single element
# syntax: current = arc.read_one(LOWV, HIGHV, VREAD)
current = arc.read_one(R1K_L, R1K_H, VREAD)
print('I = %g A' % current)
resistance = -VREAD/current
print('R = %g Ohm\n\n' % resistance)

data = arc.read_all(VREAD, BiasOrder.Rows)
#print(data)



##################### Ramp I-Vs on each component #####################
# ensure all channels are detached from GND first
# This function connects the array of channels to ground, but disconnects \
# from ground every single channel that is not included in the array. \
# Therefore, if the array is empty, it disconnects every single channel.
arc.connect_to_gnd(np.array([], dtype=np.uint64))

# generate the ramp instruction, do 2 programming pulses
# at each step, then read at pulse voltage every 2 pulses (a block)
# See syntax below:
# generate_ramp(low, high, vstart, vstep, vstop, pw[ns], inter[ns], npulse, \
#   readat, readafter, /)
arc.generate_ramp(R1K_L, R1K_H, 0.0, 0.01, 1.0, 1000, 10000, 2, \
    ReadAt.Bias, ReadAfter.Block)
arc.generate_ramp(R1K_L, R1K_H, 1.0, -0.01, 0, 1000, 10000, 2, \
    ReadAt.Bias, ReadAfter.Block)

# then switch all channels back to GND
# This will likely turn off the Gate channels as well
arc.finalise_operation(IdleMode.SoftGnd)

# and submit it for execution
arc.execute()
# the ramp is now being applied...
# start picking the data, we will read the wordline values as
# channel 22 is a word channel. `get_iter` will return an
# iterator on the internal output buffer which will block until
# either a new result is in or the operation has finished (and
# in that case the loop will break)
count = 0
for datum in arc.get_iter(DataMode.Bits):
    # datum now holds all the wordline currents. However
    # since only channel 0 is selected all other values
    # are NaN
    aux = datum[0];
    dato = aux[0];
    print(dato)
    count = count + 1
    # (32, )
    # ...


##################### Ramp I-V on transistor #####################
# ensure all channels are detached from GND first
# This function connects the array of channels to ground, but disconnects \
# from ground every single channel that is not included in the array. \
# Therefore, if the array is empty, it disconnects every single channel.
arc.connect_to_gnd(np.array([], dtype=np.uint64))

# Array of tuples [(channel, voltage), ...] with voltage conf.
# These could easily be the gates of transistors in the array controlled via 
# analog channels in a 64 channel environment of PLCC68D package
config = [(BS107_G,2)]
# Configures custom channels to custom voltages, leaving the remainder as they are.
arc.config_channels(config, None)

# generate the ramp instruction, do 2 programming pulses
# at each step, then read at pulse voltage every 2 pulses (a block)
# See syntax below:
# generate_ramp(low, high, vstart, vstep, vstop, pw[ns], inter[ns], npulse, \
#   readat, readafter, /)
arc.generate_ramp(BS107_S, BS107_D, 0.0, 0.01, 2.0, 1000, 10000, 2, \
    ReadAt.Bias, ReadAfter.Block)
arc.generate_ramp(BS107_S, BS107_D, 2.0, -0.01, 0, 1000, 10000, 2, \
    ReadAt.Bias, ReadAfter.Block)

arc.execute()

# the ramp is now being applied...
# start picking the data, we will read the wordline values as
# channel 22 is a word channel. `get_iter` will return an
# iterator on the internal output buffer which will block until
# either a new result is in or the operation has finished (and
# in that case the loop will break)
count = 0
for datum in arc.get_iter(DataMode.Bits):
    # datum now holds all the wordline currents. However
    # since only channel 0 is selected all other values
    # are NaN
    aux = datum[0];
    dato = aux[0];
    print(dato)
    count = count + 1
    # (32, )
    # ...

arc.connect_to_gnd([])  # clear grounds
arc.open_channels(list(range(64))) # set channels to open
arc.execute()   


# Comment start
'''# Comment start
 
'''# Comment end