#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
import CombineHarvester.CombineTools.ch as ch
import os
import importlib
import argparse
from utils.helpers import load_cfg_file

config = load_cfg_file()

# Create the parser
parser = argparse.ArgumentParser(description='Variable position in config file (0,1,2,...)')
parser.add_argument('--period', type=str, required=True, help='period')
parser.add_argument('--VarNb', type=int, required=True, help='An integer variable')
args = parser.parse_args()

var_nb = args.VarNb
era = args.period

print('>> Producing datacards for | channel: var')
for chn in config['GENERAL']['channels']:
    if var_nb >= len(config["DV"][chn]):
        print(' !!!!!! DV_studied for all channels must have the same size !!!!!! ')
        raise Exception('Variable index out of range for channel {}'.format(chn))
    else:
        print('                           | {}    : {}'.format(chn, config["DV"][chn][var_nb]))

cats = [(0, 'signal_region')]
masses = ch.MassesFromRange(config['GENERAL']['masses'])

# New: VBF-only mass subset
vbf_masses = ch.MassesFromRange(config['GENERAL']['massesvbf'])
vbf_mass_set = [m for m in vbf_masses]

cb = ch.CombineHarvester()

print('>> Creating processes and observations...')

for chn in config['GENERAL']['channels']:
    print('            ... for ' + chn)
    var_name = config["DV"][chn][var_nb]
    cb.AddObservations(masses, ['HNL'], [era], [chn], cats)
    cb.AddProcesses(masses, ['HNL'], [era], [chn], config['TH1F']['bkg_procs'], cats, False)
    cb.AddProcesses(masses, ['HNL'], [era], [chn], [config['TH1F']['sig_procs']], cats, True)
    # New: VBF signal only for masses above 600GeV
    cb.AddProcesses(vbf_masses, ['HNL'], [era], [chn], [config['TH1F']['sig_procs_vbf']], cats, True)

print('>> Adding systematic uncertainties...')

for chn in config['GENERAL']['channels']:
    print('            ... for ' + chn)
    module = importlib.import_module('utils.HNLsys')
    AddSystematics = getattr(module, "AddSystematics_" + chn)
    var_name = config["DV"][chn][var_nb]
    for mass in masses:
        AddSystematics(cb, var_name, era, HNLmass= str(mass))

cb_copy = cb.cp()

print('>> Extracting histograms from input root files... ')

for chn in config['GENERAL']['channels']:
    print('            ... for ' + chn)
    var_name = config["DV"][chn][var_nb]
    for mass in masses:
        filepath_ggf = '{}/{}/{}/FakeRate/SignalRegion/TH1_{}_HNLMass{}_HNL.root'.format(
            era, config["GENERAL"]["tag"], chn, var_name, mass)
        file_ggf = os.path.join(config['PATH']['thf1hist_files_dir'], filepath_ggf)
        print(file_ggf)
        cb_copy.cp().channel([chn]).era([era]).backgrounds().mass([mass]).ExtractShapes(
            file_ggf, '$BIN/$PROCESS', '$BIN/$PROCESS_$SYSTEMATIC')
        cb_copy.cp().channel([chn]).era([era]).signals().mass([mass]).process(['HNL']).ExtractShapes(
            file_ggf, '$BIN/$PROCESS$MASS', '$BIN/$PROCESS$MASS_$SYSTEMATIC')

        #New: VBF signal shapes
        if mass in vbf_mass_set:
            filepath_vbf = '{}/{}/{}/FakeRate/SignalRegion/TH1_{}_HNLMass{}VBF_HNL.root'.format(
                era, config["GENERAL"]["tag"], chn, var_name, mass)
            file_vbf = os.path.join(config['PATH']['thf1hist_files_dir'], filepath_vbf)
            print(file_vbf)
            cb_copy.cp().channel([chn]).era([era]).signals().mass([mass]).process(['HNLVBF']).ExtractShapes(
                file_vbf, '$BIN/HNL$MASSVBF', '$BIN/HNL$MASSVBF_$SYSTEMATIC')

print('>> Setting standardised bin names...')
ch.SetStandardBinNames(cb_copy)

print('>> Setting auto MC statitic parameter...')
cb_copy.SetAutoMCStats(cb_copy, 10)

print('>> Writting datacards')

writer = ch.CardWriter('$TAG/$MASS/$ANALYSIS_$CHANNEL_$ERA.txt', '$TAG/common/$ANALYSIS_$CHANNEL_$ERA_M$MASS.input.root')

for chn in cb_copy.channel_set():
    for mass in masses:
        writer.WriteCards(os.environ['CMSSW_BASE'] + config['PATH']['output_dir'] +'/datacards/'+config['GENERAL']['tag']+'/'+chn+'/'+config['DV'][chn][var_nb], cb_copy.cp().channel([chn]).mass([mass]))

print('>> Done!')


