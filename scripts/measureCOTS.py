from pyarc2 import Instrument, find_ids, ReadAt, ReadAfter, \
    IdleMode, DataMode, ControlMode, AuxDACFn, BiasOrder
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, '../')
import connect2arc

if 'arc' in globals():
    print("Arc2 is already connected.")
else:
    print("Connecting to Arc2.\n\n")
    arc2id = find_ids()[0]
    # firmware; shipped with your board
    fw = 'efm03_20240918.bin'
    # connect to the board
    arc = Instrument(arc2id, fw)
    arc.finalise_operation(IdleMode.SoftGnd, None)

############ Defining connection environment for the experiment ############
# Generalized read-out voltage
VREAD = 1
all_channels = [i for i in range(64)]
# Channel definitions
# R 100K, _H is for PLUST, _L is for MINUS
# R100K_H = 15
# R100K_L = 31

# R 1K, _H is for PLUST, _L is for MINUS
R1K_H = 47
R1K_L = 63

# R 100K, _H is for PLUST, _L is for MINUS
# R1K_H = 32
# R1K_L = 48

# R 10K, _H is for PLUST, _L is for MINUS
R10K_H = 0
R10K_L = 16

# BS107 gate, source and drain
BS107_G = 54
BS107_D = 32
BS107_S = 48

# TSMC chip gates, sources and drains
TSMC18_G1 = 16
TSMC18_G2 = 17
TSMC18_G3 = 18
TSMC18_G4 = 19
TSMC18_G5 = 20
TSMC18_G6 = 21
TSMC18_G7 = 22
TSMC18_G8 = 23

TSMC18_D1 = 34

TSMC18_S1 = 50

TSMC18_B = 14

############ Connection environment definition complete ############♣


# Set connection from Channels to Header banks
arc.set_control_mode(ControlMode.Header).execute()
# ensure all channels are detached from GND first
# This function connects the array of channels to ground, but disconnects \
# from ground every single channel that is not included in the array. \
# Therefore, if the array is empty, it disconnects every single channel.
arc.connect_to_gnd(np.array([], dtype=np.uint64)).execute()

# Read a single element
# syntax: current = arc.read_one(LOWV, HIGHV, VREAD)
current = arc.read_one(R1K_L, R1K_H, VREAD)
print('I = %g A' % current)
resistance = -VREAD/current
print('R1k = %g Ohm\n\n' % resistance)

# Read a single element
# syntax: current = arc.read_one(LOWV, HIGHV, VREAD)
current = arc.read_one(R10K_L, R10K_H, VREAD)
print('I = %g A' % current)
resistance = -VREAD/current
print('R10k = %g Ohm\n\n' % resistance)

# Read a single element
# syntax: current = arc.read_one(LOWV, HIGHV, VREAD)
# current = arc.read_one(R100K_L, R100K_H, VREAD)
# print('I = %g A' % current)
# resistance = -VREAD/current
# print('R100k = %g Ohm\n\n' % resistance)

# data = arc.read_all(VREAD, BiasOrder.Rows)
#print(data)
all_gates = [TSMC18_G1, TSMC18_G2, TSMC18_G3, TSMC18_G4, TSMC18_G5, TSMC18_G6, TSMC18_G7, TSMC18_G8, TSMC18_B]
arc.connect_to_gnd(all_gates).execute()
# Array of tuples [(channel, voltage), ...] with voltage conf.
# These could easily be the gates of transistors in the array controlled via 
# analog channels in a 64 channel environment of PLCC68D package
config = [(BS107_G,0)]
# Configures custom channels to custom voltages, leaving the remainder as they are.
arc.config_channels(config, None).execute()
config = [(BS107_S,0)]
# Configures custom channels to custom voltages, leaving the remainder as they are.
arc.config_channels(config, None).execute()
config = [(BS107_D,0.010)]
# Configures custom channels to custom voltages, leaving the remainder as they are.
arc.config_channels(config, None).execute()

voltage_read = arc.vread_channels([BS107_G],True)
print('BS107 gate voltage VG = %g' % voltage_read[0])
voltage_read = arc.vread_channels([BS107_S],True)
print('BS107 source voltage VS = %g' % voltage_read[0])
voltage_read = arc.vread_channels([BS107_D],True)
print('BS107 source voltage VD = %g\n\n' % voltage_read[0])
voltages_read = arc.vread_channels(all_channels,True)

Vmax = 3
Vstep = 0.1
countmax = int(Vmax/Vstep)
sweep = [i for i in range(countmax+1)]
sweep = np.array(sweep)*Vstep
bwsweep = np.flip(sweep)
sweep = np.append(sweep,bwsweep[1:])

result = []
for appV in sweep:
    config = [(BS107_G,appV)]
    # Configures custom channels to custom voltages, leaving the remainder as they are.
    arc.config_channels(config, None).execute()
    current = arc.read_slice_open([BS107_D],False)
    # arc.read_slice_open_deferred([BS107_D],False)
    # print(appV)
    print('I_BS107 = %g A' % current[BS107_D])
    result.append(current[BS107_D])
    # currdata = current(34)
 
