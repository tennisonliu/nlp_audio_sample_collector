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

def get_random_time_segment(segment_ms):
	segment_start = np.random.randint(low=0, high=10000-segment_ms)   # Make sure segment doesn't run past the 10sec background 
	segment_end = segment_start + segment_ms - 1
	
	return (segment_start, segment_end)

def is_overlapping(segment_time, previous_segments):
	segment_start, segment_end = segment_time
	overlap = False
	for previous_start, previous_end in previous_segments:
		if segment_start <= previous_end and segment_end >= previous_start:
			overlap = True

	return overlap

def insert_audio_clip(background, audio_clip, previous_segments):
	segment_ms = len(audio_clip)
	segment_time = get_random_time_segment(segment_ms)
	while is_overlapping(segment_time, previous_segments):
		segment_time = get_random_time_segment(segment_ms)
	previous_segments.append(segment_time)
	new_background = background.overlay(audio_clip, position = segment_time[0])
	
	return new_background, segment_time

def insert_ones(y, segment_end_ms):
	segment_end_y = int(segment_end_ms * Ty / 10000.0)
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
	for filename in os.listdir(neg_path):
		if filename.endswith("wav"):
			fp_negative = AudioSegment.from_wav(neg_path+"/"+filename)
			negatives.append(fp_negative)
	for filename in os.listdir(back_path):
		if filename.endswith("wav"):
			fp_background = AudioSegment.from_wav(back_path+"/"+filename)
			segment_start = 1*1000
			segment_end = 11*1000
			fp_background = fp_background[segment_start:segment_end]
			backgrounds.append(fp_background)
	return activates, negatives, backgrounds

Ty = 1375

def generating_training_sets(backgrounds, activates, negatives, index):
	y = np.zeros((1, Ty))
	previous_segments = []
	
	random_index_background = np.random.randint(0, 5)
	random_background = backgrounds[random_index_background]
	num_of_activates = np.random.randint(1, 2)
	random_indices_act = np.random.randint(len(activates), size = num_of_activates)
	random_activates = [activates[j] for j in random_indices_act]
	
	num_of_negatives = np.random.randint(1, 2)
	random_indices_neg = np.random.randint(len(negatives), size = num_of_negatives)
	random_negatives = [negatives[j] for j in random_indices_neg]
	
	print("random_index_act: ", random_indices_act)
	print("random_index_neg: ", random_indices_neg)
	print("random_index_background: ", random_index_background)
	
		
	for random_activate in random_activates:
		random_background, segment_time = insert_audio_clip(random_background, random_activate, previous_segments)
		segment_start, segment_end = segment_time
		y = insert_ones(y, segment_end_ms=segment_end)
	

	for random_negative in random_negatives:
		random_background, _ = insert_audio_clip(random_background, random_negative, previous_segments)
	
	file_handle = random_background.export(""+str(index)+ ".wav", format="wav")
	print("File was saved in your directory.")
	x = graph_spectrogram(""+str(index)+ ".wav")
	return x, y

if __name__=="main":
	act_path = ""           #add path to activation samples
	neg_path = ""           #add path to negative samples
	back_path = ""          #add path to background samples
	activates, negatives, backgrounds = load_samples(act_path, neg_path, back_path)

	final_x = []
	final_y = []
	for i in range(0, 10):
			x, y = generating_training_sets(backgrounds = backgrounds, activates = activates, negatives = negatives, index = i)
			final_x.append(x)
			final_y.append(y)

	print(len(final_x), len(final_x[0]), len(final_x[0][0]), type(final_x))
	print(len(final_y), len(final_y[0]), len(final_y[0][0]), type(final_y))

	np.save("", final_x)
	np.save("", final_y)
