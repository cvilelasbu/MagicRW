import ROOT

from multiprocessing import Process

from DunePRISMSamples import *

pickle = False
train = False
plot = False
produceBinned = True
plotBinned = True

FHC_nominalFilePath = "/gpfs/scratch/crfernandesv/DunePrism/FHC/4855489.*[0-4].Processed.root"
FHC_fakeFilePath = "/gpfs/scratch/crfernandesv/DunePrism/FHC/4855489.*[5-9].Processed.root"
FHC_outFilePath = "/gpfs/scratch/crfernandesv/MagicRW/FHC_Samples"
FHC_outFilePathTV = "/gpfs/scratch/crfernandesv/MagicRW/FHC_SamplesTV"
FHC_outFilePathTV_PRISM = "/gpfs/scratch/crfernandesv/MagicRW/FHC_SamplesTV_PRISM"

RHC_nominalFilePath = "/gpfs/scratch/crfernandesv/DunePrism/RHC/4855497.*[0-4].Processed.root"
RHC_fakeFilePath = "/gpfs/scratch/crfernandesv/DunePrism/RHC/4855497.*[5-9].Processed.root"
RHC_outFilePath = "/gpfs/scratch/crfernandesv/MagicRW/RHC_Samples"
RHC_outFilePathTV = "/gpfs/scratch/crfernandesv/MagicRW/RHC_SamplesTV"
RHC_outFilePathTV_PRISM = "/gpfs/scratch/crfernandesv/MagicRW/RHC_SamplesTV_PRISM"

# BELOW "chargeSel" means sign of the PDG code, so + is particle, and - antiparticle - selecting the outgoing muon.
samplesOA_FHC = [ Nominal(         inFilePath = FHC_nominalFilePath, outFilePath = FHC_outFilePath, chargeSel=+1),
                  ProtonEdepm20pc( inFilePath = FHC_fakeFilePath,    outFilePath = FHC_outFilePath, chargeSel=+1),
                  PionEdepm20pc(   inFilePath = FHC_fakeFilePath,    outFilePath = FHC_outFilePath, chargeSel=+1),
                  ProtonEdepm20pcA(inFilePath = FHC_fakeFilePath,    outFilePath = FHC_outFilePath, chargeSel=+1) ]

samplesOA_TV_FHC = [NominalTV(         inFilePath = FHC_nominalFilePath, outFilePath = FHC_outFilePathTV, chargeSel=+1), 
                    ProtonEdepm20pcTV( inFilePath = FHC_fakeFilePath,    outFilePath = FHC_outFilePathTV, chargeSel=+1),
                    PionEdepm20pcTV(   inFilePath = FHC_fakeFilePath,    outFilePath = FHC_outFilePathTV, chargeSel=+1),
                    ProtonEdepm20pcATV(inFilePath = FHC_fakeFilePath,    outFilePath = FHC_outFilePathTV, chargeSel=+1)]

samplesPRISM_TV_FHC = [ NominalTV_PRISM(         inFilePath = FHC_nominalFilePath, outFilePath = FHC_outFilePathTV_PRISM, chargeSel=+1), 
                        ProtonEdepm20pcTV_PRISM( inFilePath = FHC_fakeFilePath,    outFilePath = FHC_outFilePathTV_PRISM, chargeSel=+1),
                        PionEdepm20pcTV_PRISM(   inFilePath = FHC_fakeFilePath,    outFilePath = FHC_outFilePathTV_PRISM, chargeSel=+1),
                        ProtonEdepm20pcATV_PRISM(inFilePath = FHC_fakeFilePath,    outFilePath = FHC_outFilePathTV_PRISM, chargeSel=+1)]

samplesOA_RHC = [Nominal(         inFilePath = RHC_nominalFilePath, outFilePath = RHC_outFilePath, chargeSel=-1), 
                 ProtonEdepm20pc( inFilePath = RHC_fakeFilePath,    outFilePath = RHC_outFilePath, chargeSel=-1),
                 PionEdepm20pc(   inFilePath = RHC_fakeFilePath,    outFilePath = RHC_outFilePath, chargeSel=-1),
                 ProtonEdepm20pcA(inFilePath = RHC_fakeFilePath,    outFilePath = RHC_outFilePath, chargeSel=-1)]

