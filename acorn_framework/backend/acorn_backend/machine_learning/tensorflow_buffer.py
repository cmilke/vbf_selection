tensorflow = None
keras = None
Input = None
Dense = None
Model = None

def load_tensorflow():
    global tensorflow, keras
    global Input, Dense, Model
    import tensorflow
    #from tensorflow import keras
    import keras
    from keras.layers import Input, Dense
    from keras.models import Model
