from __future__ import absolute_import
import CombineHarvester.CombineTools.ch as ch
import yaml
from utils.helpers import load_cfg_file
config = load_cfg_file()

PathFileNP = config['PATH']['path_file_np']
tag = config['GENERAL']['tag']
vbf_masses = ch.MassesFromRange(config['GENERAL']['massesvbf'])
vbf_mass_set = [str(m) for m in vbf_masses]

def AddSystNP(lnN_or_Shape_NP, src, cb, VBF = None):
    for process in lnN_or_Shape_NP.keys():
        if lnN_or_Shape_NP[process] == None:
            print('No NPs found for ' +process)
            continue
        if 'HNL' in process:
            # Add signal processes with uncertainties for each mass point
            mass = process.replace('HNL','')
            for NP in lnN_or_Shape_NP[process].keys():
                if lnN_or_Shape_NP[process][NP]['type'] == 'lnN':
                    src.cp().process(['HNL']).mass([mass]).AddSyst(
                        cb, NP, 'lnN', ch.SystMap()(1. + abs(1.-lnN_or_Shape_NP[process][NP]['fit_param'])))
                if lnN_or_Shape_NP[process][NP]['type'] == 'Shape':
                    src.cp().process(['HNL']).mass([mass]).AddSyst(
                        cb, NP, 'shape', ch.SystMap()(1.00))
            if VBF != None:
                processVBF = process + 'VBF'
                for NP in VBF[processVBF].keys():
                    if VBF[processVBF][NP]['type'] == 'lnN':
                        src.cp().process(['HNLVBF']).mass([mass]).AddSyst(
                            cb, NP, 'lnN', ch.SystMap()(1. + abs(1.-VBF[processVBF][NP]['fit_param'])))
                    if VBF[processVBF][NP]['type'] == 'Shape':
                        src.cp().process(['HNLVBF']).mass([mass]).AddSyst(
                            cb, NP, 'shape', ch.SystMap()(1.00))

        else:
            for NP in lnN_or_Shape_NP[process].keys():
                if lnN_or_Shape_NP[process][NP]['type'] == 'lnN':
                    src.cp().process([process]).AddSyst(
                        cb, NP, 'lnN', ch.SystMap()(1. + abs(1.-lnN_or_Shape_NP[process][NP]['fit_param'])))
                if lnN_or_Shape_NP[process][NP]['type'] == 'Shape':
                    src.cp().process([process]).AddSyst(
                        cb, NP, 'shape', ch.SystMap()(1.00))
    return

def AddSystematics_tte(cb, var, era, HNLmass = None):
    src = cb.cp()
    src.channel(['tte'])
    if HNLmass != None:
        if HNLmass in vbf_mass_set:
            PathFileNP_channel_VBF = PathFileNP + era + '/' + tag + '/tte/'+var+'_HNLMass'+HNLmass+'VBF.yaml'
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/tte/'+var+'_HNLMass'+HNLmass+'.yaml'
    else:
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/tte/'+var+'.yaml'
    signal = cb.cp().signals().process_set()

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiUncorr_$ERA', 'lnN', ch.SystMap('era')
          (['2018'], 1.015)
          (['2017'], 1.02)
          (['2016'], 1.01)
          (['2016_HIPM'], 1.01))

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiCorr', 'lnN', ch.SystMap('era')
          (['2018'], 1.02)
          (['2017'], 1.009)
          (['2016'], 1.006)
          (['2016_HIPM'], 1.006))
        
    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'TrgSFsingleEleStat', 'lnN', ch.SystMap()(1.03))
    
    with open(PathFileNP_channel, 'r') as file:
        lnN_or_Shape_NP = yaml.load(file, Loader=yaml.FullLoader)
    
    if HNLmass in vbf_mass_set:
        with open(PathFileNP_channel_VBF, 'r') as file:
            lnN_or_Shape_NP_VBF = yaml.load(file, Loader=yaml.FullLoader)
        AddSystNP(lnN_or_Shape_NP, src, cb, VBF = lnN_or_Shape_NP_VBF)
    else:
        AddSystNP(lnN_or_Shape_NP, src, cb)

#------------------------------------------------------------------------------------------------------------------------------

def AddSystematics_tee(cb, var, era, HNLmass = None):
    src = cb.cp()
    src.channel(['tee'])
    if HNLmass != None:
        if HNLmass in vbf_mass_set:
            PathFileNP_channel_VBF = PathFileNP + era + '/' + tag + '/tee/'+var+'_HNLMass'+HNLmass+'VBF.yaml'
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/tee/'+var+'_HNLMass'+HNLmass+'.yaml'
    else:
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/tee/'+var+'.yaml' 
    signal = cb.cp().signals().process_set()

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiUncorr_$ERA', 'lnN', ch.SystMap('era')
          (['2018'], 1.015)
          (['2017'], 1.02)
          (['2016'], 1.01)
          (['2016_HIPM'], 1.01))

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiCorr', 'lnN', ch.SystMap('era')
          (['2018'], 1.02)
          (['2017'], 1.009)
          (['2016'], 1.006)
          (['2016_HIPM'], 1.006))

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'TrgSFsingleEleStat', 'lnN', ch.SystMap()(1.03))
            
    with open(PathFileNP_channel, 'r') as file:
        lnN_or_Shape_NP = yaml.load(file, Loader=yaml.FullLoader)

    if HNLmass in vbf_mass_set:
        with open(PathFileNP_channel_VBF, 'r') as file:
            lnN_or_Shape_NP_VBF = yaml.load(file, Loader=yaml.FullLoader)

        AddSystNP(lnN_or_Shape_NP, src, cb, VBF = lnN_or_Shape_NP_VBF)
    else:
        AddSystNP(lnN_or_Shape_NP, src, cb)
    

