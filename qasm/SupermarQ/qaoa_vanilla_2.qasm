// Generated : 2022-05-04--15-52-58

OPENQASM 2.0;
include "qelib1.inc";


// Qubits: [0, 1]
qreg q[2];
creg m0[2];  // Measurement: 0,1


h q[0];
h q[1];
cx q[0],q[1];
rz(pi*-2.5000750908) q[1];
cx q[0],q[1];
rx(pi*1.7499649859) q[0];
rx(pi*1.7499649859) q[1];

// Gate: cirq.MeasurementGate(2, cirq.MeasurementKey(name='0,1'), ())
measure q[0] -> m0[0];
measure q[1] -> m0[1];
