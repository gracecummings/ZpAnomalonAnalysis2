#This willl run all the myPlotTreeMaker for a set of initial conditions
import argparse
import subprocess

parser = argparse.ArgumentParser()
if __name__=='__main__':
    parser.add_argument("-wp","--btagWP",type=float,default=0.6,help = "doulbeB tagger working point (default M1)")
    parser.add_argument("-z","--zPtCut",type=float,default = 100,help = "pT cut on Z")
    parser.add_argument("-mt2","--mt2",type=float,default = 200,help = "guess for mt2 mass")
    args = parser.parse_args()

    zptcut   = args.zPtCut
    btagWP   = args.btagWP
    mt2guess = args.mt2

    pathlist = ['ZpAnomalonHZ_UFO-Zp2000-ND175-NS1_v2_ntuple_RA2AnalysisTree.root','ZpAnomalonHZ_UFO-Zp2000-ND300-NS1_v2_94X_mc2017_realistic_v3_RA2AnalysisTree.root','ZpAnomalonHZ_UFO-Zp2000-ND500-NS200_v2_94X_mc2017_realistic_v3_RA2AnalysisTree.root','ZpAnomalonHZ_UFO-Zp2000-ND800-NS200_v2_94X_mc2017_realistic_v3_RA2AnalysisTree.root']

    for path in pathlist:
        #isSig = False
        #if "ZpAnomalon" in path:
        #    isSig = True
        subprocess.call(["python","myPlotZpAnomalonHZ_TreeMaker.py","-f",path,"-z",str(zptcut),"-wp",str(btagWP),"-mt2",str(mt2guess),"-s","True"])
