#!/usr/bin/env python
import os 

from utils.helpers import load_cfg_file, parse_range

def main():
    config = load_cfg_file()

    tag = config['GENERAL']['tag']
    periods = config['GENERAL']['eras']
    channels = config['GENERAL']['channels']
    mass_range = parse_range(config['GENERAL']['masses'])

    for mass in mass_range:
        for chn in channels:
            for var_nb in range(len(config["DV"][chn])):
                command = 'HiggsAnalysis/CombinedLimit/scripts/combineCards.py '
                for period in periods:
                    command += 'HNL' + chn + period+ '=HNLAnalysis/results/datacards/' +tag+ '/'+chn+'/'+config["DV"][chn][var_nb]+'/' + str(mass) + '/HNL_' + chn + '_' +period + '.txt '
                command += '> HNLAnalysis/results/datacards/' +tag+ '/'+chn+'/'+config["DV"][chn][var_nb]+'/' + str(mass) + '/HNL_' + chn + '_all_years.txt'
                os.system(command)

if __name__ == '__main__':
    main()