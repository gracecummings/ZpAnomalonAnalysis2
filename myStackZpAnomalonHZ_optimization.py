import argparse
import ROOT
import glob
import os
import ConfigParser
import numpy as np
from datetime import date
from ROOT import kOrange, kViolet, kCyan, kGreen, kPink, kAzure, kMagenta, kBlue
from math import sqrt

def findScale(prodnum,lumi,xsec):
    expecnum = xsec*lumi
    scalefac = expecnum/prodnum
    return scalefac

def nameFall17(histFile):
    s1 = histFile.split("Fall17.")[1]
    s2 = s1.split("_TuneCP5")[0]
    return s2

def nameSignal(histFile):
    s1 = histFile.split("ZpAnomalonHZ_UFO-")[1]
    s2 = s1.split("_v2")[0]
    return s2

def massZpsignal(nameSig):#unused
    s1 = nameSig.split("Zp")[1]
    s2 = s1.split("-")[0]
    return int(s2)

def massNDsignalFile(histFile):
    s1 = histFile.split("ZpAnomalonHZ_UFO-")[1]
    s2 = s1.split("_v2")[0]
    s3 = s2.split("ND")[1]
    s4 = s3.split("-")[0]
    return int(s4)

def massNDsignal(nameSig):#unused
    s1 = nameSig.split("ND")[1]
    s2 = s1.split("-")[0]
    return int(s2)

def massPoints(nameSig):
    s1  = nameSig.split("-")
    mzp = int(s1[0].split("Zp")[1])
    mnd = int(s1[1].split("ND")[1])
    mns = int(s1[2].split("NS")[1])
    return mzp,mnd,mns

def orderFall17DY(histFile):
    s1 = histFile.split("to")[0]
    s2 = s1.split("HT-")[1]
    return int(s2)

def orderFall17TT(histFile):
    s1 = histFile.split("hists_")[1]
    s2 = s1.split("Events")[0]
    return int(s2)

