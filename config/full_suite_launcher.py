import os
import runpy
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "rerun_logs"
RESULT_DIR = ROOT / "rerun_results"
MAIN = ROOT / "src" / "main.py"
MASTER_LOG = LOG_DIR / "phase6_scale121_master.log"


RUNS = [
    ("baseline", "phase6_baseline_121_s42.log"),
    ("vector_a_undefended", "phase6_vecA_undef_121_s42.log"),
    ("vector_a_defended", "phase6_vecA_def_121_s42.log"),
]


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


def run_condition(condition: str, log_name: str) -> None:
    log_path = LOG_DIR / log_name
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    start = time.time()

    with MASTER_LOG.open("a") as master, log_path.open("w") as per_run:
        tee = Tee(original_stdout, master, per_run)
        sys.stdout = tee
        sys.stderr = tee
        try:
            print(f"=== START 121-task {condition} at {time.ctime()} ===", flush=True)
            sys.argv = [
                str(MAIN),
                "--iterations", "5",
                "--condition", condition,
                "--seed", "42",
                "--task-set", "full",
                "--result-root", str(RESULT_DIR),
            ]
            runpy.run_path(str(MAIN), run_name="__main__")
            elapsed = time.time() - start
            print(f"=== DONE 121-task {condition} at {time.ctime()} elapsed={elapsed:.1f}s ===", flush=True)
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr


def main() -> None:
    os.chdir(ROOT)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    os.environ["VIRA_NUM_GPU"] = "99"
    os.environ["VIRA_NO_FALLBACK"] = "1"
    os.environ["OLLAMA_KEEP_ALIVE"] = "24h"
    os.environ["OLLAMA_MAX_LOADED_MODELS"] = "2"

    with MASTER_LOG.open("a") as master:
        master.write(f"=== PHASE6 SCALE121 CHAIN START {time.ctime()} ===\n")
        master.flush()

    for condition, log_name in RUNS:
        run_condition(condition, log_name)

    with MASTER_LOG.open("a") as master:
        master.write(f"=== PHASE6 SCALE121 CHAIN COMPLETE {time.ctime()} ===\n")
        master.flush()


if __name__ == "__main__":
    main()
