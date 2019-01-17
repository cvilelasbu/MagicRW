from MagicRWSample import Sample

import pandas as pd

import numpy as np

from math import acos, pi, cos, sin

m_proton = 0.93827208

proton_track_pthr = 0.200
pion_track_pthr = 0.130

proton_mom_res = 0.05
pion_mom_res = 0.05
lepton_mom_res = 0.05

angularResolution = 2e-3

class Nominal(Sample) :
    
    def __init__(self, outFilePath, inFilePath, chargeSel = 0) :
        self.chargeSel = chargeSel

        super(Nominal, self).__init__(name = "Nominal", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)

    def leptonEnergy(self, event) :
        return event.LepE

    def protonEdepFV(self, event) :
        return 0

    def protonEdepVeto(self, event) :
        return 0

    def protonEdep(self, event) :
        return event.eRecoP

    def neutronEdepFV(self, event) :
        return 0

    def neutronEdepVeto(self, event) :
        return 0

    def neutronEdep(self, event) :
        return event.eRecoN

    def piCEdepFV(self, event) :
        return 0

    def piCEdepVeto(self, event) :
        return 0

    def piCEdep(self, event) :
        return event.eRecoPip + event.eRecoPim

    def pi0EdepFV(self, event) :
        return 0

    def pi0EdepVeto(self, event) :
        return 0

    def pi0Edep(self, event) :
        return event.eRecoPi0

    def otherEdepVeto(self, event) :
        return 0

    def otherEdepFV(self, event) :
        return 0
    
    def otherEdep(self, event) :
        return event.eRecoOther
    
    def nonLepDepVeto(self, event) :
        return event.Ehad_veto/1000. # Convert from MeV to GeV!

    def nonLepDepFV(self, event) :
        return 0
    
    def nonLepDep(self, event) :
        return self.protonEdep(event) + self.neutronEdep(event) + self.piCEdep(event) + self.pi0Edep(event) + self.otherEdep(event)
    
    def bindingEnergy(self) :
        return 0.0
    
    def Erec(self, event) :
        return self.nonLepDep(event) + self.leptonEnergy(event) + self.bindingEnergy()

    def q0(self, event) :
        return event.Y*event.Ev

    def q3(self, event) :
        return (event.Q2 + self.q0(event)**2)**0.5

    def w(self, event) :
        return event.W

    def Q2(self, event) :
        return event.Q2

    def GENIEIntMode(self, event) :
        return event.mode

    def protonEKinTrue(self, event) :
        return event.eP

    def neutronEKin(self, event) :
        return event.eN + (1 - self.EKinProtonRatio(event))*event.eP

    def Etrue(self, event) :
        return event.Ev

    def leptonAngle(self, event) :
        return acos(event.LepMomZ/( (event.LepMomX**2 +event.LepMomY**2 +event.LepMomZ**2)**0.5 ) )

    def leading4Mom(self, event, pdgCode) :
        return 0, 0# NOT implemented in CAFs
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
    
#    def selection(self, event) :
#        isSelected = True
#
#        if not event.isCC :
#            isSelected = False
#            return isSelected
#        if self.nonLepDepVeto(event) > 0.05 :
#            isSelected = False
#            return isSelected
##        if event.stop != 0 :
##            isSelected = False
##            return isSelected
#        if self.chargeSel != 0 :
#            if np.sign(event.LepPDG) != np.sign(self.chargeSel) :
#                isSelected = False
#                return isSelected
#            
#        return isSelected

