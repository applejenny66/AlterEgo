import numpy as np
import tensorflow as tf
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os
import keyboard
import time

import data

test_model = True
channels = range(1, 8) # Must be same as trained model if test_model==True
#channels = [1, 3, 4]

#word_map = ['left', 'right', 'rotate', 'silence']
#word_map = ['zero', 'one', 'two', 'three', 'four', 'silence']
word_map = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'plus', 'minus', 'times', 'divided by', 'undo', 'silence']

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

    def normalize_kernel(kernel, subtract_mean=False):
        if subtract_mean:
            kernel = np.array(kernel, np.float32) - np.mean(kernel)
        return np.array(kernel, np.float32) / np.sum(np.abs(kernel))
    def ricker_function(t, sigma):
        return 2./(np.sqrt(3*sigma)*np.pi**0.25)*(1.-(float(t)/sigma)**2)*np.exp(-(float(t)**2)/(2*sigma**2))
    def ricker_wavelet(n, sigma):
        return np.array(map(lambda x: ricker_function(x, sigma), range(-n//2, n//2+1)))

    #### Apply ricker wavelet subtraction
    ricker_width = 35 * sample_rate // 250
    ricker_sigma = 4.0 * sample_rate / 250
    ricker_kernel = normalize_kernel(ricker_wavelet(ricker_width, ricker_sigma))
    ricker_convolved = data.transform.correlate(sequence_groups, ricker_kernel)
    ricker_subtraction_multiplier = 2.0
    sequence_groups = sequence_groups - ricker_subtraction_multiplier * ricker_convolved

    #### Apply sine wavelet kernel
#    period = int(sample_rate)
#    sin_kernel = normalize_kernel(np.sin(np.arange(period)/float(period) * 1*np.pi), subtract_mean=True)
#    sequence_groups = data.transform.correlate(sequence_groups, sin_kernel)

    low_freq = 0.5 #0.5
    high_freq = 8 #8
    order = 1

    #### Apply soft bandpassing
    sequence_groups = data.transform.bandpass_filter(sequence_groups, low_freq, high_freq, sample_rate, order=order)
    
    #### Apply hard bandpassing
#    sequence_groups = data.transform.fft(sequence_groups)
#    sequence_groups = data.transform.fft_frequency_cutoff(sequence_groups, low_freq, high_freq, sample_rate)
#    sequence_groups = np.real(data.transform.ifft(sequence_groups))
    
    return sequence_groups


num_classes = 15 #len(filter(lambda x: '.txt' in x, os.listdir('patient_data')))
num_classes_act = 2 #len(filter(lambda x: '.txt' in x, os.listdir('patient_data')))
length = 450 #600 DO NOT CHANGE
length_act = 450 #600 DO NOT CHANGE

####################
graph1 = tf.Graph()
with graph1.as_default():
    #### Model (MUST BE SAME AS patient_train.py)
    learning_rate = 1e-4
    dropout_rate = 0.4

    inputs = tf.placeholder(tf.float32,[None, length, len(channels)]) #[batch_size,timestep,features]
    targets = tf.placeholder(tf.int32, [None, num_classes])
    weights = tf.placeholder(tf.float32, [None])
    training = tf.placeholder(tf.bool)

    conv1 = tf.layers.conv1d(inputs, 400, 12, activation=tf.nn.relu, padding='valid')
    conv1 = tf.layers.max_pooling1d(conv1, 2, strides=2)
    conv2 = tf.layers.conv1d(conv1, 400, 6, activation=tf.nn.relu, padding='valid')
    conv2 = tf.layers.max_pooling1d(conv2, 2, strides=2)
    conv3 = tf.layers.conv1d(conv2, 400, 3, activation=tf.nn.relu, padding='valid')
    conv3 = tf.layers.max_pooling1d(conv3, 2, strides=2)
    conv4 = tf.layers.conv1d(conv3, 400, 3, activation=tf.nn.relu, padding='valid')
    conv4 = tf.layers.max_pooling1d(conv4, 2, strides=2)
    conv5 = tf.layers.conv1d(conv4, 400, 3, activation=tf.nn.relu, padding='valid')
    conv5 = tf.layers.max_pooling1d(conv5, 2, strides=2)
    dropout = tf.layers.dropout(conv5, dropout_rate, training=training)
    reshaped = tf.reshape(dropout, [-1, np.prod(dropout.shape[1:])])
    fc1 = tf.layers.dense(reshaped, 250, activation=tf.nn.relu)
    logits = tf.layers.dense(fc1, num_classes, activation=tf.nn.softmax)

    loss = tf.reduce_mean(tf.multiply(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=targets), weights))

    optimizer = tf.train.AdamOptimizer(learning_rate).minimize(loss)

    correct = tf.equal(tf.argmax(logits,1), tf.argmax(targets,1))
    accuracy = tf.reduce_mean(tf.cast(correct, tf.float32))
    
    saver1 = tf.train.Saver()
####################

####################
graph2 = tf.Graph()
with graph2.as_default():
    #### Model (MUST BE SAME AS patient_train.py)
    learning_rate = 1e-4
    dropout_rate = 0.4

    inputs_act = tf.placeholder(tf.float32,[None, length_act, len(channels)]) #[batch_size,timestep,features]
    targets_act = tf.placeholder(tf.int32, [None, num_classes_act])
    weights_act = tf.placeholder(tf.float32, [None])
    training_act = tf.placeholder(tf.bool)

    conv1_act = tf.layers.conv1d(inputs_act, 400, 12, activation=tf.nn.relu, padding='valid')
    conv1_act = tf.layers.max_pooling1d(conv1_act, 2, strides=2)
    conv2_act = tf.layers.conv1d(conv1_act, 400, 6, activation=tf.nn.relu, padding='valid')
    conv2_act = tf.layers.max_pooling1d(conv2_act, 2, strides=2)
    conv3_act = tf.layers.conv1d(conv2_act, 400, 3, activation=tf.nn.relu, padding='valid')
    conv3_act = tf.layers.max_pooling1d(conv3_act, 2, strides=2)
    conv4_act = tf.layers.conv1d(conv3_act, 400, 3, activation=tf.nn.relu, padding='valid')
    conv4_act = tf.layers.max_pooling1d(conv4_act, 2, strides=2)
    conv5_act = tf.layers.conv1d(conv4_act, 400, 3, activation=tf.nn.relu, padding='valid')
    conv5_act = tf.layers.max_pooling1d(conv5_act, 2, strides=2)
    dropout_act = tf.layers.dropout(conv5_act, dropout_rate, training=training_act)
    reshaped_act = tf.reshape(dropout_act, [-1, np.prod(dropout_act.shape[1:])])
    fc1_act = tf.layers.dense(reshaped_act, 250, activation=tf.nn.relu)
    logits_act = tf.layers.dense(fc1_act, num_classes_act, activation=tf.nn.softmax)

    loss_act = tf.reduce_mean(tf.multiply(tf.nn.softmax_cross_entropy_with_logits(logits=logits_act, labels=targets_act), weights_act))

    optimizer_act = tf.train.AdamOptimizer(learning_rate).minimize(loss_act)

    correct_act = tf.equal(tf.argmax(logits_act,1), tf.argmax(targets_act,1))
    accuracy_act = tf.reduce_mean(tf.cast(correct_act, tf.float32))
    
    saver2 = tf.train.Saver()
####################
        
predictions = []
certainty_sums = [0.0] * num_classes
activated_timestamp = 0
produced_timestamp = 0
last_activated = False
with tf.Session(graph=graph1) as session1:
    if test_model:
        tf.global_variables_initializer().run()
        saver1.restore(session1, 'math4_triggerless_model.ckpt')
    with tf.Session(graph=graph2) as session2:
        if test_model:
            tf.global_variables_initializer().run()
            saver2.restore(session2, 'math4_activation_model.ckpt')
        
        displayed = 0
        step = 1
        bar_size = 20
        last_test_output = None
        last_input_indices = None
        selected = None
        def on_data(history, trigger_history, index_history, count, samples_per_update, recorded_count):
            global displayed
            global last_test_output
            global last_input_indices
            global selected
            global predictions
            global certainty_sums
            global activated_timestamp
            global produced_timestamp
            global last_activated
            if count - displayed > step:

    #            if test_model:
    #                start = None
    #                end = None
    #                trigger = None
    #                for i in range(len(trigger_history))[::-1]:
    #                    if trigger_history[i] == 1 and trigger == False:
    #                        end = i
    #                        trigger = True
    #                    if trigger_history[i] == 0:
    #                        if trigger:
    #                            start = i
    #                            break
    #                        trigger = False
    #                if start and end:
    #                    signal_length = end - start
    #                    side_padding = (length - signal_length) // 2
    #                    print signal_length
    #                    print end - start > 50
    #                    print end + side_padding < len(history)
    #                    print start - side_padding - 1 >= 0
    #                    if end - start > 50 and end + side_padding + 1 < len(history) and start - side_padding - 1 >= 0:
    #    #                    input_indices = index_history[start:end+1]
    #                        start_modified, end_modified = start-(length-signal_length-side_padding-1), end+side_padding
    #                        input_indices = index_history[start_modified:end_modified+1]
    #                        print 'DEBUG'
    #                        if not last_input_indices is None:
    #                            print len(input_indices) != len(last_input_indices)
    #                            if len(input_indices) == len(last_input_indices):
    #                                print not np.all(input_indices == last_input_indices)
    #                        if last_input_indices is None or (len(input_indices) != len(last_input_indices) 
    #                            or not np.all(input_indices == last_input_indices)):
    #                            last_input_indices = input_indices
    #
    #                            print start, end
    #                            print start_modified, end_modified
    #
    #                            sequence = history[start_modified:end_modified+1,channels]
    #                            test_feed = {inputs: [sequence], training: False}
    #                            last_test_output = session.run(logits, test_feed)[0]
    #                            selected = np.argmax(last_test_output)
    #                            os.system('say ' + str(word_map[selected]) + ' &')
    #                            predictions.append(selected)

                if test_model:
                    sequence = history[-length:,channels]
                    test_feed = {inputs: [sequence], training: False}
                    activation_feed = {inputs_act: [sequence], training_act: False}
                    test_output = session1.run(logits, test_feed)[0]
                    activation_output = session2.run(logits_act, activation_feed)[0]
                    selected = np.argmax(test_output)
                    activated = bool(1-np.argmax(activation_output))
    #                certainty_sums += test_output
                    certainty_sums += np.square(test_output)

                    if activated and not last_activated:
                        certainty_sums = np.array([0.0] * num_classes)
                        activated_timestamp = time.time()
                    if not activated and last_activated:
                        if time.time() - activated_timestamp >= 0.3 and time.time() - produced_timestamp > 1:
                            best_guess = np.argmax(certainty_sums[:-1])
                            produced_timestamp = time.time()
                            os.system('say ' + str(word_map[best_guess]) + ' &')
                            predictions.append(best_guess)
    
                    last_activated = activated

                print 'SPU: ' + str(samples_per_update) + '\t\t' + '\t'.join(['Channel ' + str(i+1) for i in range(8)])
                print str('{:.1f}'.format(count/250.)) + 's\t\t' + '\t'.join(
                    map(lambda (i, x): '{:f}'.format(x) if i in channels else '--\t', enumerate(history[-1])))
                print
                if test_model:
                    for i in range(len(test_output)):
                        n = int(test_output[i] * bar_size)
                        print i, '[' + '#' * n + ' ' * (bar_size - n) + ']', test_output[i]
                    print
                    for i in range(len(activation_output)):
                        n = int(activation_output[i] * bar_size)
                        print i, '[' + '#' * n + ' ' * (bar_size - n) + ']', activation_output[i]
                    print
                print 'Predicted\t', predictions


            displayed = count // step * step
    
        data.serial.start('/dev/tty.usbserial-DQ007UBV',
                          on_data, channels=channels, transform_fn=transform_data,
                          history_size=1500, shown_size=1200, override_step=55)