from collections import deque
from src.Pod import Pod
from src.utils.load_data import load_pods, load_pod_distribution
from typing import List, Optional
from pathlib import Path

class PodQueue:
    """
    Class encapsulating the logic of a FIFO Queue of Pods.
    Uses deque internally for constant time popleft().
    """

    def __init__(self):
        self.pod_queue = deque(load_pods())
        self.pod_distribution = load_pod_distribution()

    def has_next(self) -> bool:
        return len(self.pod_queue) > 0

    def peek(self) -> Optional[Pod]:
        return self.pod_queue[0] if self.pod_queue else None

    def pop(self) -> Optional[Pod]:
        return self.pod_queue.popleft() if self.pod_queue else None

    def requeue(self, pod: Pod):
        self.pod_queue.append(pod)


    def __len__(self):
        return len(self.pod_queue)
