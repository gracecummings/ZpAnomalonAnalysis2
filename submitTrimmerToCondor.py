#Author: Grace Cummings
#Date: November 13th, 2019
#Purpose: Script to generate jdl files for condor submissions of the skimmer script
#Notes: Based on scripts by B. Tannenwald https://github.com/neu-physics/BsToMuMuAnalysis/blob/master/submitSampleToCondor.py and J. Hakala https://gitlab.cern.ch/johakala/nanolyzer/blob/condor/generateJobs.py


import os
import sys
import argparse
from datetime import date
from itertools import islice

parser = argparse.ArgumentParser()
parser.add_argument("-s","--sampleTXTFile",help=".txt file with the ntuple names you want skimmed")
#parser.add_argument("-o","--outPath",help="output directory path ending with /")
#parser.add_argument("-r","--release",help="CMSSW release")
parser.add_argument("-e","--eosDirTuples",help="folder in gcumming user directory with ntuples")
parser.add_argument("-d","--prodDate",help="date when ntuples were made exp 'Nov12'")
parser.add_argument("-c","--chunksize",type=int,help="how many files you want to run over per job")
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
#THIS CURRENTLY DOES NOT VERIFY
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


#Create jobs
txtFile = open(args.sampleTXTFile,"r")
readIn  = txtFile.readlines()
corrIn  = map(lambda x : x.split("\n")[0],readIn)
corrInstr = str(corrIn)
corrInstr = corrInstr.replace(' ','')

#chunking
filenum = len(corrIn)
cleanDiv = filenum/args.chunksize
remain   = filenum % args.chunksize
chunks = []
if remain != 0:
    chunks = [args.chunksize]*cleanDiv+[remain]
else:
    chunks = [args.chunksize]*cleanDiv
iterIn = iter(corrIn)
chunkedIn = [list(islice(iterIn,elem)) for elem in chunks]

for i,chunk in enumerate(chunkedIn):
    sampleName = chunk[0].split("_RA")[0]#Only works with chunking
    #samplePath = str(args.eosDir)+'/'+sampleName

    #Make the jdl for each sample
    jdlName = "trimmer_"+sampleName+"_chunk"+str(i)+"_"+str(date.today())+".jdl"
    jdl = open(jdlName,"w")
    jdl.write("universe = vanilla\n")
    jdl.write("Should_Transfer_Files = YES\n")
    jdl.write("WhenToTransferOutput = ON_EXIT\n")
    jdl.write("Transfer_Input_Files = "+tarballName+"\n")
    #os.system("echo Output = condorTrimmerOutput/{0}/{1}_$(Cluster)_$(Process)_out.stdout >> {2}".format(str(date.today()),sampleName,jdlName))
    jdl.write("Output = condorTrimmerOutput/{0}/{1}_out.stdout\n".format(str(date.today()),sampleName+"_chunk"+str(i)))
    #os.system("echo Error = condorTrimmerOutput/{0}/{1}_$(Cluster)_$(Process)_err.stderr >> {2}".format(str(date.today()),sampleName,jdlName))
    jdl.write("Error = condorTrimmerOutput/{0}/{1}_err.stder\n".format(str(date.today()),sampleName+"_chunk"+str(i)))
    #os.system("Log = condorTrimmerOutput/{0}/{1}_$(Cluster_$(Process)_log.log >> {2}".format(str(date.today()),sampleName,jdlName))
    jdl.write("Log = condorTrimmerOutput/{0}/{1}_log.log\n".format(str(date.today()),sampleName+"_chunk"+str(i)))
    jdl.write("Executable = trimmer.sh\n")
    #os.system("echo Arguments = {0} {1} {2} {3} >> {4}".format(chunk,args.eosDirTuples,sampleName+"_chunk"+str(i)+"_"+str(args.prodDate),eosDirName,jdlName))
    good_chunk = str(chunk).replace(' ','')#This id the string I need to pass to 
    test_chunk = str(chunk).translate(None,' ')
    #os.system("echo Arguments = {0} {1} {2} {3} >> {4}".format(args.eosDirTuples,sampleName+"_chunk"+str(i)+"_"+str(args.prodDate),eosDirName,good_chunk,jdlName))
    jdl.write("Arguments = {0} {1} {2} {3}\n".format(args.eosDirTuples,sampleName+"_chunk"+str(i)+"_"+str(args.prodDate),eosDirName,good_chunk))
    jdl.write("Queue 1\n")#Not sure about this one
    jdl.close()
    #print chunk
    #print good_chunk
    
    #submit the jobs
    os.system("condor_submit {0}".format(jdlName))
