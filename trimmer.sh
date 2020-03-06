#!/bin/bash

#untar your crap
echo "untaring  directory with skimming code"
tar -xvf condorTrimmer.tar.gz
cd condorTrimmer

#source your environment
source /cvmfs/sft.cern.ch/lcg/views/LCG_89/x86_64-slc6-gcc62-opt/setup.sh

#run this mother
echo "running the skimmer"
#python runTreeMakerTrimmer.py -f $1 -e $2 -o $3 #This has been changed to spit file out where executed
python runTreeMakerTrimmer.py -e $1 -o $2 -f $4 #This has been changed to spit file out where executed

#For each file created, do something. This needs to go to an eos space
OUTDIR=root://cmseos.fnal.gov//store/user/gcumming/$3/
for FILE in ./*.root
do
    echo "copying ${FILE} to eos ${OUTDIR}"
    xrdcp ${FILE} ${OUTDIR}/${FILE}
    XRDEXIT=$?
    if [[ $XRDEXIT -ne 0 ]]; then
	rm ${FILE}
	echo "failure in xrdcp, exit code $XRDEXIT"
	exit $XRDEXIT
    fi
    rm ${FILE}
done


#cleanup
cd ${_CONDOR_SCRATCH_DIR_}
rm -rf condorTrimmer
rm condorTrimmer.tar.gz