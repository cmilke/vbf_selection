def delta_eta_tagger(event, vbf_jets):
    delta_eta = abs( event[vbf_jets[0]].eta - event[vbf_jets[1]].eta )
    return delta_eta


def mjj_tagger(event, vbf_jets):
    m0 = event[vbf_jets[0]].m
    m1 = event[vbf_jets[1]].m
    mjj = m0 + m1
    return mjj


def mjjj_tagger(event, vbf_jets):
    mjjj = 0
    for jet in event: mjjj += jet.m
    return mjjj
