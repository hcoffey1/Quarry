from qiskit import QuantumCircuit, Aer, execute
import Eval_Metrics as EM
import sys
import time

#Machines available from IBM for basic account
from qiskit.test.mock import FakeArmonk, FakeBelem, FakeBogota, FakeManila, FakeQuito, FakeSantiago


def runCircuit(resultDict, qc, backend):
    '''Run circuit on simulated backend and collect result metrics'''

    backendName = backend.configuration().backend_name

    ideal_result = execute(
        qc, backend=Aer.get_backend('qasm_simulator')).result()
    noisy_result = execute(qc, backend=backend).result()

    PST = EM.Compute_PST(correct_answer=ideal_result.get_counts(
    ).keys(), dict_in=noisy_result.get_counts())

    TVD = EM.Compute_TVD(dict_ideal=ideal_result.get_counts(
    ), dict_in=noisy_result.get_counts())

    IST = EM.Compute_IST(correct_answer=ideal_result.get_counts(
    ).keys(), dict_in=noisy_result.get_counts())

    Entropy = EM.Compute_Entropy(dict_in=noisy_result.get_counts())

    if qc.name not in resultDict:
        resultDict[qc.name] = {}

    if backendName not in resultDict[qc.name]:
        resultDict[qc.name][backendName] = {}

    resultDict[qc.name][backendName] = [
        ideal_result, noisy_result, PST, TVD, IST, Entropy]


def printResults(resultDict):
    '''Prints metrics per backend on each circuit'''

    header = [
        ("Backend Name", 20),
        ("PST", 10),
        ("TVD", 10),
        ("IST", 10),
        ("Entropy", 10)
    ]

    def printHeader(header):
        for h in header:
            print("{h:{field_size}}".format(h=h[0], field_size=h[1]), end='')
        print('')

    for file in resultDict.keys():
        print("{} {:.6f}(s) {}".format(
            file, resultDict[file]['__time']/(10**9), '++++++++++++++'))
        printHeader(header)
        for backend in resultDict[file]:
            if backend == '__time':
                continue

            PST = resultDict[file][backend][2]
            TVD = resultDict[file][backend][3]
            IST = resultDict[file][backend][4]
            Entropy = resultDict[file][backend][5]
            print("{:20}{:<10.3f}{:<10.3f}{:<10.3f}{:<10.3f}".format(
                backend, PST, TVD, IST, Entropy))


def main():
    if len(sys.argv) == 1:
        print("Usage: {} file.qasm".format(sys.argv[0]))
        return 1

    inputFile = sys.argv[1]

    backends = [
        FakeArmonk(),
        FakeBelem(),
        FakeBogota(),
        FakeManila(),
        FakeQuito(),
        FakeSantiago()
    ]

    #Read in given circuit
    qc = QuantumCircuit.from_qasm_file(inputFile)
    qc.name = inputFile

    #Simulate circuit on each backend
    timeBegin = time.time_ns()
    resultDict = {}
    for backend in backends:
        if backend.configuration().n_qubits < qc.num_qubits:
            continue

        runCircuit(resultDict, qc, backend)
    timeEnd = time.time_ns()

    #Time taken to simulate
    resultDict[qc.name]['__time'] = timeEnd - timeBegin

    #Output
    printResults(resultDict)


if __name__ == "__main__":
    main()
