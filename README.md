# CS 758 Class Project

## Files

### `env.yml`
Contains `Conda` dependencies. Run:

`conda env update --file env.yml`

to make sure python environment is correctly configured.

### `est.py`
Takes a single argument specifying path to QASM file to estimate
circuit fidelity on.

### `dataGen.py`
Run to generate a data set containing Qiskit backend and circuit
fidelity information.

### `Q_Util.py`
Misc. functions for use in other files.

### `Eval_Metrics.py`
Methods for calculating fidelity metrics.