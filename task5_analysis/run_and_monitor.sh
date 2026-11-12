#!/bin/bash
# Script for Task 5: Run HPL benchmark and monitor OS resources (CPU, Memory, Swap)

NP=${1:-4} # Number of MPI processes (default: 4)
LOG_FILE="vmstat_${NP}procs.log"
HPL_OUT="hpl_result_${NP}procs.txt"

echo "[Task 5] Starting OS resource monitoring (sampling every 1 second)..."
# Run vmstat in background (-n prints header only once)
vmstat -n 1 > "$LOG_FILE" &
VMSTAT_PID=$!

echo "[Task 5] Running HPL benchmark with $NP MPI processes..."
# Run the actual MPI HPL command (adjust path/hostfile once cluster is ready)
mpirun -np "$NP" ./xhpl > "$HPL_OUT"

echo "[Task 5] Benchmark finished. Stopping monitor..."
kill "$VMSTAT_PID"

echo "[Task 5] Done! Logs saved to $LOG_FILE and $HPL_OUT"
