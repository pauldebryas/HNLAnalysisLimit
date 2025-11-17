# Limit code

## How to install

Setup the Combine repository:
```sh
cmssw-el7
cmsrel CMSSW_11_3_4
cd CMSSW_11_3_4/src
cmsenv
git -c advice.detachedHead=false clone --depth 1 --branch v9.2.1 https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
scramv1 b clean; scramv1 b -j$(nproc --ignore=2)
```

Then clone this repository in CMSSW_11_3_4/src

## How to run
```sh
cd CMSSW_11_3_4/src/
cmssw-el7
cmsenv
```
Setup the parameter in the config.ini file.
Then you can create the datacards:
```sh
python HNLAnalysis/scripts/01_create_datacards.py --period 2017 --VarNb 0
```
or if you want to add VBF
```sh
python HNLAnalysis/scripts/01bis_create_datacards.py --period 2017 --VarNb 0 
```

```sh
python HNLAnalysis/scripts/02_combine_per_years.py 
python HNLAnalysis/scripts/03_run_datacard.py
python HNLAnalysis/scripts/04_compute_intPoint.py
```
Go to PlotKit to compute BDV

```sh
python HNLAnalysis/scripts/05_combine_per_channels.py
python HNLAnalysis/scripts/06_run_datacard_per_channels.py
python HNLAnalysis/scripts/07_compute_intPoint_per_channels.py
python HNLAnalysis/scripts/08_impact_study.py
python HNLAnalysis/scripts/09_GOF_study.py
python HNLAnalysis/scripts/10_produce_postfitplots.py 
```