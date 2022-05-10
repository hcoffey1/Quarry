#Input: Gate counts, Average node degree
#Output: PST, TVD, Entropy, Swaps
from qiskit import QuantumCircuit 
from MachineID import MachineDict
from pandas import DataFrame
from qiskit.providers.aer.noise import NoiseModel
from qiskit import transpile 
import numpy as np

import matplotlib.pyplot as plt

import pandas as pd
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
    optimizationLevel = 2
    try:
        dataEntry = QUtil.getV2Input(qc, backend)
        swapCount = QUtil.getSwapCount(qc, backend, optimizationLevel)
        if swapCount == None:
            return None
        dataEntry['Swaps'] = swapCount

    #TODO: Investigate what errors are occuring and resolve them so we can get more data entries
    except:
        print("genSwapDataEntry failed, returning None...")
        return None
    return dataEntry


def genDataEntry(qc, backend) -> DataFrame:
    optimizationLevel = 0
    dataEntry = QUtil.getSWAPInput(qc, backend)
    outEntries = QUtil.simCircuit(qc, backend, optimizationLevel)

    if outEntries == None:
        return None

    #Output Metrics
    dataEntry['PST'] = outEntries['PST']
    dataEntry['TVD'] = outEntries['TVD']
    dataEntry['Entropy'] = outEntries['Entropy']

    dataEntry['Swaps'] = outEntries['Swaps']

    dataEntry['L2'] = outEntries['L2']
    dataEntry['Hellinger'] = outEntries['Hellinger']

    unroll_qc = transpile(qc, optimization_level=optimizationLevel, backend=backend)
    esp = QUtil.getESP(unroll_qc, NoiseModel.from_backend(backend))
    dataEntry['ESP'] = esp 

    return dataEntry

def genESPHMDataEntry(qc : QuantumCircuit, backend) -> DataFrame:
    """Collect circuit depth,width -> ESP"""
    optimizationLevel = 0
    dataEntry = {}

    dataEntry['width'] = qc.width()
    dataEntry['depth'] = qc.depth()

    unroll_qc = transpile(qc, optimization_level=optimizationLevel, backend=backend)
    esp = QUtil.getESP(unroll_qc, NoiseModel.from_backend(backend))

    dataEntry['ESP'] = esp 

    return DataFrame(dataEntry, index=[0])

#TODO: Standardize data set creation so we don't have a dozen functions doing this
def createDataSet(directory, outputFile) -> None:
    entries = []
    fileList = getListOfFiles(directory)
    i = 0
    for inputFile in fileList:
        print("Running", inputFile, "...")
        if inputFile in QUtil.FAULT_CIRCUITS:
            print("Faulty circuit, skipping...")
            i+=1
            continue

        #Read in given circuit
        qc = QuantumCircuit.from_qasm_file(inputFile)
        qc.name = inputFile

        n = 10 
        backends = QUtil.getFakeBackends(qc, n)
        j = 0
        for be in backends:
            print("\tRunning", be.configuration().backend_name, "on", inputFile,
                  "(file: {}/{}, be: {}/{})...".format(i, len(fileList), j, len(backends)))
            e = genDataEntry(qc, be)
            if type(e) == DataFrame:
                if not e.empty:
                    entries.append(e)
            j += 1
        i += 1

    df = pd.concat(entries)

    df.to_csv(outputFile, index=False)

def createESPHMDataSet(directory, outputFile) -> None:
    entries = []
    fileList = getListOfFiles(directory)
    fileList = list(filter(lambda x: "large" not in x, fileList))
    i = 0
    for inputFile in fileList:
        print("Running", inputFile, "...")
        if inputFile in QUtil.FAULT_CIRCUITS:
            print("Faulty circuit, skipping...")
            continue

        try:
            #Read in given circuit
            qc = QuantumCircuit.from_qasm_file(inputFile)
            qc.name = inputFile

            n = 1000
            backends = QUtil.getFakeBackends(qc, n)
            j = 0
            for be in backends:
                print("\tRunning", be.configuration().backend_name, "on", inputFile,
                    "(file: {}/{}, be: {}/{})...".format(i, len(fileList), j, len(backends)))
                e = genESPHMDataEntry(qc, be)
                if not e.empty:
                    entries.append(e)
                j += 1
        except:
            print("{} failed to produce data.".format(inputFile))
        i += 1

    df = pd.concat(entries)

    df.to_csv(outputFile, index=False)


def runNoise() -> None:
    ts = QUtil.getTS()
    directory = "./qasm/Noise_Benchmarks/"
    outFile = './dataSets_V2/dataSets_Noise/' + ts + '_data.csv'
    createDataSet(directory, outFile)

def runESPHM() -> None:
    ts = QUtil.getTS()
    directory = "./qasm/QASMBench/"
    outFile = './dataSets_ESP/' + ts + '_data.csv'
    createESPHMDataSet(directory, outFile)


def runSupermarQ() -> None:
    ts = QUtil.getTS()
    directory = "./qasm/SupermarQ/"
    outFile = './dataSets_V2/dataSets_SupermarQ/' + ts + '_data.csv'
    createDataSet(directory, outFile)

def runSmall() -> None:
    ts = QUtil.getTS()
    directory = "./qasm/QASMBench/small/"
    outFile = './dataSets_V2/dataSets_Small/' + ts + '_data.csv'
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
        if inputFile in QUtil.FAULT_CIRCUITS:
            print("Faulty circuit, skipping...")
            continue

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

def drawESPDepthVar(dir):
    files = [os.path.join(dir, f) for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]

    #Read in entries
    dfs = [pd.read_csv(f) for f in files]
    df = pd.concat(dfs)

    #Filter out those with ESP == 1
    #Likely from faulty noise models
    df = df[df.ESP != 1]

    #Filter very large values out, these have an ESP of nearly 0
    df = df[df.depth < 700]

    depthdata = (df['depth'])

    xdata = []
    ydata = []
    for depth in (set(depthdata)):
        xdata.append(depth)
        ydata.append((df[df.depth == depth]['ESP']).var())

    ax = plt.axes()
    ax.scatter(xdata, ydata)

    ax.set_xlabel("Circuit Depth")
    ax.set_ylabel("ESP Variance")
    ax.set_title("Platform ESP Variance vs. Circuit Depth")
    plt.show()



def main():
    QUtil.GLOBAL_BASIS_GATES = QUtil.getGlobalBasisGates()

    runSmall()
    #runNoise()
    #runESPHM()
    #runSupermarQ()
    #genSwapData("./qasm/QASMBench/")
    #drawESPDepthVar("./dataSets_ESP")


if __name__ == "__main__":
	main()
