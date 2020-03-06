import numpy
import math
import tensorflow
import keras

from acorn_backend.machine_learning.neural_network_template import template_NN

class ML_tagger_base(template_NN):
    def __init__(self, jet_selector, tag=True):
        super().__init__(tag)
        self.jet_selector = jet_selector


    def get_label(self, event):
        return int(event.signal)


    def prepare_events(self, event_list, label_list):
        organized_data = []
        for event in event_list:
            jet0, jet1 = self.jet_selector(event)
            event_properties = [
                jet0.pt(),
                jet0.eta(),
                jet1.pt(),
                jet1.eta(),
                (jet0.vector()+jet1.vector()).mass
            ]
            organized_data.append(event_properties)

            if label_list != None: label_list.append( self.get_label(event) )

        prepared_data = numpy.array(organized_data)
        return prepared_data


    def train_model(self, training_data, training_labels):
        print('TRAINING NEW MODEL')

        # Build and compile neural network model 
        model = keras.Sequential([
            #keras.layers.InputLayer( input_shape=(5,) ),
            keras.layers.Dense(18, activation=tensorflow.nn.relu, input_shape=(5,)),
            keras.layers.Dense(2, activation=tensorflow.nn.softmax)
        ])

        model.compile( optimizer='adam',
                       loss='sparse_categorical_crossentropy',
                       metrics=['accuracy'])

        model.fit(training_data, training_labels, epochs=5) # Train Model
        model.save(self.model_file) # Save Model


    def tag_event(self, event):
        prepared_datum = self.prepare_events( [event], None )
        predictions = self.network_model.predict(prepared_datum)[0]
        if predictions[0] == 0:
            llr = 100
        elif predictions[1] == 0:
            llr = -100
        else:
            llr = math.log(predictions[1] / predictions[0])
        return llr
