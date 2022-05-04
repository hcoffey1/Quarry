// Generated : 2022-05-04--15-52-58

OPENQASM 2.0;
include "qelib1.inc";


// Qubits: [0, 1, 2, 3]
qreg q[4];
creg m0[4];  // Measurement: 0,1,2,3


h q[0];
h q[1];
h q[2];
h q[3];
cx q[0],q[1];
rz(pi*-4.1564467852) q[1];
cx q[0],q[1];
cx q[1],q[3];
rz(pi*-4.1564467852) q[3];
cx q[1],q[3];
cx q[0],q[3];
cx q[1],q[2];
rz(pi*4.1564467852) q[3];
rz(pi*-4.1564467852) q[2];
cx q[0],q[3];
cx q[1],q[2];
cx q[0],q[2];
rx(pi*1.8201685705) q[1];
rz(pi*4.1564467852) q[2];
cx q[0],q[2];
cx q[2],q[3];
rx(pi*1.8201685705) q[0];
rz(pi*4.1564467852) q[3];
cx q[2],q[3];
rx(pi*1.8201685705) q[2];
rx(pi*1.8201685705) q[3];

// Gate: cirq.MeasurementGate(4, cirq.MeasurementKey(name='0,1,2,3'), ())
measure q[0] -> m0[0];
measure q[1] -> m0[1];
measure q[2] -> m0[2];
measure q[3] -> m0[3];
