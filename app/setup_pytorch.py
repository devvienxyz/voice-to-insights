import torch
import types
import streamlit.watcher.local_sources_watcher

torch.set_num_threads(10)
torch.set_num_interop_threads(10)


# Patch streamlit watcher
def patched_get_module_paths(module):
    try:
        paths = getattr(module, "__path__", None)
        if paths is None or not isinstance(paths, (list, types.ModuleType)):
            return []
        return list(paths)
    except Exception:
        return []


streamlit.watcher.local_sources_watcher.get_module_paths = patched_get_module_paths
