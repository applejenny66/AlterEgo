import os
os.environ["CUDA_VISIBLE_DEVICES"]="0"

import numpy as np
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from display_utils import DynamicConsoleTable
import math
import time
import os.path

import data

abs_path = os.path.abspath(os.path.dirname(__file__))

def normalize_kernel(kernel, subtract_mean=False):
    if subtract_mean:
        kernel = np.array(kernel, np.float32) - np.mean(kernel)
    return np.array(kernel, np.float32) / np.sum(np.abs(kernel))
def ricker_function(t, sigma):
    return 2./(np.sqrt(3*sigma)*np.pi**0.25)*(1.-(float(t)/sigma)**2)*np.exp(-(float(t)**2)/(2*sigma**2))
def ricker_wavelet(n, sigma):
    return np.array(map(lambda x: ricker_function(x, sigma), range(-n//2, n//2+1)))
    
def transform_data(sequence_groups, sample_rate=250):
    #### Apply DC offset and drift correction
    drift_low_freq = 0.5 #0.5
    sequence_groups = data.transform.subtract_initial(sequence_groups)
    sequence_groups = data.transform.highpass_filter(sequence_groups, drift_low_freq, sample_rate)
    sequence_groups = data.transform.subtract_mean(sequence_groups)

    #### Apply notch filters at multiples of notch_freq
    notch_freq = 60
    num_times = 3 #pretty much just the filter order
    freqs = map(int, map(round, np.arange(1, sample_rate/(2. * notch_freq)) * notch_freq))
    for _ in range(num_times):
        for f in reversed(freqs):
            sequence_groups = data.transform.notch_filter(sequence_groups, f, sample_rate)

    #### Apply standard deviation normalization
    #sequence_groups = data.transform.normalize_std(sequence_groups)

    #### Apply ricker wavelet subtraction
    ricker_width = 35 * sample_rate // 250
    ricker_sigma = 4.0 * sample_rate / 250
    ricker_kernel = normalize_kernel(ricker_wavelet(ricker_width, ricker_sigma))
    ricker_convolved = data.transform.correlate(sequence_groups, ricker_kernel)
    ricker_subtraction_multiplier = 2.0
    sequence_groups = sequence_groups - ricker_subtraction_multiplier * ricker_convolved

    #### Apply sine wavelet kernel
    #period = int(sample_rate)
    #sin_kernel = normalize_kernel(np.sin(np.arange(period)/float(period) * 1*np.pi), subtract_mean=True)
    #sequence_groups = data.transform.correlate(sequence_groups, sin_kernel)

    low_freq = 0.5 #0.5
    high_freq = 8 #8
    order = 1

    #### Apply soft bandpassing
    sequence_groups = data.transform.bandpass_filter(sequence_groups, low_freq, high_freq, sample_rate, order=order)
    
    #### Apply hard bandpassing
    #sequence_groups = data.transform.fft(sequence_groups)
    #sequence_groups = data.transform.fft_frequency_cutoff(sequence_groups, low_freq, high_freq, sample_rate)
    #sequence_groups = np.real(data.transform.ifft(sequence_groups))
#    
    return sequence_groups

#length = 3000 #3000 #600 #2800
    
channels = range(0, 8)
surrounding = 250 #250

labels = [64, 148, 125, 66, 181, 106, 191, 94, 79, 170, 144, 55, 152, 101, 128, 92, 142, 116, 81, 85, 140, 134, 127, 90, 175, 149, 83, 69, 123, 196, 141, 185, 119, 178, 164, 98, 103, 78, 104, 158, 162, 67, 169, 153, 108, 168, 68, 54, 95, 109, 89, 86, 167, 189, 157, 182, 176, 135, 172, 145, 61, 163, 173, 62, 52, 154, 56, 177, 160, 115, 105, 194, 188, 96, 112, 124, 166, 143, 150, 139, 60, 84, 82, 174, 88, 133, 161, 199, 77, 73, 117, 59, 180, 147, 155, 195, 137, 198, 159, 114]

train_1 = data.process_scrambled(labels, ['sen_word40_train_1.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)

labels = [109, 104, 110, 88, 119, 133, 117, 138, 59, 157, 161, 178, 70, 91, 153, 167, 136, 94, 51, 147, 112, 168, 164, 170, 93, 81, 84, 132, 160, 195, 115, 95, 152, 198, 127, 105, 193, 65, 89, 149, 188, 177, 101, 53, 97, 176, 74, 54, 134, 63, 75, 121, 69, 126, 174, 118, 144, 103, 124, 190, 106, 107, 139, 145, 185, 123, 55, 140, 60, 83, 67, 62, 114, 116, 73, 129, 98, 90, 58, 80, 163, 111, 179, 79, 166, 135, 57, 181, 100, 102, 175, 189, 183, 184, 120, 158, 50, 99, 141, 82]

train_2 = data.process_scrambled(labels, ['sen_word40_train_2.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([45]), num_classes=200)

labels = [168, 165, 171, 79, 188, 58, 56, 173, 85, 52, 181, 108, 61, 163, 179, 142, 152, 54, 190, 104, 144, 123, 192, 131, 154, 125, 67, 117, 155, 72, 176, 141, 55, 95, 148, 113, 126, 186, 172, 139, 121, 129, 175, 143, 84, 150, 162, 136, 94, 74, 101, 63, 68, 98, 167, 151, 197, 140, 199, 71, 97, 92, 166, 164, 69, 161, 107, 115, 189, 102, 195, 149, 100, 157, 120, 110, 194, 65, 114, 130, 105, 196, 51, 75, 138, 132, 76, 159, 62, 193, 135, 111, 184, 127, 64, 112, 183, 57, 147, 82]

train_3 = data.process_scrambled(labels, ['sen_word40_train_3.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([21]), num_classes=200)

labels = [106, 169, 141, 122, 166, 135, 103, 105, 194, 75, 62, 136, 170, 167, 55, 162, 183, 90, 51, 188, 165, 65, 186, 185, 148, 131, 95, 139, 179, 89, 99, 171, 84, 129, 94, 83, 140, 192, 158, 195, 196, 156, 134, 154, 57, 108, 125, 193, 66, 157, 151, 173, 64, 96, 138, 144, 178, 87, 85, 78, 187, 121, 79, 53, 52, 56, 123, 93, 97, 74, 60, 168, 61, 63, 143, 181, 104, 190, 153, 130, 58, 82, 152, 150, 71, 67, 86, 69, 116, 137, 182, 119, 199, 73, 176, 112, 109, 132, 160, 175]

train_4 = data.process_scrambled(labels, ['sen_word40_train_4.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)

labels = [141, 125, 118, 62, 180, 61, 122, 123, 166, 145, 78, 142, 199, 151, 132, 115, 102, 177, 181, 56, 182, 140, 73, 80, 152, 76, 186, 168, 150, 67, 52, 129, 105, 95, 124, 59, 70, 87, 103, 172, 100, 164, 196, 88, 163, 58, 66, 106, 133, 153, 86, 138, 55, 54, 136, 149, 171, 193, 176, 195, 121, 192, 135, 79, 173, 92, 77, 97, 119, 112, 90, 114, 108, 191, 167, 147, 117, 190, 155, 57, 128, 175, 83, 162, 84, 183, 75, 148, 91, 65, 187, 63, 98, 198, 161, 89, 81, 107, 85, 139]

train_5 = data.process_scrambled(labels, ['sen_word40_train_5.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([49]), num_classes=200)

labels = [141, 125, 118, 62, 180, 61, 122, 123, 166, 145, 78, 142, 199, 151, 132, 115, 102, 177, 181, 56, 182, 140, 73, 80, 152, 76, 186, 168, 150, 67, 52, 129, 105, 95, 124, 59, 70, 87, 103, 172, 100, 164, 196, 88, 163, 58, 66, 106, 133, 153, 86, 138, 55, 54, 136, 149, 171, 193, 176, 195, 121, 192, 135, 79, 173, 92, 77, 97, 119, 112, 90, 114, 108, 191, 167, 147, 117, 190, 155, 57, 128, 175, 83, 162, 84, 183, 75, 148, 91, 65, 187, 63, 98, 198, 161, 89, 81, 107, 85, 139]

train_6 = data.process_scrambled(labels, ['sen_word40_train_6.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)

labels = [95, 150, 60, 83, 154, 193, 130, 158, 54, 152, 172, 112, 195, 93, 186, 149, 159, 105, 175, 81, 56, 59, 138, 58, 109, 72, 66, 183, 198, 178, 160, 69, 179, 115, 84, 99, 77, 125, 101, 108, 168, 136, 165, 120, 61, 76, 173, 62, 82, 148, 51, 164, 88, 194, 137, 117, 86, 100, 64, 197, 155, 67, 161, 85, 124, 123, 50, 114, 121, 53, 187, 169, 116, 145, 96, 199, 57, 185, 91, 65, 151, 94, 167, 147, 75, 126, 191, 143, 111, 128, 140, 89, 107, 180, 142, 102, 181, 129, 122, 133]

train_7 = data.process_scrambled(labels, ['sen_word40_train_7.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)

training_sequence_groups = data.combine([train_1, train_2, train_3, train_4, train_5, train_6, train_7])

print len(training_sequence_groups)
print map(len, training_sequence_groups)

lens = map(len, data.get_inputs(training_sequence_groups)[0])
print min(lens), np.mean(lens), max(lens)


labels = [182, 51, 164, 112, 160, 77, 141, 86, 135, 148, 138, 61, 189, 121, 62, 68, 87, 109, 161, 115, 169, 177, 152, 171, 168]

test1_1 = data.process_scrambled(labels, ['sen_word40_test1_1.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [111, 125, 181, 58, 195, 60, 103, 91, 97, 56, 171, 70, 139, 150, 118, 188, 183, 73, 119, 63, 124, 122, 190, 114, 145]

test1_2 = data.process_scrambled(labels, ['sen_word40_test1_2.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [145, 64, 66, 187, 70, 183, 170, 152, 144, 178, 146, 56, 181, 59, 173, 111, 130, 150, 118, 80, 166, 74, 83, 165, 77]

test1_3 = data.process_scrambled(labels, ['sen_word40_test1_3.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [124, 188, 154, 58, 100, 79, 94, 130, 146, 72, 54, 66, 187, 135, 125, 149, 122, 87, 172, 63, 68, 80, 115, 180, 183]

test1_4 = data.process_scrambled(labels, ['sen_word40_test1_4.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [186, 90, 128, 166, 105, 160, 95, 158, 92, 168, 187, 199, 173, 178, 124, 118, 97, 130, 66, 141, 64, 86, 174, 162, 54]

test1_5 = data.process_scrambled(labels, ['sen_word40_test1_5.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [76, 180, 65, 187, 139, 127, 117, 96, 137, 152, 149, 63, 172, 142, 175, 71, 118, 186, 156, 69, 191, 99, 124, 54, 126]

test1_6 = data.process_scrambled(labels, ['sen_word40_test1_6.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


test1_sequence_groups = data.combine([test1_1, test1_2, test1_3, test1_4, test1_5, test1_6])

print len(test1_sequence_groups)
print map(len, test1_sequence_groups)

lens = map(len, data.get_inputs(test1_sequence_groups)[0])
print min(lens), np.mean(lens), max(lens)


labels = [41, 14, 36, 39, 28, 11, 17, 21, 38, 29, 8, 35, 23, 42, 45, 31, 10, 46, 4, 13, 24, 16, 15, 19, 40]

test2_1 = data.process_scrambled(labels, ['sen_word40_test2_1.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [22, 29, 17, 37, 46, 26, 30, 18, 20, 43, 12, 7, 27, 48, 15, 47, 1, 45, 23, 40, 19, 6, 13, 44, 4]

test2_2 = data.process_scrambled(labels, ['sen_word40_test2_2.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [48, 29, 43, 37, 15, 33, 17, 1, 7, 25, 31, 32, 5, 44, 26, 40, 24, 4, 30, 19, 34, 38, 6, 27, 36]

test2_3 = data.process_scrambled(labels, ['sen_word40_test2_3.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [10, 31, 21, 11, 6, 8, 32, 9, 22, 48, 1, 44, 45, 36, 27, 3, 40, 38, 25, 47, 41, 13, 16, 37, 34]

test2_4 = data.process_scrambled(labels, ['sen_word40_test2_4.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [15, 41, 1, 9, 6, 23, 29, 18, 13, 7, 44, 5, 26, 12, 36, 24, 16, 47, 0, 39, 19, 33, 31, 32, 38]

test2_5 = data.process_scrambled(labels, ['sen_word40_test2_5.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [3, 41, 39, 8, 22, 40, 1, 5, 30, 10, 23, 11, 15, 49, 20, 32, 45, 47, 19, 7, 36, 24, 42, 29, 43]

test2_6 = data.process_scrambled(labels, ['sen_word40_test2_6.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


test2_sequence_groups = data.combine([test2_1, test2_2, test2_3, test2_4, test2_5, test2_6])

print len(test2_sequence_groups)
print map(len, test2_sequence_groups)

lens = map(len, data.get_inputs(test2_sequence_groups)[0])
print min(lens), np.mean(lens), max(lens)


training_sequence_groups = data.combine([training_sequence_groups, test1_sequence_groups])

#validation_sequence_groups = test1_sequence_groups
validation_sequence_groups = test2_sequence_groups



# Split into training and validation data
#training_sequence_groups, validation_sequence_groups = data.split(sequence_groups, 1./5)

#def train_test_split(sequence_groups, test_indices):
#    training_sequence_groups = []
#    validation_sequence_groups = []
#    test_indices = set(test_indices)
#    for i in range(len(sequence_groups)):
#        if i in test_indices:
#            validation_sequence_groups.append(sequence_groups[i])
#            training_sequence_groups.append([])
#        else:
#            training_sequence_groups.append(sequence_groups[i])
#            validation_sequence_groups.append([])
#    return training_sequence_groups, validation_sequence_groups
#            
#training_sequence_groups, validation_sequence_groups = train_test_split(sequence_groups, range(2, 20, 5))
#print map(len, training_sequence_groups)
#print map(len, validation_sequence_groups)

#training_sequence_groups = data.transform.pad_truncate(training_sequence_groups, length)
#validation_sequence_groups = data.transform.pad_truncate(validation_sequence_groups, length)

# Format into sequences and labels
train_sequences, train_labels = data.get_inputs(training_sequence_groups)
val_sequences, val_labels = data.get_inputs(validation_sequence_groups)


train_sequences = transform_data(train_sequences)
val_sequences = transform_data(val_sequences)


# Calculate sample weights
#class_weights = compute_class_weight('balanced', np.unique(train_labels), train_labels)
#train_weights = class_weights[list(train_labels)]
train_weights = np.ones(len(train_labels))

#train_labels = tf.keras.utils.to_categorical(train_labels)
#val_labels = tf.keras.utils.to_categorical(val_labels)

words = np.array([
        'i',
        'am',
        'you',
        'are',
        'the',
        'want',
        'need',
        'cold',
        'hot',
        'food',
        'where',
        'what',
        'how',
        'feeling',
        'doing',
        'tired',
        'water',
        'hungry',
        'thirsty',
        'hello',
        'that',
        'probably',
        'thank',
        'of',
        'because',
        'not',
        'something',
        'different',
        'important',
        'assistance',
        'help',
        'bathroom',
        'good',
        'bad',
        'it',
        'is',
        'seem',
        'come',
        'family',
        'question',
    ])

label_map = [[32, 39, 24], [6, 23, 34], [39, 23, 10], [29, 35, 13], [2, 24, 34], [35, 14, 4], [14, 32, 13], [32, 23, 4], [24, 34, 35], [12, 37, 2], [33, 20, 34], [11, 35, 6], [23, 7, 16], [13, 20, 32], [3, 2, 25], [25, 4, 39], [24, 2, 5], [0, 1, 17], [25, 20, 27], [25, 26, 4], [20, 0, 6], [38, 3, 18], [10, 3, 8], [21, 3, 0], [15, 0, 1], [6, 14, 27], [14, 26, 10], [11, 1, 15], [39, 12, 1], [7, 16, 10], [26, 7, 16], [13, 7, 16], [21, 26, 28], [8, 9, 29], [21, 12, 37], [12, 33, 9], [21, 5, 30], [28, 9, 29], [5, 30, 11], [27, 9, 29], [36, 28, 38], [37, 30, 38], [37, 30, 11], [36, 27, 38], [36, 28, 19], [31, 35, 22], [12, 33, 20], [3, 21, 4], [6, 25, 11], [13, 23, 34], [1, 10, 0, 22], [2, 14, 26, 27], [5, 24, 32, 39], [19, 31, 8, 9], [12, 23, 17, 18], [20, 35, 24, 4], [34, 11, 2, 36], [26, 0, 1, 27], [9, 3, 25, 33], [14, 32, 16, 10], [37, 30, 13, 15], [16, 29, 21, 5], [6, 30, 7, 38], [5, 15, 31, 39], [36, 28, 17, 29], [28, 8, 33, 7], [38, 37, 15, 36], [18, 19, 35, 22], [0, 5, 26, 20], [23, 11, 3, 4], [14, 28, 25, 34], [27, 24, 2, 12], [30, 13, 32, 39], [33, 7, 9, 29], [21, 1, 10, 16], [38, 37, 15, 6], [17, 18, 36, 15], [22, 19, 31, 10], [3, 14, 34, 24], [20, 4, 39, 35], [23, 11, 2, 6], [37, 0, 1, 26], [13, 32, 25, 30], [28, 38, 12, 8], [33, 16, 5, 15], [21, 27, 9, 31], [33, 7, 36, 18], [2, 22, 17, 19], [35, 20, 24, 23], [12, 32, 3, 4], [13, 25, 6, 34], [0, 1, 27, 16], [36, 28, 39, 11], [37, 10, 33, 9], [29, 21, 26, 7], [5, 30, 29, 31], [15, 22, 18, 31], [20, 17, 19, 8], [14, 11, 0, 5], [34, 35, 21, 4], [38, 24, 23, 13, 17], [12, 33, 3, 25, 14], [10, 26, 7, 2, 15], [32, 39, 6, 36, 28], [38, 17, 1, 27, 16], [9, 29, 18, 22, 8], [19, 10, 0, 5, 33], [23, 34, 35, 25, 20], [11, 21, 24, 4, 32], [38, 12, 2, 3, 7], [13, 36, 26, 27, 16], [39, 8, 28, 9, 29], [18, 31, 0, 22, 19], [35, 26, 23, 34, 4], [28, 3, 32, 20, 15], [38, 13, 25, 14, 11], [1, 24, 14, 2, 27], [39, 8, 16, 36, 17], [29, 21, 30, 33, 9], [5, 30, 1, 10, 31], [20, 36, 18, 22, 19], [3, 14, 34, 24, 2], [10, 9, 35, 25, 11], [6, 32, 23, 4, 21], [5, 16, 0, 1, 13], [6, 30, 26, 33, 19], [30, 38, 7, 12, 18], [7, 22, 39, 12, 37], [26, 8, 31, 35, 17], [15, 23, 14, 34, 24], [10, 2, 3, 11, 4], [32, 38, 20, 0, 36], [16, 25, 27, 28, 9], [19, 29, 1, 15, 12], [5, 33, 13, 28, 22], [21, 30, 15, 27, 39], [17, 37, 6, 29, 31], [8, 38, 20, 4, 18], [2, 24, 34, 10, 28], [23, 12, 0, 1, 11], [39, 3, 21, 25, 14], [5, 9, 35, 13, 32], [31, 30, 6, 26, 8], [36, 8, 16, 15, 17], [22, 6, 29, 31, 18], [21, 25, 37, 23, 19], [6, 35, 4, 39, 20], [7, 0, 1, 14, 11], [38, 12, 33, 34, 27], [36, 32, 2, 3, 15], [28, 9, 33, 13, 17, 10], [37, 24, 26, 30, 22, 19], [13, 12, 28, 35, 4, 18], [32, 24, 23, 2, 20, 5], [11, 38, 0, 1, 25, 14], [34, 39, 3, 7, 16, 27], [10, 33, 29, 19, 6, 16], [17, 27, 15, 7, 9, 29], [5, 26, 36, 30, 19, 37], [8, 33, 31, 22, 4, 18], [8, 0, 37, 23, 34, 35], [37, 30, 20, 24, 2, 13], [21, 3, 25, 14, 28, 39], [32, 9, 11, 12, 38, 27], [15, 31, 10, 6, 26, 19], [17, 15, 18, 21, 0, 22], [39, 35, 25, 14, 11, 34], [10, 26, 24, 4, 13, 23], [37, 2, 12, 33, 20, 30], [3, 21, 32, 7, 16, 17], [29, 38, 16, 37, 6, 27], [2, 18, 31, 24, 22, 8], [34, 6, 14, 4, 5, 23], [37, 30, 13, 20, 0, 32], [21, 28, 39, 35, 11, 36], [3, 8, 17, 25, 10, 33], [1, 17, 12, 38, 36, 15], [26, 27, 28, 7, 16, 18], [19, 31, 22, 26, 10, 1], [34, 30, 2, 11, 9, 23], [13, 0, 1, 25, 32, 35], [24, 12, 33, 4, 21, 28], [14, 27, 3, 9, 39, 38], [8, 5, 20, 17, 22, 36], [7, 16, 37, 29, 8, 1], [31, 20, 29, 4, 18, 19], [11, 2, 6, 34, 14, 24], [27, 9, 3, 21, 35, 25], [38, 29, 23, 26, 32, 0], [36, 18, 10, 1, 13, 37], [31, 12, 22, 20, 10, 19], [25, 8, 16, 35, 4, 14], [33, 16, 23, 2, 21, 3], [13, 26, 0, 1, 24, 9], [31, 12, 11, 38, 36, 28], [6, 30, 9, 34, 15, 37], [7, 32, 30, 36, 31, 29], [6, 29, 8, 17, 27, 39], [19, 32, 25, 5, 22, 18], [23, 12, 0, 22, 4, 17]]

train_labels = np.array(map(lambda i: label_map[i], train_labels))
val_labels = np.array(map(lambda i: label_map[i], val_labels))

bigram_count_map = {}
for i in range(len(label_map)):
    for j in range(len(label_map[i])-1):
        key = tuple(label_map[i][j:j+2])
        bigram_count_map[key] = bigram_count_map.get(key, 0) + 1
trigram_count_map = {}
for i in range(len(label_map)):
    for j in range(len(label_map[i])-2):
        key = tuple(label_map[i][j:j+3])
        trigram_count_map[key] = trigram_count_map.get(key, 0) + 1
fourgram_count_map = {}
for i in range(len(label_map)):
    for j in range(len(label_map[i])-3):
        key = tuple(label_map[i][j:j+4])
        fourgram_count_map[key] = fourgram_count_map.get(key, 0) + 1
fivegram_count_map = {}
for i in range(len(label_map)):
    for j in range(len(label_map[i])-4):
        key = tuple(label_map[i][j:j+5])
        fivegram_count_map[key] = fivegram_count_map.get(key, 0) + 1
unigram_count_map = {unigram: count for (unigram, count) in\
                     zip(*np.unique(np.concatenate(label_map), return_counts=True))}
print unigram_count_map
print bigram_count_map
print len(bigram_count_map)
print trigram_count_map
print len(trigram_count_map)

print np.shape(train_sequences)
print np.shape(train_labels)
print np.shape(val_sequences)
print np.shape(val_labels)

num_classes = len(np.unique(reduce(lambda a,b: a+b, label_map))) + 1


learning_rate = 1e-4 #5e-4 #1e-3
dropout_rate = 0.4

sample_rate = 250
cnn_window_size = 1000 * sample_rate // 1000 #1000 #600 #1250
cnn_window_stride = 250 * sample_rate // 1000 #250 #100 #250
num_channels = 8

inputs = tf.placeholder(tf.float32,[None, None, cnn_window_size, num_channels]) #[batch_size,timestep,window,features]
targets = tf.sparse_placeholder(tf.int32)
sequence_lengths = tf.placeholder(tf.int32, [None])
weights = tf.placeholder(tf.float32, [None])
training = tf.placeholder(tf.bool)
batch_size = tf.shape(inputs)[0]
max_timesteps = tf.shape(inputs)[1]

vis_inputs = tf.placeholder(tf.float32, [None, cnn_window_size, num_channels])
vis_targets = tf.placeholder(tf.int32, [None, num_classes])

reshaped = tf.reshape(inputs, [-1, cnn_window_size, num_channels])

conv1 = tf.layers.conv1d(reshaped, 512, 50, activation=tf.nn.relu, padding='valid', name='conv1') # 3
conv1 = tf.layers.max_pooling1d(conv1, 2, strides=2)
conv2 = tf.layers.conv1d(conv1, 512, 25, activation=tf.nn.relu, padding='valid', name='conv2')
conv2 = tf.layers.max_pooling1d(conv2, 2, strides=2)
conv3 = tf.layers.conv1d(conv2, 512, 12, activation=tf.nn.relu, padding='valid', name='conv3')
conv3 = tf.layers.max_pooling1d(conv3, 2, strides=2)
conv4 = tf.layers.conv1d(conv3, 512, 12, activation=tf.nn.relu, padding='valid', name='conv4')
conv4 = tf.layers.max_pooling1d(conv4, 2, strides=2)
#conv5 = tf.layers.conv1d(conv4, 512, 12, activation=tf.nn.relu, padding='valid', name='conv5')
#conv5 = tf.layers.max_pooling1d(conv5, 2, strides=2)
dropout = tf.layers.dropout(conv4, dropout_rate, training=training)

vis_conv1 = tf.layers.conv1d(vis_inputs, 512, 50, activation=tf.nn.relu, padding='valid', name='conv1', reuse=True)
vis_conv1 = tf.layers.max_pooling1d(vis_conv1, 2, strides=2)
vis_conv2 = tf.layers.conv1d(vis_conv1, 512, 25, activation=tf.nn.relu, padding='valid', name='conv2', reuse=True)
vis_conv2 = tf.layers.max_pooling1d(vis_conv2, 2, strides=2)
vis_conv3 = tf.layers.conv1d(vis_conv2, 512, 12, activation=tf.nn.relu, padding='valid', name='conv3', reuse=True)
vis_conv3 = tf.layers.max_pooling1d(vis_conv3, 2, strides=2)
vis_conv4 = tf.layers.conv1d(vis_conv3, 512, 12, activation=tf.nn.relu, padding='valid', name='conv4', reuse=True)
vis_conv4 = tf.layers.max_pooling1d(vis_conv4, 2, strides=2)
#vis_conv5 = tf.layers.conv1d(vis_conv4, 512, 12, activation=tf.nn.relu, padding='valid', name='conv5', reuse=True)
#vis_conv5 = tf.layers.max_pooling1d(vis_conv5, 2, strides=2)
vis_dropout = tf.layers.dropout(vis_conv4, dropout_rate, training=False)



# EXPLORATORY (global average pooling)
#dropout = tf.reduce_mean(dropout, axis=1)

reshaped = tf.reshape(dropout, [-1, np.prod(dropout.shape[1:])])
vis_reshaped = tf.reshape(vis_dropout, [-1, np.prod(vis_dropout.shape[1:])])
#fc_size = 1024
#fc1 = tf.layers.dense(reshaped, fc_size, activation=tf.nn.relu)
#reshaped = tf.reshape(fc1, [batch_size, max_timesteps, fc_size])

#lstm_hidden_size = 256
#lstm1 = tf.nn.rnn_cell.LSTMCell(lstm_hidden_size, use_peepholes=True)
#dropout1 = tf.nn.rnn_cell.DropoutWrapper(lstm1, 1.0-dropout_rate)
#lstm1b = tf.nn.rnn_cell.LSTMCell(lstm_hidden_size, use_peepholes=True)
#dropout1b = tf.nn.rnn_cell.DropoutWrapper(lstm1b, 1.0-dropout_rate)
#lstm2 = tf.nn.rnn_cell.LSTMCell(lstm_hidden_size, use_peepholes=True)
#dropout2 = tf.nn.rnn_cell.DropoutWrapper(lstm2, 1.0-dropout_rate)
#lstm2b = tf.nn.rnn_cell.LSTMCell(lstm_hidden_size, use_peepholes=True)
#dropout2b = tf.nn.rnn_cell.DropoutWrapper(lstm2b, 1.0-dropout_rate)
#
#forward_stack = tf.nn.rnn_cell.MultiRNNCell([dropout2])
#backward_stack = tf.nn.rnn_cell.MultiRNNCell([dropout2b])
#
#outputs, states = tf.nn.bidirectional_dynamic_rnn(forward_stack, backward_stack, inputs, dtype=tf.float32)
#outputs = tf.concat(outputs, 2)
#
#reshaped = tf.reshape(outputs, [-1, 2 * lstm_hidden_size])

#reshaped = tf.layers.dense(reshaped, 1024, activation=tf.nn.relu,
#            kernel_initializer=tf.initializers.truncated_normal(stddev=np.sqrt(2.0/(2 * lstm_hidden_size * 1024))))

fc_size = 1024 #512

reshaped = tf.layers.dense(reshaped, fc_size, activation=tf.nn.relu,
    kernel_initializer=tf.initializers.truncated_normal(stddev=np.sqrt(2.0/(int(np.prod(dropout.shape[1:])) * fc_size))), name='fc1')
reshaped = tf.layers.dense(reshaped, fc_size, activation=tf.nn.relu,
            kernel_initializer=tf.initializers.truncated_normal(stddev=np.sqrt(2.0/(fc_size * fc_size))),
                           name='fc2')
logits = tf.layers.dense(reshaped, num_classes,
            kernel_initializer=tf.initializers.truncated_normal(stddev=np.sqrt(2.0/(fc_size * num_classes))),
                         name='fc3')

vis_reshaped = tf.layers.dense(vis_reshaped, fc_size, activation=tf.nn.relu, name='fc1', reuse=True)
vis_reshaped = tf.layers.dense(vis_reshaped, fc_size, activation=tf.nn.relu, name='fc2', reuse=True)
vis_logits = tf.layers.dense(vis_reshaped, num_classes, name='fc3', reuse=True)


logits = tf.reshape(logits, [batch_size, -1, num_classes])

vis_logits = tf.reshape(vis_logits, [tf.shape(vis_inputs)[0], -1, num_classes])
vis_loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=vis_logits, labels=vis_targets))
vis_gradients = tf.gradients(vis_loss, vis_inputs)
vis_gradients /= tf.sqrt(tf.reduce_mean(tf.square(vis_gradients))) + 1e-5

logits = tf.transpose(logits, [1, 0, 2])

#loss = tf.reduce_mean(tf.multiply(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=targets), weights))
loss = tf.nn.ctc_loss(labels=targets, inputs=logits, sequence_length=sequence_lengths, time_major=True)
loss = tf.reduce_mean(tf.multiply(loss, weights))

# L2 regularization
#l2 = 0.005 * sum([tf.nn.l2_loss(tf_var) for tf_var in tf.trainable_variables()\
#                          if 'noreg' not in tf_var.name.lower() and 'bias' not in tf_var.name.lower()])
#loss += l2

optimizer = tf.train.AdamOptimizer(learning_rate).minimize(loss)
#optimizer = tf.train.RMSPropOptimizer(learning_rate).minimize(loss)

#opt = tf.train.RMSPropOptimizer(learning_rate)
#gradients = opt.compute_gradients(loss)
#clipped_gradients = [(tf.clip_by_value(grad, -1., 1.), var) for grad, var in gradients]
#optimizer = opt.apply_gradients(clipped_gradients)

#decoded, log_prob = tf.nn.ctc_greedy_decoder(logits, sequence_lengths)
ctc_output = tf.nn.ctc_beam_search_decoder(logits, sequence_lengths, top_paths=10) # 10
decoded, log_prob = ctc_output[0], ctc_output[1]

error = tf.reduce_mean(tf.edit_distance(tf.cast(decoded[0], tf.int32), targets, normalize=True))

decoded_selected = tf.sparse_placeholder(tf.int32)
#decoded_selected = tf.placeholder(tf.int32, [None, None])
#sparse_decoded_selected = tf.contrib.layers.dense_to_sparse(decoded_selected, eos_token=-1)
error_selected = tf.edit_distance(decoded_selected, targets, normalize=True)


num_epochs = 20000 #200
batch_size = 20 #20 #50

num_training_samples = len(train_sequences)
num_validation_samples = len(val_sequences)
num_training_batches = max(1, int(num_training_samples / batch_size))
num_validation_batches = max(1, int(num_validation_samples / batch_size))
start_time = None
last_time = None

# Table display
progress_bar_size = 20
max_batches = max(num_training_batches, num_validation_batches)
layout = [
    dict(name='Ep.', width=len(str(num_epochs)), align='center'),
    dict(name='Batch', width=2*len(str(max_batches))+1, align='center'),
#    dict(name='', width=0, align='center'),
    dict(name='Progress/Timestamp', width=progress_bar_size+2, align='center'),
    dict(name='ETA/Elapsed', width=7, suffix='s', align='center'),
    dict(name='', width=0, align='center'),
    dict(name='Train Loss', width=8, align='center'),
    dict(name='Train Err', width=7, align='center'),
    dict(name='', width=0, align='center'),
    dict(name='Val Loss', width=8, align='center'),
    dict(name='Val Err', width=7, align='center'),
    dict(name='', width=0, align='center'),
    dict(name='Min Val Err', width=7, align='center'),
]

training_losses = []
training_errors = []
validation_losses = []
validation_errors = []

since_training = 0
def update_table(epoch, batch, training_loss, training_error, min_validation_error,
                 validation_loss=None, validation_error=None, finished=False):
    global last_time
    global since_training
    num_batches = num_training_batches if validation_loss is None else num_validation_batches
    progress = int(math.ceil(progress_bar_size * float(batch) / num_batches))
#    progress_string = '[' + '#' * progress + ' ' * (progress_bar_size - progress) + ']'
    status = ' Training' if validation_loss is None else ' Validating'
    status = status[:max(0, progress_bar_size - progress)]
    progress_string = '[' + '#' * progress + status + ' ' * (progress_bar_size - progress - len(status)) + ']'
    now = time.time()
    start_elapsed = now - start_time
    if validation_loss is None:
        epoch_elapsed = now - last_time
        since_training = now
    else:
        epoch_elapsed = now - since_training
    batch_time_estimate = epoch_elapsed / batch if batch else 0.0
    eta_string = batch_time_estimate * (num_batches - batch) or '--'
    if finished:
        epoch_elapsed = now - last_time
        last_time = now
        progress_string = time.strftime("%I:%M:%S %p",time.localtime())+'; '+str(int(start_elapsed*10)/10.)+'s'
        eta_string = epoch_elapsed
        training_losses.append(training_loss)
        training_errors.append(training_error)
        validation_losses.append(validation_loss)
        validation_errors.append(validation_error)
    table.update(epoch + 1, str(batch + 1) + '/' + str(num_batches),
                 progress_string, eta_string, '',
                 training_loss or '--', training_error or '--', '',
                 validation_loss or '--', validation_error or '--', '',
                 min_validation_error if finished else '--')
#    if finished and (epoch + 1) % 10 == 0:
#        print
#        print 'training_losses =', training_losses
#        print
#        print 'training_errors =', training_errors
#        print
#        print 'validation_losses =', validation_losses
#        print
#        print 'validation_errors =', validation_errors
            
def sparsify(labels):
    indices = []
    values = []
    for n, seq in enumerate(labels):
        indices.extend(zip([n]*len(seq), range(len(seq))))
        values.extend(seq)
    indices = np.asarray(indices, dtype=np.int64)
    values = np.asarray(values, dtype=np.int32)
    shape = np.asarray([len(labels), max(map(len, labels))], dtype=np.int64)
    return indices, values, shape

def window_split(sequence, window, stride=None, step=1):
    if stride is None: stride = window
    return np.array([sequence[i:i+window:step] for i in range(0, len(sequence)-window+1, stride)])

saver = tf.train.Saver()
with tf.Session() as session:
    tf.global_variables_initializer().run()
    
    table = DynamicConsoleTable(layout)
    table.print_header()
    
    start_time = time.time()
    last_time = start_time
    
    min_validation_error = float('inf')
    errors = []
    ks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    error_top_ks = [[] for _ in range(len(ks))]
    error_top_ks_orig = [[] for _ in range(len(ks))]
    for epoch in range(num_epochs):
        training_loss = 0.0
        training_error = 0.0
        permutation = np.random.permutation(num_training_samples)
        train_sequences = train_sequences[permutation]
        train_labels = train_labels[permutation]
        train_weights = train_weights[permutation]
        training_decoded = []
        training_log_probs = []
        for batch in range(num_training_batches):            
            indices = range(batch * batch_size, (batch + 1) * batch_size)
            if batch == num_training_batches - 1:
                indices = range(batch * batch_size, num_training_samples)
            batch_sequences = train_sequences[indices]
#            print np.shape(batch_sequences)
            tmp_lengths = map(len, batch_sequences)
            tmp = np.array(map(lambda seq: window_split(seq, cnn_window_size, stride=cnn_window_stride),
                               batch_sequences))
            batch_lengths = map(len, tmp)
            batch_sequences = data.transform.pad_truncate(batch_sequences, max(tmp_lengths), position=0.0)
            batch_sequences = np.array(map(lambda seq: window_split(seq, cnn_window_size, stride=cnn_window_stride),
                                           batch_sequences))
#            print np.shape(batch_sequences)
            batch_labels = train_labels[indices]
            batch_weights = train_weights[indices]
            sparse_batch_labels = sparsify(batch_labels)
            
            update_table(epoch, batch, training_loss / (batch_size * max(1, batch)),
                         training_error / (batch_size * max(1, batch)), min_validation_error)
                        
            training_feed = {inputs: batch_sequences, targets: sparse_batch_labels,
                             sequence_lengths: batch_lengths, weights: batch_weights, training: True}
            batch_loss, _, batch_decoded, batch_error, batch_log_prob = \
                                    session.run([loss, optimizer, decoded, error, log_prob], training_feed)
            
            training_loss += batch_loss * len(indices)
            training_error += batch_error * len(indices)
#            batch_decoded = tf.sparse_tensor_to_dense(batch_decoded[0], default_value=-1).eval()
            batch_decoded = map(lambda x: tf.sparse_tensor_to_dense(x, default_value=-1).eval(), batch_decoded)
            for i in range(len(batch_decoded[0])):
                training_decoded.append([])
                for j in range(len(batch_decoded)):
                    training_decoded[-1].append(batch_decoded[j][i])
            for log_probs in batch_log_prob:
                training_log_probs.append(log_probs)
            
        training_loss /= num_training_samples
        training_error /= num_training_samples
                
        validation_loss = 0.0
        validation_error = 0.0
        validation_error_top_ks = [0.0] * len(ks)
        validation_error_top_ks_orig = [0.0] * len(ks)
        permutation = np.random.permutation(num_validation_samples)
        val_sequences = val_sequences[permutation]
        val_labels = val_labels[permutation]
        validation_decoded = []
        validation_log_probs = []
        for batch in range(num_validation_batches):         
            indices = range(batch * batch_size, (batch + 1) * batch_size)
            if batch == num_validation_batches - 1:
                indices = range(batch * batch_size, num_validation_samples)
            batch_sequences = val_sequences[indices]
#            print np.shape(batch_sequences)
            tmp_lengths = map(len, batch_sequences)
            tmp = np.array(map(lambda seq: window_split(seq, cnn_window_size, stride=cnn_window_stride),
                               batch_sequences))
            batch_lengths = map(len, tmp)
            batch_sequences = data.transform.pad_truncate(batch_sequences, max(tmp_lengths), position=0.0)
            batch_sequences = np.array(map(lambda seq: window_split(seq, cnn_window_size, stride=cnn_window_stride),
                                           batch_sequences))
#            print np.shape(batch_sequences)
            batch_labels = val_labels[indices]
            batch_weights = np.ones(len(indices))
            sparse_batch_labels = sparsify(batch_labels)
                        
            update_table(epoch, batch, training_loss, training_error, min_validation_error,
                         validation_loss / (batch_size * max(1, batch)),
                         validation_error / (batch_size * max(1, batch)))
            
            validation_feed = {inputs: batch_sequences, targets: sparse_batch_labels,
                               sequence_lengths: batch_lengths, weights: batch_weights, training: False}
            batch_loss, batch_error, batch_decoded, batch_log_prob = \
                                            session.run([loss, error, decoded, log_prob], validation_feed)
            validation_loss += batch_loss * len(indices)
            validation_error += batch_error * len(indices)
            
            batch_decoded = map(lambda x: tf.sparse_tensor_to_dense(x, default_value=-1).eval(), batch_decoded)
            
            # Calculate the most likely path based on language model
#            for i in range(len(batch_decoded)):
#                tmp = filter(lambda x: x > -1, batch_decoded[i][0])
#                print tmp
#                print batch_log_prob[0][i]
#                for j in range(len(tmp)-1):
#                    key = tuple(tmp[j:j+2])
#                    print key, 1.0 if key in bigram_count_map else 0.0
#                for j in range(len(tmp)-2):
#                    key = tuple(tmp[j:j+3])
#                    print key, 1.0 if key in trigram_count_map else 0.0
                    
            # modifies probabilities
            for i in range(len(batch_decoded)):
                for j in range(len(batch_decoded[i])):
                    tmp = filter(lambda x: x > -1, batch_decoded[i][j])
#                    print tmp
#                    print batch_log_prob[j][i]
                    for k in range(len(tmp)-1):
                        key = tuple(tmp[k:k+2])
                        batch_log_prob[j][i] += np.log(1.0 if key in bigram_count_map else 0.5)
                    for k in range(len(tmp)-2):
                        key = tuple(tmp[k:k+3])
                        batch_log_prob[j][i] += np.log(1.0 if key in trigram_count_map else 0.5)
                    for k in range(len(tmp)-3):
                        key = tuple(tmp[k:k+4])
                        batch_log_prob[j][i] += np.log(1.0 if key in fourgram_count_map else 0.5)
                    for k in range(len(tmp)-4):
                        key = tuple(tmp[k:k+5])
                        batch_log_prob[j][i] += np.log(1.0 if key in fivegram_count_map else 0.5)
                
            batch_decoded_selected = batch_decoded[0]
            batch_decoded_selected = map(list, map(lambda x: x[np.where(x > -1)], batch_decoded_selected))
            
#            print
#            print batch_decoded_selected


            batch_decoded_selected_orig = []
            for i in range(len(batch_decoded[0])):
                pairs = [(batch_log_prob[i][j], batch_decoded[j][i]) for j in range(len(batch_decoded))]
#                pairs = sorted(pairs, key=lambda x: x[0])
#                pairs = pairs[::-1]
                selected = map(lambda p: p[1][np.where(p[1] > -1)], pairs)
                batch_decoded_selected_orig.append(list(selected))

            top_k = max(ks)
            batch_decoded_selected_orig = map(lambda x: x[:top_k], batch_decoded_selected_orig)
            batch_decoded_selected_orig = np.reshape(batch_decoded_selected_orig, [-1])
            batch_labels = val_labels[indices]
            batch_labels_top_k_orig = []
            for i in range(len(batch_labels)):
                batch_labels_top_k_orig.extend([batch_labels[i] for _ in range(top_k)])
#            batch_labels_top_k = np.reshape(batch_labels_top_k, [-1])
#            print np.shape(batch_labels_top_k)
#            batch_labels_top_k = np.array(batch_labels_top_k)
#            print np.shape(batch_labels_top_k)
            sparse_batch_labels_top_k_orig = sparsify(batch_labels_top_k_orig)
            
            sparse_indices, value, shape = sparsify(batch_decoded_selected_orig)
            if not len(sparse_indices):
                sparse_indices = np.zeros((0, 2))
            
            selected_feed = {decoded_selected: (sparse_indices, value, shape), targets: sparse_batch_labels_top_k_orig}
            batch_error_selected_orig = session.run(error_selected, selected_feed)
#            batch_error_selected = np.transpose(np.reshape(batch_error_selected, [top_k, -1]))
            batch_error_selected_orig = np.reshape(batch_error_selected_orig, [-1, top_k])
    


            
            batch_decoded_selected = []
            for i in range(len(batch_decoded[0])):
                pairs = [(batch_log_prob[i][j], batch_decoded[j][i]) for j in range(len(batch_decoded))]
                pairs = sorted(pairs, key=lambda x: x[0])
                pairs = pairs[::-1]
                selected = map(lambda p: p[1][np.where(p[1] > -1)], pairs)
                batch_decoded_selected.append(list(selected))

            top_k = max(ks)
            batch_decoded_selected = map(lambda x: x[:top_k], batch_decoded_selected)
            batch_decoded_selected = np.reshape(batch_decoded_selected, [-1])
            batch_labels = val_labels[indices]
            batch_labels_top_k = []
            for i in range(len(batch_labels)):
                batch_labels_top_k.extend([batch_labels[i] for _ in range(top_k)])
#            batch_labels_top_k = np.reshape(batch_labels_top_k, [-1])
#            print np.shape(batch_labels_top_k)
#            batch_labels_top_k = np.array(batch_labels_top_k)
#            print np.shape(batch_labels_top_k)
            sparse_batch_labels_top_k = sparsify(batch_labels_top_k)
            
            sparse_indices, value, shape = sparsify(batch_decoded_selected)
            if not len(sparse_indices):
                sparse_indices = np.zeros((0, 2))
            
            selected_feed = {decoded_selected: (sparse_indices, value, shape), targets: sparse_batch_labels_top_k}
            batch_error_selected = session.run(error_selected, selected_feed)
#            batch_error_selected = np.transpose(np.reshape(batch_error_selected, [top_k, -1]))
            batch_error_selected = np.reshape(batch_error_selected, [-1, top_k])
    
    
    
            for i in range(len(ks)):
                tmp_error = np.min(batch_error_selected[:,:ks[i]], axis=1)
#                print tmp_error
                tmp_error = np.mean(tmp_error)
                validation_error_top_ks[i] += tmp_error * len(indices)
                tmp_error = np.min(batch_error_selected_orig[:,:ks[i]], axis=1)
#                print tmp_error
                tmp_error = np.mean(tmp_error)
                validation_error_top_ks_orig[i] += tmp_error * len(indices)
                        
#            print batch_error, batch_error_selected
            
            for i in range(len(batch_decoded[0])):
                validation_decoded.append([])
                for j in range(len(batch_decoded)):
                    validation_decoded[-1].append(batch_decoded[j][i])
            for log_probs in batch_log_prob:
                validation_log_probs.append(log_probs)
                
        validation_loss /= num_validation_samples
        validation_error /= num_validation_samples
        
        errors.append(validation_error)
        for i in range(len(ks)):
            validation_error_top_ks[i] /= num_validation_samples
            validation_error_top_ks_orig[i] /= num_validation_samples
            error_top_ks[i].append(validation_error_top_ks[i])
            error_top_ks_orig[i].append(validation_error_top_ks_orig[i])
            
#        min_validation_error = min(validation_error_top_ks[np.argmax(ks)], min_validation_error)
        if validation_error_top_ks[0] < min_validation_error:
            model_name = 'ctc_cnn_sen_word40_test_model.ckpt'
            save_path = saver.save(session, os.path.join(abs_path, model_name))
            print ' Model saved:', model_name,
        min_validation_error = min(validation_error_top_ks[0], min_validation_error)
        
        print
        print validation_error
        for i in range(len(ks)):
            print validation_error_top_ks_orig[i], '\t',
        print
        for i in range(len(ks)):
            print validation_error_top_ks[i], '\t',
        print

#        plt.figure(1)
#        plt.gcf().clear()
#        plt.plot(errors)
#        for i in range(len(ks)):
#            plt.plot(error_top_ks[i])
#        plt.pause(0.00001)
        
#        avg_kernel = normalize_kernel([1.0] * (sample_rate // 20))
#        def deprocess(x):
##            x -= np.mean(x)
##            x /= (np.std(x) + 1e-5)
#            x = data.transform.correlate(x, avg_kernel)
##            x *= 0.1
##            x += 0.5
##            x = np.clip(x, 0, 1)
##            x *= 255
###            x = np.transpose(x, (1, 2, 0))
##            x = np.clip(x, 0, 255).astype('uint8')
#            return x
#        test_index = 0
#        num_copies = 10 #20
#        if (epoch+1) % 1 == 0:
##            test_input = np.random.rand((num_classes-1)*num_copies, cnn_window_size, num_channels) * 2 - 1.0
#            test_input = np.zeros(((num_classes-1)*num_copies, cnn_window_size, num_channels))
#            for i in range(300):
#                test_targets = np.zeros(((num_classes-1)*num_copies, num_classes))
#                for c in range(num_classes-1):
#                    test_targets[c*num_copies:(c+1)*num_copies,c] = 1.0
#                gradients_output, logits_output = session.run([vis_gradients, vis_logits],
#                                                              {vis_inputs: test_input, vis_targets: test_targets})
#                test_input += gradients_output[0] * 0.02
#                print logits_output[0]
##                test_input += (np.random.rand(num_classes-1, cnn_window_size, num_channels) - 0.5) * 0.02
#                if (i+1) % 15 == 0 or i == 0:
#                    plt.gcf().clear()
#                    plt.plot(deprocess(np.mean(test_input[test_index*num_copies:(test_index+1)*num_copies,:,:], axis=0)))
#                    plt.pause(0.00001)
#                    print i+1


        if (epoch+1) % 10 == 0:
            print 'errors =', errors
            print 'error_top_ks_orig =', error_top_ks_orig
            print 'error_top_ks =', error_top_ks
            
        
        update_table(epoch, batch, training_loss, training_error,
                     min_validation_error, validation_loss, validation_error, finished=True)
        print
#        print 'Training:'
#        for i in range(min(5, len(training_decoded))):
##            print train_labels[i], ' => ', training_decoded[i][np.where(training_decoded[i] > -1)]
#            print '\t', ' '.join(words[train_labels[i]]), ' =>'
#            pairs = zip(training_log_probs[i], range(len(training_decoded[i])))
#            pairs = sorted(pairs)[::-1]
#            for j in range(len(training_decoded[i])):
#                print '\t\t', np.exp(training_log_probs[i][j]), '\t', \
#                ' '.join(words[training_decoded[i][j][np.where(training_decoded[i][j] > -1)]]), \
#                '\t\t\t', np.exp(pairs[j][0]), '\t', \
#                ' '.join(words[training_decoded[i][pairs[j][1]][
#                            np.where(training_decoded[i][pairs[j][1]] > -1)]])
        print 'Validation:'
        for i in range(min(5, len(validation_decoded))):
#            print val_labels[i], ' => ', validation_decoded[i][np.where(validation_decoded[i] > -1)]
            print '\t', ' '.join(words[val_labels[i]]), ' =>'
            pairs = zip(validation_log_probs[i], range(len(validation_decoded[i])))
            pairs = sorted(pairs)[::-1]
            for j in range(len(validation_decoded[i])):
                print '\t\t', np.exp(validation_log_probs[i][j]), '\t', \
                ' '.join(words[validation_decoded[i][j][np.where(validation_decoded[i][j] > -1)]]), \
                '\t\t\t', np.exp(pairs[j][0]), '\t', \
                ' '.join(words[validation_decoded[i][pairs[j][1]][
                            np.where(validation_decoded[i][pairs[j][1]] > -1)]])
            
        
        reprint_header = (epoch+1) % 10 == 0 and epoch < num_epochs - 1
        table.finalize(divider=not reprint_header)
        if reprint_header:
            table.print_header()