# "Official ND selection as of Jan 10 2019
    def selection (self, event) :
        isSelected = True

        if self.chargeSel != 0 :
            if np.sign(event.reco_q) != np.sign(self.chargeSel) :
                isSelected = False
                return isSelected
            
            # Select true charge for training
            if -1 * np.sign(event.LepPDG) != np.sign(self.chargeSel) :
                isSelected = False
                return isSelected

        # Select true CC for training
        if event.isCC != 1:
            isSelected = False
            return isSelected
        
        # Select true mu for training
        if np.abs(event.LepPDG) != 13 :
            isSelected = False
            return isSelected
            
        if event.reco_numu != 1 :
            isSelected = False
            return isSelected
        
        if event.muon_exit != 0 :
            isSelected = False
            return isSelected
        
        if event.Ehad_veto >= 30 :
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
#            print "WARNING!!!: Zero deposited proton energy", event.fString
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

    def RotateVector(self, angle, v, u ) :

        # Rotate vector v around vector u by angle
        u = u/np.linalg.norm(u)

        # Use Euler-Rodriguez
        a = cos (angle/2.)
        b = u[0] * sin (angle/2.)
        c = u[1] * sin (angle/2.)
        d = u[2] * sin (angle/2.)

        w = [ b, c, d ]

        return v + 2 * a*np.cross(w, v) + 2*(np.cross(w, np.cross(w, v)))

    def smearAngle(self, v3, angleSigma) :
        originalVector = v3
        
        # Get normal vector:
        u = np.cross(v3, [0, 0, 1])
        if not sum(u) :
            u = np.cross(v3, [0, 1, 0])
        if not sum(u) :
            u = np.cross(v3, [1, 0, 0])

        # Rotate v around u by randomly thrown angle
        angle = np.random.normal(scale = angleSigma)
        v3prime = self.RotateVector(angle, v3, u)
        
        # Now randomize around original vector's direction
        angle = np.random.uniform(low = 0., high = pi) # just pi as angle above can be negative, right?
        v3primeprime = self.RotateVector(angle, v = v3prime, u = originalVector)

        return v3primeprime

    def smearMomentum(self, mom3, sigma) :
        return mom3 * np.random.normal(1., sigma)
        

    def singleTransverseKinematics(self, event, leadProton4Mom) :
        return 0 # Not implemented in current CAFs
        lepton4Mom = event.PrimaryLep_4mom
        nu4Mom = event.nu_4mom
        
        EKinProtonRatio = self.EKinProtonRatio(event)
        
        leadProtonTransformed3Mom = np.array( self.transformed3Mom(leadProton4Mom, EKinProtonRatio) )
        
        lepton3Mom = np.array( [ lepton4Mom[i] for i in range(0, 3) ] )
        nu3Mom = np.array( [ nu4Mom[i] for i in range(0, 3) ] )

        # Smear angles
        lepton3Mom = self.smearAngle(lepton3Mom, angularResolution)
        leadProtonTransformed3Mom = self.smearAngle(leadProtonTransformed3Mom, angularResolution)
        
        # Smear momenta?
        lepton3Mom = self.smearMomentum(lepton3Mom, lepton_mom_res)
        leadProtonTransformed3Mom = self.smearMomentum(leadProtonTransformed3Mom, proton_mom_res)

        # Calculate STVs
        protonPt = self.transverseVector(inp = leadProtonTransformed3Mom, planarNormal = nu3Mom)
        leptonPt = self.transverseVector(inp = lepton3Mom, planarNormal = nu3Mom)

