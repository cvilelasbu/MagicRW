from MagicRWSample import Sample

import pandas as pd

import numpy as np

from math import acos, pi

m_proton = 0.93827208

proton_track_pthr = 0.200
pion_track_pthr = 0.130

angularResolution = 2e-3*180/pi


class Nominal(Sample) :
    
    def __init__(self, outFilePath, inFilePath) :
        super(Nominal, self).__init__(name = "Nominal_ND_stop0_FHC", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)

    def leptonEnergy(self, event) :
        return event.PrimaryLep_4mom[3]

    def protonEdepFV(self, event) :
        return event.ProtonDep_FV

    def protonEdepVeto(self, event) :
        return event.ProtonDep_veto

    def protonEdep(self, event) :
        return self.protonEdepFV(event) + self.protonEdepVeto(event)

    def neutronEdepFV(self, event) :
        return event.NeutronDep_FV

    def neutronEdepVeto(self, event) :
        return event.NeutronDep_veto

    def neutronEdep(self, event) :
        return self.neutronEdepFV(event) + self.neutronEdepVeto(event)

    def piCEdepFV(self, event) :
        return event.PiCDep_FV

    def piCEdepVeto(self, event) :
        return event.PiCDep_veto

    def piCEdep(self, event) :
        return self.piCEdepFV(event) + self.piCEdepVeto(event)

    def pi0EdepFV(self, event) :
        return event.Pi0Dep_FV

    def pi0EdepVeto(self, event) :
        return event.Pi0Dep_veto

    def pi0Edep(self, event) :
        return self.pi0EdepFV(event) + self.pi0EdepVeto(event)

    def otherEdepVeto(self, event) :
        return event.OtherDep_veto

    def otherEdepFV(self, event) :
        return event.OtherDep_FV
    
    def otherEdep(self, event) :
        return self.otherEdepFV(event) + self.otherEdepVeto(event)
    
    def nonLepDepVeto(self, event) :
        return self.protonEdepVeto(event) + self.neutronEdepVeto(event) + self.piCEdepVeto(event) + self.pi0EdepVeto(event) + self.otherEdepVeto(event)

    def nonLepDepFV(self, event) :
        return self.protonEdepFV(event) + self.neutronEdepFV(event) + self.piCEdepFV(event) + self.pi0EdepFV(event) + self.otherEdepFV(event)
    
    def nonLepDep(self, event) :
        return self.nonLepDepVeto(event) + self.nonLepDepFV(event)
    
    def bindingEnergy(self) :
        return 0.0323
    
    def Erec(self, event) :
        return self.nonLepDep(event) + self.leptonEnergy(event) + self.bindingEnergy()

    def q0(self, event) :
        return event.FourMomTransfer_True[3]

    def q3(self, event) :
        return sum ( [ event.FourMomTransfer_True[i]**2 for i in range(0,3) ] )**0.5

    def w(self, event) :
        w2 = - event.Q2_True + 2*self.q0(event)*m_proton + m_proton**2

        if w2 > 0 :
            return w2**0.5
        else :
            return 0 # Sometimes (rarely) w^2 is negative (?!), return 0 in those cases

    def Q2(self, event) :
        return event.Q2_True

    def GENIEIntMode(self, event) :
        return event.GENIEInteractionTopology

    def protonEKinTrue(self, event) :
        return event.EKinProton_True

    def Etrue(self, event) :
        return event.nu_4mom[3]

    def leptonAngle(self, event) :
        return acos(event.PrimaryLep_4mom[3]/( sum ( [ PrimaryLep_4mom[i]**2 for i in range(0, 3) ] )**0.5 ) )

    def leading4Mom(self, event, pdgCode) :
        maxMom = 0
        max4Mom = [0, 0, 0, 0]
        nAboveThr = 0
        EKinRatio = 1.
        if pdgCode == 2212 :
            thisTHR = proton_track_pthr
            EKinRatio = self.EKinProtonRatio(event)
        elif pdgCode == 211 :
            EKinRatio = self.EKinPionRatio(event)
            thisTHR = pion_track_pthr

        maxMom = thisTHR

        for i in range(0, event.NFSParts) :
            if abs(event.FSPart_PDG[i]) == pdgCode :

                this4Mom = [ event.FSPart_4Mom[j] for j in range(i*4, i*4+4) ]
                
                this3Mom = self.transformed3Mom(v4Mom = this4Mom, EKinRatio = EKinRatio)

                thisMom = sum( [ i**2 for i in this3Mom ] )**0.5

                if thisMom > thisTHR :
                    nAboveThr += 1
                    if thisMom > maxMom :
                        maxMom = thisMom
                        max4Mom = this4Mom

        return max4Mom, nAboveThr
            
    def leadingProton4mom(self, event) :
        return self.leading4Mom(event, 2212)

    def leadingPion4mom(self, event) :
        return self.leading4Mom(event, 211)

    def protonAngle(self, event) :
        proton4mom = self.leadingProton4mom(event)
        if proton4mom[0] :
            return acos(proton4mom[3] / ( sum( [ proton4mom[i]**2 for i in range(0, 3) ] )**0.5 ) )
        else  :
            return 0

    def pionAngle(self, event) :
        pion4mom = self.leadingPion4mom(event)
        if pion4mom[0] :
            return acos(pion4mom[3] / ( sum( [ pion4mom[i]**2 for i in range(0, 3) ] )**0.5 ) )
        else :
            return 0

    def selection(self, event) :
        isSelected = True

        if not event.IsCC :
            isSelected = False
            return isSelected
        if self.nonLepDepVeto(event) > 0.05 :
            isSelected = False
            return isSelected
        if event.stop != 0 :
            isSelected = False
            return isSelected
        if event.PrimaryLepPDG != 13 :
            isSelected = False
            return isSelected
            
        return isSelected

    def transverseVector(self, inp, planarNormal) :
        pnUnit = planarNormal/np.linalg.norm(planarNormal)
        inpProjectPN = np.dot(pnUnit, inp)

        return inp - (inpProjectPN * pnUnit)


    def transformed3Mom(self, v4Mom, EKinRatio) :

        momSquared = sum ( [ v4Mom[i]**2 for i in range(0, 3) ] )

        if not momSquared : 
            return [ 0. for i in range(0, 3) ]

        mass = ( v4Mom[3] **2 - momSquared )**0.5

        EKinTransformed = ( v4Mom[3] - mass )*EKinRatio
        pTransformed = ( (mass + EKinTransformed)**2 - mass**2)**0.5
        pRatio = pTransformed / momSquared**0.5

        return [ v4Mom[i]*pRatio for i in range(0, 3) ]


    # Get the ratios here
    def EKinProtonRatio (self, event) : 
        # Apply momentum transformation to proton
        try :
            EKinProtonRatio = self.protonEdepFV(event) / super(self.__class__, self).protonEdepFV(event) # Assume super of self is the nominal sample and that the "transformed variable" is energy deposit
        except AttributeError :
            EKinProtonRatio = 1. # If super doesn't have protonEdep, we must be looking at the Nominal sample, so leave variables 
        except ZeroDivisionError :
            print "WARNING!!!: Zero deposited proton energy", event.fString
            EKinProtonRatio = 1.
        return EKinProtonRatio

    def EKinPionRatio (self, event) : 
        # Apply momentum transformation to proton
        try :
            EKinPionRatio = self.pionEdepFV(event) / super(self.__class__, self).pionEdepFV(event)
        except AttributeError :
            EKinPionRatio = 1.
        except ZeroDivisionError :
            EKinPionRatio = 1.

        return EKinPionRatio

    def singleTransverseKinematics(self, event, leadProton4Mom) :
    
        lepton4Mom = event.PrimaryLep_4mom
        nu4Mom = event.nu_4mom
        
        # Smear angles
        
        EKinProtonRatio = self.EKinProtonRatio(event)
        
        leadProtonTransformed3Mom = np.array( self.transformed3Mom(leadProton4Mom, EKinProtonRatio) )
        
        lepton3Mom = np.array( [ lepton4Mom[i] for i in range(0, 3) ] )
        nu3Mom = np.array( [ nu4Mom[i] for i in range(0, 3) ] )

        # Calculate STVs
        protonPt = self.transverseVector(inp = leadProtonTransformed3Mom, planarNormal = nu3Mom)
        leptonPt = self.transverseVector(inp = lepton3Mom, planarNormal = nu3Mom)

        dphit = pi-acos(np.dot(leptonPt/np.linalg.norm(leptonPt), protonPt/np.linalg.norm(protonPt))) # Minus sign here?
        dpt = protonPt + leptonPt
        dalphat = pi-acos(np.dot(leptonPt/np.linalg.norm(leptonPt), dpt/np.linalg.norm(dpt))) # Minus sign here?
        
        return np.linalg.norm(dpt), dalphat, dphit

    def doubleTransverseKinematics(self, event, leadProton4Mom, leadPion4Mom) :

        lepton4Mom = event.PrimaryLep_4mom
        nu4Mom = event.nu_4mom

        EKinProtonRatio = self.EKinProtonRatio(event)
        EKinPionRatio = self.EKinPionRatio(event)

        leadProtonTransformed3Mom = np.array( self.transformed3Mom(leadProton4Mom, EKinProtonRatio) )
        leadPionTransformed3Mom = np.array( self.transformed3Mom(leadPion4Mom, EKinPionRatio) )
        
        lepton3Mom = np.array( [ lepton4Mom[i] for i in range(0, 3) ] )
        nu3Mom = np.array( [ nu4Mom[i] for i in range(0, 3) ] )

        ztt = np.cross(nu3Mom, lepton3Mom)
        ztt = ztt/np.linalg.norm(ztt)
        
        dptt = np.dot( leadProtonTransformed3Mom + leadPionTransformed3Mom, ztt)

        return dptt
                                              
    # Variables to be used in training
    observables = { "Erec"        : { "label" : r'E$_{\mathrm{rec}}$ [GeV]',               "range" : [0., 6.] , "logScale" : False },
                    "Elep_true"   : { "label" : r'E${_{\ell}}^{\mathrm{true}}$ [GeV]}',    "range" : [0., 5.] , "logScale" : False },
                    "Eproton_dep" : { "label" : r'E${_{p}}^{\mathrm{dep}}$ [GeV]',         "range" : [0., 2.] , "logScale" : True },
                    "EpiC_dep"    : { "label" : r'E${_{\pi^{\pm}}}^{\mathrm{dep}}$ [GeV]', "range" : [0., 2.] , "logScale" : True },
                    "Epi0_dep"    : { "label" : r'E${_{\pi^{0}}}^{\mathrm{dep}}$ [GeV]',   "range" : [0., 2.] , "logScale" : True }
#                    "protonAngle" : { "label" : r'\theta${_{p}}^{\mathrm{beam}}$ [GeV]',   "range" : [-pi, pi] , "logScale" : False },
#                    "pionAngle"   : { "label" : r'\theta${_{\pi^{\pm}}}^{\mathrm{beam}}$ [GeV]',   "range" : [-pi, pi] , "logScale" : False }
    }
                    
    
    # Pairs of true variables for binned reweighting
    trueVarPairs = [ ["q0", "q3"], ["EKproton_True", "Etrue"], ["w", "Etrue"] , ["Q2", "Etrue"] ]
    
    def variables(self, event) :

        leadPion4Mom, nPionAboveTHR = self.leadingPion4mom(event)
        leadProton4Mom, nProtonAboveTHR = self.leadingProton4mom(event)

        dpt = 0
        dalphat = 0
        dphit = 0
        dptt = 0
        if event.IsCC and nPionAboveTHR == 0 and event.NPi0 == 0 and nProtonAboveTHR == 1 :
            dpt, dalphat, dphit = self.singleTransverseKinematics(event = event, leadProton4Mom =  leadProton4Mom)
        elif event.IsCC and nPionAboveTHR == 1 and event.NPi0 == 0 and nProtonAboveTHR == 1 :
            dptt = self.doubleTransverseKinematics(event = event, leadProton4Mom =  leadProton4Mom, leadPion4Mom = leadPion4Mom)

        variables = { "Erec" :           self.Erec(event),
                      "Elep_true" :      self.leptonEnergy(event),
                      "Eproton_dep" :    self.protonEdep(event) if leadProton4Mom[3] > 0 else 0, 
                      "EpiC_dep" :       self.piCEdep(event) if leadPion4Mom[3] > 0 else 0,
                      "Epi0_dep" :       self.pi0Edep(event),
                      "Etrue" :          self.Etrue(event),
                      "q0" :             self.q0(event),
                      "q3" :             self.q3(event),
                      "w" :              self.w(event),
                      "Q2" :             self.Q2(event),
                      "GENIEIntMode" :   self.GENIEIntMode(event),
                      "EKproton_True" :  self.protonEKinTrue(event),
                      "dpt" :            dpt,
                      "dalphat" :        dalphat,
                      "dphit"    :       dphit,
                      "dptt"    :        dptt, 
                      "nPionAboveTrackThr" : nPionAboveTHR,
                      "nProtonAboveTrackThr" : nProtonAboveTHR
        }

        return variables

