import numpy
import math
import acorn_backend.machine_learning.tensorflow_buffer as tb
import acorn_backend.simple_event_taggers
from acorn_backend.machine_learning.neural_network_template import template_NN

class simple_2_jet_tagger(acorn_backend.simple_event_taggers.base_tagger, template_NN):
    #############################################
    ### Neural Network specific class members ###
    #############################################
    model_file = 'data/basic_nn_tagger_model.h5'
    network_model = None


    @classmethod
    def get_label(cls, event):
        return int(event.signal)


    @classmethod
    def prepare_events(cls, event_selections_tuple_list, label_list):
        organized_data = []
        for event, selections in event_selections_tuple_list:
            jet_list = event.jets
            jet0 = jet_list[selections[0]]
            jet1 = jet_list[selections[1]]
            event_properties = [
                jet0.vector.pt,
                jet0.vector.eta,
                jet1.vector.pt,
                jet1.vector.eta,
                (jet0.vector+jet1.vector).mass
            ]
            organized_data.append(event_properties)

            if label_list != None: label_list.append( cls.get_label(event) )

        prepared_data = numpy.array(organized_data)
        return prepared_data


    @classmethod
    def train_model(cls, training_data, training_labels):
        print('TRAINING NEW MODEL')

        # Build and compile neural network model 
        model = tb.keras.Sequential([
            #tb.keras.layers.InputLayer( input_shape=(5,) ),
            tb.keras.layers.Dense(18, activation=tb.tensorflow.nn.relu, input_shape=(5,)),
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
        if cls.network_model == None: cls.load_model()
        elif cls.network_model == -1: self.discriminant = 0
        else:
            prepared_datum = cls.prepare_events( [(event,selections)], None )
            predictions = cls.network_model.predict(prepared_datum)[0]
            if predictions[0] == 0:
                llr = 100
            elif predictions[1] == 0:
                llr = -100
            else:
                llr = math.log(predictions[1] / predictions[0])
            self.discriminant = llr
