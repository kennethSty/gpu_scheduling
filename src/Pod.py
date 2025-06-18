from typing import List

class Pod:
    def __init__(self, id: str, cpu_request: int, gpu_request: float):
        self.id = id
        self.cpu_request = cpu_request
        self.gpu_request = gpu_request
        self.is_served = False

    def consume_cpu(self, free_cpu: int, hypothetical=False) -> int:
        remaining_cpu = free_cpu - self.cpu_request
        assert remaining_cpu >= 0 
        
        if not hypothetical:
            self.cpu_request = 0
        
        return remaining_cpu

    def consume_gpus(self, free_gpu: float, hypothetical=False) -> float:
        # If request gpu is larger than 1.0 only full GPUs can be allocated
        allocation = min(self.gpu_request, 1.0)
        remaining_gpu = free_gpu - allocation 
        assert remaining_gpu >= 0.0
        
        if not hypothetical:
            self.gpu_request -= allocation
        
        return remaining_gpu

    def is_cpu_only_task(self) -> bool:
        return self.gpu_request == 0

    def __eq__(self, other):
        if not isinstance(other, Pod):
            return False
        return (self.cpu_request == other.cpu_request) and \
               (round(self.gpu_request, 3) == round(other.gpu_request, 3))

    def __hash__(self):
        #needed to use pod objects as keys in dictionaries
        return hash((self.cpu_request, round(self.gpu_request, 3)))

