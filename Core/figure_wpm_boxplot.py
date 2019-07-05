import os
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import math
import time

import data

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
surrounding = 0 #250

labels = [64, 148, 125, 66, 181, 106, 191, 94, 79, 170, 144, 55, 152, 101, 128, 92, 142, 116, 81, 85, 140, 134, 127, 90, 175, 149, 83, 69, 123, 196, 141, 185, 119, 178, 164, 98, 103, 78, 104, 158, 162, 67, 169, 153, 108, 168, 68, 54, 95, 109, 89, 86, 167, 189, 157, 182, 176, 135, 172, 145, 61, 163, 173, 62, 52, 154, 56, 177, 160, 115, 105, 194, 188, 96, 112, 124, 166, 143, 150, 139, 60, 84, 82, 174, 88, 133, 161, 199, 77, 73, 117, 59, 180, 147, 155, 195, 137, 198, 159, 114]

train_1 = data.process_scrambled(labels, ['sen200_train_1.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)

labels = [109, 104, 110, 88, 119, 133, 117, 138, 59, 157, 161, 178, 70, 91, 153, 167, 136, 94, 51, 147, 112, 168, 164, 170, 93, 81, 84, 132, 160, 195, 115, 95, 152, 198, 127, 105, 193, 65, 89, 149, 188, 177, 101, 53, 97, 176, 74, 54, 134, 63, 75, 121, 69, 126, 174, 118, 144, 103, 124, 190, 106, 107, 139, 145, 185, 123, 55, 140, 60, 83, 67, 62, 114, 116, 73, 129, 98, 90, 58, 80, 163, 111, 179, 79, 166, 135, 57, 181, 100, 102, 175, 189, 183, 184, 120, 158, 50, 99, 141, 82]

train_2 = data.process_scrambled(labels, ['sen200_train_2.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)

labels = [168, 165, 171, 79, 188, 58, 56, 173, 85, 52, 181, 108, 61, 163, 179, 142, 152, 54, 190, 104, 144, 123, 192, 131, 154, 125, 67, 117, 155, 72, 176, 141, 55, 95, 148, 113, 126, 186, 172, 139, 121, 129, 175, 143, 84, 150, 162, 136, 94, 74, 101, 63, 68, 98, 167, 151, 197, 140, 199, 71, 97, 92, 166, 164, 69, 161, 107, 115, 189, 102, 195, 149, 100, 157, 120, 110, 194, 65, 114, 130, 105, 196, 51, 75, 138, 132, 76, 159, 62, 193, 135, 111, 184, 127, 64, 112, 183, 57, 147, 82]

train_3 = data.process_scrambled(labels, ['sen200_train_3.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([21]), num_classes=200)

labels = [106, 169, 141, 122, 166, 135, 103, 105, 194, 75, 62, 136, 170, 167, 55, 162, 183, 90, 51, 188, 165, 65, 186, 185, 148, 131, 95, 139, 179, 89, 99, 171, 84, 129, 94, 83, 140, 192, 158, 195, 196, 156, 134, 154, 57, 108, 125, 193, 66, 157, 151, 173, 64, 96, 138, 144, 178, 87, 85, 78, 187, 121, 79, 53, 52, 56, 123, 93, 97, 74, 60, 168, 61, 63, 143, 181, 104, 190, 153, 130, 58, 82, 152, 150, 71, 67, 86, 69, 116, 137, 182, 119, 199, 73, 176, 112, 109, 132, 160, 175]

train_4 = data.process_scrambled(labels, ['sen200_train_4.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)

labels = [141, 125, 118, 62, 180, 61, 122, 123, 166, 145, 78, 142, 199, 151, 132, 115, 102, 177, 181, 56, 182, 140, 73, 80, 152, 76, 186, 168, 150, 67, 52, 129, 105, 95, 124, 59, 70, 87, 103, 172, 100, 164, 196, 88, 163, 58, 66, 106, 133, 153, 86, 138, 55, 54, 136, 149, 171, 193, 176, 195, 121, 192, 135, 79, 173, 92, 77, 97, 119, 112, 90, 114, 108, 191, 167, 147, 117, 190, 155, 57, 128, 175, 83, 162, 84, 183, 75, 148, 91, 65, 187, 63, 98, 198, 161, 89, 81, 107, 85, 139]

train_5 = data.process_scrambled(labels, ['sen200_train_5.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([49]), num_classes=200)

labels = [143, 136, 199, 120, 179, 67, 161, 146, 162, 141, 107, 78, 133, 91, 112, 193, 169, 130, 159, 90, 98, 54, 189, 113, 163, 52, 101, 63, 85, 123, 157, 95, 69, 181, 132, 152, 73, 197, 104, 74, 153, 70, 72, 151, 97, 177, 122, 68, 168, 148, 115, 58, 160, 192, 138, 158, 55, 92, 56, 185, 99, 140, 81, 65, 61, 62, 144, 108, 100, 172, 186, 142, 176, 121, 156, 116, 170, 135, 137, 110, 187, 198, 102, 134, 149, 64, 106, 150, 93, 57, 96, 183, 178, 87, 195, 191, 164, 155, 154, 105]

train_6 = data.process_scrambled(labels, ['sen200_train_6.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)

labels = [95, 150, 60, 83, 154, 193, 130, 158, 54, 152, 172, 112, 195, 93, 186, 149, 159, 105, 175, 81, 56, 59, 138, 58, 109, 72, 66, 183, 198, 178, 160, 69, 179, 115, 84, 99, 77, 125, 101, 108, 168, 136, 165, 120, 61, 76, 173, 62, 82, 148, 51, 164, 88, 194, 137, 117, 86, 100, 64, 197, 155, 67, 161, 85, 124, 123, 50, 114, 121, 53, 187, 169, 116, 145, 96, 199, 57, 185, 91, 65, 151, 94, 167, 147, 75, 126, 191, 143, 111, 128, 140, 89, 107, 180, 142, 102, 181, 129, 122, 133]

train_7 = data.process_scrambled(labels, ['sen200_train_7.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)

training_sequence_groups = data.combine([train_1, train_2, train_3, train_4, train_5, train_6, train_7])

print len(training_sequence_groups)
print map(len, training_sequence_groups)

lens = map(len, data.get_inputs(training_sequence_groups)[0])
print min(lens), np.mean(lens), max(lens)


labels = [182, 51, 164, 112, 160, 77, 141, 86, 135, 148, 138, 61, 189, 121, 62, 68, 87, 109, 161, 115, 169, 177, 152, 171, 168]

test1_1 = data.process_scrambled(labels, ['sen200_test1_1.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [111, 125, 181, 58, 195, 60, 103, 91, 97, 56, 171, 70, 139, 150, 118, 188, 183, 73, 119, 63, 124, 122, 190, 114, 145]

test1_2 = data.process_scrambled(labels, ['sen200_test1_2.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [145, 64, 66, 187, 70, 183, 170, 152, 144, 178, 146, 56, 181, 59, 173, 111, 130, 150, 118, 80, 166, 74, 83, 165, 77]

test1_3 = data.process_scrambled(labels, ['sen200_test1_3.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [124, 188, 154, 58, 100, 79, 94, 130, 146, 72, 54, 66, 187, 135, 125, 149, 122, 87, 172, 63, 68, 80, 115, 180, 183]

test1_4 = data.process_scrambled(labels, ['sen200_test1_4.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [186, 90, 128, 166, 105, 160, 95, 158, 92, 168, 187, 199, 173, 178, 124, 118, 97, 130, 66, 141, 64, 86, 174, 162, 54]

test1_5 = data.process_scrambled(labels, ['sen200_test1_5.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [76, 180, 65, 187, 139, 127, 117, 96, 137, 152, 149, 63, 172, 142, 175, 71, 118, 186, 156, 69, 191, 99, 124, 54, 126]

test1_6 = data.process_scrambled(labels, ['sen200_test1_6.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


test1_sequence_groups = data.combine([test1_1, test1_2, test1_3, test1_4, test1_5, test1_6])

print len(test1_sequence_groups)
print map(len, test1_sequence_groups)

lens = map(len, data.get_inputs(test1_sequence_groups)[0])
print min(lens), np.mean(lens), max(lens)


labels = [41, 14, 36, 39, 28, 11, 17, 21, 38, 29, 8, 35, 23, 42, 45, 31, 10, 46, 4, 13, 24, 16, 15, 19, 40]

test2_1 = data.process_scrambled(labels, ['sen200_test2_1.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [22, 29, 17, 37, 46, 26, 30, 18, 20, 43, 12, 7, 27, 48, 15, 47, 1, 45, 23, 40, 19, 6, 13, 44, 4]

test2_2 = data.process_scrambled(labels, ['sen200_test2_2.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [48, 29, 43, 37, 15, 33, 17, 1, 7, 25, 31, 32, 5, 44, 26, 40, 24, 4, 30, 19, 34, 38, 6, 27, 36]

test2_3 = data.process_scrambled(labels, ['sen200_test2_3.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [10, 31, 21, 11, 6, 8, 32, 9, 22, 48, 1, 44, 45, 36, 27, 3, 40, 38, 25, 47, 41, 13, 16, 37, 34]

test2_4 = data.process_scrambled(labels, ['sen200_test2_4.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [15, 41, 1, 9, 6, 23, 29, 18, 13, 7, 44, 5, 26, 12, 36, 24, 16, 47, 0, 39, 19, 33, 31, 32, 38]

test2_5 = data.process_scrambled(labels, ['sen200_test2_5.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


labels = [3, 41, 39, 8, 22, 40, 1, 5, 30, 10, 23, 11, 15, 49, 20, 32, 45, 47, 19, 7, 36, 24, 42, 29, 43]

test2_6 = data.process_scrambled(labels, ['sen200_test2_6.txt'], channels=channels, sample_rate=250,
                                 surrounding=surrounding, exclude=set([]), num_classes=200)


test2_sequence_groups = data.combine([test2_1, test2_2, test2_3, test2_4, test2_5, test2_6])

print len(test2_sequence_groups)
print map(len, test2_sequence_groups)

lens = map(len, data.get_inputs(test2_sequence_groups)[0])
print min(lens), np.mean(lens), max(lens)



validation_sequence_groups = test1_sequence_groups
#validation_sequence_groups = test2_sequence_groups



all_sequence_groups = data.combine([training_sequence_groups, test1_sequence_groups, test2_sequence_groups])



#all_sequences, all_labels = data.get_inputs(all_sequence_groups)
all_sequences, all_labels = data.get_inputs(training_sequence_groups)

train_sequences, train_labels = data.get_inputs(training_sequence_groups)
val_sequences, val_labels = data.get_inputs(validation_sequence_groups)


all_sequences = transform_data(all_sequences)
train_sequences = transform_data(train_sequences)
val_sequences = transform_data(val_sequences)


label_map = [[11, 1, 0, 14], [10, 4, 9], [3, 10, 2], [12, 3, 2, 5, 0], [11, 3, 2, 14, 4], [14, 2, 12], [10, 16, 3, 14, 11, 0], [1, 11, 0, 4, 16, 10], [13, 4, 6, 9], [1, 7, 16], [8, 16, 12, 9, 7], [12, 1, 5, 8, 9, 7], [19, 18, 17, 5, 4, 15], [6, 0, 3, 11, 2, 17], [19, 18, 15, 13, 4, 6], [12, 11, 10, 2, 3, 13], [0, 1, 14], [7, 16, 10], [13, 12, 7, 16], [1, 13, 15], [18, 17, 3, 10, 8, 19], [12, 2, 14, 4, 17], [16, 1, 15, 14, 11, 0], [8, 6, 3, 18, 19, 5], [1, 0, 4, 16, 2, 6], [13, 15, 12, 8, 5, 9], [14, 11, 6, 9], [7, 13, 15], [9, 7, 13, 8], [5, 2, 18, 19, 17], [1, 0, 3, 4, 12], [15, 16, 5, 11, 10, 9], [7, 9, 13, 18], [19, 1, 2, 17], [14, 11, 0, 5], [3, 10, 4, 13, 12], [16, 10, 8, 9], [6, 14, 4, 17, 19, 18], [1, 10, 0], [3, 11, 2], [15, 19, 8, 16, 12, 18], [17, 0, 6, 2], [9, 3, 16, 10, 4, 14], [6, 11, 1, 15, 7, 13], [13, 7, 9], [6, 14, 15, 12, 8], [5, 6, 18], [10, 17, 19, 14, 11, 4], [12, 2, 3, 13], [0, 1, 17], [17, 8, 9], [5, 6, 16], [19, 3, 18], [14, 4, 7], [12, 0, 1, 10, 16], [5, 11, 2, 6], [6, 9, 7, 13], [5, 18, 15, 17], [8, 4, 13, 19], [11, 0, 1, 14], [10, 3, 2, 7, 16], [7, 9, 12, 6], [19, 15, 18, 8, 2, 6], [4, 16, 10, 0, 3, 14], [13, 11, 1, 15], [18, 15, 7, 9], [17, 8, 12, 15], [19, 10, 0, 5], [12, 2, 3, 13, 15, 4], [16, 15, 14, 11, 6], [5, 9, 7, 1, 17], [8, 19, 3, 18], [4, 9, 2, 0, 5, 11], [13, 7, 16], [10, 1, 14], [18, 12, 8, 17], [19, 3, 14, 4], [5, 11, 0], [16, 10, 2, 5], [1, 13, 17, 5, 12], [3, 18, 17, 8, 19], [8, 0, 1, 14, 11], [10, 2, 5, 4], [19, 18, 2, 3, 11, 6], [12, 1, 0, 4, 8], [13, 7, 16, 15, 9], [12, 7, 16], [7, 13, 17], [1, 19, 10, 3, 2, 18], [0, 5, 4, 16, 10], [6, 14, 11], [7, 13, 12, 8], [7, 9, 18, 15], [19, 11, 4, 17], [14, 3, 17], [0, 1, 2], [10, 8, 16], [18, 6, 14, 13, 12], [19, 15, 2, 10, 16], [11, 3, 4, 0, 13, 15], [12, 1, 14], [18, 8, 7, 9], [7, 9, 8, 17], [19, 17, 0, 5, 2, 6], [3, 10, 4, 16], [12, 1, 14, 11], [7, 9, 15, 13, 6, 8], [8, 9, 18, 5], [10, 0, 15, 4, 12, 19], [6, 3, 11, 2, 17], [8, 9, 16, 1, 14], [19, 5, 3, 18], [0, 2, 16, 10, 4, 7], [6, 11, 1, 15], [5, 7, 13, 17], [12, 8, 9], [3, 18, 19], [10, 2, 14], [11, 0, 5, 4], [19, 18, 7, 16, 15], [6, 3, 17], [1, 10, 0, 5], [12, 4, 9], [13, 7, 9, 2, 12, 16], [17, 18, 14, 11, 6], [10, 2, 3, 19, 15], [1, 11, 0, 5], [14, 4, 6], [6, 15, 13, 7, 16, 1], [12, 15, 13, 17, 14], [18, 13, 2, 8, 16, 19], [0, 5, 4], [14, 11, 3, 12, 15], [5, 7, 13, 15, 19], [8, 5, 4, 3, 17, 18], [6, 2, 0, 1, 15], [12, 1, 13, 11, 16], [10, 8, 9], [14, 3, 17, 18, 11, 19], [10, 4, 16, 0, 1], [19, 15, 14, 12, 2, 5], [13, 17, 10, 9, 18], [15, 0, 6, 4, 8, 16], [10, 11, 3, 2, 17], [15, 12, 7, 1, 14], [17, 7, 9, 8], [3, 14, 19, 6, 4, 18], [12, 1, 0, 6, 16], [2, 5, 11, 18, 13, 10], [8, 7, 13, 15], [19, 14, 3, 9], [0, 1, 4], [6, 2, 11], [15, 7, 9, 13, 12, 17], [6, 9, 10, 8, 16], [0, 5, 3, 18, 19], [14, 11, 2], [13, 4, 7, 16], [5, 17, 12, 1, 15, 10], [19, 3, 4, 18, 8, 16], [2, 5, 11], [10, 1, 15, 0, 5], [7, 13, 12], [17, 18, 7, 9, 6], [19, 0, 4, 3, 2, 8], [11, 13, 12, 5, 16, 10], [1, 7, 9], [18, 6, 9, 8, 5], [19, 3, 17], [1, 14, 4], [12, 15, 0, 2], [6, 14, 7, 13, 19], [10, 11, 6, 9], [6, 16, 5, 9, 8], [11, 2, 5, 18, 6, 17], [12, 4, 3, 10, 1, 0], [18, 8, 9], [19, 17, 2, 10, 0], [11, 3, 4, 1], [15, 9, 8, 16, 13, 17], [12, 8, 16], [19, 6, 16, 0, 18], [12, 11, 2, 3, 15, 4], [10, 1, 13, 15], [15, 8, 9, 17, 14], [7, 13, 19], [11, 10, 1, 0, 2, 18], [9, 3, 17], [16, 4, 13, 12, 7], [15, 6, 7, 9], [14, 19, 2, 18, 5, 16], [1, 17, 0, 3, 4, 7], [14, 11, 6], [12, 7, 9], [19, 10, 8, 6, 14], [2, 5, 3, 18], [1, 0, 14, 4, 12, 17], [10, 11, 19, 6, 9, 18], [5, 3, 8], [11, 10, 0, 6, 2, 7]]

all_labels = np.array(map(lambda i: label_map[i], all_labels))
train_labels = np.array(map(lambda i: label_map[i], train_labels))
val_labels = np.array(map(lambda i: label_map[i], val_labels))



label_lengths = map(len, all_labels)
sequence_lengths = map(len, all_sequences)

wpms = []
for i in range(len(sequence_lengths)):
    wpms.append(60.0 / (float(sequence_lengths[i]) / 250 / label_lengths[i]))
print
print np.min(wpms), np.mean(wpms), np.max(wpms)
print
num = len(filter(lambda x: x >= 100.0, wpms))
print num, len(wpms), float(num) / len(wpms)
print

plt.title('Distribution of Rates of Speech in Dataset (WPMs)')
plt.boxplot([wpms])
#plt.scatter(np.array([1.2]*len(wpms))+np.arange(0.0, 1.0, 1.0/len(wpms)), wpms, ',')
plt.scatter([2]*len(wpms), wpms, s=0.1)
plt.ylabel('WPM')

plt.savefig('figure_wpm_boxplot.png')

plt.show()

