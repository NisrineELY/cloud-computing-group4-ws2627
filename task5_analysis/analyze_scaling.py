import matplotlib.pyplot as plt
import numpy as np

# 1. Dummy Data (To be replaced with real HPL measurements)
cores = np.array([1, 2, 4, 8])

# Strong Scaling (Fixed problem size N)
strong_time_sec = np.array([120.0, 65.0, 36.0, 21.0])
strong_gflops = np.array([15.2, 28.1, 50.7, 86.8])

# Weak Scaling (Problem size grows with cores)
weak_measured_speedup = np.array([1.0, 1.85, 3.45, 6.40])

# Estimated parallel fraction (P)
P = 0.94  

# 2. Theoretical Calculations (Amdahl & Gustafson)
measured_strong_speedup = strong_time_sec[0] / strong_time_sec
amdahl_theoretical = 1 / ((1 - P) + (P / cores))
gustafson_theoretical = cores - (1 - P) * (cores - 1)

# 3. Plotting the Graphs
plt.figure(figsize=(15, 4.5))

# Graph 1: Amdahl's Law (Strong Scaling)
plt.subplot(1, 3, 1)
plt.plot(cores, cores, 'k--', alpha=0.4, label='Linear (Ideal)')
plt.plot(cores, amdahl_theoretical, 'b-o', label=f"Amdahl's Law (P={P})")
plt.plot(cores, measured_strong_speedup, 'r-s', label='Measured Speedup (HPL)')
plt.title("Strong Scaling: Amdahl's Law")
plt.xlabel('Number of Cores / MPI Processes')
plt.ylabel('Speedup')
plt.xticks(cores)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()

# Graph 2: Gustafson's Law (Weak Scaling)
plt.subplot(1, 3, 2)
plt.plot(cores, cores, 'k--', alpha=0.4, label='Linear (Ideal)')
plt.plot(cores, gustafson_theoretical, 'g-o', label=f"Gustafson's Law (P={P})")
plt.plot(cores, weak_measured_speedup, 'm-s', label='Measured Scaled Speedup')
plt.title("Weak Scaling: Gustafson's Law")
plt.xlabel('Number of Cores / MPI Processes')
plt.ylabel('Scaled Speedup')
plt.xticks(cores)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()

# Graph 3: System Throughput (GFLOPS)
plt.subplot(1, 3, 3)
plt.bar(cores.astype(str), strong_gflops, color='#4C72B0', width=0.5)
plt.title('System Throughput (GFLOPS)')
plt.xlabel('Number of Cores / MPI Processes')
plt.ylabel('GFLOPS')
plt.grid(True, axis='y', linestyle=':', alpha=0.6)

plt.tight_layout()
plt.savefig('task5_scaling_results.png', dpi=300)
print("Success! Graph saved as 'task5_scaling_results.png'")