# for datum in arc.get_iter(DataMode.Bits):
#     aux = datum[0];
#     dato = aux[15];
#     datum
#     # print('I_BS107 = %g A' % dato)
#     result.append(dato)
    
# Read a single element. It grounds all other channels!
# syntax: current = arc.read_one(LOWV, HIGHV, VREAD)
# current = arc.read_one(BS107_S, BS107_D, VREAD)

# resistance = -VREAD/current[BS107_D]
# print('R_BS107 = %g Ohm\n\n' % resistance)

voltage_read = arc.vread_channels([BS107_G],True)
print('BS107 gate voltage VG = %g\n\n' % voltage_read[0])

arc.finalise_operation(IdleMode.SoftGnd)
# arc.execute()

fig = plt.figure()
ax = fig.add_subplot(111)
line1, = ax.semilogy(sweep,abs(np.array(result)), 'b-')
ax.relim() 
ax.autoscale_view(True,True,True)
fig.canvas.draw()
fig.canvas.flush_events()

##################### Ramp ID-VG on TSMC transistor #####################
 # Array of tuples [(channel, voltage), ...] with voltage conf.
# These could easily be the gates of transistors in the array controlled via 
# analog channels in a 64 channel environment of PLCC68D package
all_gates_butG1 = [TSMC18_G2, TSMC18_G3, TSMC18_G4, TSMC18_G5, TSMC18_G6, TSMC18_G7, TSMC18_G8]
arc.connect_to_gnd(all_gates_butG1).execute()
# arc.connect_to_gnd(np.array([], dtype=np.uint64)).execute()

config = [(TSMC18_B,0), (TSMC18_G1,0), (TSMC18_S1,0), (TSMC18_D1,0)]
# Configures custom channels to custom voltages, leaving the remainder as they are.
arc.config_channels(config, None).execute()
# config = [(TSMC18_G,0)]
# # Configures custom channels to custom voltages, leaving the remainder as they are.
# arc.config_channels(config, None).execute()
# config = [(TSMC18_S,0)]
# # Configures custom channels to custom voltages, leaving the remainder as they are.
# arc.config_channels(config, None).execute()
# config = [(TSMC18_D,0.010)]
# # Configures custom channels to custom voltages, leaving the remainder as they are.
# arc.config_channels(config, None).execute()

arc.connect_to_gnd([TSMC18_B]).execute()

voltage_read = arc.vread_channels([TSMC18_B],True)
print('TSMC gate voltage VB = %g' % voltage_read[0])
voltage_read = arc.vread_channels([TSMC18_G1],True)
print('TSMC gate voltage VG = %g' % voltage_read[0])
voltage_read = arc.vread_channels([TSMC18_S1],True)
print('TSMC source voltage VS = %g' % voltage_read[0])
voltage_read = arc.vread_channels([TSMC18_D1],True)
print('TSMC source voltage VD = %g\n\n' % voltage_read[0])
voltages_read = arc.vread_channels(all_channels,True)


Vmax = 1
Vstep = 0.01
countmax = int(Vmax/Vstep)
sweep = [i for i in range(countmax+1)]
sweep = np.array(sweep)*Vstep
bwsweep = np.flip(sweep)
sweep = np.append(sweep,bwsweep[1:])

result = []
for appV in sweep:
    config = [(TSMC18_D1,appV)]
    # Configures custom channels to custom voltages, leaving the remainder as they are.
    arc.config_channels(config, None).execute()
    current = arc.read_slice_open([TSMC18_D1],False)
    # arc.read_slice_open_deferred([BS107_D],False)
    # print(appV)
    print('I_TSMC18 = %g A' % current[TSMC18_D1])
    result.append(current[TSMC18_D1])
    # currdata = current(34)
 
# for datum in arc.get_iter(DataMode.Bits):
#     aux = datum[0];
#     dato = aux[15];
#     datum
#     # print('I_BS107 = %g A' % dato)
#     result.append(dato)
    
# Read a single element. It grounds all other channels!
# syntax: current = arc.read_one(LOWV, HIGHV, VREAD)
# current = arc.read_one(BS107_S, BS107_D, VREAD)

# resistance = -VREAD/current[BS107_D]
# print('R_BS107 = %g Ohm\n\n' % resistance)

voltage_read = arc.vread_channels([TSMC18_G1],True)
print('TSMC G1 gate voltage VG = %g' % voltage_read[0])

arc.finalise_operation(IdleMode.SoftGnd)
# arc.execute()

line2, = ax.semilogy(sweep,abs(np.array(result)), 'r-')
ax.relim() 
ax.autoscale_view(True,True,True)
fig.canvas.draw()
fig.canvas.flush_events()


