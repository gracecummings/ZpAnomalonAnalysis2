import ROOT
import argparse
import geco_base

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--inputSampleDirandName",type=str)
    parser.add_argument("-o","--outPutFile",type=str)
    args = parser.parse_args()

    #Get the files you want skimmed
    sampleToSkim  = args.inputSampleDirandName
    samplePath    = "root://cmseos.fnal.gov//store/user/gcumming/"+sampleToSkim+"*_RA2AnalysisTree.root/TreeMaker2/PreSelection"
    print "Skimming trees with path:"
    print "    ",samplePath

    #Make the TChain
    inChain = ROOT.TChain("PreSelection")
    inChain.Add(samplePath)
    eventsToSkim = inChain.GetEntries()
    print "you are going to skim {0} events".format(eventsToSkim)

    #Make the output file that holds the skimmed events
    outFileName = args.outPutFile
    outFile     = outFileName+"_skim_"+str(eventsToSkim)+"MiniAODEvents.root"#For condor
    #outFile     = geco_base.directorySaveStr(outFileName,sampleToSkim,eventsToSkim,False)

    #Compile the macro to do the skimming
    ROOT.gSystem.CompileMacro("TreeMakerTrimmer.C","g0ck")
    ROOT.gSystem.Load('TreeMakerTrimmer_C')
    trimmer = ROOT.TreeMakerTrimmer(inChain)
    trimmer.Loop(outFile)

    print "congrats, you have made a skim. Hope it is lean enough for you."
    
    
