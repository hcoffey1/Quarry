// Generated : 2022-05-04--15-52-58

OPENQASM 2.0;
include "qelib1.inc";


// Qubits: [0, 1, 2, 3, 4, 5, 6]
qreg q[7];
creg m0[7];  // Measurement: 0,1,2,3,4,5,6


rx(pi*-0.5) q[0];
cx q[0],q[1];
cx q[1],q[2];
cx q[2],q[3];
cx q[3],q[4];
cx q[4],q[5];
cx q[5],q[6];
h q[1];
h q[2];
h q[3];
h q[4];
h q[5];
h q[6];
cx q[0],q[6];
swap q[5],q[1];
swap q[4],q[2];
cx q[1],q[6];
cx q[2],q[6];
cx q[3],q[6];
cx q[4],q[6];
cx q[5],q[6];
cx q[6],q[0];
cx q[5],q[0];
s q[6];
cx q[4],q[0];
h q[6];
cx q[3],q[0];
cx q[2],q[0];
cx q[1],q[0];
s q[0];
cz q[1],q[0];
s q[1];
cz q[2],q[0];
cz q[2],q[1];
cz q[3],q[0];
s q[2];
cz q[3],q[1];
cz q[4],q[0];
cz q[3],q[2];
cz q[4],q[1];
cz q[5],q[0];
s q[3];
cz q[4],q[2];
cz q[5],q[1];
h q[0];
cz q[4],q[3];
cz q[5],q[2];
h q[1];
s q[4];
cz q[5],q[3];
h q[2];
cz q[5],q[4];
h q[3];
s q[5];
h q[4];
h q[5];

// Gate: cirq.MeasurementGate(7, cirq.MeasurementKey(name='0,1,2,3,4,5,6'), ())
measure q[0] -> m0[0];
measure q[1] -> m0[1];
measure q[2] -> m0[2];
measure q[3] -> m0[3];
measure q[4] -> m0[4];
measure q[5] -> m0[5];
measure q[6] -> m0[6];
