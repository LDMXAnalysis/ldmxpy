
import AnalysisUtils as au
import ROOT as r

from numpy import linalg as la
from rootpy.tree import Tree

from EventModels import TrackerEvent

class TrackerAnalysis(object): 

    def __init__(self): 
        self.tree = None

    def initialize(self, params): 
        self.tree = Tree('tracker_ntuple', model=TrackerEvent)

    def process(self, event): 

        # Get the collection of MC particles from the event.
        particles = event.get_collection('SimParticles_sim')

        primary = [p for p in particles if p.getGenStatus() == 1][0]

        pvec = primary.getMomentum()
        vec = r.TVector3(pvec[0], pvec[1], pvec[2])
        
        self.tree.primary_pdg_id = primary.getPdgID()
        self.tree.primary_p = vec.Mag()
        self.tree.primary_theta = vec.Theta()
        self.tree.primary_phi = vec.Phi()

        # Get recoil tracker hits from the event.
        recoil_hits = event.get_collection('RecoilSimHits_sim')
        self.tree.recoil_hits_count = recoil_hits.GetEntriesFast()

        for hit in recoil_hits: 
            self.tree.rhit_x.push_back(hit.getPosition()[0])
            self.tree.rhit_y.push_back(hit.getPosition()[1])
            self.tree.rhit_z.push_back(hit.getPosition()[2])
            #self.tree.rhit_pdg_id.push_back(hit.getPdgID())
            #self.tree.rhit_trk_id.push_back(hit.getTrackID())

        # Get the FindableTracks collection from the event
        if event.collection_exist('FindableTracks_recon'):
            findable_tracks = event.get_collection('FindableTracks_recon')
            findable_dic, loose_dic, axial_dic = au.get_findable_tracks_map(findable_tracks)
        
            self.tree.recoil_track_count        = len(findable_dic)
            self.tree.recoil_loose_track_count  = len(loose_dic)
            self.tree.recoil_axial_track_count  = len(axial_dic)

            fparticles = findable_dic.keys()
            for particle in fparticles: 
           
                if particle == primary: self.tree.primary_findable = 1

                self.tree.rfindable_trk_pdg_id.push_back(particle.getPdgID())
                #self.tree.rfindable_trk_id.push_back(particle.getTrackID())
            
                pvec = particle.getMomentum()
                vec = r.TVector3(pvec[0], pvec[1], pvec[2])
                
                self.tree.rfindable_trk_p.push_back(vec.Mag())
                self.tree.rfindable_trk_theta.push_back(vec.Theta())
                self.tree.rfindable_trk_phi.push_back(vec.Phi())

        #
        # Hit Level
        #
        '''
         
        hit_counter = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        charge_counter = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        l10_hit_counter = 0

        for recoil_hit in recoil_hits:
            #recoil_hit.Print()
            hit_counter[recoil_hit.getLayerID() - 1] += 1
            charge_counter[recoil_hit.getLayerID() - 1] += recoil_hit.getEdep()
            
            if recoil_hit.getLayerID() == 10: 
                if recoil_hit.getSimParticle() in findable_particles: continue
                l10_hit_counter += 1
        
        self.tree.recoil_hits_count_l10_no_track = l10_hit_counter

        for layer_n in xrange(0, len(hit_counter)):
            setattr(self.tree, 'recoil_hits_count_l%s' % (layer_n + 1), hit_counter[layer_n])
            setattr(self.tree, 'recoil_charge_total_l%s' % (layer_n + 1), charge_counter[layer_n])

        tagger_hits = event.get_collection('TaggerSimHits_sim')
        self.tree.tagger_hits_count = tagger_hits.GetEntriesFast()
         
        hit_counter    = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        charge_counter = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        for tagger_hit in tagger_hits:
            hit_counter[tagger_hit.getLayerID() - 1] += 1
            charge_counter[tagger_hit.getLayerID() - 1] += tagger_hit.getEdep()
       
        for layer_n in xrange(0, len(hit_counter)):
            setattr(self.tree, 'tagger_hits_count_l%s' % (layer_n + 1), hit_counter[layer_n])
            setattr(self.tree, 'tagger_charge_total_l%s' % (layer_n + 1), charge_counter[layer_n])
        '''
        '''
        target_sp_hits = event.get_collection('TargetScoringPlaneHits_sim')

        self.tree.single_trk_p = -9999
        self.tree.single_trk_pdg = -9999
        if len(findable_dic) == 1:
            #print '[ TargetPhotoNuclearAnalysis ]: Only have a single findable track.'
            findable_track = findable_dic.itervalues().next()
            sim_particle = findable_track.getSimParticle()
            self.tree.single_trk_pdg = findable_track.getSimParticle().getPdgID()
            p_find = la.norm(sim_particle.getMomentum())
            #print '[ TargetPhotoNuclearAnalysis ]: p of findable track: %s' % p_find
            is_recoil = False
            if recoil_e == sim_particle: is_recoil = True
            #if is_recoil: print '[ TargetPhotoNuclearAnalysis ]: Findable track is recoil e.'
            #print 'Sim particle:'
            #sim_particle.Print()
            min = 10000
            for target_sp_hit in target_sp_hits: 
                if target_sp_hit.getSimParticle() == sim_particle: 
                    #print '[ TargetPhotoNuclearAnalysis ]: Iterating over target sp sim particle.'
                    #target_sp_hit.getSimParticle().Print()
                    pvec = target_sp_hit.getMomentum()
                    if pvec[2] < 0: 
                        #print '[ TargetPhotoNuclearAnalysis ]: particle is going backwards, pz = %s' % pvec[2] 
                        continue
                    p = la.norm(pvec)
                    #print '[ TargetPhotoNuclearAnalysis ]: Momentum at scoring plane: %s' % p
                    if is_recoil: 
                        #print '[ TargetPhotoNuclearAnalysis ]: Momentum of gamma: %s' % self.tree.pn_gamma_energy
                        diff = p_find - (pn_gamma.getEnergy() + p)
                        #print '[ TargetPhotoNuclearAnalysis ]: Difference: %s' % diff
                    else: 
                        diff = p_find - p
                    
                    if diff < min: 
                        #print '[ TargetPhotoNuclearAnalysis ]: Found best match'
                        self.tree.single_trk_p = p
                        min = diff
        '''
        self.tree.fill(reset=True)
    
    def finalize(self):

        self.tree.write()
