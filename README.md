# Quarry: Providing fast quantum circuit fidelity estimation. (University Course Project)

## Description
We present Quarry, an assistant tool for providing
fast quantum circuit fidelity estimations across a variety of
computing platforms. Quarry processes these estimated values
and provides researchers with recommendations for what platforms 
their particular circuit would perform best on. Our design
allows Quarry to use a variety of methods for determining
these recommendations. A more detailed explanation
and evaluation of the system is available in our
[final report.](./pdf/Quarry_Final_Report.pdf)

## Dependencies

`env.yml` contains `Conda` dependencies. Run:

`conda env update --file env.yml`

to make sure python environment is correctly configured.

## Usage
General usage form:

`python ./src/Est.py file mode`

To display help:

`python ./src/Est.py -h`

**Command line arguments**
|Argument|Description|
|---        |---|
|file       |Path to qasm file|
|mode       |Query mode|
|-n         |Number of platforms to query|


## File descriptions:
### `Est.py`
Main file used to query about a `qasm` file.

### `DataGen.py`
Run to generate a data set containing Qiskit backend and circuit
fidelity information.

### `QUtil.py`
Misc. functions for use in other files.

### `EvalMetrics.py`
Methods for calculating fidelity metrics.

## Notes from talk

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
