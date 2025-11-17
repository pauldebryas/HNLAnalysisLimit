import yaml
import os 

from utils.helpers import load_cfg_file, parse_range, executeDataCards, executeDataCards_allyears

def main():
    config = load_cfg_file()
    mass_range = parse_range(config['GENERAL']['masses'])
    tag = config['GENERAL']['tag']
    rMax = str(config['GENERAL'].get('rmax', 1))  
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
    
    for chn in config['GENERAL']['channels']:
        print('----------------------------------- producing limits for channel '+ chn + ' -----------------------------------')
        output_dir = os.environ['CMSSW_BASE'] + config['PATH']['output_dir'] + "limits/" + tag + "/" + chn 

        for DV in config['DV'][chn]: 
            #output dir where to store root file
            output_dir_DV = output_dir + "/" + DV + "/"

            if not os.path.exists(output_dir_DV):
                os.makedirs(output_dir_DV)

            for mass in mass_range:
                print('Mass: '+ str(mass) + ' // Variable used: ' +DV)
                if period in ['2018','2017','2016', '2016_HIPM']:
                    executeDataCards(chn,period, tag, DV, str(mass), output_dir_DV, rMax, is_blind)
                elif period == 'All':
                    executeDataCards_allyears(chn, tag, DV, str(mass), output_dir_DV, rMax, is_blind)
                else:
                    print('period parmeter unknown')

if __name__ == '__main__':
    main()



# if useBDV:

#     BDV_file =   os.environ['CMSSW_BASE'] + config['GENERAL']['BDV_file']
#     with open(BDV_file, 'r') as yaml_file:
#         BDV = yaml.load(yaml_file, Loader=yaml.FullLoader)

#     #output dir where to store root file
#     output_dir_BDV = output_dir + "/varBDV/"

#     if not os.path.exists(output_dir_BDV):
#         os.makedirs(output_dir_BDV)

#     for mass in mass_range:
#         print('mass: '+ str(mass) + ' // Variable used: ' +BDV[mass][chn])
#         if period in ['2018','2017','2016', '2016_HIPM']:
#             executeDataCards(chn,period, tag, DV, str(mass), output_dir_DV)
#         elif period == 'All':
#             executeDataCards_allyears(chn, tag, DV, str(mass), output_dir_DV)
#         else:
#             print('period parmeter unknown')