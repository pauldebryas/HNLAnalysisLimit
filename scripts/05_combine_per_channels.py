#!/usr/bin/env python
import os 
import yaml
import re

from utils.helpers import load_cfg_file, parse_range

def main():
    config = load_cfg_file()
    tag = config['GENERAL']['tag']
    channels = config['GENERAL']['channels']
    mass_range = parse_range(config['GENERAL']['masses'])
    mass_rang_VBF = parse_range(config['GENERAL']['massesvbf'])
    mass_renorm = int(config['GENERAL']['massrenorm'])
    renorm_value = str(config['GENERAL']['renormvalue'])
    periods = config['GENERAL']['eras']
    if periods in ['2018','2017','2016', '2016_HIPM']:
        period = periods
    elif periods == ['2018','2017','2016', '2016_HIPM']:
        period = 'All'
    else:
        raise RuntimeError("Unsupported number of periods: {}".format(len(periods)))

    if period in ['2018','2017','2016', '2016_HIPM']:
        BDV_file = '/afs/cern.ch/user/p/pdebryas/HNL_analysis/Analysis/PlotKit/F_Exp_limit/results/'+tag+'/BDV_inputs_'+ period +'.yaml'
        output_folder = 'HNLAnalysis/results/datacards/' +tag+ '/CombineChannels_'+ period +'/'
        period_tag = '_' + period
        nametag = period
    else:
        BDV_file = '/afs/cern.ch/user/p/pdebryas/HNL_analysis/Analysis/PlotKit/F_Exp_limit/results/'+tag+'/BDV_inputs.yaml'
        output_folder = 'HNLAnalysis/results/datacards/' +tag+ '/CombineChannels/'
        period_tag = '_all_years'
        nametag = 'AllYears'
    
    with open(BDV_file, 'r') as yaml_file:
        BDV = yaml.load(yaml_file, Loader=yaml.FullLoader)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for mass in mass_range:
        command = 'HiggsAnalysis/CombinedLimit/scripts/combineCards.py '
        for chn in channels:
            command += 'HNL' + chn + nametag +'=HNLAnalysis/results/datacards/' +tag+ '/'+chn+'/'+BDV[chn][mass]+'/' + str(mass) + '/HNL_' + chn + period_tag +'.txt '
        command += '> ' + output_folder + 'HNL_' + str(mass) + period_tag +'.txt --drop_dirname '
        #print(command)
        os.system(command)

        if period in ['2018','2017','2016', '2016_HIPM']:
            outfile = output_folder + "HNL_" + str(mass) + period_tag + ".txt"

            with open(outfile, "r") as f:
                lines = f.readlines()

            # --- Step 1: Build channel map from "Combination of" line
            channel_map = {}
            for line in lines:
                if line.startswith("Combination of "):
                    parts = line.strip().split()
                    for entry in parts[2:]:  # skip "Combination" and "of"
                        # Example entry:
                        # HNLtte2018=HNLAnalysis/results/datacards/FinalProd/tte/mT_tautau/200/HNL_tte_2018.txt
                        if "=" not in entry:
                            continue
                        _, path = entry.split("=", 1)
                        tokens = path.split("/")
                        if len(tokens) >= 6:
                            chn = tokens[4]   # e.g. "tte", "tee", ...
                            subdir = tokens[5]  # e.g. "mT_tautau", "DNNscore"
                            channel_map[chn] = subdir
                    break
            # --- Step 2: Rewrite "shapes" lines with new ROOT paths (preserve spacing)
            new_lines = []
            for line in lines:
                if line.startswith("shapes *") or line.startswith("shapes HNL"):
                    tokens = re.split(r'(\s+)', line)  # split into [word, spaces, word, spaces, ...]
                    # Example: ["shapes", " ", "*", "           ", "HNLtee2018", "  ", "../common/HNL_tee_2018_M40.input.root", " ", ...]
                    if len(tokens) >= 7:
                        name = tokens[4]  # channel tag, e.g. HNLtee2018
                        channel = name.replace("HNL", "").replace(period, "").lower()
                        if channel in channel_map:
                            old_root = tokens[6]
                            filename = os.path.basename(old_root)
                            new_root = "../" + channel + "/" + channel_map[channel] + "/common/" + filename
                            tokens[6] = new_root
                            line = "".join(tokens)  # reassemble with original spacing
                new_lines.append(line)
            #new_lines.append("* autoMCStats 10")
            if mass > mass_renorm:
                new_lines.append("sigScale    rateParam * HNL     " + renorm_value + " [" + renorm_value + "," + renorm_value + "]")
                if mass in mass_rang_VBF:
                    new_lines.append("sigScaleVBF rateParam * HNLVBF  " + renorm_value + " [" + renorm_value + "," + renorm_value + "]")
            # --- Step 3: Save file
            with open(outfile, "w") as f:
                f.writelines(new_lines)
        else:
            outfile = output_folder + "HNL_" + str(mass) + period_tag + ".txt"

            with open(outfile, "r") as f:
                lines = f.readlines()

            if mass > mass_renorm:
                lines.append("sigScale    rateParam * HNL     " + renorm_value + " [" + renorm_value + "," + renorm_value + "]\n")
                if mass in mass_rang_VBF:
                    lines.append("sigScaleVBF rateParam * HNLVBF  " + renorm_value + " [" + renorm_value + "," + renorm_value + "]")

            with open(outfile, "w") as f:
                f.writelines(lines)
if __name__ == '__main__':
    main()

