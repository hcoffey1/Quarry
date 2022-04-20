from ctypes.wintypes import MAX_PATH
from qiskit import QuantumCircuit, Aer, execute, IBMQ
import Eval_Metrics as EM
import sys
import time
import os
from os.path import exists
from qiskit.providers.aer.noise import NoiseModel
from qiskit import transpile

#0: Use all available cores
MAX_JOBS=0

#Mockup backends
import qiskit.test.mock.backends as BE

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
    print(backendName)

    if "swap" not in basisGates:
        basisGates = basisGates + ["swap"]

    swap_qc = transpile(qc, basis_gates=basisGates, optimization_level=0, backend=backend)

    swapCount = getGateCounts(swap_qc, basisGates)['swap']

    ideal_result = execute(
        qc, backend=Aer.get_backend('qasm_simulator'), max_parallel_threads=MAX_JOBS).result()
    noisy_result = execute(qc, backend=backend, max_parallel_threads=MAX_JOBS).result()

    PST = EM.Compute_PST(correct_answer=ideal_result.get_counts(
    ).keys(), dict_in=noisy_result.get_counts())

    TVD = EM.Compute_TVD(dict_ideal=ideal_result.get_counts(
    ), dict_in=noisy_result.get_counts())

    #IST = EM.Compute_IST(correct_answer=ideal_result.get_counts(
    #).keys(), dict_in=noisy_result.get_counts())

    Entropy = EM.Compute_Entropy(dict_in=noisy_result.get_counts())

    if qc.name not in resultDict:
        resultDict[qc.name] = {}

    if backendName not in resultDict[qc.name]:
        resultDict[qc.name][backendName] = {}

    resultDict[qc.name][backendName] = [
        ideal_result, noisy_result, PST, TVD, Entropy, swapCount]

def simCircuitIBMQ(resultDict, qc, backend):
    '''Run circuit on simulated backend and collect result metrics'''

    backendName = backend.configuration().backend_name
    nm = NoiseModel.from_backend(backend)

    ideal_result = execute(
        qc, backend=Aer.get_backend('qasm_simulator'), max_parallel_threads=MAX_JOBS).result()
    noisy_result = execute(qc, backend=Aer.get_backend('qasm_simulator'), noise_model=nm, max_parallel_threads=MAX_JOBS).result()

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
            Entropy = resultDict[file][backend][4]
            swapCount = resultDict[file][backend][5]
            print("{:20}{:<10.3f}{:<10.3f}{:<10.3f}{:<10}".format(
                backend, PST, TVD, Entropy, swapCount))


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
        backends = []
        import inspect
        for name,obj in inspect.getmembers(BE):
            if "Legacy" not in name and "Alternative" not in name and "Fake" in name:
                backends.append(obj())

        backends = list(filter(lambda backend: backend.configuration().n_qubits >= qc.num_qubits, backends))

        #Only using first 10 backends to speed up testing
        backends = backends[:10]

    #for b in backends:
    #    print(b.configuration().backend_name)
    #return


    #Simulate circuit on each backend
    timeBegin = time.time_ns()

    resultDict = {}
    if backendsIBMQ == None:
        for backend in backends:
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
