from qiskit import Aer, execute, transpile, transpiler, QuantumCircuit
from pandas import DataFrame
from MachineID import MachineDict
from statistics import mean
import Eval_Metrics as EM
import datetime

#Mockup backends
import qiskit.test.mock.backends as BE

#0: Use all available cores
MAX_JOBS = 24


def getV1Input(qc: QuantumCircuit, backend) -> DataFrame:
    """Returns parameters that can be passed to the V1 Predictor model"""
    basisGates = backend.configuration().basis_gates
    name = backend.configuration().backend_name
    coupling_map = backend.configuration().coupling_map
    numQubit = backend.configuration().n_qubits

    out_qc = transpile(qc, basis_gates=basisGates, optimization_level=0)

    output = getGateCounts(out_qc, basisGates)
    output["Machine"] = MachineDict[name]
    output["AvgDegree"] = getAverageDegree(coupling_map)
    output["NumQubit"] = numQubit

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


def simCircuit(qc, backend):
    '''Run circuit on simulated backend and collect result metrics'''

    backendName = backend.configuration().backend_name
    basisGates = backend.configuration().basis_gates
    print(backendName)

    if "swap" not in basisGates:
        basisGates = basisGates + ["swap"]

    try:
        swap_qc = transpile(qc, basis_gates=basisGates,
                            optimization_level=0, backend=backend)
    except transpiler.exceptions.TranspilerError:
        return None

    swapCount = getGateCounts(swap_qc, basisGates)['swap']

    ideal_result = execute(
        qc, backend=Aer.get_backend('qasm_simulator'), max_parallel_threads=MAX_JOBS).result()
    noisy_result = execute(qc, backend=backend,
                           max_parallel_threads=MAX_JOBS).result()

    PST = EM.Compute_PST(correct_answer=ideal_result.get_counts(
    ).keys(), dict_in=noisy_result.get_counts())

    TVD = EM.Compute_TVD(dict_ideal=ideal_result.get_counts(
    ), dict_in=noisy_result.get_counts())

    Entropy = EM.Compute_Entropy(dict_in=noisy_result.get_counts())

    L2 = EM.Compute_L2(noisy_result.get_counts(), ideal_result.get_counts())
    Hellinger = EM.Compute_Hellinger(
        noisy_result.get_counts(), ideal_result.get_counts())

    Fitness = EM.fitness(PST, TVD, Entropy, swapCount, Hellinger, L2)

    return [PST, TVD, Entropy, swapCount, L2, Hellinger, Fitness]


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
