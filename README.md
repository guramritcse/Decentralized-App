# CS765-Decentralized-App

## Solo Project
| Name | Roll Number |
| --- | --- |
|Guramrit Singh | 210050061|

## Running instructions
- The simulator is written in Python3

### Simulator
- The simulator is run by run.py
- To see the usage of the simulator, run the following command:
```python3 run.py --help```
- The above command will display the following:
```
usage: run.py [-h] [--info] [--N N] [--p P] [--q Q] [--A A] [--T_sim T_SIM] [--I I] [--output_dir OUTPUT_DIR]

Simulation of a Decentralized App using Blockchain

options:
  -h, --help                show this help message and exit
  --info                    Generate info
  --N N                     Number of voters in the DApp
  --p P                     Percentage of very trust worthy voters
  --q Q                     Percentage of malicious voters
  --A A                     Number of articles per user
  --T_sim T_SIM             Simulation time (in ms)
  --I I                     Article interval for getting trustworthiness stats in graph
  --output_dir OUTPUT_DIR   Output directory

```
- Options are given default values, so if you want to run the simulator with the default values, you can simply run:
```python3 run.py```
- The default values are:
    - N: 50
    - p: 50
    - q: 10
    - A: 1
    - T_sim: 200
    - I: 4 
    - output_dir: output
- The output of the simulator will be stored in the output directory. The following files will be generated:
    - info.txt: The info about the miners if --info flag is used
    - trustworthiness.png: The plot representing the trustworthiness of the voters v/s the number of articles they have voted on

## Directory Structure
- This directory contains the following files:
    - [run.py](run.py): The main file to run the simulator
    - [README.md](README.md): This README file
    - [Report.pdf](Report.pdf): The report of this assignment
    - [simulator.py](simulator.py): The simulator class
    - [user.py](user.py): The User class denoting each user of the DApp
    - [dapp.py](dapp.py): The DApp class denoting the DApp
    - [contract.py](contract.py): The SmartContract class denoting the smart contract
    - [smart_contract.sol](smart_contract.sol): The smart contract written in Solidity
    - [results](results): This directory contains the files of the simulation and analysis that have been used in the report
 
## Libraries used and their versions
- simpy (4.1.1)
