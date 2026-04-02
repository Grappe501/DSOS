
import json

def update_progress():
    with open('tracking/progress.json') as f:
        data = json.load(f)

    for phase in data:
        tasks = data[phase]["tasks"]
        if tasks:
            done = sum(1 for t in tasks if t.get("done"))
            data[phase]["progress"] = int((done/len(tasks))*100)

    with open('tracking/progress.json','w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    update_progress()
    print("Progress updated.")
