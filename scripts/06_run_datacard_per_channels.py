import os 
import subprocess 
from utils.helpers import load_cfg_file, parse_range

def main():
    config = load_cfg_file()
    mass_range = parse_range(config['GENERAL']['masses'])
    tag = config['GENERAL']['tag']
    rMax = config['GENERAL'].get('rmax', 1.) 
    isblind = config['GENERAL']['isblind']
    if isblind == 'True':
        is_blind = True
    else:
        is_blind = False
    mass_renorm = int(config['GENERAL']['massrenorm'])
    periods = config['GENERAL']['eras']
    if periods in ['2018','2017','2016', '2016_HIPM']:
        period = periods
    elif periods == ['2018','2017','2016', '2016_HIPM']:
        period = 'All'
    else:
        raise RuntimeError("Unsupported number of periods: {}".format(len(periods)))
        
    if period in ['2018','2017','2016', '2016_HIPM']:
        folderName = "CombineChannels_" + period + "/"
        period_tag = '_' + period
    else:
        folderName = "CombineChannels/"
        period_tag = '_all_years'

    output_folder = os.environ['CMSSW_BASE'] + config['PATH']['output_dir'] + "limits/" + tag + "/" + folderName
    if is_blind:
        output_folder = output_folder + 'blinded/'
    else:
        output_folder = output_folder + 'unblinded/'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    #mass_range = [600, 700, 800, 900, 1000]
    for mass in mass_range:
        if mass < mass_renorm:
            rmax = rMax
        else:
            rmax = rMax
        print('----------------------------------- producing combined limits for mass '+ str(mass) + ' -----------------------------------')
        if is_blind:
            combine_command = "combine -M AsymptoticLimits HNLAnalysis/results/datacards/" +tag+ "/"+folderName+"HNL_" + str(mass) + period_tag +".txt -m "+str(mass)+" -n "+str(mass)+" --rMin=0 --rMax="+str(rmax)+" --run blind"
        else:
            combine_command = "combine -M AsymptoticLimits HNLAnalysis/results/datacards/" +tag+ "/"+folderName+"HNL_" + str(mass) + period_tag +".txt -m "+str(mass)+" -n "+str(mass)+" --rMin=0 --rMax="+str(rmax)
        print("")
        print(">>> " + combine_command)
        p = subprocess.Popen(combine_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print(line.rstrip("\n"))
        print(">>>   higgsCombine"+str(mass)+".AsymptoticLimits.mH"+str(mass)+".root created")
        mv_cmd = "mv higgsCombine"+str(mass)+".AsymptoticLimits.mH"+str(mass)+".root "+ output_folder + "AsymptoticLimit_HNL"+str(mass)+".root "
        print(">>> " + mv_cmd)
        output = subprocess.check_output(mv_cmd, shell=True, stderr=subprocess.STDOUT)
        retval = p.wait()
        print("---------------------------------------------")


if __name__ == '__main__':
    main()

