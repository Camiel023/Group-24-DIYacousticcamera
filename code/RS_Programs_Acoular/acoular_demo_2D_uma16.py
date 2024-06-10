"""
Demo for Acoular analysis using a MiniDSP UMA16v2 array

Generates a test data set for sources, analyzes and calculates a map.

The simulation generates the sound pressure at 16 microphones in the 'UMA16' geometry.
The sound pressure signals are sampled at 48000 Hz for a duration of 1 second.
Then analyzed with acoular in the frequency domain.

Adapted from acoular demo example
R.Sprik 7/6/2024
"""
import acoular as ac
import matplotlib.pyplot as plt
import numpy as np

### set up the parameters
sfreq      = 48000                       # sample frequency
duration   = 1                           # recording duration in s
nsamples   = duration * sfreq
micgeofile = 'uma16array.xml'            # configuration file of the UMA16v2 array
h5savefile = 'test_sources_uma16.h5'     # outputfile with test data

### define microphone geometry
mg = ac.MicGeom(from_file=micgeofile)

### generate test data and save to 'h5' file ###
# in real life this would come from an array measurement

#noise signal
n1 = ac.WNoiseGenerator(sample_freq=sfreq, numsamples=nsamples, seed=1, rms = 0.1)
n2 = ac.WNoiseGenerator(sample_freq=sfreq, numsamples=nsamples, seed=4, rms = 0.1)
n3 = ac.WNoiseGenerator(sample_freq=sfreq, numsamples=nsamples, seed=3, rms = 0.0)

#sine wave signal
fdel = 3.0
fsrc1 = 4000.0-fdel; fsrc2 = fsrc1+2*fdel #not exactly the same frequency to avoid interference
s1 = ac.SineGenerator(freq = fsrc1, sample_freq=sfreq, numsamples=nsamples, amplitude = 0.1)
s2 = ac.SineGenerator(freq = fsrc2, sample_freq=sfreq, numsamples=nsamples, amplitude = 0.1)

###  Generate test signal 
# two seperated sine sources with a noise source in the middle
# amplitudes set by rms value
sep  = 0.2 # seperated sine sources
dist = 0.3
p1 = ac.PointSource(signal=s1, mics=mg, loc=(-sep/2,    0, dist))
p2 = ac.PointSource(signal=s2, mics=mg, loc=( sep/2,    0, dist))
p3 = ac.PointSource(signal=n3, mics=mg, loc=(     0,  0.0, dist))
# mix and save
pa = ac.SourceMixer(sources=[p1, p2, p3])
wh5 = ac.WriteH5(source=pa, name=h5savefile)
wh5.save()

##### analyze the data on the test file and generate map #####
ts = ac.TimeSamples(name=h5savefile)
ps = ac.PowerSpectra(time_data=ts, block_size=128, window='Hanning')

# pixel grid to analyze
grsz = 0.75 # grid extend
rg = ac.RectGrid(x_min=-grsz, x_max=grsz, y_min=-grsz, y_max=grsz, z=dist, increment=0.005)
st = ac.SteeringVector(grid=rg, mics=mg)

# Beamforming using the basic delay-and-sum algorithm in the frequency domain.
bb  = ac.BeamformerBase(freq_data=ps, steer=st)
# others: (choose by uncommenting the line)
#bb = ac.BeamformerEig(freq_data=ps, steer=st)

# response filtered around fsrc with a bandwith a fraction of an octave
ffilt = 1.0*(fsrc1+fsrc2)/2; noct = 5 #narrow band with freq. offset
pm = bb.synthetic(ffilt, noct)

# Calculate the sound pressure level from the squared sound pressure in dB.
Lm = ac.L_p(pm)
# show map
plt.figure(10, figsize=(12,6) )
plt.subplot(1,2,1)
plt.imshow(Lm.T, origin='lower', vmax=Lm.T.max(), vmin=Lm.T.max() - 10, extent=rg.extend(), interpolation='bicubic')
plt.colorbar()
plt.title(f"sep={sep}m, dist={dist}m, freq~{(fsrc1+fsrc2)/2}Hz")

plt.subplot(1,2,2)
print(f"map size: {np.shape(Lm.T)}")
midx = int(np.shape(Lm.T)[0]/2)
midy = int(np.shape(Lm.T)[1]/2)
plt.plot(Lm.T[:,midx], 'b-')
plt.plot(Lm.T[midy,:], 'r-')
plt.ylim(Lm.T.max()-6,Lm.T.max()+1)
plt.title("Hor(r), Ver(g) section through map (0,0)")
plt.xlabel("Grid index")
plt.ylabel("Signal (dB)")
plt.show()

# done

# plot microphone geometry
plt.figure(20)
plt.plot(mg.mpos[0], mg.mpos[1], 'o')
plt.axis('equal')
plt.title("UMA16 layout")
plt.xlabel("X")
plt.ylabel("Y")

plt.show()
