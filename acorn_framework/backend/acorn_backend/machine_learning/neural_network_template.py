import keras

class template_NN():
    def __init__(self, tag=True):
        self.model_file = 'data/'+self.__class__.__name__+'.h5'
        if tag: self.network_model = keras.models.load_model(self.model_file)


    def test_model(self, test_data, test_labels):
        print('TESTING MODEL')
        network_model = keras.models.load_model(self.model_file) # Load Model

        # Evaluate Trained Model
        test_loss, test_accuracy = network_model.evaluate(test_data, test_labels)
        predictions = network_model.predict(test_data)
        for label, prediction in zip(test_labels[:20], predictions[:20]):
            result = str(label) + ': '
            result += str(prediction)
            print(result)

        print('Test accuracy: ', test_accuracy)

        plot_model = keras.utils.vis_utils.plot_model
        plot_model(network_model, to_file=self.model_file[:-2]+'pdf', show_shapes=True, show_layer_names=True)
