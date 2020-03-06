#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import sys
import pickle
import numpy
import itertools
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

from acorn_backend.plotting_utils import hist1, hist2
from acorn_backend.tagger_methods import selector_options

_input_titles = {'sig':'Signal', 'bgd':'Background'}

_plots = {
    'leading_eta': hist1( 'leading_eta', '$\eta$ Distribution of Leading Two Jets',
        ['any'], 50, (-4,4), xlabel='$\Delta \eta$')

  , 'leading_eta_delta': hist1( 'leading_eta_delta', '$\Delta \eta$ Distribution of Leading Two Jets',
        ['any'], 50, (0,8), xlabel='$\eta$')
}

for key in ['mjjSL', 'maxpt', 'mjjmax']:
    name = 'correlation_mjj_eta_'+key
    _plots[name] = hist2( name, '$\Delta \eta$ VS $M_{jj}$ for '+key,
        50, ( (0,2000), (0,10) ), xlabel=('$M_{jj}$ (GeV)'), ylabel=('$\Delta \eta$') )


for input_key in ['bgd', 'sig']:
    name = 'mjj_'+input_key
    label_list = ['mjjSL', 'maxpt', 'mjjmax']
    _plots[name] = hist1( name, '$M_{jj}$ Distribution of Various Jet Selections for '+_input_titles[input_key],
        label_list, 50, (0,2000), xlabel='$M_{jj}$', ylim=(0,0.26))

    name = 'mjj_2jet_'+input_key
    _plots[name] = hist1( name, '$M_{jj}$ Distribution for Two-Jet ' + _input_titles[input_key] + ' Events',
        [''], 50, (0,2000), xlabel='$M_{jj}$', ylim=(0,0.26))

    name = 'correlation_pt_eta_'+input_key
    _plots[name] = hist2( name, 'Correlation Between $\eta$ and $p_T$ of '+_input_titles[input_key],
        50, ( (0,5), (30,200) ), xlabel=('$\eta$'), ylabel=('$p_T$') )

    name = 'correlation_mjj_2maxpt-vs-mjjmax_Disjoint_'+input_key
    _plots[name] = hist2( name, '$M_{jj}$ Correlations Between \'$\Delta$\' maxpt and mjjmax for '+_input_titles[input_key],
        50, ( (0,2000), (0,2000) ), xlabel=('$M_{jj}$ between Leading $p_T$ Jets'), ylabel=('$M_{jj}$ between $M_{jj}$-Max Jets') )

    for key0, key1 in itertools.combinations(['mjjSL', 'maxpt', 'mjjmax'],2):
        name = 'correlation_mjj_'+key0+'-vs-'+key1+'_'+input_key
        _plots[name] = hist2( name, '$M_{jj}$ Correlations Between '+key0+' and '+key1+' for '+_input_titles[input_key],
            50, ( (0,2000), (0,2000) ), xlabel=('$M_{jj}$ between '+key0+' Jets'), ylabel=('$M_{jj}$ between '+key1+' Jets') )

        name = 'correlation_eta_'+key0+'-vs-'+key1+'_'+input_key
        _plots[name] = hist2( name, '$\Delta \eta$ Correlations Between '+key0+' and '+key1+' for '+_input_titles[input_key],
            50, ( (0,10), (0,10) ), xlabel=('$\Delta \eta$ between '+key0+' Jets'), ylabel=('$\Delta \eta$ between '+key1+' Jets') )

        name = 'correlation_sumpt_'+key0+'-vs-'+key1+'_'+input_key
        _plots[name] = hist2( name, '$p_T$ Sum Correlations Between '+key0+' and '+key1+' for '+_input_titles[input_key],
            50, ( (0,500), (0,500) ), xlabel=('$p_T$ Sum of '+key0+' Jets'), ylabel=('$p_T$ Sum of '+key1+' Jets') )


def extract_data():
    for input_type in ['bgd', 'sig']:
        print('Loading '+input_type)
        data_dump = pickle.load( open('data/output_cmilke_record_'+input_type+'.p', 'rb') )

        print('Iterating over JVT 2-Jet Events')
        JVT_events_with_2_jets = [ event for event in data_dump['JVT'].events if len(event.jets) == 2 ]
        for event in JVT_events_with_2_jets:
            jet0 = event.jets[0]
            jet1 = event.jets[1]
            mjj = ( jet0.vector() + jet1.vector() ).mass
            _plots['mjj_2jet_'+input_type].add(mjj)

        print('Iterating over JVT 3-Jet Events')
        JVT_events_with_3_jets = [ event for event in data_dump['JVT'].events if len(event.jets) > 2 ]
        for event in JVT_events_with_3_jets:
            for jet in event.jets:
                _plots['correlation_pt_eta_'+input_type].add(jet.eta(), jet.pt()) 

            Detas, ptsums, mjjs = {}, {}, {}
            for selector_key in ['mjjSL', 'maxpt', 'mjjmax']:
                jet0, jet1 = selector_options[selector_key](event)
                Deta = abs(jet0.eta() - jet1.eta())
                mjj = ( jet0.vector() + jet1.vector() ).mass
                Detas[selector_key] = Deta
                ptsums[selector_key] = jet0.pt() + jet1.pt()
                mjjs[selector_key] = mjj
                _plots['mjj_'+input_type].add(mjj, selector_key)

                if input_type == 'sig':
                    _plots['correlation_mjj_eta_'+selector_key].add(mjj, Deta)
                    if selector_key == 'maxpt':
                        _plots['leading_eta'].add(jet0.eta(), 'any')
                        _plots['leading_eta'].add(jet0.eta(), 'any')
                        _plots['leading_eta_delta'].add(Deta, 'any')

            if selector_options['maxpt'](event) != selector_options['mjjmax'](event):
                _plots['correlation_mjj_2maxpt-vs-mjjmax_Disjoint_'+input_type].add(mjjs['maxpt'], mjjs['mjjmax'])

            for key0, key1 in itertools.combinations(['mjjSL', 'maxpt', 'mjjmax'],2):
                _plots['correlation_mjj_'+key0+'-vs-'+key1+'_'+input_type].add(mjjs[key0], mjjs[key1])
                _plots['correlation_eta_'+key0+'-vs-'+key1+'_'+input_type].add(Detas[key0], Detas[key1])
                _plots['correlation_sumpt_'+key0+'-vs-'+key1+'_'+input_type].add(ptsums[key0], ptsums[key1])


    print('Data extracted, plotting...')


def draw_distributions():
    refresh = len(sys.argv) > 1
    cache = {}
    cache_file = 'studies/cache/general_plots.p'
    if refresh: extract_data()
    else: cache = pickle.load( open(cache_file, 'rb') )

    blacklist = [
        #'correlation'
      #, 'correlation_mjj' , 'correlation_eta' , 'correlation_sumpt'
    ]
    for key,plot in _plots.items():
        valid = True
        for substring in blacklist:
            if substring in key: valid = False
        if valid: plot.generate_plot(refresh, cache)

    if refresh: pickle.dump( cache, open(cache_file, 'wb') )

draw_distributions()