#------------------------------------------------------------------------------------------------------------------------------

def AddSystematics_ttm(cb, var, era, HNLmass = None):
    src = cb.cp()
    src.channel(['ttm'])
    if HNLmass != None:
        if HNLmass in vbf_mass_set:
            PathFileNP_channel_VBF = PathFileNP + era + '/' + tag + '/ttm/'+var+'_HNLMass'+HNLmass+'VBF.yaml'
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/ttm/'+var+'_HNLMass'+HNLmass+'.yaml'
    else:
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/ttm/'+var+'.yaml' 
    signal = cb.cp().signals().process_set()

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiUncorr_$ERA', 'lnN', ch.SystMap('era')
          (['2018'], 1.015)
          (['2017'], 1.02)
          (['2016'], 1.01)
          (['2016_HIPM'], 1.01))

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiCorr', 'lnN', ch.SystMap('era')
          (['2018'], 1.02)
          (['2017'], 1.009)
          (['2016'], 1.006)
          (['2016_HIPM'], 1.006))

    with open(PathFileNP_channel, 'r') as file:
        lnN_or_Shape_NP = yaml.load(file, Loader=yaml.FullLoader)

    if HNLmass in vbf_mass_set:
        with open(PathFileNP_channel_VBF, 'r') as file:
            lnN_or_Shape_NP_VBF = yaml.load(file, Loader=yaml.FullLoader)

        AddSystNP(lnN_or_Shape_NP, src, cb, VBF = lnN_or_Shape_NP_VBF)
    else:
        AddSystNP(lnN_or_Shape_NP, src, cb)
#------------------------------------------------------------------------------------------------------------------------------

def AddSystematics_tmm(cb, var, era, HNLmass = None):
    src = cb.cp()
    src.channel(['tmm'])
    if HNLmass != None:
        if HNLmass in vbf_mass_set:
            PathFileNP_channel_VBF = PathFileNP + era + '/' + tag + '/tmm/'+var+'_HNLMass'+HNLmass+'VBF.yaml'
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/tmm/'+var+'_HNLMass'+HNLmass+'.yaml'
    else:
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/tmm/'+var+'.yaml' 
    signal = cb.cp().signals().process_set()

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiUncorr_$ERA', 'lnN', ch.SystMap('era')
          (['2018'], 1.015)
          (['2017'], 1.02)
          (['2016'], 1.01)
          (['2016_HIPM'], 1.01))

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiCorr', 'lnN', ch.SystMap('era')
          (['2018'], 1.02)
          (['2017'], 1.009)
          (['2016'], 1.006)
          (['2016_HIPM'], 1.006))
    
    with open(PathFileNP_channel, 'r') as file:
        lnN_or_Shape_NP = yaml.load(file, Loader=yaml.FullLoader)

    if HNLmass in vbf_mass_set:
        with open(PathFileNP_channel_VBF, 'r') as file:
            lnN_or_Shape_NP_VBF = yaml.load(file, Loader=yaml.FullLoader)

        AddSystNP(lnN_or_Shape_NP, src, cb, VBF = lnN_or_Shape_NP_VBF)
    else:
        AddSystNP(lnN_or_Shape_NP, src, cb)

#------------------------------------------------------------------------------------------------------------------------------

def AddSystematics_tem(cb, var, era, HNLmass = None):
    src = cb.cp()
    src.channel(['tem'])
    if HNLmass != None:
        if HNLmass in vbf_mass_set:
            PathFileNP_channel_VBF = PathFileNP + era + '/' + tag + '/tem/'+var+'_HNLMass'+HNLmass+'VBF.yaml'
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/tem/'+var+'_HNLMass'+HNLmass+'.yaml'
    else:
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/tem/'+var+'.yaml' 
    signal = cb.cp().signals().process_set()

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiUncorr_$ERA', 'lnN', ch.SystMap('era')
          (['2018'], 1.015)
          (['2017'], 1.02)
          (['2016'], 1.01)
          (['2016_HIPM'], 1.01))

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiCorr', 'lnN', ch.SystMap('era')
          (['2018'], 1.02)
          (['2017'], 1.009)
          (['2016'], 1.006)
          (['2016_HIPM'], 1.006))
    
    with open(PathFileNP_channel, 'r') as file:
        lnN_or_Shape_NP = yaml.load(file, Loader=yaml.FullLoader)
    
    if HNLmass in vbf_mass_set:
        with open(PathFileNP_channel_VBF, 'r') as file:
            lnN_or_Shape_NP_VBF = yaml.load(file, Loader=yaml.FullLoader)

        AddSystNP(lnN_or_Shape_NP, src, cb, VBF = lnN_or_Shape_NP_VBF)
    else:
        AddSystNP(lnN_or_Shape_NP, src, cb)

#------------------------------------------------------------------------------------------------------------------------------

