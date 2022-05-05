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


def genDataEntry(qc, backend):
    basisGates = backend.configuration().basis_gates
    coupling_map = backend.configuration().coupling_map
    numQubit = backend.configuration().n_qubits
    name = backend.configuration().backend_name
    noise = NoiseModel.from_backend(backend)

    #Counting gates prior to mapping to topology
    out_qc = transpile(qc, basis_gates=basisGates, optimization_level=0)

    dataEntry = QUtil.getGateCounts(out_qc, basisGates)

    for gate in QUtil.GLOBAL_BASIS_GATES:
        if gate not in dataEntry:
            dataEntry[gate] = -1

    #Avg Error Metrics
    dataEntry["measureSuccess"] = QUtil.getAvgMeasurementSuccess(noise)
    dataEntry = {**dataEntry, **(QUtil.getAvgGateSuccess(noise))}

    #Topology Metrics
    graph = networkx.DiGraph()
    graph.add_edges_from(coupling_map)

    dataEntry["Machine"] = MachineDict[name]

    dataEntry["GraphDensity"] = networkx.density(graph)
    dataEntry["AvgDegree"] = QUtil.getAverageDegree(coupling_map)
    dataEntry["AvgConnectivity"] = networkx.average_node_connectivity(graph)
    dataEntry["AvgNeighborDegree"] = mean(
        list(networkx.average_neighbor_degree(graph).values()))
    dataEntry["AvgClustering"] = networkx.average_clustering(graph)
    dataEntry["AvgShortestPath"] = networkx.average_shortest_path_length(graph)

    #Circuit Metrics
    dataEntry["NumQubit"] = numQubit
    dataEntry["Depth"] = out_qc.depth()

    QB_metric = QB.QASMetric(out_qc.qasm())
    dataEntry = {**dataEntry, **(QB_metric.evaluate_qasm())}

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


def createDataSet(directory, outputFile):
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


def main():
    QUtil.GLOBAL_BASIS_GATES = QUtil.getGlobalBasisGates()

    ts = QUtil.getTS()
    directory = "./qasm/Noise_Benchmarks/"
    outFile = './dataSets_V2/dataSets_Noise/' + ts + '_data.csv'
    createDataSet(directory, outFile)

    ts = QUtil.getTS()
    directory = "./qasm/SupermarQ/"
    outFile = './dataSets_V2/dataSets_SupermarQ/' + ts + '_data.csv'
    createDataSet(directory, outFile)


if __name__ == "__main__":
	main()
