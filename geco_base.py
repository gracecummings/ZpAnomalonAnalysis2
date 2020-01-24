#This is a definition file of functions I (GEC) use all the time
from datetime import date
import ROOT
import os

def directorySaveStr(custom_name,sample_name,nevents,is_hist_bool):
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


