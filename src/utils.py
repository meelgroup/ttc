import os
import shutil

def check_existence(paths):
    for path in paths:
        if not os.path.exists(path['path']):
            raise FileNotFoundError(f"{path['name']} not found: {path['path']}")

def check_tools(tools):
    for tool in tools:
        if not shutil.which(tool):
            raise EnvironmentError(f"{tool} not found in the system PATH.")

def set_verbosity(level):
    from src.global_storage import global_storage
    global_storage.verbosity = level

def log(message, level=1):
    from src.global_storage import global_storage
    if global_storage.verbosity >= level:
        print(message)
