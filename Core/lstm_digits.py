import numpy as np
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Flatten, LSTM, Conv1D, MaxPooling1D, Activation, BatchNormalization, GlobalMaxPooling1D
from keras.optimizers import Adam
from keras.callbacks import Callback
from keras.utils import to_categorical
from sklearn.utils.class_weight import compute_class_weight
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import data

length = 600 #300

#results = []
#for x in range(1, 21):
    
# Load data and apply transformations
sequence_groups = data.digits_dataset()
#class_map = ['012', '120', '201', '021', '210', '102']

#sequence_groups = data.combine([
#        data.process(10, ['data/data/2_subvocal_digits_9_trials.txt']),
#        data.process(10, ['data/data/3_subvocal_digits_11_trials.txt']),
#        data.process(10, ['data/data/4_subvocal_digits_10_trials.txt']),
#        data.process(10, ['data/data/5_subvocal_digits_10_trials.txt']),
#        data.process(10, ['data/data/6_subvocal_digits_10_trials.txt']),
#    ])

#sequence_groups = sequence_groups[:2]

sequence_groups = data.transform.default_transform(sequence_groups)

#sequence_groups = np.array(map(lambda x: x[30:], sequence_groups))

# Split into training and validation data
training_sequence_groups, validation_sequence_groups = data.split(sequence_groups, 1./6)

# Augment training data by varying positioning of padding/truncating

# Uncomment
#training_sequence_groups = data.transform.pad_extra(training_sequence_groups, length)
#training_sequence_groups = data.transform.augment_pad_truncate_intervals(training_sequence_groups, length, 10)
#training_sequence_groups = data.transform.augment_pad_truncate_intervals(training_sequence_groups, length, 100)

#training_sequence_groups = data.transform.augment_pad_truncate_intervals(training_sequence_groups, length, 50)
training_sequence_groups = data.transform.pad_truncate(training_sequence_groups, length)

#training_sequence_groups = data.transform.augment(training_sequence_groups,
#                                                  [(data.transform.gaussian_filter, [3], {})],
#                                                  include_original=True)

# Pad/truncate validation data
#validation_sequence_groups = data.transform.pad_truncate(validation_sequence_groups, length)

# Uncomment
#validation_sequence_groups = data.transform.pad_extra(validation_sequence_groups, length/2)
#validation_sequence_groups = data.transform.augment_pad_truncate_intervals(validation_sequence_groups, length, 10)
validation_sequence_groups = data.transform.pad_truncate(validation_sequence_groups, length)

# Format into sequences and labels
train_sequences, train_labels = data.get_inputs(training_sequence_groups)
val_sequences, val_labels = data.get_inputs(validation_sequence_groups)

# Calculate sample weights
class_weights = compute_class_weight('balanced', np.unique(train_labels), train_labels)
sample_weights = class_weights[list(train_labels)]

train_labels = to_categorical(train_labels)
val_labels = to_categorical(val_labels)

print np.shape(train_sequences)
print np.shape(train_labels)
print np.shape(val_sequences)
print np.shape(val_labels)

class PlotLosses(Callback):
    def on_train_begin(self, logs={}):
        self.losses = []
        self.loss_fig = plt.figure(1)
        self.plot = True

    def on_batch_end(self, batch, logs={}):
        if batch > 1:
            self.losses.append(logs.get('loss'))

    def on_epoch_end(self, batch, logs={}):
        if self.plot:
            self.loss_fig.clear()
            plt.figure(1)
            plt.plot(self.losses)
            plt.title('Training Loss')
            plt.pause(0.0001)
        predicted = np.argmax(self.model.predict(val_sequences), axis=1)
        actual = np.argmax(val_labels, axis=1)
        output = [[] for _ in range(num_classes)]
        count_matrix = [[0] * num_classes for _ in range(num_classes)]
        for i in range(len(actual)):
            output[actual[i]].append(predicted[i])
            count_matrix[actual[i]][predicted[i]] += 1
        print
        print '     Predicted\t', '\t'.join(map(str, range(num_classes)))
        print 'Actual\t', '-' * ((num_classes + 1) * 8 + 1)
        for i in range(num_classes):
#            print i, output[i], np.mean(np.array(output[i]) == i)
            print ' '*(5-len(str(i))), i, '\t|\t', \
                '\t'.join(map(lambda x: str(x) if x else '-', count_matrix[i])), \
                '\t| ', np.mean(np.array(output[i]) == i)
        print
        self.model.save('lstm_digits.h5')
        
        intermediate_layer_model = Model(inputs=self.model.input, outputs=self.model.get_layer('lstm_1').output)
        intermediate_output = intermediate_layer_model.predict(val_sequences)
        plt.figure(11)
        plt.imshow(np.transpose(intermediate_output[0]))
        plt.figure(12)
        for i in range(4):
            plt.plot(val_sequences[0][:,i])
            plt.gca().set_xlim((0, length))
        plt.show()
        

plot_losses = PlotLosses()

num_classes = len(sequence_groups)

#model = Sequential()
#
#model.add(Conv1D(400, 3, activation='relu', input_shape=(length, np.shape(train_sequences[0])[1])))
##model.add(BatchNormalization())
#model.add(MaxPooling1D(2, 2))
#
#model.add(Conv1D(400, 3, activation='relu'))
##model.add(BatchNormalization())
#model.add(MaxPooling1D(2, 2))
#
#model.add(Conv1D(400, 3, activation='relu'))
#model.add(GlobalMaxPooling1D())
#
#model.add(Dropout(0.4)) #0.4
##model.add(Flatten())
#
#model.add(Dense(250, activation='relu'))
#
#model.add(Dense(num_classes, activation='softmax'))

model = Sequential()

model.add(LSTM(256, return_sequences=True,
               input_shape=(length, np.shape(train_sequences[0])[1])))
#model.add(Bidirectional(LSTM(256, return_sequences=True),
#                        input_shape=(max_length, np.shape(training_sequences[0])[1])))

#model.add(LSTM(256, return_sequences=True))

model.add(Dropout(0.4))

model.add(Flatten())

#model.add(Dense(250, activation='relu'))

model.add(Dense(num_classes, activation='softmax'))

adam = Adam(lr=1e-4) #1e-3
model.compile(loss='categorical_crossentropy',
              optimizer=adam,
              metrics=['accuracy'])
print model.summary()

history = model.fit(train_sequences, train_labels, sample_weight=sample_weights,
                    validation_data=(val_sequences, val_labels),
                    batch_size=50, #50
                    epochs=200,
                    callbacks=[plot_losses])

max_val_acc = max(history.history['val_acc'])
print
print max_val_acc
#    results.append((x, max_val_acc))

model.save('lstm_digits.h5')

#print
#print results
#xs, ys = zip(*results)
#plt.figure()
#plt.plot(xs, ys)
#plt.show()