# Comment start
'''# Comment start
##################### Ramp I-Vs on each component #####################
# ensure all channels are detached from GND first
# This function connects the array of channels to ground, but disconnects \
# from ground every single channel that is not included in the array. \
# Therefore, if the array is empty, it disconnects every single channel.
arc.connect_to_gnd(np.array([], dtype=np.uint64)).execute()

# generate the ramp instruction, do 2 programming pulses
# at each step, then read at pulse voltage every 2 pulses (a block)
# See syntax below:
# generate_ramp(low, high, vstart, vstep, vstop, pw[ns], inter[ns], npulse, \
#   readat, readafter, /)
arc.generate_ramp(R100K_L, R100K_H, 0.0, 0.1, 1.0, 1000, 10000, 1, \
    ReadAt.Bias, ReadAfter.Block)
arc.generate_ramp(R100K_L, R100K_H, 1.0, -0.1, 0, 1000, 10000, 1, \
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
result = []
voltage = []
for datum in arc.get_iter(DataMode.Bits):
    # datum now holds all the wordline currents. However
    # since only channel 0 is selected all other values
    # are NaN
    count = count + 1
    aux = datum[0];
    dato = aux[15];
    print(dato)
    result.append(dato)
    count = count + 1
    voltage.append(count*0.01)

fig = plt.figure()
ax = fig.add_subplot(111)
line1, = ax.plot(voltage,result, 'r-')
ax.relim() 
ax.autoscale_view(True,True,True)
fig.canvas.draw()
fig.canvas.flush_events()
    # (32, )
    # ...
    
print('Finished resistor I-V curve...\n\n')



##################### Ramp I-V on transistor #####################
# ensure all channels are detached from GND first
# This function connects the array of channels to ground, but disconnects \
# from ground every single channel that is not included in the array. \
# Therefore, if the array is empty, it disconnects every single channel.
# arc.connect_to_gnd(np.array([], dtype=np.uint64))

# Array of tuples [(channel, voltage), ...] with voltage conf.
# These could easily be the gates of transistors in the array controlled via 
# analog channels in a 64 channel environment of PLCC68D package
config = [(BS107_G,2)]
# Configures custom channels to custom voltages, leaving the remainder as they are.
arc.config_channels(config, None).execute()

# generate the ramp instruction, do 2 programming pulses

voltage_read = arc.vread_channels([BS107_G],True)
print('BS107 gate voltage pre-sweep VG = %g\n\n' % voltage_read[0])
voltages_read = arc.vread_channels(all_channels,True)
# wait = input("Gate voltage has been applied, press Enter to continue.\n\n")   


# at each step, then read at pulse voltage every 2 pulses (a block)
# NOTE: Ramp instructions GROUND ALL OTHER CHANNELS!
# See syntax below:
# generate_ramp(low, high, vstart, vstep, vstop, pw[ns], inter[ns], npulse, \
#   readat, readafter, /)
Vmax = 0.4
Vstep = 0.01
countmax = Vmax/Vstep
arc.generate_ramp(BS107_S, BS107_D, 0.0, Vstep, Vmax, 1000000, 1000000, 1, \
    ReadAt.Bias, ReadAfter.Block)
arc.generate_ramp(BS107_S, BS107_D, Vmax, -Vstep, 0, 1000000, 1000000, 1, \
    ReadAt.Bias, ReadAfter.Block)
 
arc.execute()

voltage_read = arc.vread_channels([BS107_G],True)
print('BS107 gate voltage post-sweep VG = %g\n\n' % voltage_read[0])
voltages_read = arc.vread_channels(all_channels,True)
    
arc.connect_to_gnd([])  # clear grounds
arc.open_channels(list(range(64))) # set channels to open
# then switch all channels back to GND
# This will likely turn off the Gate channels as well
arc.finalise_operation(IdleMode.SoftGnd, None)
arc.execute()

# the ramp is now being applied...
# start picking the data, we will read the wordline values as
# channel 22 is a word channel. `get_iter` will return an
# iterator on the internal output buffer which will block until
# either a new result is in or the operation has finished (and
# in that case the loop will break)
count = 0
result = []
voltage = []
for datum in arc.get_iter(DataMode.Bits):
    # datum now holds all the wordline currents. However
    # since only channel 0 is selected all other values
    # are NaN
    count = count + 1
    aux = datum[0];
    dato = aux[16];
    print(dato)
    result.append(dato)
    # count = count + 1
    appV = count*0.01
    if appV > Vmax:
        appV = Vmax-(count-countmax)*Vstep
    voltage.append(appV)
    
    # (32, )
    # ...
    
fig = plt.figure()
ax = fig.add_subplot(111)
line1, = ax.plot(voltage,result, 'r-')
ax.relim() 
ax.autoscale_view(True,True,True)
fig.canvas.draw()
fig.canvas.flush_events()


# arc.execute()   


 
'''# Comment end