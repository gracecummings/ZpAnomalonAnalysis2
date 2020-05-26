import ROOT as R
import os,sys
from math import acos,asin,sqrt
R.gROOT.ProcessLine("RestFrames::RFKey load_libRestFrames(1)")



def SetupGenerator(frames):
    # set particle masses and widths
    mH   = 400     # default search value
    mW   = 80.385  # GeV, PDG 2016
    wW   = 2.085
    mL   = 0.106   # muons
    mN   = 0.

    frames['LAB_Gen'] = R.RestFrames.ppLabGenFrame("LAB_Gen","LAB")
    frames['H_Gen']  = R.RestFrames.DecayGenFrame("H_Gen","H^{0}")
    frames['Wa_Gen'] = R.RestFrames.ResonanceGenFrame("Wa_Gen","W_{a}")
    frames['Wb_Gen'] = R.RestFrames.ResonanceGenFrame("Wb_Gen","W_{b}")
    frames['La_Gen'] = R.RestFrames.VisibleGenFrame("La_Gen","#it{l}_{a}")
    frames['Na_Gen'] = R.RestFrames.InvisibleGenFrame("Na_Gen","#nu_{a}")
    frames['Lb_Gen'] = R.RestFrames.VisibleGenFrame("Lb_Gen","#it{l}_{b}")
    frames['Nb_Gen'] = R.RestFrames.InvisibleGenFrame("Nb_Gen","#nu_{b}")
    
    frames['LAB_Gen'].SetChildFrame(frames['H_Gen']);
    frames['H_Gen'].AddChildFrame(frames['Wa_Gen']);
    frames['H_Gen'].AddChildFrame(frames['Wb_Gen']);
    frames['Wa_Gen'].AddChildFrame(frames['La_Gen']);
    frames['Wa_Gen'].AddChildFrame(frames['Na_Gen']);
    frames['Wb_Gen'].AddChildFrame(frames['Lb_Gen']);
    frames['Wb_Gen'].AddChildFrame(frames['Nb_Gen']);

    if frames['LAB_Gen'].InitializeTree():
        print("...Successfully initialized generator tree")
    else:
        print("...Failed initializing generator tree")

    # set Higgs masses
    frames['H_Gen'].SetMass(mH);
    # set W masses and widths
    frames['Wa_Gen'].SetMass(mW);               frames['Wa_Gen'].SetWidth(wW)
    frames['Wb_Gen'].SetMass(mW);               frames['Wb_Gen'].SetWidth(wW)
    # set lepton and neutrino masses
    frames['La_Gen'].SetMass(mL);               frames['Lb_Gen'].SetMass(mL)

    # set lepton pT and eta cuts
    frames['La_Gen'].SetPtCut(10.);             frames['Lb_Gen'].SetPtCut(10.)
    frames['La_Gen'].SetEtaCut(2.5);            frames['Lb_Gen'].SetEtaCut(2.5)
    
    if frames['LAB_Gen'].InitializeAnalysis():
        print("...Successfully initialized generator analysis")
    else:
        print("...Failed initializing generator analysis")

    return
    ########## End of Generator setup ##########

    
def SetupRecoFrame(frames):
    frames['LAB'] = R.RestFrames.LabRecoFrame("LAB","LAB");
    frames['H'] = R.RestFrames.DecayRecoFrame("H","H^{ 0}");
    frames['Wa'] = R.RestFrames.DecayRecoFrame("Wa","W_{a}");
    frames['Wb'] = R.RestFrames.DecayRecoFrame("Wb","W_{b}");
    frames['La'] = R.RestFrames.VisibleRecoFrame("La","#it{l}_{a}");
    frames['Na'] = R.RestFrames.InvisibleRecoFrame("Na","#nu_{a}");
    frames['Lb'] = R.RestFrames.VisibleRecoFrame("Lb","#it{l}_{b}");
    frames['Nb'] = R.RestFrames.InvisibleRecoFrame("Nb","#nu_{b}");
    
    frames['LAB'].SetChildFrame(frames['H']);
    frames['H'].AddChildFrame(frames['Wa']);
    frames['H'].AddChildFrame(frames['Wb']);
    frames['Wa'].AddChildFrame(frames['La']);
    frames['Wa'].AddChildFrame(frames['Na']);
    frames['Wb'].AddChildFrame(frames['Lb']);
    frames['Wb'].AddChildFrame(frames['Nb']);
    
    if frames['LAB'].InitializeTree():
        print("...Successfully initialized reconstruction tree")
    else:
        print("...Failed initializing reconstruction tree")

    # Invisible Group
    frames['INV'] = R.RestFrames.InvisibleGroup("INV","#nu #nu Jigsaws")
    frames['INV'].AddFrame(frames['Na'])
    frames['INV'].AddFrame(frames['Nb'])

    # Set nu nu mass equal to l l mass
    frames['NuNuM'] = R.RestFrames.SetMassInvJigsaw("NuNuM", "M_{#nu#nu} = m_{#it{l}#it{l}}")
    frames['INV'].AddJigsaw(frames['NuNuM'])

    frames['NuNuR'] = R.RestFrames.SetRapidityInvJigsaw("NuNuR", "#eta_{#nu#nu} = #eta_{#it{l}#it{l}}")
    frames['INV'].AddJigsaw(frames['NuNuR'])
    
    #NuNuR.AddVisibleFrames( frames['LAB'].GetListVisibleFrames() )    
    vframes = frames['LAB'].GetListVisibleFrames()
    for i in range(vframes.GetN()):
        frames['NuNuR'].AddVisibleFrame( vframes.Get(i) )

    # MinMassesSqInvJigsaw MinMW("MinMW","min M_{W}, M_{Wa}= M_{Wb}",2);
    frames['MinMW'] = R.RestFrames.ContraBoostInvJigsaw("MinMW","min M_{W}, M_{Wa}= M_{Wb}")
    frames['INV'].AddJigsaw(frames['MinMW'])
    frames['MinMW'].AddVisibleFrame(frames['La'], 0)
    frames['MinMW'].AddVisibleFrame(frames['Lb'], 1)
    frames['MinMW'].AddInvisibleFrame(frames['Na'], 0)
    frames['MinMW'].AddInvisibleFrame(frames['Nb'], 1)

    if frames['LAB'].InitializeAnalysis():
        print("...Successfully initialized analysis")
    else:
        print("...Failed initializing analysis")
        
    return frames
    ########## End of Reco setup ##########

