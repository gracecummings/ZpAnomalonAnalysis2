import argparse
import ROOT
import glob
import os
import ConfigParser
import geco_base
from datetime import date
from ROOT import kOrange, kViolet, kCyan, kGreen, kPink, kAzure, kMagenta, kBlue


def findScale(prodnum,lumi,xsec):
    expecnum = xsec*lumi
    scalefac = expecnum/prodnum
    return scalefac

def nameFall17(histFile):
    s1 = histFile.split("Fall17.")[1]
    s2 = s1.split("_TuneCP5")[0]
    return s2

def nameSignal(histFile):
    s1 = histFile.split("ZpAnomalonHZ_")[1]
    s2 = s1.split("_hists")[0]
    return s2

def massZpsignal(nameSig):#unused
    s1 = nameSig.split("Zp")[1]
    s2 = s1.split("-")[0]
    return int(s2)

def massNDsignal(nameSig):#unused
    s1 = nameSig.split("ND")[1]
    s2 = s1.split("-")[0]
    return int(s2)

def massPoints(nameSig):
    s1  = nameSig.split("-")
    mzp = int(s1[1].split("Zp")[1])
    mnd = int(s1[2].split("ND")[1])
    mns = int(s1[3].split("NS")[1])
    return mzp,mnd,mns

def orderFall17DY(histFile):
    s1 = histFile.split("to")[0]
    s2 = s1.split("HT-")[1]
    return int(s2)

def orderFall17TT(histFile):
    s1 = histFile.split("Events")[0]
    s2 = s1.split("_")[-1]
    return int(s2)

if __name__=='__main__':
    #build module objects
    parser = argparse.ArgumentParser()
    config = ConfigParser.RawConfigParser()

    #Define parser imputs
    parser.add_argument("-L","--lumi", type=float,default = 137, help = "integrated luminosity for scale in fb^-1")
    parser.add_argument("-x","--xsec", type=float,help = "desired siganl cross section in fb")

    #Set module options 
    args = parser.parse_args()
    config.optionxform = str

    #Get command line parameters
    lumi = args.lumi
    sig_xsec = args.xsec

    #Files to stack
    DYJetsToLL = glob.glob('histsBkgCommitf27c357/Fall17.DYJetsToLL_M-50_HT*')#Add more dynamics here
    TT         = glob.glob('histsBkgCommitf27c357/Fall17.TTT*')#Add more dynamics here)
    WZTo2L2Q   = glob.glob('histsBkgCommitf27c357/Fall17.WZTo2L2Q*')
    ZZTo2L2Q   = glob.glob('histsBkgCommitf27c357/Fall17.ZZTo2L2Q*')
    bkgfiles   = [DYJetsToLL,TT,WZTo2L2Q,ZZTo2L2Q]
    bkgnames   = ["DYJetsToLL","TT","WZTo2L2Q","ZZTo2L2Q"]
    sigfiles   = glob.glob('histsSigCommitf27c357/ZpAnomalonHZ_UFO-Zp*')
    #Prep signals
    #sig_colors  = [kOrange,kOrange-3,kCyan,kCyan-6,kGreen,kGreen-6,kPink+7,kPink+4,kViolet+4,kMagenta-2,kMagenta+3]
    sig_colors = geco_base.colsFromPalette(sigfiles,ROOT.kCMYK)
    sig_info    = []

    for s,sig in enumerate(sigfiles):
        sig_dict = {}
        sig_dict["tfile"] = ROOT.TFile(sig)
        sig_samplesize    = sig_dict["tfile"].Get('hnevents').GetBinContent(1)
        sig_dict["scale"] = findScale(float(sig_samplesize),sig_xsec,lumi)
        #sig_dict["color"] = sig_colors[s]
        sig_dict["name"]  = nameSignal(sig)
        mzp,mnd,mns       = massPoints(sig_dict["name"])
        sig_dict["mzp"]   = mzp
        sig_dict["mnd"]   = mnd
        sig_dict["mns"]   = mns
        sig_info.append(sig_dict)

    #Sort Signals
    sig_info = sorted(sig_info,key = lambda sig: (sig["mnd"],sig["mzp"],sig["mns"]))

    for s,sig in enumerate(sig_info):
        sig["color"] = sig_colors[s]

    #Prep backgrounds
    fp = open('xsects_2017.ini')
    config.readfp(fp)
    #bkg_colors = [kAzure-4,kViolet,kAzure-6,kViolet+8,kBlue,kViolet-5,kBlue-8,kViolet+6]
    bkg_colors = geco_base.colsFromPalette(bkgnames,ROOT.kLake)
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
            #debug
            #print nameFall17(bkgbin)
            #print "the number of events initially ran over ",bkgbin_sampsize
            #print bkgbin
            #print bkgbin_xs_pairs[s][0]
            #print bkgbin_xs_pairs[s][1]
            #print bkgbin_dict
            #print "the expected yield ",bkg_binsum["expyield"]

        bkg_binsum["binlist"] = bkg_binlist
        bkg_binsum["name"]    = bkg_channel
        bkg_info.append(bkg_binsum)

    #Sort the backgrounds from smallest yields to largest
    bkg_info = sorted(bkg_info, key = lambda bkg:bkg["expyield"])

    #Get list of included histograms
    keys = bkg_info[0]["binlist"][0]["tfile"].GetListOfKeys()

    #Make some plots
    for i,key in enumerate(keys):
        hname = key.GetName()                                                                      
        tc = ROOT.TCanvas("tc",hname,600,600)
        #tc.SetLogy()
        leg = ROOT.TLegend(0.45,0.55,0.90,0.88)
        hsbkg = ROOT.THStack('hsbkg','')
        for bkg in bkg_info:
            #print "************Making Histograms*****************"
            #print bkg
            #print "************ended relevant print**************"
            for b,bkgbin in enumerate(bkg["binlist"]):
                hbkg = bkgbin["tfile"].Get(hname)
                hbkg.SetStats(0)
                hbkg.Scale(bkgbin["scale"])
                hbkg.SetFillColor(bkgbin["color"])
                hbkg.SetLineColor(bkgbin["color"])
                hbkg.SetMaximum(500)
                #hbkg.SetMinimum(0.1)
                hsbkg.Add(hbkg)
                hsbkg.Draw("HIST")
                hsbkg.SetMaximum(500)
                #hsbkg.SetMinimum(0.1)
                if b == len(bkg["binlist"])-1:
                    leg.AddEntry(hbkg,bkg["name"],"f")

        for sig in sig_info:
            hsig = sig["tfile"].Get(hname)
            hsig.SetStats(0)
            hsig.Scale(sig["scale"])
            hsig.SetLineColor(sig["color"])
            hsig.SetLineWidth(2)
            hsig.SetMaximum(500)
            #hsig.SetMinimum(0.1)
            hsig.Draw("HISTSAME")
            leg.AddEntry(hsig,"Zp"+str(sig["mzp"])+" ND"+str(sig["mnd"])+" NS"+str(sig["mns"])+" "+str(sig_xsec/1000)+" pb","l")
                    
        ROOT.gStyle.SetLegendBorderSize(0)
        leg.Draw()

        savdir = str(date.today())
        if not os.path.exists("stacked_stuff/"+savdir):
            os.makedirs("stacked_stuff/"+savdir)
        pngname = "stacked_stuff/"+savdir+"/"+hname+".png"
        tc.SaveAs(pngname)
