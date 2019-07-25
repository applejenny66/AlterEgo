import os
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="0"
os.environ['KERAS_BACKEND'] = 'tensorflow'
import numpy as np
import tensorflow as tf
from tensorflow.python.keras.models import load_model
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from sklearn.utils.multiclass import unique_labels

import math
import time
import json

# Local imports
import config
import data_proc

def normalize_kernel(kernel, subtract_mean=False):
    if subtract_mean:
        kernel = np.array(kernel, np.float32) - np.mean(kernel)
    return np.array(kernel, np.float32) / np.sum(np.abs(kernel))


def ricker_function(t, sigma):
    return 2. / (np.sqrt(3 * sigma) * np.pi ** 0.25) * (1. - (float(t) / sigma) ** 2) * np.exp(
        -(float(t) ** 2) / (2 * sigma ** 2))


def ricker_wavelet(n, sigma):
    return np.array(map(lambda x: ricker_function(x, sigma), range(-n // 2, n // 2 + 1)))


def transform_data(sequence_groups, sample_rate=250):
    #### Apply DC offset and drift correction
    drift_low_freq = 0.5  # 0.5
    sequence_groups = data_proc.transform.subtract_initial(sequence_groups)
    sequence_groups = data_proc.transform.highpass_filter(sequence_groups, drift_low_freq, sample_rate)
    sequence_groups = data_proc.transform.subtract_mean(sequence_groups)

    #### Apply notch filters at multiples of notch_freq
    notch_freq = 60
    num_times = 3  # pretty much just the filter order
    freqs = map(int, map(round, np.arange(1, sample_rate / (2. * notch_freq)) * notch_freq))
    for _ in range(num_times):
        for f in reversed(freqs):
            sequence_groups = data_proc.transform.notch_filter(sequence_groups, f, sample_rate)

    #### Apply standard deviation normalization
    # sequence_groups = data_proc.transform.normalize_std(sequence_groups)

    #### Apply ricker wavelet subtraction
    ricker_width = 35 * sample_rate // 250
    ricker_sigma = 4.0 * sample_rate / 250
    ricker_kernel = normalize_kernel(ricker_wavelet(ricker_width, ricker_sigma))
    ricker_convolved = data_proc.transform.correlate(sequence_groups, ricker_kernel)
    ricker_subtraction_multiplier = 2.0
    sequence_groups = sequence_groups - ricker_subtraction_multiplier * ricker_convolved

    #### Apply sine wavelet kernel
    # period = int(sample_rate)
    # sin_kernel = normalize_kernel(np.sin(np.arange(period)/float(period) * 1*np.pi), subtract_mean=True)
    # sequence_groups = data_proc.transform.correlate(sequence_groups, sin_kernel)

    low_freq = 0.5  # 0.5
    high_freq = 8  # 8
    order = 1

    #### Apply soft bandpassing
    sequence_groups = data_proc.transform.bandpass_filter(sequence_groups, low_freq, high_freq, sample_rate, order=order)

    #### Apply hard bandpassing
    # sequence_groups = data_proc.transform.fft(sequence_groups)
    # sequence_groups = data_proc.transform.fft_frequency_cutoff(sequence_groups, low_freq, high_freq, sample_rate)
    # sequence_groups = np.real(data_proc.transform.ifft(sequence_groups))
    #
    return sequence_groups


with open(config.data_maps, 'r') as f:
    input_data = json.load(f)

training_files = []
test_files = []
for data_file in input_data:
    if data_file['type'] == 'phonemes_utkarsh':
        if 'train' in data_file['filename']:
            train_file = data_proc.process_scrambled(data_file['labels'], [config.file_path+data_file['filename']], channels=config.channels,
                                       sample_rate=config.sample_rate, surrounding=config.surrounding, exclude=set([]),
                                       num_classes=config.num_classes)
            training_files.append(train_file)
        if 'test' in data_file['filename']:
            test_file = data_proc.process_scrambled(data_file['labels'], [config.file_path+data_file['filename']], channels=config.channels,
                                       sample_rate=config.sample_rate, surrounding=config.surrounding,
                                       exclude=set([]), num_classes=config.num_classes)
            test_files.append(test_file)

training_sequence_groups = data_proc.combine(training_files)
test_sequence_groups = data_proc.combine(test_files)

print("Training sequences:")
print(len(training_sequence_groups), " sequences")
lens = map(len, data_proc.get_inputs(training_sequence_groups)[0])
print min(lens), np.mean(lens), max(lens)

print("Test sequences:")
print(len(test_sequence_groups), "sequences")
lens = map(len, data_proc.get_inputs(test_sequence_groups)[0])
print min(lens), np.mean(lens), max(lens)

# Format into sequences and labels
train_sequences, train_labels = data_proc.get_inputs(training_sequence_groups)
test_sequences, test_labels = data_proc.get_inputs(test_sequence_groups)

train_sequences = transform_data(train_sequences)
test_sequences = transform_data(test_sequences)

label_map = config.phoneme_label_map
print("Label map:", len(label_map))
num_classes = len(np.unique(reduce(lambda a,b: a+b, label_map))) + 2 #(for start and end symbols)
start_symbol = num_classes - 2 # 29
end_symbol = num_classes - 1 # 30


label_map = map(lambda label_seq: [start_symbol] + label_seq + [end_symbol], label_map)
label_map = map(lambda label_seq: tf.keras.utils.to_categorical(label_seq, num_classes=num_classes), label_map)

train_labels = np.array(map(lambda i: label_map[i], train_labels))
test_labels = np.array(map(lambda i: label_map[i], test_labels))

max_input_length = max(map(len, train_sequences) + map(len, test_sequences))
max_labels_length = max(map(len, train_labels) + map(len, test_labels))

train_sequences = data_proc.transform.pad_truncate(train_sequences, max_input_length, position=0.0, value=-1e8)
test_sequences = data_proc.transform.pad_truncate(test_sequences, max_input_length, position=0.0, value=-1e8)
train_labels = data_proc.transform.pad_truncate(train_labels, max_labels_length, position=0.0, value=0)
test_labels = data_proc.transform.pad_truncate(test_labels, max_labels_length, position=0.0, value=0)

# --------------------------------------------------------------------------------------------------------------------------------------------

def greedy_decode(input_seq):
	input_seq = np.expand_dims(input_seq, 0)
	states_value = encoder_model.predict(input_seq) # Encoder states

	# Generate empty target sequence of length 1
	target_seq = np.zeros((1, 1, num_classes))
	# Populate the first character of target sequence with the start character
	target_seq[0, 0, start_symbol] = 1 # target_seq[0,0,29] = 1

	# Sampling loop for a batch of sequences
	# To simplify, we assume a batch of size 1
	stop_condition = False; 
	max_decoder_seq_length = 8 # change to 5+2
	decoded_sequence = [start_symbol] # [29]
	while not stop_condition:
		output_tokens, h, c = decoder_model.predict([target_seq] + states_value) # Takes in target_seq and Encoder states
		# print('OUTPUT TOKENS:', output_tokens)
		# print('SUM:', np.sum(output_tokens))

		# Sample a token
		sampled_token_index = np.argmax(output_tokens[0, -1, :]) # Greedy search decoding
		decoded_sequence.append(sampled_token_index) # [29,loc1]

		# Exit condition: either hit max length
		# or find stop character
		if (sampled_token_index == end_symbol or len(decoded_sequence) > max_decoder_seq_length):
			stop_condition = True

		# Update the target sequence (of length 1)
		target_seq = np.zeros((1, 1, num_classes))
		target_seq[0, 0, sampled_token_index] = 1

		# Update states
		states_value = [h, c]

	return decoded_sequence


def beam_decode(input_seq, k=5, max_decoder_seq_length=10):

    output_seq_list = []
    output_probs_list = []

    input_seq = np.expand_dims(input_seq, 0)
    h, c = encoder_model.predict(input_seq) # Encoder states

    decoded_seq_list = np.zeros((k, max_decoder_seq_length), dtype=np.int32)
    decoded_seq_list[:, 0] = start_symbol
    decoded_probs = np.ones(k, dtype=np.float32)

    target_seq_list = np.zeros((k, 1, num_classes)) # Generate empty target sequences
    target_seq_list[:, 0, start_symbol] = 1 # Populate the first character of target sequence with the start character

    h_values_list = np.tile(h, k).reshape((k, h.shape[1]))
    c_values_list = np.tile(c, k).reshape((k, c.shape[1]))

    i = 1 # i!=0 coz start symbol already given

    while k>0 and i<max_decoder_seq_length:
        output_tokens, h, c = decoder_model.predict([target_seq_list, h_values_list, c_values_list]) # Takes in target_seq and Encoder states
        output_tokens = np.squeeze(output_tokens, axis=1)
        # print('OUTPUT TOKENS:', output_tokens.shape)
        # print('OUTPUT TOKENS:', output_tokens)

        # Calc  probs
        top_k_output_tokens_ind = np.argsort(output_tokens, axis=1)[:,-k:]
        top_k_output_tokens_prob =  np.sort(output_tokens, axis=1)[:,-k:]
        decoded_probs_diagonal = np.diag(decoded_probs) 
        k_probs = np.dot(decoded_probs_diagonal, top_k_output_tokens_prob)

        # Update the target sequence (of length 1)
        flatten_k_probs = np.argsort(k_probs.flatten())[-k:]
        rows = flatten_k_probs/k # branches
        cols = flatten_k_probs%k

        # First character
        if i==1:
            rows = np.arange(k)
            cols = np.arange(k)

        target_seq_list = np.zeros((k,1,num_classes))
        selected_token_ind = top_k_output_tokens_ind[rows,cols]

        print('-'*130)
        print(rows)
        print(selected_token_ind)

        target_seq_list[np.arange(k),0,selected_token_ind]=1

        decoded_temp_list = decoded_seq_list[rows]
        decoded_temp_list[:,i] = selected_token_ind
        decoded_seq_list = decoded_temp_list
        decoded_probs = k_probs.flatten()[flatten_k_probs]

        # Update states
        h_values_list = h[rows,:]
        c_values_list = c[rows, :]
        i+=1

        # Delete finished branches
        # to_be_deleted = []
        # for a,b in zip(rows,cols):
        #     if top_k_output_tokens_ind[a,b]==end_symbol:
        #         output_seq_list.append(list(decoded_seq_list[a]))
        #         output_probs_list.append(decoded_probs[a])
        #         to_be_deleted.append(a)

        to_be_deleted = rows[np.where(top_k_output_tokens_ind[rows,cols]==end_symbol)]
        output_seq_list += decoded_seq_list[to_be_deleted]
        output_probs_list += decode_probs[to_be_deleted]

        decoded_seq_list = np.delete(decoded_seq_list, to_be_deleted, axis=0)
        decoded_probs = np.delete(decoded_probs, to_be_deleted, axis=0)
        k-=len(to_be_deleted)

    # append the rest
    if k>0:
        output_seq_list.append(list(decoded_seq_list))
        output_probs_list.append(list(decoded_probs))

    return output_seq_list, output_probs_list


def plot_confusion_matrix(y_true, y_pred, classes, normalize=False, title=None, cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if not title:
        if normalize:
            title = 'Normalized confusion matrix'
        else:
            title = 'Confusion matrix, without normalization'

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    # Only use the labels that appear in the data
    classes = classes[unique_labels(y_true, y_pred)]
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    fig, ax = plt.subplots()
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    ax.figure.colorbar(im, ax=ax)
    # We want to show all ticks...
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           # ... and label them with the respective list entries
           xticklabels=classes, yticklabels=classes,
           title=title,
           ylabel='True label',
           xlabel='Predicted label')

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    return ax

# --------------------------------------------------------------------------------------------------------------------------------------------

print('TEST LABELS SHAPE:', test_labels.shape)


# Enter the model name to be loaded
log_name = '20190724-110527_e100_b80_phon_bidir_utkarsh_CV' # Max validation = 32.6%, Fold 0 acc on test: 14.34%


# Loading the models
model = load_model('SavedModels/Full_{}.h5'.format(log_name))
encoder_model = load_model('SavedModels/Encoder_{}.h5'.format(log_name))
decoder_model = load_model('SavedModels/Decoder_{}.h5'.format(log_name))
# print(model.metrics_tensors)


test_index = 10
print 'TEST INDEX :', test_index
print list(np.argmax(test_labels[test_index], axis=1))
print beam_decode(test_sequences[test_index])
print greedy_decode(test_sequences[test_index])


counter = 0 # Tracks number of predictions with same length as actual target
y_test, y_pred = [], []

for test_index in range(len(test_sequences)):
	# print 'TEST INDEX :', test_index
	# print list(np.argmax(test_labels[test_index], axis=1))
	# print greedy_decode(test_sequences[test_index])
	# print '\n'
	counter += 1
	actual = list(np.argmax(test_labels[test_index], axis=1))
	predicted = greedy_decode(test_sequences[test_index])
	if (len(actual) == len(predicted)):
		for index in range(len(actual)):
			y_test.append(actual[index])
			y_pred.append(predicted[index])

print('Number of predicted sequences with equal length as target labels : {} out of {}'.format(counter, len(test_sequences)))

np.set_printoptions(precision=2)
class_names = ['<start>', 'AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'UW', 'CH', 'D', 'G', 'HH', 'JH', 'K', 'L', 'N', 'NG', 'R', 'S', 'SH', 'T', 'TH', 'Y', 'Z', '<end>']

# Mapping numbers to actual class names
for index, element in enumerate(y_test):	y_test[index] = class_names[element]
for index, element in enumerate(y_pred):	y_pred[index] = class_names[element]

# Plot non-normalized confusion matrix
plot_confusion_matrix(y_test, y_pred, classes=class_names,
                      title='Confusion matrix, without normalization')

# Plot normalized confusion matrix
plot_confusion_matrix(y_test, y_pred, classes=class_names, normalize=True,
                      title='Normalized confusion matrix')

plt.show()
'''

