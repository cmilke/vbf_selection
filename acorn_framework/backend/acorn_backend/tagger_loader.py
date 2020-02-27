import acorn_backend.base_jet_selectors as base_selectors
from acorn_backend.machine_learning import MLselectors

selector_options = [
    [], #0
    [], #1
    [ #2
        base_selectors.base_selector
      #, base_selectors.dummy_2_jet_selector
    ],
    [ #3
        base_selectors.truth_selector
      , base_selectors.maximal_mjj_selector
      , base_selectors.subleading_mjj_selector
      #, base_selectors.subsubleading_mjj_selector
      , base_selectors.highest_pt_selector
      #, base_selectors.fantasy_optimal_mjj_selector
      , base_selectors.dummy_3_jet_selector
      #, base_selectors.random_selector
      , base_selectors.maximal_Delta_eta_selector
      #, base_selectors.quark_gluon_tag_selector
      #, base_selectors.coLinearity_merger
      #, basic_neural_net_selector 
      #, dual_layer_selector 
      #, pair_MLP_selector
    ]
]
