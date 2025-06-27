import os
from mongo_helper import insert_modules

def scan_test_modules():
    test_dir = os.path.join(os.path.dirname(__file__), '..', 'tests')
    files = os.listdir(test_dir)
    modules = [f[:-3] for f in files if f.endswith('.py') and not f.startswith('__')]
    return modules

if __name__ == '__main__':
    modules = scan_test_modules()
    insert_modules(modules)
    print(f"[✅] Modules inserted to MongoDB: {modules}")
