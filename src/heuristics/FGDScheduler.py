from typing import Optional
from src.heuristics.BaseScheduler import BaseScheduler
from src.Node import Node
from src.Pod import Pod
from src.PodQueue import PodQueue
from src.Cluster import Cluster
from collections import defaultdict
import copy

class LocalFGDScheduler(BaseScheduler):
    """
    Implements a schedular similar, but simpler than the original FGD algorithm
    in Weng et. al 2023. Instead of computing the expected Fragmentation 
    for a given node (F_n(M)) it computes the node that results in the least  F_n(m)) 
    """

    def schedule(self, pods:PodQueue, cluster: Cluster, verbose=False) -> int:
        scheduled = 0
        print("Start Scheduling")
        while(pods.has_next()):
            pod = pods.pop()
            node = self.__min_frag_node(pod, pods, cluster)
            if node is not None: # ATM no requeuing implemented
                node.serve(pod)
                scheduled += 1
                if verbose: print(f"{node.id} serves {pod.id}")
            if len(pods) % 1000 == 0:
                print(f"{len(pods)} left to schedule")
        return scheduled

    def __min_frag_node(self, pod: Pod, 
                        pods: PodQueue, cluster: Cluster) -> Optional[Node]:
        best_node = None
        best_delta = float('inf')
        node_score_set = defaultdict()

        for node in cluster.node_list:
            if node.can_serve(pod):
                frag_current = node.expected_frag(pods.pod_distribution)
                frag_after = node.hypothetical_expected_frag(
                        pod, pods.pod_distribution)

                delta = frag_after - frag_current

                if delta < best_delta:
                    best_node = node
                    best_delta = delta
        return best_node


