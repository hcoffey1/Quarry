#Input: Gate counts, Average node degree
#Output: PST, TVD, Entropy, Swaps
from qiskit import QuantumCircuit 
from MachineID import MachineDict
from pandas import DataFrame
import pandas as pd
from qiskit.providers.aer.noise import NoiseModel
import QUtil

import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import qasm.QASMBench.metrics.OpenQASMetric as QB

def genSwapDataEntry(qc, backend) -> DataFrame:
    try:
        dataEntry = QUtil.getV2Input(qc, backend)
        dataEntry['Swaps'] = QUtil.getSwapCount(qc, backend) 
    except:
        print("genSwapDataEntry failed, returning None...")
        return None 
    return dataEntry

def genDataEntry(qc, backend) -> DataFrame:
    dataEntry = QUtil.getV2Input(qc, backend)

    outEntries = QUtil.simCircuit(qc, backend)

    if outEntries == None:
        return None 

    #Output Metrics
    dataEntry['PST'] = outEntries['PST']
    dataEntry['TVD'] = outEntries['TVD']
    dataEntry['Entropy'] = outEntries['Entropy']
    dataEntry['Swaps'] = outEntries['Swaps']
    dataEntry['L2'] = outEntries['L2']
    dataEntry['Hellinger'] = outEntries['Hellinger']

    return dataEntry


def createDataSet(directory, outputFile) -> None:
    entries = []
    for inputFile in getListOfFiles(directory):
        print("Running", inputFile, "...")

        #Read in given circuit
        qc = QuantumCircuit.from_qasm_file(inputFile)
        qc.name = inputFile

        n = 1000
        backends = QUtil.getFakeBackends(qc, n)

        for be in backends:
            e = genDataEntry(qc, be)
            if not e.empty:
                entries.append(e)

    df = pd.concat(entries)

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

def getListOfFiles(dirName):
    #https://thispointer.com/python-how-to-get-list-of-files-in-directory-and-sub-directories/
    # create a list of file and sub directories 
    # names in the given directory 

    listOfFile = os.listdir(dirName)
    allFiles = list()

    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        elif entry.endswith('.qasm'):
            allFiles.append(fullPath)
            
    return allFiles

def genSwapData(directory) -> None:
    ts = QUtil.getTS()
    outFile = './dataSets_SWAP/' + ts + '_data.csv'
    entries = []
    i = 1
    inputs = getListOfFiles(directory)
    inputs = list(filter(lambda x: "large" not in x, inputs))
    for inputFile in inputs:
        print("Running", inputFile, "...({}/{})".format(i, len(inputs)))

        #Read in given circuit
        try: 
            qc = QuantumCircuit.from_qasm_file(inputFile)
            qc.name = inputFile

            n = 1000
            backends = QUtil.getFakeBackends(qc, n)

            for be in backends:
                e = genSwapDataEntry(qc, be)
                if type(e) == DataFrame:
                    if not e.empty:
                        entries.append(e)
        except:
            print("Circuit failed to generate data.")

        i += 1

    df = pd.concat(entries)

    df.to_csv(outFile, index=False)

def main():
    QUtil.GLOBAL_BASIS_GATES = QUtil.getGlobalBasisGates()

    #runNoise()
    #runSupermarQ()
    genSwapData("./qasm/QASMBench/")

if __name__ == "__main__":
	main()
