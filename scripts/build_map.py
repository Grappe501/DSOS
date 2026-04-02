
import os, json

def scan_build():
    structure = {}
    for root, dirs, files in os.walk('.'):
        structure[root] = files
    return structure

def load_progress():
    with open('tracking/progress.json') as f:
        return json.load(f)

def generate_map():
    structure = scan_build()
    progress = load_progress()
    output = {
        "structure": structure,
        "progress": progress
    }
    with open('tracking/build_map.json','w') as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    generate_map()
    print("Build map generated.")
