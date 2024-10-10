from pyarc2 import Instrument, find_ids, ReadAt, ReadAfter, \
    IdleMode, DataMode, ControlMode, AuxDACFn, BiasOrder
import numpy as np
import matplotlib.pyplot as plt
# import sys
# sys.path.insert(0, '../')
# import connect2arc
# import time
from datetime import datetime
import os
import csv

now = datetime.now()
onlydate = now.strftime("%Y-%m-%d")
onlytime = now.strftime("%H%M%S")
outputs_dir = 'C:\\measurements\\'+onlydate+'\\'+onlytime+'\\arC_outputs\\'
os.makedirs(outputs_dir, exist_ok=True)

if 'arc' in globals():
    print("Arc2 is already connected.")
else:
    print("Connecting to Arc2.\n\n")
    arc2id = find_ids()[0]
    # firmware; shipped with your board
    fw = 'efm03_20220905.bin'
    # connect to the board
    arc = Instrument(arc2id, fw)
    arc.finalise_operation(IdleMode.SoftGnd, None)

############ Defining connection environment for the experiment ############
# Generalized read-out voltage
VREAD = 0.1
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

# TSMC chip gates, connected to Selector lines 4-27 in 32SLP48DIP board
TSMC18_G1 = 4   # Selector channel connected to G1 with jumper
TSMC18_G2 = 17
TSMC18_G3 = 18
TSMC18_G4 = 19
TSMC18_G5 = 20
TSMC18_G6 = 21
TSMC18_G7 = 22
TSMC18_G8 = 23

all_sel = [TSMC18_G1, TSMC18_G2, TSMC18_G3, TSMC18_G4, TSMC18_G5, TSMC18_G6, TSMC18_G7, TSMC18_G8]

# Analogue channel nuimbers connected to transistors' D, S, and B
TSMC18_D5 = 34
TSMC18_D7 = 36
TSMC18_D8 = 38

TSMC18_S5 = 50
TSMC18_S7 = 52
TSMC18_S8 = 57

TSMC18_B = 14

############ Connection environment definition complete ############♣


# Set connection from Channels to Header banks
# arc.set_control_mode(ControlMode.Header).execute()
# ensure all channels are detached from GND first

# This function connects the array of channels to ground, but disconnects \
# from ground every single channel that is not included in the array. \
# Therefore, if the array is empty, it disconnects every single channel.
arc.connect_to_gnd(np.array([], dtype=np.uint64)).execute()

# Configure Selector line voltages, current source and Arbitrary supply
# arc.config_aux_channels([(AuxDACFn.SELL, 0), (AuxDACFn.SELH, 0.3), ...
#                          (AuxDACFn.CREF, 6), (AuxDACFn.CSET, 5), ...
#                          (AuxDACFn.ARB1, 0), (AuxDACFn.ARB2, 0)])
# Configure Selector line voltages low and high
arc.config_aux_channels([(AuxDACFn.SELL, 0), (AuxDACFn.SELH, 0.3)])

##################### Ramp ID-VD on TSMC transistor #####################
 # Array of tuples [(channel, voltage), ...] with voltage conf.
# These could easily be the gates of transistors in the array controlled via 
# analog channels in a 64 channel environment of PLCC68D package
arc.connect_to_gnd(np.array([], dtype=np.uint64)).execute()


config = [(TSMC18_B,0), (TSMC18_S8,0), (TSMC18_D8,0)]
# Configures custom channels to custom voltages, leaving the remainder as they are.
arc.config_channels(config, None).execute()

# Configure the voltage sweep lists
Vmax = 3.5
Vstep = 0.01
countmax = int(Vmax/Vstep)
sweep = [i for i in range(countmax+1)]
sweep = np.array(sweep)*Vstep
bwsweep = np.flip(sweep)
sweep = np.append(sweep,bwsweep[1:])

# Turn on listed selector lines to configured selector HIGH voltage
arc.config_selectors([TSMC18_G1])

# Sweep voltage point-by-point in a ladder fashion and read crrent at each step
result = []
for appV in sweep:
    config = [(TSMC18_D8,appV)]
    # Configures custom channels to custom voltages, leaving the remainder as they are.
    arc.config_channels(config, None).execute()
    current = arc.read_slice_open([TSMC18_D8],False)
    # arc.read_slice_open_deferred([BS107_D],False)
    # print(appV)
    print('I_TSMC18 = %g A' % current[TSMC18_D8])
    result.append(current[TSMC18_D8])
    # currdata = current(34)

# Set all channels back to 0V in case the sweep does not go back to 0V    
config = [(TSMC18_B,0), (TSMC18_S8,0), (TSMC18_D8,0)]
# Configures custom channels to custom voltages, leaving the remainder as they are.
arc.config_channels(config, None).execute()
# Turn OFF ALL selector lines [empty list]
arc.config_selectors([])

# Connect all channels to ground upon finalising
arc.finalise_operation(IdleMode.SoftGnd)
arc.execute()

# Plot results (creates figure if none is available, otherwise hold ON)
current_read = abs(np.array(result))
if 'fig' not in globals():
    fig = plt.figure()
    ax = fig.add_subplot(111)
line2, = ax.semilogy(sweep,current_read, 'b-')
ax.relim() 
ax.autoscale_view(True,True,True)
fig.canvas.draw()
fig.canvas.flush_events()

# Save results to csv file
resultFile = open(outputs_dir+'I-V_VG='+str(TSMC18_G8)+'.csv','w',newline='')
csv_out = csv.writer(resultFile)
# print("VD, ID",file = resultFile)
csv_out.writerow(['VD','ID'])
aux = zip(sweep,current_read)
table = np.array(list(aux))
for row in table:
        csv_out.writerow(row)
        # print(row, file = resultFile)
resultFile.close()

##################### Fast Ramp I-V on transistor #####################

# Turn on listed selector lines to configured selector HIGH voltage
arc.config_selectors([TSMC18_G1])

# generate the ramp instruction
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

# Turn OFF ALL selector lines [empty list]
arc.config_selectors([])
   
fig = plt.figure()
ax = fig.add_subplot(111)
line1, = ax.plot(voltage,result, 'r-')
ax.relim() 
ax.autoscale_view(True,True,True)
fig.canvas.draw()
fig.canvas.flush_events()

####### Perform a readAll operation after turning on all the selectors ########
# Turn ON ALL selector lines [empty list]
arc.config_selectors(all_sel)
data = arc.read_all(VREAD, BiasOrder.Rows)
print(data)

# Turn OFF ALL selector lines [empty list]
arc.config_selectors([])

# Float all channels before finalizing
arc.connect_to_gnd([])  # clear grounds
arc.open_channels(list(range(64))) # set channels to open
arc.execute()
 
# Comment start
'''# Comment start


# arc.execute()   
'''# Comment end