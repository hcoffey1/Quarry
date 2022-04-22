from qiskit import QuantumCircuit, Aer, execute, IBMQ
import os

directory = "./qasm/"

def printCircuitSizes(dir):
    for file in os.listdir(dir):
        print(file)


def main():
    printCircuitSizes(directory)

if __name__ == "__main__":
	main()