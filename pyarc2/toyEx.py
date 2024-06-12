
from pyarc2 import Instrument, find_ids

# low voltage channel (typically grounded)
LOWV = 7
# high voltage channel
HIGHV = 33
# read-out voltage
VREAD = 0.2

# Get the ID of the first available ArC TWO
arc2id = find_ids()[0]

# firmware; shipped with your board
fw = 'arc2fw.bin'

# connect to the board
arc = Instrument(arc2id, fw)

current = arc.read_one(LOWV, HIGHV, VREAD)
print('I = %g A' % current)
