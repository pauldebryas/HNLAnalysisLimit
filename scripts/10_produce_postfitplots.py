#!/usr/bin/env python
import os 
import yaml
import re

from utils.helpers import load_cfg_file, parse_range, executeCommand

def main():
    istest = False  # True for testing purpose (no command executed, just printed out)

    config = load_cfg_file()
    tag = config['GENERAL']['tag']
    isblind = config['GENERAL']['isblind']
    if isblind == 'True':
        is_blind = True
    else:
        is_blind = False
    channels = config['GENERAL']['channels']
    mass_range = parse_range(config['GENERAL']['masses'])
    mass_renorm = int(config['GENERAL']['massrenorm'])
    periods = config['GENERAL']['eras']
    fitregion = config['DataBackgroundPlots']['fitregion']
    rMax = str(config['GENERAL'].get('rmax', 1))  # fallback if not in cfg
    rMin = str(config['GENERAL'].get('rmin', 0))  # fallback if not in cfg
    if periods in ['2018','2017','2016', '2016_HIPM']:
        period = periods
    elif periods == ['2018','2017','2016', '2016_HIPM']:
        raise RuntimeError("Unsupported number of periods: {}".format(len(periods)))

    BDV_file = '/afs/cern.ch/user/p/pdebryas/HNL_analysis/Analysis/PlotKit/F_Exp_limit/results/'+tag+'/BDV_inputs_'+ period +'.yaml'
    period_tag = '_' + period
    
    with open(BDV_file, 'r') as yaml_file:
        BDV = yaml.load(yaml_file, Loader=yaml.FullLoader)

    #channels = ['ttm']
    #mass_range = [50, 60, 100, 250, 350, 400, 450, 500, 600, 700, 800, 900, 1000]
    for chn in channels:
        output_folder = 'HNLAnalysis/results/'+fitregion+'Plots/' +tag+ '/' + period+ '/'+ chn+ '/'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        for mass in mass_range:
            # 1. Convert txt datacard to root workspace
            cmd1 = "text2workspace.py HNLAnalysis/results/datacards/"+tag+"/"+chn+"/"+BDV[chn][mass]+"/"+str(mass)+"/HNL_"+chn + period_tag + ".txt -m "+str(mass)
            executeCommand(cmd1, istest)

            if mass < mass_renorm:
                rmax = rMax
            else:
                rmax = '5'

            # 2. Run Fit Diagnostic
            if is_blind:
                cmd2 = "combine -M FitDiagnostics HNLAnalysis/results/datacards/"+tag+"/"+chn+"/"+BDV[chn][mass]+"/"+str(mass)+"/HNL_"+chn+period_tag + ".root -m "+str(mass)+" --rMin " + rMin + " --rMax "+rmax+" --run blind --saveShapes --saveWithUncertainties -n postFit_blinded_"+chn+"_"+str(mass)
            else:
                cmd2 = "combine -M FitDiagnostics HNLAnalysis/results/datacards/"+tag+"/"+chn+"/"+BDV[chn][mass]+"/"+str(mass)+"/HNL_"+chn+period_tag + ".root -m "+str(mass)+" --rMin " + rMin + " --rMax "+rmax+" --saveShapes --saveWithUncertainties -n postFit_unblinded_"+chn+"_"+str(mass)
            executeCommand(cmd2, istest)

            # 3. Plot python 
            if fitregion == 'postfit':
                cmd3 = "python HNLAnalysis/scripts/utils/postFitPlot.py -i fitDiagnosticspostFit_unblinded_"+chn+"_"+str(mass)+".root --fit postfit-s --tag "+tag+" --dv "+BDV[chn][mass]+" --period "+period+" --mass "+str(mass)+ " --channel "+ chn
            else:
                cmd3 = "python HNLAnalysis/scripts/utils/postFitPlot.py -i fitDiagnosticspostFit_unblinded_"+chn+"_"+str(mass)+".root --fit prefit --tag "+tag+" --dv "+BDV[chn][mass]+" --period "+period+" --mass "+str(mass)+ " --channel "+ chn
            executeCommand(cmd3, istest)

            # 4. move plot to the good folder
            cmd4 = "mv plot_"+chn+"_"+str(mass)+".pdf " + output_folder
            executeCommand(cmd4, istest)

    # 4. move plot to the good folder
    cmd5 = "rm fitDiagnosticspostFit_*.root higgsCombinepostFit_*.root"
    executeCommand(cmd5, istest)

if __name__ == '__main__':
    main()



# "text2workspace.py HNLAnalysis/results/datacards/"+tag+"/"+channel+"/"+BDV[channel][mass]+"/"+mass+"/HNL_"+channel+"_"period_tag"".txt -m "+mass
# combine -M FitDiagnostics HNLAnalysis/results/datacards/"+tag+"/"+channel+"/"+BDV[channel][mass]+"/"+mass+"/HNL_"+channel+"_"period_tag"".root -m "+mass+"" --rMin 0 --rMax "+rmax+" --saveShapes --saveWithUncertainties -n postFit_unblinded
# python postFitPlot.py -i fitDiagnosticspostFit_unblinded_tmm_40.root -o postFitPlots_tmm_40

