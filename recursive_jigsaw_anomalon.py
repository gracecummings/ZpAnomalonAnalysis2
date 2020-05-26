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
    frames['Zp_Gen']  = R.RestFrames.DecayGenFrame("H_Gen","H^{0}")
    frames['Wa_Gen'] = R.RestFrames.ResonanceGenFrame("Wa_Gen","W_{a}")
    frames['Wb_Gen'] = R.RestFrames.ResonanceGenFrame("Wb_Gen","W_{b}")
    frames['La_Gen'] = R.RestFrames.VisibleGenFrame("La_Gen","#it{l}_{a}")
    frames['Na_Gen'] = R.RestFrames.InvisibleGenFrame("Na_Gen","#nu_{a}")
    frames['Lb_Gen'] = R.RestFrames.VisibleGenFrame("Lb_Gen","#it{l}_{b}")
    frames['Nb_Gen'] = R.RestFrames.InvisibleGenFrame("Nb_Gen","#nu_{b}")
    
    frames['LAB_Gen'].SetChildFrame(frames['Zp_Gen']);
    frames['Zp_Gen'].AddChildFrame(frames['Wa_Gen']);
    frames['Zp_Gen'].AddChildFrame(frames['Wb_Gen']);
    frames['Wa_Gen'].AddChildFrame(frames['La_Gen']);
    frames['Wa_Gen'].AddChildFrame(frames['Na_Gen']);
    frames['Wb_Gen'].AddChildFrame(frames['Lb_Gen']);
    frames['Wb_Gen'].AddChildFrame(frames['Nb_Gen']);

    #if frames['LAB_Gen'].InitializeTree():
    #    print("...Successfully initialized generator tree")
    #else:
    #    print("...Failed initializing generator tree")

    # set Zpiggs masses
    frames['Zp_Gen'].SetMass(mH);
    # set W masses and widths
    frames['Wa_Gen'].SetMass(mW);               frames['Wa_Gen'].SetWidth(wW)
    frames['Wb_Gen'].SetMass(mW);               frames['Wb_Gen'].SetWidth(wW)
    # set lepton and neutrino masses
    frames['La_Gen'].SetMass(mL);               frames['Lb_Gen'].SetMass(mL)

    # set lepton pT and eta cuts
    frames['La_Gen'].SetPtCut(10.);             frames['Lb_Gen'].SetPtCut(10.)
    frames['La_Gen'].SetEtaCut(2.5);            frames['Lb_Gen'].SetEtaCut(2.5)
    
    #if frames['LAB_Gen'].InitializeAnalysis():
    #    print("...Successfully initialized generator analysis")
    #else:
    #    print("...Failed initializing generator analysis")

    return
    ########## End of Generator setup ##########

    
def SetupRecoFrame(frames):
    frames['LAB'] = R.RestFrames.LabRecoFrame("LAB","LAB");
    frames['Zp'] = R.RestFrames.DecayRecoFrame("Zp","Z'");
    frames['ND'] = R.RestFrames.DecayRecoFrame("ND","ND");
    frames['NDbar'] = R.RestFrames.DecayRecoFrame("NDbar","ND~");
    frames['Z'] = R.RestFrames.VisibleRecoFrame("Z","Z_{0}");
    frames['NS'] = R.RestFrames.InvisibleRecoFrame("NS","NS");
    frames['h'] = R.RestFrames.VisibleRecoFrame("h","h");
    frames['NSbar'] = R.RestFrames.InvisibleRecoFrame("NSbar","NS~");
    
    frames['LAB'].SetChildFrame(frames['Zp']);
    frames['Zp'].AddChildFrame(frames['ND']);
    frames['Zp'].AddChildFrame(frames['NDbar']);
    frames['ND'].AddChildFrame(frames['Z']);
    frames['ND'].AddChildFrame(frames['NS']);
    frames['NDbar'].AddChildFrame(frames['h']);
    frames['NDbar'].AddChildFrame(frames['NSbar']);
    
    if not frames['LAB'].InitializeTree():
        print("...Failed initializing reconstruction tree")

    # Invisible Group
    frames['INV'] = R.RestFrames.InvisibleGroup("INV","NS NS~ Jigsaws")
    frames['INV'].AddFrame(frames['NS'])
    frames['INV'].AddFrame(frames['NSbar'])

    # Set NS NS mass equal to Z h mass
    frames['NSNSM'] = R.RestFrames.SetMassInvJigsaw("NSNSM", "M_(NSNS} = m_{zh}")
    frames['INV'].AddJigsaw(frames['NSNSM'])
    
    #Set Rapidity Jigsaw
    frames['NSNSR'] = R.RestFrames.SetRapidityInvJigsaw("NSNSR", "#eta_{NSNS} = #eta_{zh}")
    frames['INV'].AddJigsaw(frames['NSNSR'])
    
    #NuNuR.AddVisibleFrames( frames['LAB'].GetListVisibleFrames() )    
    vframes = frames['LAB'].GetListVisibleFrames()
    for i in range(vframes.GetN()):
        frames['NSNSR'].AddVisibleFrame( vframes.Get(i) )

    # MinMassesSqInvJigsaw MinMW("MinMW","min M_{W}, M_{ND}= M_{Wb}",2);
    frames['MinMND'] = R.RestFrames.ContraBoostInvJigsaw("MinMND","min M_{ND}, M_{ND}= M_{ND}")
    frames['INV'].AddJigsaw(frames['MinMND'])
    frames['MinMND'].AddVisibleFrame(frames['Z'], 0)
    frames['MinMND'].AddVisibleFrame(frames['h'], 1)
    frames['MinMND'].AddInvisibleFrame(frames['NS'], 0)
    frames['MinMND'].AddInvisibleFrame(frames['NSbar'], 1)

    #if frames['LAB'].InitializeAnalysis():
        #print("...Successfully initialized analysis")
    #else:
    #    print("...Failed initializing analysis")
        
    return frames
    ########## End of Reco setup ##########