if __name__=='__main__':
    #build module objects
    parser = argparse.ArgumentParser()
    config = ConfigParser.RawConfigParser()

    #Define parser imputs
    parser.add_argument("-L","--lumi", type=float,default = 137, help = "integrated luminosity for scale in fb^-1")
    parser.add_argument("-x","--xsec", type=float,help = "desired siganl cross section in fb")
    parser.add_argument("-p","--plot", type=str,help = "desired plot name to make the optimization for")

    #Set module options 
    args = parser.parse_args()
    config.optionxform = str

    #Get command line parameters
    lumi = args.lumi
    sig_xsec = args.xsec
    released_plot = args.plot

    #Files to stack
    DYJetsToLL = glob.glob('histsBkg_Commitb1a1547/Fall17.DYJetsToLL_M-50_HT**')#Add more dynamics here
    TT         = glob.glob('histsBkg_Commitb1a1547/Fall17.TTT*')#Add more dynamics here)
    #WZTo2L2Q   = glob.glob()
    #ZZTo2L2Q   = glob.glob()
    bkgfiles   = [DYJetsToLL,TT]#,WZ,ZZ]
    bkgnames   = ["DYJetsToLL","TT","WZTo2L2Q","ZZTo2L2Q"]
    sigfiles   = glob.glob('histsSig_Commitb1a1547_Zpt100DoubleBDisc0/ZpAnomalonHZ_UFO-*')

    sigfiles.sort()
    
    #Prep signals
    sig_colors  = [kOrange,kOrange-3,kCyan,kCyan-6,kGreen,kGreen-6,kPink+7,kPink+4,kViolet+4,kMagenta-2,kMagenta+3]
    sig_info    = []
    for s,sig in enumerate(sigfiles):
        sig_dict = {}
        sig_dict["tfile"] = ROOT.TFile(sig)
        sig_samplesize    = sig_dict["tfile"].Get('hnevents').GetBinContent(1)
        sig_dict["scale"] = findScale(float(sig_samplesize),sig_xsec,lumi)
        sig_dict["color"] = sig_colors[s]
        sig_dict["name"]  = nameSignal(sig)
        mzp,mnd,mns       = massPoints(sig_dict["name"])
        sig_dict["mzp"]   = mzp
        sig_dict["mnd"]   = mnd
        sig_dict["mns"]   = mns
        sig_info.append(sig_dict)

    #Sort Signals by NS mass, then by ND mass
    sig_info = sorted(sig_info,key = lambda sig: (sig["mns"],sig["mnd"]))

    #Prep backgrounds
    fp = open('xsects_2017.ini')
    config.readfp(fp)
    bkg_colors = [kAzure-4,kViolet,kAzure-6,kViolet+8,kBlue,kViolet-5,kBlue-8,kViolet+6]
    bkg_info   = []
    #Loop through the different bkg processes
    for b,bkg in enumerate(bkgfiles):
        bkg_binsum   = {}
        bkg_binlist  = []
        bkg_channel  = bkgnames[b]
        bkg_expyield = 0
        # bkg xs from .ini file
        bkgbin_xs_pairs = config.items(bkg_channel)
        if bkg_channel == "DYJetsToLL":
            #orders smallest HT to largest
            bkg.sort(key = orderFall17DY)
        elif bkg_channel == "TT":
            #orders smallest # events (xs) to largest
            bkg.sort(key = orderFall17TT)
        #loop through each process bin or categrory
        for s,bkgbin in enumerate(bkg):
            bkgbin_dict = {}
            bkgbin_dict["binname"] = bkgbin_xs_pairs[s][0]
            bkgbin_dict["tfile"]   = ROOT.TFile(bkgbin)
            bkgbin_sampsize        = bkgbin_dict["tfile"].Get('hnevents').GetBinContent(1)
            bkgbin_xs              = float(bkgbin_xs_pairs[s][1].split()[0])*1000#Into Femtobarns
            bkgbin_dict["scale"]   = findScale(float(bkgbin_sampsize),bkgbin_xs,lumi)
            bkgbin_dict["color"]   = bkg_colors[b]
            #get the number of passing events
            bkgbin_yield           = bkgbin_dict["tfile"].Get('hzreco_pt').GetEntries()
            bkg_expyield          += bkgbin_yield*bkgbin_dict["scale"]
            bkg_binlist.append(bkgbin_dict)
            bkg_binsum["expyield"] = bkg_expyield

        bkg_binsum["binlist"] = bkg_binlist
        bkg_binsum["name"]    = bkg_channel
        bkg_info.append(bkg_binsum)

    #Sort the backgrounds from smallest yields to largest
    bkg_info = sorted(bkg_info, key = lambda bkg:bkg["expyield"])

    #Make the stacked plot
    hname = released_plot
    leg = ROOT.TLegend(0.45,0.55,0.90,0.88)
    hsbkg = ROOT.THStack('hsbkg','')
    for bkg in bkg_info:
        for b,bkgbin in enumerate(bkg["binlist"]):
            hbkg = bkgbin["tfile"].Get(hname)
            hbkg.SetStats(0)
            hbkg.Scale(bkgbin["scale"])
            hbkg.SetFillColor(bkgbin["color"])
            hbkg.SetMaximum(10000000)
            hbkg.SetMinimum(0.1)
            hsbkg.Add(hbkg)
            #hsbkg.Draw("HIST")
            hsbkg.SetMaximum(10000000)
            hsbkg.SetMinimum(0.1)
            if b == len(bkg["binlist"])-1:
                leg.AddEntry(hbkg,bkg["name"],"f")

    #Make a multigraph
    mg = ROOT.TMultiGraph()
                
    #Prep the pads
    tc = ROOT.TCanvas("tc",hname,600,800)
    p1 = ROOT.TPad("p1","stack_"+hname,0,0.4,1.0,1.0)
    #tc.SetLogy()
    p1.SetLogy()
    #p1.SetBottomMargin(0)
    p1.SetLeftMargin(0.15)
    p1.SetRightMargin(0.05)
    p2 = ROOT.TPad("p2","signif_"+hname,0,0.0,1.0,0.4)
    #p2.SetTopMargin(0)
    p2.SetRightMargin(.05)
    p2.SetLeftMargin(0.15)
    p2.SetBottomMargin(0.2)

    #Prepare first pad for stack
    p1.Draw()
    p1.cd()

    #Draw the stack
    hsbkg.Draw("HIST")
    hsbkg.GetXaxis().SetTitle("bDiscriminatorCSV")
    hsbkg.GetXaxis().SetTitleSize(0.05)
    hsbkg.GetYaxis().SetTitle("Events/0.02 discrim val")
    hsbkg.GetYaxis().SetTitleSize(0.05)
    tc.Modified()
    
    #Add the signal plots
    for p,masspoint in enumerate(sig_info):
        #print "def saw ",masspoint["name"]
        hsig = masspoint["tfile"].Get(hname)
        hsig.SetStats(0)
        hsig.Scale(masspoint["scale"])
        hsig.SetLineColor(masspoint["color"])
        hsig.SetMaximum(10000000)
        hsig.SetMinimum(0.1)
        hsig.Draw("HISTSAME")
        leg.AddEntry(hsig,masspoint["name"]+" "+str(sig_xsec/1000)+" pb","l")
        
        #Now the significance calculation
        hsum = hsbkg.GetStack().Last()
        cutlist = np.zeros(hsum.GetNbinsX())
        signiflist = np.zeros(hsum.GetNbinsX())

        for ibin in range(hsum.GetNbinsX()):
            theocut = hsum.GetBinLowEdge(ibin)
            bkg     = 0
            sig     = 0
            for b in range(ibin,hsum.GetNbinsX()):
                bkg += hsum.GetBinContent(b)
                sig += hsig.GetBinContent(b)

            signif           = sig/sqrt(bkg)
            signiflist[ibin] = signif
            cutlist[ibin]    = theocut

        #remove underflow bin
        signiflist = np.delete(signiflist,0)
        cutlist    = np.delete(cutlist,0)

        #Build the graphs
        tg = ROOT.TGraph(hsum.GetNbinsX()-1,cutlist,signiflist)
        tg.SetTitle("")
        tg.SetLineWidth(2)
        tg.SetLineColor(masspoint["color"])
        mg.Add(tg)

        #Make the second pad with the significance plot
        tc.cd()
        p2.Draw()
        p2.cd()
        mg.Draw("AL")
        #Now, the beauty aspects
        mg.SetTitle("")
        #x axis
        mg.GetXaxis().SetTitle("cut value")
        mg.GetXaxis().SetTitleSize(0.07)
        mg.GetXaxis().SetLabelSize(0.05)
        mg.GetXaxis().SetLimits(0,1)
        #y axis
        mg.GetYaxis().SetTitle("S/#sqrt{B} a.u.")
        mg.GetYaxis().SetTitleSize(0.07)
        mg.GetYaxis().SetTitleOffset(.7)
        mg.GetYaxis().SetLabelSize(0.05)
        mg.SetMinimum(0)
        mg.SetMaximum(160)
        
        #Go back to previous pad so next kinematic plots draw
        tc.cd()
        p1.cd()

    #Draw the legent with everything added
    leg.SetBorderSize(0)
    leg.Draw()

    #Save the plot
    savdir = str(date.today())
    if not os.path.exists("opt_plots/"+savdir):
        os.makedirs("opt_plots/"+savdir)
    pngname = "opt_plots/"+savdir+"/"+hname+"_optimization.png" 
    tc.SaveAs(pngname)
