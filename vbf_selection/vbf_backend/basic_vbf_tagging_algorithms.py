def delta_eta_tagger(event, vbf_jets):
    delta_eta = abs( event[vbf_jets[0]].eta - event[vbf_jets[1]].eta )
    return delta_eta
