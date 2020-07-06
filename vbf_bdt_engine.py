import sys

sys.argv.append('-b')
import ROOT
from ROOT import TMVA, TFile, TCut, TCanvas, RDataFrame



def rvec(*var_list):
    branch_list = ROOT.vector('string') ()
    for var in var_list: branch_list.push_back(var)
    return branch_list



ROOT.gInterpreter.Declare("""
    using Vec_t = const ROOT::VecOps::RVec<float>;
    using Vec_4 = ROOT::Math::PtEtaPhiEVector;
    using Pair = std::tuple<Vec_4, Vec_4>;

    std::vector<Vec_4> make_vectors(Vec_t& pt, Vec_t& eta, Vec_t& phi, Vec_t& e) {
            std::vector<Vec_4> vectors;
            for ( int i=0; i<pt.size(); i++ ) {
                vectors.push_back( Vec_4(pt[i], eta[i], phi[i], e[i]) );
            }
            return vectors;
    }

    float get_mjj(Pair pair) { return (std::get<0>(pair) + std::get<1>(pair)).M(); }

    bool mjj_decending(const Pair first, const Pair second) { return get_mjj(first) > get_mjj(second); }

    std::vector<Pair> make_pairs( std::vector<Vec_4> vectors) {
        std::vector<Pair> pair_list;
        for (int i = 0; i < vectors.size(); i++) {
            for (int j = i+1; j < vectors.size(); j++) {
                pair_list.push_back( Pair(vectors[i], vectors[j]) );
            }
        }
        std::sort( pair_list.begin(), pair_list.end(), mjj_decending ); 
        return pair_list;
    }
""")



def retrieve_data(inname, outname, input_variables):
    dataframe = RDataFrame('VBF_tree', inname)
    vectors = dataframe.Define('vectors', 'make_vectors(vbf_candidates_pT, vbf_candidates_eta, vbf_candidates_phi, vbf_candidates_E)' )
    pairs = vectors.Filter('vectors.size() > 1').Define('pairs', 'make_pairs(vectors)' )
    mjj = pairs.Define('mjj', 'get_mjj(pairs[0])')
    deta = mjj.Define('mjj_Deta', 'abs( std::get<0>(pairs[0]).eta() - std::get<1>(pairs[0]).eta() )')
    weighted = deta.Define('weight', 'mc_sf[0]')

    trimmed = weighted.Range(0,15000)
    trimmed.Snapshot('data', outname, rvec(*input_variables, 'weight'))


def main():
    input_variables = ['mjj', 'mjj_Deta']
    input_variables += [f'FoxWolfram{i}' for i in range(1,8)]

    retrieve_data('../output/V5/output_MC16d_VBF-HH-bbbb_cvv1.root', 'bdt_output/signal.root', input_variables)
    retrieve_data('../output/V5/output_MC16d_ggF-HH-bbbb.root' , 'bdt_output/background.root', input_variables)

    sigfile = TFile.Open( 'bdt_output/signal.root' )
    sigtree = sigfile.Get('data')
    bgdfile = TFile.Open( 'bdt_output/background.root' )
    bgdtree = bgdfile.Get('data')

    TMVA.Tools.Instance()
    dataloader = TMVA.DataLoader("bdt_output")
    for var in input_variables: dataloader.AddVariable(var, 'F')
    dataloader.AddSignalTree(sigtree, 1)
    dataloader.AddBackgroundTree(bgdtree, 1)
    dataloader.SetSignalWeightExpression("weight")
    dataloader.SetBackgroundWeightExpression("weight")

    dataloader.PrepareTrainingAndTestTree(TCut(''), 'nTrain_Signal=10000:nTrain_Background=10000:nTest_Signal=5000:nTest_Background=5000'
        ':SplitMode=Random:NormMode=NumEvents:!V')

    atype = 'Classification'
    split_type = 'Random'
    num_folds = 3
    split_expr = '' # Used for deterministic split type
    #cvOptions = f'!V:!Silent:ModelPersistence:AnalysisType={atype}:SplitType={split_type}:NumFolds={num_folds}:SplitExpr={split_expr}'
    cvOptions = f'!V:!Silent:ModelPersistence:AnalysisType={atype}:SplitType={split_type}:NumFolds={num_folds}'
    cross_validator = TMVA.CrossValidation("TMVACrossValidation", dataloader, cvOptions)

    cross_validator.BookMethod(TMVA.Types.kBDT, 'cuts10,depth3',
            '!H:!V'
            ':NTrees=200:MinNodeSize=2.5%'
            ':BoostType=AdaBoost'
            ':NegWeightTreatment=Pray'
            ':Shrinkage=0.10'
            ':nCuts=10'
            ':MaxDepth=3'
    )

    #cross_validator.BookMethod(TMVA.Types.kBDT, 'cuts50,depth4',
    #        '!H:!V'
    #        ':NTrees=500:MinNodeSize=2.5%'
    #        ':BoostType=AdaBoost'
    #        ':NegWeightTreatment=Pray'
    #        ':Shrinkage=0.10'
    #        ':nCuts=50'
    #        ':MaxDepth=4'
    #)

    #cross_validator.BookMethod(TMVA.Types.kBDT, 'cuts50,depth8',
    #        '!H:!V'
    #        ':NTrees=500:MinNodeSize=2.5%'
    #        ':BoostType=AdaBoost'
    #        ':NegWeightTreatment=Pray'
    #        ':Shrinkage=0.10'
    #        ':nCuts=50'
    #        ':MaxDepth=8'
    #)

    cross_validator.Evaluate()

    canvas = TCanvas('pad','',800,600)
    roc = cross_validator.GetResults()[0].GetAvgROCCurve(100)
    roc.GetXaxis().SetTitle('Signal Efficiency');
    roc.GetYaxis().SetTitle('Background Rejection');
    roc.Draw('ACP')
    #roc = cross_validator.GetResults()[1].GetAvgROCCurve(100)
    #roc.Draw('same')
    #roc = cross_validator.GetResults()[2].GetAvgROCCurve(100)
    #roc.Draw('same')
    #canvas.BuildLegend()
    canvas.SetGridx()
    canvas.SetGridy()
    canvas.SaveAs('training_roc.png')

main()
