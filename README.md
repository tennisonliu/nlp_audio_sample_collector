# training_sample_collection
Quick and easy Python Script to collect and generate training samples to train NLP learning algorithms.These scripts are especially helpful for generating audio training samples that can be fed into Keras/Tensorflow.
The two components:
* audio_sampling.py: script to easily collect audio samples through microphone from users.
* sample_generator.py: takes the audio samples generated from audio_sampling.py and generates training samples.

# Requirements
* numpy
* pydub
* glob
* IPython

# Note on implementation
* When generating large training sets, exporting the training sets might drain the RAM on the local Machine. Modify the code to generate chunks/batches of training sets instead.
* The script to collect audio samples records 3 seconds of audio as default. This should be changed for different applications.
