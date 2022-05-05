#Input: Gate counts, Average node degree
#Output: PST, TVD, Entropy, Swaps
from collections import defaultdict
from statistics import mean
from qiskit import QuantumCircuit, transpile
from MachineID import MachineDict
from pandas import DataFrame
from qiskit.providers.aer.noise import NoiseModel
import QUtil

import networkx

import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import qasm.QASMBench.metrics.OpenQASMetric as QB


def genDataEntry(qc, backend) -> DataFrame:
    dataEntry = QUtil.getV2Input(qc, backend)

    outEntries = QUtil.simCircuit(qc, backend)

    if outEntries == None:
        return None
    
    #Output Metrics
    dataEntry['PST'] = outEntries[0]
    dataEntry['TVD'] = outEntries[1]
    dataEntry['Entropy'] = outEntries[2]
    dataEntry['Swaps'] = outEntries[3]
    dataEntry['L2'] = outEntries[4]
    dataEntry['Hellinger'] = outEntries[5]

    return dataEntry


def createDataSet(directory, outputFile) -> None:
    entries = []
    for inputFile in os.listdir(directory):
        print("Running", inputFile, "...")

        #Read in given circuit
        qc = QuantumCircuit.from_qasm_file(directory+inputFile)
        qc.name = inputFile

        n = 1000
        backends = QUtil.getFakeBackends(qc, n)

        for be in backends:
            e = genDataEntry(qc, be)
            if e != None:
                entries.append(e)

    mergedDict = defaultdict(list)
    for d in entries:
        for key, value in d.items():
           mergedDict[key].append(value)

    df = DataFrame.from_dict(mergedDict)

    df.to_csv(outputFile, index=False)

def runNoise() -> None:
    ts = QUtil.getTS()
    directory = "./qasm/Noise_Benchmarks/"
    outFile = './dataSets_V2/dataSets_Noise/' + ts + '_data.csv'
    createDataSet(directory, outFile)

def runSupermarQ() -> None:
    ts = QUtil.getTS()
    directory = "./qasm/SupermarQ/"
    outFile = './dataSets_V2/dataSets_SupermarQ/' + ts + '_data.csv'
    createDataSet(directory, outFile)

def main():
    QUtil.GLOBAL_BASIS_GATES = QUtil.getGlobalBasisGates()

    #runNoise()
    #runSupermarQ()

if __name__ == "__main__":
	main()
