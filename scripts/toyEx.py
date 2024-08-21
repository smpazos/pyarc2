from pyarc2 import Instrument, find_ids, ReadAt, ReadAfter, \
    IdleMode, DataMode, ControlMode, AuxDACFn, BiasOrder
import numpy as np
import sys
sys.path.insert(0, '../')
import connect2arc

# low voltage channel (typically grounded)
LOWV = 63
# high voltage channel
HIGHV = 47
# read-out voltage
VREAD = 1

if 'arc' in globals():
    print("Arc2 is already connected.")
else:
    print("Connecting to Arc2.")
    arc = connect2arc()

# Set connection from Channels to Header banks
arc.set_control_mode(ControlMode.Header)

# Read a single element
current = arc.read_one(LOWV, HIGHV, VREAD)
print('I = %g A' % current)
resistance = -VREAD/current
print('R = %g Ohm\n\n' % resistance)

data = arc.read_all(VREAD, BiasOrder.Rows)
#print(data)

# Read a full column 16
slicedata16 = arc.read_slice(LOWV, VREAD)
# Read a full column 48
slicedata48 = arc.read_slice(48, VREAD)

# ensure all channels are detached from GND first
arc.connect_to_gnd(np.array([], dtype=np.uint64))
# generate the ramp instruction, do 2 programming pulses
# at each step, then read after each set of 2 pulses (a block)
# at arbitrary voltage (200 mV)
# generate_ramp(low, high, vstart, vstep, vstop, pw[ns], inter[ns], npulse, \
#   readat, readafter, /)
arc.generate_ramp(LOWV, HIGHV, 0.0, 0.1, 1.0, 1000, 10000, 2, \
    ReadAt.Bias, ReadAfter.Block)
arc.generate_ramp(LOWV, HIGHV, 1.0, -0.1, 0, 1000, 10000, 2, \
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


arc.connect_to_gnd([])  # clear grounds
arc.open_channels(list(range(64))) # set channels to open
arc.execute()   

# Comment start
'''# Comment start

# Array of tuples [(channel, voltage), ...] with voltage conf.
# These could easily be the gates of transistors in the array controlled via 
# analog channels in a 64 channel environment of PLCC68D package
config = [(1,1), (2,0), (3,1.5)]
# Configures custom channels to custom voltages, leaving the remainder as they are.
arc.config_channels(config, None)
arc.execute()
 

# the following will set the low and high voltage for selectors to
# 0.0 and 3.3 V respectively and toggle selectors 9 and 12 to high.
arc.config_aux_channels([(AuxDACFn.SELL, 0.0), (AuxDACFn.SELH, 3.3)])
arc.config_selectors([9, 12])
arc.execute()


 
'''# Comment end