from src.Pod import Pod
from src.utils.load_data import load_pods

POD_PATH = 

def main():
    pod_list = load_pods(POD_PATH)
    pod_type_freqs = {}
    n = 0

    for pod in pod_list:
        pod_type = (pod.cpu_request, pod.gpu_request)
        if pod_type not in gpu_request_freqs:
            pod_type_freqs[pod_type] = 0
            n += 1
        else:
            pod_type_freqs[pod_type] += 1

    # WIP
            

