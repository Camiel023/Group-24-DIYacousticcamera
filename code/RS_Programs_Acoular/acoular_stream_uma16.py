# Readout and analyze UMA16v2 array using sounddevice and acoular
#
# R.Sprik 7/6/2024

import sounddevice       as sd
import acoular           as ac
import matplotlib.pyplot as plt

# from os import path
# import pylab as plt
# from ipywidgets import interact, interactive, fixed, interact_manual
# import ipywidgets as widgets

### define UMA16v2 configuration
print(sd.query_devices())
uma16dev = sd.query_devices("UMA16v2")
#uma16dev = sd.query_devices()[0]  #to be able to do something without UMA16
Fs       = 48000
sd.default.samplerate = Fs
sd.default.channels   = 16
sd.default.device     = uma16dev['index']
print(sd.query_devices())

blocksize = 128
npt       = blocksize * 256
dur       = npt/Fs

### Create the scene: a grid to work on and mic positions
grdsz = 0.2; dist = 0.6
rg = ac.RectGrid( x_min=-grdsz, x_max=grdsz, y_min=-grdsz, y_max=grdsz, z=dist, increment = 0.01 )

### array definition
micgeofile = 'uma16array.xml'
print(f"Using microphone file {micgeofile}")
mg = ac.MicGeom( from_file=micgeofile )
# Check: Plot microphone layout
#plt.ion()
plt.plot(mg.mpos[0], mg.mpos[1], 'o')
plt.show()

### Prepare Acoular Beamformer
st = ac.SteeringVector( grid=rg, mics=mg )
print("Preparation ready")

### [place n loop to repeat]
### Collect and process audio data with acoular
ts = ac.SoundDeviceSamplesGenerator(device = uma16dev['index'], numchannels=16, numsamples=npt)
ps = ac.PowerSpectra ( time_data=ts, block_size=blocksize, window='Rectangular' )
bb = ac.BeamformerBase( freq_data=ps, steer=st )

"""
# Check: Test read from TimeSamples device with n-blocks
def test_read(ts):
    # ts.numsamples = 1024
    i = 0
    b = 0
    for smp in ts.result(128):
        i+=len(smp)
        b += 1
        # print(smp)
    print("Testread done, %i rows in %i blocks" % (i, b))
test_read(ts)
"""

freq = 3000   # filter frequency
noct = 1      # bandwidth in octave fractions
vmin = 80     # dsiplay range
vmax = 100

### analyze
pm = bb.synthetic( freq, noct )
lm = ac.L_p( pm )

### plot map
plt.imshow( lm.T, origin='lower', vmin=lm.max()*vmin/100, vmax=lm.max()*vmax/100, extent=rg.extend(), interpolation='bicubic')
plt.colorbar()
plt.show()
