from src.Node import Node
from src.Pod import Pod
from pathlib import Path
import csv
from collections import defaultdict
from typing import Dict
from pathlib import Path

POD_PATH = Path(__file__).parent.parent.parent / "data" / "openb_pod_list_default.csv"
NODE_PATH = Path(__file__).parent.parent.parent / "data" / "openb_node_list_all_node.csv"

def load_nodes(path = NODE_PATH):
    with open(path, 'r') as f:
        reader = csv.reader(f)
        _ = next(reader) #write header
        return  [
                Node(
                    row[0],      # id
                    int(row[1]), # total_cpu
                    int(row[3])  # num_gpus
                    ) 
                for row in reader
                ]

def load_pods(path = POD_PATH):
    with open(path, 'r') as f:
        reader = csv.reader(f)
        _ = next(reader)
        pod_list = []
        for row in reader:
            num_gpus = float(row[3])
            if num_gpus >= 1.0:
                pod_list.append(
                    Pod(
                        row[0],      # id 
                        int(row[1]), # cpu_request
                        num_gpus     # gpu_requeset
                    )
                )
            else:
                num_gpus = float(row[4]) / 1000 # convert gpu_milli to num_gpus
                pod_list.append(
                        Pod(
                            row[0],     
                            int(row[1]), 
                            num_gpus
                        )
                )
        return pod_list


def load_pod_distribution(path = POD_PATH) -> Dict['Pod', float]:
    pod_list = load_pods(path)
    histogram = defaultdict(int) 

    for pod in pod_list:
        histogram[pod] += 1 # defaultdict automatically creates keys if necessary

    total = sum(histogram.values())

    return {pod: count / total for pod, count in histogram.items()}

