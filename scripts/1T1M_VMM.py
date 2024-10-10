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
G1 = 4   # Selector channel connected to G1 with jumper
G2 = 17
G3 = 18
G4 = 19
G5 = 20
G6 = 21
G7 = 22
G8 = 23

all_sel = [G1, G2, G3, G4, G5, G6, G7, G8]

# Analogue channel nuimbers connected to transistors' D, S, and B
WL0 = 34
WL1 = 36
WL2 = 38
all_WL = [WL0, WL1, WL2]

BL0 = 50
BL1 = 52
BL2 = 57
all_BL = [BL0, BL1, BL2]
gnd_allBL = [(BL0,0), (BL1,0), (BL2,0)]
# gnd_allBL = [(BL0,0), (BL1,0), (BL2,0), (BL3,0), (BL4,0), (BL5,0), (BL6,0), (BL7,0)]

GNDTAP = 14

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

####### Perform a readAll operation after turning on all the selectors ########
# Turn ON ALL selector lines [empty list]
arc.config_selectors(all_sel)

data = [0.1, 0, 0.1, 0]
config = [(WL0,data(0)), (WL1,data(1)), (WL2,data(2))]
# Configures custom channels to custom voltages, leaving the remainder as they are.
arc.config_channels(config, None).execute()
# Configures custom channels to custom voltages, leaving the remainder as they are.
arc.config_channels(gnd_allBL, None).execute()

#data = arc.read_all(VREAD, BiasOrder.Rows)
data = arc.read_slice_open(all_BL, False)
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