from qiskit import QuantumCircuit, Aer, execute, IBMQ
import Eval_Metrics as EM
import sys
import time
import os
from os.path import exists
from qiskit.providers.aer.noise import NoiseModel
from qiskit import transpile

#Machines available from IBM for basic account
from qiskit.test.mock import FakeArmonk, FakeBelem, FakeBogota, FakeManila, FakeQuito, FakeSantiago

def getGateCounts(qc, basisGates):
    """Get counts of each gate type in the given circuit"""

    gateCounts = {}

    for g in basisGates:
        gateCounts[g] = 0
    
    gateCounts["measure"] = 0

    qasm = qc.qasm()

    for l in qasm.split('\n'):
        if len(l) == 0:
            continue

        if "barrier" in l \
                or "QASM" in l \
                or "qreg" in l \
                or "creg" in l \
                or "include" in l:
                    continue
        gate = l.split()[0].split('(')[0]
        if gate not in gateCounts:
            print("Unhandled instruction: ", l)
            exit(1)

        gateCounts[gate] += 1

    return gateCounts

def simCircuit(resultDict, qc, backend):
    '''Run circuit on simulated backend and collect result metrics'''

    backendName = backend.configuration().backend_name
    basisGates = backend.configuration().basis_gates

    if "swap" not in basisGates:
        basisGates = basisGates + ["swap"]

    swap_qc = transpile(qc, basis_gates=basisGates, optimization_level=0, backend=backend)

    swapCount = getGateCounts(swap_qc, basisGates)['swap']

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
        ideal_result, noisy_result, PST, TVD, IST, Entropy, swapCount]

def simCircuitIBMQ(resultDict, qc, backend):
    '''Run circuit on simulated backend and collect result metrics'''

    backendName = backend.configuration().backend_name
    nm = NoiseModel.from_backend(backend)

    ideal_result = execute(
        qc, backend=Aer.get_backend('qasm_simulator')).result()
    noisy_result = execute(qc, backend=Aer.get_backend('qasm_simulator'), noise_model=nm).result()

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
        ("Entropy", 10),
        ("Swaps", 10)
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
            swapCount = resultDict[file][backend][6]
            print("{:20}{:<10.3f}{:<10.3f}{:<10.3f}{:<10.3f}{:<10}".format(
                backend, PST, TVD, IST, Entropy, swapCount))


def main():
    if len(sys.argv) == 1:
        print("Usage: {} file.qasm".format(sys.argv[0]))
        return 1

    backendsIBMQ = None
    TOKEN_FILE = os.environ.get('IBMQ_TOKEN')

    if TOKEN_FILE != None and exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            TOKEN=f.read()

        print("Token found, using pulling IBMQ data...", end='')
        IBMQ.save_account(TOKEN, overwrite=True)
        IBMQ.load_account()
        provider = IBMQ.providers()[0]
        backendsIBMQ = provider.backends()
        backendsIBMQ = list(filter(lambda backend: "simulator" not in backend.configuration().backend_name, backendsIBMQ))
        print("Done")

        #For writing noise models out to compare 
        #nm = NoiseModel.from_backend(backends[0])
        #nm = NoiseModel.from_backend(FakeArmonk())
        #with open("armonk_04_18_22", 'w') as f:
        #    f.write(json.dumps(nm.to_dict()))
        #print(nm.to_dict())
        #print(backends[0].configuration().backend_name)

    else:
        backends = [
            FakeArmonk(),
            FakeBelem(),
            FakeBogota(),
            FakeManila(),
            FakeQuito(),
            FakeSantiago()
        ]

    inputFile = sys.argv[1]

    #Read in given circuit
    qc = QuantumCircuit.from_qasm_file(inputFile)
    qc.name = inputFile

    #Simulate circuit on each backend
    timeBegin = time.time_ns()

    resultDict = {}
    if backendsIBMQ == None:
        for backend in backends:
            if backend.configuration().n_qubits < qc.num_qubits:
                continue

            simCircuit(resultDict, qc, backend)
    else:
        for backend in backendsIBMQ:
            if backend.configuration().n_qubits < qc.num_qubits:
                continue

            simCircuitIBMQ(resultDict, qc, backend)


    timeEnd = time.time_ns()

    #Time taken to simulate
    resultDict[qc.name]['__time'] = timeEnd - timeBegin

    #Output
    printResults(resultDict)


if __name__ == "__main__":
    main()
