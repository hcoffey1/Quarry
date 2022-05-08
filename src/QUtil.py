from typing import Dict
from numpy import average
from qiskit import Aer, execute, transpile, transpiler, QuantumCircuit
from qiskit.providers.aer.noise import NoiseModel
from pandas import DataFrame
from MachineID import MachineDict
from statistics import mean
import EvalMetrics as EM
import datetime
import networkx
import os
import inspect
import sys
import matplotlib.pyplot as plt

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

#Mockup backends
import qiskit.test.mock.backends as BE
import qasm.QASMBench.metrics.OpenQASMetric as QB


#0: Use all available cores
MAX_JOBS = 24
GLOBAL_BASIS_GATES = None


def drawWeightedGraph(G: networkx.Graph) -> None:
    """Visualize weighted Networkx graph"""
    pos = networkx.spring_layout(G)
    networkx.draw(G, pos, with_labels=True)
    labels = networkx.get_edge_attributes(G, 'weight')
    networkx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    fig = plt.gcf()
    fig.suptitle(G.name)

    fileName = (G.name.split('.')[0])
    plt.savefig('./img/cxgraph/{}.png'.format(fileName))


def getCxGraph(qc: QuantumCircuit) -> networkx.Graph:
    """Nodes are Qubits, Edges are CX, Weights are Qubit number distances"""
    G = networkx.Graph()
    G.name = qc.name
    for instruction, qargs, cargs in qc._data:
        if len(qargs) > 1:
            qb = ((qargs[0]._index), (qargs[1]._index))
            G.add_edge(qb[0], qb[1], weight=abs(qb[0]-qb[1]))
    return G


def getGraphMetrics(G: networkx.Graph, label: str) -> dict:
    """Calculate metrics from Networkx graph"""
    output = {}
    output["{}GraphDensity".format(label)] = networkx.density(G)
    output["{}AvgConnectivity".format(
        label)] = networkx.average_node_connectivity(G)
    output["{}AvgNeighborDegree".format(label)] = mean(
        list(networkx.average_neighbor_degree(G).values()))
    output["{}AvgClustering".format(label)] = networkx.average_clustering(G)

    if label != "CX":
        output["{}AvgShortestPath".format(
            label)] = networkx.average_shortest_path_length(G)
    else:
        output["{}AvgShortestPath".format(
            label)] = 0 

    return output


def getCxGraphMetrics(G: networkx.Graph) -> dict:
    """Calculate graph metrics and weight metrics"""
    output = getGraphMetrics(G, 'CX')
    output['CXAverageDegree'] = getAverageDegree(G.edges)

    weights = []
    for e in G.edges:
        weights.append(G[e[0]][e[1]]['weight'])

    output['CXAverageWeight'] = average(weights)
    output['CXMaxWeight'] = max(weights)
    output['CXMinWeight'] = min(weights)

    return output


def getAvgMeasurementSuccess(noise: NoiseModel) -> float:
    sum = 0

    readoutErrors = noise._local_readout_errors
    if len(readoutErrors.keys()) == 0:
        return 1

    for qe in readoutErrors.values():
        m0e = (qe.probabilities[0][0])
        m1e = (qe.probabilities[1][1])
        sr = (m0e + m1e)/2
        sum += sr

    return sum*1.0/len(readoutErrors.keys())


def getAvgGateSuccess(noise: NoiseModel) -> dict:
    gateSuccess = {}

    for gate in GLOBAL_BASIS_GATES:
        key = gate + "Success"

        if gate not in noise._noise_instructions:
            gateSuccess[key] = 1
            continue

        local_errors = noise._local_quantum_errors[gate]

        gateSuccess[key] = 0
        for qb in local_errors:
            gateSuccess[key] += max(local_errors[qb].probabilities)

        gateSuccess[key] /= len(local_errors.keys())

    return gateSuccess


def getESP(qc: QuantumCircuit, noise: NoiseModel) -> float:
    """
    Estimated Success Probability
    https://dl.acm.org/doi/abs/10.1145/3386162
    """
    esp = 1

    for instruction, qargs, cargs in qc._data:
        if instruction.name not in noise._noise_instructions:
            continue

        if len(qargs) > 1:
            qb = ((qargs[0]._index), (qargs[1]._index))
        else:
            qb = (qargs[0]._index, )

        if instruction.name == 'measure':
            m0e = (noise._local_readout_errors[qb].probabilities[0][0])
            m1e = (noise._local_readout_errors[qb].probabilities[1][1])
            sr = (m0e + m1e)/2
        else:
            #Assume that highest probability is for success
            sr = max(
                noise._local_quantum_errors[instruction.name][qb].probabilities)
        esp *= sr

    return esp


def getV1Input(qc: QuantumCircuit, backend) -> DataFrame:
    """Returns parameters that can be passed to the V1 Predictor model"""
    basisGates = backend.configuration().basis_gates
    name = backend.configuration().backend_name
    coupling_map = backend.configuration().coupling_map
    numQubit = backend.configuration().n_qubits

    out_qc = transpile(qc, basis_gates=basisGates, optimization_level=0)

    output = getGateCounts(out_qc, basisGates)

    for gate in GLOBAL_BASIS_GATES:
        if gate not in output:
            output[gate] = -1

    output["Machine"] = MachineDict[name]
    output["AvgDegree"] = getAverageDegree(coupling_map)
    output["NumQubit"] = numQubit

    return DataFrame(output, index=[0])


