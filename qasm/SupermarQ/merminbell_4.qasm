// Generated : 2022-05-04--15-52-58

OPENQASM 2.0;
include "qelib1.inc";


// Qubits: [0, 1, 2, 3]
qreg q[4];
creg m0[4];  // Measurement: 0,1,2,3


rx(pi*-0.5) q[0];
cx q[0],q[1];
cx q[1],q[2];
cx q[2],q[3];
h q[1];
h q[2];
h q[3];
cx q[0],q[3];
swap q[2],q[1];
cx q[1],q[3];
cx q[2],q[3];
cx q[3],q[0];
cx q[2],q[0];
s q[3];
cx q[1],q[0];
h q[3];
s q[0];
cz q[1],q[0];
s q[1];
cz q[2],q[0];
cz q[2],q[1];
h q[0];
s q[2];
h q[1];
h q[2];

// Gate: cirq.MeasurementGate(4, cirq.MeasurementKey(name='0,1,2,3'), ())
measure q[0] -> m0[0];
measure q[1] -> m0[1];
measure q[2] -> m0[2];
measure q[3] -> m0[3];
