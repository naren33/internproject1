import os
import re

TEST_DIR = os.path.join(os.path.dirname(__file__), '..', 'tests')

def fetch_testcases(module_name):
    file_path = os.path.join(TEST_DIR, f"{module_name}.py")
    
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match function names starting with test_
    test_cases = re.findall(r"def (test_[a-zA-Z0-9_]+)\s*\(", content)
    
    return sorted(set(test_cases))