#        print np.dot(leptonPt/np.linalg.norm(leptonPt), protonPt/np.linalg.norm(protonPt))

        dphit = pi-acos(np.dot(leptonPt/np.linalg.norm(leptonPt), protonPt/np.linalg.norm(protonPt))) # Minus sign here?
        dpt = protonPt + leptonPt
        dalphat = pi-acos(np.dot(leptonPt/np.linalg.norm(leptonPt), dpt/np.linalg.norm(dpt))) # Minus sign here?
        
        return np.linalg.norm(dpt), dalphat, dphit

    def doubleTransverseKinematics(self, event, leadProton4Mom, leadPion4Mom) :
        return 0 # Not implemented in current CAFs

        lepton4Mom = event.PrimaryLep_4mom
        nu4Mom = event.nu_4mom

        EKinProtonRatio = self.EKinProtonRatio(event)
        EKinPionRatio = self.EKinPionRatio(event)

        leadProtonTransformed3Mom = np.array( self.transformed3Mom(leadProton4Mom, EKinProtonRatio) )
        leadPionTransformed3Mom = np.array( self.transformed3Mom(leadPion4Mom, EKinPionRatio) )
        
        lepton3Mom = np.array( [ lepton4Mom[i] for i in range(0, 3) ] )
        nu3Mom = np.array( [ nu4Mom[i] for i in range(0, 3) ] )

        lepton3Mom = self.smearAngle(lepton3Mom, angularResolution)
        leadProtonTransformed3Mom = self.smearAngle(leadProtonTransformed3Mom, angularResolution)
        leadPionTransformed3Mom = self.smearAngle(leadPionTransformed3Mom, angularResolution)

        # Smear momenta?
        lepton3Mom = self.smearMomentum(lepton3Mom, lepton_mom_res)
        leadProtonTransformed3Mom = self.smearMomentum(leadProtonTransformed3Mom, proton_mom_res)
        leadPionTransformed3Mom = self.smearMomentum(leadPionTransformed3Mom, pion_mom_res)

        ztt = np.cross(nu3Mom, lepton3Mom)
        ztt = ztt/np.linalg.norm(ztt)
        
        dptt = np.dot( leadProtonTransformed3Mom + leadPionTransformed3Mom, ztt)

        return dptt

    def getOAbin(self, event) :
        return 0 # Not implemented in current CAFs
        return int(-(event.XOffset+event.vtxInDetX)/60)
                                              
    # Variables to be used in training
    observables = { "Erec"                : { "label" : r'E$_{\mathrm{rec}}$ [GeV]',                                "range" : [0., 6.] , "logScale" : False },
                    "Elep_true"           : { "label" : r'E${_{\ell}}^{\mathrm{true}}$ [GeV]}',                     "range" : [0., 5.] , "logScale" : False },
                    "Eproton_dep"         : { "label" : r'E${_{p}}^{\mathrm{dep}}$ [GeV]',                          "range" : [0., 2.] , "logScale" : True },
                    "EpiC_dep"            : { "label" : r'E${_{\pi^{\pm}}}^{\mathrm{dep}}$ [GeV]',                  "range" : [0., 2.] , "logScale" : True },
                    "Epi0_dep"            : { "label" : r'E${_{\pi^{0}}}^{\mathrm{dep}}$ [GeV]',                    "range" : [0., 2.] , "logScale" : True }
    }
                    
    
    # Pairs of true variables for binned reweighting
    trueVarPairs = { "q0q3" :  {"vars" : ["q0", "q3"],               "labels" : [r'q$_{0}$ [GeV]', r'q$_{3}$ [GeV/c]'], "bins" : 75, "range" : [[0., 5.], [0., 5.]] },
                     "EnuTp" : {"vars" : ["Etrue", "EKproton_True"], "labels" : [r'E${_{\nu}}^{\mathrm{true}}$ [GeV]', r'EK$_{\mathrm{p}}^{\mathrm{true}}$ [GeV]'], "bins" : 75, "range" : [[0., 10.], [0., 3.]] },                    "ElTp" :  {"vars" : ["Elep_true", "EKproton_True"], "labels" : [r'E${_{\ell}}^{\mathrm{true}}$ [GeV]', r'EK$_{\mathrm{p}}^{\mathrm{true}}$ [GeV]'], "bins" : 75, "range" : [[0., 10.], [0., 3.]] },
                     "EnuQ2" : {"vars" : ["Etrue", "Q2"],            "labels" : [r'E${_{\nu}}^{\mathrm{true}}$ [GeV]', r'Q$^{2}$ [GeV$^{2}]'], "bins" : 75, "range" : [[0., 10.], [0., 5.]] },
                     "EnuW"  : {"vars" : ["Etrue", "w"],             "labels" : [r'E${_{\nu}}^{\mathrm{true}}$ [GeV]', r'W [GeV/c$^{2}$]'], "bins" : 75, "range" : [[0., 10.], [0., 5.]] } }
                     
                     

    def variables(self, event) :

        leadPion4Mom, nPionAboveTHR = self.leadingPion4mom(event)
        leadProton4Mom, nProtonAboveTHR = self.leadingProton4mom(event)

        dpt = 0
        dalphat = 0
        dphit = 0
        dptt = 0
