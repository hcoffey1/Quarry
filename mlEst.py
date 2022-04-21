#Input: Gate counts, Average node degree
#Output: PST, TVD, Entropy, Swaps
from collections import defaultdict
from operator import ge
import tensorflow as tf
import sys
from qiskit import QuantumCircuit, Aer, execute, IBMQ, transpile
from qiskit.providers.aer.noise import NoiseModel
from Q_Util import simCircuit, getFakeBackends, getGateCounts

from pandas import DataFrame

GLOBAL_BASIS_GATES = None


def select_global_basis_gates(backends):
    global GLOBAL_BASIS_GATES

    tmp_gates = []
    for be in backends:
        tmp_gates += be.configuration().basis_gates

    GLOBAL_BASIS_GATES = list(set(tmp_gates))


def gen_data_entry(qc, backend):
    basisGates = backend.configuration().basis_gates

    out_qc = transpile(qc, basis_gates=basisGates, optimization_level=0)

    dataEntry = getGateCounts(out_qc, basisGates)

    for gate in GLOBAL_BASIS_GATES:
        if gate not in dataEntry:
            dataEntry[gate] = -1

    outEntries = simCircuit(qc, backend)

    dataEntry['PST'] = outEntries[0]
    dataEntry['TVD'] = outEntries[1]
    dataEntry['Entropy'] = outEntries[2]
    dataEntry['Swaps'] = outEntries[3]

    return dataEntry


def main():
    if len(sys.argv) == 1:
        print("Usage: {} file.qasm".format(sys.argv[0]))
        return 1

    inputFile = sys.argv[1]

    #Read in given circuit
    qc = QuantumCircuit.from_qasm_file(inputFile)
    qc.name = inputFile

    n = 10
    backends = getFakeBackends(qc, n)
    select_global_basis_gates(backends)
    print(GLOBAL_BASIS_GATES)

    entries = []
    for be in backends:
        entries.append(gen_data_entry(qc, be))

    mergedDict = defaultdict(list)
    for d in entries:
        for key, value in d.items():
           mergedDict[key].append(value)

    print(DataFrame.from_dict(mergedDict))

if __name__ == "__main__":
	main()
