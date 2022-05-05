import numpy as np
from collections import Counter


def fitness(PST, TVD, Entropy, Swaps, Hellinger, L2) -> float:
    a = 1
    b = 1
    c = 1.0/10
    d = 1.0/10
    e = 1
    f = 1

    X = PST*a
    Y = (TVD*b
         + Entropy*c
         + Swaps*d
         + Hellinger*e
         + L2*f)

    fitness = 0
    if Y != 0:
        fitness = X/Y

    return fitness


def _removekey(d, key_list):
    for i in key_list:
        r = dict(d)
        del r[i]

    return r


def normalizeDict(input_dict):

    if sum(input_dict.values()) == 0:
        print('Error, dictionary with total zero elements!!')
    factor = 1.0/sum(input_dict.values())

    for k in input_dict:
        input_dict[k] = input_dict[k]*factor

    return input_dict


def computePST(dict_in, correct_answer) -> float:

    _in = dict_in.copy()
    norm_dict = normalizeDict(_in)
    output = 0
    for ele in correct_answer:
        if ele in norm_dict:
            output += norm_dict[ele]
    pst = output

    return pst


def computeIST(dict_in, correct_answer) -> float:

    #delete correct answers from the input dict
    # DON NOT renormalize
    norm_dict = normalizeDict(dict_in)
    pst = computePST(norm_dict, correct_answer)
    test_in = _removekey(norm_dict, correct_answer)
    dominant_Incorr = Counter(test_in).most_common(1)[0][1]

    return pst/dominant_Incorr


def computeTVD(dict_in, dict_ideal) -> float:

    dict_in = normalizeDict(dict_in)
    dict_ideal = normalizeDict(dict_ideal)
    epsilon = 0.00000000001
    _in1 = Counter(dict_in.copy())
    _in2 = Counter(dict_ideal.copy())
    a = Counter(dict.fromkeys(dict_in, epsilon))
    b = Counter(dict.fromkeys(dict_ideal, epsilon))

    p = dict(Counter(_in1) + Counter(b))
    q = dict(Counter(_in2) + Counter(a))
    p = list(dict(sorted(p.items())).values())
    q = list(dict(sorted(q.items())).values())

    list_of_absdiff = []
    for p_i, q_i in zip(p, q):

        # caluclate the square of the difference of ith distr elements
        s = abs(p_i - q_i)

        # append
        list_of_absdiff.append(s)

    # calculate sum of squares
    soad = sum(list_of_absdiff)

    return soad/2


def computeL2(dict_in, dict_ideal) -> float:

    dict_in = normalizeDict(dict_in)
    dict_ideal = normalizeDict(dict_ideal)
    epsilon = 0.00000000001
    _in1 = Counter(dict_in.copy())
    _in2 = Counter(dict_ideal.copy())
    a = Counter(dict.fromkeys(dict_in, epsilon))
    b = Counter(dict.fromkeys(dict_ideal, epsilon))

    p = dict(Counter(_in1) + Counter(b))
    q = dict(Counter(_in2) + Counter(a))
    p = list(dict(sorted(p.items())).values())
    q = list(dict(sorted(q.items())).values())

    list_of_absdiff = []
    for p_i, q_i in zip(p, q):

        # caluclate the square of the difference of ith distr elements
        s = np.square(p_i - q_i)

        # append
        list_of_absdiff.append(s)

    # calculate sum of squares
    soad = sum(list_of_absdiff)

    return np.sqrt(soad)


def computeHellinger(dict_in, dict_ideal) -> float:

    dict_in = normalizeDict(dict_in)
    dict_ideal = normalizeDict(dict_ideal)
    epsilon = 0.00000000001
    _in1 = Counter(dict_in.copy())
    _in2 = Counter(dict_ideal.copy())
    a = Counter(dict.fromkeys(dict_in, epsilon))
    b = Counter(dict.fromkeys(dict_ideal, epsilon))

    p = dict(Counter(_in1) + Counter(b))
    q = dict(Counter(_in2) + Counter(a))
    p = list(dict(sorted(p.items())).values())
    q = list(dict(sorted(q.items())).values())

    list_of_absdiff = []
    for p_i, q_i in zip(p, q):

        # caluclate the square of the difference of ith distr elements
        s = np.square(np.sqrt(p_i) - np.sqrt(q_i))

        # append
        list_of_absdiff.append(s)

    # calculate sum of squares
    soad = sum(list_of_absdiff)

    return np.sqrt(soad)


def computeEntropy(dict_in) -> float:

    _in1 = normalizeDict(dict(dict_in.copy()))
    epsilon = 0.000001
    P = list(dict(Counter(_in1)).values())
    a = Counter(dict.fromkeys(dict_in, epsilon))
    P = list(dict(Counter(_in1) + Counter(a)).values())
    P = np.asarray(P, dtype=np.float)

    return -1*sum(P*np.log(P))
