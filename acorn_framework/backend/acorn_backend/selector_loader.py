import acorn_backend.base_jet_selectors as base_selectors

from acorn_backend.machine_learning import tensorflow_buffer
from acorn_backend.machine_learning.basic_selector import basic_neural_net_selector

selector_options = [
    [], #0
    [], #1
    [base_selectors.base_selector], #2
    [
        base_selectors.truth_selector
      , base_selectors.maximal_mjj_selector
      , base_selectors.highest_pt_selector
      , base_selectors.random_selector
      , basic_neural_net_selector 
    ] #3
]


def load_selector_models():
    tensorflow_buffer.load_tensorflow()

    basic_neural_net_selector.load_model()