samplesOA_TV_RHC = [ NominalTV(         inFilePath = RHC_nominalFilePath, outFilePath = RHC_outFilePathTV, chargeSel=-1), 
                     ProtonEdepm20pcTV( inFilePath = RHC_fakeFilePath,    outFilePath = RHC_outFilePathTV, chargeSel=-1),
                     PionEdepm20pcTV(   inFilePath = RHC_fakeFilePath,    outFilePath = RHC_outFilePathTV, chargeSel=-1),
                     ProtonEdepm20pcATV(inFilePath = RHC_fakeFilePath,    outFilePath = RHC_outFilePathTV, chargeSel=-1)]

samplesPRISM_TV_RHC = [ NominalTV_PRISM(         inFilePath = RHC_nominalFilePath, outFilePath = RHC_outFilePathTV_PRISM, chargeSel=-1), 
                        ProtonEdepm20pcTV_PRISM( inFilePath = RHC_fakeFilePath,    outFilePath = RHC_outFilePathTV_PRISM, chargeSel=-1),
                        PionEdepm20pcTV_PRISM(   inFilePath = RHC_fakeFilePath,    outFilePath = RHC_outFilePathTV_PRISM, chargeSel=-1),
                        ProtonEdepm20pcATV_PRISM(inFilePath = RHC_fakeFilePath,    outFilePath = RHC_outFilePathTV_PRISM, chargeSel=-1)]


samplesTestNom = [ Nominal(         inFilePath = FHC_nominalFilePath, outFilePath = FHC_outFilePath, chargeSel=+1) ]

samples = [  samplesOA_FHC, samplesOA_TV_FHC, samplesPRISM_TV_FHC, samplesOA_RHC, samplesOA_TV_RHC, samplesPRISM_TV_RHC ]
#samples = [  samplesOA_FHC, samplesOA_RHC ]


if pickle :
    processesPickle = []
    for sample in samples :
        for s in sample : 
            processesPickle.append( Process( target = s.pickleData ) )

    for p in processesPickle :
        p.start()
    for p in processesPickle :
        p.join()

if train :
    processesPickle = []

    for sample in samples :
        sNom = sample[0]
        for s in sample[1:] :
            processesPickle.append( Process( target = s.trainBDT, args=(sNom,) ) )
        
    for p in processesPickle :
        p.start()
    for p in processesPickle :
        p.join()

if plot :
    processesPickle = []

    for sample in samples :
        sNom = sample[0]
        for s in sample[1:] :
            processesPickle.append( Process( target = s.plotDiagnostics, args=(sNom,) ) )

    for p in processesPickle :
        p.start()
    for p in processesPickle :
        p.join()

if produceBinned :
    processesPickle = []

    for sample in samples :
        sNom = sample[0]
        for s in sample[1:] :
            processesPickle.append( Process( target = s.makeBinnedWeights ) )

    for p in processesPickle :
        p.start()
    for p in processesPickle :
        p.join()

if plotBinned :
    processesPickle = []

    for sample in samples :
        sNom = sample[0]
        for s in sample[1:] :
            processesPickle.append( Process( target = s.plotDiagnostics, args=(sNom, "EnuTp",) ) )
            processesPickle.append( Process( target = s.plotDiagnostics, args=(sNom, "ElTp",) ) )
            processesPickle.append( Process( target = s.plotDiagnostics, args=(sNom, "q0q3",) ) )
            processesPickle.append( Process( target = s.plotDiagnostics, args=(sNom, "EnuW",) ) )
            processesPickle.append( Process( target = s.plotDiagnostics, args=(sNom, "EnuQ2",) ) )

    for p in processesPickle :
        p.start()
    for p in processesPickle :
        p.join()

