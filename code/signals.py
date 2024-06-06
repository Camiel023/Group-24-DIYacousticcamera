import numpy as np
from scipy.signal import chirp, sweep_poly

def SineWave(npt, fs, freq, amp = 1.0, phase = 0):
    # npt = number-of-points
    # fs = samplerate
    # freq = frequency in Hz
    # amp = Amplitude (Probably 0<=1)
    # phase = Starting phase in radians
    dt = 1/fs;
    asrc = np.zeros(npt)
    # amp = 1.0; freq1 = 1000.0; freq2 = freq1+20.0
    for ii in range(npt):
        tt = ii*dt
        asrc[ii]= np.sin(2*np.pi*freq*tt+phase)*amp
    return(asrc)

def GaussEnvelope(npt, fs, tshift, width):
    env = np.zeros(npt)
    for ii in range(npt):
        tt = ii/fs
        # aa = amp*np.sin(2*np.pi*freq*tt+phase) * np.exp(-((tt - tshift)/trel)**2)
        env[ii] = np.exp(-((tt - tshift)/width)**2)
    return env
    
def PulseWave(npt, fs, freq, amp = 1.0, phase = 0, tshift = 0, width = None):
    # npt, fs, freq, amp = as usual
    # tshift = maximum amplitude point shift in sec (default = middle)
    # width = ramp up/down time in sec

    # shift the gaussian to half the duration
    dur = npt/fs
    tshift += dur/2

    # guestimate a default ramp up/down time
    if width is None:
        width = dur/5

    # assemble
    wave = SineWave(npt, fs, freq, amp, phase)
    gauss = GaussEnvelope(npt, fs, tshift, width)

    # if random_phase:
    #     fwave = np.fft.fft(wave)
    #     phase = 2*np.pi*np.random.random(npt)
    #     ephase = np.exp(1j*phase)
    #     fasrc = np.multiply(ephase, fwave)
    #     wave = np.real(np.fft.ifft(fwave)) 
        
    return gauss*wave

def ChirpWaveLin(npt, fs, freq1, freq2, amp = 1.0):
    t = np.linspace(0, npt/fs, npt)
    w = amp*chirp(t, f0=freq1, f1=freq2, t1=npt/fs, method='linear')
    return(w)

def ChirpWaveLog(npt, dt, freq1, freq2, amp = 1.0):
    t = np.linspace(0, npt/fs, npt)
    w = amp*chirp(t, f0=freq1, f1=freq2, t1=npt/fs, method='logarithmic')
    return(w)
