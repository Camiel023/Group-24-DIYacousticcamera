import scipy.signal as sps
import numpy as np

def HighpassFilter(samples, fs):
    filter_stop_freq = 200  # Hz
    filter_pass_freq = 400  # Hz
    filter_order = 1001
    #
    # High-pass filter
    nyquist_rate = fs / 2.
    desired = (0, 0, 1, 1)
    bands = (0, filter_stop_freq, filter_pass_freq, nyquist_rate)
    filter_coefs = sps.firls(filter_order, bands, desired, nyq=nyquist_rate)

    return sps.filtfil(filter_coefs, [1], samples)
    
    # # Apply high-pass filter on all 16 channels
    # farecs = samples
    # for ii in range(0,16):
    #    print(ii)
    #    farec = sps.filtfilt(filter_coefs, [1], samples[:,ii])
    #    farecs[:,ii] = farec[:]
    # return farecs

def BandpassFilter(samples, fs, center_freq, width, order=5):
    nyquist = fs / 2
    low  = (center_freq - width/2) / nyquist
    high = (center_freq + width/2) / nyquist
    b, a = sps.butter(order, [low, high], btype='band')
    return sps.filtfilt(b, a, samples)

def BandpassFilter16(samples, fs, center_freq, width, order=5):
    outsmp = np.zeros((len(samples), 16))
    for i in range(0, 16):
        outsmp[:, i] = BandpassFilter(samples[:, i], fs, center_freq, width)
    return outsmp

def Normalize(samples):
    return samples / np.max(samples)

def Normalize16(channels):
    for i in range(0, 16):
        samples[:, i] = Normalize(samples[:, i])
    return samples
