# GPU-Sharing Workload Scheduler

A Python implementation of GPU scheduling algorithms for containerized workloads, including a Fragmentation Gradient Descent (FGD) scheduler inspired by the paper ["Beware of Fragmentation: Scheduling GPU-Sharing Workloads with Fragmentation Gradient Descent"](https://arxiv.org/abs/2305.19537).

## Overview

This project simulates GPU cluster scheduling with support for:

* Fractional GPU allocation (0.1 to 1.0 GPU units)
* Multi-GPU requests (>1.0 GPU units requiring full GPUs)
* CPU and GPU co-scheduling
* Fragmentation-aware scheduling algorithms

## Architecture

### Core Components

* `Pod`: Represents a containerized workload with CPU and GPU resource requests
* `GPU`: Models individual GPU resources with fractional allocation support
* `Node`: Represents a compute node with multiple GPUs and CPU resources
* `Cluster`: Collection of nodes representing the entire cluster
* `PodQueue`: FIFO queue of pending pods with workload distribution statistics

### Scheduling Algorithms

#### 1. First Fit Scheduler (`FirstFitScheduler`)

* **Algorithm**: Assigns each pod to the first node that can accommodate it
* **Complexity**: O(n × m) where n = pods, m = nodes
* **Use case**: Baseline comparison, fast scheduling

#### 2. Fragmentation Gradient Descent Scheduler (`LocalFGDScheduler`)

* **Algorithm**: Selects the node that minimizes fragmentation increase
* **Complexity**: O(n × m × k) where k = average pods in distribution
* **Features**:

  * Fragmentation-aware placement decisions
  * Expected fragmentation calculation based on workload distribution
  * Optimized with hypothetical serving (no deep copying)

## Key Features

### Fragmentation Calculation

The system implements fragmentation scoring based on the FGD paper:

* **GPU Fragmentation**: Unused GPU capacity that cannot serve future workloads
* **Expected Fragmentation**: Probability-weighted fragmentation across workload distribution
* **Fragmentation Delta**: Change in fragmentation after hypothetical pod placement

### Performance Optimizations

* **Hypothetical Serving**: Simulates resource allocation without state mutation
* **Utility Functions**: Pure functions for fragmentation calculations
* **Efficient Data Structures**: Uses `deque` for O(1) queue operations

## Installation

```bash
git clone <repository-url>
cd gpu-scheduler
pip install -r requirements.txt  # if requirements.txt exists
```

## Usage

### Basic Scheduling Comparison with Provided Data

Run the main scheduling script from the root directory:

```bash
python schedule.py
```

### Custom Workload

To test the scheduler with your own workload:

1. Format your input as a CSV with `cpu_request`, `gpu_request` columns.
2. Replace or extend the data loading function in `utils/load_data.py`.
3. Update the `schedule.py` logic if needed.

Example custom CSV:

```csv
cpu_request,gpu_request
2,0.5
4,1.0
1,0.0
8,2.0
```

## File Structure

```text
src/
├── Pod.py                      # Pod resource model
├── GPU.py                      # GPU resource management
├── Node.py                     # Compute node with multiple GPUs
├── Cluster.py                  # Cluster of nodes
├── PodQueue.py                 # Pod queue with workload distribution
├── heuristics/
│   ├── BaseScheduler.py        # Abstract scheduler base class
│   ├── FirstFitScheduler.py    # First-fit scheduling algorithm
│   └── FGDScheduler.py         # Fragmentation gradient descent
└── utils/
    ├── fragmentation_utils.py  # Pure fragmentation calculation functions
    └── load_data.py            # Data loading utilities
schedule.py                     # Main evaluation script
```

## Resource Model

### Pod Specifications

* **CPU Request**: Integer CPU units required
* **GPU Request**: Float GPU units (0.0 to N.0)

  * `0.0`: CPU-only workload
  * `0.1-1.0`: Fractional GPU sharing
  * `>1.0`: Multi-GPU requiring full GPUs

### Node Specifications

* **CPU Capacity**: Total CPU units available
* **GPU List**: Collection of individual GPU resources
* **Scheduling Constraints**:

  * Multi-GPU requests require full GPUs
  * Fractional requests can share GPUs
  * CPU requirements must be satisfied

## Evaluation Metrics

The evaluation script tracks several metrics:

* **Schedule Success Rate**: Percentage of pods successfully placed
* **Average Time per Pod**: Scheduling latency per workload
* **Fragmentation Score**: Resource utilization efficiency
* **Cluster Utilization**: Overall resource usage

## Result and example output (verbose setting)
1. Suprisingly both scheduler, although choosing different nodes for the initial pods, 
towards the end of the queue choose similar pods. 
Additionally, although by design fragmentation-aware scheduling should lead to a higher scheduling success rate, this is not achieved. 
2. Unsuprisingly, FGD is slower than first fit by several orders of mangitude as the node evaluations are not done in parallel, adding a factor of N into the complexity of the algorith.

Further work is necessary to determine the reason for the exact same scheduling success rate.

```
First Fit Results:
Scheduled 6973 out of 8152 pods.
Scheduling success rate: 85.54%
Average time per pod: 0.000695 seconds
Average time per pod: 0.695 milliseconds

openb-node-0123 serves openb-pod-0000
openb-node-0123 serves openb-pod-0001
openb-node-0124 serves openb-pod-0002
openb-node-0124 serves openb-pod-0003
…….
openb-node-0123 serves openb-pod-8106
openb-node-0123 serves openb-pod-8113
openb-node-0123 serves openb-pod-8114
0 left to schedule

FGD Results:
Scheduled 6973 out of 8152 pods.
Scheduling success rate: 85.54%
Average time per pod: 0.075204 seconds
Average time per pod: 75.204 milliseconds

openb-node-1328 serves openb-pod-0000
openb-node-0356 serves openb-pod-0001
openb-node-1329 serves openb-pod-0002
…..
openb-node-0123 serves openb-pod-8106
openb-node-0123 serves openb-pod-8113
openb-node-0123 serves openb-pod-8114
0 left to schedule
```

## Fragmentation Gradient Descent Details

For each pending pod:

1. Calculate current fragmentation for each eligible node
2. Simulate pod placement (hypothetical serving)
3. Calculate fragmentation after placement
4. Select node with minimum fragmentation increase

### Optimization

* Avoids deep copies by using in-place hypothetical simulation
* Leverages workload distribution statistics to estimate expected fragmentation

## Research Background

This implementation is based on the research paper:

* **Title**: "Beware of Fragmentation: Scheduling GPU-Sharing Workloads with Fragmentation Gradient Descent"
* **Key Insight**: GPU fragmentation significantly impacts cluster utilization
* **Solution**: Fragmentation-aware scheduling reduces resource waste

## Possible Future Enhancements
* Further evaluation to determine the reason for the similar success scheduling rate
* Support for GPU type constraints
* Dynamic workload arrival patterns and requeuing
* Distributed scheduling simulation with actual parallelization of the nodes
* Plotting of scheduling trajectory 