def PlotTree(rFrame,name="tree",title="Tree",flag=False):
    treePlot = R.RestFrames.TreePlot("TreePlot","TreePlot")

    treePlot.SetTree(rFrame);
    treePlot.Draw(name, title, flag)
    R.SetOwnership( treePlot, False )

#################################################################
# MAIN
#################################################################
# Number of events to generate
Ngen = 10000

print("Initializing generator frames and tree...")
genFrames={};
recoFrames={};
SetupGenerator(genFrames)
SetupRecoFrame(recoFrames)

PlotTree(genFrames['LAB_Gen'],"GenTree","Generator Tree",True)
PlotTree(recoFrames['LAB'],"RecoTree", "Reconstruction Tree")
PlotTree(recoFrames['INV'],"InvTree", "Invisible Jigsaws", True);

h_MH = R.TH1F("MH", "M_{H^{ 0}}", 64, 0., 3000.)
h_DcosH = R.TH1F("DcosH","#theta_{H^{ 0}} - #theta_{H^{ 0}}^{true}", 64,
		 -acos(-1.)/2., acos(-1.)/2.)

#genFrames['H_Gen'].SetMass(1000.); # not working
for igen in range(Ngen):
    if(igen%(max(Ngen,10)/10) == 0): print("Generating event ",igen,"of",Ngen)
    #generate event
    genFrames['LAB_Gen'].ClearEvent()                            # clear the gen tree
    status=genFrames['LAB_Gen'].AnalyzeEvent()                   # generate a new event
    #print("genstatus", status)
    
    #analyze event
    recoFrames['LAB'].ClearEvent();                               #clear the reco tree
    MET = genFrames['LAB_Gen'].GetInvisibleMomentum()         # Get the MET from gen tree [TVector3]
    MET.SetZ(0.);
    print type(MET)
    recoFrames['INV'].SetLabFrameThreeVector(MET);            # Set the MET in reco tree
    recoFrames['La'].SetLabFrameFourVector(genFrames['La_Gen'].GetFourVector())  # set lepton 4-vectors
    recoFrames['Lb'].SetLabFrameFourVector(genFrames['Lb_Gen'].GetFourVector())
    
    recoFrames['LAB'].AnalyzeEvent()                                # analyze the event

    # Generator-level observables
    cosHgen  = genFrames['H_Gen'].GetCosDecayAngle()
    cosH = cosHgen
    cosWagen  = genFrames['Wa_Gen'].GetCosDecayAngle()
    cosWa = cosWagen

    # Reconstruction-level observables
    MH   = recoFrames['H'].GetMass()
    MHN  = recoFrames['H'].GetMass()/genFrames['H_Gen'].GetMass();
    MWaN = recoFrames['Wa'].GetMass()/genFrames['Wa_Gen'].GetMass();
    cosH  = recoFrames['H'].GetCosDecayAngle();
    cosWa = recoFrames['Wa'].GetCosDecayAngle();
    DcosH  = asin(sqrt(1.-cosH*cosH)*cosHgen-sqrt(1.-cosHgen*cosHgen)*cosH);
    DcosWa = asin(sqrt(1.-cosWa*cosWa)*cosWagen-sqrt(1.-cosWagen*cosWagen)*cosWa);

    h_MH.Fill(MH)
    h_DcosH.Fill(DcosH)

tc=R.TCanvas()
tc.Divide(2,1)
tc.cd(1); h_MH.Draw()
tc.cd(2); h_DcosH.Draw()
tc.Draw()
print("Hit return to exit")
sys.stdin.readline()
