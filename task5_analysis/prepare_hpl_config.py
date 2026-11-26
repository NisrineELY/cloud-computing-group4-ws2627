import math
import sys


def calculate_n(ram_gb: float, mem_fraction: float = 0.80, block_size: int = 128) -> int:
    """Calculate a safe HPL matrix dimension N targeting ~80% of RAM, aligned to NB."""
    total_bytes = ram_gb * (1024 ** 3)
    target_bytes = total_bytes * mem_fraction
    raw_n = math.sqrt(target_bytes / 8.0)
    aligned_n = int(raw_n // block_size) * block_size
    return max(aligned_n, block_size)


def choose_pq(num_procs: int) -> tuple[int, int]:
    """Choose P and Q such that P * Q == num_procs and |P - Q| is minimal."""
    best_p, best_q = 1, num_procs
    best_diff = num_procs - 1
    for p in range(1, int(math.isqrt(num_procs)) + 1):
        if num_procs % p == 0:
            q = num_procs // p
            diff = abs(q - p)
            if diff < best_diff:
                best_diff = diff
                best_p, best_q = p, q
    return best_p, best_q


def write_hpl_dat(filename: str, n: int, nb: int, p: int, q: int) -> None:
    content = f"""HPLinpack benchmark input file
Innovative Computing Laboratory, University of Tennessee
HPL.out      output file name (if any)
6            device out (6=stdout,7=stderr,file)
1            # of problems sizes (N)
{n:<12} Ns
1            # of NBs
{nb:<12} NBs
0            PMAP process mapping (0=Row-,1=Column-major)
1            # of process grids (P x Q)
{p:<12} Ps
{q:<12} Qs
16.0         threshold
1            # of panel fact
2            PFACTs (0=left, 1=Crout, 2=Right)
1            # of recursive stopping criterium
4            NBMINs (>= 1)
1            # of panels in recursion
2            NDIVs
1            # of recursive panel fact.
1            RFACTs (0=left, 1=Crout, 2=Right)
1            # of broadcast
1            BCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM)
1            # of lookahead depth
1            DEPTHs (>=0)
2            SWAP (0=bin-exch,1=long,2=mix)
64           swapping threshold
0            L1 in (0=transposed,1=no-transposed) form
0            U  in (0=transposed,1=no-transposed) form
1            Equilibration (0=no,1=yes)
8            memory alignment in double (>= 4)
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    ram_gb = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0
    num_procs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    nb = int(sys.argv[3]) if len(sys.argv) > 3 else 128

    n_val = calculate_n(ram_gb=ram_gb, mem_fraction=0.80, block_size=nb)
    p_val, q_val = choose_pq(num_procs)
    out_path = "task5_analysis/HPL.dat"
    write_hpl_dat(out_path, n=n_val, nb=nb, p=p_val, q=q_val)

    print(f"RAM input: {ram_gb} GB | MPI processes: {num_procs}")
    print(f"Recommended N: {n_val} (NB={nb}) | Grid: P={p_val}, Q={q_val}")
    print(f"Generated {out_path}")
