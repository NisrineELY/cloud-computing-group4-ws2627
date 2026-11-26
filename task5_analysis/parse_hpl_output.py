import re
import sys
from typing import Dict, Tuple, Union


def parse_hpl_file(filepath: str) -> Dict[str, Union[float, int, str]]:
    """Extract problem size N, execution time (sec), and GFLOPS from an HPL output file."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    pattern = re.compile(
        r"^\s*(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s*$",
        re.MULTILINE,
    )
    matches = pattern.findall(text)
    if not matches:
        raise ValueError(f"No HPL benchmark result line found in '{filepath}'.")

    _, n_str, nb_str, p_str, q_str, time_str, gflops_str = matches[-1]
    return {
        "N": int(n_str),
        "NB": int(nb_str),
        "P": int(p_str),
        "Q": int(q_str),
        "time_sec": float(time_str),
        "gflops": float(gflops_str),
    }


def choose_pq(num_procs: int) -> Tuple[int, int]:
    best_p, best_q = 1, num_procs
    best_diff = num_procs - 1
    for p in range(1, int(num_procs ** 0.5) + 1):
        if num_procs % p == 0:
            q = num_procs // p
            diff = abs(q - p)
            if diff < best_diff:
                best_diff = diff
                best_p, best_q = p, q
    return best_p, best_q


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 parse_hpl_output.py <path_to_hpl_output.txt>")
        sys.exit(1)

    result = parse_hpl_file(sys.argv[1])
    for key, value in result.items():
        print(f"{key}: {value}")
