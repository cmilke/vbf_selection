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


    def generate_llr(self, prediction):
        if prediction[0] == 0:
            llr = 100
        elif prediction[1] == 0:
            llr = -100
        else:
            llr = math.log(predictions[1] / predictions[0])
        return llr


    def tag_event(self, event):
        prepared_datum = self.prepare_events( [event], None )
        prediction = self.network_model.predict(prepared_datum)[0]
        llr = generate_llr(prediction)
        return llr


    def mass_process(tagger_key, event_list):
        prepared_data = self.prepare_events( event_list, None )
        predictions = self.network_model.predict(prepared_data)
        for index, event in enumerate(input_list):
            discriminant = generate_llr(predictions[index])
            event.set_discriminant(discriminant)



