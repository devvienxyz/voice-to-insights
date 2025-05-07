import torch
import streamlit.watcher.local_sources_watcher as watcher


# Set thread limits
CPU_COUNT = 10
torch.set_num_threads(CPU_COUNT)
torch.set_num_interop_threads(CPU_COUNT)


# Patch get_module_paths to avoid torch.classes crash
def safe_get_module_paths(module):
    try:
        # Avoid calling __path__._path directly
        return list(getattr(module, "__path__", []))
    except Exception:
        return []


watcher.get_module_paths = safe_get_module_paths


def run_health_check():
    try:
        paths = watcher.get_module_paths(torch.classes)
        print("✅ Health check passed:", paths)
    except Exception as e:
        print("❌ Health check failed:", repr(e))


if __name__ == "__main__":
    run_health_check()
