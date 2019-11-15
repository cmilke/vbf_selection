import numpy
import math
import acorn_backend.machine_learning.tensorflow_buffer as tb
import acorn_backend.simple_event_taggers
from acorn_backend.machine_learning.neural_network_template import template_NN

class basic_nn_tagger(acorn_backend.simple_event_taggers.base_tagger, template_NN):
    #############################################
    ### Neural Network specific class members ###
    #############################################
    model_file = 'data/basic_nn_tagger_model.h5'
    network_model = None


    @classmethod
    def prepare_event(cls, event, selections):
        jet_list = event.jets
        jet0 = jet_list[selections[0]]
        jet1 = jet_list[selections[1]]
        data = [
            jet0.vector.pt,
            jet0.vector.eta,
            jet1.vector.pt,
            jet1.vector.eta,
            (jet0.vector+jet1.vector).mass
        ]

        prepared_event = numpy.array(data)
        return prepared_event


    @classmethod
    def get_label(cls, event):
        return int(event.signal)


    @classmethod
    def train_model(cls, training_data, training_labels):
        print('TRAINING NEW MODEL')

        # Build and compile neural network model 
        model = tb.keras.Sequential([
            #tb.keras.layers.Flatten( input_shape=(1,5) ),
            tb.keras.layers.Dense(18, activation=tb.tensorflow.nn.relu),
            tb.keras.layers.Dense(2, activation=tb.tensorflow.nn.softmax)
        ])

        model.compile( optimizer='adam',
                       loss='sparse_categorical_crossentropy',
                       metrics=['accuracy'])

        model.fit(training_data, training_labels, epochs=5) # Train Model
        model.save(cls.model_file) # Save Model


    ######################
    ### Tagger Members ###
    ######################
    key = '2jetNNtagger'
    value_range = (-20, 20)

    def __init__(self, event, selections):
        cls = self.__class__
        if cls.network_model == None:
            self.discriminant = 0
        else:
            prepared_event = cls.prepare_event(event, selections)
            singular_datum = numpy.array([prepared_event])
            predictions = cls.network_model.predict(singular_datum)[0]
            if predictions[0] == 0:
                llr = 100
            else:
                llr = math.log(predictions[1] / predictions[0])
            self.discriminant = llr
