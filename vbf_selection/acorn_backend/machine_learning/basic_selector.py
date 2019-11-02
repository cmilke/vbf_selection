import sys

#TensorFlor and tf.keras
import tensorflow
from tensorflow import keras

#Helper libraries
import numpy
import math
import matplotlib
import matplotlib.pyplot as plot
PI = math.pi

import acorn_backend.base_jet_selectors


class basic_neural_net_selector(acorn_backend.base_jet_selectors.base_selector):
    #############################################
    ### Neural Network specific class members ###
    #############################################
    model_file = 'data/basic_neural_net_model.h5'
    jet_count_range = range(3,4) # This neural net is only intented for 3-jet events
    pair_labels = [
        [0,1],
        [0,2],
        [1,2]
    ]
    network_model = None


    @classmethod
    def load_model(cls):
        cls.network_model = keras.models.load_model(cls.model_file)
    

    @classmethod
    def prepare_event(cls, event):
        # Extract and normalize eta, phi, and pt from each jet
        normalized_list = []
        for jet in event.jets:
            # Normalize eta by converting it to theta
            theta = 2 * math.atan( math.exp(-jet.eta) )
            normalized_eta = theta / PI

            # Phi is naturally bounded, so it's trivial to normalize
            normalized_phi = ( jet.phi + PI) / (2*PI)

            # Normalize pt by arbitrarily bounding it with a
            # sigmoid centered at pt = 75
            rescaled_pt = (jet.pt - 75) / 15
            normalized_pt = 1 / ( 1 + math.exp(-rescaled_pt) )

            normalized_jet = [normalized_eta, normalized_phi, normalized_pt]
            normalized_list += normalized_jet

        prepared_event = numpy.array(normalized_list)
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
        model = keras.Sequential([
            keras.layers.Dense(18, activation=tensorflow.nn.relu),
            keras.layers.Dense(3, activation=tensorflow.nn.softmax)
        ])

        model.compile( optimizer='adam',
                       loss='sparse_categorical_crossentropy',
                       metrics=['accuracy'])

        model.fit(training_data, training_labels, epochs=5) # Train Model
        model.save(cls.model_file) # Save Model


    @classmethod
    def test_model(cls, test_data, test_labels):
        print('TESTING MODEL')
        model = keras.models.load_model(cls.model_file) # Load Model

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
        prepared_event = cls.prepare_event(event)
        singular_datum = numpy.array([prepared_event])
        predictions = cls.network_model.predict(singular_datum)
        prediction_index = numpy.argmax(predictions)
        jet_index_pair = cls.pair_labels[prediction_index]
        return tuple(jet_index_pair)
