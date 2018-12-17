import numpy as np
from pydub import AudioSegment
import random
import sys
import io
import os
import glob
import IPython
from td_utils import *
%matplotlib inline

"""
get_random_time_segment(segment_ms) gets a random time segment in background audio
is_overlapping(segment_time, existing_segments) checks if a time segment overlaps with existing segments
insert_audio_clip(background, audio_clip, existing_times) inserts an audio segment at a random time in background audio using get_random_time_segment and is_overlapping
insert_ones(y, segment_end_ms) inserts 1's into label vector y after the word "activate"
"""

def get_random_time_segment(segment_ms):
    """
    Gets a random time segment of duration segment_ms in a 10,000 ms audio clip.
    
    Arguments:
    segment_ms -- the duration of the audio clip in ms ("ms" stands for "milliseconds")
    
    Returns:
    segment_time -- a tuple of (segment_start, segment_end) in ms
    """
    
    segment_start = np.random.randint(low=0, high=10000-segment_ms)   # Make sure segment doesn't run past the 10sec background 
    segment_end = segment_start + segment_ms - 1
    
    return (segment_start, segment_end)

    def is_overlapping(segment_time, previous_segments):
    """
    Checks if the time of a segment overlaps with the times of existing segments.
    
    Arguments:
    segment_time -- a tuple of (segment_start, segment_end) for the new segment
    previous_segments -- a list of tuples of (segment_start, segment_end) for the existing segments
    
    Returns:
    True if the time segment overlaps with any of the existing segments, False otherwise
    """
    
    segment_start, segment_end = segment_time
    
    # Step 1: Initialize overlap as a "False" flag. (≈ 1 line)
    overlap = False
    
    # Compare start/end times and set the flag to True if there is an overlap (≈ 3 lines)
    for previous_start, previous_end in previous_segments:
        if segment_start <= previous_end and segment_end >= previous_start:
            overlap = True

    return overlap

    def insert_audio_clip(background, audio_clip, previous_segments):
    """
    Insert a new audio segment over the background noise at a random time step, ensuring that the 
    audio segment does not overlap with existing segments.
    
    Arguments:
    background -- a 10 second background audio recording.  
    audio_clip -- the audio clip to be inserted/overlaid. 
    previous_segments -- times where audio segments have already been placed
    
    Returns:
    new_background -- the updated background audio
    """
    
    # Get the duration of the audio clip in ms
    segment_ms = len(audio_clip)
    
    # Step 1: Use one of the helper functions to pick a random time segment onto which to insert 
    # the new audio clip. (≈ 1 line)
    segment_time = get_random_time_segment(segment_ms)

    # Step 2: Check if the new segment_time overlaps with one of the previous_segments. If so, keep 
    # picking new segment_time at random until it doesn't overlap. (≈ 2 lines)
    while is_overlapping(segment_time, previous_segments):
        segment_time = get_random_time_segment(segment_ms)

    # Step 3: Add the new segment_time to the list of previous_segments (≈ 1 line)
    previous_segments.append(segment_time)
    
    # Step 4: Superpose audio segment and background
    new_background = background.overlay(audio_clip, position = segment_time[0])
    
    return new_background, segment_time

    def insert_ones(y, segment_end_ms):
    """
    Update the label vector y. The labels of the 50 output steps strictly after the end of the segment 
    should be set to 1. By strictly we mean that the label of segment_end_y should be 0 while, the
    50 followinf labels should be ones.
    
    
    Arguments:
    y -- numpy array of shape (1, Ty), the labels of the training example
    segment_end_ms -- the end time of the segment in ms
    
    Returns:
    y -- updated labels
    """
    
    # duration of the background (in terms of spectrogram time-steps)
    segment_end_y = int(segment_end_ms * Ty / 10000.0)
    
    # Add 1 to the correct index in the background label (y)
    for i in range(segment_end_y + 1, segment_end_y + 51):
        if i < Ty:
            y[0, i] = 1
    
    return y

    def load_samples(act_path, neg_path, back_path):
    activates = []
    backgrounds = []
    negatives = []
    for filename in os.listdir(act_path):
        if filename.endswith("wav"):
            fp_activate = AudioSegment.from_wav(act_path+"/"+filename)
            activates.append(fp_activate)
    # print(len(activates))
    for filename in os.listdir(neg_path):
        if filename.endswith("wav"):
            fp_negative = AudioSegment.from_wav(neg_path+"/"+filename)
            negatives.append(fp_negative)
    # print(len(negatives))
    for filename in os.listdir(back_path):
        if filename.endswith("wav"):
            fp_background = AudioSegment.from_wav(back_path+"/"+filename)
            segment_start = 1*1000
            segment_end = 11*1000
            fp_background = fp_background[segment_start:segment_end]
            backgrounds.append(fp_background)
    # print(len(backgrounds))
    return activates, negatives, backgrounds

    Ty = 1375 #Ty determines the length of the output vector

    def generating_training_sets(backgrounds, activates, negatives, index):
    """
    Creates a certain number of training samples with background noise overlayed 
    with random activation phrases and negative phrases.
    
    Arguments:
    num_samples -- number of training phrases we wish to generate
    background -- list of background noises
    activates -- list of activation phrases
    negatives -- list of negative phrases
    
    Returns:
    x -- the spectrogram of the training example
    y -- the label at each time step of the spectrogram
    """
    # Set the random seed
    # np.random.seed(10)
    
    # Initialise label y = label vector of zeros
    y = np.zeros((1, Ty))
    
    # Initialize segment times as empty list
    previous_segments = []
    
        # select random background noises
    random_index_background = np.random.randint(0, 5)
    random_background = backgrounds[random_index_background]
    # select random activation phrases
    num_of_activates = np.random.randint(1, 2)
    #num_of_activates = 1
    random_indices_act = np.random.randint(len(activates), size = num_of_activates)
    random_activates = [activates[j] for j in random_indices_act]
    
    # select random negative phrases
    num_of_negatives = np.random.randint(1, 2)
    # num_of_negatives = 1
    random_indices_neg = np.random.randint(len(negatives), size = num_of_negatives)
    random_negatives = [negatives[j] for j in random_indices_neg]
    
    print("random_index_act: ", random_indices_act)
    print("random_index_neg: ", random_indices_neg)
    print("random_index_background: ", random_index_background)
    
        
    for random_activate in random_activates:
        # Insert the audio clip on the background
        random_background, segment_time = insert_audio_clip(random_background, random_activate, previous_segments)
        # Retrieve segment_start and segment_end from segment_time
        segment_start, segment_end = segment_time
        # Insert labels in "y"
        y = insert_ones(y, segment_end_ms=segment_end)
    

    for random_negative in random_negatives:
        # Insert the audio clip on the background 
        random_background, _ = insert_audio_clip(random_background, random_negative, previous_segments)
    
    file_handle = random_background.export(""+str(index)+ ".wav", format="wav")
    print("File was saved in your directory.")

    # Get and plot spectrogram of the new recording (background with superposition of positive and negatives)
    x = graph_spectrogram(""+str(index)+ ".wav")
    return x, y



act_path = ""           #add path to activation samples
neg_path = ""           #add path to negative samples
back_path = ""          #add path to background samples
activates, negatives, backgrounds = load_samples(act_path, neg_path, back_path)

final_x = []
final_y = []
for i in range(0, 10): #this generates 10 training samples
        x, y = generating_training_sets(backgrounds = backgrounds, activates = activates, negatives = negatives, index = i)
        final_x.append(x)
        final_y.append(y)

print(len(final_x), len(final_x[0]), len(final_x[0][0]), type(final_x))
print(len(final_y), len(final_y[0]), len(final_y[0][0]), type(final_y))

np.save("", final_x)
np.save("", final_y)
