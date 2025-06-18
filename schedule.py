import time
from src.Cluster import Cluster
from src.PodQueue import PodQueue
from src.heuristics.FirstFitScheduler import FirstFitScheduler
from src.heuristics.BaseScheduler import BaseScheduler
from src.heuristics.FGDScheduler import LocalFGDScheduler
from src.utils.load_data import load_pod_distribution

def run_scheduler(scheduler: BaseScheduler, scheduler_name: str):
    pod_queue = PodQueue()
    n_pods = len(pod_queue)
    cluster = Cluster()
    pod_dist = load_pod_distribution()

    start_time = time.perf_counter()
    scheduled = scheduler.schedule(pod_queue, cluster)
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    avg_time_per_pod = total_time / n_pods

    print(f"\n{scheduler_name} Results:")
    print(f"Scheduled {scheduled} out of {n_pods} pods.")
    print(f"Scheduling success rate: {100 * scheduled / n_pods:.2f}%")
    print(f"Average time per pod: {avg_time_per_pod:.6f} seconds")
    print(f"Average time per pod: {avg_time_per_pod * 1000:.3f} milliseconds")

if __name__ == "__main__":
    first_fit_scheduler = FirstFitScheduler()
    fgd_scheduler = LocalFGDScheduler()

    run_scheduler(first_fit_scheduler, "First Fit")
    run_scheduler(fgd_scheduler, "FGD")