def AddSystematics_tee_ss(cb, var, era, HNLmass = None):
    src = cb.cp()
    src.channel(['tee_ss'])
    if HNLmass != None:
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/tee_ss/'+var+'_HNLMass'+HNLmass+'.yaml'
    else:
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/tee_ss/'+var+'.yaml' 
    signal = cb.cp().signals().process_set()

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiUncorr_$ERA', 'lnN', ch.SystMap('era')
          (['2018'], 1.015)
          (['2017'], 1.02)
          (['2016'], 1.01)
          (['2016_HIPM'], 1.01))

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiCorr', 'lnN', ch.SystMap('era')
          (['2018'], 1.02)
          (['2017'], 1.009)
          (['2016'], 1.006)
          (['2016_HIPM'], 1.006))

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'TrgSFsingleEleStat', 'lnN', ch.SystMap()(1.03))
            
    with open(PathFileNP_channel, 'r') as file:
        lnN_or_Shape_NP = yaml.load(file, Loader=yaml.FullLoader)
    
    AddSystNP(lnN_or_Shape_NP, src, cb)

#------------------------------------------------------------------------------------------------------------------------------

def AddSystematics_tee_os(cb, var, era, HNLmass = None):
    src = cb.cp()
    src.channel(['tee_os'])
    if HNLmass != None:
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/tee_os/'+var+'_HNLMass'+HNLmass+'.yaml'
    else:
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/tee_os/'+var+'.yaml' 
    signal = cb.cp().signals().process_set()

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiUncorr_$ERA', 'lnN', ch.SystMap('era')
          (['2018'], 1.015)
          (['2017'], 1.02)
          (['2016'], 1.01)
          (['2016_HIPM'], 1.01))

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiCorr', 'lnN', ch.SystMap('era')
          (['2018'], 1.02)
          (['2017'], 1.009)
          (['2016'], 1.006)
          (['2016_HIPM'], 1.006))

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'TrgSFsingleEleStat', 'lnN', ch.SystMap()(1.03))
            
    with open(PathFileNP_channel, 'r') as file:
        lnN_or_Shape_NP = yaml.load(file, Loader=yaml.FullLoader)
    
    AddSystNP(lnN_or_Shape_NP, src, cb)

#------------------------------------------------------------------------------------------------------------------------------

def AddSystematics_tmm_ss(cb, var, era, HNLmass = None):
    src = cb.cp()
    src.channel(['tmm_ss'])
    if HNLmass != None:
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/tmm_ss/'+var+'_HNLMass'+HNLmass+'.yaml'
    else:
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/tmm_ss/'+var+'.yaml' 
    signal = cb.cp().signals().process_set()

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiUncorr_$ERA', 'lnN', ch.SystMap('era')
          (['2018'], 1.015)
          (['2017'], 1.02)
          (['2016'], 1.01)
          (['2016_HIPM'], 1.01))

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiCorr', 'lnN', ch.SystMap('era')
          (['2018'], 1.02)
          (['2017'], 1.009)
          (['2016'], 1.006)
          (['2016_HIPM'], 1.006))
    
    with open(PathFileNP_channel, 'r') as file:
        lnN_or_Shape_NP = yaml.load(file, Loader=yaml.FullLoader)

    AddSystNP(lnN_or_Shape_NP, src, cb)

#------------------------------------------------------------------------------------------------------------------------------

