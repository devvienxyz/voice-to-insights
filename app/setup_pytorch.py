import os
import torch

# os.cpu_count()
CPU_COUNT = 10
torch.set_num_threads(CPU_COUNT)
torch.set_num_interop_threads(CPU_COUNT)
