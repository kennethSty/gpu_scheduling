from abc import ABC, abstractmethod
from src.PodQueue import PodQueue
from src.Cluster import Cluster
class BaseScheduler:
    @abstractmethod
    def schedule(self, pods: PodQueue, cluster: Cluster):
        """
        Schedules pods onto nodes.
        """
        pass
