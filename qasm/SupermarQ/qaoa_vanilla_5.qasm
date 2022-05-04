// Generated : 2022-05-04--15-52-58

OPENQASM 2.0;
include "qelib1.inc";


// Qubits: [0, 1, 2, 3, 4]
qreg q[5];
creg m0[5];  // Measurement: 0,1,2,3,4


h q[0];
h q[1];
h q[2];
h q[3];
h q[4];
cx q[1],q[3];
rz(pi*1.1666441496) q[3];
cx q[1],q[3];
cx q[1],q[2];
cx q[0],q[3];
rz(pi*1.1666441496) q[2];
rz(pi*-1.1666441496) q[3];
cx q[1],q[2];
cx q[0],q[3];
cx q[3],q[4];
rz(pi*1.1666441496) q[4];
cx q[3],q[4];
cx q[2],q[4];
rz(pi*1.1666441496) q[4];
cx q[2],q[4];
cx q[0],q[4];
cx q[2],q[3];
rz(pi*-1.1666441496) q[4];
rz(pi*-1.1666441496) q[3];
cx q[0],q[4];
cx q[2],q[3];
cx q[0],q[2];
rx(pi*-0.2499681579) q[3];
rz(pi*1.1666441496) q[2];
cx q[0],q[2];
cx q[0],q[1];
rx(pi*-0.2499681579) q[2];
rz(pi*1.1666441496) q[1];
cx q[0],q[1];
cx q[1],q[4];
rx(pi*-0.2499681579) q[0];
rz(pi*1.1666441496) q[4];
cx q[1],q[4];
rx(pi*-0.2499681579) q[1];
rx(pi*-0.2499681579) q[4];

// Gate: cirq.MeasurementGate(5, cirq.MeasurementKey(name='0,1,2,3,4'), ())
measure q[0] -> m0[0];
measure q[1] -> m0[1];
measure q[2] -> m0[2];
measure q[3] -> m0[3];
measure q[4] -> m0[4];
