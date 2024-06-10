"""
Demo for Acoular analysis using a MiniDSP UMA16v2 array

Generates a test data set for 2 or 3 sources, analyzes and generates a map.

Uses a recorded or simulated 'h5' file for the 16 microphones in the 'UMA16' geometry.
The sound pressure signals are sampled at 48000 Hz for a duration of 1 second.

Adapted from acoular demo example
R.Sprik 7/6/2024
"""

import acoular as ac
import matplotlib.pyplot as plt

### set up the array parameters
micgeofile = 'uma16array.xml'              #configuration file of the UMA16v2 array
mg         = ac.MicGeom(from_file=micgeofile)

# plot microphone geometry
plt.figure(10)
plt.plot(mg.mpos[0], mg.mpos[1], 'o')
plt.axis('equal')
plt.title("UMA16 layout")
plt.xlabel("X")
plt.ylabel("Y")

### data file in 'h5' format
h5savefile = 'test_sources_uma16.h5' 

# get data from file
ts = ac.TimeSamples(name=h5savefile)
ps = ac.PowerSpectra(time_data=ts, block_size=128, window='Hanning')

# pixel grid to analyze
grsz = 0.25; dist = 0.6
rg = ac.RectGrid(x_min=-grsz, x_max=grsz, y_min=-grsz, y_max=grsz, z=dist, increment=0.01)
st = ac.SteeringVector(grid=rg, mics=mg)

bb = ac.BeamformerBase(freq_data=ps, steer=st)

# filtered response in a fraction of an octave around ffilt
ffilt = 13000.0; noct = 4
pm = bb.synthetic(ffilt, noct)
Lm = ac.L_p(pm)

# show map
plt.figure(20)
plt.imshow(Lm.T, origin='lower', vmin=Lm.max() - 10, extent=rg.extend(), interpolation='bicubic')
plt.colorbar()
plt.title(f"{h5savefile} at {ffilt}Hz")


plt.show()

