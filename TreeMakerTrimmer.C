#define TreeMakerTrimmer_cxx
#include "TreeMakerTrimmer.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <iostream>

void TreeMakerTrimmer::Loop(std::string outputFileName)
{
//   In a ROOT session, you can do:
//      root> .L TreeMakerTrimmer.C
//      root> TreeMakerTrimmer t
//      root> t.GetEntry(12); // Fill t data members with entry number 12
//      root> t.Show();       // Show values of entry 12
//      root> t.Show(16);     // Read and show values of entry 16
//      root> t.Loop();       // Loop on all entries
//

//     This is the loop skeleton where:
//    jentry is the global entry number in the chain
//    ientry is the entry number in the current Tree
//  Note that the argument to GetEntry must be:
//    jentry for TChain::GetEntry
//    ientry for TTree::GetEntry and TBranch::GetEntry
//
//       To read only selected branches, Insert statements like:
// METHOD1:
//    fChain->SetBranchStatus("*",0);  // disable all branches
//    fChain->SetBranchStatus("branchname",1);  // activate branchname
// METHOD2: replace line
//    fChain->GetEntry(jentry);       //read all branches
//by  b_branchname->GetEntry(ientry); //read only this branch
   if (fChain == 0) return;

   Long64_t nentries = fChain->GetEntriesFast();
   Long64_t original_nentries;
   Long64_t nbytes = 0, nb = 0;
   
   //Define the skim output file and tree
   TFile* trimFile = new TFile(outputFileName.c_str(),"recreate");
   TTree* trimTree = fChain->CloneTree(0);
   TH1F*  hnevents = new TH1F("hnevents","original entries",1,0,1);
   hnevents->SetBinContent(1,nentries);

   //Define cut variablesx
   int   passEvents = 0;
   //float minZpt     = 100.0;
   //float wpdoubleb = 0.6;
   
   std::cout<<"starting skim"<<std::endl;
   
   for (Long64_t jentry=0; jentry<nentries;jentry++) {
      Long64_t ientry = LoadTree(jentry);
      if (ientry < 0) break;
      nb = fChain->GetEntry(jentry);   nbytes += nb;
     
      //Define some bools to signal events to write
      bool passZ      = false;
      bool passH      = false;
      bool passMET    = false;
      bool passfatnum = false;

      //A counter, for my sanity
      if (jentry%20000 == 0) {
      	std::cout<<"skimming event "<<jentry<<std::endl;
      }

      //Quick break to check condor
      //if (jentry == 2000) {
      //break;
      //}

      //Checking the ZProducer Zs
      unsigned int nZs = ZCandidates->size();
      //std::cout<<"The number of good Zs "<<nZs<<std::endl;
      if (nZs > 0) {
	//std::vector<TLorentzVector>::iterator zit;
	//I know there is always one Z, so this might not be the best way
	//for (zit = ZCandidates->begin(); zit != ZCandidates->end(); ++zit) {
	//  std::cout<<"The Z pt, if there is a Z, is "<<zit->Pt()<<std::endl;
	//  if (zit->Pt() > minZpt) {
	    passZ = true;
	    //  }
      //	}
      }

      //std::cout<<"    passZ value "<<passZ<<std::endl;

      //Checking the Fat Jets
      unsigned int nFats = JetsAK8Clean->size();
      //std::cout<<"The number of cleaned fat jets "<<nFats<<std::endl;
      if (nFats > 0) {
	//std::vector<TLorentzVector>::iterator fatit;
	//for (fatit = JetsAK8Clean->begin();fatit != JetsAK8Clean->end(); ++fatit) {
	//  std::cout<<"The fat jet pT is "<<fatit->Pt()<<std::endl;
        //}
	passfatnum = true;
      }
      //A quick look at what this crazy thing write
      //if (jentry == 25000) {
      //std::cout<<"reached 50 events"<<std::endl;
      //break;
      //}

      //std::cout<<"The passZ is "<<passZ<<" and the passfatnum is "<<passfatnum<<std::endl;
      if (Cut(ientry) < 0) continue;
      if (passZ && passfatnum) {
      	trimTree->Fill();
      	passEvents += 1;
      }
   }
   trimFile->Write();
   trimFile->Close();   
   std::cout<<"trimmed to "<< passEvents <<" events"<<std::endl;
}

