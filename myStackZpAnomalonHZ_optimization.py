import argparse
import ROOT
import glob
import os
import geco_base
import numpy as np
from datetime import date
from ROOT import kOrange, kViolet, kCyan, kGreen, kPink, kAzure, kMagenta, kBlue, kBird
from math import sqrt

if __name__=='__main__':
    #build module objects
    parser = argparse.ArgumentParser()

    #Define parser imputs
    parser.add_argument("-L","--lumi", type=float,default = 137, help = "integrated luminosity for scale in fb^-1")
    parser.add_argument("-x","--xsec", type=float,help = "desired siganl cross section in fb")
    parser.add_argument("-p","--plot", type=str,help = "desired plot name to make the optimization for")
    parser.add_argument("-mzp","--masszp",type=int)
    parser.add_argument("-mnd","--massnd",type=int)
    parser.add_argument("-mns","--massns",type=int)
    args = parser.parse_args()

    #Get command line parameters
    lumi = args.lumi
    sig_xsec = args.xsec
    released_plot = args.plot
    masszp = args.masszp
    massnd = args.massnd
    massns = args.massns
    
    #Gather Samples
    bkgfiles = geco_base.gatherBkg('histsBkgCommitf27c357')
    bkgnames = ["DYJetsToLL","TT","WZTo2L2Q","ZZTo2L2Q"]
    if massns:
        sigfiles = glob.glob('histsSigCommitf27c357/*NS'+str(massns)+'*')
    else:
        sigfiles = glob.glob('histsSigCommitf27c357/ZpAnomalonHZ_UFO-Zp*')

    #Prep signals
    sig_colors = geco_base.colsFromPalette(sigfiles,ROOT.kCMYK)
    sig_info   = geco_base.prepSig(sigfiles,sig_colors,sig_xsec,lumi)

    #Prep backgrounds
    bkg_colors = geco_base.colsFromPalette(bkgnames,ROOT.kDeepSea)
    bkg_info   = geco_base.prepBkg(bkgfiles,bkgnames,bkg_colors,'xsects_2017.ini',lumi)

    #Make the stacked plot
    hname = released_plot
    leg = ROOT.TLegend(0.45,0.55,0.90,0.88)
    hsbkg = ROOT.THStack('hsbkg','')
    geco_base.stackBkg(bkg_info,released_plot,hsbkg,leg,10000000,0.1)

    #Make a multigraph
    mg = ROOT.TMultiGraph()
                
    #Prep the pads
    tc = ROOT.TCanvas("tc",hname,600,800)
    p1 = ROOT.TPad("p1","stack_"+hname,0,0.4,1.0,1.0)
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
    hsbkg.Draw("HIST")#add PFC for palette drawing
    hsbkg.GetXaxis().SetTitle("delta Phi Z and Higgs")
    hsbkg.GetXaxis().SetTitleSize(0.05)
    hsbkg.GetYaxis().SetTitle("Events")
    hsbkg.GetYaxis().SetTitleSize(0.05)
    tc.Modified()
    
    #Add the signal plots
    max_max = 0
    for p,masspoint in enumerate(sig_info):
        #print "def saw ",masspoint["name"]
        #if p == 1:
        #    break
        hsig = masspoint["tfile"].Get(hname)
        hsig.SetStats(0)
        hsig.Scale(masspoint["scale"])
        hsig.SetLineColor(masspoint["color"])
        hsig.SetLineWidth(2)
        hsig.SetMaximum(10000000)
        hsig.SetMinimum(0.1)
        hsig.Draw("HISTSAME")
        leg.AddEntry(hsig,"Zp"+str(masspoint["mzp"])+" ND"+str(masspoint["mnd"])+" NS"+str(masspoint["mns"])+" "+str(sig_xsec/1000)+" pb","l")
        
        #Now the significance calculation
        hsum = hsbkg.GetStack().Last()
        cutlist = np.zeros(hsum.GetNbinsX())
        signiflist = np.zeros(hsum.GetNbinsX())

        for ibin in range(hsum.GetNbinsX()):
            theocut = hsum.GetBinLowEdge(ibin)
            bkg_sig = 0
            sig     = 0
            for b in range(ibin,hsum.GetNbinsX()):
                bkg_sig += hsum.GetBinContent(b)+hsig.GetBinContent(b)
                sig     += hsig.GetBinContent(b)

            if bkg_sig == 0.0:
                signif = 0.0
            else:
                signif           = sig/sqrt(bkg_sig)
                signiflist[ibin] = signif
            cutlist[ibin]    = theocut

        #remove underflow bin
        signiflist = np.delete(signiflist,0)
        cutlist    = np.delete(cutlist,0)

        #Debug
        #print signiflist
        #print cutlist

        #Build the graphs
        tg = ROOT.TGraph(hsum.GetNbinsX()-1,cutlist,signiflist)
        tg.SetTitle("")
        tg.SetLineWidth(2)
        tg.SetLineColor(masspoint["color"])
        #tg.SetLineStyle(masspoint["style"])
        mg.Add(tg)

        #Make the second pad with the significance plot
        tc.cd()
        p2.Draw()
        p2.cd()
        mg.Draw("AL")
        #Now, the beauty aspects
        #print signiflist
        temp_max = np.amax(signiflist)
        if temp_max > max_max:
            max_max = temp_max
            
        mg.SetTitle("")
        #x axis
        mg.GetXaxis().SetTitle("cut value")
        mg.GetXaxis().SetTitleSize(0.07)
        mg.GetXaxis().SetLabelSize(0.05)
        mg.GetXaxis().SetLimits(cutlist[0],cutlist[-1]+hsum.GetBinWidth(1))
        #y axis
        mg.GetYaxis().SetTitle("S/#sqrt{B+S} a.u.")
        mg.GetYaxis().SetTitleSize(0.07)
        mg.GetYaxis().SetTitleOffset(.7)
        mg.GetYaxis().SetLabelSize(0.05)
        mg.SetMinimum(0)
        mg.SetMaximum(max_max+10)
        
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
    pngname = "opt_plots/"+savdir+"/"+hname+"_deepdoubleb_optimization.png" 
    tc.SaveAs(pngname)
