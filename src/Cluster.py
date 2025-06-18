from pathlib import Path
from src.Node import Node
from src.utils.load_data import load_nodes

class Cluster:
    def __init__(self):
        self.node_list = load_nodes()
        self.total_gpu_capacity = self.__compute_gpu_capacity()
        self.free_gpu_capacity = self.total_gpu_capacity

    def update_gpu_capacity(self):
        self.free_gpu_capacity = self.__compute_gpu_capacity() 

    def __compute_gpu_capacity(self) -> float:
        total = 0.0
        for node in self.node_list:
            total += node.get_gpu_capacity()
        return total
