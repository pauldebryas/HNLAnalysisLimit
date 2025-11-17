import os
import configparser
import json
import re
import subprocess 

def load_cfg_file():
    ''' Return informations contain in config.ini
    '''
    global_path = os.environ['CMSSW_BASE'] + '/src/HNLAnalysis/'
    config_file = os.path.join(global_path, 'config.ini')
    config = configparser.ConfigParser()
    config.read(config_file)

    # Initialize an empty dictionary to hold the converted configuration
    config_dict = {}
    # Iterate over sections
    for section in config.sections():
        # Initialize a dictionary for the current section
        section_dict = {}
        # Iterate over options in the section
        for option in config.options(section):
            # Get the value for the current option
            value = config.get(section, option)
            # Check if the value is a single line
            if '\n' not in value:
                # If it's a single line, add it directly to the dictionary
                section_dict[option.encode('utf-8')] = value.encode('utf-8')
            else:
                # If it's multiple lines, add it as a list of lines
                section_dict[option.encode('utf-8')] = [unicode_string.encode('utf-8') for unicode_string in value.splitlines()] 
        # Add the section dictionary to the main dictionary
        config_dict[section.encode('utf-8')] = section_dict

    return config_dict

def parse_range(range_str):
    ranges = []
    for part in range_str.split(','):
        if ':' in part:
            start_stop, step = part.split(':')
            step = int(step)
            start, stop = map(int, start_stop.split('-'))
            ranges.extend(range(start, stop + 1, step))
        else:
            ranges.append(int(part))
    return ranges

def process_line(line):
    if line.strip() and not line.startswith(('imax', 'jmax', 'kmax', 'shapes', 'bin', 'observation', 'process', 'rate', '----')):
        parts = re.split(r'(\s+)', line)
        for i in range(len(parts)):
            if parts[i].strip() and re.match(r'^-?\d+(\.\d+)?$', parts[i]):
                try:
                    # Convert part to float and check if less than 1.0001
                    if float(parts[i]) < 1.0001:
                        parts[i] = '-'
                except ValueError:
                    continue
        # Reconstruct the line preserving the spacing
        line = ''.join(parts)
    return line

# EXECUTE datacards
def executeDataCards(channel, era, tag, var, mass, output_dir, rMax, is_blind = True):
    if is_blind:
        combine_command = "combine -M AsymptoticLimits HNLAnalysis/results/datacards/"+tag+"/"+channel+"/"+var+"/"+mass+"/HNL_"+channel+"_"+era+".txt -m "+mass+" -n "+var+" --rMin=0 --rMax="+rMax+" --run blind"
    else:
        combine_command = "combine -M AsymptoticLimits HNLAnalysis/results/datacards/"+tag+"/"+channel+"/"+var+"/"+mass+"/HNL_"+channel+"_"+era+".txt -m "+mass+" -n "+var+" --rMin=0 --rMax="+rMax
    print("")
    print(">>> " + combine_command)
    p = subprocess.Popen(combine_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print(line.rstrip("\n"))
    print(">>>   higgsCombine"+var+".AsymptoticLimits.mH"+mass+".root created")
    mv_cmd = "mv higgsCombine"+var+".AsymptoticLimits.mH"+mass+".root "+ output_dir + "AsymptoticLimit_HNL"+mass+ "_" + era + ".root "
    print(">>> " + mv_cmd)
    output = subprocess.check_output(mv_cmd, shell=True, stderr=subprocess.STDOUT)
    retval = p.wait()
    print("---------------------------------------------")
    return

# EXECUTE datacards for all years
def executeDataCards_allyears(channel, tag, var, mass, output_dir, rMax, is_blind = True):
    if is_blind:
        combine_command = "combine -M AsymptoticLimits HNLAnalysis/results/datacards/"+tag+"/"+channel+"/"+var+"/"+mass+"/HNL_"+channel+"_all_years.txt -m "+mass+" -n "+var+" --rMin=0 --rMax="+rMax+" --run blind"
    else:
        combine_command = "combine -M AsymptoticLimits HNLAnalysis/results/datacards/"+tag+"/"+channel+"/"+var+"/"+mass+"/HNL_"+channel+"_all_years.txt -m "+mass+" -n "+var+" --rMin=0 --rMax="+rMax
    print("")
    print(">>> " + combine_command)
    p = subprocess.Popen(combine_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print(line.rstrip("\n"))
    print(">>>   higgsCombine"+var+".AsymptoticLimits.mH"+mass+".root created")
    mv_cmd = "mv higgsCombine"+var+".AsymptoticLimits.mH"+mass+".root "+ output_dir + "AsymptoticLimit_HNL"+mass+".root "
    print(">>> " + mv_cmd)
    output = subprocess.check_output(mv_cmd, shell=True, stderr=subprocess.STDOUT)
    retval = p.wait()
    print("---------------------------------------------")
    return

def executeCommand(cmd, test=False):
    print(">>> " + cmd)
    if test == False:
        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            print(output)
        except subprocess.CalledProcessError as e:
            print("Command failed with error code", e.returncode)
            print(e.output)
            raise
    print("---------------------------------------------")
    return