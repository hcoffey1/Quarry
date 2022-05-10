# Quarry: Providing fast quantum circuit fidelity estimation. (University Course Project)

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

### Notes from talk

* Is ESP correlated with other metrics?
  - Spearman's rank correlation coefficient
  - Are ML models actually worth it compared to ESP?
  - Use OpenMP to multithread computation.
  
* Focus on developing model for swaps
  - Compare performance against compiler.
  - Train on heavily optimized circuits, save computation estimating in the future

* Design model for predicting fitness instead of other metrics?
  - Could benefit prototype implementation. Only need to train 1 model instead of all the component metric models.

* Timeline visualization of fitness

* Heatmap of latency for methods (QC size, QM size) -> Latency

* Heatmaps of (Metric1, Metric2) -> ESP ?
