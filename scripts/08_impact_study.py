import ROOT
import os
import yaml
import numpy as np
ROOT.gROOT.SetBatch(ROOT.kTRUE)

from utils.helpers import load_cfg_file, executeCommand

# MAIN
def main():
    istest = False  # True for testing purpose (no command executed, just printed out)

    config = load_cfg_file()
    tag = config['GENERAL']['tag']
    isblind = config['GENERAL']['isblind']
    if isblind == 'True':
        is_blind = True
    else:
        is_blind = False
    periods = config['GENERAL']['eras']
    if periods in ['2018','2017','2016', '2016_HIPM']:
        period = periods
    elif periods == ['2018','2017','2016', '2016_HIPM']:
        period = 'All'
    else:
        raise RuntimeError("Unsupported number of periods: {}".format(len(periods)))

    massToStudy = str(config['ImpactStudy']['mass'])
    expectedSignal = str(config['ImpactStudy'].get('expectSignal', 0.022))  # fallback if not in cfg
    rMax = str(config['ImpactStudy'].get('rmax', 0.1))  # fallback if not in cfg
    rMin = str(config['ImpactStudy'].get('rmin', -0.1))  # fallback if not in cfg

    if period in ['2018','2017','2016', '2016_HIPM']:
        CombineDatacardsPath = 'HNLAnalysis/results/datacards/' + tag + '/CombineChannels_' + period + '/'
        period_tag = '_' + period
    else:
        CombineDatacardsPath = 'HNLAnalysis/results/datacards/' + tag + '/CombineChannels/'
        period_tag = '_all_years'

    save_res_dir = os.environ['CMSSW_BASE'] + config['PATH']['output_dir']+ "impact/"+ tag 
    if not os.path.exists(save_res_dir):
        os.makedirs(save_res_dir)

    txt_file = CombineDatacardsPath + "HNL_" + massToStudy + period_tag + ".txt"
    root_file = CombineDatacardsPath + "HNL_" + massToStudy + period_tag + ".root"
    if is_blind:
        impacts_json = "impacts_m" + massToStudy + period_tag + ".json"
        impacts_plot = "impacts" + massToStudy + period_tag
    else:
        impacts_json = "impacts_m" + massToStudy + period_tag + "_unblinded.json"
        impacts_plot = "impacts" + massToStudy + period_tag + "_unblinded"

    # 1. Convert txt datacard to root workspace
    cmd1 = "text2workspace.py " + txt_file + " -m " + massToStudy
    executeCommand(cmd1, istest)

    # 2. Initial fit
    if is_blind:
        cmd2 = "combineTool.py -M Impacts -d " + root_file + " -m " + massToStudy + " --doInitialFit --robustFit 1 --expectSignal " + expectedSignal + " -t -1 --rMax " + rMax + " --rMin " + rMin
    else:
        cmd2 = "combineTool.py -M Impacts -d " + root_file + " -m " + massToStudy + " --doInitialFit --robustFit 1 --rMax " + rMax + " --rMin " + rMin
    executeCommand(cmd2, istest)

    # 3. Perform fits
    if is_blind:
        cmd3 = "combineTool.py -M Impacts -d " + root_file + " -m " + massToStudy + " --robustFit 1 --doFits --expectSignal " + expectedSignal + " -t -1 --rMax " + rMax + " --rMin " + rMin
    else:
        cmd3 = "combineTool.py -M Impacts -d " + root_file + " -m " + massToStudy + " --robustFit 1 --doFits --rMax " + rMax + " --rMin " + rMin
    executeCommand(cmd3, istest)

    # 4. Collect impact results
    if is_blind:
        cmd4 = "combineTool.py -M Impacts -d " + root_file + " -m " + massToStudy + " -o " + impacts_json + " --expectSignal " + expectedSignal + " -t -1 --rMax " + rMax + " --rMin " + rMin
    else:
        cmd4 = "combineTool.py -M Impacts -d " + root_file + " -m " + massToStudy + " -o " + impacts_json + " --rMax " + rMax + " --rMin " + rMin
    executeCommand(cmd4, istest)

    # 5. Plot impacts
    cmd5 = "plotImpacts.py -i " + impacts_json + " -o " + impacts_plot
    executeCommand(cmd5, istest)

    # --- Cleanup temporary combine files
    executeCommand("rm -f higgsCombine_initialFit* higgsCombine_paramFit*", istest)

    # --- Move final results to save_res_dir
    json_dst = os.path.join(save_res_dir, impacts_json)
    pdf_dst  = os.path.join(save_res_dir, impacts_plot + ".pdf")
    executeCommand("mv " + impacts_json + " " + json_dst, istest)
    executeCommand("mv " + impacts_plot + ".pdf " + pdf_dst, istest)

if __name__ == '__main__':
    main()

# Example of commands to be executed for impact study in blinded mode. Unblinded: remove " -t -1" option
# 1 command: text2workspace.py HNLAnalysis/results/datacards/FinalProd/CombineChannels_2018/HNL_300_2018.txt -m 300
# 2 command: combineTool.py -M Impacts -d HNLAnalysis/results/datacards/FinalProd/CombineChannels_2018/HNL_300_2018.root -m 300 --doInitialFit --robustFit 1 --expectSignal 0.022 -t -1 --rMax 0.1
# 3 command: combineTool.py -M Impacts -d HNLAnalysis/results/datacards/FinalProd/CombineChannels_2018/HNL_300_2018.root -m 300 --robustFit 1 --doFits --expectSignal 0.022 -t -1 --rMax 0.1
# 4 command: combineTool.py -M Impacts -d HNLAnalysis/results/datacards/FinalProd/CombineChannels_2018/HNL_300_2018.root -m 300 -o impacts_m300.json --expectSignal 0.022 -t -1 --rMax 0.1
# 5 command: plotImpacts.py -i impacts_m300.json -o impacts300