#def PlotTree(rFrame,name="tree",title="Tree",flag=False):
#    treePlot = R.RestFrames.TreePlot("TreePlot","TreePlot")
#
#    treePlot.SetTree(rFrame);
#    treePlot.Draw(name, title, flag)
#    R.SetOwnership( treePlot, False )
#
##################################################################
## MAIN
##################################################################
## Number of events to generate
#Ngen = 10000
#
#print("Initializing generator frames and tree...")
#genFrames={};
#recoFrames={};
#SetupGenerator(genFrames)
#SetupRecoFrame(recoFrames)
#
#PlotTree(genFrames['LAB_Gen'],"GenTree","Generator Tree",True)
#PlotTree(recoFrames['LAB'],"RecoTree", "Reconstruction Tree")
#PlotTree(recoFrames['INV'],"InvTree", "Invisible Jigsaws", True);
#
#h_MZp = R.TH1F("MZp", "M_{Zp^{ 0}}", 64, 0., 3000.)
#h_DcosZp = R.TH1F("DcosH","#theta_{H^{ 0}} - #theta_{H^{ 0}}^{true}", 64,
#		 -acos(-1.)/2., acos(-1.)/2.)
#
##genFrames['Zp_Gen'].SetMass(1000.); # not working
#for igen in range(Ngen):
#    if(igen%(max(Ngen,10)/10) == 0): print("Generating event ",igen,"of",Ngen)
#    #generate event
#    genFrames['LAB_Gen'].ClearEvent()                            # clear the gen tree
#    status=genFrames['LAB_Gen'].AnalyzeEvent()                   # generate a new event
#    #print("genstatus", status)
#    
#    #analyze event
#    recoFrames['LAB'].ClearEvent();                               #clear the reco tree
#    MET = genFrames['LAB_Gen'].GetInvisibleMomentum()         # Get the MET from gen tree [TVector3]
#    MET.SetZ(0.);
#    recoFrames['INV'].SetLabFrameThreeVector(MET);            # Set the MET in reco tree
#    recoFrames['La'].SetLabFrameFourVector(genFrames['La_Gen'].GetFourVector())  # set lepton 4-vectors
#    recoFrames['Lb'].SetLabFrameFourVector(genFrames['Lb_Gen'].GetFourVector())
#    
#    recoFrames['LAB'].AnalyzeEvent()                                # analyze the event
#
#    # Generator-level observables
#    cosHgen  = genFrames['H_Gen'].GetCosDecayAngle()
#    cosH = cosHgen
#    cosNDgen  = genFrames['ND_Gen'].GetCosDecayAngle()
#    cosND = cosNDgen
#
#    # Reconstruction-level observables
#    MH   = recoFrames['H'].GetMass()
#    MHN  = recoFrames['H'].GetMass()/genFrames['H_Gen'].GetMass();
#    MNDN = recoFrames['ND'].GetMass()/genFrames['ND_Gen'].GetMass();
#    cosH  = recoFrames['H'].GetCosDecayAngle();
#    cosND = recoFrames['ND'].GetCosDecayAngle();
#    DcosH  = asin(sqrt(1.-cosH*cosH)*cosHgen-sqrt(1.-cosHgen*cosHgen)*cosH);
#    DcosND = asin(sqrt(1.-cosND*cosND)*cosNDgen-sqrt(1.-cosNDgen*cosNDgen)*cosND);
#
#    h_MH.Fill(MH)
#    h_DcosH.Fill(DcosH)
#
#tc=R.TCanvas()
#tc.Divide(2,1)
#tc.cd(1); h_MH.Draw()
#tc.cd(2); h_DcosH.Draw()
#tc.Draw()
#print("Hit return to exit")
#sys.stdin.readline()
#
