import numpy as np

from collections import Counter
def removekey(d, key_list):
    for i in key_list:
        r = dict(d)
        del r[i]
    
    return r

def normalize_dict(input_dict):
 
    
    if sum(input_dict.values()) == 0:
        print('Error, dictionary with total zero elements!!')    
    factor=1.0/sum(input_dict.values())
 
    
    for k in input_dict:
        input_dict[k] = input_dict[k]*factor
    
    return input_dict 
    
def Compute_PST(dict_in, correct_answer):
    
    _in = dict_in.copy()
    norm_dict=normalize_dict(_in)
    output=0
    for ele in correct_answer:
        if ele in norm_dict:
            output+=norm_dict[ele] 
    pst = output
    
    return pst

def Compute_IST(dict_in, correct_answer):
    
    #delete correct answers from the input dict 
    # DON NOT renormalize 
    norm_dict=normalize_dict(dict_in)
    pst = Compute_PST(norm_dict, correct_answer)
    test_in=removekey(norm_dict, correct_answer)
    dominant_Incorr=Counter(test_in).most_common(1)[0][1]         
    
    return pst/dominant_Incorr

def Compute_TVD(dict_in,dict_ideal):
    
    dict_in = normalize_dict(dict_in)
    dict_ideal=normalize_dict(dict_ideal)
    epsilon = 0.00000000001
    _in1 = Counter(dict_in.copy())
    _in2 = Counter(dict_ideal.copy())
    a = Counter(dict.fromkeys(dict_in, epsilon))
    b = Counter(dict.fromkeys(dict_ideal, epsilon))

    p = dict(Counter(_in1) + Counter(b))
    q = dict(Counter(_in2) + Counter(a))
    p=list(dict(sorted(p.items())).values())
    q=list(dict(sorted(q.items())).values())

    list_of_absdiff = []
    for p_i, q_i in zip(p, q):

        # caluclate the square of the difference of ith distr elements
        s = abs(p_i - q_i)

        # append 
        list_of_absdiff.append(s)

    # calculate sum of squares
    soad = sum(list_of_absdiff)    

    return soad/2

def Compute_L2(dict_in,dict_ideal):
    
    dict_in = normalize_dict(dict_in)
    dict_ideal=normalize_dict(dict_ideal)
    epsilon = 0.00000000001
    _in1 = Counter(dict_in.copy())
    _in2 = Counter(dict_ideal.copy())
    a = Counter(dict.fromkeys(dict_in, epsilon))
    b = Counter(dict.fromkeys(dict_ideal, epsilon))

    p = dict(Counter(_in1) + Counter(b))
    q = dict(Counter(_in2) + Counter(a))
    p=list(dict(sorted(p.items())).values())
    q=list(dict(sorted(q.items())).values())

    list_of_absdiff = []
    for p_i, q_i in zip(p, q):

        # caluclate the square of the difference of ith distr elements
        s = np.square(p_i - q_i)

        # append 
        list_of_absdiff.append(s)

    # calculate sum of squares
    soad = sum(list_of_absdiff)    

    return np.sqrt(soad)

def Compute_Hellinger(dict_in,dict_ideal):
    
    dict_in = normalize_dict(dict_in)
    dict_ideal=normalize_dict(dict_ideal)
    epsilon = 0.00000000001
    _in1 = Counter(dict_in.copy())
    _in2 = Counter(dict_ideal.copy())
    a = Counter(dict.fromkeys(dict_in, epsilon))
    b = Counter(dict.fromkeys(dict_ideal, epsilon))

    p = dict(Counter(_in1) + Counter(b))
    q = dict(Counter(_in2) + Counter(a))
    p=list(dict(sorted(p.items())).values())
    q=list(dict(sorted(q.items())).values())

    list_of_absdiff = []
    for p_i, q_i in zip(p, q):

        # caluclate the square of the difference of ith distr elements
        s = np.square(np.sqrt(p_i) - np.sqrt(q_i))

        # append 
        list_of_absdiff.append(s)

    # calculate sum of squares
    soad = sum(list_of_absdiff)    

    return np.sqrt(soad)


def Compute_Entropy(dict_in):
    
    _in1 = normalize_dict(dict(dict_in.copy()))
    epsilon = 0.000001
    P = list(dict(Counter(_in1)).values())
    a = Counter(dict.fromkeys(dict_in, epsilon))
    P = list(dict(Counter(_in1) + Counter(a)).values())
    P = np.asarray(P, dtype=np.float)
        
    return -1*sum(P*np.log(P))
