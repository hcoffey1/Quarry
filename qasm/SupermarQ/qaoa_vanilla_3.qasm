// Generated : 2022-05-04--15-52-58

OPENQASM 2.0;
include "qelib1.inc";


// Qubits: [0, 1, 2]
qreg q[3];
creg m0[3];  // Measurement: 0,1,2


h q[0];
h q[1];
h q[2];
cx q[0],q[2];
rz(pi*3.195934198) q[2];
cx q[0],q[2];
cx q[0],q[1];
rz(pi*-3.195934198) q[1];
cx q[0],q[1];
cx q[1],q[2];
rx(pi*0.8040636195) q[0];
rz(pi*-3.195934198) q[2];
cx q[1],q[2];
rx(pi*0.8040636195) q[1];
rx(pi*0.8040636195) q[2];

// Gate: cirq.MeasurementGate(3, cirq.MeasurementKey(name='0,1,2'), ())
measure q[0] -> m0[0];
measure q[1] -> m0[1];
measure q[2] -> m0[2];
