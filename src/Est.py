from qiskit import QuantumCircuit, Aer, execute, IBMQ
import sys
import time
import os
from os.path import exists
from qiskit.providers.aer.noise import NoiseModel
from qiskit import transpile
import EvalMetrics as EM

from QUtil import simCircuit, getFakeBackends, MAX_JOBS


def evalCircuitSim(resultDict, qc, backend):
    '''Run circuit on simulated backend and collect result metrics'''

    backendName = backend.configuration().backend_name

    if qc.name not in resultDict:
        resultDict[qc.name] = []

    print(backendName, backend.configuration().n_qubits)
    resultDict[qc.name].append([backendName, simCircuit(qc, backend)])


def evalCircuitESP(resultDict, qc, backend):
    '''Estimate circuit fidelity via ESP'''

    backendName = backend.configuration().backend_name
    basisGates = backend.configuration().basis_gates

    if qc.name not in resultDict:
        resultDict[qc.name] = []

    print(backendName, backend.configuration().n_qubits)
    unroll_qc = transpile(qc, basis_gates=basisGates,
                          optimization_level=0, backend=backend)

    esp = EM.getESP(unroll_qc, NoiseModel.from_backend(backend))
    resultDict[qc.name].append([backendName, esp])


def simCircuitIBMQ(resultDict, qc, backend):
    '''Run circuit on simulated backend and collect result metrics, TODO: Update this to work with new framework'''

    backendName = backend.configuration().backend_name
    nm = NoiseModel.from_backend(backend)

    ideal_result = execute(
        qc, backend=Aer.get_backend('qasm_simulator'), max_parallel_threads=MAX_JOBS).result()
    noisy_result = execute(qc, backend=Aer.get_backend(
        'qasm_simulator'), noise_model=nm, max_parallel_threads=MAX_JOBS).result()

    PST = EM.computePST(correct_answer=ideal_result.get_counts(
    ).keys(), dict_in=noisy_result.get_counts())

    TVD = EM.computeTVD(dict_ideal=ideal_result.get_counts(
    ), dict_in=noisy_result.get_counts())

    IST = EM.computeIST(correct_answer=ideal_result.get_counts(
    ).keys(), dict_in=noisy_result.get_counts())

    Entropy = EM.computeEntropy(dict_in=noisy_result.get_counts())

    if qc.name not in resultDict:
        resultDict[qc.name] = {}

    if backendName not in resultDict[qc.name]:
        resultDict[qc.name][backendName] = {}

    resultDict[qc.name][backendName] = [
        ideal_result, noisy_result, PST, TVD, IST, Entropy]


def printResultsESP(resultDict, execTime):
    '''Prints metrics per backend on each circuit'''

    header = [
        ("Backend Name", 20),
        ("ESP", 10)
    ]

    def printHeader(header):
        for h in header:
            print("{h:{field_size}}".format(h=h[0], field_size=h[1]), end='')
        print('')

    for file in resultDict.keys():
        print("{} {:.6f}(s) {}".format(
            file, execTime/(10**9), '++++++++++++++'))
        printHeader(header)

        for i in range(len(resultDict[file])):
            backend = resultDict[file][i][0]
            ESP = resultDict[file][i][1]
            print("{:20}{:<10.3f}".format(
                backend, ESP))


def printResultsSim(resultDict, execTime):
    '''Prints metrics per backend on each circuit'''

    header = [
        ("Backend Name", 20),
        ("PST", 10),
        ("TVD", 10),
        ("Entropy", 10),
        ("Swaps", 10),
        ("L2", 10),
        ("Hellinger", 10),
        ("Fitness", 10)
    ]

    def printHeader(header):
        for h in header:
            print("{h:{field_size}}".format(h=h[0], field_size=h[1]), end='')
        print('')

    for file in resultDict.keys():
        print("{} {:.6f}(s) {}".format(
            file, execTime/(10**9), '++++++++++++++'))
        printHeader(header)

        for i in range(len(resultDict[file])):
            backend = resultDict[file][i][0]
            PST = resultDict[file][i][1][0]
            TVD = resultDict[file][i][1][1]
            Entropy = resultDict[file][i][1][2]
            swapCount = resultDict[file][i][1][3]
            L2 = resultDict[file][i][1][4]
            Hellinger = resultDict[file][i][1][5]
            Fitness = resultDict[file][i][1][6]
            print("{:20}{:<10.3f}{:<10.3f}{:<10.3f}{:<10}{:<10.3f}{:<10.3f}{:<10.3f}".format(
                backend, PST, TVD, Entropy, swapCount, L2, Hellinger, Fitness))


def main():
    if len(sys.argv) == 1:
        print("Usage: {} file.qasm".format(sys.argv[0]))
        return 1

    inputFile = sys.argv[1]

    #Read in given circuit
    qc = QuantumCircuit.from_qasm_file(inputFile)
    qc.name = inputFile

    backendsIBMQ = None
    TOKEN_FILE = os.environ.get('IBMQ_TOKEN')

    if TOKEN_FILE != None and exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            TOKEN = f.read()

        print("Token found, using pulling IBMQ data...", end='')
        IBMQ.save_account(TOKEN, overwrite=True)
        IBMQ.load_account()
        provider = IBMQ.providers()[0]
        backendsIBMQ = provider.backends()
        backendsIBMQ = list(filter(
            lambda backend: "simulator" not in backend.configuration().backend_name, backendsIBMQ))
        print("Done")

    else:
        n = 10
        backends = getFakeBackends(qc, n)

    #Simulate circuit on each backend
    timeBegin = time.time_ns()

    resultDictSim = {}
    for backend in backends:
        evalCircuitSim(resultDictSim, qc, backend)
    timeEnd = time.time_ns()

    resultDictSim[qc.name] = sorted(
        resultDictSim[qc.name], key=lambda i: i[1][6], reverse=True)

    #Time taken to simulate
    execTime = timeEnd - timeBegin

    #Output
    printResultsSim(resultDictSim, execTime)

    timeBegin = time.time_ns()

    #Estimate circuit on each backend with ESP
    resultDictESP = {}
    for backend in backends:
        evalCircuitESP(resultDictESP, qc, backend)
    timeEnd = time.time_ns()

    resultDictESP[qc.name] = sorted(
        resultDictESP[qc.name], key=lambda i: i[1], reverse=True)

    #Time taken
    execTime = timeEnd - timeBegin

    #Output
    printResultsESP(resultDictESP, execTime)


if __name__ == "__main__":
    main()