class ProtonEdepm20pc(Nominal) :
    
    def __init__(self, outFilePath, inFilePath) :
        super(Nominal, self).__init__(name = "ProtonEdepm20pc_ND_stop0_FHC", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)

    def protonEdepFV(self, event) :
        return 0.8*event.ProtonDep_FV

    def protonEdepVeto(self, event) :
        return 0.8*event.ProtonDep_veto

class PionEdepm20pc(Nominal) :
    
    def __init__(self, outFilePath, inFilePath) :
        super(Nominal, self).__init__(name = "PionEdepm20pc_ND_stop0_FHC", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)

    def pionEdepFV(self, event) :
        return 0.8*event.PionDep_FV

    def pionEdepVeto(self, event) :
        return 0.8*event.PionDep_veto

class ProtonEdepm20pcA(Nominal) :
    
    def __init__(self, outFilePath, inFilePath) :
        super(Nominal, self).__init__(name = "ProtonEdepm20pcA_ND_stop0_FHC", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)

    def protonEdepFV(self, event) :
        if event.EKinNeutron_True >  0. :
            return 0.8*event.ProtonDep_FV
        else :
            return event.ProtonDep_FV

    def protonEdepVeto(self, event) :
        if event.EKinNeutron_True > 0. :
            return 0.8*event.ProtonDep_veto
        else :
            return event.ProtonDep_veto
