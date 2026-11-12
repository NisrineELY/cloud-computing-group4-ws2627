import matplotlib.pyplot as plt
import numpy as np

# Parse vmstat log file
free_mem_mb = []
swap_used_mb = []
cpu_user = []
cpu_sys = []
cpu_wait = []

with open('vmstat_sample.log', 'r') as f:
    lines = f.readlines()[2:]  # Skip the 2 header lines
    for line in lines:
        parts = line.split()
        if len(parts) >= 16:
            # vmstat reports memory in KB -> convert to MB
            swap_used_mb.append(int(parts[2]) / 1024.0)
            free_mem_mb.append(int(parts[3]) / 1024.0)
            cpu_user.append(int(parts[12]))
            cpu_sys.append(int(parts[13]))
            cpu_wait.append(int(parts[15]))

time_sec = np.arange(len(cpu_user))

plt.figure(figsize=(13, 5))

# Graph 1: CPU Breakdown (User vs System/Kernel vs I/O Wait)
plt.subplot(1, 2, 1)
plt.plot(time_sec, cpu_user, 'b-o', label='User CPU % (HPL Math)')
plt.plot(time_sec, cpu_sys, 'r-s', label='System/Kernel CPU % (MPI/OS Overhead)')
plt.plot(time_sec, cpu_wait, 'y-^', label='I/O Wait % (Bottleneck)')
plt.title('CPU Utilization & OS Overhead Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('CPU Usage (%)')
plt.ylim(0, 105)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()

# Graph 2: Memory & Swap Activity (Paging Bottleneck Detection)
plt.subplot(1, 2, 2)
ax1 = plt.gca()
ax1.plot(time_sec, free_mem_mb, 'g-o', label='Free RAM (MB)')
ax1.set_xlabel('Time (seconds)')
ax1.set_ylabel('Free RAM (MB)', color='g')
ax1.tick_params(axis='y', labelcolor='g')
ax1.grid(True, linestyle=':', alpha=0.6)

ax2 = ax1.twinx()
ax2.plot(time_sec, swap_used_mb, 'm--s', label='Swap Used (MB)')
ax2.set_ylabel('Swap Used (MB)', color='m')
ax2.tick_params(axis='y', labelcolor='m')

plt.title('Memory Depletion & Swap (Paging) Detection')
plt.tight_layout()
plt.savefig('task5_os_bottlenecks.png', dpi=300)
print("Success! OS metrics graph saved as 'task5_os_bottlenecks.png'")