#        if event.IsCC and nPionAboveTHR == 0 and event.NPi0 == 0 and nProtonAboveTHR == 1 :
#            dpt, dalphat, dphit = self.singleTransverseKinematics(event = event, leadProton4Mom =  leadProton4Mom)
#        elif event.IsCC and nPionAboveTHR == 1 and event.NPi0 == 0 and nProtonAboveTHR == 1 :
#            dptt = self.doubleTransverseKinematics(event = event, leadProton4Mom =  leadProton4Mom, leadPion4Mom = leadPion4Mom)

        variables = { "Erec" :           self.Erec(event),
                      "Elep_true" :      self.leptonEnergy(event),
#                      "Eproton_dep" :    self.protonEdep(event) if leadProton4Mom[3] > 0 else 0, 
#                      "EpiC_dep" :       self.piCEdep(event) if leadPion4Mom[3] > 0 else 0,
                      "Eproton_dep" :    self.protonEdep(event),
                      "EpiC_dep" :       self.piCEdep(event),
                      "Epi0_dep" :       self.pi0Edep(event),
                      "Etrue" :          self.Etrue(event),
                      "q0" :             self.q0(event),
                      "q3" :             self.q3(event),
                      "w" :              self.w(event),
                      "Q2" :             self.Q2(event),
                      "GENIEIntMode" :   self.GENIEIntMode(event),
                      "EKproton_True" :  self.protonEKinTrue(event),
                      "EKneutron" :      self.neutronEKin(event),
                      "dpt" :            dpt,
                      "dalphat" :        dalphat,
                      "dphit"    :       dphit,
                      "dptt"    :        dptt, 
                      "nPionAboveTrackThr" : nPionAboveTHR,
                      "nProtonAboveTrackThr" : nProtonAboveTHR,
                      "oaBin" :          self.getOAbin(event)
        }

        return variables

class ProtonEdepm20pc(Nominal) :
    
    def __init__(self, outFilePath, inFilePath, chargeSel = 0) :
        self.chargeSel = chargeSel
        super(Nominal, self).__init__(name = "ProtonEdepm20pc", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)


    def protonEdep(self, event) :
        return event.eRecoP*0.8

class PionEdepm20pc(Nominal) :
    
    def __init__(self, outFilePath, inFilePath, chargeSel = 0 ) :
        self.chargeSel = chargeSel
        super(Nominal, self).__init__(name = "PionEdepm20pc", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)

    def piCEdep(self, event) :
        return (event.eRecoPip + event.eRecoPim)*0.8
        
class ProtonEdepm20pcA(Nominal) :
    
    def __init__(self, outFilePath, inFilePath, chargeSel =0 ) :
        self.chargeSel = chargeSel
        super(Nominal, self).__init__(name = "ProtonEdepm20pcA", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)

    def protonEdep(self, event) :
        if event.eN > 0. :
            return event.eRecoP*0.8
        else :
            return event.eRecoP


