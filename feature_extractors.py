import itertools

from uproot_methods import TLorentzVector as LV

_fourvec_names = [ f'vbf_candidates_{v}' for v in ['pT', 'eta', 'phi', 'E'] ]
make_vector_list = lambda datarow: [ LV.from_ptetaphie(*vec) for vec in zip(*datarow[_fourvec_names]) ]

def get_features_mjj_deta(datarow):
    vector_list = make_vector_list(datarow)
    pair_list = [ (i,j) for i,j in itertools.combinations(vector_list, 2) ]
    if len(pair_list) > 0:
        mjj_deta_pair_list = [ ( (i+j).mass, abs(i.eta-j.eta) ) for i,j in pair_list]
        mjj_deta_pair_list.sort(reverse=True)
        prepared_features = [
            mjj_deta_pair_list[0][0],
            mjj_deta_pair_list[0][1]
        ]
    else:
        prepared_features = [-1,-1]
    return prepared_features



def get_features_mjj_deta_fw(datarow):
    vector_list = make_vector_list(datarow)
    pair_list = [ (i,j) for i,j in itertools.combinations(vector_list, 2) ]
    if len(pair_list) > 0:
        mjj_deta_pair_list = [ ( (i+j).mass, abs(i.eta-j.eta) ) for i,j in pair_list]
        mjj_deta_pair_list.sort(reverse=True)
        feature_list = [
            mjj_deta_pair_list[0][0],
            mjj_deta_pair_list[0][1]
        ]
        feature_list += [ datarow[f'FoxWolfram{fwi}'] for fwi in range(1,8) ]
    else:
        feature_list = [-1]*9
    return feature_list


def get_features_mjj_deta_fw_cent(datarow):
    vector_list = make_vector_list(datarow)
    if len(vector_list) > 1:
        pair_list = [ (i,j) for i,j in itertools.combinations(vector_list, 2) ]
        mjj_deta_pair_list = [ ( (i+j).mass, abs(i.eta-j.eta) ) for i,j in pair_list]
        mjj_deta_pair_list.sort(reverse=True)
        feature_list = [
            mjj_deta_pair_list[0][0],
            mjj_deta_pair_list[0][1]
        ]
        feature_list += [ datarow[f'FoxWolfram{fwi}'] for fwi in range(1,8) ]

        centrality = -1
        if len(vector_list) > 2:
            mjj_pairs = [ ( (vector_list[i]+vector_list[j]).mass, (i,j) ) for i,j in itertools.combinations(range(len(vector_list)), 2) ]
            mjj_pairs.sort(reverse=True)
            chosen_jets = { i:vector_list[i] for i in mjj_pairs[0][1] }
            possible_additions = [ (i,vector_list[i]) for i in mjj_pairs[1][1] if i not in chosen_jets ]
            possible_additions.sort(key=lambda t: t[1].pt, reverse=True)
            chosen_jets[ possible_additions[0][0] ] = possible_additions[0][1]
            etas = sorted([ jet.eta for jet in chosen_jets.values() ])
            centrality = abs(2*(etas[1] - etas[0]) / (etas[2] - etas[0]) - 1)
        feature_list.append(centrality)
    else:
        feature_list = [-1]*10
    return feature_list



def get_features_mjjLSL_deta_cent_fw(datarow):
    vector_list = make_vector_list(datarow)
    if len(vector_list) > 1:
        pair_list = [ (i,j) for i,j in itertools.combinations(vector_list, 2) ]
        mjj_deta_pair_list = [ ( (i+j).mass, abs(i.eta-j.eta) ) for i,j in pair_list]
        mjj_deta_pair_list.sort(reverse=True)
        feature_list = [
            mjj_deta_pair_list[0][0],
            mjj_deta_pair_list[0][1]
        ]
        if len(vector_list) > 2:
            feature_list += [
                mjj_deta_pair_list[1][0],
                mjj_deta_pair_list[1][1]
            ]

            mjj_pairs = [ ( (vector_list[i]+vector_list[j]).mass, (i,j) ) for i,j in itertools.combinations(range(len(vector_list)), 2) ]
            mjj_pairs.sort(reverse=True)
            chosen_jets = { i:vector_list[i] for i in mjj_pairs[0][1] }
            possible_additions = [ (i,vector_list[i]) for i in mjj_pairs[1][1] if i not in chosen_jets ]
            possible_additions.sort(key=lambda t: t[1].pt, reverse=True)
            chosen_jets[ possible_additions[0][0] ] = possible_additions[0][1]
            etas = sorted([ jet.eta for jet in chosen_jets.values() ])
            centrality = abs(2*(etas[1] - etas[0]) / (etas[2] - etas[0]) - 1)
            feature_list.append(centrality)
        else:
            feature_list += [-1,-1,-1]

        feature_list += [ datarow[f'FoxWolfram{fwi}'] for fwi in range(1,8) ]
    else:
        feature_list = [-1]*12
    return feature_list


Extractors = {
    'mjj-Deta': get_features_mjj_deta,
    'mjj-Deta-FW': get_features_mjj_deta_fw,
    'mjj-Deta-FW-Cent': get_features_mjj_deta_fw_cent,
    'mjjLSL-Deta-Cent-FW': get_features_mjjLSL_deta_cent_fw,
}