def getV2Input(qc: QuantumCircuit, backend) -> DataFrame:
    basisGates = backend.configuration().basis_gates
    coupling_map = backend.configuration().coupling_map
    numQubit = backend.configuration().n_qubits
    name = backend.configuration().backend_name
    noise = NoiseModel.from_backend(backend)

    #Counting gates prior to mapping to topology
    out_qc = transpile(qc, basis_gates=basisGates, optimization_level=0)

    output = getGateCounts(out_qc, basisGates)

    for gate in GLOBAL_BASIS_GATES:
        if gate not in output:
            output[gate] = -1

    #Avg Error Metrics
    output["measureSuccess"] = getAvgMeasurementSuccess(noise)
    output = {**output, **(getAvgGateSuccess(noise))}

    #Topology Metrics
    graph = networkx.DiGraph()
    graph.add_edges_from(coupling_map)

    output["Machine"] = MachineDict[name]
    output["QCAvgDegree"] = getAverageDegree(coupling_map)

    output = {**output, **(getGraphMetrics(graph, 'QC'))}

    output = {**output, **(getCxGraphMetrics(getCxGraph(qc)))}

    #Circuit Metrics
    output["NumQubit"] = numQubit
    output["Depth"] = out_qc.depth()

    QB_metric = QB.QASMetric(out_qc.qasm())
    output = {**output, **(QB_metric.evaluate_qasm())}

    return DataFrame(output, index=[0])


def genMachineIDs():
    backends = extractBackends()
    i = 0
    for be in backends:
        print("\""+be.configuration().backend_name+"\"", ':', i, ',')
        i += 1


def getTS() -> str:
    dtObj = datetime.datetime.now()
    ts = "{}-{:02d}-{:02d}--{:02d}-{:02d}-{:02d}".format(dtObj.year, dtObj.month,
                                                         dtObj.day, dtObj.hour, dtObj.minute, dtObj.second)
    return ts


def getMaxQubit(cm) -> int:
    maxX = (sorted(cm, key=lambda x: x[0], reverse=True)[0][0])
    maxY = (sorted(cm, key=lambda x: x[1], reverse=True)[1][1])
    return max(maxX, maxY)


def getAverageDegree(cm) -> float:
    maxQubit = getMaxQubit(cm)
    return len(cm)/(1.0*maxQubit+1)


def getGateCounts(qc, basisGates):
    """Get counts of each gate type in the given circuit"""

    gateCounts = {}

    ignoredInstructions = ['barrier']

    for g in basisGates:
        gateCounts[g] = 0

    gateCounts["measure"] = 0

    for instruction, qargs, cargs in qc._data:
        if instruction.name in ignoredInstructions:
            continue

        if instruction.name not in gateCounts:
            print("Unhandled instruction: ", instruction.name)
            raise RuntimeError

        gateCounts[instruction.name] += 1

    return gateCounts


def getSwapCount(qc, backend):
    '''Get count of SWAP operations added for circuit on given backend.'''
    basisGates = backend.configuration().basis_gates
    if "swap" not in basisGates:
        basisGates = basisGates + ["swap"]

    try:
        swap_qc = transpile(qc, basis_gates=basisGates,
                            optimization_level=0, backend=backend)
    except transpiler.exceptions.TranspilerError:
        return None

    return getGateCounts(swap_qc, basisGates)['swap']


def simCircuit(qc, backend):
    '''Run circuit on simulated backend and collect result metrics'''

    backendName = backend.configuration().backend_name
    print(backendName)

    outDict = {}
    outDict["Swaps"] = getSwapCount(qc, backend)

    ideal_result = execute(
        qc, backend=Aer.get_backend('qasm_simulator'), max_parallel_threads=MAX_JOBS).result()
    noisy_result = execute(qc, backend=backend,
                           max_parallel_threads=MAX_JOBS).result()

    outDict["PST"] = EM.computePST(correct_answer=ideal_result.get_counts(
    ).keys(), dict_in=noisy_result.get_counts())

    outDict["TVD"] = EM.computeTVD(dict_ideal=ideal_result.get_counts(
    ), dict_in=noisy_result.get_counts())

    outDict["Entropy"] = EM.computeEntropy(dict_in=noisy_result.get_counts())

    outDict["L2"] = EM.computeL2(
        noisy_result.get_counts(), ideal_result.get_counts())
    outDict["Hellinger"] = EM.computeHellinger(
        noisy_result.get_counts(), ideal_result.get_counts())

    outDict["Fitness"] = EM.fitness(outDict["PST"], outDict["TVD"], outDict["Entropy"],
                                    outDict["Swaps"], outDict["Hellinger"], outDict["L2"])

    return outDict


def extractBackends():
    backends = []
    import inspect
    for name, obj in inspect.getmembers(BE):
        if "Legacy" not in name \
                and "Alternative" not in name \
                and "V2" not in name \
                and "Fake" in name:
            backends.append(obj())

    return backends


def getGlobalBasisGates():
    tmp_gates = []
    for be in extractBackends():
        tmp_gates += be.configuration().basis_gates

    return list(set(tmp_gates))


def getFakeBackends(qc, n):
    #Filter out backends with too few qubits for circuit
    lb = qc.num_qubits
    backends = list(
        filter(lambda backend: backend.configuration().n_qubits >= lb, extractBackends()))

    #Sort backends by qubit count
    backends = list(sorted(backends, key=lambda i: i.configuration().n_qubits))

    #Return first n backends
    backends = backends[:n]
    return backends
