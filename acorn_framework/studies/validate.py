#!/usr/bin/env python
import sys
import pickle

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

#Define all the high level root stuff: ntuple files, branches to be used
_Nevents = 30000
_hist_bins = 32
_category_key = 'JVT'


_xlimits = {
    'Event Count':None, 'PDGID':[-5,40], '$p_T$':[20,200], '$\eta$':None, '$\phi$':None,
    'Mass':None, 'Leading $p_T$ Mass':[0,3000], '$\Delta \eta_{max}$':None
}


def load_data(record_name, input_type, validation_data):
    input_file = 'data/output_'+record_name+'_'+input_type+'.p'
    data_dump = pickle.load( open(input_file, 'rb') )
    num_events = 0
    for event in data_dump[_category_key].events:
        if len(event.jets) < 3: continue
        validation_data['Event Count'][input_type].append( int(event.signal) )
        for jet in event.jets:
            validation_data['PDGID'][input_type].append( jet.truth_id )
            validation_data['$p_T$'][input_type].append( jet.vector.pt )
            validation_data['$\eta$'][input_type].append( jet.vector.eta )
            validation_data['$\phi$'][input_type].append( jet.vector.phi )
            validation_data['Mass'][input_type].append( jet.vector.mass )

        event.jets.sort(key=lambda j: j.vector.pt, reverse=True)
        leading_pt_mass = (event.jets[0].vector + event.jets[1].vector).mass
        validation_data['Leading $p_T$ Mass'][input_type].append(leading_pt_mass)

        event.jets.sort(key=lambda j: j.vector.eta)
        max_delta_eta = abs(event.jets[0].vector.eta - event.jets[2].vector.eta)
        validation_data['$\Delta \eta_{max}$'][input_type].append(max_delta_eta)


        num_events += 1
        if num_events >= _Nevents: break


def validate():
    record_name = sys.argv[1]

    # Load data
    print('Loading...')
    input_keys = ['sig', 'bgd']
    validation_data = { d_key:{i_key:[] for i_key in input_keys} for d_key in _xlimits.keys() }
    for input_type in input_keys: load_data(record_name, input_type, validation_data)


    # Plot data
    print('Plotting...')
    output = PdfPages('plots/figures/validation_'+record_name+'.pdf')

    for plot_name, inputs in validation_data.items():
        plot_range = None if plot_name not in _xlimits else _xlimits[plot_name]
        plot_values = { 'x': [], 'label': [] }
        for input_type,data in inputs.items():
            plot_values['x'].append(data)
            plot_values['label'].append( input_type+' - '+str(len(data)) )
        fig,ax = plt.subplots()
        counts, bins, hist = plt.hist(**plot_values, histtype='step', linewidth=2, bins=_hist_bins, range=plot_range)
        for value in counts: print( value.sum() )
        ax.legend()
        plt.grid()
        plt.title(record_name+': Distribution of '+plot_name+' Over '+str(_Nevents)+' Events')
        if plot_range != None: plt.xlim(*_xlimits[plot_name])
        output.savefig()
        plt.close()
    output.close()

validate()
