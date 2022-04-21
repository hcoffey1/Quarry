from qiskit import Aer, execute, transpile
from statistics import mean
import Eval_Metrics as EM

#Mockup backends
import qiskit.test.mock.backends as BE

#0: Use all available cores
MAX_JOBS = 0


def fitness(PST, TVD, Entropy, Swaps):
    a = 1
    b = 1
    c = 1
    d = 1.0/10
    fitness = 0

    X = PST*a
    Y = (TVD*b+Entropy*c+Swaps*d)

    if Y != 0:
        fitness = X/Y

    return fitness


def getMaxQubit(cm):
    maxQubit = 0
    maxX = (sorted(cm, key=lambda x: x[0], reverse=True)[0][0])
    maxY = (sorted(cm, key=lambda x: x[1], reverse=True)[1][1])
    return max(maxX, maxY)


def getAverageDegree(cm):
    maxQubit = getMaxQubit(cm)

    counts = [0] * (maxQubit+1)

    for e in cm:
        counts[e[0]] += 1
        counts[e[1]] += 1

    return mean(counts)


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

    swap_qc = transpile(qc, basis_gates=basisGates,
                        optimization_level=0, backend=backend)

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

    Fitness = fitness(PST, TVD, Entropy, swapCount)

    return [PST, TVD, Entropy, swapCount, Fitness]


def getFakeBackends(qc):
    backends = []
    import inspect
    for name, obj in inspect.getmembers(BE):
        if "Legacy" not in name \
                and "Alternative" not in name \
                and "V2" not in name \
                and "Fake" in name:
            backends.append(obj())

    backends = list(filter(
        lambda backend: backend.configuration().n_qubits >= qc.num_qubits, backends))

    #Only using first n backends to speed up testing
    n = 10
    backends = backends[:n]

    return backends
