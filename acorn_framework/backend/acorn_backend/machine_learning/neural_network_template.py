# TensorFlow and tf.keras
# I don't want these to be loaded when unpickeling
# this object, so I import them indirectly through this buffer file
import acorn_backend.machine_learning.tensorflow_buffer as tb

class template_NN():
    #############################################
    ### Neural Network specific class members ###
    #############################################
    model_file = None
    jet_count_range = range(4,4) # This neural net should never be used...
    network_model = None


    @classmethod
    def load_model(cls):
        try: cls.network_model = tb.keras.models.load_model(cls.model_file)
        except OSError:
            print('\nWARNING: Model ' + cls.model_file + ' does not exist.'
                ' If you are not currently tagging this model, then something has gone wrong!\n')
            

    @classmethod
    def prepare_event(cls, event):
        return None


    @classmethod
    def get_label(cls, event):
        return None


    @classmethod
    def train_model(cls, training_data, training_labels):
        return None


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

        plot_model = tb.keras.utils.vis_utils.plot_model
        plot_model(model, to_file=cls.model_file[:-2]+'.pdf', show_shapes=True, show_layer_names=True)
