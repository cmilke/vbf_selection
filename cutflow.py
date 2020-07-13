#!/usr/bin/python3

import sys
import uproot



def get_vals(outputname, hist_name, stages_to_print):
    directory = uproot.open(outputname)
    cutflow_hist = directory[hist_name]
    labeled_values = { k:v for k,v in zip(cutflow_hist.xlabels, cutflow_hist.values) }
    recorded_vals = [ labeled_values[key] for key in stages_to_print ]
    for val in recorded_vals: print(f'{val:.4f} ', end=' ')
    print()
        


def main():
    base_names = { val:'VBF-HH-bbbb_cvv'+str(val).replace('.','p') for val in [ 0, 0.5, 1, 1.5, 2, 4 ] }
    base_names['ggF'] = 'ggF-HH-bbbb'

    #print(' 6Jet | Pair | VSel | Deta | mjj  |  HH  |')
    for cvv, base in base_names.items():
        print(cvv)
        for mode in ['dump', 'cut']:
            stages_to_print = [
                #'6 jets, pT > 30 GeV',
                'VBF Pair',
                'VBF dEta',
                'VBF mjj',
                'VBF BDT',
                '4 good jets (w/o IS), >= 2 tagged',
                'Multi Tagged',
                'Valid',
                'VBF pTsum',
                'pT(h)s',
                'dEta_hh'
            ]
            outputname = '../output/'+sys.argv[1]+'/output_MC16d_'+base+'_'+mode+'.root'
            get_vals(outputname, 'FourTagCutflow', stages_to_print)
        print('-----------------------------------------')



if __name__ == "__main__": main()
