from src.heuristics.BaseScheduler import BaseScheduler
from src.PodQueue import PodQueue
from src.Cluster import Cluster

class FirstFitScheduler(BaseScheduler):
    def schedule(self, pods: PodQueue, cluster: Cluster, verbose = False) -> int:
        scheduled = 0
        print("Start Scheduling")
        while (pods.has_next()):
            pod = pods.pop()
            for node in cluster.node_list:
                if node.can_serve(pod):
                    node.serve(pod)
                    scheduled += 1
                    if verbose: print(f"{node.id} serves {pod.id}")
                    break
            if len(pods) % 1000 == 0:
                print(f"{len(pods)} left to schedule")
        return scheduled
