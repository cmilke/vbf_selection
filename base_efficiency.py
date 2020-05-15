import uproot
import numpy
import matplotlib
matplotlib.use('Agg')
#matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt


def get_efficiency(file_base, hist_name, cut1, cut2):
    output_dir = '/home/cmilke/Documents/slac_local/output/V4/output_MC16d_'
    directory = uproot.open(output_dir+file_base+'.root')

    hist = directory[hist_name]
    labeled_values = { k:v for k,v in zip(hist.xlabels, hist.values) }
    efficiency = labeled_values[cut2] / labeled_values[cut1]
    print( '{}: {:.02f} / {:.02f} = {:.02f}'.format(file_base, labeled_values[cut2], labeled_values[cut1], efficiency*100) )
    return efficiency


def main():
    #plt.xticks(ticks=numpy.arange(0.5,8.5,1), labels=['ggF', '0', '0.5', '1', '1.5', '2', '4'])
    ggF_base = 'ggF-HH-bbbb'
    VBF_bases = { val:'VBF-HH-bbbb_cvv'+str(val).replace('.','p') for val in [ 0, 0.5, 1, 1.5, 2, 4 ] }

    hist_name_list = [ ('TwoTagCutflow', '2tag'), ('FourTagCutflow','4tag') ]
    #hist_name_list = [  ('FourTagCutflow','4tag') ]
    cut_list = [ 
        ('6 jets, pT > 30 GeV', 'VBF mjj'),
    ]
    for cuts in cut_list:
        print(cuts)
        plot_bins = [0,1,2,3,4,5,6]
        plot_values = {'x': [], 'weights':[], 'label':[],
            'bins': plot_bins+[7], 'histtype':'step', 'linewidth':2
        }
        for hist_name, hist_label in hist_name_list:
            print(hist_name)
            data = []
            data.append( get_efficiency(ggF_base, hist_name, *cuts) )
            for base in VBF_bases.values():
                data.append( get_efficiency(base, hist_name, *cuts) )
            plot_values['x'].append(plot_bins)
            plot_values['weights'].append(data)
            plot_values['label'].append(hist_label)

            print()
        fig,ax = plt.subplots()
        plt.hist(**plot_values)
        plt.xlabel('$\kappa_{2V}$ Value')
        plt.ylabel('Efficiency')
        plt.title('Efficiency of VBF/ggF Discrimination \nas Ratio of Cutflow Bins: \"'+cuts[1]+'\" / \"'+cuts[0]+'\"')
        plt.ylim(0,1)

        ax.set_xticklabels('')
        # Customize minor tick labels
        ax.set_xticks(ticks=numpy.arange(0.5,7.5,1), minor=True)
        ax.set_xticklabels(['ggF', '0', '0.5', '1', '1.5', '2', '4'], minor=True)

        plt.legend()
        plt.grid()
        #plt.show()
        fig.savefig('figures/base-efficiency_'+cuts[0]+'-'+cuts[1]+'.png')
        print('\n------------------------\n')

if __name__ == "__main__": main()
