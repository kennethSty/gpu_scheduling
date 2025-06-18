from src.Pod import Pod

class GPU:
    def __init__(self, id: int, free_gpu: float = 1.0):
        self.id = id
        self.free_gpu = free_gpu

    def can_serve(self, free_cpu: float, pod: Pod) -> bool:
        if pod.gpu_request >= 1.0:
            return (pod.cpu_request <= free_cpu) and \
                   (self.free_gpu == 1.0) # partial GPUs cannot be allocated
        else:
            return (pod.cpu_request <= free_cpu) and \
                   (pod.gpu_request <= self.free_gpu)

    def get_fragmentation(self, free_cpu: float, pod: Pod) -> float:
        return 0.0 if self.can_serve(free_cpu, pod) else self.free_gpu

    def serve(self, pod: Pod): 
        self.free_gpu = pod.consume_gpus(self.free_gpu)

    def hypothetical_serve(self, pod: Pod) -> float:
        return pod.consume_gpus(self.free_gpu, hypothetical=True)

    def get_capacity(self) -> float:
        return self.free_gpu