class NominalTV(Nominal) :

    def __init__(self, outFilePath, inFilePath, chargeSel = 0) :
        self.chargeSel = chargeSel
        super(Nominal, self).__init__(name = "NominalTV", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)

    observables = { "Erec"                : { "label" : r'E$_{\mathrm{rec}}$ [GeV]',                                "range" : [0., 6.] , "logScale" : False },
                    "Elep_true"           : { "label" : r'E${_{\ell}}^{\mathrm{true}}$ [GeV]}',                     "range" : [0., 5.] , "logScale" : False },
                    "Eproton_dep"         : { "label" : r'E${_{p}}^{\mathrm{dep}}$ [GeV]',                          "range" : [0., 2.] , "logScale" : True },
                    "EpiC_dep"            : { "label" : r'E${_{\pi^{\pm}}}^{\mathrm{dep}}$ [GeV]',                  "range" : [0., 2.] , "logScale" : True },
                    "Epi0_dep"            : { "label" : r'E${_{\pi^{0}}}^{\mathrm{dep}}$ [GeV]',                    "range" : [0., 2.] , "logScale" : True },
                    "nPionAboveTrackThr"  : { "label" : r'N${_{\pi^{\pm}}}^{p > '+str(pion_track_pthr*1e3)+' MeV/c}$',"range" : [0.0, 10] , "logScale" : True },
                    "nProtonAboveTrackThr": { "label" : r'N${_{p}}^{p > '+str(proton_track_pthr*1e3)+' MeV/c}$',        "range" : [.0, 10] , "logScale" : True },
                    "dpt"                 : { "label" : r'$\delta{_{p_{\mathrm{T}}}}$ [GeV/c]',                       "range" : [0.01, 1.5], "logScale" : False },
                    "dphit"               : { "label" : r'$\delta{_{\phi_{\mathrm{T}}}}$',                            "range" : [0.01, pi],  "logScale" : False },
                    "dalphat"             : { "label" : r'$\delta{_{\alpha_{\mathrm{T}}}}$',                          "range" : [0.01, pi],  "logScale" : False },
                    "dptt"                : { "label" : r'$\delta{_{p_\mathrm{TT}}}$ [GeV/c]',                      "range" : [-1., 1.], "logScale" : True },                    
                }

class ProtonEdepm20pcTV(NominalTV) :
    
    def __init__(self, outFilePath, inFilePath, chargeSel = 0) :
        self.chargeSel = chargeSel
        super(Nominal, self).__init__(name = "ProtonEdepm20pcTV", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)

    def protonEdepFV(self, event) :
        return 0.8*event.ProtonDep_FV

    def protonEdepVeto(self, event) :
        return 0.8*event.ProtonDep_veto

class PionEdepm20pcTV(NominalTV) :
    
    def __init__(self, outFilePath, inFilePath, chargeSel = 0) :
        self.chargeSel = chargeSel
        super(Nominal, self).__init__(name = "PionEdepm20pcTV", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)

    def piCEdepFV(self, event) :
        return 0.8*event.PiCDep_FV

    def piCEdepVeto(self, event) :
        return 0.8*event.PiCDep_veto

class ProtonEdepm20pcATV(NominalTV) :
    
    def __init__(self, outFilePath, inFilePath, chargeSel = 0) :
        self.chargeSel = chargeSel
        super(Nominal, self).__init__(name = "ProtonEdepm20pcATV", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)

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

