import os
import inspect
import importlib.util
import pytest

# Path to the challenges folder
CHALLENGES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../challenges')

def get_python_files(directory, exclude_file):
    """Recursively get all python files in a directory and subdirectories."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file.startswith("test_") and file != exclude_file:
                python_files.append(os.path.join(root, file))
    return python_files

def test_method_name_and_count():
    current_file = os.path.basename(__file__)
    test_files = get_python_files(CHALLENGES_DIR, current_file)
    for test_file in test_files:
        spec = importlib.util.spec_from_file_location("module.name", test_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        functions_list = [o for o in inspect.getmembers(module) if inspect.isfunction(o[1]) and o[0].startswith('test_')]
        assert len(functions_list) == 1, f"{test_file} should contain only one function"
        assert functions_list[0][0][5:] == os.path.basename(test_file)[5:-3], f"The function in {test_file} should have the same name as the file without 'test_' prefix"
