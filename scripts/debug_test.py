import sys
import pyarc2

all_channels = [i for i in range(64)]

# open file for results
output_file = open("debug_output_osc.txt","w")

# list connected instruments
ids = pyarc2.find_ids()

# end script if nothing is connected
if len(ids) == 0:
    output_file.close()
    sys.exit("error: no instrument found")

# load firmware
arc = pyarc2.Instrument(ids[0], 'efm03_20240418.bin')
arc.finalise_operation(pyarc2.IdleMode.SoftGnd)

# set the header pins as connected if 32NNA68 is connected
arc.set_logic(1).execute()

# set and read a series of arbitrary voltages
arc.config_channels([],0).execute()
voltage = arc.vread_channels(all_channels,True)
output_file.write(str(voltage))
output_file.write("\n\n")
arc.config_channels([],2.5).execute()
voltage = arc.vread_channels(all_channels,True)
output_file.write(str(voltage))
output_file.write("\n\n")
arc.config_channels([],-2.5).execute()
voltage = arc.vread_channels(all_channels,True)
output_file.write(str(voltage))
output_file.write("\n\n")
arc.config_channels([],5).execute()
voltage = arc.vread_channels(all_channels,True)
output_file.write(str(voltage))
output_file.write("\n\n")
arc.config_channels([],-5).execute()
voltage = arc.vread_channels(all_channels,True)
output_file.write(str(voltage))
output_file.write("\n\n")

output_file.write("\n\n")

# set a series of arbitrary voltages and read currenst at those references
arc.config_channels([],0).execute()
current = arc.read_slice_open(all_channels,False)
output_file.write(str(current))
output_file.write("\n\n")
arc.config_channels([],0.5).execute()
current = arc.read_slice_open(all_channels,False)
output_file.write(str(current))
output_file.write("\n\n")
arc.config_channels([],-0.5).execute()
current = arc.read_slice_open(all_channels,False)
output_file.write(str(current))
output_file.write("\n\n")
arc.config_channels([],1).execute()
current = arc.read_slice_open(all_channels,False)
output_file.write(str(current))
output_file.write("\n\n")
arc.config_channels([],-1).execute()
current = arc.read_slice_open(all_channels,False)
output_file.write(str(current))
output_file.write("\n\n")

# end script
output_file.close()
quit("script complete")