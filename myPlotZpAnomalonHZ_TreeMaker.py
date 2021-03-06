from ROOT import *
from math import pi,sqrt,cos,sin
from datetime import date
import os
import sys
import glob
import argparse
import itertools
import geco_base as gb
import recursive_jigsaw_anomalon as rj

def make4Vector(vdict):
    v = TLorentzVector()
    v.SetPtEtaPhiM(vdict["pt"],vdict["eta"],vdict["phi"],vdict["m"])
    return v

def only4Vector(vdict):
    v = vdict["fvec"]
    return v

def hNameFunc(elem):
    hist_def = elem.split()
    hname = hist_def[0]
    
def deltaR(vec1,vec2):
    v1phi = vec1.Phi()
    v2phi = vec2.Phi()
    v1eta = vec1.Eta()
    v2eta = vec2.Eta()
    dR = sqrt((v2phi-v1phi)**2+(v2eta-v1eta)**2)
    return dR

gROOT.ProcessLine(".L lester_mt2_bisect.h")                                                                                                                    
MT2Class=asymm_mt2_lester_bisect()                                                                                                                             
MT2Class.disableCopyrightMessage()

#Parser
parser = argparse.ArgumentParser()

if __name__=='__main__':
    parser.add_argument("-f","--sample",help = "sample file")
    parser.add_argument("-o","--output",help = "output file name")
    parser.add_argument("-s","--isSig", type=bool,help="is this a signal sample?")
    parser.add_argument("-wp","--btagWP",type=float,default=0.6,help = "doulbeB tagger working point (default M1)")
    parser.add_argument("-z","--zPtCut",type=float,default = 100,help = "pT cut on Z")
    args = parser.parse_args()

    #Defined by command line options
    #mcdir     = args.signal
    mcfile    = args.sample
    outf      = args.output
    doubleBWP = args.btagWP
    zptcut    = args.zPtCut
    isSig     = args.isSig


    #Start the analysis
    inputlist = []
    if isSig:
        ch = TChain("TreeMaker2/PreSelection")#, just Preslection for bkg
        inputlist = glob.glob('sigSamplesCommitf27c357/'+mcfile+'*.root')
        #Get Mass points
        gzp,gennd,genns = gb.massPoints(mcfile)
    else:
        ch = TChain("PreSelection")
        inputlist = glob.glob('bkgSamplesCommitf27c357/'+mcfile+'*.root')
    print "Building the TChain"

    skimmed_events = 0
    for f in inputlist:
        ch.Add(f)
        tf = TFile.Open(f)
        if not isSig:
            ntuple_events = tf.Get("hnevents").GetBinContent(1)
            skimmed_events+=ntuple_events
       
    #open output
    #Makes File to save histograms to
    events = ch.GetEntries()
    print "The TChain has {0} events".format(events)
    samplename = mcfile.split(".root")[0]
    outfdefault = samplename+"_hists"
    if not os.path.exists("analysis_output_ZpAnomalon/"+str(date.today())+"/"):
        os.makedirs("analysis_output_ZpAnomalon/"+str(date.today())+"/")
    if outf:
        outname = outf+"_"+str(events)+"Events.root"
        output = TFile("analysis_output_ZpAnomalon/"+str(date.today())+"/"+outname,"RECREATE")
    else:
        outname = outfdefault+"_"+str(events)+"Events_Zpt"+str(zptcut)+"btag"+str(doubleBWP)+".root"
        output  = TFile("analysis_output_ZpAnomalon/"+str(date.today())+"/"+outname,"RECREATE")
    print "Created output file"

    #Import files that defines the histograms
    import leptophobic_zprime_hist_list_cfi as hist

    #TCanvas for troubleshooting
    #Histograms initialized in config file
    #tc = TCanvas("tc","canvas for immediate interest",1800,1350)
    #tc = TCanvas("tc","canvas for immediate interest",1350,1800)
    #tc1 = TCanvas("tc1"."canvas for less immediate interest",1350)
    
    #Put Counters Here
    events_passing   = 0#passing events
    events_process   = 0
    events_gfj       = 0#events with a passing fat jet
    events_goodZ     = 0#events with a passing Z
    accepted_fj      = 0#number of passing fat jets in total
    events_pMET      = 0#events passing MET cut
    accepted_unrecfj = 0
    accepted_recfj   = 0
    close_ghgZ       = 0
    notclose_ghgZ    = 0
    ishclose_ghgZ    = 0

    sdFile = TFile.Open("weights/puppiCorr_2017.root","READ")
    sd_corrGEN = sdFile.Get("puppiJECcorr_gen")
    sd_corrRECO_cen = sdFile.Get("puppiJECcorr_reco_0eta1v3")
    sd_corrRECO_for = sdFile.Get("puppiJECcorr_reco_1v3eta2v5")

    #Loop over all Events in TChain
    for i,event in enumerate(ch):
        events_process = i
        #if i == 500:
        #    break
        #This is a progresse counter
        if i % 5000 == 0:
            print "reading event "+str(i)
        
        #This will kill this at a reasonable place
        #if i == 1000000:
        #    break
        #Look at gen level
        #gnparts = len(ch.GenParticles)
        #ghiggs  = TLorentzVector()
        #gZ      = TLorentzVector()
        #gfv     = TLorentzVector
        #gmulist = []
        #zindex  = -999999
        #for j in range(gnparts):
        #    gfv       = ch.GenParticles[j]
        #    gpid      = ch.GenParticles_PdgId[j]
        #    gstat     = ch.GenParticles_Status[j]
        #    gmothrIdx = ch.GenParticles_ParentIdx[j]
        #    gmothrID  = ch.GenParticles_ParentId[j]
        #    if abs(gpid) == 25:
        #        ghiggs = gfv
        #    if abs(gpid) == 23:
        #        gZ = gfv
        #    if abs(gpid) == 13 and gmothrID == 23:
        #        gmulist.append(gfv)#

        #Gen particle studies
        #ghZdR            = lambda mu : deltaR(ghiggs,mu)
        #dRghiggsgmuons   = map(ghZdR,gmulist)
        #if isSig:
        #    dRghiggsclosegmu = min(dRghiggsgmuons)
        #    dRghiggsfargmu   = max(dRghiggsgmuons)
        #    if dRghiggsfargmu < 0.8 and dRghiggsclosegmu < 0.8:
        #        close_ghgZ += 1
        #    elif dRghiggsclosegmu < 0.8:
        #        ishclose_ghgZ += 1
        #    else:
        #        notclose_ghgZ += 1

        #dphi_ghiggs_gZ = abs(ghiggs.Phi() - gZ.Phi())
        #if dphi_ghiggs_gZ >= 3.14159:
        #    dphi_ghiggs_gZ = 2*3.14159 - dphi_ghiggs_gZ

        #Filling gen object only histograms
        #hist.hghiggsgZ_dphi.Fill(dphi_ghiggs_gZ)


    
        #Looks at TreeMaker selected muons for Z cand
        mutm_zcand_nparts = len(ch.SelectedMuons)
        for mutm in range(int(mutm_zcand_nparts)):
            mu_tm = ch.SelectedMuons[mutm]
            hist.hmutm_zcand_pt.Fill(mu_tm.Pt())
            
        #Looks at Full Sim Muons
        munparts   = ch.GetLeaf("NMuons").GetValue()
        mu1        = TLorentzVector()
        mu2        = TLorentzVector()
        mut        = TLorentzVector()
        mulist     = []
        for muon in range(int(munparts)):
            mudict     = {}
            mut        = ch.Muons[muon]
            mu_pt      = mut.Pt()
            mu_eta     = mut.Eta()
            mu_tightID = ch.Muons_tightID[muon]
            mu_q       = ch.Muons_charge[muon]
            if mu_pt > 20.0 and abs(mu_eta) < 2.4 and mu_tightID:
                mudict["fvec"] = mut
                mudict["q"]    = mu_q
                mulist.append(mudict)
        if len(mulist) > 1:
            dimulist    = list(itertools.combinations(mulist,2))
            gooddimuons = []
            for mumu in dimulist:
                mumuv = []
                if mumu[0]["q"] != mumu[1]["q"]:
                    mumuv = map(only4Vector,mumu)
                    if max(mumuv, key = lambda mu : mu.Pt()).Pt() > 60:
                        if (mumuv[0]+mumuv[1]).M() > 70 and (mumuv[0]+mumuv[1]).M() < 110:
                            gooddimuons.append(mumuv)
            if len(gooddimuons) != 0:
                zdiff           = lambda x : abs(91.187 - (x[0]+x[1]).M())
                zmdifflist      = map(zdiff,gooddimuons)
                minzmdiffIdx    = zmdifflist.index(min(zmdifflist))
                minzmdiffdimuon = gooddimuons[minzmdiffIdx]
                mu1 = max(minzmdiffdimuon, key = lambda x : x.Pt())
                mu2 = min(minzmdiffdimuon, key = lambda x : x.Pt())
                hist.hmu1_pt.Fill(mu1.Pt())
                hist.hmu2_pt.Fill(mu2.Pt())
                                
                #Looks at reconstructed Z
                dimuon = mu1 + mu2
                if dimuon.Pt() > zptcut:
                    events_goodZ += 1
                    hist.hmu_zcand_pt.Fill(mu1.Pt())
                    hist.hmu_zcand_pt.Fill(mu2.Pt())
                    #Looks at FullSim level Fat Jets
                    fnparts       = len(ch.JetsAK8)
                    freclusnparts = len(ch.JetsAK8Clean)
                    lfat          = TLorentzVector()
                    sfat          = TLorentzVector()
                    nextsfat      = TLorentzVector()
                    unclusfat     = TLorentzVector()
                    flist         = []
                    clist         = []
                    frecluslist   = []
                    funcluslist   = []
                    lfdict        = {}
                    sfdict        = {}
                    nextsfdict    = {}

                    #This is just to compare to reclusting for now
                    #if fnparts > 0:
                    #    for fat in range(int(fnparts)):
                    #        fdict             = {}
                    #        tf                = ch.JetsAK8[fat]
                    #        fat_SD            = ch.JetsAK8_softDropMass[fat]
                    #        fat_id            = ch.JetsAK8_ID[fat]
                    #        fat_DoubleB       = ch.JetsAK8_doubleBDiscriminator[fat]
                    #        fdict["fvec"]     = tf
                    #        fdict["softdrop"] = fat_SD
                    #        if tf.Pt() > 250 and abs(tf.Eta()) < 2.4 and fat_id and fat_SD > 50 and fat_DoubleB >= doubleBWP:
                    #            accepted_unrecfj += 1
                    #            hist.hfjet_unclus_pt.Fill(tf.Pt())
                    #            hist.hfjet_unclus_mass.Fill(tf.M())
                    #            hist.hfjet_unclus_SD.Fill(fat_SD)
                    #            funcluslist.append(fdict)
                    #    if funcluslist != []:
                    #        print "YES! unclustered!"
                    #        sfdict_unclus      = min(funcluslist, key = lambda fat : abs(125.0 - fat["softdrop"]))
                    #        unclusfat          = sfdict_unclus["fvec"]
                    #        fatdR              = lambda mu : deltaR(unclusfat,mu)
                    #        dRunclusfatmu      = map(fatdR,minzmdiffdimuon)
                    #        dRunclusfatclosemu = min(dRunclusfatmu)
                    #        dRunclusfatfarmu   = max(dRunclusfatmu)
                    #        hsfjet_unclus_pt.Fill(unclusfat.Pt())
                    #        hsfjet_unclus_mass.Fill(unclusfat.M())
                    #        hsfjet_unclus_SD.Fill(sfdict_unclus["softdrop"])
                    #        hsfatdimuon_unclus_dR.Fill(dRunclusfatclosemu)
                    #        if dRunclusfatclosemu < 0.8 and dRunclusfatfarmu < 0.8:
                    #            hist.hdRles8_both_unclus_pt.Fill(unclusfat.Pt())
                    #            hist.hdRles8_both_unclus_mass.Fill(unclusfat.M())
                    #            hist.hdRles8_both_unclus_SD.Fill(sfdict_unclus["softdrop"])
                    #            hist.hdRles8_both_unclus_fjmulti.Fill(len(funcluslist))
                    #            hist.hdRles8_both_ghiggs_pt.Fill(ghiggs.Pt())
                    #            hist.hdRles8_both_ghiggs_eta.Fill(ghiggs.Eta())
                    #        elif dRunclusfatclosemu < 0.8 and dRunclusfatfarmu >= 0.8:
                    #            hist.hdRles8_one_unclus_pt.Fill(unclusfat.Pt())
                    #            hist.hdRles8_one_ghiggs_pt.Fill(ghiggs.Pt())
                    #            hist.hdRles8_one_ghiggs_eta.Fill(ghiggs.Eta())
                    #            hist.hdRles8_one_unclus_mass.Fill(unclusfat.M())
                    #            hist.hdRles8_one_unclus_SD.Fill(sfdict_unclus["softdrop"])
                    #            hist.hdRles8_one_unclus_fjmulti.Fill(len(funcluslist))
                    #        else:
                    #            hist.hdRgr8_unclus_pt.Fill(unclusfat.Pt())
                    #            hist.hdRgr8_ghiggs_pt.Fill(ghiggs.Pt())
                    #            hist.hdRgr8_ghiggs_eta.Fill(ghiggs.Eta())
                    #            hist.hdRgr8_unclus_mass.Fill(unclusfat.M())
                    #            hist.hdRgr8_unclus_SD.Fill(sfdict_unclus["softdrop"])
                    #            hist.hdRgr8_unclus_fjmulti.Fill(len(funcluslist))
                                
                    #This is where I think the real stuff starts
                    if freclusnparts > 0:
                        #Look at missing pT
                        ptmiss     = ch.GetLeaf("METclean").GetValue()
                        ptmiss_phi = ch.GetLeaf("METPhiclean").GetValue()
                        
                        for fat in range(int(freclusnparts)):
                            fdict             = {}
                            tf                = ch.JetsAK8Clean[fat]#saves a four vector, need to see how this four vector is built
                            fat_SD            = ch.JetsAK8Clean_softDropMass[fat]
                            fat_id            = ch.JetsAK8Clean_ID[fat]
                            #fat_DoubleB       = ch.JetsAK8Clean_doubleBDiscriminator[fat]#bDiscriminatorCSV
                            fat_DoubleB       = ch.JetsAK8Clean_zhDiscriminatorDeepDecorrel[fat]#DeepAK8
                            #fat_DoubleB       = ch.JetsAK8Clean_hDiscriminatorDeep[fat]#DeepAK8
                            #fat_DoubleB       = ch.JetsAK8Clean_deepDoubleBDiscriminatorH[fat]
                            fat_SDMassCorr    = gb.getSoftDropCorrection(sd_corrGEN,sd_corrRECO_cen,sd_corrRECO_for,tf.Pt(),tf.Eta())
                            fdict["DoubleB"]  = fat_DoubleB
                            fdict["fvec"]     = tf
                            fdict["softdrop"] = fat_SD
                            fdict["corrSD"]   = fat_SD*fat_SDMassCorr
                            if tf.Pt() > 250 and abs(tf.Eta()) < 2.4 and fat_id and fdict["corrSD"] > 10 and fat_DoubleB >= doubleBWP:
                                accepted_recfj += 1
                                #frecluslist.append(fdict)
                                #if fat_SD > 105 and fat_SD < 145:
                                flist.append(fdict)
                                #else:
                                #    clist.append(fdict)
                                #hist.hfjet_reclus_pt.Fill(tf.Pt())
                                #hist.hfjet_reclus_mass.Fill(tf.M())
                                #hist.hfjet_reclus_SD.Fill(fat_SD)

                                #Filling Hists that apply to all fat jets
                                hist.hfjet_pt.Fill(tf.Pt())
                                hist.hfjet_mass.Fill(tf.M())
                                hist.hfjet_SD.Fill(fat_SD)
                                hist.hfjet_corrSD.Fill(fdict["corrSD"])

                            #This compares reclustered to unreclusted
                            #if funcluslist != []:
                            #    for jet in funcluslist:
                            #        hist.hfj_unreclus_pt.Fill(jet["fvec"].Pt())
                            #        hist.hfj_unreclus_mass.Fill(jet["fvec"].M())
                            #        hist.hfj_unreclus_SD.Fill(jet["softdrop"])
                    
                        if flist == []:# and clist == []:
                            continue
                        else:
                            accepted_fj += len(flist)            
                            events_gfj +=1
                            #sfdict = min(flist, key = lambda fat : abs(125.0 - fat["softdrop"]))
                            sfdict = min(flist, key = lambda fat : abs(125.0 - fat["corrSD"]))
                            lfdict = max(flist, key = lambda fat : fat["fvec"].Pt())
                            sfat   = sfdict["fvec"]
                            lfat   = lfdict["fvec"]
                             
                            #Compares selections with reclustering to unreclustered selections
                            #This should compare the ones that used to be close to the new ones
                            #Comments below can be used for new distribution
                            #sfatdR = lambda mu : deltaR(sfat,mu)
                            #dRunclusfatclosemu = min(map(sfatdR,minzmdiffdimuon))
                            #if dRunclusfatclosemu < 0.8 and dRunclusfatfarmu < 0.8:
                            #    hist.hdRles8_both_fjet_pt.Fill(sfat.Pt())
                            #    hist.hdRles8_both_fjet_mass.Fill(sfat.M())
                            #    hist.hdRles8_both_fjet_SD.Fill(sfdict["softdrop"])
                            #    hist.hdRles8_both_fjet_fjmulti.Fill(len(flist))
                            #elif dRunclusfatclosemu < 0.8 and dRunclusfatfarmu >= 0.8:
                            #    hist.hdRles8_one_fjet_pt.Fill(sfat.Pt())
                            #    hist.hdRles8_one_fjet_mass.Fill(sfat.M())
                            #    hist.hdRles8_one_fjet_SD.Fill(sfdict["softdrop"])
                            #    hist.hdRles8_one_fjet_fjmulti.Fill(len(flist))
                            #else:
                            #    hist.hdRgr8_fjet_pt.Fill(sfat.Pt())
                            #    hist.hdRgr8_fjet_mass.Fill(sfat.M())
                            #    hist.hdRgr8_fjet_SD.Fill(sfdict["softdrop"])
                            #    hist.hdRgr8_fjet_fjmulti.Fill(len(flist))
                                
                            if ptmiss > 50:
                                #events_passing += 1
                                events_pMET += 1
                                ptmiss_px = ptmiss*cos(ptmiss_phi)
                                ptmiss_py = ptmiss*sin(ptmiss_phi)
                                #Calculating Generator Level Observables
                                #dphi_ghsf = abs(ghiggs.Phi()-sfat.Phi())
                                #if dphi_ghsf >= 3.14159:
                                #    dphi_ghsf = 2*3.14159 - dphi_ghsf
                                #dphi_ghlf = abs(ghiggs.Phi()-lfat.Phi())
                                #if dphi_ghlf >= 3.14159:
                                #    dphi_ghlf = 2*3.14159 - dphi_ghlf
                                
                                #Getting the  built ZCandidates
                                znparts = len(ch.ZCandidates)
                                for z in range(int(znparts)):
                                    ztm = ch.ZCandidates[z]
                                    
                                #Calculating angular varibles, compound variables
                                dR_sfat_dimuon   = deltaR(sfat,dimuon)
                                dR_sfat_mu1      = deltaR(sfat,mu1)
                                dR_sfat_mu2      = deltaR(sfat,mu2)
                                dR_mu1_mu2       = deltaR(mu1,mu2)
                                deta_sfat_dimuon = abs(sfat.Eta()-dimuon.Eta())
                                dphi_sfat_dimuon = abs(sfat.Phi()-dimuon.Phi())
                                dphi_dimuon_ptmiss = abs(dimuon.Phi()-ptmiss_phi)
                                dphi_sfat_ptmiss   = abs(sfat.Phi()-ptmiss_phi)
                                if dphi_sfat_dimuon >= 3.14159:
                                    dphi_sfat_dimuon = 2*3.14159 - dphi_sfat_dimuon
                                if dphi_dimuon_ptmiss >= 3.14159:
                                    dphi_dimuon_ptmiss = 2*3.14159 - dphi_dimuon_ptmiss
                                if dphi_sfat_ptmiss >= 3.14159:
                                    dphi_sfat_ptmiss = 2*3.14159 - dphi_sfat_ptmiss
                                zh = dimuon+sfat

                                #Calculate Transverse Mass
                                zMET_mt = sqrt(2*dimuon.Pt()*ptmiss*(1-cos(dphi_dimuon_ptmiss)))
                                hMET_mt = sqrt(2*sfat.Pt()*ptmiss*(1-cos(dphi_sfat_ptmiss)))
                                
                                #Calculate Mt2
                                mt2200   = MT2Class.get_mT2(dimuon.M(),dimuon.Px(),dimuon.Py(),sfat.M(),sfat.Px(),sfat.Py(),ptmiss_px,ptmiss_py,200,200,0)
                                mt2SD200 = MT2Class.get_mT2(dimuon.M(),dimuon.Px(),dimuon.Py(),sfdict["softdrop"],sfat.Px(),sfat.Py(),ptmiss_px,ptmiss_py,200,200,0)
                                mt201   = MT2Class.get_mT2(dimuon.M(),dimuon.Px(),dimuon.Py(),sfat.M(),sfat.Px(),sfat.Py(),ptmiss_px,ptmiss_py,1,1,0)
                                mt2SD01 = MT2Class.get_mT2(dimuon.M(),dimuon.Px(),dimuon.Py(),sfdict["softdrop"],sfat.Px(),sfat.Py(),ptmiss_px,ptmiss_py,1,1,0)
                                


                                #Calculate Razor
                                z3p = dimuon.P()
                                h3p = sfat.P()
                                mr1 = sqrt((z3p+h3p)**2-(dimuon.Pz()+sfat.Pz())**2)
                                twicemr1 = 2*mr1
                                mrt = sqrt(0.5*(ptmiss*(dimuon.Pt()+sfat.Pt())-(ptmiss*sin(ptmiss_phi)*zh.Py()+ptmiss*cos(ptmiss_phi)*zh.Px())))
                                r1  = mrt/mr1
                                mr2 = sqrt(zh.Energy()**2-zh.Pz()**2)
                                r2  = mrt/mr2

                                #Calculate recursive jigsaw variables
                                jigsawframes = {}
                                rj.SetupRecoFrame(jigsawframes)
                                jigsawframes['LAB'].InitializeAnalysis()
                                jigsawframes['LAB'].ClearEvent()
                                ptmiss_3vec = TVector3(ptmiss_px,ptmiss_py,0.)
                                jigsawframes['INV'].SetLabFrameThreeVector(ptmiss_3vec)
                                jigsawframes['Z'].SetLabFrameFourVector(dimuon)
                                jigsawframes['h'].SetLabFrameFourVector(sfat)
                                jigsawframes['LAB'].AnalyzeEvent()
                                mZp = jigsawframes['Zp'].GetMass()
                                mND = jigsawframes['ND'].GetMass()
                                mNDbar = jigsawframes['NDbar'].GetMass()

                                if sfdict["corrSD"] > 70 and sfdict["corrSD"] < 150:
                                #if hMET_mt >= 400:
                                    events_passing += 1

                                    #Make good estimate plots
                                    if isSig:
                                        hist.hjignddiv.Fill(mND/gennd)
                                        hist.hjigzpdiv.Fill(mZp/gzp)
                                        hist.h2razdiv.Fill(twicemr1/gzp)
                                        hist.hmt2200div.Fill(mt2200/gennd)
                                        hist.hmt21div.Fill(mt201/gennd)
                                        hist.hzmtdiv.Fill(zMET_mt/gennd)
                                
                                    #Filling 1D histograms that cover selection based quantities 
                                    #hbtagfrac.Fill(len(flist)/fnparts)
                                    hist.hsfatdimuon_dR.Fill(dR_sfat_dimuon)
                                    hist.hsfatmu1_dR.Fill(dR_sfat_mu1)
                                    hist.hsfatmu2_dR.Fill(dR_sfat_mu2)
                                    hist.hmu1mu2_dR.Fill(dR_mu1_mu2)
                                    hist.hsfatdimuon_dphi.Fill(dphi_sfat_dimuon)
                                    hist.hsfatdimuon_deta.Fill(deta_sfat_dimuon)
                                    hist.hsfatMET_dphi.Fill(dphi_sfat_ptmiss)
                                    hist.hdimuonMET_dphi.Fill(dphi_dimuon_ptmiss)
                                    hist.hnfatpass.Fill(len(flist))
                                    hist.hsfjet_pt.Fill(sfat.Pt())
                                    hist.hlfjet_pt.Fill(lfat.Pt())
                                    hist.hsfjet_btag.Fill(sfdict["DoubleB"])
                                    hist.hsfjet_mass.Fill(sfat.M())
                                    hist.hlfjet_mass.Fill(lfat.M())
                                    hist.hsfjet_SD.Fill(sfdict["softdrop"])
                                    hist.hsfjet_corrSD.Fill(sfdict["corrSD"])
                                    hist.hlfjet_SD.Fill(lfdict["softdrop"])
                                    hist.hSDMassvpT.Fill(sfat.Pt(),sfdict["softdrop"])
                                    hist.hcorrSDMassvpT.Fill(sfat.Pt(),sfdict["corrSD"])
                                    #hist.hghlf_dphi.Fill(dphi_ghlf)
                                    #hist.hghsf_dphi.Fill(dphi_ghsf)
                                    hist.hzreco_pt.Fill(dimuon.Pt())
                                    hist.hztm_pt.Fill(ztm.Pt())
                                    hist.hzreco_mass.Fill(dimuon.M())
                                    hist.hztm_mass.Fill(ztm.M())
                                    hist.hMETClean.Fill(ptmiss)
                                    hist.hMETClean_phi.Fill(ptmiss_phi)
                                    hist.hht.Fill(ch.GetLeaf("HTclean").GetValue())#Do not know how this is calculated
                                    hist.hzh_mass.Fill(zh.M())
                                    hist.hzh_pt.Fill(zh.Pt())
                                    hist.hzMET_mt.Fill(zMET_mt)
                                    hist.hhMET_mt.Fill(hMET_mt)
                                    hist.hmt2200g.Fill(mt2200)
                                    hist.hmt2SD200g.Fill(mt2SD200)
                                    hist.hmt201g.Fill(mt201)
                                    hist.hmt2SD01g.Fill(mt2SD01)
                                    hist.hmr1.Fill(mr1)
                                    hist.hmr2.Fill(mr2)
                                    hist.hmrt.Fill(mrt)
                                    hist.hr1var.Fill(r1)
                                    hist.hr2var.Fill(r2)
                                    hist.h2timemr1.Fill(twicemr1)
                                    hist.hjigzp_mass.Fill(mZp)
                                    hist.hjignd_mass.Fill(mND)
                                    hist.hjigndbar_mass.Fill(mNDbar)

                                    #Filing 2D Histograms
                                    #hist.hghmvslfSD.Fill(lfdict["SD"],ghiggs.M())
                                    #hist.hghmvssfSD.Fill(sfdict["SD"],ghiggs.M())
                                    #hist.hgZphivsdimuphi.Fill(dimuon.Phi(),gZ.Phi())
                                    #hist.hghphivslfphi.Fill(lfat.Phi(),ghiggs.Phi())
                                    #hist.hghphivssfphi.Fill(sfat.Phi(),ghiggs.Phi())
                                    #hist.hlfphivssfphi.Fill(sfat.Phi(),lfat.Phi())

                                else:#control region

                                    #Make good estimate plots
                                    if isSig:
                                        hist.h_ctrl_jignddiv.Fill(mND/gennd)
                                        hist.h_ctrl_jigzpdiv.Fill(mZp/gzp)
                                        hist.h_ctrl_2razdiv.Fill(twicemr1/gzp)
                                        hist.h_ctrl_mt2200div.Fill(mt2200/gennd)
                                        hist.h_ctrl_mt21div.Fill(mt201/gennd)
                                        hist.h_ctrl_zmtdiv.Fill(zMET_mt/gennd)
                                
                                    #Filling 1D histograms that cover selection based quantiti
                                    hist.hsfatdimuon_ctrl_dR.Fill(dR_sfat_dimuon)
                                    hist.hsfatmu1_ctrl_dR.Fill(dR_sfat_mu1)
                                    hist.hsfatmu2_ctrl_dR.Fill(dR_sfat_mu2)
                                    hist.hmu1mu2_ctrl_dR.Fill(dR_mu1_mu2)
                                    hist.hsfatdimuon_ctrl_dphi.Fill(dphi_sfat_dimuon)
                                    hist.hsfatdimuon_ctrl_deta.Fill(deta_sfat_dimuon)
                                    hist.hsfatMET_ctrl_dphi.Fill(dphi_sfat_ptmiss)
                                    hist.hdimuonMET_ctrl_dphi.Fill(dphi_dimuon_ptmiss)
                                    hist.h_ctrl_nfatpass.Fill(len(flist))
                                    hist.hsfjet_ctrl_pt.Fill(sfat.Pt())
                                    hist.hlfjet_ctrl_pt.Fill(lfat.Pt())
                                    hist.hsfjet_ctrl_btag.Fill(sfdict["DoubleB"])
                                    hist.hsfjet_ctrl_mass.Fill(sfat.M())
                                    hist.hlfjet_ctrl_mass.Fill(lfat.M())
                                    hist.hsfjet_ctrl_SD.Fill(sfdict["softdrop"])
                                    hist.hsfjet_ctrl_corrSD.Fill(sfdict["corrSD"])
                                    hist.hlfjet_ctrl_SD.Fill(lfdict["softdrop"])
                                    #hist.hghlf_dphi.Fill(dphi_ghlf)
                                    #hist.hghsf_dphi.Fill(dphi_ghsf)
                                    hist.hzreco_ctrl_pt.Fill(dimuon.Pt())
                                    hist.hztm_ctrl_pt.Fill(ztm.Pt())
                                    hist.hzreco_ctrl_mass.Fill(dimuon.M())
                                    hist.hztm_ctrl_mass.Fill(ztm.M())
                                    hist.h_ctrl_METClean.Fill(ptmiss)
                                    hist.hMETClean_ctrl_phi.Fill(ptmiss_phi)
                                    hist.h_ctrl_ht.Fill(ch.GetLeaf("HTclean").GetValue())#Do not know how this is calculated
                                    hist.hzc_mass.Fill(zh.M())
                                    hist.hzc_pt.Fill(zh.Pt())
                                    hist.hzMET_ctrl_mt.Fill(zMET_mt)
                                    hist.hcMET_mt.Fill(hMET_mt)
                                    hist.h_ctrl_mt2200g.Fill(mt2200)
                                    hist.h_ctrl_mt2SD200g.Fill(mt2SD200)
                                    hist.h_ctrl_mt201g.Fill(mt201)
                                    hist.h_ctrl_mt2SD01g.Fill(mt2SD01)
                                    hist.h_ctrl_mr1.Fill(mr1)
                                    hist.h_ctrl_mr2.Fill(mr2)
                                    hist.h_ctrl_mrt.Fill(mrt)
                                    hist.h_ctrl_r1var.Fill(r1)
                                    hist.h_ctrl_r2var.Fill(r2)
                                    hist.h_ctrl_2timemr1.Fill(twicemr1)
                                    hist.hjigzp_ctrl_mass.Fill(mZp)
                                    hist.hjignd_ctrl_mass.Fill(mND)
                                    hist.hjigndbar_ctrl_mass.Fill(mNDbar)
                                
    #Fill event number hists
    if skimmed_events > 1:
        events_process = skimmed_events
    hist.hnevents.SetBinContent(1,events_process)
    hist.hnevents_passing.SetBinContent(1,events_passing)#has fat jet in window
    hist.hnevents_pMET.SetBinContent(1,events_pMET)
    hist.hnevents_psf.SetBinContent(1,events_gfj)#has a fat jet, might not be in mass window
    hist.hnevents_pZ.SetBinContent(1,events_goodZ)
    hist.hnfatpass.SetBinContent(1,accepted_fj)
    
    #Gen level event info
    if isSig:
        hist.hnevents_dRles8_ghgZ_bothmu.SetBinContent(1,close_ghgZ)
        hist.hnevents_dRg8_ghiggsgZ.SetBinContent(1,notclose_ghgZ)
        hist.hnevents_dRles8_ghgZ_onemu.SetBinContent(1,ishclose_ghgZ)

    #Set Colors for Stuff
    #hist.hztm_pt.SetLineColor(kRed)
    #hist.hztm_mass.SetLineColor(kRed)
    #hist.hlfjet_SD.SetLineColor(kRed)
    #hist.hsfjet_SD.SetLineColor(kBlue)
    #hist.hghlf_dphi.SetLineColor(kRed)
    #hist.hghsf_dphi.SetLineColor(kBlue)
    #hist.hbuiltjet_mass.SetLineColor(kRed)
    #hist.hmutm_zcand_pt.SetLineColor(kRed)
    #hist.hfj_unreclus_pt.SetLineColor(kRed)
    #hist.hfj_unreclus_mass.SetLineColor(kRed)
    #hist.hfj_unreclus_SD.SetLineColor(kRed)
    #hist.hdRgr8_unclus_pt.SetLineColor(kRed)
    #hist.hdRles8_one_unclus_pt.SetLineColor(kRed)
    #hist.hdRles8_both_unclus_pt.SetLineColor(kRed)
    #hist.hdRgr8_unclus_mass.SetLineColor(kRed)
    #hist.hdRles8_one_unclus_mass.SetLineColor(kRed)
    #hist.hdRles8_both_unclus_mass.SetLineColor(kRed)
    #hist.hdRgr8_unclus_SD.SetLineColor(kRed)
    #hist.hdRles8_one_unclus_SD.SetLineColor(kRed)
    #hist.hdRles8_both_unclus_SD.SetLineColor(kRed)
    #hist.hdRles8_both_unclus_fjmulti.SetLineColor(kRed)
    #hist.hdRles8_one_unclus_fjmulti.SetLineColor(kRed)
    #hist.hdRgr8_unclus_fjmulti.SetLineColor(kRed)
    #hist.hdRgr8_ghiggs_pt.SetLineColor(kGreen)
    #hist.hdRles8_both_ghiggs_pt.SetLineColor(kGreen)
    #hist.hdRles8_one_ghiggs_pt.SetLineColor(kGreen)
    #hist.hdRgr8_ghiggs_eta.SetLineColor(kGreen)
    #hist.hdRles8_both_ghiggs_eta.SetLineColor(kGreen)
    #hist.hdRles8_one_ghiggs_eta.SetLineColor(kGreen)

    #Create Stacks
    #hist.hsgr8_pt.Add(hdRgr8_unclus_pt)
    #hist.hsgr8_pt.Add(hdRgr8_fjet_pt)
    #hist.hsgr8_pt.Add(hdRgr8_ghiggs_pt)
    #hist.hsgr8_mass.Add(hdRgr8_unclus_mass)
    #hist.hsgr8_mass.Add(hdRgr8_fjet_mass)
    #hist.hsgr8_SD.Add(hdRgr8_unclus_SD)
    #hist.hsgr8_SD.Add(hdRgr8_fjet_SD)    
    #hist.hsles8_both_pt.Add(hdRles8_both_unclus_pt)
    #hist.hsles8_both_pt.Add(hdRles8_both_fjet_pt)
    #hist.hsles8_both_pt.Add(hdRles8_both_ghiggs_pt)
    #hist.hsles8_both_mass.Add(hdRles8_both_unclus_mass)
    #hist.hsles8_both_mass.Add(hdRles8_both_fjet_mass)
    #hist.hsles8_both_SD.Add(hdRles8_both_unclus_SD)
    #hist.hsles8_both_SD.Add(hdRles8_both_fjet_SD)
    #hist.hsles8_one_pt.Add(hdRles8_one_unclus_pt)
    #hist.hsles8_one_pt.Add(hdRles8_one_fjet_pt)
    #hist.hsles8_one_pt.Add(hdRles8_one_ghiggs_pt)
    #hist.hsles8_one_mass.Add(hdRles8_one_unclus_mass)
    #hist.hsles8_one_mass.Add(hdRles8_one_fjet_mass)
    #hist.hsles8_one_SD.Add(hdRles8_one_unclus_SD)
    #hist.hsles8_one_SD.Add(hdRles8_one_fjet_SD)
    #hist.hsles8_both_fjmulti.Add(hdRles8_both_unclus_fjmulti)
    #hist.hsles8_both_fjmulti.Add(hdRles8_both_fjet_fjmulti)
    #hist.hsles8_one_fjmulti.Add(hdRles8_one_unclus_fjmulti)
    #hist.hsles8_one_fjmulti.Add(hdRles8_one_fjet_fjmulti)
    #hist.hsgr8_fjmulti.Add(hdRgr8_unclus_fjmulti)
    #hist.hsgr8_fjmulti.Add(hdRgr8_fjet_fjmulti)
    
    #tc.Divide(3,4)
    #Column 1
    #tc.cd(1)
    #hist.hsgr8_pt.Draw("nostack")
    #tc.cd(4)
    #gPad.SetLogy()
    #hist.hsgr8_fjmulti.Draw("nostack")
    #tc.cd(7)
    #hist.hsgr8_SD.Draw("nostack")
    #tc.cd(10)
    #hist.hdRgr8_ghiggs_eta.Draw()
    #Column 2
    #tc.cd(2)
    #hist.hsles8_both_pt.Draw("nostack")
    #tc.cd(5)
    #gPad.SetLogy()
    #hist.hsles8_both_fjmulti.Draw("nostack")
    #tc.cd(8)
    #hist.hsles8_both_SD.Draw("nostack")
    #tc.cd(11)
    #hist.hdRles8_both_ghiggs_eta.Draw()
    #Column 3
    #tc.cd(3)
    #hist.hsles8_one_pt.Draw("nostack")
    #tc.cd(6)
    #gPad.SetLogy()
    #hist.hsles8_one_fjmulti.Draw("nostack")
    #tc.cd(9)
    #hist.hsles8_one_SD.Draw("nostack")
    #tc.cd(12)
    #hist.hdRles8_one_ghiggs_eta.Draw()
    #Column 4#old canvas
    #tc.cd(4)
    #hist.hsfatdimuon_dR.Draw()
    #tc.cd(8)
    #hist.hsfatdimuon_dphi.Draw()
    #tc.cd(12)
    #hist.hsfatdimuon_deta.Draw()
    #tc.Update()

    print "this is the total number of events:                    ",events
    print "this is the total number of passing events:            ",events_passing
    print "this is the total number of events with good  fatjets: ",events_gfj
    print "this is the total number of events with good Zs:       ",events_goodZ
    if skimmed_events > 1:
        print "this is the total number of events preskim:            ",skimmed_events
    #print "this is the total number of good, unreclusted fat jets: ",accepted_unrecfj
    #print "this is the total number of good, reclusted fat jets: ",accepted_recfj
    #print "this is the total number of good, selected fat jets: ",accepted_fj
    #print "number of gen higgs with both gen muons in cone:   ",close_ghgZ
    #print "number of gen higgs with one gen muon in cone:     ",ishclose_ghgZ
    #print "number of gen higgs with neither gen muon in cone: ",notclose_ghgZ 

    #This should save the histograms
    output.Write()
    output.Close()

    sdFile.Close()

    print "Wrote and saved generated histograms in ",outname
    #print "press enter to continue"
    #Keep the canvas open
    #sys.stdin.readline()
    
                    
                    
