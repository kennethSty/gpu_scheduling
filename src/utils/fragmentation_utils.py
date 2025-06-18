from typing import Dict, List
from src.Pod import Pod

def compute_free_gpus_from_states(gpu_states: List[float]) -> float:
    """
    Compute free GPUs from a list of GPU capacity states.
    This is a pure function that doesn't need node state.
    """
    num_full_gpus = 0.0
    max_partial_capacity = 0.0
    for capacity in gpu_states:
        if capacity == 1.0:
            num_full_gpus += 1.0
        elif capacity > max_partial_capacity:
            max_partial_capacity = capacity
    return num_full_gpus + max_partial_capacity

def can_serve_with_state(pod: Pod, free_cpus: int, 
                         gpu_states: List[float]) -> bool:
    """
    Check if we can serve a pod given CPU and GPU states.
    Pure function - no node state needed.
    """
    if pod.gpu_request > 1.0:
        running_request = pod.gpu_request
        for gpu_state in gpu_states:
            if pod.cpu_request <= free_cpus and gpu_state == 1.0:
                running_request -= 1.0
        return running_request <= 0.0
    else:
        return any(
            pod.cpu_request <= free_cpus and pod.gpu_request <= gpu_state
            for gpu_state in gpu_states
        )

def compute_gpu_fragmentation(pod: Pod, free_cpus: int, 
                              gpu_state: float) -> float:
    """
    Compute fragmentation for a single GPU given CPU and GPU state.
    Pure function - no node state needed.
    """
    if pod.gpu_request >= 1.0:
        can_serve = (pod.cpu_request <= free_cpus) and (gpu_state == 1.0)
    else:
        can_serve = (pod.cpu_request <= free_cpus) and (pod.gpu_request <= gpu_state)
    
    return 0.0 if can_serve else gpu_state

def compute_fragmentation_score_with_state(pod: Pod, free_cpus: int, 
                                           gpu_states: List[float]) -> float:
    """
    Compute fragmentation score for a pod given CPU and GPU states.
    Pure function - no node state needed.
    """
    if pod.is_cpu_only_task():
        return compute_free_gpus_from_states(gpu_states)
    
    if not can_serve_with_state(pod, free_cpus, gpu_states):
        return compute_free_gpus_from_states(gpu_states)
    else:
        return sum(
            compute_gpu_fragmentation(pod, free_cpus, gpu_state)
            for gpu_state in gpu_states
        )

def compute_expected_fragmentation_with_state(
    pod_distribution: Dict[Pod, float], 
    free_cpus: int, 
    gpu_states: List[float]
) -> float:
    """
    Compute expected fragmentation given pod distribution and node state.
    Pure function - no node state needed.
    """
    total = 0
    for pod, prob in pod_distribution.items():
        total += prob * compute_fragmentation_score_with_state(
                pod, free_cpus, gpu_states)
    return total