class NominalTV_Neutron(NominalTV) :

    def __init__(self, outFilePath, inFilePath, chargeSel = 0) :
        self.chargeSel = chargeSel
        super(Nominal, self).__init__(name = "NominalTV_ND_Neutron_FHC", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)

    observables = { "Erec"                : { "label" : r'E$_{\mathrm{rec}}$ [GeV]',                                "range" : [0., 6.] , "logScale" : False },
                    "Elep_true"           : { "label" : r'E${_{\ell}}^{\mathrm{true}}$ [GeV]}',                     "range" : [0., 5.] , "logScale" : False },
                    "Eproton_dep"         : { "label" : r'E${_{p}}^{\mathrm{dep}}$ [GeV]',                          "range" : [0., 2.] , "logScale" : True },
                    "EKneutron"       : { "label" : r'E${_{n}}^{\mathrm{true}}$',                               "range" : [0., 2.], "logScale" : True },
                    "EpiC_dep"            : { "label" : r'E${_{\pi^{\pm}}}^{\mathrm{dep}}$ [GeV]',                  "range" : [0., 2.] , "logScale" : True },
                    "Epi0_dep"            : { "label" : r'E${_{\pi^{0}}}^{\mathrm{dep}}$ [GeV]',                    "range" : [0., 2.] , "logScale" : True },
#                    "nPionAboveTrackThr"  : { "label" : r'N${_{\pi^{\pm}}}^{p > '+str(pion_track_pthr*1e3)+' MeV/c}$',"range" : [0.0, 10] , "logScale" : True },
#                    "nProtonAboveTrackThr": { "label" : r'N${_{p}}^{p > '+str(proton_track_pthr*1e3)+' MeV/c}$',        "range" : [.0, 10] , "logScale" : True },
#                    "dpt"                 : { "label" : r'$\delta{_{p_{\mathrm{T}}}}$ [GeV/c]',                       "range" : [0.01, 1.5], "logScale" : False },
#                    "dphit"               : { "label" : r'$\delta{_{\phi_{\mathrm{T}}}}$',                            "range" : [0.01, pi],  "logScale" : False },
#                    "dalphat"             : { "label" : r'$\delta{_{\alpha_{\mathrm{T}}}}$',                          "range" : [0.01, pi],  "logScale" : False },
#                    "dptt"                : { "label" : r'$\delta{_{p_\mathrm{TT}}}$ [GeV/c]',                      "range" : [-1., 1.], "logScale" : True },                    
                }

#                     def selection(self, event) :
#                         isSelected = True
#                 
#                         if not event.IsCC :
#                             isSelected = False
#                             return isSelected
#                         if self.nonLepDepVeto(event) > 0.05 :
#                             isSelected = False
#                             return isSelected
#                 #        if event.stop != 0 :
#                 #            isSelected = False
#                 #            return isSelected
#                         if self.chargeSel != 0 :
#                             if event.PrimaryLepPDG != (self.chargeSel * 13) :
#                                 isSelected = False
#                                 return isSelected
#                             
#                         return isSelected


#    observables = { "Erec"                : { "label" : r'E$_{\mathrm{rec}}$ [GeV]',                                "range" : [0., 6.] , "logScale" : False },
#                    "Elep_true"           : { "label" : r'E${_{\ell}}^{\mathrm{true}}$ [GeV]}',                     "range" : [0., 5.] , "logScale" : False },
#                    "Eproton_dep"         : { "label" : r'E${_{p}}^{\mathrm{dep}}$ [GeV]',                          "range" : [0., 2.] , "logScale" : True },
#                    "EpiC_dep"            : { "label" : r'E${_{\pi^{\pm}}}^{\mathrm{dep}}$ [GeV]',                  "range" : [0., 2.] , "logScale" : True },
#                    "Epi0_dep"            : { "label" : r'E${_{\pi^{0}}}^{\mathrm{dep}}$ [GeV]',                    "range" : [0., 2.] , "logScale" : True }
#                }

class ProtonEdepm20pcTV_Neutron(NominalTV_Neutron) :
    
    def __init__(self, outFilePath, inFilePath, chargeSel = 0) :
        self.chargeSel = chargeSel
        super(Nominal, self).__init__(name = "ProtonEdepm20pcTV_Neutron", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)

    def protonEdepFV(self, event) :
        return 0.8*event.ProtonDep_FV

    def protonEdepVeto(self, event) :
        return 0.8*event.ProtonDep_veto

class PionEdepm20pcTV_Neutron(NominalTV_Neutron) :
    
    def __init__(self, outFilePath, inFilePath, chargeSel = 0) :
        self.chargeSel = chargeSel
        super(Nominal, self).__init__(name = "PionEdepm20pcTV_Neutron", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)

    def piCEdepFV(self, event) :
        return 0.8*event.PiCDep_FV

    def piCEdepVeto(self, event) :
        return 0.8*event.PiCDep_veto

class ProtonEdepm20pcATV_Neutron(NominalTV_Neutron) :
    
    def __init__(self, outFilePath, inFilePath, chargeSel = 0) :
        self.chargeSel = chargeSel
        super(Nominal, self).__init__(name = "ProtonEdepm20pcATV_Neutron", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)

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


