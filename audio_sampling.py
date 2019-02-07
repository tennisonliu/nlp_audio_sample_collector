import pyaudio
import wave
import time
import sys
import os

#countdown display
def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        print(timeformat, end='\r')
        time.sleep(1)
        t -= 1

def recording(output_fp, samprate, num_channels, dev_ind):
    FORMAT = pyaudio.paInt16 #2 bytes audio encoding
    CHANNELS = num_channels
    RATE = int(samprate)
    CHUNK = 1024 #? 
    RECORD_TIME = 3 # record for 3 seconds
    WAVE_OUTPUT_FILENAME = output_fp
    # start recording
    stream = p.open(format = FORMAT, input_device_index=int(dev_ind), channels = CHANNELS, rate = RATE, input = True, frames_per_buffer = CHUNK)
    print("Recording...")
    frames = []
    
    for i in range(0, int(RATE/CHUNK*RECORD_TIME)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Finished Recording.\n")
    
    stream.stop_stream()
    stream.close()
    
    #write output file
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(p.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    print("New wav file created.")

if __name__ = "__main__":
    #create instance of PyAudio class
    p = pyaudio.PyAudio()
    for ind in range (0, p.get_device_count()):
        info = p.get_device_info_by_index(ind)
        print(info)

    dev_ind = input("Which device do you wish to connect to?\n")
    info = p.get_device_info_by_index(int(dev_ind))
    samprate = info['defaultSampleRate']
    num_channels = info['maxInputChannels']
    print('sampling rate: ', samprate, ' num_channels: ', num_channels)
    time.sleep(1)

    voice_name = input("What is your name?\n")

    path = r""  #add path_variable
    # Create directory
    dirName = path+'\\Directory_' + voice_name
     
    try:
        # Create target Directory
        os.mkdir(dirName)
        print(dirName ,  " Created ") 
    except FileExistsError:
        print(dirName ,  " already exists")

    print('Please read the following phrase three times, slowly and clearly after each prompt and countdown: \n')
    time.sleep(3)
    tot = 3
    while(tot!=0):
        if tot==3:
            print('Hello Australia\n')
        else:
            print("\nPlease read the phrase again: 'Hello Australia'\n")
        countdown(3)
        tot = tot-1
        temp_dirName = dirName + '\\train_'+str(abs(tot-3))
        recording(temp_dirName, samprate, num_channels, dev_ind)
        time.sleep(2)

    negatives = ['Morning Alexa','Baby powder','Red Water']
    for i in range (0, len(negatives)):
        print("\nPlease read the following phrase: ", negatives[i], "\n")
        countdown(3)
        temp_dirName = dirName + '\\negatives'+str(abs(i+1))
        recording(temp_dirName, samprate, num_channels, dev_ind)
        time.sleep(2)

    p.terminate()
