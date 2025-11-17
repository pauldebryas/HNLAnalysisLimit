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
    seed = str(config['ImpactStudy']['seed'])

    if period in ['2018','2017','2016', '2016_HIPM']:
        CombineDatacardsPath = 'HNLAnalysis/results/datacards/' + tag + '/CombineChannels_' + period + '/'
        period_tag = '_' + period
    else:
        CombineDatacardsPath = 'HNLAnalysis/results/datacards/' + tag + '/CombineChannels/'
        period_tag = '_all_years'

    save_res_dir = os.environ['CMSSW_BASE'] + config['PATH']['output_dir']+ "gof/"+ tag 
    if not os.path.exists(save_res_dir):
        os.makedirs(save_res_dir)

    txt_file = CombineDatacardsPath + "HNL_" + massToStudy + period_tag + ".txt"
    root_file = CombineDatacardsPath + "HNL_" + massToStudy + period_tag + ".root"
    if is_blind:
        gof_json = "gof_m" + massToStudy + period_tag + ".json"
        gof_output = "gof_m" + massToStudy + period_tag 
    else:
        gof_json = "gof_m" + massToStudy + period_tag + "_unblinded.json"
        gof_output = "gof_m" + massToStudy + period_tag + "_unblinded"

    # 1. Convert txt datacard to root workspace
    cmd1 = "text2workspace.py " + txt_file + " -m " + massToStudy
    executeCommand(cmd1, istest)

    # 2. Test statistic on the Asimov dataset (blinded) or data (unblinded)
    if is_blind:
        cmd2 = "combine -M GoodnessOfFit " + root_file + " -m " + massToStudy + " --algo=saturated -t -1 --expectSignal " + expectedSignal + " -n .gof_m" + massToStudy + "_asimov"
    else:
        cmd2 = "combine -M GoodnessOfFit " + root_file + " -m " + massToStudy + " --algo=saturated -n .gof_m" + massToStudy + "_obs"
    executeCommand(cmd2, istest)

    # 3. Build expected distribution from toys (blinded) or data (unblinded)
    if is_blind:
        cmd3 = "combine -M GoodnessOfFit " + root_file + " -m " + massToStudy + " --algo=saturated -t 500 --expectSignal " + expectedSignal + " -s " + seed + " -n .gof_m" + massToStudy + "_asimov_toys"
    else:
        cmd3 = "combine -M GoodnessOfFit " + root_file + " -m " + massToStudy + " --algo=saturated -t 500 --toysFreq -s " + seed + " -n .gof_m" + massToStudy + "_obs_toys"
    executeCommand(cmd3, istest)

    if is_blind:
        gof_root1 = "higgsCombine.gof_m" + massToStudy + "_asimov.GoodnessOfFit.mH" + massToStudy + ".root"
        gof_root2 = "higgsCombine.gof_m" + massToStudy + "_asimov_toys.GoodnessOfFit.mH" + massToStudy + "." + seed + ".root"
    else:
        gof_root1 = "higgsCombine.gof_m" + massToStudy + "_obs.GoodnessOfFit.mH" + massToStudy + ".root"
        gof_root2 = "higgsCombine.gof_m" + massToStudy + "_obs_toys.GoodnessOfFit.mH" + massToStudy + "." + seed + ".root"

    # 4. To plot the GoF test-statistic distribution, first collect the values of the test-statistic into a json file, and then plots from the json file:
    cmd4 = "combineTool.py -M CollectGoodnessOfFit --input " + gof_root1 + " " + gof_root2 + " -m " + massToStudy + " -o " + gof_json
    executeCommand(cmd4, istest)
    cmd5 = "plotGof.py " + gof_json + " --statistic saturated --mass " + massToStudy + ".0 -o " + gof_output
    executeCommand(cmd5, istest)

    # --- Cleanup temporary combine files (to check if any)
    executeCommand("rm -f higgsCombine.gof_* gof_m*.png", istest)

    # --- Move final results to save_res_dir
    json_dst = os.path.join(save_res_dir, gof_json)
    pdf_dst  = os.path.join(save_res_dir, gof_output + ".pdf")
    executeCommand("mv " + gof_json + " " + json_dst, istest)
    executeCommand("mv " + gof_output + ".pdf" + " " + pdf_dst, istest)

if __name__ == '__main__':
    main()

