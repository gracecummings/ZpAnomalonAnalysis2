#This is a definition file of functions I (GEC) use all the time
from datetime import date
import ROOT
import os
import glob
import ConfigParser

def directorySaveStr(custom_name,sample_name,nevents,is_hist_bool):#not currently working
    dir_name    = "skims_ZpAnomalon/"
    outfdefault = sample_name+"_skims_ZpAnomalon"
    if is_hist_bool:
        dir_name = "analysis_output_ZpAnomalon/"
        outfdefault = sample_name+"_hists_ZpAnomalon"
    if not os.path.exists(dir_name+str(date.today())+"/"):
        os.makedirs(dir_name+str(date.today())+"/")
    if custom_name:
        outname = custom_name+"_"+str(nevents)+"Events.root"
        output  = dir_name+str(date.today())+"/"+outname
    else:
        outname = outfdefault+"_"+str(nevents)+"Events.root"
        output  = dir_name+str(date.today())+"/"+outname

    return output

def orderFall17DY(histFile):
    s1 = histFile.split("to")[0]
    s2 = s1.split("HT-")[1]
    return int(s2)       

def orderFall17TT(histFile):
    s1 = histFile.split("Events")[0]
    s2 = s1.split("_")[-1]
    return int(s2)

def massPoints(nameSig):
    s1  = nameSig.split("-")
    mzp = int(s1[1].split("Zp")[1])
    mnd = int(s1[2].split("ND")[1])
    mns = int(s1[3].split("NS")[1])
    return mzp,mnd,mns

def nameSignal(histFile):
    s1 = histFile.split("ZpAnomalonHZ_")[1]
    s2 = s1.split("_v2")[0]
    return s2

def findScale(prodnum,lumi,xsec):
    expecnum = xsec*lumi
    scalefac = expecnum/prodnum
    return  scalefac

def colsFromPalette(samplist,palname):
    collist = []
    ROOT.gStyle.SetPalette(palname)
    cols = ROOT.TColor.GetPalette()
    colsnum = cols.GetSize()
    for i in range(len(samplist)):
        collist.append(cols.At(0+i*colsnum/len(samplist)))
    return collist

def gatherBkg(bkg_dir):
    DYJetsToLL = glob.glob(str(bkg_dir)+'/Fall17.DYJetsToLL_M-50_HT*')
    TT         = glob.glob(str(bkg_dir)+'/Fall17.TTT*')                                         
    WZTo2L2Q   = glob.glob(str(bkg_dir)+'/Fall17.WZTo2L2Q*')                                    
    ZZTo2L2Q   = glob.glob(str(bkg_dir)+'/Fall17.ZZTo2L2Q*')                                    
    bkgfiles   = [DYJetsToLL,TT,WZTo2L2Q,ZZTo2L2Q]
    return bkgfiles

def prepSig(sigfiles,sig_colors,sig_xsec,lumi):
    sig_info = []
    for s,sig in enumerate(sigfiles):
        sig_dict = {}                                                                                   
        sig_dict["tfile"] = ROOT.TFile(sig)                                                             
        sig_samplesize    = sig_dict["tfile"].Get('hnevents').GetBinContent(1)                          
        sig_dict["scale"] = findScale(float(sig_samplesize),sig_xsec,lumi)                    
        sig_dict["name"]  = nameSignal(sig)                                                   
        mzp,mnd,mns       = massPoints(sig_dict["name"])                                      
        sig_dict["mzp"]   = mzp                                                                         
        sig_dict["mnd"]   = mnd                                                                         
        sig_dict["mns"]   = mns                                                                         
        sig_info.append(sig_dict)                                                                       
                                                                                                        
    #Sort Signals by ND mass, then by Zp mass                                                           
    sig_info = sorted(sig_info,key = lambda sig: (sig["mnd"],sig["mzp"],sig["mns"]))                    
    for s,sig in enumerate(sig_info):                                                                   
        sig["color"] = sig_colors[s]

    return sig_info

def prepBkg(bkgfiles,bkgnames,bkg_colors,ini_file,lumi):
    config = ConfigParser.RawConfigParser()
    config.optionxform = str
    fp = open(ini_file)
    config.readfp(fp)
    bkg_info = []
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
            bkgbin_xs              = float(bkgbin_xs_pairs[s][1].split()[0])*1000#Into Femtobarn
            bkgbin_dict["scale"]   = findScale(float(bkgbin_sampsize),bkgbin_xs,lumi)
            bkgbin_dict["color"]   = bkg_colors[b]
            #get the number of passing events
            bkgbin_yield           = bkgbin_dict["tfile"].Get('hnevents_pMET').GetBinContent(1)
            bkg_expyield          += bkgbin_yield*bkgbin_dict["scale"]
            bkg_binlist.append(bkgbin_dict)
            bkg_binsum["expyield"] = bkg_expyield

        bkg_binsum["binlist"] = bkg_binlist
        bkg_binsum["name"]    = bkg_channel
        bkg_info.append(bkg_binsum)

    #Sort the backgrounds from the smallest yields to largest        
    bkg_info = sorted(bkg_info, key = lambda bkg:bkg["expyield"])

    return bkg_info

def stackBkg(bkg_info,hist_to_stack,hsbkg,legend,stack_max,stack_min):
    for bkg in bkg_info:                                                                                
        for b,bkgbin in enumerate(bkg["binlist"]):                                                      
            hbkg = bkgbin["tfile"].Get(hist_to_stack)
            hbkg.SetStats(0)                                                                            
            hbkg.Scale(bkgbin["scale"])                                                                 
            hbkg.SetFillColor(bkgbin["color"])                                                          
            hbkg.SetLineColor(bkgbin["color"])                                                          
            hbkg.SetMaximum(stack_max)
            hbkg.SetMinimum(stack_min)
            hsbkg.Add(hbkg)                                                                             
            hsbkg.Draw("HIST")                                                                          
            hsbkg.SetMaximum(stack_max)
            hsbkg.SetMinimum(stack_min)
            if b == len(bkg["binlist"])-1:                                                              
                legend.AddEntry(hbkg,bkg["name"],"f")


    
