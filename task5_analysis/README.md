# Task 5: Performance Evaluation, Scaling Laws & OS Bottleneck Analysis

This directory contains the monitoring scripts, analysis tools, and theoretical scaling models for Task 5 of the Cloud Computing project.

## 1. Overview & Objectives
The goal of Task 5 is to evaluate the cluster computational throughput (GFLOPS) using the HPL (High-Performance Linpack) benchmark over MPI, analyze scalability using Amdahl and Gustafson laws, and identify operating system bottlenecks (CPU overhead, memory depletion, and swap/paging activity).

## 2. Directory Contents
- run_and_monitor.sh: Bash automation wrapper that runs xhpl via mpirun while sampling OS kernel metrics (vmstat) every second in the background.
- analyze_scaling.py: Python script that computes and plots theoretical vs. empirical speedup curves (Amdahl Law / Strong Scaling and Gustafson Law / Weak Scaling) alongside system GFLOPS throughput.
- analyze_os_metrics.py: Python script that parses vmstat logs to visualize User vs. Kernel CPU utilization, I/O wait times, RAM depletion, and Swap (paging) bottlenecks.
- task5_scaling_results.png: Generated scaling and throughput plots.
- task5_os_bottlenecks.png: Generated OS resource utilization and bottleneck detection plots.

## 3. Theoretical Framework
1. Amdahl Law (Strong Scaling - Fixed Problem Size N):
   S(N) = 1 / ((1 - P) + (P / N))
   Evaluates speedup when the matrix size N remains constant while increasing the number of MPI processes. Deviations from the theoretical curve reflect MPI network communication overhead and OS context switching.

2. Gustafson Law (Weak Scaling - Scaled Problem Size):
   S(N) = N - (1 - P)*(N - 1)
   Evaluates scaled speedup when problem size grows proportionally with cluster nodes, maintaining constant memory utilization per node (~80% RAM).

3. Optimal HPL Matrix Size (N) Calculation:
   To maximize GFLOPS while avoiding OS swap thrashing, matrix size N is calculated for ~80% of total cluster RAM:
   N = sqrt((Total_RAM_in_Bytes * 0.80) / 8)

## 4. How to Run on the Cluster (Once Task 4 is Ready)
1. Place xhpl and HPL.dat in the working directory on the master node.
2. Execute the monitoring wrapper (e.g., for 4 MPI processes):
   ./run_and_monitor.sh 4
3. Update analyze_scaling.py and analyze_os_metrics.py with the generated log files and re-run to produce the final report figures.
