"""
###############################################
#                  UmaCam v.0                 #
###############################################
#
# On Raspberry Pi 5 with Bookworm 64 bit
#
# Take still image with RPi camera
# Readout and analyze UMA16v2 mirophone array
# using 'sounddevice' and 'acoular'
# repeat this 'ntake' times
# 
# files stored for later analysis.
# E.g. with filnmbs = "cap", itake = 1
# - still image      cap1.jpg
# - recorded sound   cap1.h5  if h5store  = True  
# -                  cap1.wav if wavstore = True  
# - map by acoular   cap1.png
#  
# - general log      cap.log
#
# Works on Raspberry Pi 5 with Bookworm
#
# R.Sprik 8/6/2024
"""

import matplotlib.pyplot as plt
import numpy             as np
import os, time

import sounddevice       as sd
import acoular           as ac
import matplotlib.pyplot as plt
import numpy             as np

from picamera2 import Picamera2

### setup RPi camera for still frame capture
print(">>>Initializing RPi camera")
camera = None

def initialize_camera():
    global camera
    camera = Picamera2()
    config = camera.create_still_configuration()
    # config["main"]["size"] = (4608, 2592)
    config["main"]["size"] = (1920, 1440)  #improve: can be smaller to compare with sound map
                                           #         Autofocus ?
    camera.configure(config)
    return(config["main"]["size"])

def capture_single_frame(filename):
    filepath = os.path.expanduser(filename)
    print("capturing frame", filepath)
    camera.start()                          #improve: start, stop and close not needed for repeating calls
    time.sleep(0.5)  
    camera.capture_file(filepath)           #save a file for later
    frame = camera.capture_array()          #capture a frame to work with later on
    camera.stop()
    #camera.close()
    return(frame)
# 
camcfg = initialize_camera()
# filnm = "captest.jpg
# frame = capture_single_frame(filnm)
# plt.imshow(frame)
# plt.title(f"{filnm}")
# plt.show()

### setup UMA16 v2 configuration
print(">>>Initializing UMA16v2")
#print(sd.query_devices())
uma16dev = sd.query_devices("UMA16v2")
Fs       = 44100
sd.default.samplerate = Fs
nchan = 16; sd.default.channels   = nchan
sd.default.device     = uma16dev['index']
print(sd.query_devices())

blocksize = 128
npt       = blocksize * 256
dur       = npt/Fs

##### setup Acoular for beamforming
print(">>>Setup Acoular for UMA16v2")
### Create acoular map grid and mic positions in meters.
grdsz = 0.2; dist = 0.6; inc = 0.01
rg = ac.RectGrid( x_min=-grdsz, x_max=grdsz, y_min=-grdsz, y_max=grdsz, z=dist, increment = inc )

print(f"Grid: extend = {grdsz}m, dist = {dist}m, points: {rg.shape}")

### array definition
micgeofile = 'uma16array.xml'
print(f"Using microphone file {micgeofile}")
mg = ac.MicGeom( from_file=micgeofile )
# Check: Plot microphone layout
#plt.ion()
"""
plt.plot(mg.mpos[0], mg.mpos[1], 'o')
plt.title("UMA16 layout")
plt.show()
"""
### Prepare Acoular steering vectors
st = ac.SteeringVector( grid=rg, mics=mg )
#bb = ac.BeamformerBase( freq_data=ps, steer=st )
print(">>>Preparation ready\n")

### Take still image and collect and process audio data with acoular
# store results on files
ntake = 2
print(f">>>Start {ntake} recordings")
filnmbs  = "cap"

fillog   = f"{filnmbs}.log"
flog = open(fillog, 'w')

def prtlog(message):
    print(message)
    flog.write(message+"\n")

filtfreq = 3000.0; filtoct = 1 # frequency band to use in sound map
ptime    = 1.0                 # pause time after each take

# response on console and on log file for later reference
prtlog(f"{time.ctime(time.time())}: Start")
prtlog(f"Name  : {filnmbs}")
prtlog(f"Image : {camcfg} pixels")
prtlog(f"Audio : {dur}s, Fs = {Fs}Hz")
prtlog(f"Grid  : extend = {grdsz}m, dist = {dist}m, pixels: {rg.shape}")
prtlog(f"Filter: freq = {filtfreq}Hz, BW = {filtoct}")
prtlog(f"ntake : {ntake}")
prtlog(f"pause : {ptime}s")
wavstore = False  # save sound recording in wav format, not for now
h5store  = True   # save sound recording in h5 format for acoular

for itake in range(0,ntake):
    plt.close("all")
    prtlog("{time.ctime()}: take {itake} of {ntake}")
    
    ### frame from camera
    filimg = f"{filnmbs}{itake}.jpg"
    frame = capture_single_frame(filimg)
    plt.figure(10)
    plt.subplot(1,2,1)
    plt.imshow(frame)
    plt.title(f"{filnmbs}{itake}")
    #plt.ion()
    #plt.show()
    #plt.pause(0.01)

    ### sound
    ts = ac.SoundDeviceSamplesGenerator(device = uma16dev['index'], numchannels=16, numsamples=npt)
    if wavstore:
        filsndw  = f"{filnmbs}{itake}.wav" # save in "wav" format
        WV = ac.WriteWAV(source=ts, name=filsndw)
    if h5store:
        filsndh = f"{filnmbs}{itake}.h5"   # save in h5 format for later analysis with acoular
        # ac.tprocess.WriteH5(filsndh)
        wh5 = ac.WriteH5(source=ts, name=filsndh)
        wh5.save()
           
    ### proces
    ps = ac.PowerSpectra (time_data=ts, block_size=blocksize, window='Rectangular')    
    # st = ac.SteeringVector(grid=rg, mics=mg) # known already
    bb = ac.BeamformerBase(freq_data=ps, steer=st)
    
    ### analyze within a frequency band
    freq = filtfreq   # filter frequency
    noct = filtoct    # bandwidth in octave fractions
    vmin = 80         # display range
    vmax = 100
    pm = bb.synthetic( freq, noct ) 
    Lm = ac.L_p( pm )

    ### plot map
    print("rec shape = ", Lm.shape)
    plt.subplot(1,2,2)
    #plt.imshow( Lm.T, origin='lower', vmin=Lm.max()*vmin/100, vmax=Lm.max()*vmax/100, extent=rg.extend(), interpolation='bicubic')
    plt.imshow(Lm.T, origin='lower', extent=rg.extend(), interpolation='bicubic')
    plt.colorbar()
    plt.title(f"{filnmbs}{itake}; {freq}Hz, BW{noct}")
    #plt.show()        
    filacc = f"{filnmbs}{itake}.png"
    plt.savefig(filacc)
    plt.ion()
    plt.show()
    plt.pause(ptime)
    
    # Pause before next take
    if itake<ntake-1:
        print(f"... waiting for next take")
        time.sleep(ptime)
    
prtlog(f"{time.ctime(time.time())}: Done")   
flog.close()
camera.close()

######################################
"""
import h5py

filename = 'test16c.h5'
with h5py.File(filename, 'w') as f:
    f.create_dataset(name='time_data', data=arec)
    obj = f['/time_data']
    obj.attrs['sample_freq'] = Fs

def list_h5_datasets(file_path):
    with h5py.File(file_path, 'r') as f:
        print("Datasets in '{}':".format(file_path))
        f.visititems(lambda name, obj: print(name, ": ", obj))
        
filename = 'audio16channels.h5'
list_h5_datasets(filename)
"""

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
