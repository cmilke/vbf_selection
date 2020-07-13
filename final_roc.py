#!/usr/bin/python3

import uproot
import numpy
import re
from matplotlib import pyplot as plt



def get_final_sig(outputname, hist_name, stage_to_print):
    directory = uproot.open(outputname)
    cutflow_hist = directory[hist_name]
    labeled_values = { k:v for k,v in zip(cutflow_hist.xlabels, cutflow_hist.values) }
    return labeled_values[stage_to_print]
        


def main():
    ntupledir = '../nano_ntuple_maker/run/'
    base_names = { val:'VBF-HH-bbbb_cvv'+str(val).replace('.','p') for val in [ 0, 0.5, 1, 1.5, 2 ] }
    base_names['ggF'] = 'ggF-HH-bbbb'

    cutvalues = numpy.arange(-0.2, 0.21, 0.01)
    cutstrlist = []
    for cutval in cutvalues:
        cutstrlist.append(re.sub('0(?=[.])', '', f'{cutval:.02f}'))
    cutstrlist[ cutstrlist.index('-.20') ] = '-0.2'
    cutstrlist[ cutstrlist.index('.00') ] = '0'
    cutlist = list( zip(cutvalues, cutstrlist) )
    


    #print(' 6Jet | Pair | VSel | Deta | mjj  |  HH  |')
    data = {}
    base_sig = {}
    for cvv, base in base_names.items():
        data[cvv] = ([],[])
        print(cvv)
        for cutval, cutstr in cutlist:
            ntuple = ntupledir+'scan00/output_MC16d_'+base+'_scanVBFcut_'+cutstr+'.root'
            significance = get_final_sig(ntuple, 'FourTagCutflow', 'dEta_hh')
            data[cvv][0].append(cutval)
            data[cvv][1].append(significance)
        base_ntuple = ntupledir+'V9/output_MC16d_'+base+'_dump.root'
        base_sig[cvv] = get_final_sig(base_ntuple, 'FourTagCutflow', 'dEta_hh')
    print(base_sig)

    #for key, (cuts,sigs) in data.items():
    #    print(key)
    #    for cut,sig in zip(cuts,sigs): print(f'{cut:.02f}: {sig:.05f}')
    #    print()

    for key, (cuts,sigs) in data.items():
        plt.plot(cuts, sigs, label=key)
    plt.legend()
    plt.grid(True)
    plt.xlabel('BDT Cut Value')
    plt.ylabel(r'Significance of $\Delta \eta_{HH}$')
    #plt.ylim(0,0.33)
    plt.yscale('log')
    plt.title('Cut VS Significance')
    plt.savefig('figures/significance_comparison.png')
    plt.close()

    signal_dict = { key:val[1] for key,val in data.items() if key != 'ggF' }
    background= data['ggF'][1]

    for key, signal in signal_dict.items():
        plt.plot(signal, background, label=key)
    plt.legend()
    plt.grid(True)
    plt.xlabel('VBF Signficance')
    plt.ylabel('ggF Signficance')
    plt.xscale('log')
    plt.title('ggF VS VBF Significance')
    plt.savefig('figures/final_roc.png')
    plt.close()





if __name__ == "__main__": main()
