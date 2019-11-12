#!/nfs/slac/g/atlas/u02/cmilke/Anaconda3/bin/python
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle
from math import pi
from acorn_backend import jet_selectors


_phiticks=[ -4, -(4/4)*pi,-(3/4)*pi, -(2/4)*pi, -(1/4)*pi, 0, (1/4)*pi, (2/4)*pi, (3/4)*pi, (4/4)*pi , 4]
_philabels=[
    r''
  , r'$-\pi$'
  , r'$-\frac{3}{4}\pi$'
  , r'$-\frac{1}{2}\pi$'
  , r'$-\frac{1}{4}\pi$'
  , r'$0$'
  , r'$\frac{1}{4}\pi$'
  , r'$\frac{1}{2}\pi$'
  , r'$\frac{3}{4}\pi$'
  , r'$\pi$'
  , r''
]
_jet_radius=0.4
_category_key = 'JVT'
_mjjj_80percent_rejection_cut = 630 #GeV
_mjj_2maxpt_80percent_rejection_cut = 333 #GeV


def display_events(info_list, type_name, type_title):
    print( 'Displaying ' + type_name )
    output = PdfPages('plots/figures/fig_event_display_'+type_name+'.pdf')
    for jets in info_list:
        fig,ax = plt.subplots()
        ax.set_facecolor('0.4')
        jet_scatter = plt.scatter(jets[1], jets[2], c=jets[3], cmap='plasma', vmin=0, vmax=100)
        for x,y,z,c in zip(*jets[1:]):
            ax.add_artist( Circle( xy=(x, y), radius=_jet_radius, facecolor='None', edgecolor=c) )

        cbar = plt.colorbar(jet_scatter)
        cbar.set_label('Jet $p_t$ (GeV)')
        plt.xlim(-5, 5)
        plt.ylim(-pi, pi)
        plt.yticks(ticks=_phiticks, labels=_philabels)
        plt.xlabel('Jet $\eta$')
        plt.ylabel('Jet $\phi$')

        plt.title( 'Event Display for ' + type_title )
        #plt.show()
        output.savefig()
        plt.close()
    output.close()


def display(data_dump, passes_event_test, type_name, type_title):
    info_list = []
    event_index = 0
    for event in data_dump[_category_key].events:
        if event_index >= 100: break
        if len(event.jets) != 3: continue
        event_index += 1

        if not passes_event_test(event): continue

        info = [ event_index, [], [], [], [] ] #eta, phi, pt, truthquark
        for jet in event.jets:
            info[1].append(jet.vector.eta)
            info[2].append(jet.vector.phi)
            info[3].append(jet.vector.pt)
            color = 'blue'
            if jet.is_truth_quark(): color = 'yellow'
            info[4].append(color)
        info_list.append(info)

    display_events( info_list, type_name, type_title )


def passes_mjjj(event):
    mjjj = event.selectors['2maxpt'].taggers['mjjj'].discriminant
    return mjjj > _mjjj_80percent_rejection_cut 
    

def fails_mjjj(event):
    return not passes_mjjj(event)


def passes_mjjj_and_fails_mjj2maxpt(event):
    mjjj = event.selectors['2maxpt'].taggers['mjjj'].discriminant
    mjj = event.selectors['2maxpt'].taggers['mjj'].discriminant
    passes_mjjj = mjjj > _mjjj_80percent_rejection_cut 
    fails_mjj = mjj < _mjj_2maxpt_80percent_rejection_cut
    return passes_mjjj and fails_mjj


sig_data_dump = pickle.load( open('data/output_sig.p', 'rb') )
bgd_data_dump = pickle.load( open('data/output_bgd.p', 'rb') )

display(sig_data_dump, passes_mjjj, 'sig_pass_mjjj', 'Signal Event which\nCorrectly Pass $M_{jjj}$')
display(bgd_data_dump, fails_mjjj, 'bgd_fail_mjjj', 'Background Event which\nCorrectly Fail $M_{jjj}$')
display(bgd_data_dump, passes_mjjj_and_fails_mjj2maxpt, 'bgd_pass_mjjj_fail_mjj', 'Background Events\nwhich Correctly Fail $M_{jj}$ but Incorrectly Pass $M_{jjj}$')
