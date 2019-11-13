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
import acorn_backend.simple_event_taggers

class basic_nn_tagger(acorn_backend.simple_event_taggers.base_tagger):
    #############################################
    ### Neural Network specific class members ###
    #############################################
    model_file = 'data/basic_nn_tagger_model.h5'
    network_model = None


    @classmethod
    def load_model(cls):
        try: cls.network_model = tb.keras.models.load_model(cls.model_file)
        except OSError:
            print('\nWARNING: Model ' + cls.model_file + ' does not exist.'
                ' If you are not currently tagging this model, then something has gone wrong!\n')
    

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


    ######################
    ### Tagger Members ###
    ######################
    key = '2jetNNtagger'
    value_range = (-100, 100)

    def __init__(self, event, selections):
        cls = self.__class__
        if cls.network_model == None:
            self.discriminant = 0
        else:
            prepared_event = cls.prepare_event(event, selections)
            singular_datum = numpy.array([prepared_event])
            predictions = cls.network_model.predict(singular_datum)[0]
            if predictions[0] == 0:
                llr = 1000
            else:
                llr = math.log(predictions[1] / predictions[0])
            self.discriminant = llr
