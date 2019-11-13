import sys

# TensorFlow and tf.keras
# I don't want these to be loaded when unpickeling
# this object, so I import them indirectly through this buffer file
import acorn_backend.machine_learning.tensorflow_buffer as tb

#Helper libraries
import numpy
import math
import matplotlib
import matplotlib.pyplot as plot
import acorn_backend.base_jet_selectors
from uproot_methods import TLorentzVector

class basic_neural_net_selector(acorn_backend.base_jet_selectors.base_selector):
    #############################################
    ### Neural Network specific class members ###
    #############################################
    model_file = 'data/basic_neural_net_selector_model.h5'
    jet_count_range = range(3,4) # This neural net is only intented for 3-jet events
    pair_labels = [
        [0,1],
        [0,2],
        [1,2]
    ]
    network_model = None


    @classmethod
    def load_model(cls):
        try: cls.network_model = tb.keras.models.load_model(cls.model_file)
        except OSError:
            print('\nWARNING: Model ' + cls.model_file + ' does not exist.'
                ' If you are not currently tagging this model, then something has gone wrong!\n')
            

    @classmethod
    def prepare_event(cls, event):
        p_list = []
        for jet in event.jets:
            p_list.append([ jet.vector.p3.x, jet.vector.p3.y, jet.vector.p3.z ])
        prepared_event = numpy.array(p_list)
        return prepared_event


    @classmethod
    def get_label(cls, event):
        vbf_jets = [ i for i,jet in enumerate(event.jets) if jet.is_truth_quark() ]
        label = cls.pair_labels.index(vbf_jets)
        return label


    @classmethod
    def train_model(cls, training_data, training_labels):
        print('TRAINING NEW MODEL')

        # Build and compile neural network model 
        model = tb.keras.Sequential([
            tb.keras.layers.Flatten( input_shape=(3,3) ),
            tb.keras.layers.Dense(18, activation=tb.tensorflow.nn.relu),
            tb.keras.layers.Dense(3, activation=tb.tensorflow.nn.softmax)
        ])

        model.compile( optimizer='adam',
                       loss='sparse_categorical_crossentropy',
                       metrics=['accuracy'])

        model.fit(training_data, training_labels, epochs=5) # Train Model
        model.save(cls.model_file) # Save Model


    @classmethod
    def test_model(cls, test_data, test_labels):
        print('TESTING MODEL')
        model = tb.keras.models.load_model(cls.model_file) # Load Model

        # Evaluate Trained Model
        test_loss, test_accuracy = model.evaluate(test_data, test_labels)
        print('Test accuracy: ', test_accuracy)

        predictions = model.predict(test_data)
        for label, prediction in zip(test_labels[:10], predictions[:10]):
            result = str(label) + ': '
            result += str(prediction)
            print(result)


    #############################
    ### Jet Selection Members ###
    #############################
    key = 'basicNN'

    def select(self, event):
        cls = self.__class__
        if cls.network_model == None:
            return (0,1)
        else:
            prepared_event = cls.prepare_event(event)
            singular_datum = numpy.array([prepared_event])
            predictions = cls.network_model.predict(singular_datum)
            prediction_index = numpy.argmax(predictions)
            jet_index_pair = cls.pair_labels[prediction_index]
            return tuple(jet_index_pair)
