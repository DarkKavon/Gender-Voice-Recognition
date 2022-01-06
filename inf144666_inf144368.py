import glob
from pylab import *
from scipy import *
import numpy as np
import sys
from datetime import datetime
import soundfile as sf

maleRange = [60,160]
femaleRange = [180,270]
HPSCount = 5

def HPS(rate, inputData):
    T = len(inputData)/rate # sound length in seconds
    chunks = [inputData[i*rate:(i+1)*rate] for i in range(int(T))] # devide into full seconds
    resultChunks = [] # result list
    for data in chunks:
        hamWindow = np.hamming(len(data))
        # convert data into 1 chanel
        if data.ndim > 1:
            data = (data[:, 0] + data[:,1]) / 2
        else:
            pass
        data = data*hamWindow
        fft = abs(np.fft.fft(data))/rate
        fftCopy = np.copy(fft)
        for i in range(2,HPSCount):
            tab = np.copy(fft[::i])
            fftCopy = fftCopy[:len(tab)]
            fftCopy *= tab
        resultChunks.append(fftCopy)
    
    # list of 0s, len: middle list of resChunks
    result = [0]*len(resultChunks[int(len(resultChunks)/2)])
    for res in resultChunks:
        if(len(res)!=len(result)):
            continue
        result += res
        
    # comparison sum in male and female range
    if(np.sum(result[maleRange[0]:maleRange[1]]) > np.sum(result[femaleRange[0]:femaleRange[1]])): 
        return 1
    else:
        return 0

def allFiles():
    # female: 0
    # male: 1
    m = [0,0] # ok, nok
    f = [0,0] # ok, nok
    files = glob.glob("trainall/*.wav")
    for file in files:
        array, rate = sf.read(file)
        gender = int(file[-5:-4] == "M")
        result = HPS(rate, array)
        if gender == 1:
            if result == 1:
                m[0] += 1
            else:
                m[1] += 1
        else:
            if result == 1:
                f[1] += 1
            else:
                f[0] += 1
    print("Legend: [ok, not ok]")
    print("Male stats:",m)
    print("Female stats:",f)
    stats = round((m[0] + f[0]) / (np.sum(m) + np.sum(f)),4)*100
    print(str(stats)+'%')
    
if __name__ == "__main__":
    file = sys.argv[1]
    try:
        array, rate = sf.read(file)
    except:
        print("Could not read file:", file)
        sys.exit()
    result = HPS(rate, array)
    if result == 1:
        print("M")
    elif result == 0:
        print("K")
    
    