class Nominal_FD(Nominal) :
        
    def __init__(self, outFilePath, inFilePath, chargeSel = 0) :
        self.chargeSel = chargeSel
        super(Nominal, self).__init__(name = "Nominal_FD", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.)
    
    def protonEdep(self, event) :
        return event.eDepP
    
    def neutronEdep(self, event) :
        return event.eDepN

    def piCEdep(self, event) :
        return event.eDepPip + event.eDepPim

    def pi0Edep(self, event) :
        return event.eDepPi0

    def otherEdep(self, event) :
        return event.eDepOther
    
    def nonLepDepVeto(self, event) :
        return 0.
    
    def variables(self, event) :

        variables = { "Erec" :           self.Erec(event),
                      "Elep_true" :      self.leptonEnergy(event),
                      "Eproton_dep" :    self.protonEdep(event),
                      "EpiC_dep" :       self.piCEdep(event),
                      "Epi0_dep" :       self.pi0Edep(event),
                      "Etrue" :          self.Etrue(event),
                      "q0" :             self.q0(event),
                      "q3" :             self.q3(event),
                      "w" :              self.w(event),
                      "Q2" :             self.Q2(event),
                      "GENIEIntMode" :   self.GENIEIntMode(event),
                      "EKproton_True" :  self.protonEKinTrue(event),
                      "EKneutron" :      self.neutronEKin(event),
        }

        return variables

    def selection (self, event) :
        isSelected = True

        if event.cvnnumu <= 0.5 :
            isSelected = False
            return isSelected
        
        if event.cvnnue >= 0.85 :
            isSelected = False
            return isSelected
        return isSelected

class ProtonEdepm20pc_FD(Nominal_FD) :
    
    def __init__(self, outFilePath, inFilePath, chargeSel = 0) :
        self.chargeSel = chargeSel
        super(Nominal, self).__init__(name = "ProtonEdepm20pc_FD", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.)


    def protonEdep(self, event) :
        return event.eDepP*0.8

class Nominal_NoNeutron(Nominal) :
        
    def __init__(self, outFilePath, inFilePath, chargeSel = 0) :
        self.chargeSel = chargeSel
        super(Nominal, self).__init__(name = "Nominal_NoNeutron", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)
        
    def nonLepDep(self, event) :
        return self.protonEdep(event) + self.piCEdep(event) + self.pi0Edep(event) + self.otherEdep(event)

        

class ProtonEdepm20pc_NoNeutron(ProtonEdepm20pc) :
    
    def __init__(self, outFilePath, inFilePath, chargeSel = 0) :
        self.chargeSel = chargeSel
        super(Nominal, self).__init__(name = "ProtonEdepm20pc_NoNeutron", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.75)

    def nonLepDep(self, event) :
        return self.protonEdep(event) + self.piCEdep(event) + self.pi0Edep(event) + self.otherEdep(event)

class Nominal_NoNeutron_FD(Nominal_FD) :
        
    def __init__(self, outFilePath, inFilePath, chargeSel = 0) :
        self.chargeSel = chargeSel
        super(Nominal, self).__init__(name = "Nominal_NoNeutron_FD", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.)
        
    def nonLepDep(self, event) :
        return self.protonEdep(event) + self.piCEdep(event) + self.pi0Edep(event) + self.otherEdep(event)

        

class ProtonEdepm20pc_NoNeutron_FD(ProtonEdepm20pc_FD) :
    
    def __init__(self, outFilePath, inFilePath, chargeSel = 0) :
        self.chargeSel = chargeSel
        super(Nominal, self).__init__(name = "ProtonEdepm20pc_NoNeutron_FD", outFilePath = outFilePath, inFilePath = inFilePath, trainFrac = 0.)

    def nonLepDep(self, event) :
        return self.protonEdep(event) + self.piCEdep(event) + self.pi0Edep(event) + self.otherEdep(event)


