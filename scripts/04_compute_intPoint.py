import ROOT
import os
import yaml
import numpy as np
ROOT.gROOT.SetBatch(ROOT.kTRUE)

from utils.helpers import load_cfg_file, parse_range

def get_SignalYield_lim(root_file):
    limits = []
    
    # Open the ROOT file
    myFile = ROOT.TFile.Open(root_file)
    if not myFile or myFile.IsZombie():
        return None

    # Get the 'limit' tree
    tree = myFile.Get('limit')
    if not tree or not isinstance(tree, ROOT.TTree):
        myFile.Close()
        return None

    # Loop through entries in the tree
    for i in range(tree.GetEntries()):
        tree.GetEntry(i)
        limits.append(tree.limit)

    myFile.Close()
    return np.array(limits)

# MAIN
def main():

    config = load_cfg_file()
    mass_range = parse_range(config['GENERAL']['masses'])
    tag = config['GENERAL']['tag']
    periods = config['GENERAL']['eras']
    isnormalizexsec = config['GENERAL']['isnormalizexsec']
    if isnormalizexsec == 'True':
        is_normalize_xsec = True
    else:
        is_normalize_xsec = False
    if periods in ['2018','2017','2016', '2016_HIPM']:
        period = periods
    elif periods == ['2018','2017','2016', '2016_HIPM']:
        period = 'All'
    else:
        raise RuntimeError("Unsupported number of periods: {}".format(len(periods)))

    with open(config['PATH']['xsec_file'], 'r') as yaml_file:
        Xsec = yaml.load(yaml_file, Loader=yaml.FullLoader)


    for chn in config['GENERAL']['channels']:
        print('...computing interaction point for channel '+ chn + ' --------------------------------------------------------------------------------')

        for DV in config['DV'][chn]:
        #for DV in ['DNNscore']: 

            print('For ' +DV+':')

            CombinePath = os.environ['CMSSW_BASE'] + config['PATH']['output_dir'] + "limits/" + tag + "/" + chn + "/" + DV
            save_res_dir = os.environ['CMSSW_BASE'] + config['PATH']['output_dir']+ "intPoints/"+ tag 

            if not os.path.exists(save_res_dir):
                os.makedirs(save_res_dir)

            if period in ['2018','2017','2016', '2016_HIPM']:
                save_res_file = save_res_dir + "/intPoints_"+chn+ "_" + period +".yaml"
            elif period == 'All':
                save_res_file = save_res_dir + "/intPoints_"+chn+ ".yaml"
            else:
                print('period parmeter unknown')


            # Check if the YAML file exists
            if not os.path.exists(save_res_file):
                # If the file doesn't exist, create an empty YAML file
                with open(save_res_file, 'w') as f:
                    yaml.dump({}, f)

            # Read the existing YAML content from the file
            with open(save_res_file, 'r') as file:
                yaml_content = yaml.safe_load(file)
            # Modify the YAML content (for example, adding a new key-value pair)
            yaml_content[DV] = {}

            for HNL_mass in mass_range:
                HNL_mass = str(HNL_mass)
                print('HNL_mass: '+HNL_mass)
                if period in ['2018','2017','2016', '2016_HIPM']:
                    file_path = os.path.join(CombinePath, 'AsymptoticLimit_HNL' + HNL_mass + '_' + period +'.root')
                elif period == 'All':
                    file_path = os.path.join(CombinePath, 'AsymptoticLimit_HNL' + HNL_mass + '.root')
                x_sec = Xsec['HNL_tau_M-' + HNL_mass]['crossSec']
                print('Xsec for V=0.01: '+ str(x_sec))
                SYlim = get_SignalYield_lim(file_path)
                if SYlim is None:
                    print("Skipping due to error in getting limits.")
                    yaml_content[DV][int(HNL_mass)] = None
                else:
                    if is_normalize_xsec:
                        int_points = SYlim*(0.01)**2/x_sec
                    else:
                        int_points = SYlim*(0.01)**2
                    print('Limit in Nevents for V=0.01: '+str(int_points))
                    yaml_content[DV][int(HNL_mass)] = np.array(int_points).tolist()

            # Write the updated YAML content back to the file
            with open(save_res_file, 'w') as file:
                yaml.dump(yaml_content, file)

 
if __name__ == '__main__':
    main()