def AddSystematics_tmm_os(cb, var, era, HNLmass = None):
    src = cb.cp()
    src.channel(['tmm_os'])
    if HNLmass != None:
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/tmm_os/'+var+'_HNLMass'+HNLmass+'.yaml'
    else:
        PathFileNP_channel = PathFileNP + era + '/' + tag + '/tmm_os/'+var+'.yaml' 
    signal = cb.cp().signals().process_set()

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiUncorr_$ERA', 'lnN', ch.SystMap('era')
          (['2018'], 1.015)
          (['2017'], 1.02)
          (['2016'], 1.01)
          (['2016_HIPM'], 1.01))

    src.cp().process(signal + ['TrueLepton']).AddSyst(
        cb, 'lumiCorr', 'lnN', ch.SystMap('era')
          (['2018'], 1.02)
          (['2017'], 1.009)
          (['2016'], 1.006)
          (['2016_HIPM'], 1.006))
    
    with open(PathFileNP_channel, 'r') as file:
        lnN_or_Shape_NP = yaml.load(file, Loader=yaml.FullLoader)

    AddSystNP(lnN_or_Shape_NP, src, cb)


    # src.cp().process(['FakeBackground']).AddSyst(
    #     cb, 'FakeRate', 'lnN', ch.SystMap()(1.3))

    # src.cp().process(['TrueLepton']).AddSyst(
    #     cb, 'MCTruel', 'lnN', ch.SystMap()(1.02))
    
    # src.cp().process(signal + ['TrueLepton', 'FakeBackground']).AddSyst(
    #     cb, 'Trigger', 'lnN', ch.SystMap()(1.01))

    # src.cp().process(signal + ['TrueLepton', 'FakeBackground']).AddSyst(
    #     cb, 'mu_rec', 'lnN', ch.SystMap()(1.005))

    # src.cp().process(signal + ['TrueLepton', 'FakeBackground']).AddSyst(
    #     cb, 'e_rec', 'lnN', ch.SystMap()(1.005))
    
    # src.cp().process(signal + ['TrueLepton', 'FakeBackground']).AddSyst(
    #     cb, 'tau_rec', 'lnN', ch.SystMap()(1.02))
    







    '''
    src.cp().process(['ggH']).AddSyst(
        cb, 'pdf_gg', 'lnN', ch.SystMap()
        (1.097))

    src.cp().process(['qqH', 'WH', 'ZH']).AddSyst(
        cb, 'pdf_qqbar', 'lnN', ch.SystMap('channel', 'era', 'process')
          (['et', 'mt'],  ['7TeV', '8TeV'], ['qqH'],       1.036)
          (['et'],        ['7TeV'],         ['WH', 'ZH'],  1.02)
          (['et'],        ['8TeV'],         ['WH', 'ZH'],  1.04)
          (['mt'],        ['7TeV', '8TeV'], ['WH', 'ZH'],  1.04))

    src.cp().process(['ggH']).AddSyst(
        cb, 'QCDscale_ggH', 'lnN', ch.SystMap('bin_id')
          ([1, 2], 1.08))

    src.cp().process(['ggH']).AddSyst(
        cb, 'QCDscale_ggH1in', 'lnN', ch.SystMap('channel', 'bin_id')
          (['mt'], [3], 1.105)
          (['mt'], [4], 1.095)
          (['mt'], [5], 1.195)
          (['et'], [3], 1.125)
          (['et'], [5], 1.175))

    src.cp().process(['ggH']).AddSyst(
        cb, 'QCDscale_ggH2in', 'lnN', ch.SystMap('channel', 'era', 'bin_id')
          (['mt'], ['7TeV', '8TeV'],  [6], 1.228)
          (['mt'], ['7TeV', '8TeV'],  [7], 1.307)
          (['et'], ['7TeV'],          [6], 1.275)
          (['et'], ['8TeV'],          [6], 1.228)
          (['et'], ['8TeV'],          [7], 1.307))

    src.cp().process(['qqH']).AddSyst(
        cb, 'QCDscale_qqH', 'lnN', ch.SystMap('channel', 'era', 'bin_id')
          (['et', 'mt'], ['7TeV', '8TeV'], [1], 1.022)
          (['et', 'mt'], ['7TeV', '8TeV'], [2], 1.023)
          (['et', 'mt'], ['7TeV', '8TeV'], [3], 1.015)
          (['et', 'mt'], ['7TeV', '8TeV'], [4], 1.013)
          (['et', 'mt'], ['7TeV', '8TeV'], [5], 1.015)
          (['mt'],       ['7TeV', '8TeV'], [6], 1.018)
          (['et'],       ['7TeV'],         [6], 0.981)
          (['et'],       ['8TeV'],         [6], 1.018)
          (['et', 'mt'], ['7TeV', '8TeV'], [7], 1.031))

    src.cp().process(['WH', 'ZH']).AddSyst(
        cb, 'QCDscale_VH', 'lnN', ch.SystMap('channel', 'era', 'bin_id')
          (['mt'], ['7TeV', '8TeV'],  [1, 2],               1.010)
          (['mt'], ['7TeV', '8TeV'],  [3, 4, 5, 6, 7],      1.040)
          (['et'], ['7TeV'],          [1, 2, 3, 5, 6, 7],   1.040)
          (['et'], ['8TeV'],          [1, 2],               1.010)
          (['et'], ['8TeV'],          [3, 5, 6, 7],         1.040))

    src.cp().process(['qqH', 'WH', 'ZH']).AddSyst(
        cb, 'UEPS', 'lnN', ch.SystMap('bin_id')
          ([1], 1.050)
          ([2], 1.060)
          ([3], 1.007)
          ([4], 0.996)
          ([5], 1.006)
          ([6], 0.988)
          ([7], 0.986))
    src.cp().process(['ggH']).AddSyst(
        cb, 'UEPS', 'lnN', ch.SystMap('bin_id')
          ([1], 1.013)
          ([2], 1.028)
          ([3], 0.946)
          ([4], 0.954)
          ([5], 0.983)
          ([6], 0.893)
          ([7], 0.881))

    src.cp().channel(['mt']).process(signal + ['ZTT', 'ZL', 'ZJ', 'TT', 'VV']).AddSyst(
        cb, 'CMS_eff_m', 'lnN', ch.SystMap()(1.02))

    src.cp().channel(['et']).process(signal + ['ZTT', 'ZL', 'ZJ', 'TT', 'VV']).AddSyst(
        cb, 'CMS_eff_e', 'lnN', ch.SystMap()(1.02))

    src.cp().process(signal + ['ZTT', 'TT', 'VV']).AddSyst(
        cb, 'CMS_eff_t_$CHANNEL_$ERA', 'lnN', ch.SystMap()(1.08))

    src.cp().process(signal + ['ZTT', 'TT', 'VV']).AddSyst(
        cb, 'CMS_eff_t_$CHANNEL_medium_$ERA', 'lnN', ch.SystMap('channel', 'era', 'bin_id')
          (['mt'], ['7TeV', '8TeV'],  [1, 3],  1.03)
          (['mt'], ['7TeV', '8TeV'],  [6, 7],  1.01)
          (['et'], ['7TeV'],          [1],     1.03)
          (['et'], ['7TeV'],          [3],     1.08)
          (['et'], ['8TeV'],          [1, 3],  1.03)
          (['et'], ['7TeV', '8TeV'],  [6, 7],  1.01))

    src.cp().process(signal + ['ZTT', 'TT', 'VV']).AddSyst(
        cb, 'CMS_eff_t_$CHANNEL_high_$ERA', 'lnN', ch.SystMap('channel', 'bin_id')
          (['et', 'mt'],  [2, 4, 5],  1.030)
          (['et', 'mt'],  [6],        1.012)
          (['mt'],        [7],        1.015)
          (['et'],        [7],        1.012))

    src.cp().channel(['mt']).process(signal + ['ZTT']).AddSyst(
        cb, 'CMS_scale_t_mutau_$ERA', 'shape', ch.SystMap()(1.00))

    src.cp().channel(['et']).process(signal + ['ZTT']).AddSyst(
        cb, 'CMS_scale_t_etau_$ERA', 'shape', ch.SystMap()(1.00))

    src.cp().channel(['mt']).AddSyst(
        cb, 'CMS_scale_j_$ERA', 'lnN', ch.SystMap('era', 'bin_id', 'process')
          (['7TeV'], [1, 2],  ['ggH'],        0.98)
          (['7TeV'], [1, 2],  ['qqH'],        0.86)
          (['7TeV'], [1, 2],  ['WH', 'ZH'],   0.97)
          (['7TeV'], [1, 2],  ['TT'],         0.99)
          (['7TeV'], [1, 2],  ['VV'],         0.98)
          (['7TeV'], [3],     ['ggH'],        1.05)
          (['7TeV'], [3],     ['qqH'],        1.01)
          (['7TeV'], [3],     ['WH', 'ZH'],   1.05)
          (['7TeV'], [3],     ['VV'],         1.02)
          (['7TeV'], [4, 5],  ['ggH'],        1.03)
          (['7TeV'], [4, 5],  ['qqH'],        1.02)
          (['7TeV'], [4, 5],  ['WH', 'ZH'],   1.03)
          (['7TeV'], [4, 5],  ['TT'],         1.01)
          (['7TeV'], [4, 5],  ['VV'],         1.04)
          (['7TeV'], [6],     ['ggH'],        1.20)
          (['7TeV'], [6],     ['qqH'],        1.05)
          (['7TeV'], [6],     ['WH', 'ZH'],   1.20)
          (['7TeV'], [6],     ['TT'],         1.10)
          (['7TeV'], [6],     ['VV'],         1.15)
          (['8TeV'], [1],     ['ggH'],        0.98)
          (['8TeV'], [1],     ['qqH'],        0.92)
          (['8TeV'], [1],     ['WH', 'ZH'],   0.96)
          (['8TeV'], [1],     ['ZL'],         0.99)
          (['8TeV'], [1],     ['ZJ'],         0.98)
          (['8TeV'], [1],     ['TT'],         0.95)
          (['8TeV'], [1],     ['VV'],         0.98)
          (['8TeV'], [2],     ['ggH'],        0.98)
          (['8TeV'], [2],     ['qqH'],        0.92)
          (['8TeV'], [2],     ['WH', 'ZH'],   0.88)
          (['8TeV'], [2],     ['ZL'],         0.99)
          (['8TeV'], [2],     ['ZJ'],         0.97)
          (['8TeV'], [2],     ['TT'],         0.84)
          (['8TeV'], [2],     ['VV'],         0.97)
          (['8TeV'], [3],     ['ggH'],        1.04)
          (['8TeV'], [3],     ['qqH'],        0.99)
          (['8TeV'], [3],     ['WH', 'ZH'],   1.01)
          (['8TeV'], [3],     ['ZL', 'ZJ'],   1.02)
          (['8TeV'], [3],     ['VV'],         1.03)
          (['8TeV'], [4],     ['ggH'],        1.04)
          (['8TeV'], [4],     ['WH', 'ZH'],   1.03)
          (['8TeV'], [4],     ['ZL', 'ZJ'],   1.02)
          (['8TeV'], [4],     ['VV'],         1.02)
          (['8TeV'], [5],     ['ggH'],        1.02)
          (['8TeV'], [5],     ['WH', 'ZH'],   1.01)
          (['8TeV'], [5],     ['TT'],         0.97)
          (['8TeV'], [5],     ['VV'],         1.03)
          (['8TeV'], [6],     ['ggH'],        1.10)
          (['8TeV'], [6],     ['qqH'],        1.04)
          (['8TeV'], [6],     ['WH', 'ZH'],   1.15)
          (['8TeV'], [6],     ['ZL'],         1.05)
          (['8TeV'], [6],     ['ZJ'],         1.10)
          (['8TeV'], [6],     ['TT'],         1.05)
          (['8TeV'], [6],     ['VV'],         1.08)
          (['8TeV'], [7],     ['ggH'],        1.06)
          (['8TeV'], [7],     ['qqH'],        1.03)
          (['8TeV'], [7],     ['WH', 'ZH'],   1.15)
          (['8TeV'], [7],     ['ZL'],         1.05)
          (['8TeV'], [7],     ['TT'],         1.05)
          (['8TeV'], [7],     ['VV'],         1.10))

    src.cp().channel(['et']).AddSyst(
        cb, 'CMS_scale_j_$ERA', 'lnN', ch.SystMap('era', 'bin_id', 'process')
          (['7TeV'], [1, 2],  ['ggH'],        0.97)
          (['7TeV'], [1, 2],  ['qqH'],        0.85)
          (['7TeV'], [1, 2],  ['WH', 'ZH'],   0.95)
          (['7TeV'], [1, 2],  ['TT'],         0.98)
          (['7TeV'], [1, 2],  ['VV'],         0.97)
          (['7TeV'], [3],     ['ggH'],        1.02)
          (['7TeV'], [3],     ['qqH'],        1.03)
          (['7TeV'], [3],     ['WH', 'ZH'],   1.02)
          (['7TeV'], [3],     ['VV'],         1.01)
          (['7TeV'], [5],     ['ggH'],        1.06)
          (['7TeV'], [5],     ['qqH'],        1.02)
          (['7TeV'], [5],     ['WH', 'ZH'],   1.06)
          (['7TeV'], [5],     ['VV'],         1.02)
          (['7TeV'], [6],     ['ggH'],        1.20)
          (['7TeV'], [6],     ['qqH'],        1.07)
          (['7TeV'], [6],     ['WH', 'ZH'],   1.20)
          (['7TeV'], [6],     ['TT'],         1.10)
          (['7TeV'], [6],     ['VV'],         1.25)
          (['8TeV'], [1],     ['ggH'],        0.98)
          (['8TeV'], [1],     ['qqH'],        0.90)
          (['8TeV'], [1],     ['WH', 'ZH'],   0.96)
          (['8TeV'], [1],     ['ZL'],         0.99)
          (['8TeV'], [1],     ['ZJ'],         0.92)
          (['8TeV'], [1],     ['TT'],         0.95)
          (['8TeV'], [1],     ['VV'],         0.97)
          (['8TeV'], [2],     ['ggH'],        0.98)
          (['8TeV'], [2],     ['qqH'],        0.89)
          (['8TeV'], [2],     ['WH', 'ZH'],   0.95)
          (['8TeV'], [2],     ['ZL'],         0.99)
          (['8TeV'], [2],     ['ZJ'],         0.94)
          (['8TeV'], [2],     ['TT'],         0.84)
          (['8TeV'], [2],     ['VV'],         0.98)
          (['8TeV'], [3],     ['ggH'],        1.01)
          (['8TeV'], [3],     ['qqH'],        0.99)
          (['8TeV'], [3],     ['WH', 'ZH'],   1.01)
          (['8TeV'], [3],     ['VV'],         1.03)
          (['8TeV'], [5],     ['ggH'],        1.02)
          (['8TeV'], [5],     ['WH', 'ZH'],   1.01)
          (['8TeV'], [5],     ['TT'],         0.97)
          (['8TeV'], [5],     ['VV'],         1.03)
          (['8TeV'], [6],     ['ggH'],        1.10)
          (['8TeV'], [6],     ['qqH'],        1.05)
          (['8TeV'], [6],     ['WH', 'ZH'],   1.15)
          (['8TeV'], [6],     ['ZL'],         1.08)
          (['8TeV'], [6],     ['ZJ'],         1.08)
          (['8TeV'], [6],     ['TT'],         1.05)
          (['8TeV'], [6],     ['VV'],         1.10)
          (['8TeV'], [7],     ['ggH'],        1.06)
          (['8TeV'], [7],     ['qqH'],        1.03)
          (['8TeV'], [7],     ['WH', 'ZH'],   1.15)
          (['8TeV'], [7],     ['ZL'],         1.08)
          (['8TeV'], [7],     ['TT'],         1.05)
          (['8TeV'], [7],     ['VV'],         1.10))

    src.cp().AddSyst(
        cb, 'CMS_htt_scale_met_$ERA', 'lnN', ch.SystMap('channel', 'era', 'bin_id', 'process')
          (['et', 'mt'], ['7TeV'], [1, 2, 3, 4, 5, 6], signal,             1.05)
          (['mt'],       ['7TeV'], [1, 2, 3, 4, 5, 6], ['TT', 'W'],        1.07)
          (['et'],       ['7TeV'], [1, 2, 3, 4, 5, 6], ['TT', 'VV'],       1.07)
          (['et', 'mt'], ['7TeV'], [1, 2, 3, 4, 5, 6], ['ZL', 'ZJ'],       1.05)
          (['et', 'mt'], ['8TeV'], [1],                ['TT'],             1.05)
          (['et', 'mt'], ['8TeV'], [1],                ['W'],              1.01)
          (['et', 'mt'], ['8TeV'], [2],                signal,             1.01)
          (['et', 'mt'], ['8TeV'], [2],                ['TT'],             1.04)
          (['et', 'mt'], ['8TeV'], [2],                ['W'],              1.01)
          (['et', 'mt'], ['8TeV'], [2],                ['ZL'],             1.02)
          (['et', 'mt'], ['8TeV'], [3],                signal,             0.99)
          (['mt'],       ['8TeV'], [3],                ['TT'],             1.02)
          (['et'],       ['8TeV'], [3],                ['TT', 'VV', 'ZJ'], 1.01)
          (['et', 'mt'], ['8TeV'], [3],                ['W'],              1.01)
          (['et', 'mt'], ['8TeV'], [3],                ['ZL'],             1.02)
          (['et', 'mt'], ['8TeV'], [4],                signal,             0.99)
          (['et', 'mt'], ['8TeV'], [4],                ['TT'],             1.02)
          (['et', 'mt'], ['8TeV'], [4],                ['W'],              1.01)
          (['et', 'mt'], ['8TeV'], [4],                ['ZL'],             1.03)
          (['mt'],       ['8TeV'], [5],                signal,             0.99)
          (['et'],       ['8TeV'], [5],                signal,             0.98)
          (['et', 'mt'], ['8TeV'], [5],                ['TT'],             1.01)
          (['et', 'mt'], ['8TeV'], [5],                ['W'],              1.03)
          (['mt'],       ['8TeV'], [5],                ['ZL'],             1.02)
          (['et'],       ['8TeV'], [5],                ['ZL'],             1.12)
          (['mt'],       ['8TeV'], [5],                ['ZJ'],             0.98)
          (['et'],       ['8TeV'], [5],                ['ZJ'],             0.97)
          (['et', 'mt'], ['8TeV'], [6],                signal,             0.99)
          (['et', 'mt'], ['8TeV'], [6],                ['TT', 'W'],        1.04)
          (['et', 'mt'], ['8TeV'], [6],                ['ZL', 'ZJ'],       1.03)
          (['et', 'mt'], ['8TeV'], [7],                signal,             0.99)
          (['et', 'mt'], ['8TeV'], [7],                ['TT', 'W'],        1.03)
          (['et', 'mt'], ['8TeV'], [7],                ['ZL', 'ZJ'],       1.03))

    src.cp().AddSyst(
        cb, 'CMS_eff_b_$ERA', 'lnN', ch.SystMap('channel', 'era', 'bin_id', 'process')
          (['mt'],        ['7TeV'], [1, 2, 3, 4, 5, 6],  ['TT'],      0.90)
          (['mt'],        ['7TeV'], [3, 4, 5],           ['VV'],      0.98)
          (['et'],        ['7TeV'], [1],                 ['TT'],      0.97)
          (['et'],        ['7TeV'], [2, 3, 5, 6],        ['TT'],      0.94)
          (['et'],        ['7TeV'], [3, 5],              ['VV'],      0.97)
          (['et'],        ['7TeV'], [6],                 ['VV'],      0.85)
          (['mt'],        ['8TeV'], [1],                 ['TT'],      0.98)
          (['et'],        ['8TeV'], [1],                 ['TT'],      0.96)
          (['et', 'mt'],  ['8TeV'], [2, 3, 4],           ['TT'],      0.96)
          (['mt'],        ['8TeV'], [5, 6, 7],           ['TT'],      0.94)
          (['et'],        ['8TeV'], [5, 6, 7],           ['TT'],      0.96))

    src.cp().process(['ZTT', 'ZL', 'ZJ']).AddSyst(
        cb, 'CMS_htt_zttNorm_$ERA', 'lnN', ch.SystMap()(1.03))

    src.cp().process(['ZTT']).AddSyst(
        cb, 'CMS_htt_extrap_ztt_$BIN_$ERA', 'lnN', ch.SystMap('channel', 'bin_id')
          (['et', 'mt'], [1, 2, 3, 4, 5],   1.05)
          (['et', 'mt'], [6],               1.10)
          (['mt'],       [7],               1.13)
          (['et'],       [7],               1.16))
    src.cp().channel(['et']).bin_id([6]).era(['7TeV']).process(['ZL']).AddSyst(
        cb, 'CMS_htt_extrap_ztt_$BIN_$ERA', 'lnN', ch.SystMap()(1.10))

    src.cp().process(['TT']).AddSyst(
        cb, 'CMS_htt_ttbarNorm_$ERA', 'lnN', ch.SystMap('era', 'bin_id')
          (['7TeV'], [1, 2, 3, 4, 5, 6],    1.08)
          (['8TeV'], [1, 2, 3, 4, 5],       1.10)
          (['8TeV'], [6, 7],                1.08))

    src.cp().process(['TT']).AddSyst(
        cb, 'CMS_htt_ttbarNorm_$BIN_$ERA', 'lnN', ch.SystMap('channel', 'era', 'bin_id')
          (['mt'],  ['7TeV'], [6],     1.20)
          (['mt'],  ['8TeV'], [6, 7],  1.33)
          (['et'],  ['7TeV'], [6],     1.23)
          (['et'],  ['8TeV'], [6, 7],  1.33))

    src.cp().process(['W']).AddSyst(
        cb, 'CMS_htt_WNorm_$BIN_$ERA', 'lnN', ch.SystMap('channel', 'era', 'bin_id')
          (['mt', 'et'], ['7TeV'], [1, 2],    1.20)
          (['mt', 'et'], ['7TeV'], [3, 4],    1.10)
          (['mt'],       ['7TeV'], [5],       1.12)
          (['et'],       ['7TeV'], [5],       1.10)
          (['mt'],       ['7TeV'], [6],       1.20)
          (['et'],       ['7TeV'], [6],       1.50)
          (['mt', 'et'], ['8TeV'], [1, 2],    1.20)
          (['mt'],       ['8TeV'], [3],       1.15)
          (['et'],       ['8TeV'], [3],       1.16)
          (['mt', 'et'], ['8TeV'], [4],       1.11)
          (['mt'],       ['8TeV'], [5],       1.16)
          (['et'],       ['8TeV'], [5],       1.17)
          (['mt'],       ['8TeV'], [6],       1.21)
          (['et'],       ['8TeV'], [6],       1.26)
          (['mt'],       ['8TeV'], [7],       1.51)
          (['et'],       ['8TeV'], [7],       1.56))

    src.cp().process(['VV']).AddSyst(
        cb, 'CMS_htt_DiBosonNorm_$ERA', 'lnN', ch.SystMap()(1.15))

    src.cp().process(['VV']).AddSyst(
        cb, 'CMS_htt_DiBosonNorm_$BIN_$ERA', 'lnN', ch.SystMap('channel', 'era', 'bin_id')
          (['mt'],      ['7TeV'], [6],      1.37)
          (['et'],      ['7TeV'], [6],      1.40)
          (['mt'],      ['8TeV'], [6],      1.50)
          (['mt'],      ['8TeV'], [7],      1.45)
          (['et'],      ['8TeV'], [6],      1.39)
          (['et'],      ['8TeV'], [7],      1.33))

    src.cp().process(['QCD']).AddSyst(
        cb, 'CMS_htt_QCDSyst_$BIN_$ERA', 'lnN', ch.SystMap('channel', 'era', 'bin_id')
          (['mt'],      ['7TeV'], [1, 2, 3, 4, 5],   1.10)
          (['et'],      ['7TeV'], [1, 2],            1.20)
          (['et'],      ['7TeV'], [3, 5],            1.10)
          (['mt'],      ['7TeV'], [6],               1.22)
          (['et'],      ['7TeV'], [6],               1.40)
          (['mt'],      ['8TeV'], [1, 2],            1.06)
          (['mt'],      ['8TeV'], [3, 4, 5],         1.10)
          (['mt'],      ['8TeV'], [6],               1.30)
          (['mt'],      ['8TeV'], [7],               1.70)
          (['et'],      ['8TeV'], [1, 2, 3, 5],      1.10)
          (['et'],      ['8TeV'], [6],               1.30)
          (['et'],      ['8TeV'], [7],               2.00))

    src.cp().channel(['mt']).process(['QCD']).bin_id([3]).AddSyst(
        cb, 'CMS_htt_QCDShape_mutau_1jet_medium_$ERA', 'shape', ch.SystMap()(1.00))
    src.cp().channel(['et']).process(['QCD']).bin_id([3]).AddSyst(
        cb, 'CMS_htt_QCDShape_etau_1jet_medium_$ERA', 'shape', ch.SystMap()(1.00))

    src.cp().channel(['mt']).process(['QCD']).bin_id([4]).AddSyst(
        cb, 'CMS_htt_QCDShape_mutau_1jet_high_lowhiggs_$ERA', 'shape', ch.SystMap()(1.00))

    src.cp().channel(['mt']).process(['QCD']).bin_id([6]).era(['7TeV']).AddSyst(
        cb, 'CMS_htt_QCDShape_mutau_vbf_$ERA', 'shape', ch.SystMap()(1.00))
    src.cp().channel(['et']).process(['QCD']).bin_id([6]).era(['7TeV']).AddSyst(
        cb, 'CMS_htt_QCDShape_etau_vbf_$ERA', 'shape', ch.SystMap()(1.00))

    src.cp().channel(['mt']).process(['QCD']).bin_id([6]).era(['8TeV']).AddSyst(
        cb, 'CMS_htt_QCDShape_mutau_vbf_loose_$ERA', 'shape', ch.SystMap()(1.00))
    src.cp().channel(['et']).process(['QCD']).bin_id([6]).era(['8TeV']).AddSyst(
        cb, 'CMS_htt_QCDShape_etau_vbf_loose_$ERA', 'shape', ch.SystMap()(1.00))

    src.cp().process(['ZJ']).AddSyst(
        cb, 'CMS_htt_ZJetFakeTau_$BIN_$ERA', 'lnN', ch.SystMap('channel', 'era', 'bin_id')
          (['et', 'mt'],  ['7TeV', '8TeV'], [1, 2, 3, 4, 5],   1.20)
          (['mt'],        ['7TeV', '8TeV'], [6],               1.30)
          (['et'],        ['7TeV'],         [6],               1.56)
          (['et'],        ['8TeV'],         [6],               1.20)
          (['mt'],        ['8TeV'],         [7],               1.80)
          (['et'],        ['8TeV'],         [7],               1.65))

    src.cp().channel(['mt']).process(['ZL']).AddSyst(
        cb, 'CMS_htt_ZLeptonFakeTau_$CHANNEL_$ERA', 'lnN', ch.SystMap()(1.30))

    src.cp().channel(['et']).process(['ZL']).bin_id([3, 6, 7]).AddSyst(
        cb, 'CMS_htt_ZLeptonFakeTau_$CHANNEL_low_$ERA', 'lnN',
          ch.SystMap('bin_id')([3], 1.20)([6, 7], 1.06))
    src.cp().channel(['et']).process(['ZL']).bin_id([3, 5]).AddSyst(
        cb, 'CMS_htt_ZLeptonFakeTau_$CHANNEL_met_$ERA', 'lnN',
          ch.SystMap()(1.30))
    src.cp().channel(['et']).process(['ZL']).bin_id([1, 6, 7]).AddSyst(
        cb, 'CMS_htt_ZLeptonFakeTau_$CHANNEL_medium_$ERA', 'lnN',
          ch.SystMap('bin_id')([1], 1.20)([6, 7], 1.08))
    src.cp().channel(['et']).process(['ZL']).bin_id([3]).era(['8TeV']).AddSyst(
        cb, 'CMS_htt_ZLeptonFakeTau_$CHANNEL_medium_$ERA', 'lnN',
          ch.SystMap('bin_id')([3], 1.20))
    src.cp().channel(['et']).process(['ZL']).bin_id([2, 5, 6, 7]).AddSyst(
        cb, 'CMS_htt_ZLeptonFakeTau_$CHANNEL_high_$ERA', 'lnN',
          ch.SystMap('bin_id')([2, 5], 1.20)([6, 7], 1.06))

    src.cp().channel(['mt']).process(['ZL']).AddSyst(
        cb, 'CMS_htt_ZLeptonFakeTau_$BIN_$ERA', 'lnN', ch.SystMap('era', 'bin_id')
          (['7TeV'], [6],       2.00)
          (['8TeV'], [5],       1.26)
          (['8TeV'], [6],       1.70))

    src.cp().channel(['et']).process(['ZL']).AddSyst(
        cb, 'CMS_htt_ZLeptonFakeTau_$BIN_$ERA', 'lnN', ch.SystMap('era', 'bin_id')
          (['8TeV'], [5],       1.30)
          (['8TeV'], [6],       1.70)
          (['8TeV'], [7],       1.74))

    src.cp().channel(['mt']).process(['ZL']).AddSyst(
        cb, 'CMS_htt_ZLScale_mutau_$ERA', 'shape', ch.SystMap()(1.00))
    src.cp().channel(['et']).process(['ZL']).AddSyst(
        cb, 'CMS_htt_ZLScale_etau_$ERA', 'shape', ch.SystMap()(1.00))
    '''