#Author: Grace Cummings
#Date: November 13th, 2019
#Purpose: Script to generate jdl files for condor submissions of the skimmer script
#Notes: Based on scripts by B. Tannenwald https://github.com/neu-physics/BsToMuMuAnalysis/blob/master/submitSampleToCondor.py and J. Hakala https://gitlab.cern.ch/johakala/nanolyzer/blob/condor/generateJobs.py


import os
import sys
import argparse
from datetime import date

parser = argparse.ArgumentParser()
parser.add_argument("-s","--sampleTXTFile",help=".txt file with the ntuple names you want skimmed")
#parser.add_argument("-o","--outPath",help="output directory path ending with /")
#parser.add_argument("-r","--release",help="CMSSW release")
parser.add_argument("-e","--eosDir",help="folder in gcumming user directory with ntuples")
parser.add_argument("-d","--prodDate",help="date when ntuples were made exp 'Nov12'")
args = parser.parse_args()

#Check that arguments were given
#if (not (len(vars(args)) != 2)):
#    os.system('python submitTrimmerToCondor.py -h')
#    quit

#Check output directory
#if (args.outPath is None):
#    mainPath = '/uscms/home/gcumming/nobackup/work_2019_summer/ZpAnomalonHZ/'+str(args.release)+'/src/ZpAnomalonAnalysis/skims_ZpAnomalon/'+str(date.today())+'/'
#    if not os.path.exists(mainPath):
#        os.makedirs(mainPath)
#else:
#    if not os.path.exists(args.outPath):
#        os.makedirs(args.outPath)

#Check and make output dir in eos
eosDirName = "skims"+str(args.prodDate)

#Check input text file
if (args.sampleTXTFile is None):
    print "please specify path to text file with samples to be skimmed"
else:
    if (not os.path.exists(args.sampleTXTFile)):
        print "invalid sample text file"

#Make log directories
if not os.path.exists("condorTrimmerOutput/"+str(date.today())+"/"):
    os.makedirs("condorTrimmerOutput/"+str(date.today())+"/")

#Tar the work area
print "Creating tarball of work area"
tarballName = "condorTrimmer.tar.gz"
os.system("tar -h -cvf "+tarballName+" condorTrimmer")


#For each sample create a job
txtFile = open(args.sampleTXTFile,"r")
readIn  = txtFile.readlines()
for line in readIn:
    sampleName = line.split("\n")[0]
    samplePath = str(args.eosDir)+'/'+sampleName

    #Make the jdl for each sample
    jdlName = "trimmer_"+sampleName+"_"+str(date.today())+".jdl"
    os.system("touch {0}".format(jdlName))
    os.system("echo universe = vanilla >> {0}".format(jdlName))
    os.system("echo Should_Transfer_Files = YES >> {0}".format(jdlName))
    os.system("echo WhenToTransferOutput = ON_EXIT >> {0}".format(jdlName))
    os.system("echo Transfer_Input_Files = {0} >> {1}".format(tarballName,jdlName))
    #os.system("echo Output = condorTrimmerOutput/{0}/{1}_$(Cluster)_$(Process)_out.stdout >> {2}".format(str(date.today()),sampleName,jdlName))
    os.system("echo Output = condorTrimmerOutput/{0}/{1}_out.stdout >> {2}".format(str(date.today()),sampleName,jdlName))
    #os.system("echo Error = condorTrimmerOutput/{0}/{1}_$(Cluster)_$(Process)_err.stderr >> {2}".format(str(date.today()),sampleName,jdlName))
    os.system("echo Error = condorTrimmerOutput/{0}/{1}_err.stderr >> {2}".format(str(date.today()),sampleName,jdlName))
    #os.system("echo Log = condorTrimmerOutput/{0}/{1}_$(Cluster_$(Process)_log.log >> {2}".format(str(date.today()),sampleName,jdlName))
    os.system("echo Log = condorTrimmerOutput/{0}/{1}_log.log >> {2}".format(str(date.today()),sampleName,jdlName))
    os.system("echo Executable = trimmer.sh >> {0}".format(jdlName))
    os.system("echo Arguments = {0} {1} {2} >> {3}".format(samplePath,sampleName+"_"+str(args.prodDate),eosDirName,jdlName))
    os.system("echo Queue 1 >> {0}".format(jdlName))#Not sure about this one
    

    #submit the jobs
    #os.system("condor_submit {0}".format(jdlName))
