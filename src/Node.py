from typing import Optional
from src.Pod import Pod
from src.GPU import GPU
from src.utils.fragmentation_utils import compute_expected_fragmentation_with_state
from typing import Dict 

class Node:
    def __init__(self, id: str, cpu_compute: int, num_gpus: int):
        self.id = id
        self.total_cpus = cpu_compute
        self.num_gpus = num_gpus
        self.gpu_list = [GPU(i) for i in range(0, num_gpus)]

        self.free_cpus = self.total_cpus
        self.free_gpus = float(self.num_gpus)

    def can_serve(self, pod: Pod) -> bool:
        if pod.gpu_request > 1.0:
            running_request = pod.gpu_request
            for gpu in self.gpu_list:
                if gpu.can_serve(self.free_cpus, pod):
                    running_request -= 1.0 # allocate full gpu when multi-gpu request
            return running_request <= 0.0 # <0 does not happen by assumption
        else:
            return any(gpu.can_serve(self.free_cpus, pod) for gpu in self.gpu_list)

    def serve(self, pod: Pod):
        assert self.can_serve(pod)

        if pod.gpu_request > 1.0:
            running_request = pod.gpu_request
            for gpu in self.gpu_list:
                if running_request <= 0.0:
                    break
                elif gpu.can_serve(self.free_cpus, pod):
                    gpu.serve(pod)
                    running_request -= 1.0 #allocate full gpus for multi-gpu requests
            assert running_request == 0.0
        else:
            for gpu in self.gpu_list:
                if gpu.can_serve(self.free_cpus, pod):
                    gpu.serve(pod)
                    break
        
        self.free_gpus = self.__compute_free_gpus() # update free_gpus
        self.free_cpu = pod.consume_cpu(self.free_cpus) #consume node cpus once
   
    def hypothetical_serve(self, pod: Pod) -> tuple:
        """
        Simulate serving a pod without actually modifying the node state.
        Returns (hypothetical_free_cpus, hypothetical_gpu_states) where
        hypothetical_gpu_states is a list of hypothetical free_gpu values.
        """
        assert self.can_serve(pod)
        
        hypothetical_free_cpus = pod.consume_cpu(self.free_cpus, hypothetical=True)
        hypothetical_gpu_states = []
        
        if pod.gpu_request > 1.0:
            running_request = pod.gpu_request
            for gpu in self.gpu_list:
                if running_request <= 0.0:
                    hypothetical_gpu_states.append(gpu.free_gpu)
                elif gpu.can_serve(self.free_cpus, pod):
                    hypothetical_gpu_states.append(gpu.hypothetical_serve(pod))
                    running_request -= 1.0
                else:
                    hypothetical_gpu_states.append(gpu.free_gpu)
        else:
            served = False
            for gpu in self.gpu_list:
                if not served and gpu.can_serve(self.free_cpus, pod):
                    hypothetical_gpu_states.append(gpu.hypothetical_serve(pod))
                    served = True
                else:
                    hypothetical_gpu_states.append(gpu.free_gpu)
        
        return hypothetical_free_cpus, hypothetical_gpu_states
  
    def hypothetical_expected_frag(self, served_pod: Pod, 
                                   pod_distribution: Dict[Pod, float]) -> float:
        """
        Compute expected fragmentation after hypothetically serving a pod.
        Uses utility functions for the actual computation.
        """
        hypothetical_free_cpus, hypothetical_gpu_states = self.hypothetical_serve(served_pod)
        
        return compute_expected_fragmentation_with_state(
                pod_distribution, 
                hypothetical_free_cpus, 
                hypothetical_gpu_states
                )

    def expected_frag(self, pod_distribution: Dict[Pod, float]) -> float:
        total = 0
        for pod, prob in pod_distribution.items():
            total += prob * self.compute_frag_score(pod)

        return total

    def compute_frag_score(self, pod: Pod):
        """
        Computes the fragmentation of this node wrt. to the input pod.
        Based on equations 2 and 3 of Beware of Fragmentation Paper (2023)
        """
        if pod.is_cpu_only_task() or not self.can_serve(pod): 
            return self.free_gpus

        else:
            return sum(gpu.get_fragmentation(self.free_cpus, pod) 
                    for gpu in self.gpu_list)

    def get_gpu_capacity(self) -> float:
        return self.free_gpus

    
    def __compute_free_gpus(self) -> float:
        num_full_gpus = 0.0
        max_partial_capacity = 0.0
        for gpu in self.gpu_list:
            capacity = gpu.get_capacity()
            if capacity == 1.0:
                num_full_gpus += 1.0
            elif capacity > max_partial_capacity:
                max_partial_capacity = capacity
        return num_full_gpus + max_partial_capacity

               
