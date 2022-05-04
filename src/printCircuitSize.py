#This is just scratchwork being backedup onto the repo
#Will likely delete this later -HC
from qiskit import QuantumCircuit, Aer, execute, IBMQ
import os

directory = "./qasm/"

circuits = []
errCircuits = []

def printCircuitSizes(dir):
    global errCircuits
    global circuits

    for file in os.listdir(dir):
        if os.path.isfile(dir+file) and file.endswith('.qasm'):
            try:
                qc = QuantumCircuit.from_qasm_file(dir+file)
                print(qc.num_qubits)
                print(dir+file)
                circuits.append((dir+file, qc.num_qubits))
                del qc
            except:
                errCircuits = []

        elif os.path.isdir(dir+file):
            printCircuitSizes(dir + file + "/")

def main():
    pass 
    #printCircuitSizes(directory)

if __name__ == "__main__":
	main()
