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
import acorn_backend.simple_event_taggers.base_tagger

# TODO: actually make this a tagger not a selector
class basic_nn_tagger(acorn_backend.simple_event_taggers.base_tagger):
    #############################################
    ### Neural Network specific class members ###
    #############################################
    model_file = 'data/basic_nn_tagger_model.h5'
    jet_count_range = range(3,4) # This neural net is only intented for 3-jet events
    pair_labels = [
        [0,1],
        [0,2],
        [1,2]
    ]
    network_model = None


    @classmethod
    def load_model(cls):
        cls.network_model = tb.keras.models.load_model(cls.model_file)
    

    @classmethod
    def prepare_event(cls, event):
        # Extract and normalize eta, phi, and pt from each jet
        normalized_list = []
        for jet in event.jets:
            # Normalize eta by converting it to theta
            theta = 2 * math.atan( math.exp(-jet.vector.eta) )
            normalized_eta = theta / math.pi

            # Phi is naturally bounded, so it's trivial to normalize
            normalized_phi = ( jet.vector.phi + math.pi) / (2*math.pi)

            # Normalize pt by arbitrarily bounding it with a
            # sigmoid centered at pt = 75
            rescaled_pt = (jet.vector.pt - 75) / 15
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
        model = tb.keras.Sequential([
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
        prepared_event = cls.prepare_event(event)
        singular_datum = numpy.array([prepared_event])
        predictions = cls.network_model.predict(singular_datum)
        prediction_index = numpy.argmax(predictions)
        jet_index_pair = cls.pair_labels[prediction_index]
        return tuple(jet_index_pair)
