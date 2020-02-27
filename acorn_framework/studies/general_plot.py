#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import sys
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

from acorn_backend.analysis_utils import reload_data
from acorn_backend.plotting_utils import hist1

_plots = {
    'leading_eta': hist1( 'leading_eta', '$\eta$ Distribution of Leading Two Jets', ['Leading', 'Sub-Leading'], 50, (-4,4),
        xlabel='$\Delta \eta$')

  , 'leading_eta_delta': hist1( 'leading_eta_delta', '$\Delta \eta$ Distribution of Leading Two Jets', [''], 50, (0,8),
        xlabel='$\eta$')
}


def extract_data():
    for input_type in ['bgd', 'sig']:
        data_dump = pickle.load( open('data/output_aviv_tag_'+input_type+'.p', 'rb') )

        JVT_events_with_3_jets = [ event for event in data_dump['JVT'].events if len(event.jets) > 2 ]
        for event in JVT_events_with_3_jets:
            selector = event.selectors['2maxpt']
            if 'any' in selector.deep_filters:
                eta0 = event.jets[selector.selections[0]].vector.eta
                eta1 = event.jets[selector.selections[1]].vector.eta
                _plots['leading_eta'].add(eta0, 'Leading')
                _plots['leading_eta'].add(eta1, 'Sub-Leading')
                _plots['leading_eta_delta'].add(abs(eta0-eta1))


def draw_distributions():
    #if len(sys.argv) > 1: extract_data()
    extract_data()
    for plot in plot_list: plot.generate_plot()

draw_distributions()
