import json
import os.path

def read_json(filename) -> dict:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_dir,"..", "config", filename)
    with open(filepath, "r") as file:
        return json.load(file)