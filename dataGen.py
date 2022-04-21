#Input: Gate counts, Average node degree
#Output: PST, TVD, Entropy, Swaps
from collections import defaultdict
import os
import datetime
from qiskit import QuantumCircuit, transpile
from Q_Util import simCircuit, getFakeBackends, getGateCounts, getAverageDegree, getGlobalBasisGates
from MachineID import MachineDict
from pandas import DataFrame

GLOBAL_BASIS_GATES = None


def gen_data_entry(qc, backend):
    basisGates = backend.configuration().basis_gates
    coupling_map = backend.configuration().coupling_map
    numQubit = backend.configuration().n_qubits
    name = backend.configuration().backend_name

    out_qc = transpile(qc, basis_gates=basisGates, optimization_level=0)

    dataEntry = getGateCounts(out_qc, basisGates)

    for gate in GLOBAL_BASIS_GATES:
        if gate not in dataEntry:
            dataEntry[gate] = -1

    dataEntry["Machine"] = MachineDict[name]
    dataEntry["AvgDegree"] = getAverageDegree(coupling_map)
    dataEntry["NumQubit"] = numQubit

    outEntries = simCircuit(qc, backend)

    if outEntries == None:
        return None

    dataEntry['PST'] = outEntries[0]
    dataEntry['TVD'] = outEntries[1]
    dataEntry['Entropy'] = outEntries[2]
    dataEntry['Swaps'] = outEntries[3]

    return dataEntry


def createDataSet(directory, outputFile):
    entries = []
    for inputFile in os.listdir(directory):
        print("Running", inputFile, "...")

        #Read in given circuit
        qc = QuantumCircuit.from_qasm_file(directory+inputFile)
        qc.name = inputFile

        n = 1000
        backends = getFakeBackends(qc, n)

        for be in backends:
            e = gen_data_entry(qc, be)
            if e != None:
                entries.append(e)

    mergedDict = defaultdict(list)
    for d in entries:
        for key, value in d.items():
           mergedDict[key].append(value)

    df = DataFrame.from_dict(mergedDict)

    df.to_csv(outputFile, index=False)


def getTS():
    dtObj = datetime.datetime.now()
    ts = "{}-{:02d}-{:02d}_{:02d}:{:02d}.{:02d}".format(dtObj.year, dtObj.month,
                                    dtObj.day, dtObj.hour, dtObj.minute, dtObj.second)

    return ts


def main():
    global GLOBAL_BASIS_GATES
    GLOBAL_BASIS_GATES = getGlobalBasisGates()

    ts = getTS()
    directory = "./qasm/Noise_Benchmarks/"
    outFile = './dataSets_Noise/' + ts + '_data.csv'
    createDataSet(directory, outFile)

    #ts = getTS()
    #directory = "./qasm/SWAP_Benchmarks/"
    #outFile = './dataSets_SWAP/' + ts + '_data.csv'
    #createDataSet(directory, outFile)


if __name__ == "__main__":
	main()
