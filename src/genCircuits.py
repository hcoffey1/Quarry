#Hayden Coffey
#Use SupermarQ to generate additional qasm benchmarks.
#https://github.com/SupertechLabs/SupermarQ
import supermarq
import sys
from Q_Util import getTS

OUT_DIR: str = "./qasm/SupermarQ/"


def main():
	if len(sys.argv) == 1 or int(sys.argv[1]) > 10:
		print("Need to specify max qubit size circuit to produce. (Max 10)")
		return 1

	count = int(sys.argv[1])

	ts = getTS()
	header = "Generated : " + ts

	for i in range(2, count+1):
		supermarq.benchmarks.mermin_bell.MerminBell(num_qubits=i).circuit().save_qasm(
			file_path=OUT_DIR + "merminbell_" + str(i) + ".qasm", header=header)
		supermarq.benchmarks.qaoa_vanilla_proxy.QAOAVanillaProxy(num_qubits=i).circuit().save_qasm(
			file_path=OUT_DIR + "qaoa_vanilla_" + str(i) + ".qasm", header=header)
		supermarq.benchmarks.qaoa_fermionic_swap_proxy.QAOAFermionicSwapProxy(num_qubits=i).circuit().save_qasm(
			file_path=OUT_DIR + "qaoa_fermionic_" + str(i) + ".qasm", header=header)


if __name__ == "__main__":
	main()
