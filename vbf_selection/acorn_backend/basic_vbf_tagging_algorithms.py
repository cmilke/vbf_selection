from uproot_methods import TLorentzVector


def delta_eta_tagger(event, vbf_jets):
    jet_list = event.jets
    delta_eta = abs( jet_list[vbf_jets[0]].eta - jet_list[vbf_jets[1]].eta )
    return delta_eta


def unified_delta_eta_tagger(event, vbf_jets):
    jet_list = event.jets
    if len(vbf_jets) == 2: return delta_eta_tagger(jet_list, vbf_jets)

    simple_eta = jet_list[vbf_jets[0]].eta
    j1 = jet_list[vbf_jets[1]]
    j2 = jet_list[vbf_jets[2]]
    v1 = TLorentzVector.from_ptetaphim(j0.pt, j0.eta, j0.phi, j0.m)
    v2 = TLorentzVector.from_ptetaphim(j2.pt, j2.eta, j2.phi, j2.m)
    unified_vector = v1+v2
    unified_eta = unified_vector.eta

    delta_eta = abs( simple_eta - unified_eta )
    return delta_eta


def mjj_tagger(event, vbf_jets):
    jet_list = event.jets
    j0 = jet_list[vbf_jets[0]]
    j1 = jet_list[vbf_jets[1]]
    v0 = TLorentzVector.from_ptetaphim(j0.pt, j0.eta, j0.phi, j0.m)
    v1 = TLorentzVector.from_ptetaphim(j1.pt, j1.eta, j1.phi, j1.m)
    combined = v0 + v1
    mjj = combined.mass
    return mjj


def mjjj_tagger(event, vbf_jets):
    jet_list = event.jets
    total_4vector = TLorentzVector(0,0,0,0)
    for jet in jet_list:
        vec = TLorentzVector.from_ptetaphim(jet.pt, jet.eta, jet.phi, jet.m)
        total_4vector += vec
    mjjj = total_4vector.mass
    return mjjj